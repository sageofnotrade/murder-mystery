<template>
  <div class="mb-4">
    <form @submit.prevent="onSubmit" class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 w-full">
    <input
      v-model="userInput"
      :placeholder="placeholder"
      aria-label="User Input Field"
      class="w-full flex-1 px-4 py-2 rounded bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-500 transition duration-150"
    />
    <button
      :disabled="isLoading"
      type="submit"
      class="px-5 py-2 bg-pink-500 text-white rounded hover:bg-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center gap-2"
    >
      <span>Submit</span>
      <Send class="w-4 h-4" />
    </button>
  </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Send } from 'lucide-vue-next'

const props = defineProps({
  placeholder: String,
  isLoading: Boolean
})

const emit = defineEmits(['submit-input'])
const userInput = ref('')

const onSubmit = () => {
  if (!userInput.value.trim()) return
  emit('submit-input', userInput.value)
  userInput.value = ''
}
</script>
