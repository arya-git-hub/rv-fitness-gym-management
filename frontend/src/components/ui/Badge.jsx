// src/components/ui/Badge.jsx
// Small status pill.
// Usage: <Badge variant="success">Active</Badge>

const variants = {
  default:  'bg-surface-600 text-gray-300',
  success:  'bg-emerald-900/50 text-emerald-400 ring-1 ring-emerald-500/30',
  warning:  'bg-amber-900/50  text-amber-400  ring-1 ring-amber-500/30',
  danger:   'bg-red-900/50    text-red-400    ring-1 ring-red-500/30',
  info:     'bg-blue-900/50   text-blue-400   ring-1 ring-blue-500/30',
  brand:    'bg-brand-900/50  text-brand-400  ring-1 ring-brand-500/30',
}

export default function Badge({ children, variant = 'default', className = '' }) {
  return (
    <span className={`
      inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium
      ${variants[variant]} ${className}
    `}>
      {children}
    </span>
  )
}
