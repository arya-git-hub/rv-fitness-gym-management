// src/components/ui/Pagination.jsx
// Usage:
//   <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />

import { ChevronLeft, ChevronRight } from 'lucide-react'

export default function Pagination({ page, totalPages, onPageChange }) {
  if (totalPages <= 1) return null

  return (
    <div className="flex items-center justify-center gap-2 mt-6">
      <button
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        className="p-2 rounded-lg bg-surface-700 text-gray-400 hover:text-white hover:bg-surface-600
                   disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        aria-label="Previous page"
      >
        <ChevronLeft className="w-4 h-4" />
      </button>

      {/* Page numbers — show up to 5 */}
      {Array.from({ length: totalPages }, (_, i) => i + 1)
        .filter((p) => p === 1 || p === totalPages || Math.abs(p - page) <= 1)
        .reduce((acc, p, idx, arr) => {
          if (idx > 0 && p - arr[idx - 1] > 1) acc.push('…')
          acc.push(p)
          return acc
        }, [])
        .map((p, i) =>
          p === '…' ? (
            <span key={`ellipsis-${i}`} className="px-2 text-gray-500">…</span>
          ) : (
            <button
              key={p}
              onClick={() => onPageChange(p)}
              className={`
                w-9 h-9 rounded-lg text-sm font-medium transition-colors
                ${p === page
                  ? 'gradient-brand text-white'
                  : 'bg-surface-700 text-gray-400 hover:text-white hover:bg-surface-600'
                }
              `}
              aria-label={`Page ${p}`}
              aria-current={p === page ? 'page' : undefined}
            >
              {p}
            </button>
          )
        )}

      <button
        onClick={() => onPageChange(page + 1)}
        disabled={page >= totalPages}
        className="p-2 rounded-lg bg-surface-700 text-gray-400 hover:text-white hover:bg-surface-600
                   disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        aria-label="Next page"
      >
        <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  )
}
