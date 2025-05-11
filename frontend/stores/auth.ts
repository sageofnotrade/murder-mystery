import { defineStore } from 'pinia'

interface User {
  id: string
  email: string
  psychological_traits?: Record<string, any>
  preferences?: Record<string, any>
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  loading: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    isAuthenticated: false,
    loading: false
  }),

  getters: {
    getUser: (state) => state.user,
    getIsAuthenticated: (state) => state.isAuthenticated,
    isLoading: (state) => state.loading
  },

  actions: {
    async login(email: string, password: string) {
      this.loading = true
      try {
        // TODO: Implement Supabase authentication
        this.isAuthenticated = true
        this.user = {
          id: 'temp-id',
          email
        }
      } catch (error) {
        console.error('Login error:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async logout() {
      this.loading = true
      try {
        // TODO: Implement Supabase logout
        this.user = null
        this.isAuthenticated = false
      } catch (error) {
        console.error('Logout error:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async register(email: string, password: string) {
      this.loading = true
      try {
        // TODO: Implement Supabase registration
        this.isAuthenticated = true
        this.user = {
          id: 'temp-id',
          email
        }
      } catch (error) {
        console.error('Registration error:', error)
        throw error
      } finally {
        this.loading = false
      }
    }
  }
}) 