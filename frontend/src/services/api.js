import axios from 'axios'
import { mockEventos, mockNoticias, mockStats } from '../data/mockEvents'

// ── Cambia esta URL cuando el backend esté listo ──────────────────────────────
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
// ─────────────────────────────────────────────────────────────────────────────

const USE_MOCK = true // Cambia a false para usar la API real

const client = axios.create({ baseURL: API_BASE, timeout: 8000 })

const delay = (ms) => new Promise((r) => setTimeout(r, ms))

export async function getStats() {
  if (USE_MOCK) {
    await delay(300)
    return mockStats
  }
  const { data } = await client.get('/stats')
  return data
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
  const { data } = await client.get('/eventos', { params })
  return data
}

export async function getEventosMapa() {
  if (USE_MOCK) {
    await delay(300)
    return mockEventos.map(({ evento_id, titulo, resumen, municipio, fecha, lat, lon }) => ({
      evento_id, titulo, resumen, municipio, fecha, lat, lon,
    }))
  }
  const { data } = await client.get('/eventos/mapa')
  return data
}

export async function getEvento(id) {
  if (USE_MOCK) {
    await delay(300)
    return mockEventos.find((e) => e.evento_id === Number(id)) || null
  }
  const { data } = await client.get(`/eventos/${id}`)
  return data
}

export async function getNoticias(params = {}) {
  if (USE_MOCK) {
    await delay(300)
    return mockNoticias
  }
  const { data } = await client.get('/noticias', { params })
  return data
}
