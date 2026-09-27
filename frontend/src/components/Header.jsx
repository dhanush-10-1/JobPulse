import { Activity, BarChart3, BriefcaseBusiness, Menu, X } from 'lucide-react'
import { useState } from 'react'

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <header className="site-header">
      <a className="brand" href="#top" aria-label="JobPulse home">
        <span className="brand-mark"><Activity size={18} strokeWidth={2.5} /></span>
        <span>Job<span>Pulse</span></span>
      </a>
      <p className="brand-tagline">Discover and analyze opportunities</p>
      <button className="menu-button" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle navigation">
        {menuOpen ? <X size={20} /> : <Menu size={20} />}
      </button>
      <nav className={`main-nav ${menuOpen ? 'is-open' : ''}`}>
        <a className="active" href="#jobs" onClick={() => setMenuOpen(false)}><BriefcaseBusiness size={16} /> Jobs</a>
        <a href="#analytics" onClick={() => setMenuOpen(false)}><BarChart3 size={16} /> Analytics</a>
      </nav>
    </header>
  )
}
