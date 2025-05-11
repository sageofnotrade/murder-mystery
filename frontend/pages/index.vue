<template>
  <div class="max-w-4xl mx-auto">
    <section class="text-center mb-16">
      <h1 class="text-5xl font-bold mb-6 bg-gradient-to-r from-mystery-accent to-mystery-accent/70 bg-clip-text text-transparent">
        Welcome to Murþrą
      </h1>
      <p class="text-xl text-mystery-light mb-8">
        A personalized, AI-driven detective experience that adapts to your psychology and decisions.
      </p>
      <div class="flex justify-center space-x-4">
        <NuxtLink
          to="/auth/register"
          class="bg-mystery-accent text-mystery-dark px-8 py-3 rounded-lg text-lg font-semibold hover:bg-mystery-accent/90 transition-colors"
        >
          Start Your Mystery
        </NuxtLink>
        <NuxtLink
          to="/about"
          class="border border-mystery-accent text-mystery-accent px-8 py-3 rounded-lg text-lg font-semibold hover:bg-mystery-accent/10 transition-colors"
        >
          Learn More
        </NuxtLink>
      </div>
    </section>

    <section class="grid md:grid-cols-3 gap-8 mb-16">
      <div class="bg-mystery-darker p-6 rounded-lg">
        <h3 class="text-xl font-semibold mb-3 text-mystery-accent">AI-Driven Stories</h3>
        <p class="text-mystery-light">
          Each mystery is uniquely crafted based on your psychological profile and decisions.
        </p>
      </div>
      <div class="bg-mystery-darker p-6 rounded-lg">
        <h3 class="text-xl font-semibold mb-3 text-mystery-accent">Visual Investigation</h3>
        <p class="text-mystery-light">
          Use our interactive detective board to connect clues and solve the mystery.
        </p>
      </div>
      <div class="bg-mystery-darker p-6 rounded-lg">
        <h3 class="text-xl font-semibold mb-3 text-mystery-accent">Dynamic Characters</h3>
        <p class="text-mystery-light">
          Interact with suspects who react and adapt to your investigation style.
        </p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default'
})
</script>
