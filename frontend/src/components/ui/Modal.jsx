// src/components/ui/Modal.jsx
// Accessible modal dialog with backdrop.
// Usage:
//   <Modal isOpen={open} onClose={() => setOpen(false)} title="Delete member?">
//     <p>Are you sure?</p>
//     <Modal.Footer>
//       <Button variant="ghost" onClick={() => setOpen(false)}>Cancel</Button>
//       <Button variant="danger" onClick={handleDelete}>Delete</Button>
//     </Modal.Footer>
//   </Modal>

import { useEffect } from 'react'
import { X } from 'lucide-react'

export default function Modal({ isOpen, onClose, title, children, size = 'md' }) {
  // Close on Escape key
  useEffect(() => {
    if (!isOpen) return
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [isOpen, onClose])

  // Prevent body scroll when open
  useEffect(() => {
    document.body.style.overflow = isOpen ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [isOpen])

  if (!isOpen) return null

  const sizes = { sm: 'max-w-md', md: 'max-w-lg', lg: 'max-w-2xl', xl: 'max-w-4xl' }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Panel */}
      <div className={`
        relative w-full ${sizes[size]} bg-surface-800 border border-surface-600
        rounded-2xl shadow-2xl animate-[fadeSlideIn_0.2s_ease_both]
      `}>
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-surface-700">
          <h2 id="modal-title" className="text-lg font-semibold text-white">
            {title}
          </h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-surface-700 transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-4">{children}</div>
      </div>
    </div>
  )
}

Modal.Footer = function ModalFooter({ children }) {
  return (
    <div className="flex items-center justify-end gap-3 pt-4 mt-4 border-t border-surface-700">
      {children}
    </div>
  )
}
