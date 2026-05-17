import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.connection import init_db
from app.routes import geoloc, noticias, rss
from app.rss.scheduler import iniciar_scheduler
from app.routes import eventos

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    iniciar_scheduler(intervalo_horas=12)
    yield


app = FastAPI(
    title="Resumidor de Noticias Regionales",
    redirect_slashes=False,
    description=(
        "API para captura, normalización y consulta de noticias regionales colombianas. "
        "Ingestión RSS regional y geolocalización para Medellín y Valle de Aburrá."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restringir en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(noticias.router)
app.include_router(rss.router)
app.include_router(geoloc.router)
app.include_router(eventos.router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "mensaje": "API de noticias regionales activa"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
