import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.connection import init_db
from app.routes import noticias, rss
from app.rss.scheduler import iniciar_scheduler

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="Resumidor de Noticias Regionales",
    redirect_slashes=False,
    description=(
        "API para captura, normalización y consulta de noticias regionales colombianas. "
        "Módulo 1: Ingestión RSS."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restringir en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    iniciar_scheduler(intervalo_horas=12)


app.include_router(noticias.router)
app.include_router(rss.router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "mensaje": "API de noticias regionales activa"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
