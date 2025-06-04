import axios from 'axios'
import type { AxiosResponse } from 'axios'
import type { ApiResponse } from '@/types/api'

const api = axios.create({
  baseURL: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:3000/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add request interceptor for authentication
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const useApi = () => {
  return {
    get: <T>(url: string, config = {}): Promise<AxiosResponse<ApiResponse<T>>> => 
      api.get<ApiResponse<T>>(url, config),
    post: <T>(url: string, data = {}, config = {}): Promise<AxiosResponse<ApiResponse<T>>> => 
      api.post<ApiResponse<T>>(url, data, config),
    put: <T>(url: string, data = {}, config = {}): Promise<AxiosResponse<ApiResponse<T>>> => 
      api.put<ApiResponse<T>>(url, data, config),
    delete: <T>(url: string, config = {}): Promise<AxiosResponse<ApiResponse<T>>> => 
      api.delete<ApiResponse<T>>(url, config)
  }
} 