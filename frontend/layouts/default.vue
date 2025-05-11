<template>
  <div class="min-h-screen flex flex-col">
    <header class="bg-mystery-darker border-b border-mystery-accent/20">
      <nav class="container mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <NuxtLink to="/" class="text-2xl font-bold text-mystery-accent">
            Murþrą
          </NuxtLink>
          <div class="flex items-center space-x-4">
            <NuxtLink to="/auth/login" class="text-mystery-light hover:text-mystery-accent transition-colors">
              Login
            </NuxtLink>
            <NuxtLink to="/auth/register" class="bg-mystery-accent text-mystery-dark px-4 py-2 rounded-lg hover:bg-mystery-accent/90 transition-colors">
              Register
            </NuxtLink>
          </div>
        </div>
      </nav>
    </header>

    <main class="flex-grow container mx-auto px-4 py-8">
      <slot />
    </main>

    <footer class="bg-mystery-darker border-t border-mystery-accent/20">
      <div class="container mx-auto px-4 py-6">
        <p class="text-center text-mystery-light">
          © 2024 Murþrą - AI-Driven Murder Mystery
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
// Default layout component
</script> 