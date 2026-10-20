// src/layouts/PublicLayout.jsx
// Shell for all public-facing pages (header + footer).

import { useState, useEffect } from 'react'
import { Link, NavLink, useLocation } from 'react-router-dom'
import { Menu, X, Dumbbell, Phone } from 'lucide-react'

const NAV_LINKS = [
  { to: '/',           label: 'Home' },
  { to: '/about',      label: 'About' },
  { to: '/membership', label: 'Membership' },
  { to: '/events',     label: 'Events' },
  { to: '/blog',       label: 'Blog' },
  { to: '/contact',    label: 'Contact' },
]

export default function PublicLayout({ children }) {
  const [menuOpen, setMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const location = useLocation()

  // Close mobile menu on route change
  useEffect(() => setMenuOpen(false), [location])

  // Shrink header on scroll
  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handler)
    return () => window.removeEventListener('scroll', handler)
  }, [])

  return (
    <div className="min-h-screen flex flex-col bg-surface-900">
      {/* ── Header ─────────────────────────────────────────────── */}
      <header className={`
        sticky top-0 z-40 transition-all duration-300
        ${scrolled ? 'glass shadow-xl py-3' : 'bg-transparent py-5'}
      `}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-9 h-9 gradient-brand rounded-xl flex items-center justify-center
                            group-hover:glow-brand transition-all duration-300">
              <Dumbbell className="w-5 h-5 text-white" />
            </div>
            <div className="leading-tight">
              <span className="font-display font-bold text-lg text-white">RV</span>
              <span className="font-display font-bold text-lg text-gradient"> Fitness</span>
              <p className="text-[10px] text-gray-500 -mt-0.5">Narsobawadi</p>
            </div>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-1">
            {NAV_LINKS.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  `px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-150
                   ${isActive
                     ? 'text-brand-400 bg-brand-500/10'
                     : 'text-gray-400 hover:text-white hover:bg-surface-700'
                   }`
                }
              >
                {label}
              </NavLink>
            ))}
          </nav>

          {/* CTA + mobile toggle */}
          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="hidden md:inline-flex items-center gap-2 px-5 py-2 rounded-lg
                         gradient-brand text-white text-sm font-medium
                         hover:opacity-90 transition-opacity glow-brand"
            >
              Member Login
            </Link>

            <button
              className="md:hidden p-2 rounded-lg bg-surface-700 text-gray-400 hover:text-white"
              onClick={() => setMenuOpen((v) => !v)}
              aria-label={menuOpen ? 'Close menu' : 'Open menu'}
            >
              {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile drawer */}
        {menuOpen && (
          <div className="md:hidden glass border-t border-surface-700 px-4 py-4">
            <nav className="flex flex-col gap-1 mb-4">
              {NAV_LINKS.map(({ to, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={to === '/'}
                  className={({ isActive }) =>
                    `px-4 py-3 rounded-lg text-sm font-medium transition-colors
                     ${isActive
                       ? 'text-brand-400 bg-brand-500/10'
                       : 'text-gray-400 hover:text-white hover:bg-surface-700'
                     }`
                  }
                >
                  {label}
                </NavLink>
              ))}
            </nav>
            <Link
              to="/login"
              className="block w-full text-center px-5 py-2.5 rounded-lg
                         gradient-brand text-white text-sm font-medium"
            >
              Member Login
            </Link>
          </div>
        )}
      </header>

      {/* ── Page content ───────────────────────────────────────── */}
      <main className="flex-1 page-enter">{children}</main>

      {/* ── Footer ─────────────────────────────────────────────── */}
      <footer className="bg-surface-800 border-t border-surface-700 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Brand */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 gradient-brand rounded-lg flex items-center justify-center">
                  <Dumbbell className="w-4 h-4 text-white" />
                </div>
                <span className="font-display font-bold text-white">RV Fitness</span>
              </div>
              <p className="text-sm text-gray-500 leading-relaxed">
                Your transformation starts here. Premium gym in the heart of Narsobawadi.
              </p>
            </div>

            {/* Quick links */}
            <div>
              <h4 className="text-sm font-semibold text-white mb-3 uppercase tracking-wider">Quick Links</h4>
              <ul className="space-y-2">
                {NAV_LINKS.map(({ to, label }) => (
                  <li key={to}>
                    <Link to={to} className="text-sm text-gray-500 hover:text-brand-400 transition-colors">
                      {label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Contact */}
            <div>
              <h4 className="text-sm font-semibold text-white mb-3 uppercase tracking-wider">Contact</h4>
              <div className="flex items-start gap-2 text-sm text-gray-500">
                <Phone className="w-4 h-4 mt-0.5 text-brand-500 shrink-0" />
                <span>+91 XXXXX XXXXX</span>
              </div>
              <p className="text-sm text-gray-500 mt-2">Narsobawadi, Maharashtra, India</p>
              <p className="text-sm text-gray-500 mt-1">rvfitness@email.com</p>
            </div>
          </div>

          <div className="border-t border-surface-700 mt-8 pt-6 text-center text-xs text-gray-600">
            © {new Date().getFullYear()} RV Fitness, Narsobawadi. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  )
}
