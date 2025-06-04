<template>
  <div class="clue-detail" role="main" aria-labelledby="clue-title">
    <div class="clue-header">
      <h2 id="clue-title" class="text-2xl font-bold mb-4">{{ clue?.description }}</h2>
      <div class="clue-meta flex gap-4 text-sm text-gray-600" role="group" aria-label="Clue metadata">
        <span class="clue-type" aria-label="Clue type">{{ clue?.type }}</span>
        <span class="clue-location" aria-label="Location">{{ clue?.location }}</span>
        <span class="discovery-date" aria-label="Discovery date">{{ formatDate(clue?.discovered_at) }}</span>
      </div>
    </div>

    <div class="clue-content mt-6">
      <!-- Discovery Information -->
      <section class="discovery-info bg-gray-50 p-4 rounded-lg mb-4" aria-labelledby="discovery-title">
        <h3 id="discovery-title" class="text-lg font-semibold mb-2">Discovery Information</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p class="text-sm text-gray-600" id="method-label">Method</p>
            <p aria-labelledby="method-label">{{ clue?.discovery_method }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-600" id="location-label">Location</p>
            <p aria-labelledby="location-label">{{ clue?.discovery_location }}</p>
          </div>
        </div>
      </section>

      <!-- Relevance and Status -->
      <section class="relevance-section flex flex-col sm:flex-row items-start sm:items-center gap-4 mb-4" aria-labelledby="relevance-title">
        <h3 id="relevance-title" class="sr-only">Relevance and Status</h3>
        <div class="relevance-score">
          <label for="relevance-slider" class="text-sm text-gray-600 block mb-1">Relevance</label>
          <div class="flex items-center gap-2">
            <input 
              id="relevance-slider"
              type="range" 
              v-model="relevanceScore" 
              min="0" 
              max="1" 
              step="0.1"
              @change="updateRelevance"
              class="w-32"
              :aria-valuetext="`${(relevanceScore * 100).toFixed(0)}% relevance`"
            />
            <span aria-live="polite">{{ (relevanceScore * 100).toFixed(0) }}%</span>
          </div>
        </div>
        <div class="red-herring">
          <label for="red-herring-checkbox" class="flex items-center gap-2 cursor-pointer">
            <input 
              id="red-herring-checkbox"
              type="checkbox" 
              v-model="isRedHerring"
              @change="updateRedHerring"
              class="form-checkbox"
              aria-describedby="red-herring-desc"
            />
            <span class="text-sm text-gray-600">Red Herring</span>
          </label>
          <span id="red-herring-desc" class="sr-only">Mark this clue as a false lead</span>
        </div>
      </section>

      <!-- Notes Section -->
      <section class="notes-section mb-4" aria-labelledby="notes-title">
        <h3 id="notes-title" class="text-lg font-semibold mb-2">Notes</h3>
        <label for="notes-textarea" class="sr-only">Add your notes about this clue</label>
        <textarea
          id="notes-textarea"
          v-model="notes"
          @blur="updateNotes"
          class="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          rows="4"
          placeholder="Add your notes about this clue..."
          aria-describedby="notes-help"
        ></textarea>
        <span id="notes-help" class="text-xs text-gray-500">Notes are automatically saved when you click outside the text area</span>
      </section>

      <!-- Related Suspects Section -->
      <ClueRelatedSuspects 
        v-if="clue"
        :clue="clue"
        @suspect-selected="handleSuspectSelected"
      />

      <!-- Connections Section -->
      <section class="connections-section mb-4" aria-labelledby="connections-title">
        <h3 id="connections-title" class="text-lg font-semibold mb-2">Connections</h3>
        <div v-if="clue?.connections && clue.connections.length > 0" class="connections-list">
          <div 
            v-for="connection in clue.connections" 
            :key="connection.id" 
            class="connection-item p-3 bg-gray-50 rounded-lg mb-2 hover:bg-gray-100 transition-colors"
            role="listitem"
          >
            <div class="flex justify-between items-start">
              <div>
                <p class="font-medium">{{ connection.connection_type }}</p>
                <p class="text-sm text-gray-600">{{ connection.details?.reason }}</p>
              </div>
              <button 
                @click="viewConnectedClue(connection.connected_clue_id)"
                class="text-blue-600 hover:text-blue-800 focus:ring-2 focus:ring-blue-500 rounded px-2 py-1"
                :aria-label="`View clue ${connection.connected_clue_id}`"
              >
                View Clue
              </button>
            </div>
          </div>
        </div>
        <div v-else class="text-gray-500 italic" role="status">
          No connections found
        </div>
        <button 
          @click="showAddConnection = true"
          class="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          aria-describedby="add-connection-desc"
        >
          Add Connection
        </button>
        <span id="add-connection-desc" class="sr-only">Add a connection to another clue</span>
      </section>

      <!-- Analysis Section -->
      <section class="analysis-section" aria-labelledby="analysis-title">
        <h3 id="analysis-title" class="text-lg font-semibold mb-2">Analysis</h3>
        <div v-if="analysis" class="analysis-content bg-gray-50 p-4 rounded-lg">
          <div v-for="(value, key) in analysis" :key="key" class="mb-3">
            <p class="text-sm text-gray-600 capitalize">{{ key.replace('_', ' ') }}</p>
            <p>{{ value }}</p>
          </div>
        </div>
        <div v-else class="text-gray-500 italic" role="status">
          No analysis available
        </div>
        <button 
          @click="requestAnalysis"
          :disabled="analysisLoading"
          class="mt-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          :aria-label="analysisLoading ? 'Analyzing clue...' : 'Analyze clue'"
        >
          <span v-if="analysisLoading">Analyzing...</span>
          <span v-else>Analyze Clue</span>
        </button>
      </section>
    </div>

    <!-- Add Connection Modal -->
    <div 
      v-if="showAddConnection" 
      class="modal fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      role="dialog"
      aria-labelledby="modal-title"
      aria-modal="true"
      @click.self="showAddConnection = false"
    >
      <div class="modal-content bg-white p-6 rounded-lg w-full max-w-md mx-4">
        <h3 id="modal-title" class="text-lg font-semibold mb-4">Add Connection</h3>
        <form @submit.prevent="addConnection">
          <div class="mb-4">
            <label for="connection-type" class="block text-sm text-gray-600 mb-2">Connection Type</label>
            <input 
              id="connection-type"
              v-model="newConnection.type"
              type="text"
              class="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
              placeholder="e.g., Related evidence, Contradicts"
            />
          </div>
          <div class="mb-4">
            <label for="connection-reason" class="block text-sm text-gray-600 mb-2">Reason</label>
            <textarea
              id="connection-reason"
              v-model="newConnection.reason"
              class="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows="3"
              required
              placeholder="Explain how these clues are connected..."
            ></textarea>
          </div>
          <div class="flex justify-end gap-2">
            <button 
              type="button"
              @click="showAddConnection = false"
              class="px-4 py-2 text-gray-600 hover:text-gray-800 focus:ring-2 focus:ring-gray-500 rounded"
            >
              Cancel
            </button>
            <button 
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Add Connection
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useClueStore } from '@/stores/clue'
import ClueRelatedSuspects from './ClueRelatedSuspects.vue'

const props = defineProps({
  clueId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['view-clue', 'suspect-selected'])

const clueStore = useClueStore()
const clue = ref(null)
const relevanceScore = ref(0.5)
const isRedHerring = ref(false)
const notes = ref('')
const analysis = ref(null)
const analysisLoading = ref(false)
const showAddConnection = ref(false)
const newConnection = ref({
  type: '',
  reason: ''
})

onMounted(async () => {
  await loadClue()
})

const loadClue = async () => {
  try {
    const clueData = await clueStore.getClueDetails(props.clueId)
    clue.value = clueData
    relevanceScore.value = clueData.relevance_score || 0.5
    isRedHerring.value = clueData.is_red_herring || false
    notes.value = clueData.notes || ''
  } catch (error) {
    console.error('Error loading clue:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

const updateRelevance = async () => {
  try {
    await clueStore.updateClueRelevance(props.clueId, relevanceScore.value)
  } catch (error) {
    console.error('Error updating relevance:', error)
  }
}

const updateRedHerring = async () => {
  try {
    await clueStore.markClueAsRedHerring(props.clueId, isRedHerring.value)
  } catch (error) {
    console.error('Error updating red herring status:', error)
  }
}

const updateNotes = async () => {
  try {
    await clueStore.updateClueNotes(props.clueId, notes.value)
  } catch (error) {
    console.error('Error updating notes:', error)
  }
}

const addConnection = async () => {
  try {
    await clueStore.addClueConnection(props.clueId, {
      connection_type: newConnection.value.type,
      details: {
        reason: newConnection.value.reason
      }
    })
    showAddConnection.value = false
    newConnection.value = { type: '', reason: '' }
    await loadClue()
  } catch (error) {
    console.error('Error adding connection:', error)
  }
}

const viewConnectedClue = (connectedClueId) => {
  emit('view-clue', connectedClueId)
}

const requestAnalysis = async () => {
  try {
    analysisLoading.value = true
    analysis.value = await clueStore.analyzeClue(props.clueId)
  } catch (error) {
    console.error('Error analyzing clue:', error)
  } finally {
    analysisLoading.value = false
  }
}

const handleSuspectSelected = (suspect) => {
  emit('suspect-selected', suspect)
}
</script>

<style scoped>
.clue-detail {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.modal {
  backdrop-filter: blur(2px);
}

.connection-item {
  transition: background-color 0.2s ease-in-out;
}

@media (max-width: 640px) {
  .clue-detail {
    padding: 1rem;
  }
  
  .relevance-section {
    flex-direction: column;
    align-items: flex-start;
  }
}

/* Focus styles for better accessibility */
.form-checkbox:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Screen reader only content */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style> 