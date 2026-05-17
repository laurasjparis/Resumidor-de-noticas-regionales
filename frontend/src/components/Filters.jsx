import { useState, useEffect } from 'react'

const CATEGORIAS = ['Todas', 'Orden público', 'Convivencia', 'Drogas', 'Accidente', 'Protesta', 'Emergencia', 'General']

export default function Filters({ eventos, onFilter }) {
  const [q,          setQ]          = useState('')
  const [municipio,  setMunicipio]  = useState('')
  const [categoria,  setCategoria]  = useState('')
  const [fecha,      setFecha]      = useState('')

  const municipios = ['Todos', ...new Set(eventos.map((e) => e.municipio).sort())]

  useEffect(() => {
    onFilter({
      q:         q.trim(),
      municipio: municipio === 'Todos' ? '' : municipio,
      categoria: categoria === 'Todas' ? '' : categoria,
      fecha,
    })
  }, [q, municipio, categoria, fecha])

  const hasFilters = q || (municipio && municipio !== 'Todos') || (categoria && categoria !== 'Todas') || fecha

  function reset() {
    setQ(''); setMunicipio(''); setCategoria(''); setFecha('')
  }

  const fieldCls =
    'w-full bg-slate-card border border-slate-border rounded-lg px-3 py-2 text-sm text-ink placeholder-ink-soft transition-colors'

  return (
    <div className="bg-slate-surface border border-slate-border rounded-xl p-[18px]">
      <div className="flex flex-wrap gap-3 items-end">
        {/* Search */}
        <div className="flex-1 min-w-[180px]">
          <label className="block text-[11px] text-ink-dim mb-1.5 font-medium uppercase">Buscar</label>
          <div className="relative">
            <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-lilac" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="Palabra clave..."
              value={q}
              onChange={(e) => setQ(e.target.value)}
              className={`${fieldCls} pl-8`}
            />
          </div>
        </div>

        {/* Municipio */}
        <div className="min-w-[140px]">
          <label className="block text-[11px] text-ink-dim mb-1.5 font-medium uppercase">Ciudad</label>
          <select value={municipio} onChange={(e) => setMunicipio(e.target.value)} className={fieldCls}>
            {municipios.map((m) => <option key={m}>{m}</option>)}
          </select>
        </div>

        {/* Categoría */}
        <div className="min-w-[150px]">
          <label className="block text-[11px] text-ink-dim mb-1.5 font-medium uppercase">Categoría</label>
          <select value={categoria} onChange={(e) => setCategoria(e.target.value)} className={fieldCls}>
            {CATEGORIAS.map((c) => <option key={c}>{c}</option>)}
          </select>
        </div>

        {/* Fecha */}
        <div className="min-w-[140px]">
          <label className="block text-[11px] text-ink-dim mb-1.5 font-medium uppercase">Fecha</label>
          <input
            type="date"
            value={fecha}
            onChange={(e) => setFecha(e.target.value)}
            className={`${fieldCls} [color-scheme:light]`}
          />
        </div>

        {/* Clear */}
        {hasFilters && (
          <button
            onClick={reset}
            className="px-3 py-2 rounded-lg text-sm text-ink-muted hover:text-lilac border border-slate-border hover:border-lilac transition-colors"
          >
            Limpiar
          </button>
        )}
      </div>
    </div>
  )
}
