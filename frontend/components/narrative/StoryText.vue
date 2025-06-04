<template>
  <div class="text-white text-lg leading-relaxed px-2 py-1 transition-opacity duration-300">
    <p v-if="character?.name" class="text-pink-400 font-bold mb-2">
      {{ character.name }}:
    </p>
    <p 
      class="whitespace-pre-line"
      :class="isPlayerInput ? 'text-pink-400 italic' : 'text-white'"
    >
      <span v-if="!animate">{{ text }}</span>
      <span v-else>{{ displayedText }}</span>
    </p>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  text: String,
  character: Object,
  animate: Boolean
})

const displayedText = ref('')
const isPlayerInput = computed(() => props.text?.toLowerCase().startsWith('you said'))

watch(
  () => props.text,
  async (newText) => {
    displayedText.value = ''
    if (!props.animate) {
      displayedText.value = newText
      return
    }

    for (let i = 0; i <= newText.length; i++) {
      displayedText.value = newText.slice(0, i)
      await new Promise((r) => setTimeout(r, 20))
    }
  },
  { immediate: true }
)
</script>

<style scoped>
p span {
  transition: all 0.3s ease-in-out;
}

div:hover {
  background-color: rgba(255, 255, 255, 0.05);
  border-left: 3px solid #f472b6; /* pink-400 */
  padding-left: 0.75rem;
}
</style>
