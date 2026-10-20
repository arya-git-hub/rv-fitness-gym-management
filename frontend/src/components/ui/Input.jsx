// src/components/ui/Input.jsx
// A labelled input with error display.
// Usage:
//   <Input label="Email" type="email" error={errors.email?.message} {...register('email')} />

import { forwardRef } from 'react'

const Input = forwardRef(function Input(
  { label, error, hint, className = '', id, ...props },
  ref
) {
  const inputId = id || label?.toLowerCase().replace(/\s+/g, '-')

  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-gray-300">
          {label}
        </label>
      )}
      <input
        id={inputId}
        ref={ref}
        className={`
          w-full px-4 py-2.5 rounded-lg text-sm
          bg-surface-700 border text-gray-100 placeholder-gray-500
          transition-colors duration-150 outline-none
          ${error
            ? 'border-red-500 focus:border-red-500'
            : 'border-surface-500 focus:border-brand-500'}
          ${className}
        `}
        {...props}
      />
      {hint && !error && <p className="text-xs text-gray-500">{hint}</p>}
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  )
})

export default Input
