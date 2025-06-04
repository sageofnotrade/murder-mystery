<template>
  <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
    <button
      v-for="choice in choices"
      :key="choice.id"
      @click="$emit('select-choice', choice.id)"
      class="w-full px-4 py-3 bg-gray-800 text-white rounded-lg shadow hover:bg-pink-600 focus:outline-none focus:ring-2 focus:ring-pink-500 transition"
    >
      {{ choice.text }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  choices: Array
})
</script>
