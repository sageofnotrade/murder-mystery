<template>
  <Transition name="fade-slide" mode="out-in">
    <div
      v-if="currentNarrativeSegment"
      key="segment"
      class="max-w-4xl mx-auto px-6 py-12 space-y-8"
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

      <button class="bg-gray-800 text-white px-4 py-2 rounded hover:bg-gray-700">Take a Turn</button>
      <button class="bg-gray-800 text-white px-4 py-2 rounded hover:bg-gray-700">Continue</button>
      <button class="bg-gray-800 text-white px-4 py-2 rounded hover:bg-gray-700">Retry</button>
      <button class="bg-gray-800 text-white px-4 py-2 rounded hover:bg-gray-700">Erase</button>
    </div>
    </div>
  </Transition>

      <!-- Floating Input Bar -->
      <div class="fixed bottom-0 left-0 w-full bg-gray-950 border-t border-gray-700 p-4 z-50">
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
    >
      <RefreshIcon class="w-4 h-4" />
      Restart Mystery
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
