from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

logger = logging.getLogger(__name__)


def agrupar_noticias(embeddings: list[list[float]], umbral: float = 0.55) -> list[list[int]]:
    """
    Agrupa noticias por similitud coseno.
    
    Recibe los embeddings (vectores) y devuelve una lista de grupos.
    Cada grupo es una lista de índices de noticias.
    
    Ejemplo: [[0, 3, 7], [1, 4], [2], [5, 6]]
    Significa: noticias 0,3,7 son un evento; 1,4 otro; 2 sola; 5,6 otro.
    
    umbral: qué tan parecidas deben ser para agruparse (0.0 a 1.0)
             0.55 funciona bien para noticias en español.
    """
    if not embeddings:
        return []

    matriz = np.array(embeddings)
    # Calcular similitud entre TODAS las noticias (matriz NxN)
    similitudes = cosine_similarity(matriz)

    n = len(embeddings)
    visitados = set()
    grupos = []

    for i in range(n):
        if i in visitados:
            continue

        # Crear un nuevo grupo con esta noticia
        grupo = [i]
        visitados.add(i)

        # Buscar todas las noticias similares a esta
        for j in range(i + 1, n):
            if j in visitados:
                continue
            if similitudes[i][j] >= umbral:
                grupo.append(j)
                visitados.add(j)

        grupos.append(grupo)

    logger.info(f"Se formaron {len(grupos)} grupos de {n} noticias (umbral={umbral})")
    return grupos


def obtener_similitudes(embeddings: list[list[float]], grupo: list[int]) -> dict[int, float]:
    """
    Para un grupo de noticias, calcula la similitud de cada una
    respecto a la primera (que actúa como 'ancla').
    Devuelve {indice: similitud}.
    """
    if len(grupo) <= 1:
        return {grupo[0]: 1.0}

    matriz = np.array(embeddings)
    ancla = matriz[grupo[0]].reshape(1, -1)
    resultado = {}

    for idx in grupo:
        vec = matriz[idx].reshape(1, -1)
        sim = cosine_similarity(ancla, vec)[0][0]
        resultado[idx] = round(float(sim), 4)

    return resultado