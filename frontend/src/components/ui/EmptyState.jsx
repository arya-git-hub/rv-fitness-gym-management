// src/components/ui/EmptyState.jsx
// Shown when a list/table has no data.
// Usage: <EmptyState icon={Users} title="No members yet" description="Add your first member." action={<Button>Add member</Button>} />

import { PackageOpen } from 'lucide-react'

export default function EmptyState({
  icon: Icon = PackageOpen,
  title = 'Nothing here yet',
  description,
  action,
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="w-16 h-16 rounded-2xl bg-surface-700 flex items-center justify-center mb-4">
        <Icon className="w-8 h-8 text-gray-500" />
      </div>
      <h3 className="text-base font-semibold text-gray-300 mb-1">{title}</h3>
      {description && <p className="text-sm text-gray-500 max-w-xs">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}
