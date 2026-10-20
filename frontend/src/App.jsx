import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from './lib/queryClient'
import WorkoutsPage from './features/workouts/WorkoutsPage'

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/workouts" element={<WorkoutsPage />} />
          <Route path="*" element={<Navigate to="/workouts" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
