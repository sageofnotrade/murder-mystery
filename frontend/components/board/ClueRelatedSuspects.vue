<template>
  <section class="related-suspects-section mb-4" aria-labelledby="suspects-title">
    <h3 id="suspects-title" class="text-lg font-semibold mb-2">Related Suspects</h3>
    
    <div v-if="loading" class="flex justify-center py-4" role="status" aria-label="Loading suspects">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-red-600" role="alert">{{ error }}</p>
    </div>

    <div v-else-if="relatedSuspects.length > 0" class="suspects-list">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div 
          v-for="suspect in relatedSuspects" 
          :key="suspect.id"
          class="suspect-card bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
          role="button"
          tabindex="0"
          :aria-label="`View details for suspect ${suspect.name}`"
          @click="selectSuspect(suspect)"
          @keydown.enter="selectSuspect(suspect)"
          @keydown.space.prevent="selectSuspect(suspect)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <h4 class="font-medium text-gray-900">{{ suspect.name }}</h4>
              <p class="text-sm text-gray-600 mt-1">{{ suspect.role || 'Unknown role' }}</p>
              
              <!-- Connection details -->
              <div v-if="suspect.connection" class="mt-2">
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {{ suspect.connection.type }}
                </span>
                <p class="text-xs text-gray-500 mt-1">{{ suspect.connection.reason }}</p>
              </div>

              <!-- Relevance indicator -->
              <div class="mt-2 flex items-center">
                <span class="text-xs text-gray-500 mr-2">Relevance:</span>
                <div class="flex-1 bg-gray-200 rounded-full h-2 max-w-20">
                  <div 
                    class="bg-gradient-to-r from-green-400 to-red-400 h-2 rounded-full transition-all"
                    :style="{ width: `${(suspect.relevance || 0.5) * 100}%` }"
                    :aria-label="`${Math.round((suspect.relevance || 0.5) * 100)}% relevance`"
                  ></div>
                </div>
                <span class="text-xs text-gray-600 ml-2">{{ Math.round((suspect.relevance || 0.5) * 100) }}%</span>
              </div>
            </div>

            <!-- Status indicators -->
            <div class="flex flex-col items-end space-y-1">
              <span 
                v-if="suspect.status === 'prime_suspect'"
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800"
                aria-label="Prime suspect"
              >
                Prime
              </span>
              <span 
                v-else-if="suspect.status === 'person_of_interest'"
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800"
                aria-label="Person of interest"
              >
                POI
              </span>
              <span 
                v-else-if="suspect.status === 'cleared'"
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800"
                aria-label="Cleared"
              >
                Cleared
              </span>
            </div>
          </div>

          <!-- Last seen/alibi info -->
          <div v-if="suspect.last_seen || suspect.alibi" class="mt-3 pt-3 border-t border-gray-100">
            <div v-if="suspect.last_seen" class="text-xs text-gray-600">
              <span class="font-medium">Last seen:</span> {{ suspect.last_seen }}
            </div>
            <div v-if="suspect.alibi" class="text-xs text-gray-600 mt-1">
              <span class="font-medium">Alibi:</span> {{ suspect.alibi }}
            </div>
          </div>
        </div>
      </div>

      <!-- Add new suspect connection -->
      <div class="mt-4">
        <button 
          @click="showAddSuspect = true"
          class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          aria-describedby="add-suspect-desc"
        >
          Add Suspect Connection
        </button>
        <span id="add-suspect-desc" class="sr-only">Add a connection between this clue and a suspect</span>
      </div>
    </div>

    <div v-else class="text-gray-500 italic text-center py-8" role="status">
      <p>No related suspects found for this clue.</p>
      <button 
        @click="showAddSuspect = true"
        class="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      >
        Add Suspect Connection
      </button>
    </div>

    <!-- Add Suspect Modal -->
    <div 
      v-if="showAddSuspect" 
      class="modal fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      role="dialog"
      aria-labelledby="add-suspect-modal-title"
      aria-modal="true"
      @click.self="showAddSuspect = false"
    >
      <div class="modal-content bg-white p-6 rounded-lg w-full max-w-md mx-4">
        <h3 id="add-suspect-modal-title" class="text-lg font-semibold mb-4">Add Suspect Connection</h3>
        <form @submit.prevent="addSuspectConnection">
          <div class="mb-4">
            <label for="suspect-select" class="block text-sm text-gray-600 mb-2">Select Suspect</label>
            <select 
              id="suspect-select"
              v-model="newSuspectConnection.suspectId"
              class="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
              <option value="">Choose a suspect...</option>
              <option v-for="suspect in availableSuspects" :key="suspect.id" :value="suspect.id">
                {{ suspect.name }} - {{ suspect.role }}
              </option>
            </select>
          </div>
          
          <div class="mb-4">
            <label for="connection-type-select" class="block text-sm text-gray-600 mb-2">Connection Type</label>
            <select 
              id="connection-type-select"
              v-model="newSuspectConnection.connectionType"
              class="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
              <option value="">Choose connection type...</option>
              <option value="direct_evidence">Direct Evidence</option>
              <option value="circumstantial">Circumstantial</option>
              <option value="witness_testimony">Witness Testimony</option>
              <option value="alibi_related">Alibi Related</option>
              <option value="motive_related">Motive Related</option>
            </select>
          </div>

          <div class="mb-4">
            <label for="connection-reason-textarea" class="block text-sm text-gray-600 mb-2">Reason</label>
            <textarea
              id="connection-reason-textarea"
              v-model="newSuspectConnection.reason"
              class="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows="3"
              required
              placeholder="Explain how this clue relates to the suspect..."
            ></textarea>
          </div>

          <div class="flex justify-end gap-2">
            <button 
              type="button"
              @click="showAddSuspect = false"
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
  </section>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'

const props = defineProps({
  clue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['suspect-selected'])

const loading = ref(false)
const error = ref(null)
const relatedSuspects = ref([])
const availableSuspects = ref([])
const showAddSuspect = ref(false)
const newSuspectConnection = ref({
  suspectId: '',
  connectionType: '',
  reason: ''
})

onMounted(async () => {
  await loadRelatedSuspects()
  await loadAvailableSuspects()
})

const loadRelatedSuspects = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Mock data for related suspects - replace with actual API call
    const suspects = [
      {
        id: '1',
        name: 'John Smith',
        role: 'Butler',
        status: 'prime_suspect',
        relevance: 0.8,
        connection: {
          type: 'Direct Evidence',
          reason: 'Fingerprints found on the clue'
        },
        last_seen: 'Library at 9 PM',
        alibi: 'Claims to have been in the kitchen'
      },
      {
        id: '2',
        name: 'Mary Johnson',
        role: 'Housekeeper',
        status: 'person_of_interest',
        relevance: 0.6,
        connection: {
          type: 'Circumstantial',
          reason: 'Had access to the location where clue was found'
        },
        last_seen: 'Garden at 8:30 PM',
        alibi: 'Cleaning the dining room'
      }
    ]
    
    // Filter suspects based on clue's related_suspects if available
    if (props.clue.related_suspects && props.clue.related_suspects.length > 0) {
      relatedSuspects.value = suspects.filter(suspect => 
        props.clue.related_suspects.includes(suspect.id)
      )
    } else {
      relatedSuspects.value = suspects
    }
  } catch (err) {
    error.value = 'Failed to load related suspects'
    console.error('Error loading related suspects:', err)
  } finally {
    loading.value = false
  }
}

const loadAvailableSuspects = async () => {
  try {
    // Mock data for all available suspects - replace with actual API call
    availableSuspects.value = [
      { id: '1', name: 'John Smith', role: 'Butler' },
      { id: '2', name: 'Mary Johnson', role: 'Housekeeper' },
      { id: '3', name: 'Dr. Wilson', role: 'Family Doctor' },
      { id: '4', name: 'Sarah Davis', role: 'Secretary' },
      { id: '5', name: 'Tom Brown', role: 'Gardener' }
    ]
  } catch (err) {
    console.error('Error loading available suspects:', err)
  }
}

const selectSuspect = (suspect) => {
  emit('suspect-selected', suspect)
}

const addSuspectConnection = async () => {
  try {
    // TODO: Implement API call to create suspect-clue connection
    console.log('Adding suspect connection:', newSuspectConnection.value)
    
    // For now, just add to the local list
    const selectedSuspect = availableSuspects.value.find(
      s => s.id === newSuspectConnection.value.suspectId
    )
    
    if (selectedSuspect) {
      const newConnection = {
        ...selectedSuspect,
        connection: {
          type: newSuspectConnection.value.connectionType,
          reason: newSuspectConnection.value.reason
        },
        relevance: 0.5, // Default relevance
        status: 'person_of_interest'
      }
      
      relatedSuspects.value.push(newConnection)
    }
    
    showAddSuspect.value = false
    newSuspectConnection.value = {
      suspectId: '',
      connectionType: '',
      reason: ''
    }
  } catch (err) {
    error.value = 'Failed to add suspect connection'
    console.error('Error adding suspect connection:', err)
  }
}

// Screen reader only class for accessibility
const srOnlyClass = 'absolute w-px h-px p-0 -m-px overflow-hidden whitespace-nowrap border-0'
</script>

<style scoped>
.suspect-card {
  transition: all 0.2s ease-in-out;
}

.suspect-card:hover {
  transform: translateY(-1px);
}

.suspect-card:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

.modal {
  backdrop-filter: blur(2px);
}

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

@media (max-width: 640px) {
  .suspects-list .grid {
    grid-template-columns: 1fr;
  }
}
</style> 