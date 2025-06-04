import { ref } from 'vue'
import { defineStore } from 'pinia'
import {
  fetchInitialNarrative,
  submitNarrativeChoice,
  submitUserInput as apiSubmitUserInput
} from '@/services/narrativeService'

export const useNarrativeStore = defineStore('narrative', () => {
  const isInitialized = ref(false)
  const currentSegment = ref(null)
  const history = ref([])

  const initializeNarrative = async () => {
    const data = await fetchInitialNarrative()
    currentSegment.value = data
    history.value.push(data)
    isInitialized.value = true
  }

  const submitChoice = async (choiceId) => {
    const data = await submitNarrativeChoice(choiceId)
    currentSegment.value = data
    history.value.push(data)
  }

  const submitUserInput = async (input) => {
    const data = await apiSubmitUserInput(input)
    currentSegment.value = data
    history.value.push(data)
  }

  const resetNarrative = () => {
    isInitialized.value = false
    currentSegment.value = null
    history.value = []
  }

  return {
    isInitialized,
    currentSegment,
    history,
    initializeNarrative,
    submitChoice,
    submitUserInput,
    resetNarrative
  }
})
