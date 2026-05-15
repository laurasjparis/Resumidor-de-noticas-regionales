"""
Catálogo de fuentes RSS colombianas monitoreadas.
Cada entrada incluye nombre, URL del feed y categoría base.
"""

FUENTES_RSS = [
    {
        "nombre": "El Colombiano",
        "url": "https://www.elcolombiano.com/feed",
        "categoria": "general",
    },
    {
        "nombre": "Caracol Radio",
        "url": "https://caracol.com.co/feed/rss/",
        "categoria": "general",
    },
    {
        "nombre": "Blu Radio",
        "url": "https://www.bluradio.com/feed",
        "categoria": "general",
    },
    {
        "nombre": "Minuto30",
        "url": "https://www.minuto30.com/feed/",
        "categoria": "general",
    },
    {
        "nombre": "Semana",
        "url": "https://feeds.semana.com/semana-noticias-colombia",
        "categoria": "general",
    },
    {
        "nombre": "Alerta Paisa",
        "url": "https://alertapaisa.com/feed/",
        "categoria": "orden_publico",
    },
    {
        "nombre": "Q'Hubo",
        "url": "https://www.qhubo.com/feed/",
        "categoria": "orden_publico",
    },
]

# Palabras clave para clasificar noticias como orden_publico / convivencia
PALABRAS_ORDEN_PUBLICO = [
    "balacera", "homicidio", "asesinato", "muerto", "herido",
    "robo", "hurto", "atraco", "extorsión", "secuestro",
    "violencia", "riña", "pelea", "ataque", "disparos",
    "policía", "capturado", "detenido", "operativo",
    "narcotráfico", "droga", "coca", "tráfico",
    "explosión", "bomba", "atentado", "terrorismo",
    "desaparecido", "feminicidio", "abuso", "delito",
    "pandilla", "banda criminal", "clan",
    "orden público", "convivencia",
]

MUNICIPIOS_VALLE_ABURRA = [
    "medellín", "medellin", "bello", "itagüí", "itagui", "envigado",
    "sabaneta", "la estrella", "caldas", "copacabana", "girardota", "barbosa",
]

COMUNAS_Y_BARRIOS_MEDELLIN = [
    "comuna 1", "comuna 2", "comuna 3", "comuna 4", "comuna 5", "comuna 6",
    "comuna 7", "comuna 8", "comuna 9", "comuna 10", "comuna 11", "comuna 12",
    "comuna 13", "comuna 14", "comuna 15", "comuna 16",
    "laureles", "robledo", "manrique", "belén", "belen", "castilla",
    "aranjuez", "guayabal", "boston", "prado", "el poblado",
]
