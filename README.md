# Resumidor de Noticias Regionales — Módulo 1: Ingestión RSS

Backend en **FastAPI** para captura, normalización y almacenamiento de noticias regionales colombianas desde feeds RSS. Incluye un frontend en **React/Vite** para consultar las noticias desde el navegador.

---

## Estructura del proyecto

```
backend/
├── app/
│   ├── main.py            # Punto de entrada FastAPI
│   ├── config.py          # Variables de entorno (pydantic-settings)
│   ├── database/
│   │   └── connection.py  # Engine SQLAlchemy y sesión
│   ├── models/
│   │   ├── noticia.py     # Modelo ORM
│   │   └── schemas.py     # Schemas Pydantic (request/response)
│   ├── rss/
│   │   ├── fuentes.py     # Catálogo de feeds RSS y palabras clave
│   │   ├── parser.py      # Parseo feedparser + extracción de contenido
│   │   └── limpieza.py    # Limpieza HTML y clasificación automática
│   └── routes/
│       ├── noticias.py    # GET /noticias, GET /noticias/{id}
│       └── rss.py         # POST /rss/actualizar
└── tests/
    └── test_rss.py        # Pruebas unitarias
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
| `GET` | `/noticias` | Listar noticias (paginación, filtros por fuente y categoría) |
| `GET` | `/noticias/{id}` | Obtener noticia por ID |
| `POST` | `/rss/actualizar` | Disparar ingestión de todos los feeds RSS |

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

## Base de datos

Por defecto usa **SQLite** (`noticias.db` en la raíz de `backend/`).
Para producción, cambiar `DATABASE_URL` en `.env`:

```
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/noticias_db
```

La tabla se crea automáticamente al iniciar el servidor.

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
- **Geolocalización**: idem, extraer topónimos de `titulo` + `contenido`.
- **Frontend React**: consumir `GET /noticias` con paginación y filtros.

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
