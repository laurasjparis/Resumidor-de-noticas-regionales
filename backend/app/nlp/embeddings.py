from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

# Se carga una sola vez cuando se importa el módulo
# Este modelo entiende español y es liviano (~120MB)
_modelo = None


def get_modelo():
    global _modelo
    if _modelo is None:
        logger.info("Cargando modelo de embeddings...")
        _modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        logger.info("Modelo de embeddings cargado.")
    return _modelo


def generar_embeddings(textos: list[str]) -> list[list[float]]:
    """
    Recibe una lista de textos y devuelve una lista de vectores.
    Cada vector es una lista de 384 números.
    """
    modelo = get_modelo()
    embeddings = modelo.encode(textos, show_progress_bar=True)
    return embeddings.tolist()


def texto_de_noticia(noticia) -> str:
    """
    Combina título + descripción para crear el texto
    que se convierte en vector. No usamos contenido completo
    porque es muy largo y añade ruido.
    """
    partes = []
    if noticia.titulo:
        partes.append(noticia.titulo)
    if noticia.descripcion:
        partes.append(noticia.descripcion)
    return " . ".join(partes)