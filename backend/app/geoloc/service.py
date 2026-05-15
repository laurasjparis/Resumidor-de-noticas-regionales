from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.geoloc.extractor import LugarDetectado, extraer_lugares
from app.geoloc.geocoder import GeocodingService
from app.geoloc.normalizer import normalizar_lugar
from app.models.noticia import Noticia
from app.models.ubicacion import UbicacionNoticia

TIPO_PRIORIDAD = {
    "barrio": 4,
    "comuna": 4,
    "sector": 3,
    "municipio": 2,
    "direccion_aproximada": 1,
    "otro": 0,
}

PRECISION_PRIORIDAD = {
    "exacta": 3,
    "aproximada": 2,
    "baja": 1,
}

TIPOS_UBICACION_UTIL = {"barrio", "comuna", "sector", "municipio"}
PRECISION_MINIMA_UTIL = {"exacta", "aproximada"}
LUGARES_DESCARTADOS = {"Antioquia", "Colombia"}


@dataclass(frozen=True)
class ProcesamientoNoticiaResultado:
    noticia_id: int
    con_ubicaciones: bool


def procesar_noticia(
    db: Session,
    noticia_id: int,
    forzar_reproceso: bool = False,
) -> ProcesamientoNoticiaResultado | None:
    noticia = (
        db.query(Noticia)
        .options(joinedload(Noticia.ubicaciones))
        .filter(Noticia.id == noticia_id)
        .first()
    )
    if not noticia:
        return None

    if noticia.ubicaciones and not forzar_reproceso:
        return ProcesamientoNoticiaResultado(noticia_id=noticia.id, con_ubicaciones=True)

    if noticia.ubicaciones and forzar_reproceso:
        for ubicacion in list(noticia.ubicaciones):
            db.delete(ubicacion)
        db.commit()

    candidatos = extraer_lugares(
        noticia.titulo or "",
        noticia.descripcion or "",
        noticia.contenido or "",
    )
    geocoder = GeocodingService(db)
    resultados = []
    vistos = set()

    for candidato in candidatos:
        lugar_normalizado, query = normalizar_lugar(
            candidato.texto_detectado,
            candidato.tipo_lugar,
        )
        clave = (lugar_normalizado, candidato.tipo_lugar)
        if clave in vistos:
            continue
        vistos.add(clave)

        geo = geocoder.geocodificar(
            candidato.texto_detectado,
            query,
            candidato.tipo_lugar,
        )
        if not geo:
            continue

        if not es_ubicacion_util(
            lugar_normalizado=lugar_normalizado,
            tipo_lugar=candidato.tipo_lugar,
            precision=geo.precision,
        ):
            continue

        resultados.append(
            {
                "candidato": candidato,
                "lugar_normalizado": lugar_normalizado,
                "latitud": geo.latitud,
                "longitud": geo.longitud,
                "precision": geo.precision,
                "fuente_geocodificacion": geo.fuente_geocodificacion,
            }
        )

    if not resultados:
        return ProcesamientoNoticiaResultado(noticia_id=noticia.id, con_ubicaciones=False)

    principal_idx = seleccionar_principal(resultados)
    for idx, item in enumerate(resultados):
        candidato: LugarDetectado = item["candidato"]
        db.add(
            UbicacionNoticia(
                noticia_id=noticia.id,
                texto_detectado=candidato.texto_detectado,
                lugar_normalizado=item["lugar_normalizado"],
                tipo_lugar=candidato.tipo_lugar,
                latitud=item["latitud"],
                longitud=item["longitud"],
                precision=item["precision"],
                es_principal=idx == principal_idx,
                fuente_extraccion=candidato.fuente_extraccion,
                fuente_geocodificacion=item["fuente_geocodificacion"],
            )
        )

    db.commit()
    return ProcesamientoNoticiaResultado(noticia_id=noticia.id, con_ubicaciones=True)


def procesar_noticias_pendientes(
    db: Session,
    limit: int | None = None,
    forzar_reproceso: bool = False,
) -> dict:
    query = db.query(Noticia).order_by(Noticia.creado_en.desc())
    if not forzar_reproceso:
        query = query.outerjoin(Noticia.ubicaciones).filter(UbicacionNoticia.id.is_(None))
    if limit:
        query = query.limit(limit)

    noticias = query.all()
    total_con_ubicaciones = 0
    total_sin_ubicaciones = 0
    total_errores = 0

    for noticia in noticias:
        try:
            resultado = procesar_noticia(
                db,
                noticia.id,
                forzar_reproceso=forzar_reproceso,
            )
            if resultado and resultado.con_ubicaciones:
                total_con_ubicaciones += 1
            else:
                total_sin_ubicaciones += 1
        except Exception:
            db.rollback()
            total_errores += 1

    return {
        "total_evaluadas": len(noticias),
        "total_con_ubicaciones": total_con_ubicaciones,
        "total_sin_ubicaciones": total_sin_ubicaciones,
        "total_errores": total_errores,
    }


def obtener_ubicaciones_noticia(db: Session, noticia_id: int) -> list[UbicacionNoticia]:
    return (
        db.query(UbicacionNoticia)
        .filter(UbicacionNoticia.noticia_id == noticia_id)
        .order_by(UbicacionNoticia.es_principal.desc(), UbicacionNoticia.id.asc())
        .all()
    )


def listar_eventos_geograficos(
    db: Session,
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
    categoria: str | None = None,
    municipio: str | None = None,
    solo_principal: bool = True,
):
    query = (
        db.query(Noticia, UbicacionNoticia)
        .join(UbicacionNoticia, UbicacionNoticia.noticia_id == Noticia.id)
        .order_by(Noticia.fecha.desc().nullslast(), Noticia.creado_en.desc())
    )

    if solo_principal:
        query = query.filter(UbicacionNoticia.es_principal.is_(True))
    if fecha_desde:
        query = query.filter(Noticia.fecha >= fecha_desde)
    if fecha_hasta:
        query = query.filter(Noticia.fecha <= fecha_hasta)
    if categoria:
        query = query.filter(Noticia.categoria == categoria)
    if municipio:
        query = query.filter(UbicacionNoticia.lugar_normalizado.ilike(f"%{municipio}%"))

    return query.all()


def seleccionar_principal(resultados: list[dict]) -> int:
    puntajes = []
    for idx, item in enumerate(resultados):
        candidato: LugarDetectado = item["candidato"]
        puntajes.append(
            (
                1 if candidato.en_titulo else 0,
                TIPO_PRIORIDAD.get(candidato.tipo_lugar, 0),
                PRECISION_PRIORIDAD.get(item["precision"], 0),
                -candidato.orden,
                -idx,
            )
        )

    return max(range(len(puntajes)), key=lambda i: puntajes[i])


def es_ubicacion_util(lugar_normalizado: str, tipo_lugar: str, precision: str) -> bool:
    if lugar_normalizado in LUGARES_DESCARTADOS:
        return False
    if tipo_lugar not in TIPOS_UBICACION_UTIL:
        return False
    if precision not in PRECISION_MINIMA_UTIL:
        return False
    return True
