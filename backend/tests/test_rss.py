"""
Pruebas básicas del módulo RSS.
Ejecutar: pytest tests/
"""
import pytest
from unittest.mock import patch, MagicMock

from app.rss.limpieza import (
    clasificar_categoria,
    es_noticia_relevante_region,
    limpiar_html,
    limpiar_texto,
)
from app.rss.parser import parsear_fecha, procesar_feed


# --- limpieza ---

def test_limpiar_html_elimina_tags():
    resultado = limpiar_html("<p>Hola <b>mundo</b></p>")
    assert resultado == "Hola mundo"


def test_limpiar_html_vacio():
    assert limpiar_html(None) == ""
    assert limpiar_html("") == ""


def test_limpiar_texto_normaliza_espacios():
    assert limpiar_texto("  texto   con   espacios  ") == "texto con espacios"


def test_clasificar_categoria_orden_publico():
    cat = clasificar_categoria("Balacera en Bello deja dos heridos", "", "general")
    assert cat == "orden_publico"


def test_clasificar_categoria_general():
    cat = clasificar_categoria("Festival de flores en Medellín", "", "general")
    assert cat == "general"


def test_es_noticia_relevante_region_municipio():
    assert es_noticia_relevante_region(
        "Enfrentamiento armado en Bello deja dos heridos",
        "",
    ) is True


def test_es_noticia_relevante_region_barrio():
    assert es_noticia_relevante_region(
        "Hurto en Laureles",
        "Vecinos alertan por varios casos recientes",
    ) is True


def test_es_noticia_relevante_region_descarta_nacional():
    assert es_noticia_relevante_region(
        "Gobierno anuncia reforma tributaria",
        "Debate nacional en el Congreso",
    ) is False


# --- parser ---

def test_parsear_fecha_published():
    entry = MagicMock()
    entry.get = lambda k, d=None: (
        "Mon, 12 May 2025 10:00:00 +0000" if k == "published" else d
    )
    fecha = parsear_fecha(entry)
    assert fecha is not None
    assert fecha.year == 2025


def test_parsear_fecha_sin_datos():
    entry = MagicMock()
    entry.get = lambda k, d=None: d
    fecha = parsear_fecha(entry)
    assert fecha is None


@patch("app.rss.parser.feedparser.parse")
def test_procesar_feed_filtra_fuera_de_la_region(mock_parse):
    entrada_fuera = MagicMock()
    entrada_fuera.get = lambda k, d=None: {
        "title": "Gobierno anuncia reforma tributaria",
        "link": "https://ejemplo.com/nacional",
        "summary": "Debate nacional en el Congreso",
    }.get(k, d)

    entrada_region = MagicMock()
    entrada_region.get = lambda k, d=None: {
        "title": "Capturan a dos personas en Bello",
        "link": "https://ejemplo.com/bello",
        "summary": "Operativo en Bello deja dos capturados",
    }.get(k, d)

    mock_parse.return_value = MagicMock(bozo=False, entries=[entrada_fuera, entrada_region])

    noticias = procesar_feed({"nombre": "Prueba", "url": "https://feed.test", "categoria": "general"})

    assert len(noticias) == 1
    assert noticias[0]["titulo"] == "Capturan a dos personas en Bello"
