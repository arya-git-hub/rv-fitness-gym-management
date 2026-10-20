// src/components/ui/Card.jsx
// Glass-style dark card container.
// Usage: <Card><Card.Header>Title</Card.Header><Card.Body>…</Card.Body></Card>

export default function Card({ children, className = '', hover = false }) {
  return (
    <div className={`
      bg-surface-800 border border-surface-700 rounded-xl
      ${hover ? 'card-hover cursor-pointer' : ''}
      ${className}
    `}>
      {children}
    </div>
  )
}

Card.Header = function CardHeader({ children, className = '' }) {
  return (
    <div className={`px-6 py-4 border-b border-surface-700 ${className}`}>
      {children}
    </div>
  )
}

Card.Body = function CardBody({ children, className = '' }) {
  return (
    <div className={`px-6 py-4 ${className}`}>
      {children}
    </div>
  )
}

Card.Footer = function CardFooter({ children, className = '' }) {
  return (
    <div className={`px-6 py-4 border-t border-surface-700 ${className}`}>
      {children}
    </div>
  )
}
