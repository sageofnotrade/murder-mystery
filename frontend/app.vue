<template>
  <div class="min-h-screen bg-mystery-dark text-white">
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>

<script setup lang="ts">
// Main app component
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body {
  @apply bg-mystery-dark text-white;
  font-family: 'Inter', sans-serif;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  @apply bg-mystery-dark;
}

::-webkit-scrollbar-thumb {
  @apply bg-mystery-accent rounded-full;
}

::-webkit-scrollbar-thumb:hover {
  @apply bg-mystery-accent/80;
}
</style>
