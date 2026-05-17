import axios from 'axios'
import { mockEventos, mockNoticias, mockStats } from '../data/mockEvents'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

const client = axios.create({ baseURL: API_BASE, timeout: 8000 })

const delay = (ms) => new Promise((r) => setTimeout(r, ms))

const CATEGORY_LABELS = {
  orden_publico: 'Orden público',
  convivencia: 'Convivencia',
  drogas: 'Drogas',
  accidente: 'Accidente',
  protesta: 'Protesta',
  emergencia: 'Emergencia',
  general: 'General',
}

function formatDate(value) {
  if (!value) return ''
  return value.slice(0, 10)
}

function getSummary(noticia) {
  return noticia.descripcion || noticia.contenido || 'Sin resumen disponible.'
}

function getCategoryLabel(categoria) {
  return CATEGORY_LABELS[categoria] || categoria || 'General'
}

function normalizeNews(noticia) {
  const fecha = formatDate(noticia.fecha || noticia.creado_en)

  return {
    ...noticia,
    evento_id: noticia.id,
    titulo: noticia.titulo,
    resumen: getSummary(noticia),
    categoria: getCategoryLabel(noticia.categoria),
    municipio: noticia.municipio || 'Sin ubicación',
    departamento: noticia.departamento || 'Colombia',
    fecha,
    fuente: noticia.fuente,
    url: noticia.url,
    lat: noticia.lat ?? null,
    lon: noticia.lon ?? null,
    noticias_relacionadas: [
      {
        titulo: noticia.titulo,
        fuente: noticia.fuente,
        url: noticia.url,
      },
    ],
  }
}

function hasCoordinates(item) {
  return Number.isFinite(Number(item.lat)) && Number.isFinite(Number(item.lon))
}

function buildStats(noticias) {
  const fechas = noticias
    .map((noticia) => noticia.creado_en || noticia.fecha)
    .filter(Boolean)
    .sort()

  return {
    total_noticias: noticias.length,
    total_eventos: noticias.length,
    ciudades: new Set(noticias.map((noticia) => noticia.municipio).filter(Boolean)).size,
    ultima_actualizacion: fechas.at(-1) || null,
  }
}

async function fetchNoticias(params = {}) {
  const { data } = await client.get('/noticias', {
    params: {
      skip: params.skip ?? 0,
      limit: params.limit ?? 200,
      fuente: params.fuente || undefined,
      categoria: params.categoria || undefined,
    },
  })
  return data
}

export async function getStats() {
  if (USE_MOCK) {
    await delay(300)
    return mockStats
  }

  const noticias = await fetchNoticias({ limit: 200 })
  return buildStats(noticias)
}

export async function getEventos(params = {}) {
  if (USE_MOCK) {
    await delay(400)
    let items = [...mockEventos]
    if (params.municipio) items = items.filter((e) => e.municipio === params.municipio)
    if (params.categoria) items = items.filter((e) => e.categoria === params.categoria)
    if (params.fecha)     items = items.filter((e) => e.fecha === params.fecha)
    if (params.q)         items = items.filter((e) =>
      e.titulo.toLowerCase().includes(params.q.toLowerCase()) ||
      e.resumen.toLowerCase().includes(params.q.toLowerCase())
    )
    return items
  }

  const noticias = await fetchNoticias(params)
  return noticias.map(normalizeNews)
}

export async function getEventosMapa() {
  if (USE_MOCK) {
    await delay(300)
    return mockEventos.map(({ evento_id, titulo, resumen, municipio, fecha, lat, lon }) => ({
      evento_id, titulo, resumen, municipio, fecha, lat, lon,
    }))
  }

  const eventos = await getEventos()
  return eventos.filter(hasCoordinates)
}

export async function getEvento(id) {
  if (USE_MOCK) {
    await delay(300)
    return mockEventos.find((e) => e.evento_id === Number(id)) || null
  }

  try {
    const { data } = await client.get(`/noticias/${id}`)
    return normalizeNews(data)
  } catch (error) {
    if (error.response?.status === 404) return null
    throw error
  }
}

export async function getNoticias(params = {}) {
  if (USE_MOCK) {
    await delay(300)
    return mockNoticias
  }

  return fetchNoticias(params)
}
