// src/lib/axios.js
// Axios instance pre-configured with the API base URL.
// Automatically attaches the Supabase JWT from localStorage.

import axios from 'axios'
import { supabase } from '../config/supabase'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor — attach the Bearer token from the active Supabase session.
api.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession()
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`
  }
  return config
})

// Response interceptor — normalize errors to { detail: "..." } shape.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail =
      error.response?.data?.detail ||
      error.message ||
      'Something went wrong. Please try again.'
    return Promise.reject(new Error(detail))
  }
)

export default api
