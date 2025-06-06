<template>
  <Transition name="fade-slide" mode="out-in">
    <div
      v-if="currentNarrativeSegment"
      key="segment"
      class="max-w-4xl mx-auto px-6 py-16 sm:py-20 space-y-10"
    >

      <!-- Story Log (AI Dungeon-style) -->
      <div v-for="(segment, index) in narrativeHistory" :key="index">
        <StoryText
          :text="segment.text"
          :character="segment.character"
          :animate="index === narrativeHistory.length - 1 ? animateText : false"
        />
      </div>
      <div ref="storyEndRef" />

      <!-- Action Choices -->
      <ActionChoices
        v-if="currentNarrativeSegment.choices.length > 0"
        :choices="currentNarrativeSegment.choices"
        @select-choice="handleChoiceSelection"
      />
          <div class="flex flex-wrap sm:flex-nowrap flex-col sm:flex-row gap-4 justify-center mt-6">
  <button class="px-4 py-2 rounded font-semibold bg-pink-600 text-white hover:bg-pink-500 focus:outline-none focus:ring-2 focus:ring-pink-400">
    Continue
  </button>
  <button class="px-4 py-2 rounded bg-gray-700 text-white hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-400">
    Take a Turn
  </button>
  <button class="px-4 py-2 rounded bg-yellow-600 text-white hover:bg-yellow-500 focus:outline-none focus:ring-2 focus:ring-yellow-300">
    Retry
  </button>
  <button class="px-4 py-2 rounded bg-red-600 text-white hover:bg-red-500 focus:outline-none focus:ring-2 focus:ring-red-400">
    Erase
  </button>
</div>
    </div>
  </Transition>

      <!-- Floating Input Bar -->
      <div class="fixed bottom-0 left-0 w-full bg-gray-900 border-t border-gray-700 p-4 z-50 shadow-inner">

        <div class="max-w-3xl mx-auto">
          <UserInput
            v-if="allowUserInput"
            :placeholder="inputPlaceholder"
            @submit-input="handleUserInput"
            :isLoading="isSubmitting"
          />
        </div>
      </div>

  <!-- Footer Navigation -->
  <div class="text-sm text-right mb-4 flex justify-end gap-6">
    <NuxtLink to="/dashboard" class="flex items-center text-pink-400 hover:underline gap-1">
      <ArrowLeftIcon class="w-4 h-4" />
      Back to Dashboard
    </NuxtLink>
    <button
      @click="restartMystery"
      class="flex items-center text-pink-400 hover:underline gap-1"
      aria-label="Restart the mystery"
    >
      <RefreshIcon class="w-4 h-4" />
      <span class="sr-only">Restart Mystery</span>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useNarrativeStore } from '@/stores/narrativeStore'
import StoryText from './StoryText.vue'
import ActionChoices from './ActionChoices.vue'
import UserInput from './UserInput.vue'
import NarrativeHistory from './NarrativeHistory.vue'
import { onUpdated, nextTick } from 'vue'


const narrativeStore = useNarrativeStore()
const isSubmitting = ref(false)
const animateText = ref(true)
const inputPlaceholder = ref('What would you like to do?')

const currentNarrativeSegment = computed(() => narrativeStore.currentSegment)
const narrativeHistory = computed(() => narrativeStore.history)
const allowUserInput = computed(() => currentNarrativeSegment.value?.allowInput ?? false)

const handleChoiceSelection = async (choiceId) => {
  isSubmitting.value = true
  await narrativeStore.submitChoice(choiceId)
  isSubmitting.value = false
}

const handleUserInput = async (input) => {
  isSubmitting.value = true
  await narrativeStore.submitUserInput(input)
  isSubmitting.value = false
}

const scrollToHistoryItem = (index) => {
  // Optional: add scroll animation
}

onMounted(async () => {
  if (!narrativeStore.isInitialized) {
    await narrativeStore.initializeNarrative()
  }
})

const restartMystery = () => {
  narrativeStore.resetNarrative()
  narrativeStore.initializeNarrative()
}

const storyEndRef = ref(null)

onUpdated(async () => {
  await nextTick()
  if (storyEndRef.value) {
    storyEndRef.value.scrollIntoView({ behavior: 'smooth' })
  }
})

</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.4s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.fade-slide-enter-to {
  opacity: 1;
  transform: translateY(0);
}

.fade-slide-leave-from {
  opacity: 1;
  transform: translateY(0);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>
