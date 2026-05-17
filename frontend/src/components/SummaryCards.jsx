import { useEffect, useRef } from 'react'
import { gsap } from 'gsap'

function StatCard({ icon, label, value, sub, accent, featured = false }) {
  const cardRef = useRef(null)
  const valRef  = useRef(null)

  useEffect(() => {
    gsap.from(cardRef.current, { opacity: 0, y: 24, duration: 0.5, ease: 'power2.out' })
    if (typeof value === 'number') {
      gsap.from({ n: 0 }, {
        n: value,
        duration: 1.2,
        ease: 'power2.out',
        onUpdate() {
          if (valRef.current) valRef.current.textContent = Math.round(this.targets()[0].n).toLocaleString('es-CO')
        },
      })
    }
  }, [value])

  return (
    <div
      ref={cardRef}
      className={`card-hover border rounded-xl p-[18px] flex gap-3 ${
        featured
          ? 'sm:col-span-2 bg-ink border-ink flex-col sm:flex-row sm:items-center sm:justify-between'
          : 'bg-slate-card border-slate-border flex-col'
      }`}
    >
      <div className="flex items-center justify-between">
        <div
          className={`${featured ? 'w-11 h-11 text-xl' : 'w-9 h-9 text-lg'} rounded-lg flex items-center justify-center`}
          style={{
            background: featured ? '#C84B2F' : `${accent}18`,
            border: `1px solid ${featured ? '#C84B2F' : `${accent}45`}`,
            color: featured ? '#F5F2EC' : accent,
          }}
        >
          {icon}
        </div>
        <span className={`text-[11px] font-medium uppercase ${featured ? 'text-[#E8A020] sm:ml-4' : 'text-ink-dim'}`}>
          {label}
        </span>
      </div>
      <div className={featured ? 'sm:text-right' : ''}>
        <p ref={valRef} className={`${featured ? 'text-[40px] text-slate-deep' : 'text-3xl text-ink'} font-bold leading-none`}>
          {typeof value === 'number' ? value.toLocaleString('es-CO') : value}
        </p>
        {sub && <p className={`${featured ? 'text-sm text-[#D5CFC4]' : 'text-xs text-ink-soft'} mt-2`}>{sub}</p>}
      </div>
    </div>
  )
}

export default function SummaryCards({ stats, loading }) {
  if (loading) {
    return (
      <div className="grid sm:grid-cols-2 gap-4">
        {Array.from({ length: 2 }).map((_, i) => (
          <div key={i} className="bg-slate-card border border-slate-border rounded-xl p-[18px] h-28 animate-pulse" />
        ))}
      </div>
    )
  }

  const cards = [
    {
      icon: '🕐',
      label: 'Actualización',
      value: stats?.ultima_actualizacion
        ? new Date(stats.ultima_actualizacion).toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })
        : '--:--',
      sub: stats?.ultima_actualizacion
        ? new Date(stats.ultima_actualizacion).toLocaleDateString('es-CO')
        : 'Sin datos',
      accent: '#C84B2F',
      featured: true,
    },
    {
      icon: '📰',
      label: 'Noticias',
      value: stats?.total_noticias ?? 0,
      sub: 'tomadas de fuentes RSS',
      accent: '#C84B2F',
    },
  ]

  return (
    <div className="grid sm:grid-cols-2 gap-4">
      {cards.map((c) => (
        <StatCard key={c.label} {...c} />
      ))}
    </div>
  )
}
