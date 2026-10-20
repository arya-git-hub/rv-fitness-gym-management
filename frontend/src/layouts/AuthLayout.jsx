// src/layouts/AuthLayout.jsx
// Shell for login / register pages — centered card with brand logo.

import { Link } from 'react-router-dom'
import { Dumbbell } from 'lucide-react'

export default function AuthLayout({ children, title, subtitle }) {
  return (
    <div className="min-h-screen bg-surface-900 flex items-center justify-center p-4"
         style={{
           backgroundImage: 'radial-gradient(ellipse at 20% 50%, rgba(249,115,22,0.07) 0%, transparent 60%), radial-gradient(ellipse at 80% 20%, rgba(234,88,12,0.05) 0%, transparent 60%)'
         }}>
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <Link to="/" className="flex items-center gap-3 group mb-6">
            <div className="w-12 h-12 gradient-brand rounded-2xl flex items-center justify-center
                            group-hover:glow-brand transition-all duration-300">
              <Dumbbell className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="font-display font-bold text-xl text-white">RV Fitness</p>
              <p className="text-xs text-gray-500">Narsobawadi</p>
            </div>
          </Link>
          {title && <h1 className="text-2xl font-display font-bold text-white">{title}</h1>}
          {subtitle && <p className="text-sm text-gray-400 mt-1 text-center">{subtitle}</p>}
        </div>

        {/* Card */}
        <div className="bg-surface-800 border border-surface-700 rounded-2xl p-8 shadow-2xl">
          {children}
        </div>
      </div>
    </div>
  )
}
