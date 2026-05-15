import logging

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.noticia import Noticia
from app.models.schemas import ActualizarRSSResponse
from app.rss.fuentes import FUENTES_RSS
from app.rss.parser import procesar_feed, obtener_contenido_completo

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rss", tags=["rss"])


@router.post("/actualizar", response_model=ActualizarRSSResponse)
def actualizar_rss(
    obtener_contenido: bool = False,
    db: Session = Depends(get_db),
):
    """
    Recorre todas las fuentes RSS, extrae las noticias y guarda las nuevas.
    - `obtener_contenido=true`: descarga el artículo completo (más lento).
    - Noticias duplicadas (misma URL) se ignoran silenciosamente.
    """
    total = 0
    nuevas = 0
    duplicadas = 0
    errores = 0
    fuentes_procesadas = []

    for fuente in FUENTES_RSS:
        noticias = procesar_feed(fuente)
        fuentes_procesadas.append(fuente["nombre"])

        for datos in noticias:
            total += 1
            try:
                if obtener_contenido and not datos["contenido"]:
                    datos["contenido"] = obtener_contenido_completo(datos["url"])

                noticia = Noticia(**datos)
                db.add(noticia)
                db.commit()
                db.refresh(noticia)
                nuevas += 1
            except IntegrityError:
                db.rollback()
                duplicadas += 1
            except Exception as exc:
                db.rollback()
                errores += 1
                logger.error("Error guardando noticia '%s': %s", datos.get("url"), exc)

    return ActualizarRSSResponse(
        total_procesadas=total,
        nuevas=nuevas,
        duplicadas=duplicadas,
        errores=errores,
        fuentes=fuentes_procesadas,
    )
