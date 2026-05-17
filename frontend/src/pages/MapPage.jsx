import { useEffect, useState } from 'react'
import { getEventos } from '../services/api'
import EventMap from '../components/EventMap'

export default function MapPage() {
  const [eventos, setEventos] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getEventos().then(setEventos).finally(() => setLoading(false))
  }, [])

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      <div className="mb-6">
        <h1 className="text-ink text-2xl font-bold">Mapa de casos</h1>
        <p className="text-ink-dim text-sm mt-1">
          {loading ? 'Cargando casos...' : `${eventos.length} casos ubicados`}
        </p>
      </div>

      {loading ? (
        <div className="h-[600px] bg-slate-card border border-slate-border rounded-xl animate-pulse" />
      ) : (
        <EventMap eventos={eventos} height="600px" />
      )}
    </main>
  )
}
