<script setup>
definePageMeta({
  middleware: [] // disable any auth middleware
})

import NarrativeInterface from '@/components/narrative/NarrativeInterface.vue'
</script>

<template>
  <NarrativeInterface />
</template>
