import re
from typing import Optional
from bs4 import BeautifulSoup
from app.rss.fuentes import MUNICIPIOS_VALLE_ABURRA, COMUNAS_Y_BARRIOS_MEDELLIN, PALABRAS_ORDEN_PUBLICO


def limpiar_html(texto: Optional[str]) -> str:
    """Elimina tags HTML y normaliza espacios en blanco."""
    if not texto:
        return ""
    soup = BeautifulSoup(texto, "html.parser")
    texto_plano = soup.get_text(separator=" ")
    return _normalizar_espacios(texto_plano)


def limpiar_texto(texto: Optional[str]) -> str:
    """Elimina caracteres de control y normaliza espacios."""
    if not texto:
        return ""
    texto = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", texto)
    return _normalizar_espacios(texto)


def _normalizar_espacios(texto: str) -> str:
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def clasificar_categoria(titulo: str, descripcion: str, categoria_base: str) -> str:
    """
    Sobreescribe la categoría si el texto contiene palabras clave de orden público.
    Devuelve la categoría_base si no hay coincidencia.
    """

    texto_combinado = f"{titulo} {descripcion}".lower()
    for palabra in PALABRAS_ORDEN_PUBLICO:
        if palabra in texto_combinado:
            return "orden_publico"
    return categoria_base


def es_noticia_relevante_region(
    titulo: str,
    descripcion: str,
    contenido: Optional[str] = None,
) -> bool:
    """
    Determina si una noticia está orientada a Medellín o al Valle de Aburrá.
    Exige al menos una mención explícita a municipios objetivo, comunas o barrios frecuentes.
    """

    texto = _normalizar_para_busqueda(f"{titulo} {descripcion} {contenido or ''}")
    referencias = MUNICIPIOS_VALLE_ABURRA + COMUNAS_Y_BARRIOS_MEDELLIN

    for referencia in referencias:
        patron = rf"\b{re.escape(_normalizar_para_busqueda(referencia))}\b"
        if re.search(patron, texto):
            return True
    return False


def _normalizar_para_busqueda(texto: str) -> str:
    texto = limpiar_texto(texto).lower()
    reemplazos = str.maketrans(
        {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
            "ñ": "n",
        }
    )
    return texto.translate(reemplazos)
