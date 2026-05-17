from sqlalchemy.orm import Session
from app.models.noticia import Noticia
from app.models.evento import Evento, EventoNoticia
from app.nlp.embeddings import generar_embeddings, texto_de_noticia
from app.nlp.clustering import agrupar_noticias, obtener_similitudes
from app.nlp.resumidor import generar_resumen
import logging

logger = logging.getLogger(__name__)


def procesar_eventos(db: Session, umbral: float = 0.55) -> dict:
    """
    Pipeline completo:
    1. Leer noticias de la BD
    2. Generar embeddings
    3. Agrupar por similitud
    4. Generar resúmenes con Ollama
    5. Guardar eventos en la BD
    
    Retorna estadísticas del proceso.
    """
    # 1. Leer noticias
    noticias = db.query(Noticia).order_by(Noticia.fecha.desc()).all()
    if not noticias:
        return {"mensaje": "No hay noticias para procesar", "eventos_creados": 0}

    logger.info(f"Procesando {len(noticias)} noticias...")

    # 2. Generar embeddings
    textos = [texto_de_noticia(n) for n in noticias]
    embeddings = generar_embeddings(textos)

    # 3. Agrupar
    grupos = agrupar_noticias(embeddings, umbral=umbral)

    # 4. Limpiar eventos anteriores (reprocesar desde cero)
    db.query(EventoNoticia).delete()
    db.query(Evento).delete()
    db.commit()

    eventos_creados = 0

    for grupo in grupos:
        noticias_del_grupo = [noticias[i] for i in grupo]
        textos_del_grupo = [textos[i] for i in grupo]
        similitudes = obtener_similitudes(embeddings, grupo)

        # 5. Generar resumen con Ollama
        resumen = generar_resumen(textos_del_grupo)

        # Determinar categoría del evento (la más común en el grupo)
        categorias = [n.categoria for n in noticias_del_grupo if n.categoria]
        categoria = max(set(categorias), key=categorias.count) if categorias else "general"

        # Determinar rango de fechas
        fechas = [n.fecha for n in noticias_del_grupo if n.fecha]
        fecha_inicio = min(fechas) if fechas else None
        fecha_fin = max(fechas) if fechas else None

        # Título del evento = título de la noticia más representativa (primera del grupo)
        titulo_evento = noticias_del_grupo[0].titulo

        # Crear evento
        evento = Evento(
            titulo=titulo_evento,
            resumen=resumen,
            categoria=categoria,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            cantidad_noticias=len(grupo),
        )
        db.add(evento)
        db.flush()  # Para obtener el ID

        # Crear relaciones evento-noticia
        for idx in grupo:
            en = EventoNoticia(
                evento_id=evento.id,
                noticia_id=noticias[idx].id,
                similitud=similitudes.get(idx, 0.0),
            )
            db.add(en)

        eventos_creados += 1

    db.commit()
    logger.info(f"Pipeline completado: {eventos_creados} eventos creados")

    return {
        "noticias_procesadas": len(noticias),
        "eventos_creados": eventos_creados,
        "umbral_similitud": umbral,
    }