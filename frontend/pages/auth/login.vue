<template>
  <div class="min-h-screen flex items-center justify-center bg-mystery-dark">
    <div class="bg-mystery-medium p-8 rounded-lg shadow-lg max-w-md w-full">
      <h1 class="text-3xl font-bold mb-6 text-center text-mystery-accent">Sign In</h1>
      
      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label for="email" class="block text-sm font-medium text-gray-300 mb-1">Email</label>
          <input 
            type="email" 
            id="email" 
            v-model="email" 
            class="w-full px-3 py-2 bg-mystery-dark border border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-mystery-accent"
            required
          />
        </div>
        
        <div class="mb-6">
          <label for="password" class="block text-sm font-medium text-gray-300 mb-1">Password</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            class="w-full px-3 py-2 bg-mystery-dark border border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-mystery-accent"
            required
          />
        </div>
        
        <button 
          type="submit" 
          class="w-full bg-mystery-accent text-white py-2 px-4 rounded-md hover:bg-opacity-90 transition"
          :disabled="loading"
        >
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
        
        <div v-if="error" class="mt-4 text-red-500 text-sm text-center">
          {{ error }}
        </div>
      </form>
      
      <div class="mt-6 text-center">
        <p class="text-gray-400">
          Don't have an account? 
          <NuxtLink to="/auth/register" class="text-mystery-accent hover:underline">
            Sign Up
          </NuxtLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useSupabaseClient } from '#imports'

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref(null)
const supabase = useSupabaseClient()

const handleLogin = async () => {
  try {
    loading.value = true
    error.value = null
    
    const { error: signInError } = await supabase.auth.signInWithPassword({
      email: email.value,
      password: password.value
    })
    
    if (signInError) {
      error.value = signInError.message
    }
  } catch (err) {
    error.value = 'An unexpected error occurred'
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>
