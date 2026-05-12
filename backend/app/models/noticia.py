from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.database.connection import Base


class Noticia(Base):
    __tablename__ = "noticias"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(500), nullable=False)
    fecha = Column(DateTime(timezone=True), nullable=True)
    fuente = Column(String(100), nullable=False)
    url = Column(String(1000), nullable=False)
    descripcion = Column(Text, nullable=True)
    contenido = Column(Text, nullable=True)
    categoria = Column(String(100), default="general")
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("url", name="uq_noticia_url"),)
