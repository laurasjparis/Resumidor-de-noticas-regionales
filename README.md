# Resumidor de Noticias Regionales — RSS + Geolocalización

Backend en **FastAPI** para captura, normalización, almacenamiento y geolocalización de noticias regionales centradas en **Medellín** y el **Valle de Aburrá**.

---

## Estructura del proyecto

```
backend/
├── app/
│   ├── main.py            # Punto de entrada FastAPI
│   ├── config.py          # Variables de entorno (pydantic-settings)
│   ├── database/
│   │   └── connection.py  # Engine SQLAlchemy y sesión
│   ├── geoloc/
│   │   ├── extractor.py   # Detección híbrida de lugares
│   │   ├── geocoder.py    # Geocoding con caché local
│   │   ├── normalizer.py  # Normalización de municipios/barrios/comunas
│   │   └── service.py     # Orquestación de geolocalización
│   ├── models/
│   │   ├── noticia.py     # Modelo ORM
│   │   ├── ubicacion.py   # Modelos ORM de ubicaciones y caché
│   │   └── schemas.py     # Schemas Pydantic (request/response)
│   ├── rss/
│   │   ├── fuentes.py     # Catálogo de feeds RSS y palabras clave
│   │   ├── parser.py      # Parseo feedparser + filtro regional
│   │   └── limpieza.py    # Limpieza HTML, clasificación y relevancia regional
│   └── routes/
│       ├── noticias.py    # GET /noticias, GET /noticias/{id}
│       ├── rss.py         # POST /rss/actualizar
│       └── geoloc.py      # Endpoints de geolocalización
├── alembic/               # Migraciones de base de datos
└── tests/
    ├── test_rss.py
    └── test_geoloc.py
```

---

## Instalación

```bash
cd backend

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env si se necesita PostgreSQL u otro ajuste
```

---

## Ejecutar el servidor

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La documentación interactiva queda disponible en:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/health` | Health check JSON |
| `GET` | `/noticias` | Listar noticias regionales guardadas |
| `GET` | `/noticias/{id}` | Obtener noticia por ID |
| `POST` | `/rss/actualizar` | Ingerir feeds RSS y filtrar solo contenido regional |
| `POST` | `/geoloc/procesar` | Geolocalizar noticias pendientes |
| `POST` | `/geoloc/procesar/{id}` | Geolocalizar una noticia puntual |
| `GET` | `/geoloc/noticias/{id}` | Ver ubicaciones detectadas para una noticia |
| `GET` | `/geoloc/eventos` | Listar eventos geográficos con detalle completo |
| `GET` | `/geoloc/mapa` | Payload compacto para frontend de mapa |

### Parámetros de `/noticias`

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Offset de paginación |
| `limit` | int | 50 | Máximo de resultados (máx. 200) |
| `fuente` | string | — | Filtrar por nombre de fuente |
| `categoria` | string | — | Filtrar por categoría (`general`, `orden_publico`) |

### Parámetros de `POST /rss/actualizar`

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `obtener_contenido` | bool | false | Si `true`, descarga el artículo completo (más lento) |

---

## Estructura JSON de una noticia

```json
{
  "id": 1,
  "titulo": "Balacera en Bello deja dos heridos",
  "fecha": "2026-05-12T14:30:00Z",
  "fuente": "El Colombiano",
  "url": "https://elcolombiano.com/...",
  "descripcion": "Dos personas resultaron heridas...",
  "contenido": "Texto completo del artículo...",
  "categoria": "orden_publico",
  "creado_en": "2026-05-12T15:00:00Z"
}
```

---

## Flujo backend

```text
RSS -> filtro regional Medellín/Valle -> tabla noticias -> geolocalización -> ubicaciones_noticia -> endpoints /geoloc/eventos y /geoloc/mapa
```

## Base de datos

Por defecto usa **SQLite** (`noticias.db` en la raíz de `backend/`).
Para producción, cambiar `DATABASE_URL` en `.env`:

```
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/noticias_db
```

El esquema se gestiona con **Alembic**.

```bash
alembic upgrade head
```

---

## Pruebas

```bash
pip install pytest
pytest tests/ -v
```

---

## Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./noticias.db` | Cadena de conexión a la BD |
| `APP_ENV` | `development` | Entorno de ejecución |
| `LOG_LEVEL` | `INFO` | Nivel de logging |
| `HTTP_TIMEOUT` | `10` | Timeout (seg) para descargar artículos |
| `MAX_NOTICIAS_PER_PAGE` | `50` | Resultados máximos por página |

---

## Integración con otros módulos

- **NLP**: consumir `GET /noticias?categoria=orden_publico` para procesar texto de `descripcion` y `contenido`.
- **Geolocalización**: consumir `GET /geoloc/noticias/{id}`, `GET /geoloc/eventos` o `GET /geoloc/mapa`.
- **Frontend React**: consumir `GET /noticias` para listado y `GET /geoloc/mapa` para marcadores.

---

## Fuentes RSS monitoreadas

| Fuente | Categoría base |
|--------|---------------|
| El Colombiano | general |
| Caracol Radio | general |
| Blu Radio | general |
| Minuto30 | general |
| Semana | general |
| Alerta Paisa | orden_publico |
| Q'Hubo | orden_publico |
