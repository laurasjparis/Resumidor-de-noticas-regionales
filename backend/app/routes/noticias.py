import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.noticia import Noticia
from app.models.schemas import NoticiaResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/noticias", tags=["noticias"])


@router.get("", response_model=list[NoticiaResponse])
def listar_noticias(
    skip: int = Query(0, ge=0, description="Desplazamiento para paginación"),
    limit: int = Query(50, ge=1, le=200, description="Número máximo de resultados"),
    fuente: Optional[str] = Query(None, description="Filtrar por fuente (ej: 'Semana')"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    db: Session = Depends(get_db),
):
    """Retorna noticias almacenadas, ordenadas de más reciente a más antigua."""
    query = db.query(Noticia).order_by(Noticia.creado_en.desc())

    if fuente:
        query = query.filter(Noticia.fuente.ilike(f"%{fuente}%"))
    if categoria:
        query = query.filter(Noticia.categoria == categoria)

    return query.offset(skip).limit(limit).all()


@router.get("/{noticia_id}", response_model=NoticiaResponse)
def obtener_noticia(noticia_id: int, db: Session = Depends(get_db)):
    """Retorna una noticia específica por su ID."""
    noticia = db.query(Noticia).filter(Noticia.id == noticia_id).first()
    if not noticia:
        raise HTTPException(status_code=404, detail="Noticia no encontrada")
    return noticia
