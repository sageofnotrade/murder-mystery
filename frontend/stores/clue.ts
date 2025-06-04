import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'
import type { Clue, ClueConnection, ClueAnalysis, ApiResponse } from '@/types/api'

export const useClueStore = defineStore('clue', () => {
  const api = useApi()
  const loading = ref(false)
  const error = ref<string | null>(null)

  const getClueDetails = async (clueId: string): Promise<Clue> => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get<Clue>(`/clues/${clueId}`)
      return response.data.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An error occurred'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateClueRelevance = async (clueId: string, relevanceScore: number): Promise<Clue> => {
    loading.value = true
    error.value = null
    try {
      const response = await api.put<Clue>(`/clues/${clueId}/relevance`, {
        relevance_score: relevanceScore
      })
      return response.data.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An error occurred'
      throw err
    } finally {
      loading.value = false
    }
  }

  const markClueAsRedHerring = async (clueId: string, isRedHerring: boolean): Promise<Clue> => {
    loading.value = true
    error.value = null
    try {
      const response = await api.put<Clue>(`/clues/${clueId}/red-herring`, {
        is_red_herring: isRedHerring
      })
      return response.data.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An error occurred'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateClueNotes = async (clueId: string, notes: string): Promise<Clue> => {
    loading.value = true
    error.value = null
    try {
      const response = await api.put<Clue>(`/clues/${clueId}/notes`, {
        notes
      })
      return response.data.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An error occurred'
      throw err
    } finally {
      loading.value = false
    }
  }

  const addClueConnection = async (clueId: string, connection: {
    connection_type: string
    details: {
      reason: string
    }
  }): Promise<ClueConnection> => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post<ClueConnection>(`/clues/${clueId}/connections`, connection)
      return response.data.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An error occurred'
      throw err
    } finally {
      loading.value = false
    }
  }

  const analyzeClue = async (clueId: string): Promise<ClueAnalysis> => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post<ClueAnalysis>(`/clues/${clueId}/analyze`)
      return response.data.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An error occurred'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    getClueDetails,
    updateClueRelevance,
    markClueAsRedHerring,
    updateClueNotes,
    addClueConnection,
    analyzeClue
  }
}) 