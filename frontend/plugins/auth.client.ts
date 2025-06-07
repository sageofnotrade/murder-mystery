import { useAuthStore } from '~/stores/auth'
import { useNuxtApp } from '#app'
import { onUnmounted } from 'vue'

export default defineNuxtPlugin(async () => {
  const authStore = useAuthStore()
  const { $supabase } = useNuxtApp()
  
  // Check auth state on app initialization
  await authStore.checkAuth()
  
  // Listen for auth state changes
  const { data: { subscription } } = $supabase.auth.onAuthStateChange((event, session) => {
    if (event === 'SIGNED_IN' && session) {
      authStore.setAuthState(session.user, session.access_token)
    } else if (event === 'SIGNED_OUT') {
      authStore.setAuthState(null, null)
    }
  })

  // Cleanup subscription on app unmount
  onUnmounted(() => {
    subscription.unsubscribe()
  })
}) 