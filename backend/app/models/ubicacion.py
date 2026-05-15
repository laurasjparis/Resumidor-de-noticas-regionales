from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


class UbicacionNoticia(Base):
    __tablename__ = "ubicaciones_noticia"

    id = Column(Integer, primary_key=True, index=True)
    noticia_id = Column(Integer, ForeignKey("noticias.id"), nullable=False, index=True)
    texto_detectado = Column(Text, nullable=False)
    lugar_normalizado = Column(String(255), nullable=False)
    tipo_lugar = Column(String(50), nullable=False, default="otro")
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    precision = Column(String(50), nullable=False, default="baja")
    es_principal = Column(Boolean, nullable=False, default=False)
    fuente_extraccion = Column(String(50), nullable=False)
    fuente_geocodificacion = Column(String(50), nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    noticia = relationship("Noticia", back_populates="ubicaciones")

    __table_args__ = (
        UniqueConstraint(
            "noticia_id",
            "lugar_normalizado",
            "latitud",
            "longitud",
            name="uq_ubicacion_noticia_lugar_coord",
        ),
    )


class CacheGeocoding(Base):
    __tablename__ = "cache_geocoding"

    id = Column(Integer, primary_key=True, index=True)
    query_original = Column(Text, nullable=False)
    query_normalizada = Column(String(255), nullable=False, unique=True, index=True)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    tipo_lugar = Column(String(50), nullable=False, default="otro")
    precision = Column(String(50), nullable=False, default="baja")
    proveedor = Column(String(50), nullable=False, default="nominatim")
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
