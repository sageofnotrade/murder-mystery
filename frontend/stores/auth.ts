import { defineStore } from 'pinia'
import { useNuxtApp, useCookie } from '#app'

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
  token: string | null
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
    loading: false,
    token: useCookie('auth_token').value || null
  }),

  getters: {
    getUser: (state) => state.user,
    getIsAuthenticated: (state) => state.isAuthenticated,
    isLoading: (state) => state.loading,
    getToken: (state) => state.token
  },

  actions: {
    setAuthState(user: User | null, token: string | null) {
      this.user = user
      this.token = token
      this.isAuthenticated = !!user && !!token
      const authCookie = useCookie('auth_token')
      if (token) {
        authCookie.value = token
      } else {
        authCookie.value = null
      }
    },

    async login(email: string, password: string) {
      this.loading = true
      try {
        const { $supabase } = useNuxtApp()
        const { data, error } = await $supabase.auth.signInWithPassword({
          email,
          password
        })

        if (error) throw error

        if (data?.user && data?.session?.access_token) {
          this.setAuthState(data.user, data.session.access_token)
          return true
        }
        return false
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
        const { $supabase } = useNuxtApp()
        const { error } = await $supabase.auth.signOut()
        if (error) throw error
        this.setAuthState(null, null)
        return true
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
        const { $supabase } = useNuxtApp()
        const { data, error } = await $supabase.auth.signUp({
          email,
          password,
          options: {
            emailRedirectTo: `${window.location.origin}/auth/callback`
          }
        })

        if (error) throw error

        if (data?.user && data?.session?.access_token) {
          this.setAuthState(data.user, data.session.access_token)
          return true
        }
        return false
      } catch (error) {
        console.error('Registration error:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async checkAuth() {
      try {
        const { $supabase } = useNuxtApp()
        const { data: { session }, error } = await $supabase.auth.getSession()
        if (error) throw error
        if (session?.user && session?.access_token) {
          this.setAuthState(session.user, session.access_token)
          return true
        }
        this.setAuthState(null, null)
        return false
      } catch (error) {
        console.error('Auth check error:', error)
        this.setAuthState(null, null)
        return false
      }
    }
  }
})
