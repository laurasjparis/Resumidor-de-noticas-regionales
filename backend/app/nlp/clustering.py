from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta
import numpy as np
import logging

logger = logging.getLogger(__name__)


def agrupar_noticias(
    embeddings: list[list[float]],
    fechas: list[datetime | None] = None,
    umbral: float = 0.65,
    max_dias: int = 3,
) -> list[list[int]]:
    """
    Agrupa noticias por similitud coseno + cercanía temporal.

    Dos noticias se agrupan solo si:
    1. Su similitud de texto >= umbral
    2. Sus fechas tienen máximo max_dias de diferencia

    Esto evita agrupar noticias temáticamente similares
    pero de eventos distintos.
    """
    if not embeddings:
        return []

    matriz = np.array(embeddings)
    similitudes = cosine_similarity(matriz)

    n = len(embeddings)
    visitados = set()
    grupos = []

    for i in range(n):
        if i in visitados:
            continue

        grupo = [i]
        visitados.add(i)

        for j in range(i + 1, n):
            if j in visitados:
                continue

            # Condición 1: similitud de texto
            if similitudes[i][j] < umbral:
                continue

            # Condición 2: cercanía temporal
            if fechas and fechas[i] and fechas[j]:
                diff = abs((fechas[i] - fechas[j]).total_seconds())
                if diff > max_dias * 86400:  # 86400 = segundos en un día
                    continue

            grupo.append(j)
            visitados.add(j)

        grupos.append(grupo)

    logger.info(f"Se formaron {len(grupos)} grupos de {n} noticias (umbral={umbral}, max_dias={max_dias})")
    return grupos


def obtener_similitudes(embeddings: list[list[float]], grupo: list[int]) -> dict[int, float]:
    """
    Para un grupo de noticias, calcula la similitud de cada una
    respecto a la primera (que actúa como 'ancla').
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