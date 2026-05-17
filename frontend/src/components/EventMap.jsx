import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import { Link } from 'react-router-dom'
import 'leaflet/dist/leaflet.css'

const COLOMBIA_CENTER = [4.5709, -74.2973]

export default function EventMap({ eventos = [], height = '420px' }) {
  const eventosConUbicacion = eventos.filter((e) =>
    Number.isFinite(Number(e.lat)) && Number.isFinite(Number(e.lon))
  )

  if (eventosConUbicacion.length === 0) {
    return (
      <div
        className="rounded-xl overflow-hidden border border-slate-border bg-slate-surface flex items-center justify-center text-center px-6"
        style={{ height }}
      >
        <div>
          <p className="text-ink font-semibold">Sin ubicaciones para mostrar</p>
          <p className="text-ink-muted text-sm mt-1">
            Las noticias actuales del backend no incluyen coordenadas.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-xl overflow-hidden border border-slate-border" style={{ height }}>
      <MapContainer
        center={COLOMBIA_CENTER}
        zoom={7}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {eventosConUbicacion.map((e, index) => (
          <CircleMarker
            key={e.evento_id}
            center={[e.lat, e.lon]}
            radius={8}
            pathOptions={{
              fillColor: index === 0 ? '#C84B2F' : '#E8A020',
              fillOpacity: 0.9,
              color: '#FFFFFF',
              weight: 2,
            }}
          >
            <Popup minWidth={220}>
              <div className="p-1">
                <p className="font-semibold text-sm leading-snug mb-1">{e.titulo}</p>
                <p className="text-xs text-ink-muted leading-relaxed mb-2 line-clamp-3">{e.resumen}</p>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-ink-dim">📍 {e.municipio}</span>
                  <span className="text-ink-dim font-semibold">{e.fecha}</span>
                </div>
                <Link
                  to={`/eventos/${e.evento_id}`}
                  className="mt-2 inline-block text-xs text-lilac hover:underline"
                >
                  Ver detalle
                </Link>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  )
}
