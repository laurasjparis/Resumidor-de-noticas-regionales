from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.geoloc.service import (
    listar_eventos_geograficos,
    obtener_ubicaciones_noticia,
    procesar_noticia,
    procesar_noticias_pendientes,
)
from app.models.noticia import Noticia
from app.models.schemas import (
    EventoMapaResponse,
    EventoGeograficoResponse,
    GeolocNoticiaResponse,
    GeolocProcesamientoResponse,
)

router = APIRouter(prefix="/geoloc", tags=["geoloc"])


@router.post("/procesar", response_model=GeolocProcesamientoResponse)
def procesar_geoloc(
    limit: int | None = Query(None, ge=1, le=500),
    forzar_reproceso: bool = False,
    db: Session = Depends(get_db),
):
    return procesar_noticias_pendientes(
        db,
        limit=limit,
        forzar_reproceso=forzar_reproceso,
    )


@router.post("/procesar/{noticia_id}", response_model=GeolocProcesamientoResponse)
def procesar_geoloc_noticia(
    noticia_id: int,
    forzar_reproceso: bool = False,
    db: Session = Depends(get_db),
):
    noticia = db.query(Noticia).filter(Noticia.id == noticia_id).first()
    if not noticia:
        raise HTTPException(status_code=404, detail="Noticia no encontrada")

    try:
        resultado = procesar_noticia(
            db,
            noticia_id,
            forzar_reproceso=forzar_reproceso,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error procesando noticia: {exc}") from exc

    return GeolocProcesamientoResponse(
        total_evaluadas=1,
        total_con_ubicaciones=1 if resultado and resultado.con_ubicaciones else 0,
        total_sin_ubicaciones=0 if resultado and resultado.con_ubicaciones else 1,
        total_errores=0,
    )


@router.get("/noticias/{noticia_id}", response_model=GeolocNoticiaResponse)
def obtener_geoloc_noticia(noticia_id: int, db: Session = Depends(get_db)):
    noticia = db.query(Noticia).filter(Noticia.id == noticia_id).first()
    if not noticia:
        raise HTTPException(status_code=404, detail="Noticia no encontrada")

    ubicaciones = obtener_ubicaciones_noticia(db, noticia_id)
    return GeolocNoticiaResponse(noticia_id=noticia_id, ubicaciones=ubicaciones)


@router.get("/eventos", response_model=list[EventoGeograficoResponse])
def listar_eventos(
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
    categoria: str | None = None,
    municipio: str | None = None,
    solo_principal: bool = True,
    db: Session = Depends(get_db),
):
    filas = listar_eventos_geograficos(
        db,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        categoria=categoria,
        municipio=municipio,
        solo_principal=solo_principal,
    )
    return [
        EventoGeograficoResponse(
            noticia_id=noticia.id,
            titulo=noticia.titulo,
            fecha=noticia.fecha,
            categoria=noticia.categoria,
            fuente=noticia.fuente,
            url=noticia.url,
            descripcion=noticia.descripcion,
            ubicacion=ubicacion,
        )
        for noticia, ubicacion in filas
    ]


@router.get("/mapa", response_model=list[EventoMapaResponse])
def listar_eventos_mapa(
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
    categoria: str | None = None,
    municipio: str | None = None,
    db: Session = Depends(get_db),
):
    filas = listar_eventos_geograficos(
        db,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        categoria=categoria,
        municipio=municipio,
        solo_principal=True,
    )
    return [
        EventoMapaResponse(
            noticia_id=noticia.id,
            titulo=noticia.titulo,
            fecha=noticia.fecha,
            categoria=noticia.categoria,
            fuente=noticia.fuente,
            url=noticia.url,
            descripcion=noticia.descripcion,
            lugar=ubicacion.lugar_normalizado,
            tipo_lugar=ubicacion.tipo_lugar,
            latitud=ubicacion.latitud,
            longitud=ubicacion.longitud,
            precision=ubicacion.precision,
        )
        for noticia, ubicacion in filas
    ]
