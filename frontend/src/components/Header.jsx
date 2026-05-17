import { useEffect, useRef } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { gsap } from 'gsap'
import TextType from './TextType/TextType'

const NAV_LINKS = [
  { to: '/',     label: 'Inicio' },
  { to: '/mapa', label: 'Mapa'      },
]

export default function Header() {
  const headerRef = useRef(null)
  const location  = useLocation()

  useEffect(() => {
    gsap.fromTo(
      headerRef.current,
      { opacity: 0, y: -20 },
      { opacity: 1, y: 0, duration: 0.7, ease: 'power2.out' }
    )
  }, [])

  return (
    <header ref={headerRef} className="bg-slate-deep">
      {/* Top bar */}
      <div className="sticky top-0 z-50 border-b border-slate-line bg-slate-deep">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between">
          {/* Brand */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-8 h-8 rounded-lg bg-slate-surface border border-slate-border flex items-center justify-center">
              <svg className="w-4 h-4 text-lilac" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
            </div>
            <div>
              <p className="text-ink font-semibold text-sm leading-tight group-hover:text-lilac transition-colors">
                Monitor Regional
              </p>
              <p className="text-ink-dim text-xs">orden público · convivencia</p>
            </div>
          </Link>

          {/* Nav */}
          <nav className="flex items-center gap-1">
            {NAV_LINKS.map(({ to, label }) => (
              <Link
                key={to}
                to={to}
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  location.pathname === to
                    ? 'bg-ink text-slate-deep'
                    : 'text-ink-muted hover:text-ink'
                }`}
              >
                {label}
              </Link>
            ))}
          </nav>

          {/* Live badge */}
          <div className="hidden sm:flex items-center gap-2 text-xs text-lilac font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-lilac animate-pulse-slow" />
            EN VIVO
          </div>
        </div>
      </div>

      {/* Hero strip — only on home */}
      {location.pathname === '/' && (
        <div className="border-b border-slate-line">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-12 text-center flex flex-col items-center">
            <p className="text-ink-muted font-medium text-[11px] uppercase mb-4 inline-flex items-center gap-2 px-3 py-1 bg-slate-surface rounded-full border border-slate-border">
              <span className="w-1.5 h-1.5 rounded-full bg-lilac" />
              Seguimiento regional de noticias
            </p>
            <h1 className="text-[38px] sm:text-[50px] font-bold text-ink leading-tight tracking-normal mb-6">
              Orden público y{' '}
              <TextType
                as="em"
                text="convivencia"
                loop={false}
                initialDelay={300}
                typingSpeed={55}
                cursorCharacter="|"
                className="not-italic text-lilac"
                cursorClassName="text-lilac"
              />
            </h1>
            <p className="text-ink-muted text-[17px] max-w-2xl mx-auto leading-relaxed">
              Reunimos notas sobre seguridad y convivencia en municipios colombianos
              para ver rápido qué pasó, dónde ocurrió y de qué fuentes viene.
            </p>
          </div>
        </div>
      )}
    </header>
  )
}
