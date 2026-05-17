from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models.noticia import Noticia  # noqa: F401
    from app.models.ubicacion import CacheGeocoding, UbicacionNoticia  # noqa: F401
    from app.models.evento import Evento, EventoNoticia  # noqa: F401
    Base.metadata.create_all(bind=engine)