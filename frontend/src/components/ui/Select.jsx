// src/components/ui/Select.jsx
// Styled <select> wrapper.
// Usage: <Select label="Role" error={errors.role?.message} {...register('role')}>
//           <option value="">Pick one</option>
//           <option value="admin">Admin</option>
//         </Select>

import { forwardRef } from 'react'

const Select = forwardRef(function Select(
  { label, error, children, className = '', id, ...props },
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
      <select
        id={inputId}
        ref={ref}
        className={`
          w-full px-4 py-2.5 rounded-lg text-sm
          bg-surface-700 border text-gray-100
          transition-colors duration-150 outline-none appearance-none cursor-pointer
          ${error
            ? 'border-red-500 focus:border-red-500'
            : 'border-surface-500 focus:border-brand-500'}
          ${className}
        `}
        {...props}
      >
        {children}
      </select>
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  )
})

export default Select
