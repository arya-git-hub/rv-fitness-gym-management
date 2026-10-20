// src/components/ui/Table.jsx
// Responsive, styled table wrapper.
// Usage:
//   <Table>
//     <Table.Head>
//       <Table.Row><Table.Th>Name</Table.Th><Table.Th>Status</Table.Th></Table.Row>
//     </Table.Head>
//     <Table.Body>
//       {items.map(item => (
//         <Table.Row key={item.id}>
//           <Table.Td>{item.name}</Table.Td>
//           <Table.Td><Badge>{item.status}</Badge></Table.Td>
//         </Table.Row>
//       ))}
//     </Table.Body>
//   </Table>

export default function Table({ children, className = '' }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-surface-700">
      <table className={`w-full text-sm text-left ${className}`}>
        {children}
      </table>
    </div>
  )
}

Table.Head = function THead({ children }) {
  return (
    <thead className="bg-surface-700 text-xs text-gray-400 uppercase tracking-wider">
      {children}
    </thead>
  )
}

Table.Body = function TBody({ children }) {
  return (
    <tbody className="divide-y divide-surface-700 bg-surface-800">
      {children}
    </tbody>
  )
}

Table.Row = function TRow({ children, onClick, className = '' }) {
  return (
    <tr
      className={`
        transition-colors duration-100
        ${onClick ? 'cursor-pointer hover:bg-surface-700' : 'hover:bg-surface-700/50'}
        ${className}
      `}
      onClick={onClick}
    >
      {children}
    </tr>
  )
}

Table.Th = function Th({ children, className = '' }) {
  return (
    <th className={`px-4 py-3 font-medium ${className}`}>{children}</th>
  )
}

Table.Td = function Td({ children, className = '' }) {
  return (
    <td className={`px-4 py-3 text-gray-300 ${className}`}>{children}</td>
  )
}
