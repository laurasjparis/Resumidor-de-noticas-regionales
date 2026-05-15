import re
from dataclasses import dataclass
from functools import lru_cache

import spacy
from spacy.language import Language

from app.geoloc.normalizer import (
    BARRIOS_MEDELLIN,
    COMUNAS_MEDELLIN,
    VALLE_ABURRA_MUNICIPIOS,
    slug_lugar,
)


@dataclass(frozen=True)
class LugarDetectado:
    texto_detectado: str
    tipo_lugar: str
    fuente_extraccion: str
    en_titulo: bool
    orden: int


REGEX_PATTERNS = [
    (re.compile(r"\b(comuna\s+1[0-6]|comuna\s+[1-9])\b", re.IGNORECASE), "comuna"),
    (
        re.compile(
            r"\b(?:barrio|sector)\s+([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚáéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚáéíóúñ]+)*)",
            re.IGNORECASE,
        ),
        "barrio",
    ),
    (
        re.compile(
            r"\ben\s+([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚáéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚáéíóúñ]+)*)",
            re.IGNORECASE,
        ),
        "otro",
    ),
]


@lru_cache(maxsize=1)
def cargar_nlp() -> Language:
    try:
        return spacy.load("es_core_news_sm")
    except Exception:
        nlp = spacy.blank("es")
        ruler = nlp.add_pipe("entity_ruler")
        patterns = []
        for nombre in list(VALLE_ABURRA_MUNICIPIOS.values()) + list(BARRIOS_MEDELLIN.values()):
            patterns.append({"label": "LOC", "pattern": nombre.split(",")[0]})
        for nombre in COMUNAS_MEDELLIN.values():
            patterns.append({"label": "LOC", "pattern": nombre.split(",")[0]})
        ruler.add_patterns(patterns)
        return nlp


def extraer_lugares(titulo: str, descripcion: str, contenido: str) -> list[LugarDetectado]:
    texto_completo = " ".join(parte for parte in [titulo, descripcion, contenido] if parte).strip()
    resultados: list[LugarDetectado] = []
    vistos: set[tuple[str, str, bool]] = set()

    def agregar(texto: str, tipo_lugar: str, fuente: str, en_titulo: bool, orden: int) -> None:
        clave = (texto.strip().lower(), tipo_lugar, en_titulo)
        if texto.strip() and clave not in vistos:
            vistos.add(clave)
            resultados.append(
                LugarDetectado(
                    texto_detectado=texto.strip(),
                    tipo_lugar=tipo_lugar,
                    fuente_extraccion=fuente,
                    en_titulo=en_titulo,
                    orden=orden,
                )
            )

    for idx, (pattern, tipo_lugar) in enumerate(REGEX_PATTERNS):
        for match in pattern.finditer(titulo):
            texto = match.group(1) if match.lastindex else match.group(0)
            agregar(texto, _resolver_tipo(texto, tipo_lugar), "regex", True, idx)
        for match in pattern.finditer(texto_completo):
            texto = match.group(1) if match.lastindex else match.group(0)
            agregar(texto, _resolver_tipo(texto, tipo_lugar), "regex", False, idx + 100)

    nlp = cargar_nlp()
    for idx, ent in enumerate(nlp(texto_completo).ents):
        if ent.label_ not in {"LOC", "GPE"}:
            continue
        en_titulo = ent.start_char < len(titulo)
        agregar(ent.text, _resolver_tipo(ent.text, "otro"), "spacy", en_titulo, idx + 200)

    for idx, nombre in enumerate(list(VALLE_ABURRA_MUNICIPIOS.values()) + list(BARRIOS_MEDELLIN.values())):
        base = nombre.split(",")[0]
        pattern = re.compile(rf"\b{re.escape(base)}\b", re.IGNORECASE)
        titulo_match = pattern.search(titulo or "")
        texto_match = pattern.search(texto_completo)
        if texto_match:
            agregar(base, _resolver_tipo(base, "otro"), "diccionario", titulo_match is not None, idx + 300)

    return resultados


def _resolver_tipo(texto: str, tipo_predeterminado: str) -> str:
    nombres_barrios = {slug_lugar(x.split(",")[0]) for x in BARRIOS_MEDELLIN.values()}
    slug = slug_lugar(texto)

    if slug.startswith("comuna "):
        return "comuna"
    if slug in VALLE_ABURRA_MUNICIPIOS:
        return "municipio"
    if slug in nombres_barrios:
        return "barrio"
    return tipo_predeterminado
