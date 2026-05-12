from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./noticias.db"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # Segundos de timeout para peticiones HTTP al obtener contenido completo
    HTTP_TIMEOUT: int = 10

    # Máximo de noticias a retornar por defecto
    MAX_NOTICIAS_PER_PAGE: int = 50

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
