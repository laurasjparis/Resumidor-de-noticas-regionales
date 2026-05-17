from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from app.database.connection import get_db
from app.models.evento import Evento, EventoNoticia
from app.nlp.service import procesar_eventos

router = APIRouter(prefix="/eventos", tags=["eventos"])


@router.post("/procesar")
def procesar(
    umbral: float = Query(0.55, ge=0.0, le=1.0, description="Umbral de similitud (0.0 a 1.0)"),
    db: Session = Depends(get_db),
):
    """
    Ejecuta el pipeline completo:
    embeddings → clustering → resúmenes con Ollama.
    """
    resultado = procesar_eventos(db, umbral=umbral)
    return resultado


@router.get("/")
def listar_eventos(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    categoria: str | None = None,
    db: Session = Depends(get_db),
):
    """Lista todos los eventos con su resumen."""
    query = db.query(Evento).order_by(Evento.fecha_inicio.desc())
    if categoria:
        query = query.filter(Evento.categoria == categoria)
    eventos = query.offset(skip).limit(limit).all()

    return [
        {
            "id": e.id,
            "titulo": e.titulo,
            "resumen": e.resumen,
            "categoria": e.categoria,
            "fecha_inicio": e.fecha_inicio,
            "fecha_fin": e.fecha_fin,
            "cantidad_noticias": e.cantidad_noticias,
            "creado_en": e.creado_en,
        }
        for e in eventos
    ]


@router.get("/{evento_id}")
def detalle_evento(evento_id: int, db: Session = Depends(get_db)):
    """Detalle de un evento con todas sus noticias asociadas."""
    evento = (
        db.query(Evento)
        .options(joinedload(Evento.noticias).joinedload(EventoNoticia.noticia))
        .filter(Evento.id == evento_id)
        .first()
    )
    if not evento:
        return {"error": "Evento no encontrado"}

    return {
        "id": evento.id,
        "titulo": evento.titulo,
        "resumen": evento.resumen,
        "categoria": evento.categoria,
        "fecha_inicio": evento.fecha_inicio,
        "fecha_fin": evento.fecha_fin,
        "cantidad_noticias": evento.cantidad_noticias,
        "noticias": [
            {
                "id": en.noticia.id,
                "titulo": en.noticia.titulo,
                "fecha": en.noticia.fecha,
                "fuente": en.noticia.fuente,
                "url": en.noticia.url,
                "descripcion": en.noticia.descripcion,
                "similitud": en.similitud,
            }
            for en in evento.noticias
        ],
    }