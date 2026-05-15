import logging

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.exc import IntegrityError

from app.database.connection import SessionLocal
from app.models.noticia import Noticia
from app.rss.fuentes import FUENTES_RSS
from app.rss.parser import procesar_feed, obtener_contenido_completo

logger = logging.getLogger(__name__)


def ejecutar_actualizacion():
    """Recorre todos los feeds RSS y guarda las noticias nuevas en la BD."""
    logger.info("Scheduler: iniciando actualización automática de feeds RSS")
    db = SessionLocal()
    nuevas = 0
    duplicadas = 0
    errores = 0

    try:
        for fuente in FUENTES_RSS:
            for datos in procesar_feed(fuente):
                try:
                    if not datos["contenido"]:
                        datos["contenido"] = obtener_contenido_completo(datos["url"])
                    db.add(Noticia(**datos))
                    db.commit()
                    nuevas += 1
                except IntegrityError:
                    db.rollback()
                    duplicadas += 1
                except Exception as exc:
                    db.rollback()
                    errores += 1
                    logger.error("Error guardando '%s': %s", datos.get("url"), exc)
    finally:
        db.close()

    logger.info(
        "Scheduler: actualización completada — nuevas=%d duplicadas=%d errores=%d",
        nuevas, duplicadas, errores,
    )


def iniciar_scheduler(intervalo_horas: int = 12) -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        ejecutar_actualizacion,
        trigger="interval",
        hours=intervalo_horas,
        id="actualizar_rss",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler iniciado: actualizará feeds cada %d horas", intervalo_horas)
    return scheduler
