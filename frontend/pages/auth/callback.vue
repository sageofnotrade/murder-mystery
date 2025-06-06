<template>
  <div class="min-h-screen flex items-center justify-center bg-mystery-dark">
    <div class="bg-mystery-medium p-8 rounded-lg shadow-lg max-w-md w-full text-center">
      <div v-if="loading" class="text-mystery-accent">
        Verifying your email...
      </div>
      <div v-else-if="error" class="text-red-500">
        {{ error }}
      </div>
      <div v-else class="text-green-500">
        Email confirmed successfully! You can now 
        <NuxtLink to="/auth/login" class="text-mystery-accent hover:underline">
          sign in
        </NuxtLink>
        to your account.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
const { $supabase } = useNuxtApp()

const loading = ref(true)
const error = ref(null)
const supabase = $supabase

onMounted(async () => {
  try {
    const { error: authError } = await supabase.auth.getSession()
    if (authError) throw authError
    
    // The email confirmation is handled automatically by Supabase
    // We just need to wait for the session to be established
    await new Promise(resolve => setTimeout(resolve, 1000))
  } catch (err) {
    error.value = 'Failed to verify email. Please try again.'
    console.error(err)
  } finally {
    loading.value = false
  }
})
</script> 