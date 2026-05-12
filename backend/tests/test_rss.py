"""
Pruebas básicas del módulo RSS.
Ejecutar: pytest tests/
"""
import pytest
from unittest.mock import patch, MagicMock

from app.rss.limpieza import limpiar_html, limpiar_texto, clasificar_categoria
from app.rss.parser import parsear_fecha


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
