import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional

import feedparser
import requests
from bs4 import BeautifulSoup

from app.config import settings
from app.rss.limpieza import limpiar_html, limpiar_texto, clasificar_categoria

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; ResumidorNoticias/1.0; "
        "+https://github.com/laurasjparis/resumidor)"
    )
}


def parsear_fecha(entry: feedparser.FeedParserDict) -> Optional[datetime]:
    """Extrae y normaliza la fecha de publicación de una entrada RSS."""
    for campo in ("published", "updated"):
        valor = entry.get(campo)
        if valor:
            try:
                return parsedate_to_datetime(valor).astimezone(timezone.utc)
            except Exception:
                pass

    struct = entry.get("published_parsed") or entry.get("updated_parsed")
    if struct:
        try:
            return datetime(*struct[:6], tzinfo=timezone.utc)
        except Exception:
            pass

    return None


def obtener_contenido_completo(url: str) -> str:
    """
    Extrae el texto principal del artículo.
    Intenta primero con newspaper4k (mejor precisión); si falla, usa BeautifulSoup.
    """
    # Intento 1: newspaper4k
    try:
        from newspaper import Article
        article = Article(url, language="es")
        article.download()
        article.parse()
        if article.text and len(article.text) > 100:
            return limpiar_texto(article.text)
    except Exception as exc:
        logger.debug("newspaper4k no pudo extraer %s: %s", url, exc)

    # Intento 2: BeautifulSoup como fallback
    try:
        resp = requests.get(url, headers=HEADERS, timeout=settings.HTTP_TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        for selector in ("article", '[class*="article"]', '[class*="content"]', "main"):
            contenedor = soup.select_one(selector)
            if contenedor:
                return limpiar_html(str(contenedor))

        return limpiar_html(soup.get_text())
    except Exception as exc:
        logger.warning("No se pudo obtener contenido de %s: %s", url, exc)
        return ""


def procesar_feed(fuente: dict) -> list[dict]:
    """
    Parsea un feed RSS y devuelve una lista de noticias normalizadas.
    No accede a la base de datos; sólo transforma datos.
    """
    nombre = fuente["nombre"]
    url_feed = fuente["url"]
    categoria_base = fuente.get("categoria", "general")

    logger.info("Procesando feed: %s (%s)", nombre, url_feed)

    try:
        feed = feedparser.parse(url_feed, request_headers=HEADERS)
    except Exception as exc:
        logger.error("Error al parsear feed %s: %s", nombre, exc)
        return []

    if feed.bozo and not feed.entries:
        logger.warning("Feed malformado o vacío: %s — %s", nombre, feed.bozo_exception)
        return []

    noticias = []
    for entry in feed.entries:
        try:
            titulo = limpiar_texto(entry.get("title", ""))
            url_noticia = entry.get("link", "")
            if not titulo or not url_noticia:
                continue

            descripcion = limpiar_html(
                entry.get("summary") or entry.get("description", "")
            )
            fecha = parsear_fecha(entry)
            categoria = clasificar_categoria(titulo, descripcion, categoria_base)

            noticias.append(
                {
                    "titulo": titulo,
                    "fecha": fecha,
                    "fuente": nombre,
                    "url": url_noticia,
                    "descripcion": descripcion,
                    "contenido": "",  # Se llena bajo demanda en la ruta de actualización
                    "categoria": categoria,
                }
            )
        except Exception as exc:
            logger.error("Error procesando entrada de %s: %s", nombre, exc)

    logger.info("  → %d entradas encontradas en %s", len(noticias), nombre)
    return noticias
