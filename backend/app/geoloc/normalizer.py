import re
import unicodedata

VALLE_ABURRA_MUNICIPIOS = {
    "medellin": "Medellín",
    "bello": "Bello",
    "itagui": "Itagüí",
    "envigado": "Envigado",
    "sabaneta": "Sabaneta",
    "la estrella": "La Estrella",
    "caldas": "Caldas",
    "copacabana": "Copacabana",
    "girardota": "Girardota",
    "barbosa": "Barbosa",
}

COMUNAS_MEDELLIN = {
    "comuna 1": "Comuna 1, Medellín",
    "comuna 2": "Comuna 2, Medellín",
    "comuna 3": "Comuna 3, Medellín",
    "comuna 4": "Comuna 4, Medellín",
    "comuna 5": "Comuna 5, Medellín",
    "comuna 6": "Comuna 6, Medellín",
    "comuna 7": "Comuna 7, Medellín",
    "comuna 8": "Comuna 8, Medellín",
    "comuna 9": "Comuna 9, Medellín",
    "comuna 10": "Comuna 10, Medellín",
    "comuna 11": "Comuna 11, Medellín",
    "comuna 12": "Comuna 12, Medellín",
    "comuna 13": "Comuna 13, Medellín",
    "comuna 14": "Comuna 14, Medellín",
    "comuna 15": "Comuna 15, Medellín",
    "comuna 16": "Comuna 16, Medellín",
}

BARRIOS_MEDELLIN = {
    "laureles": "Laureles, Medellín",
    "robledo": "Robledo, Medellín",
    "manrique": "Manrique, Medellín",
    "belen": "Belén, Medellín",
    "castilla": "Castilla, Medellín",
    "aranjuez": "Aranjuez, Medellín",
    "guayabal": "Guayabal, Medellín",
    "boston": "Boston, Medellín",
    "prado": "Prado, Medellín",
    "el poblado": "El Poblado, Medellín",
}

ALIASES = {
    "medellin antioquia": "medellin",
    "bello antioquia": "bello",
    "itagui antioquia": "itagui",
    "barrio laureles": "laureles",
    "barrio robledo": "robledo",
}


def quitar_acentos(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    )


def slug_lugar(texto: str) -> str:
    limpio = quitar_acentos(texto.lower()).strip()
    limpio = re.sub(r"\s+", " ", limpio)
    limpio = re.sub(r"[^\w\s]", "", limpio)
    return limpio.strip()


def normalizar_lugar(texto: str, tipo_lugar: str) -> tuple[str, str]:
    slug = slug_lugar(texto)
    slug = ALIASES.get(slug, slug)

    if tipo_lugar == "municipio" and slug in VALLE_ABURRA_MUNICIPIOS:
        return VALLE_ABURRA_MUNICIPIOS[slug], f"{VALLE_ABURRA_MUNICIPIOS[slug]}, Antioquia, Colombia"

    if tipo_lugar == "comuna" and slug in COMUNAS_MEDELLIN:
        valor = COMUNAS_MEDELLIN[slug]
        return valor, f"{valor}, Antioquia, Colombia"

    if tipo_lugar in {"barrio", "sector"} and slug in BARRIOS_MEDELLIN:
        valor = BARRIOS_MEDELLIN[slug]
        return valor, f"{valor}, Antioquia, Colombia"

    if slug in BARRIOS_MEDELLIN:
        valor = BARRIOS_MEDELLIN[slug]
        return valor, f"{valor}, Antioquia, Colombia"

    if slug in COMUNAS_MEDELLIN:
        valor = COMUNAS_MEDELLIN[slug]
        return valor, f"{valor}, Antioquia, Colombia"

    if slug in VALLE_ABURRA_MUNICIPIOS:
        valor = VALLE_ABURRA_MUNICIPIOS[slug]
        return valor, f"{valor}, Antioquia, Colombia"

    titulo = " ".join(parte.capitalize() for parte in slug.split())
    if tipo_lugar in {"barrio", "sector", "comuna"}:
        lugar = f"{titulo}, Medellín"
        return lugar, f"{lugar}, Antioquia, Colombia"

    return titulo, f"{titulo}, Antioquia, Colombia"
