<template>
  <div class="min-h-screen bg-mystery-dark p-8">
    <div class="max-w-4xl mx-auto">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-mystery-accent">Welcome to Your Mystery</h1>
        <button 
          @click="handleLogout"
          class="bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 transition"
        >
          Log Out
        </button>
      </div>
      
      <div class="bg-mystery-medium p-6 rounded-lg shadow-lg mb-8">
        <h2 class="text-xl font-semibold mb-4 text-mystery-accent">Get Started</h2>
        <p class="text-mystery-light mb-6">
          Let's create your first mystery. We'll need to understand your preferences and psychological profile to create a unique experience.
        </p>
        
        <button 
          @click="startProfileSetup"
          class="bg-mystery-accent text-white py-2 px-6 rounded-md hover:bg-opacity-90 transition"
        >
          Begin Profile Setup
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { navigateTo } from '#app'

const router = useRouter()
const { $supabase } = useNuxtApp()

// Manually check auth (adjust this depending on your app logic)
onMounted(async () => {
  const {
    data: { session },
  } = await $supabase.auth.getSession()

  if (!session) {
    navigateTo('/auth/login')
  }
})

const startProfileSetup = () => {
  router.push('/profile')
}

const handleLogout = async () => {
  try {
    const { error } = await $supabase.auth.signOut()
    if (error) throw error
    await navigateTo('/auth/login')
  } catch (error) {
    console.error('Error logging out:', error.message)
  }
}
</script>
