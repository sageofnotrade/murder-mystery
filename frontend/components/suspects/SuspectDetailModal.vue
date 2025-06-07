<template>
    <Modal
      v-model="isOpen"
      :title="suspect?.name || 'Suspect Details'"
      size="xl"
      :loading="isLoading"
      :icon="UserIcon"
      icon-color="danger"
      @close="handleClose"
    >
      <!-- Loading State -->
      <div v-if="isLoading" class="space-y-4">
        <div class="flex items-start space-x-4">
          <div class="h-32 w-32 animate-pulse rounded-full bg-mystery-medium" />
          <div class="flex-1 space-y-2">
            <div class="h-6 w-1/3 animate-pulse rounded bg-mystery-medium" />
            <div class="h-4 w-1/2 animate-pulse rounded bg-mystery-medium" />
            <div class="h-4 w-2/3 animate-pulse rounded bg-mystery-medium" />
          </div>
        </div>
      </div>
  
      <!-- Error State -->
      <div v-else-if="error" class="rounded-lg bg-red-900/20 p-4 text-center">
        <ExclamationIcon class="mx-auto h-12 w-12 text-red-500" />
        <p class="mt-2 text-sm text-red-400">{{ error }}</p>
        <button @click="retry" class="btn-secondary mt-4">
          <RefreshIcon class="mr-2 h-4 w-4" />
          Retry
        </button>
      </div>
  
      <!-- Content -->
      <div v-else-if="suspect" class="space-y-6">
        <!-- Header Section with Image and Basic Info -->
        <div class="flex flex-col items-start space-y-4 sm:flex-row sm:space-x-6 sm:space-y-0">
          <!-- Suspect Image -->
          <div class="relative">
            <div
              class="h-32 w-32 overflow-hidden rounded-full bg-mystery-medium ring-4"
              :class="getSuspectRingColor(suspect.status)"
            >
              <img
                v-if="suspect.imageUrl && !imageError"
                :src="suspect.imageUrl"
                :alt="suspect.name"
                class="h-full w-full object-cover"
                @error="imageError = true"
              />
              <div v-else class="flex h-full w-full items-center justify-center">
                <UserIcon class="h-16 w-16 text-gray-600" />
              </div>
            </div>
            <div
              class="absolute -bottom-2 -right-2 flex h-8 w-8 items-center justify-center rounded-full"
              :class="getSuspectStatusBadgeClass(suspect.status)"
            >
              <component :is="getSuspectStatusIcon(suspect.status)" class="h-4 w-4 text-white" />
            </div>
          </div>
  
          <!-- Basic Info -->
          <div class="flex-1">
            <div class="mb-2">
              <h2 class="text-2xl font-bold text-white">{{ suspect.name }}</h2>
              <p class="text-sm text-gray-400">{{ suspect.occupation }}</p>
            </div>
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-gray-400">Age:</span>
                <span class="ml-2 text-white">{{ suspect.age || 'Unknown' }}</span>
              </div>
              <div>
                <span class="text-gray-400">Gender:</span>
                <span class="ml-2 text-white">{{ suspect.gender || 'Unknown' }}</span>
              </div>
              <div>
                <span class="text-gray-400">Last Seen:</span>
                <span class="ml-2 text-white">{{ suspect.lastKnownLocation || 'Unknown' }}</span>
              </div>
              <div>
                <span class="text-gray-400">Added:</span>
                <span class="ml-2 text-white">{{ formatDate(suspect.createdAt) }}</span>
              </div>
            </div>
          </div>
  
          <!-- Quick Actions -->
          <div class="flex flex-col space-y-2">
            <button
              @click="callSuspect"
              class="btn-secondary flex items-center justify-center"
              :disabled="!suspect.phoneNumber"
            >
              <PhoneIcon class="mr-2 h-4 w-4" />
              Call
            </button>
            <button
              @click="messageSuspect"
              class="btn-secondary flex items-center justify-center"
            >
              <ChatIcon class="mr-2 h-4 w-4" />
              Message
            </button>
            <button
              @click="trackSuspect"
              class="btn-secondary flex items-center justify-center"
            >
              <LocationMarkerIcon class="mr-2 h-4 w-4" />
              Track
            </button>
          </div>
        </div>
  
        <!-- Status Bar -->
        <div class="rounded-lg bg-mystery-medium p-4">
          <div class="flex items-center justify-between">
            <div>
              <h4 class="text-sm font-medium text-gray-400">Investigation Status</h4>
              <p class="mt-1">
                <span
                  class="inline-flex items-center rounded-full px-3 py-1 text-sm font-medium"
                  :class="getSuspectStatusClass(suspect.status)"
                >
                  {{ formatStatus(suspect.status) }}
                </span>
              </p>
            </div>
            <div class="text-right">
              <h4 class="text-sm font-medium text-gray-400">Threat Level</h4>
              <div class="mt-1 flex items-center space-x-1">
                <div
                  v-for="i in 5"
                  :key="i"
                  class="h-4 w-4 rounded"
                  :class="i <= suspect.threatLevel ? 'bg-red-500' : 'bg-gray-700'"
                />
              </div>
            </div>
          </div>
        </div>
  
        <!-- Tabbed Content -->
        <div>
          <nav class="flex space-x-1 rounded-lg bg-mystery-medium p-1" aria-label="Tabs">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                activeTab === tab.id
                  ? 'bg-mystery-accent text-white'
                  : 'text-gray-400 hover:text-white',
                'flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors'
              ]"
            >
              <component :is="tab.icon" class="mr-2 h-4 w-4" />
              {{ tab.name }}
              <span
                v-if="tab.count"
                class="ml-2 rounded-full bg-mystery-dark px-2 py-0.5 text-xs"
              >
                {{ tab.count }}
              </span>
            </button>
          </nav>
  
          <div class="mt-4">
            <!-- Biography Tab -->
            <div v-show="activeTab === 'biography'" class="prose prose-invert max-w-none">
              <div v-html="sanitizedBiography" />
            </div>
  
            <!-- Alibi Tab -->
            <div v-show="activeTab === 'alibi'" class="space-y-4">
              <div class="rounded-lg bg-mystery-medium p-4">
                <h3 class="mb-2 text-lg font-semibold text-white">Current Alibi</h3>
                <div class="prose prose-invert max-w-none">
                  <div v-html="sanitizedAlibi" />
                </div>
                <div v-if="suspect.alibiVerification" class="mt-4 flex items-center space-x-2">
                  <component
                    :is="getVerificationIcon(suspect.alibiVerification.status)"
                    class="h-5 w-5"
                    :class="getVerificationColor(suspect.alibiVerification.status)"
                  />
                  <span class="text-sm" :class="getVerificationColor(suspect.alibiVerification.status)">
                    {{ suspect.alibiVerification.status }}
                  </span>
                  <span class="text-sm text-gray-500">
                    by {{ suspect.alibiVerification.verifiedBy }}
                  </span>
                </div>
              </div>
  
              <!-- Alibi Timeline -->
              <div v-if="alibiTimeline.length > 0" class="space-y-2">
                <h4 class="text-sm font-medium text-gray-400">Alibi History</h4>
                <div class="space-y-2">
                  <div
                    v-for="alibi in alibiTimeline"
                    :key="alibi.id"
                    class="rounded-lg bg-mystery-medium/50 p-3"
                  >
                    <p class="text-sm text-gray-300">{{ alibi.description }}</p>
                    <p class="mt-1 text-xs text-gray-500">{{ formatDate(alibi.date) }}</p>
                  </div>
                </div>
              </div>
            </div>
  
            <!-- Motive Tab -->
            <div v-show="activeTab === 'motive'" class="space-y-4">
              <div class="rounded-lg bg-mystery-medium p-4">
                <h3 class="mb-2 text-lg font-semibold text-white">Potential Motive</h3>
                <div class="prose prose-invert max-w-none">
                  <div v-html="sanitizedMotive" />
                </div>
                
                <!-- Motive Strength Indicator -->
                <div class="mt-4">
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-gray-400">Motive Strength</span>
                    <span class="text-white">{{ suspect.motiveStrength }}%</span>
                  </div>
                  <div class="mt-2 h-2 w-full rounded-full bg-gray-700">
                    <div
                      class="h-full rounded-full transition-all"
                      :class="getMotiveStrengthColor(suspect.motiveStrength)"
                      :style="{ width: `${suspect.motiveStrength}%` }"
                    />
                  </div>
                </div>
              </div>
  
              <!-- Related Motives -->
              <div v-if="relatedMotives.length > 0">
                <h4 class="mb-2 text-sm font-medium text-gray-400">Other Possible Motives</h4>
                <div class="space-y-2">
                  <div
                    v-for="motive in relatedMotives"
                    :key="motive.id"
                    class="flex items-center justify-between rounded-lg bg-mystery-medium/50 p-3"
                  >
                    <span class="text-sm text-gray-300">{{ motive.type }}</span>
                    <span class="text-xs text-gray-500">{{ motive.likelihood }}% likely</span>
                  </div>
                </div>
              </div>
            </div>
  
            <!-- Evidence Tab -->
            <div v-show="activeTab === 'evidence'" class="space-y-4">
              <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div
                  v-for="evidence in relatedEvidence"
                  :key="evidence.id"
                  class="group relative overflow-hidden rounded-lg bg-mystery-medium p-4 transition-all hover:shadow-lg"
                >
                  <div class="flex items-start justify-between">
                    <div class="flex items-start space-x-3">
                      <div
                        class="flex h-10 w-10 items-center justify-center rounded-full"
                        :class="getEvidenceTypeClass(evidence.type)"
                      >
                        <component :is="getEvidenceTypeIcon(evidence.type)" class="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <h5 class="font-medium text-white">{{ evidence.title }}</h5>
                        <p class="mt-1 text-sm text-gray-400">{{ evidence.description }}</p>
                        <p class="mt-2 text-xs text-gray-500">Found {{ formatRelativeTime(evidence.foundAt) }}</p>
                      </div>
                    </div>
                    <button
                      @click="viewEvidence(evidence)"
                      class="opacity-0 transition-opacity group-hover:opacity-100"
                    >
                      <ExternalLinkIcon class="h-4 w-4 text-gray-400 hover:text-white" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
  
            <!-- Timeline Tab -->
            <div v-show="activeTab === 'timeline'">
              <div v-if="timeline.length > 0" class="relative">
                <div class="absolute left-6 top-0 h-full w-0.5 bg-mystery-accent/30" />
                <div class="space-y-6">
                  <div
                    v-for="(event, index) in timeline"
                    :key="event.id"
                    class="relative flex items-start space-x-4"
                  >
                    <div
                      class="z-10 flex h-12 w-12 items-center justify-center rounded-full border-4 border-mystery-dark"
                      :class="getTimelineEventClass(event.type)"
                    >
                      <component :is="getTimelineEventIcon(event.type)" class="h-5 w-5 text-white" />
                    </div>
                    <div class="flex-1 rounded-lg bg-mystery-medium p-4">
                      <div class="flex items-start justify-between">
                        <div>
                          <h5 class="font-medium text-white">{{ event.title }}</h5>
                          <p class="mt-1 text-sm text-gray-400">{{ event.description }}</p>
                        </div>
                        <span class="text-xs text-gray-500">{{ formatDate(event.timestamp) }}</span>
                      </div>
                      <div v-if="event.location" class="mt-2 flex items-center text-xs text-gray-500">
                        <LocationMarkerIcon class="mr-1 h-3 w-3" />
                        {{ event.location }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
  
            <!-- Connections Tab -->
            <div v-show="activeTab === 'connections'" class="space-y-4">
              <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div
                  v-for="connection in connections"
                  :key="connection.id"
                  class="flex items-center space-x-3 rounded-lg bg-mystery-medium p-4"
                >
                  <div class="h-12 w-12 overflow-hidden rounded-full bg-mystery-light">
                    <img
                      v-if="connection.imageUrl"
                      :src="connection.imageUrl"
                      :alt="connection.name"
                      class="h-full w-full object-cover"
                    />
                    <div v-else class="flex h-full w-full items-center justify-center">
                      <UserIcon class="h-6 w-6 text-gray-600" />
                    </div>
                  </div>
                  <div class="flex-1">
                    <p class="font-medium text-white">{{ connection.name }}</p>
                    <p class="text-sm text-gray-400">{{ connection.relationship }}</p>
                  </div>
                  <button
                    @click="viewConnection(connection)"
                    class="rounded p-1 text-gray-400 transition-colors hover:bg-mystery-light hover:text-white"
                  >
                    <ChevronRightIcon class="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
  
        <!-- Risk Assessment -->
        <div class="rounded-lg bg-gradient-to-r from-red-900/20 to-orange-900/20 p-4">
          <h3 class="mb-3 text-lg font-semibold text-white">Risk Assessment</h3>
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span class="text-gray-400">Flight Risk:</span>
              <span class="ml-2 font-medium text-white">{{ suspect.flightRisk || 'Low' }}</span>
            </div>
            <div>
              <span class="text-gray-400">Violence Risk:</span>
              <span class="ml-2 font-medium text-white">{{ suspect.violenceRisk || 'Low' }}</span>
            </div>
            <div>
              <span class="text-gray-400">Cooperation:</span>
              <span class="ml-2 font-medium text-white">{{ suspect.cooperationLevel || 'Unknown' }}</span>
            </div>
            <div>
              <span class="text-gray-400">Resources:</span>
              <span class="ml-2 font-medium text-white">{{ suspect.resourceLevel || 'Limited' }}</span>
            </div>
          </div>
        </div>
      </div>
  
      <template #footer>
        <div class="flex w-full items-center justify-between">
          <div class="text-xs text-gray-500">
            Case #{{ suspect?.caseNumber || 'N/A' }} • ID: {{ suspect?.id || 'N/A' }}
          </div>
          <div class="flex items-center gap-3">
            <button
              v-if="canEdit"
              @click="editSuspect"
              class="btn-secondary"
            >
              <PencilIcon class="mr-2 h-4 w-4" />
              Edit
            </button>
            <button
              @click="generateReport"
              class="btn-secondary"
            >
              <DocumentReportIcon class="mr-2 h-4 w-4" />
              Report
            </button>
            <button
              @click="handleClose"
              class="btn-primary"
            >
              Close
            </button>
          </div>
        </div>
      </template>
    </Modal>
  </template>
  
  <script setup>
  import { ref, computed, watch } from 'vue'
  import { formatDistanceToNow } from 'date-fns'
  import DOMPurify from 'dompurify'
  import Modal from '../ui/Modal.vue'
  import {
    UserIcon,
    DocumentTextIcon,
    LocationMarkerIcon,
    PhoneIcon,
    ChatIcon,
    ExclamationIcon,
    RefreshIcon,
    CheckCircleIcon,
    XCircleIcon,
    QuestionMarkCircleIcon,
    ClockIcon,
    ChevronRightIcon,
    ExternalLinkIcon,
    DocumentReportIcon,
    PencilIcon,
    ShieldCheckIcon,
    ShieldExclamationIcon,
    FingerPrintIcon,
    CameraIcon,
    BeakerIcon,
    CalendarIcon,
    LinkIcon,
    EyeIcon
  } from '@heroicons/vue/outline'
  
  const props = defineProps({
    modelValue: {
      type: Boolean,
      required: true
    },
    suspect: {
      type: Object,
      default: null
    },
    suspectId: {
      type: String,
      default: null
    },
    canEdit: {
      type: Boolean,
      default: false
    }
  })
  
  const emit = defineEmits(['update:modelValue', 'edit', 'navigate', 'generateReport'])
  
  // State
  const isOpen = computed({
    get: () => props.modelValue,
    set: (value) => emit('update:modelValue', value)
  })
  
  const isLoading = ref(false)
  const error = ref(null)
  const imageError = ref(false)
  const activeTab = ref('biography')
  
  // Mock data - replace with API calls
  const relatedEvidence = ref([])
  const timeline = ref([])
  const connections = ref([])
  const alibiTimeline = ref([])
  const relatedMotives = ref([])
  
  // Tabs configuration
  const tabs = computed(() => [
    { id: 'biography', name: 'Biography', icon: DocumentTextIcon },
    { id: 'alibi', name: 'Alibi', icon: ShieldCheckIcon },
    { id: 'motive', name: 'Motive', icon: ShieldExclamationIcon },
    { id: 'evidence', name: 'Evidence', icon: FingerPrintIcon, count: relatedEvidence.value.length },
    { id: 'timeline', name: 'Timeline', icon: ClockIcon, count: timeline.value.length },
    { id: 'connections', name: 'Connections', icon: LinkIcon, count: connections.value.length }
  ])
  
  // Computed
  const sanitizedBiography = computed(() => {
    if (!props.suspect?.biography) return '<p class="text-gray-400">No biography available.</p>'
    return DOMPurify.sanitize(props.suspect.biography)
  })
  
  const sanitizedAlibi = computed(() => {
    if (!props.suspect?.alibi) return '<p class="text-gray-400">No alibi provided.</p>'
    return DOMPurify.sanitize(props.suspect.alibi)
  })
  
  const sanitizedMotive = computed(() => {
    if (!props.suspect?.motive) return '<p class="text-gray-400">No motive identified.</p>'
    return DOMPurify.sanitize(props.suspect.motive)
  })
  
  // Methods
  const formatDate = (date) => {
    if (!date) return 'Unknown'
    try {
      return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: 'numeric'
      }).format(new Date(date))
    } catch {
      return 'Invalid Date'
    }
  }
  
  const formatRelativeTime = (date) => {
    if (!date) return ''
    try {
      return formatDistanceToNow(new Date(date), { addSuffix: true })
    } catch {
      return ''
    }
  }
  
  const formatStatus = (status) => {
    const statusMap = {
      cleared: 'Cleared',
      under_investigation: 'Under Investigation',
      prime_suspect: 'Prime Suspect',
      person_of_interest: 'Person of Interest'
    }
    return statusMap[status] || status
  }
  
  const getSuspectRingColor = (status) => {
    const colors = {
      cleared: 'ring-green-500',
      under_investigation: 'ring-yellow-500',
      prime_suspect: 'ring-red-500',
      person_of_interest: 'ring-orange-500'
    }
    return colors[status] || 'ring-gray-500'
  }
  
  const getSuspectStatusClass = (status) => {
    const classes = {
      cleared: 'bg-green-100 text-green-800',
      under_investigation: 'bg-yellow-100 text-yellow-800',
      prime_suspect: 'bg-red-100 text-red-800',
      person_of_interest: 'bg-orange-100 text-orange-800'
    }
    return classes[status] || 'bg-gray-100 text-gray-800'
  }
  
  const getSuspectStatusBadgeClass = (status) => {
    const classes = {
      cleared: 'bg-green-500',
      under_investigation: 'bg-yellow-500',
      prime_suspect: 'bg-red-500',
      person_of_interest: 'bg-orange-500'
    }
    return classes[status] || 'bg-gray-500'
  }
  
  const getSuspectStatusIcon = (status) => {
    const icons = {
      cleared: CheckCircleIcon,
      under_investigation: ClockIcon,
      prime_suspect: ExclamationIcon,
      person_of_interest: QuestionMarkCircleIcon
    }
    return icons[status] || QuestionMarkCircleIcon
  }
  
  const getVerificationIcon = (status) => {
    const icons = {
      verified: CheckCircleIcon,
      pending: ClockIcon,
      rejected: XCircleIcon
    }
    return icons[status] || QuestionMarkCircleIcon
  }
  
  const getVerificationColor = (status) => {
    const colors = {
      verified: 'text-green-500',
      pending: 'text-yellow-500',
      rejected: 'text-red-500'
    }
    return colors[status] || 'text-gray-500'
  }
  
  const getMotiveStrengthColor = (strength) => {
    if (strength >= 75) return 'bg-red-500'
    if (strength >= 50) return 'bg-orange-500'
    if (strength >= 25) return 'bg-yellow-500'
    return 'bg-green-500'
  }
  
  const getEvidenceTypeClass = (type) => {
    const classes = {
      physical: 'bg-blue-500',
      digital: 'bg-purple-500',
      witness: 'bg-green-500',
      document: 'bg-yellow-500'
    }
    return classes[type] || 'bg-gray-500'
  }
  
  const getEvidenceTypeIcon = (type) => {
    const icons = {
      physical: FingerPrintIcon,
      digital: CameraIcon,
      witness: EyeIcon,
      document: DocumentTextIcon
    }
    return icons[type] || DocumentTextIcon
  }
  
  const getTimelineEventClass = (type) => {
    const classes = {
      sighting: 'bg-blue-500',
      interview: 'bg-green-500',
      evidence: 'bg-purple-500',
      incident: 'bg-red-500'
    }
    return classes[type] || 'bg-gray-500'
  }
  
  const getTimelineEventIcon = (type) => {
    const icons = {
      sighting: EyeIcon,
      interview: ChatIcon,
      evidence: FingerPrintIcon,
      incident: ExclamationIcon
    }
    return icons[type] || ClockIcon
  }
  
  // Actions
  const callSuspect = () => {
    if (props.suspect?.phoneNumber) {
      window.location.href = `tel:${props.suspect.phoneNumber}`
    }
  }
  
  const messageSuspect = () => {
    // TODO: Implement messaging
    console.log('Message suspect:', props.suspect?.name)
  }
  
  const trackSuspect = () => {
    // TODO: Implement tracking
    console.log('Track suspect:', props.suspect?.name)
  }
  
  const editSuspect = () => {
    emit('edit', props.suspect)
  }
  
  const generateReport = () => {
    emit('generateReport', props.suspect)
  }
  
  const viewEvidence = (evidence) => {
    emit('navigate', { type: 'evidence', data: evidence })
  }
  
  const viewConnection = (connection) => {
    emit('navigate', { type: 'suspect', data: connection })
  }
  
  const handleClose = () => {
    isOpen.value = false
  }
  
  const retry = async () => {
    await loadSuspectDetails()
  }
  
  const loadSuspectDetails = async () => {
    if (!props.suspectId && !props.suspect) return
    
    isLoading.value = true
    error.value = null
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Load related data
      relatedEvidence.value = [
        {
          id: '1',
          type: 'physical',
          title: 'Fingerprints',
          description: 'Found at crime scene',
          foundAt: new Date()
        },
        {
          id: '2',
          type: 'digital',
          title: 'Security Footage',
          description: 'Captured near location',
          foundAt: new Date()
        }
      ]
      
      timeline.value = [
        {
          id: '1',
          type: 'sighting',
          title: 'Seen at Coffee Shop',
          description: 'Witness reported seeing suspect',
          timestamp: new Date(),
          location: 'Downtown Coffee Shop'
        },
        {
          id: '2',
          type: 'interview',
          title: 'Initial Interview',
          description: 'First police interview conducted',
          timestamp: new Date()
        }
      ]
      
      connections.value = [
        {
          id: '1',
          name: 'Jane Doe',
          relationship: 'Business Partner',
          imageUrl: null
        },
        {
          id: '2',
          name: 'John Smith',
          relationship: 'Friend',
          imageUrl: null
        }
      ]
    } catch (err) {
      error.value = err.message || 'Failed to load suspect details'
    } finally {
      isLoading.value = false
    }
  }
  
  // Lifecycle
  watch(() => props.modelValue, (newVal) => {
    if (newVal) {
      imageError.value = false
      activeTab.value = 'biography'
      loadSuspectDetails()
    }
  })
  </script>
  
  <style scoped>
  /* Button styles */
  .btn-primary {
    @apply inline-flex items-center justify-center rounded-md bg-mystery-accent px-4 py-2 text-sm font-medium text-white shadow-lg shadow-mystery-accent/25 transition-all hover:bg-mystery-accent/90 hover:shadow-xl hover:shadow-mystery-accent/30 focus:outline-none focus:ring-2 focus:ring-mystery-accent focus:ring-offset-2 focus:ring-offset-mystery-dark disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none;
  }
  
  .btn-secondary {
    @apply inline-flex items-center justify-center rounded-md border border-mystery-light bg-mystery-medium px-4 py-2 text-sm font-medium text-gray-300 transition-all hover:border-mystery-accent/50 hover:bg-mystery-light hover:text-white hover:shadow-lg hover:shadow-mystery-accent/10 focus:outline-none focus:ring-2 focus:ring-mystery-accent focus:ring-offset-2 focus:ring-offset-mystery-dark disabled:cursor-not-allowed disabled:opacity-50;
  }
  
  /* Prose enhancements */
  .prose :deep(h1) {
    @apply mb-4 text-2xl font-bold text-white;
  }
  
  .prose :deep(h2) {
    @apply mb-3 text-xl font-semibold text-white;
  }
  
  .prose :deep(p) {
    @apply mb-4 text-gray-300;
  }
  
  .prose :deep(ul) {
    @apply mb-4 list-inside list-disc text-gray-300;
  }
  
  .prose :deep(ol) {
    @apply mb-4 list-inside list-decimal text-gray-300;
  }
  
  .prose :deep(li) {
    @apply mb-1;
  }
  
  .prose :deep(a) {
    @apply text-mystery-accent hover:text-mystery-accent-dark;
  }
  
  .prose :deep(blockquote) {
    @apply my-4 border-l-4 border-mystery-accent pl-4 italic text-gray-400;
  }
  
  .prose :deep(code) {
    @apply rounded bg-mystery-medium px-1 py-0.5 font-mono text-sm;
  }
  
  .prose :deep(pre) {
    @apply my-4 overflow-x-auto rounded-lg bg-mystery-medium p-4;
  }
  
  .prose :deep(pre code) {
    @apply bg-transparent p-0;
  }
  </style>