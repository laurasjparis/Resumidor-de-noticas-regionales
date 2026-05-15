from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class NoticiaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    titulo: str
    fecha: Optional[datetime] = None
    fuente: str
    url: str
    descripcion: Optional[str] = None
    contenido: Optional[str] = None
    categoria: Optional[str] = "general"


class NoticiaCreate(NoticiaBase):
    pass


class NoticiaResponse(NoticiaBase):
    id: int
    creado_en: datetime


class ActualizarRSSResponse(BaseModel):
    total_procesadas: int
    nuevas: int
    duplicadas: int
    errores: int
    fuentes: list[str]


class UbicacionNoticiaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    noticia_id: int
    texto_detectado: str
    lugar_normalizado: str
    tipo_lugar: str
    latitud: float
    longitud: float
    precision: str
    es_principal: bool
    fuente_extraccion: str
    fuente_geocodificacion: str
    creado_en: datetime

class GeolocProcesamientoResponse(BaseModel):
    total_evaluadas: int
    total_con_ubicaciones: int
    total_sin_ubicaciones: int
    total_errores: int


class GeolocNoticiaResponse(BaseModel):
    noticia_id: int
    ubicaciones: list[UbicacionNoticiaResponse]


class EventoGeograficoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    noticia_id: int
    titulo: str
    fecha: Optional[datetime] = None
    categoria: Optional[str] = None
    fuente: str
    url: str
    descripcion: Optional[str] = None
    ubicacion: UbicacionNoticiaResponse


class EventoMapaResponse(BaseModel):
    noticia_id: int
    titulo: str
    fecha: Optional[datetime] = None
    categoria: Optional[str] = None
    fuente: str
    url: str
    descripcion: Optional[str] = None
    lugar: str
    tipo_lugar: str
    latitud: float
    longitud: float
    precision: str
