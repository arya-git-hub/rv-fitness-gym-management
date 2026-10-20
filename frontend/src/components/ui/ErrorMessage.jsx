// src/components/ui/ErrorMessage.jsx
// Shows an API or validation error with a retry button.
// Usage: <ErrorMessage message={error.message} onRetry={refetch} />

import { AlertCircle } from 'lucide-react'
import Button from './Button'

export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center gap-3">
      <AlertCircle className="w-10 h-10 text-red-400" />
      <p className="text-sm text-red-300 max-w-sm">{message || 'Something went wrong.'}</p>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          Try again
        </Button>
      )}
    </div>
  )
}
