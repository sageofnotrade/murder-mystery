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

// Check if we're running in development mode
const isDevMode = process.env.NODE_ENV === 'development'

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: isDevMode
      ? {
          id: 'dev-user-001',
          email: 'dev@local.test',
          psychological_traits: { curiosity: 5 },
          preferences: { theme: 'dark' }
        }
      : null,
    isAuthenticated: isDevMode,
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
        if (isDevMode) {
          this.user = { id: 'dev-user-001', email }
          this.isAuthenticated = true
        } else {
          // TODO: Implement Supabase login
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
        if (isDevMode) {
          this.user = null
          this.isAuthenticated = false
        } else {
          // TODO: Implement Supabase logout
        }
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
        if (isDevMode) {
          this.user = { id: 'dev-user-001', email }
          this.isAuthenticated = true
        } else {
          // TODO: Implement Supabase registration
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
