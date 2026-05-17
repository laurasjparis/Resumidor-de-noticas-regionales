import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Header      from './components/Header'
import Home        from './pages/Home'
import EventDetail from './pages/EventDetail'
import MapPage     from './pages/MapPage'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-deep text-ink">
        <Header />
        <Routes>
          <Route path="/"              element={<Home />}        />
          <Route path="/mapa"          element={<MapPage />}     />
          <Route path="/eventos/:id"   element={<EventDetail />} />
        </Routes>

        <footer className="bg-ink mt-16 py-6">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-ink-muted">
            <p>Monitor Regional · Noticias de orden público</p>
            <p>SINFO · {new Date().getFullYear()}</p>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  )
}
