import { useEffect, useRef, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { gsap } from 'gsap'
import { getEvento } from '../services/api'
import EventMap from '../components/EventMap'
import NewsImage from '../components/NewsImage'

const CATEGORY_COLORS = {
  'Orden público': { bg: '#FAE5E0', text: '#8C2A14' },
  'Convivencia':   { bg: '#E0E4EE', text: '#243060' },
  'Drogas':        { bg: '#EEE6DB', text: '#5C3A1E' },
  'Accidente':     { bg: '#F5EDD9', text: '#7A4F10' },
  'Protesta':      { bg: '#DFF0E4', text: '#1A5C2E' },
  'Emergencia':    { bg: '#E8F0DC', text: '#3A5918' },
}

export default function EventDetail() {
  const { id }      = useParams()
  const navigate    = useNavigate()
  const [evento,    setEvento]  = useState(null)
  const [loading,   setLoading] = useState(true)
  const [notFound,  setNotFound] = useState(false)
  const contentRef  = useRef(null)

  useEffect(() => {
    window.scrollTo(0, 0)
    async function load() {
      try {
        const data = await getEvento(id)
        if (!data) { setNotFound(true); return }
        setEvento(data)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  useEffect(() => {
    if (evento && contentRef.current) {
      gsap.from(contentRef.current.children, {
        opacity: 0, y: 20, stagger: 0.08, duration: 0.5, ease: 'power2.out',
      })
    }
  }, [evento])

  if (loading) {
    return (
      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-12 space-y-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-12 bg-slate-card border border-slate-border rounded-xl animate-pulse" />
        ))}
      </main>
    )
  }

  if (notFound || !evento) {
    return (
      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-20 text-center">
        <p className="text-5xl mb-4">🔍</p>
        <h2 className="text-ink text-xl font-semibold mb-2">Caso no encontrado</h2>
        <p className="text-ink-dim mb-6">No hay un caso con ID #{id}.</p>
        <Link to="/" className="px-4 py-2 rounded-lg bg-lilac/10 border border-lilac/30 text-lilac hover:bg-lilac/20 transition-colors text-sm">
          Volver al inicio
        </Link>
      </main>
    )
  }

  const badgeStyle = CATEGORY_COLORS[evento.categoria] || { bg: '#EDEAE2', text: '#6B5F52' }
  const fechaFmt    = new Date(evento.fecha + 'T00:00:00').toLocaleDateString('es-CO', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  })

  return (
    <main className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
      {/* Back */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-ink-muted hover:text-lilac transition-colors text-sm mb-6"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Volver
      </button>

      <div ref={contentRef} className="space-y-6">
        {/* Header card */}
        <div className="bg-slate-card border border-slate-border rounded-xl overflow-hidden">
          <NewsImage
            item={evento}
            alt={evento.titulo}
            wrapperClassName="w-full h-64 sm:h-80 overflow-hidden bg-slate-deep"
            imageClassName="w-full h-full object-cover"
          />
          
          <div className="p-6">
            <div className="flex flex-wrap items-center gap-2 mb-4">
              <span
                className="badge rounded-full text-[11px] font-semibold px-2.5 py-1"
                style={{ color: badgeStyle.text, background: badgeStyle.bg, border: `1px solid ${badgeStyle.bg}` }}
              >
                {evento.categoria}
              </span>
              <span className="text-ink-soft text-xs font-semibold">{fechaFmt}</span>
            </div>

          <h1 className="text-ink text-2xl font-bold leading-snug mb-4">
            {evento.titulo}
          </h1>

          <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-ink-muted">
            <span className="flex items-center gap-1.5">
              <svg className="w-4 h-4 text-lilac" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {evento.municipio}, {evento.departamento}
            </span>
            <span className="flex items-center gap-1.5">
              <svg className="w-4 h-4 text-lilac" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
              </svg>
              Fuente: {evento.fuente}
            </span>
          </div>
        </div>
        </div>{/* cierra header card */}

        {/* Summary */}
        <div className="bg-slate-card border border-slate-border rounded-xl p-6">
          <h2 className="text-lilac text-[11px] font-medium uppercase mb-3">Resumen del caso</h2>
          <p className="text-ink-muted leading-relaxed">{evento.resumen}</p>
          {evento.url && evento.url !== 'https://...' && (
            <a
              href={evento.url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-4 inline-flex items-center gap-1.5 text-lilac text-sm hover:underline"
            >
              Ver noticia original
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          )}
        </div>

        {/* Related news */}
        {evento.noticias_relacionadas?.length > 0 && (
          <div className="bg-slate-card border border-slate-border rounded-xl p-6">
            <h2 className="text-lilac text-[11px] font-medium uppercase mb-4">
              Notas relacionadas ({evento.noticias_relacionadas.length})
            </h2>
            <ul className="space-y-3">
              {evento.noticias_relacionadas.map((n, i) => (
                <li key={i} className="flex items-start justify-between gap-4 py-3 border-b border-slate-line last:border-0">
                  <div className="flex items-start gap-3 min-w-0">
                    <NewsImage
                      item={n}
                      alt={n.titulo}
                      wrapperClassName="w-20 h-14 rounded-md overflow-hidden bg-slate-deep shrink-0"
                      imageClassName="w-full h-full object-cover"
                    />
                    <div className="min-w-0">
                      <p className="text-ink text-sm font-medium">{n.titulo}</p>
                      <p className="text-ink-dim text-xs mt-0.5">{n.fuente}</p>
                    </div>
                  </div>
                  {n.url && n.url !== '#' && (
                    <a href={n.url} target="_blank" rel="noopener noreferrer"
                      className="shrink-0 text-lilac text-xs hover:underline">
                      Leer
                    </a>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Map */}
        {evento.lat && evento.lon && (
          <div className="bg-slate-card border border-slate-border rounded-xl overflow-hidden">
            <div className="px-6 pt-5 pb-3">
              <h2 className="text-lilac text-[11px] font-medium uppercase">Ubicación del caso</h2>
            </div>
            <EventMap eventos={[evento]} height="300px" />
          </div>
        )}
      </div>
    </main>
  )
}
