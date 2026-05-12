import re
from typing import Optional
from bs4 import BeautifulSoup


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
    from app.rss.fuentes import PALABRAS_ORDEN_PUBLICO

    texto_combinado = f"{titulo} {descripcion}".lower()
    for palabra in PALABRAS_ORDEN_PUBLICO:
        if palabra in texto_combinado:
            return "orden_publico"
    return categoria_base
