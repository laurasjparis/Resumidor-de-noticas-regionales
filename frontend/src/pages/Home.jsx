import { useEffect, useState, useMemo } from 'react'
import { getEventos } from '../services/api'
import EventCard from '../components/EventCard'
import EventMap  from '../components/EventMap'
import Filters   from '../components/Filters'

export default function Home() {
  const [eventos,  setEventos]  = useState([])
  const [loading,  setLoading]  = useState(true)
  const [filters,  setFilters]  = useState({})
  const [view,     setView]     = useState('grid') // 'grid' | 'map'

  useEffect(() => {
    async function load() {
      try {
        const evs = await getEventos()
        setEventos(evs)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const filtered = useMemo(() => {
    return eventos.filter((e) => {
      if (filters.municipio && e.municipio !== filters.municipio) return false
      if (filters.categoria && e.categoria !== filters.categoria)  return false
      if (filters.fecha     && e.fecha     !== filters.fecha)       return false
      if (filters.q) {
        const q = filters.q.toLowerCase()
        if (!e.titulo.toLowerCase().includes(q) && !e.resumen.toLowerCase().includes(q)) return false
      }
      return true
    })
  }, [eventos, filters])

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8">
      {/* Filters */}
      <section>
        <Filters eventos={eventos} onFilter={setFilters} />
      </section>

      {/* View toggle + count */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-ink font-semibold text-[17px]">Casos registrados</h2>
            <p className="text-ink-dim text-sm">
              {loading ? 'Cargando...' : `${filtered.length} caso${filtered.length !== 1 ? 's' : ''} en la lista`}
            </p>
          </div>
          <div className="flex items-center gap-1 bg-slate-surface border border-slate-border rounded-lg p-1">
            {[
              { key: 'grid', icon: (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
              )},
              { key: 'map', icon: (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                </svg>
              )},
            ].map(({ key, icon }) => (
              <button
                key={key}
                onClick={() => setView(key)}
                className={`p-1.5 rounded-md transition-colors ${
                  view === key ? 'bg-ink text-slate-deep' : 'text-ink-muted hover:text-ink'
                }`}
              >
                {icon}
              </button>
            ))}
          </div>
        </div>

        {view === 'map' ? (
          <EventMap eventos={filtered} height="500px" />
        ) : loading ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="bg-slate-card border border-slate-border rounded-xl h-52 animate-pulse" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16 text-ink-dim">
            <p className="text-4xl mb-3">🔍</p>
            <p className="font-medium">No hay casos con esos filtros.</p>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((e) => <EventCard key={e.evento_id} evento={e} />)}
          </div>
        )}
      </section>

      {/* Inline mini-map when in grid mode */}
      {view === 'grid' && filtered.length > 0 && (
        <section>
          <h2 className="text-ink font-semibold text-[17px] mb-4">Mapa de casos</h2>
          <EventMap eventos={filtered} height="380px" />
        </section>
      )}
    </main>
  )
}
