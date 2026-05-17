# Frontend

Interfaz React/Vite para consultar las noticias regionales capturadas por el backend.

## Que hace

- Lista noticias desde `GET /noticias`.
- Muestra detalle desde `GET /noticias/{id}`.
- Calcula las estadisticas visibles a partir de las noticias recibidas.
- Muestra el mapa solo cuando una noticia trae `lat` y `lon`; si el backend no entrega coordenadas, muestra un estado vacio.
- Usa datos mock solo si `VITE_USE_MOCK=true`.

## Estructura principal

- `src/services/api.js`: cliente Axios y adaptador entre las rutas reales del backend y las fichas del front.
- `src/pages/Home.jsx`: vista principal con filtros y tarjetas.
- `src/pages/EventDetail.jsx`: detalle de una noticia.
- `src/pages/MapPage.jsx`: mapa de noticias con coordenadas.
- `src/components/`: tarjetas, filtros, mapa, header y resumen.

## Variables de entorno

Crear un `.env` local si se necesita cambiar la configuracion:

```env
VITE_API_URL=/api
VITE_USE_MOCK=false
```

Para desarrollo sin Docker tambien se puede usar:

```env
VITE_API_URL=http://localhost:8000
VITE_USE_MOCK=false
```

## Correr localmente

Desde la carpeta `frontend`:

```bash
npm install
npm run dev
```

La app queda en:

```text
http://localhost:5173
```

Si se usa `VITE_API_URL=/api`, Vite redirige `/api` al backend por el proxy definido en `vite.config.js`.

## Correr con Docker Compose

Desde la raiz del repositorio:

```bash
docker compose up --build
```

Servicios principales:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Postgres: `localhost:5432`

En Docker, el frontend se construye con `VITE_API_URL=/api` y Nginx sirve la app. Las llamadas a `/api/*` se redirigen internamente al servicio `backend:8000`.

## Build de produccion

Desde `frontend`:

```bash
npm run build
```

El resultado se genera en `dist/`, pero esa carpeta no se sube al repo porque es un artefacto generado.
