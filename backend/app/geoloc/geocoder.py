import logging
from dataclasses import dataclass

from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim
from sqlalchemy.orm import Session

from app.models.ubicacion import CacheGeocoding

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResultadoGeocoding:
    query_original: str
    query_normalizada: str
    latitud: float
    longitud: float
    tipo_lugar: str
    precision: str
    fuente_geocodificacion: str


class GeocodingService:
    def __init__(self, db: Session):
        self.db = db
        self.client = Nominatim(user_agent="resumidor_noticias_geoloc")

    def geocodificar(
        self, query_original: str, query_normalizada: str, tipo_lugar: str
    ) -> ResultadoGeocoding | None:
        cache = (
            self.db.query(CacheGeocoding)
            .filter(CacheGeocoding.query_normalizada == query_normalizada)
            .first()
        )
        if cache:
            return ResultadoGeocoding(
                query_original=query_original,
                query_normalizada=query_normalizada,
                latitud=cache.latitud,
                longitud=cache.longitud,
                tipo_lugar=cache.tipo_lugar,
                precision=cache.precision,
                fuente_geocodificacion="nominatim_cache",
            )

        try:
            location = self.client.geocode(
                query_normalizada,
                addressdetails=True,
                exactly_one=True,
            )
        except (GeocoderTimedOut, GeocoderServiceError) as exc:
            logger.warning("Error geocodificando '%s': %s", query_normalizada, exc)
            return None
        except Exception as exc:
            logger.error("Fallo inesperado geocodificando '%s': %s", query_normalizada, exc)
            return None

        if not location:
            return None

        precision = clasificar_precision(tipo_lugar, getattr(location, "raw", {}) or {})
        cache = CacheGeocoding(
            query_original=query_original,
            query_normalizada=query_normalizada,
            latitud=float(location.latitude),
            longitud=float(location.longitude),
            tipo_lugar=tipo_lugar,
            precision=precision,
            proveedor="nominatim",
        )
        self.db.add(cache)
        self.db.commit()
        self.db.refresh(cache)

        return ResultadoGeocoding(
            query_original=query_original,
            query_normalizada=query_normalizada,
            latitud=cache.latitud,
            longitud=cache.longitud,
            tipo_lugar=cache.tipo_lugar,
            precision=cache.precision,
            fuente_geocodificacion="nominatim_live",
        )


def clasificar_precision(tipo_lugar: str, raw: dict) -> str:
    address_type = raw.get("type", "")
    if tipo_lugar in {"barrio", "comuna"} and address_type in {
        "suburb",
        "neighbourhood",
        "administrative",
    }:
        return "exacta"
    if tipo_lugar == "municipio" and address_type in {"city", "administrative", "town"}:
        return "exacta"
    if address_type in {"city", "town", "administrative"}:
        return "aproximada"
    return "baja"
