from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.connection import Base, get_db
from app.geoloc.extractor import extraer_lugares
from app.geoloc.geocoder import GeocodingService, clasificar_precision
from app.geoloc.normalizer import normalizar_lugar
from app.geoloc.service import es_ubicacion_util, seleccionar_principal
from app.main import app
from app.models.noticia import Noticia
from app.models.ubicacion import CacheGeocoding


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def crear_noticia(db, titulo, descripcion="", contenido="", categoria="general"):
    noticia = Noticia(
        titulo=titulo,
        fecha=datetime.now(timezone.utc),
        fuente="Prueba",
        url=f"https://ejemplo.com/{titulo.replace(' ', '-').lower()}",
        descripcion=descripcion,
        contenido=contenido,
        categoria=categoria,
    )
    db.add(noticia)
    db.commit()
    db.refresh(noticia)
    return noticia


def test_extraer_lugares_regex_diccionario():
    lugares = extraer_lugares(
        "Hurto en Laureles",
        "",
        "Capturaron a un hombre en Bello.",
    )
    textos = {l.texto_detectado for l in lugares}
    assert "Laureles" in textos
    assert "Bello" in textos


def test_normalizar_lugar_barrio_y_municipio():
    assert normalizar_lugar("laureles", "barrio")[0] == "Laureles, Medellín"
    assert normalizar_lugar("bello antioquia", "municipio")[0] == "Bello"


def test_seleccionar_principal_prioriza_titulo_y_granularidad():
    resultados = [
        {
            "candidato": type("C", (), {"en_titulo": True, "tipo_lugar": "municipio", "orden": 0})(),
            "precision": "exacta",
        },
        {
            "candidato": type("C", (), {"en_titulo": False, "tipo_lugar": "barrio", "orden": 1})(),
            "precision": "exacta",
        },
    ]
    assert seleccionar_principal(resultados) == 0


def test_geocoder_cache_hit():
    db = TestingSessionLocal()
    db.add(
        CacheGeocoding(
            query_original="Bello",
            query_normalizada="Bello, Antioquia, Colombia",
            latitud=6.338,
            longitud=-75.557,
            tipo_lugar="municipio",
            precision="exacta",
            proveedor="nominatim",
        )
    )
    db.commit()

    service = GeocodingService(db)
    resultado = service.geocodificar(
        "Bello",
        "Bello, Antioquia, Colombia",
        "municipio",
    )
    assert resultado is not None
    assert resultado.fuente_geocodificacion == "nominatim_cache"
    db.close()


def test_clasificar_precision():
    assert clasificar_precision("municipio", {"type": "city"}) == "exacta"
    assert clasificar_precision("barrio", {"type": "suburb"}) == "exacta"
    assert clasificar_precision("otro", {"type": "administrative"}) == "aproximada"


def test_es_ubicacion_util_descarta_genericos_y_precision_baja():
    assert es_ubicacion_util("Antioquia", "otro", "aproximada") is False
    assert es_ubicacion_util("Laureles, Medellín", "barrio", "baja") is False
    assert es_ubicacion_util("Bello", "municipio", "exacta") is True


@patch("app.geoloc.geocoder.Nominatim.geocode")
def test_endpoint_procesar_noticia(mock_geocode):
    mock_geocode.return_value = type(
        "Location",
        (),
        {"latitude": 6.2442, "longitude": -75.5812, "raw": {"type": "suburb"}},
    )()

    db = TestingSessionLocal()
    noticia = crear_noticia(db, "Hurto en Laureles", "Reporte en barrio Laureles")
    db.close()

    response = client.post(f"/geoloc/procesar/{noticia.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["total_con_ubicaciones"] == 1

    response = client.get(f"/geoloc/noticias/{noticia.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["ubicaciones"]) >= 1
    assert any(item["es_principal"] for item in data["ubicaciones"])


@patch("app.geoloc.geocoder.Nominatim.geocode")
def test_endpoint_eventos_filtra_por_municipio(mock_geocode):
    mock_geocode.side_effect = [
        type("Location", (), {"latitude": 6.338, "longitude": -75.557, "raw": {"type": "city"}})(),
        type("Location", (), {"latitude": 6.2518, "longitude": -75.5636, "raw": {"type": "suburb"}})(),
    ]

    db = TestingSessionLocal()
    noticia1 = crear_noticia(db, "Enfrentamiento armado en Bello", "Hechos en Bello")
    noticia2 = crear_noticia(db, "Hurto en Laureles", "Caso en Laureles")
    noticia1_id = noticia1.id
    noticia2_id = noticia2.id
    db.close()

    client.post(f"/geoloc/procesar/{noticia1_id}")
    client.post(f"/geoloc/procesar/{noticia2_id}")

    response = client.get("/geoloc/eventos", params={"municipio": "Bello"})
    assert response.status_code == 200
    eventos = response.json()
    assert len(eventos) == 1
    assert eventos[0]["noticia_id"] == noticia1_id


@patch("app.geoloc.geocoder.Nominatim.geocode")
def test_endpoint_mapa_entrega_payload_compacto(mock_geocode):
    mock_geocode.return_value = type(
        "Location",
        (),
        {"latitude": 6.338, "longitude": -75.557, "raw": {"type": "city"}},
    )()

    db = TestingSessionLocal()
    noticia = crear_noticia(db, "Enfrentamiento armado en Bello", "Hechos en Bello")
    noticia_id = noticia.id
    db.close()

    client.post(f"/geoloc/procesar/{noticia_id}")
    response = client.get("/geoloc/mapa")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["noticia_id"] == noticia_id
    assert payload[0]["lugar"] == "Bello"
    assert "latitud" in payload[0]
    assert "longitud" in payload[0]
