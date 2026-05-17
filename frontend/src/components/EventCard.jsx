import { Link } from 'react-router-dom'
import NewsImage from './NewsImage'

const CATEGORY_COLORS = {
  'Orden público': { bg: '#FAE5E0', text: '#8C2A14', border: '#FAE5E0' },
  'Convivencia':   { bg: '#E0E4EE', text: '#243060', border: '#E0E4EE' },
  'Drogas':        { bg: '#EEE6DB', text: '#5C3A1E', border: '#EEE6DB' },
  'Accidente':     { bg: '#F5EDD9', text: '#7A4F10', border: '#F5EDD9' },
  'Protesta':      { bg: '#DFF0E4', text: '#1A5C2E', border: '#DFF0E4' },
  'Emergencia':    { bg: '#E8F0DC', text: '#3A5918', border: '#E8F0DC' },
}

function CategoryBadge({ categoria }) {
  const style = CATEGORY_COLORS[categoria] || { bg: '#EDEAE2', text: '#6B5F52', border: '#D5CFC4' }
  return (
    <span
      className="badge rounded-full text-[11px] font-semibold"
      style={{ background: style.bg, color: style.text, border: `1px solid ${style.border}` }}
    >
      {categoria}
    </span>
  )
}

export default function EventCard({ evento }) {
  const {
    evento_id, titulo, resumen, categoria,
    municipio, departamento, fecha, fuente,
  } = evento

  const fechaFmt = new Date(fecha + 'T00:00:00').toLocaleDateString('es-CO', {
    day: 'numeric', month: 'short', year: 'numeric',
  })

  return (
    <article className="card-hover bg-slate-card border border-slate-border rounded-xl p-[18px] flex flex-col gap-3 animate-slide-up">
      <NewsImage
        item={evento}
        alt={titulo}
        wrapperClassName="w-full h-40 sm:h-48 rounded-lg overflow-hidden mb-1 shrink-0 bg-slate-deep"
        imageClassName="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
      />

      {/* Top row */}
      <div className="flex items-start justify-between gap-2">
        <CategoryBadge categoria={categoria} />
        <time className="text-xs text-ink-soft font-semibold shrink-0">{fechaFmt}</time>
      </div>

      {/* Title */}
      <h3 className="text-ink font-semibold text-base leading-snug line-clamp-2">
        {titulo}
      </h3>

      {/* Summary */}
      <p className="text-ink-muted text-sm leading-relaxed line-clamp-3">
        {resumen}
      </p>

      {/* Meta */}
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-ink-dim">
        <span className="flex items-center gap-1">
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          {municipio}, {departamento}
        </span>
        <span className="flex items-center gap-1">
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
          </svg>
          {fuente}
        </span>
      </div>

      {/* Footer */}
      <div className="pt-1 border-t border-slate-line">
        <Link
          to={`/eventos/${evento_id}`}
          className="inline-flex items-center gap-1.5 text-lilac text-sm font-semibold hover:text-lilac-soft transition-colors"
        >
          Ver detalle
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </Link>
      </div>
    </article>
  )
}
