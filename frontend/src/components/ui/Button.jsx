// src/components/ui/Button.jsx
// Usage:
//   <Button>Save</Button>
//   <Button variant="outline" size="sm" isLoading>Saving…</Button>
//   <Button variant="danger" onClick={handleDelete}>Delete</Button>

import { Loader2 } from 'lucide-react'

const variants = {
  primary: 'gradient-brand text-white hover:opacity-90 glow-brand',
  outline: 'border border-brand-500 text-brand-400 hover:bg-brand-500/10',
  ghost:   'text-gray-300 hover:bg-surface-700 hover:text-white',
  danger:  'bg-red-600 text-white hover:bg-red-700',
  secondary: 'bg-surface-600 text-gray-200 hover:bg-surface-500',
}

const sizes = {
  sm:  'px-3 py-1.5 text-sm',
  md:  'px-5 py-2.5 text-sm',
  lg:  'px-7 py-3 text-base',
  icon:'p-2',
}

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  className = '',
  ...props
}) {
  return (
    <button
      className={`
        inline-flex items-center justify-center gap-2 font-medium rounded-lg
        transition-all duration-200 focus:outline-none focus-visible:ring-2
        focus-visible:ring-brand-500 focus-visible:ring-offset-2 focus-visible:ring-offset-surface-900
        disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer
        ${variants[variant]} ${sizes[size]} ${className}
      `}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
      {children}
    </button>
  )
}
