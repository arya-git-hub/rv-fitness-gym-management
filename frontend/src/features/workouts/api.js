import api from '../../lib/axios'

export async function getWorkoutUser() {
  const { data } = await api.get('/api/workouts/me')
  return data
}

export async function getWorkoutOptions() {
  const { data } = await api.get('/api/workouts/options')
  return data
}

export async function getWorkoutPlans({ page, pageSize, search }) {
  const { data } = await api.get('/api/workouts', {
    params: { page, page_size: pageSize, search: search || undefined },
  })
  return data
}

export async function createWorkoutPlan(payload) {
  const { data } = await api.post('/api/workouts', payload)
  return data
}

export async function updateWorkoutPlan({ id, ...payload }) {
  const { data } = await api.put(`/api/workouts/${id}`, payload)
  return data
}

export async function deleteWorkoutPlan(id) {
  await api.delete(`/api/workouts/${id}`)
}
