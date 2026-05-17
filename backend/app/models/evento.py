from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base


class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(500), nullable=False)
    resumen = Column(Text, nullable=False)
    categoria = Column(String(100), default="general")
    fecha_inicio = Column(DateTime(timezone=True), nullable=True)
    fecha_fin = Column(DateTime(timezone=True), nullable=True)
    cantidad_noticias = Column(Integer, default=0)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    noticias = relationship("EventoNoticia", back_populates="evento", cascade="all, delete-orphan")


class EventoNoticia(Base):
    __tablename__ = "evento_noticias"

    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id", ondelete="CASCADE"), nullable=False)
    noticia_id = Column(Integer, ForeignKey("noticias.id", ondelete="CASCADE"), nullable=False)
    similitud = Column(Float, nullable=True)

    evento = relationship("Evento", back_populates="noticias")
    noticia = relationship("Noticia")