from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl


class NoticiaBase(BaseModel):
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

    class Config:
        from_attributes = True


class ActualizarRSSResponse(BaseModel):
    total_procesadas: int
    nuevas: int
    duplicadas: int
    errores: int
    fuentes: list[str]
