<template>
    <Modal
      v-model="isOpen"
      :title="clue?.title || 'Clue Details'"
      size="lg"
      :loading="isLoading"
      :icon="DocumentTextIcon"
      icon-color="primary"
      @close="handleClose"
    >
      <!-- Loading State -->
      <div v-if="isLoading" class="space-y-4">
        <div class="h-64 animate-pulse rounded-lg bg-mystery-medium" />
        <div class="space-y-2">
          <div class="h-4 w-3/4 animate-pulse rounded bg-mystery-medium" />
          <div class="h-4 w-1/2 animate-pulse rounded bg-mystery-medium" />
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
      <div v-else-if="clue" class="space-y-6">
        <!-- Action Bar -->
        <div class="flex items-center justify-between rounded-lg bg-mystery-medium/50 p-3">
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-400">Quick Actions:</span>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="toggleBookmark"
              class="rounded p-1.5 text-gray-400 transition-colors hover:bg-mystery-medium hover:text-white"
              :aria-label="isBookmarked ? 'Remove bookmark' : 'Add bookmark'"
            >
              <BookmarkIcon class="h-5 w-5" :class="{ 'fill-current text-yellow-500': isBookmarked }" />
            </button>
            <button
              @click="shareClue"
              class="rounded p-1.5 text-gray-400 transition-colors hover:bg-mystery-medium hover:text-white"
              aria-label="Share clue"
            >
              <ShareIcon class="h-5 w-5" />
            </button>
            <button
              @click="printClue"
              class="rounded p-1.5 text-gray-400 transition-colors hover:bg-mystery-medium hover:text-white"
              aria-label="Print clue"
            >
              <PrinterIcon class="h-5 w-5" />
            </button>
            <button
              v-if="canEdit"
              @click="editClue"
              class="rounded p-1.5 text-gray-400 transition-colors hover:bg-mystery-medium hover:text-white"
              aria-label="Edit clue"
            >
              <PencilIcon class="h-5 w-5" />
            </button>
          </div>
        </div>
  
        <!-- Clue Image with Lightbox -->
        <div
          v-if="clue.imageUrl"
          class="group relative aspect-video overflow-hidden rounded-lg bg-mystery-medium"
        >
          <img
            v-if="!imageError"
            :src="clue.imageUrl"
            :alt="clue.title"
            class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
            @error="imageError = true"
            @load="imageLoaded = true"
            :class="{ 'opacity-0': !imageLoaded }"
          />
          <div v-if="!imageLoaded && !imageError" class="absolute inset-0 flex items-center justify-center">
            <div class="h-8 w-8 animate-spin rounded-full border-2 border-mystery-accent border-t-transparent" />
          </div>
          <div v-if="imageError" class="flex h-full items-center justify-center">
            <PhotographIcon class="h-16 w-16 text-gray-600" />
            <p class="mt-2 text-sm text-gray-500">Image failed to load</p>
          </div>
          <button
            v-if="imageLoaded && !imageError"
            @click="openLightbox"
            class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-0 transition-all group-hover:bg-opacity-30"
          >
            <ZoomInIcon class="h-8 w-8 text-white opacity-0 transition-opacity group-hover:opacity-100" />
          </button>
        </div>
  
        <!-- Enhanced Metadata with Icons -->
        <div class="grid grid-cols-2 gap-4 rounded-lg bg-mystery-medium p-4">
          <div class="flex items-start space-x-3">
            <LocationMarkerIcon class="mt-0.5 h-5 w-5 text-gray-400" />
            <div>
              <h4 class="text-sm font-medium text-gray-400">Found At</h4>
              <p class="mt-1 text-white">{{ clue.location || 'Unknown Location' }}</p>
            </div>
          </div>
          <div class="flex items-start space-x-3">
            <UserIcon class="mt-0.5 h-5 w-5 text-gray-400" />
            <div>
              <h4 class="text-sm font-medium text-gray-400">Found By</h4>
              <p class="mt-1 text-white">{{ clue.foundBy || 'Unknown' }}</p>
            </div>
          </div>
          <div class="flex items-start space-x-3">
            <CalendarIcon class="mt-0.5 h-5 w-5 text-gray-400" />
            <div>
              <h4 class="text-sm font-medium text-gray-400">Found On</h4>
              <p class="mt-1 text-white">{{ formatDate(clue.foundAt) }}</p>
              <p class="text-xs text-gray-500">{{ formatRelativeTime(clue.foundAt) }}</p>
            </div>
          </div>
          <div class="flex items-start space-x-3">
            <StatusIcon :status="clue.status" class="mt-0.5 h-5 w-5" />
            <div>
              <h4 class="text-sm font-medium text-gray-400">Status</h4>
              <p class="mt-1">
                <span
                  class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
                  :class="getStatusClass(clue.status)"
                >
                  {{ formatStatus(clue.status) }}
                </span>
              </p>
            </div>
          </div>
        </div>
  
        <!-- Clue Content with Better Typography -->
        <div class="prose prose-invert max-w-none">
          <div v-html="sanitizedDescription" />
        </div>
  
        <!-- Tags -->
        <div v-if="clue.tags && clue.tags.length > 0" class="flex flex-wrap gap-2">
          <span
            v-for="tag in clue.tags"
            :key="tag"
            class="inline-flex items-center rounded-full bg-mystery-accent/20 px-3 py-1 text-xs font-medium text-mystery-accent"
          >
            <TagIcon class="mr-1 h-3 w-3" />
            {{ tag }}
          </span>
        </div>
  
        <!-- Evidence Chain -->
        <div v-if="clue.evidenceChain" class="rounded-lg bg-mystery-medium p-4">
          <h4 class="mb-3 flex items-center text-sm font-medium text-gray-400">
            <LinkIcon class="mr-2 h-4 w-4" />
            Evidence Chain
          </h4>
          <div class="space-y-2">
            <div
              v-for="(evidence, index) in clue.evidenceChain"
              :key="evidence.id"
              class="flex items-center space-x-2"
            >
              <div class="flex h-6 w-6 items-center justify-center rounded-full bg-mystery-accent text-xs font-bold text-white">
                {{ index + 1 }}
              </div>
              <p class="text-sm text-gray-300">{{ evidence.description }}</p>
            </div>
          </div>
        </div>
  
        <!-- Related Elements with Better UI -->
        <div v-if="relatedElements.length > 0">
          <h4 class="mb-3 flex items-center text-sm font-medium text-gray-400">
            <CollectionIcon class="mr-2 h-4 w-4" />
            Related Elements ({{ relatedElements.length }})
          </h4>
          <div class="grid grid-cols-2 gap-3">
            <button
              v-for="element in relatedElements"
              :key="element.id"
              @click="navigateToElement(element)"
              class="flex items-center space-x-3 rounded-lg bg-mystery-medium p-3 text-left transition-all hover:bg-mystery-light hover:shadow-md"
            >
              <div
                class="flex h-10 w-10 items-center justify-center rounded-full"
                :class="getElementTypeClass(element.type)"
              >
                <component :is="getElementTypeIcon(element.type)" class="h-5 w-5 text-white" />
              </div>
              <div class="flex-1 overflow-hidden">
                <p class="truncate text-sm font-medium text-white">{{ element.title }}</p>
                <p class="text-xs text-gray-400">{{ element.type }} • {{ formatRelativeTime(element.createdAt) }}</p>
              </div>
              <ChevronRightIcon class="h-4 w-4 text-gray-400" />
            </button>
          </div>
        </div>
  
        <!-- Analysis Section -->
        <div v-if="clue.analysis" class="rounded-lg bg-gradient-to-r from-mystery-medium to-mystery-light p-4">
          <h4 class="mb-3 flex items-center text-sm font-medium text-white">
            <BeakerIcon class="mr-2 h-4 w-4" />
            Forensic Analysis
          </h4>
          <div class="space-y-2 text-sm text-gray-300">
            <p><strong>Type:</strong> {{ clue.analysis.type }}</p>
            <p><strong>Confidence:</strong> {{ clue.analysis.confidence }}%</p>
            <p><strong>Summary:</strong> {{ clue.analysis.summary }}</p>
          </div>
        </div>
  
        <!-- Activity Timeline -->
        <div v-if="activities.length > 0" class="space-y-2">
          <h4 class="mb-3 flex items-center text-sm font-medium text-gray-400">
            <ClockIcon class="mr-2 h-4 w-4" />
            Recent Activity
          </h4>
          <div class="max-h-40 space-y-2 overflow-y-auto">
            <div
              v-for="activity in activities"
              :key="activity.id"
              class="flex items-start space-x-3 rounded-lg bg-mystery-medium/50 p-2"
            >
              <component :is="getActivityIcon(activity.type)" class="mt-0.5 h-4 w-4 text-gray-400" />
              <div class="flex-1">
                <p class="text-sm text-gray-300">{{ activity.description }}</p>
                <p class="text-xs text-gray-500">{{ formatRelativeTime(activity.timestamp) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
  
      <template #footer>
        <div class="flex w-full items-center justify-between">
          <div class="text-xs text-gray-500">
            ID: {{ clue?.id || 'N/A' }}
          </div>
          <div class="flex items-center gap-3">
            <button
              v-if="canDelete"
              @click="confirmDelete"
              class="btn-danger"
            >
              <TrashIcon class="mr-2 h-4 w-4" />
              Delete
            </button>
            <button
              @click="handleClose"
              class="btn-secondary"
            >
              Close
            </button>
          </div>
        </div>
      </template>
    </Modal>
  
    <!-- Image Lightbox -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-opacity duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="showLightbox"
          class="fixed inset-0 z-[60] flex items-center justify-center bg-black bg-opacity-90 p-4"
          @click="closeLightbox"
        >
          <img
            :src="clue.imageUrl"
            :alt="clue.title"
            class="max-h-full max-w-full object-contain"
            @click.stop
          />
          <button
            @click="closeLightbox"
            class="absolute right-4 top-4 rounded-full bg-black bg-opacity-50 p-2 text-white transition-colors hover:bg-opacity-75"
          >
            <XIcon class="h-6 w-6" />
          </button>
        </div>
      </Transition>
    </Teleport>
  </template>
  
  <script setup>
  import { ref, computed, watch, onMounted } from 'vue'
  import { formatDistanceToNow } from 'date-fns'
  import DOMPurify from 'dompurify'
  import Modal from '../ui/Modal.vue'
  import {
    UserIcon,
    DocumentTextIcon,
    LocationMarkerIcon,
    TagIcon,
    CalendarIcon,
    BookmarkIcon,
    ShareIcon,
    PrinterIcon,
    PencilIcon,
    PhotographIcon,
    ZoomInIcon,
    ChevronRightIcon,
    ExclamationIcon,
    RefreshIcon,
    ClockIcon,
    BeakerIcon,
    CollectionIcon,
    LinkIcon,
    TrashIcon,
    XIcon,
    ChatIcon,
    SearchIcon
  } from '@heroicons/vue/outline'
  
  const props = defineProps({
    modelValue: {
      type: Boolean,
      required: true
    },
    clue: {
      type: Object,
      default: null
    },
    clueId: {
      type: String,
      default: null
    },
    canEdit: {
      type: Boolean,
      default: false
    },
    canDelete: {
      type: Boolean,
      default: false
    }
  })
  
  const emit = defineEmits(['update:modelValue', 'edit', 'delete', 'navigate'])
  
  // State
  const isOpen = computed({
    get: () => props.modelValue,
    set: (value) => emit('update:modelValue', value)
  })
  
  const isLoading = ref(false)
  const error = ref(null)
  const imageError = ref(false)
  const imageLoaded = ref(false)
  const showLightbox = ref(false)
  const isBookmarked = ref(false)
  const relatedElements = ref([])
  const activities = ref([])
  
  // Computed
  const sanitizedDescription = computed(() => {
    if (!props.clue?.description) return ''
    return DOMPurify.sanitize(props.clue.description, {
      ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'blockquote', 'a', 'code', 'pre'],
      ALLOWED_ATTR: ['href', 'target', 'rel']
    })
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
      verified: 'Verified',
      pending: 'Pending Review',
      disputed: 'Disputed'
    }
    return statusMap[status] || status
  }
  
  const getStatusClass = (status) => {
    const classes = {
      verified: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      disputed: 'bg-red-100 text-red-800'
    }
    return classes[status] || 'bg-gray-100 text-gray-800'
  }
  
  const StatusIcon = ({ status }) => {
    const icons = {
      verified: CheckCircleIcon,
      pending: ClockIcon,
      disputed: ExclamationIcon
    }
    return icons[status] || QuestionMarkCircleIcon
  }
  
  const getElementTypeClass = (type) => {
    const classes = {
      suspect: 'bg-red-500',
      clue: 'bg-mystery-accent',
      location: 'bg-green-500',
      note: 'bg-yellow-500'
    }
    return classes[type] || 'bg-gray-500'
  }
  
  const getElementTypeIcon = (type) => {
    const icons = {
      suspect: UserIcon,
      clue: DocumentTextIcon,
      location: LocationMarkerIcon,
      note: TagIcon
    }
    return icons[type] || DocumentTextIcon
  }
  
  const getActivityIcon = (type) => {
    const icons = {
      created: PlusIcon,
      updated: PencilIcon,
      viewed: EyeIcon,
      commented: ChatIcon,
      analyzed: BeakerIcon
    }
    return icons[type] || ClockIcon
  }
  
  // Actions
  const toggleBookmark = () => {
    isBookmarked.value = !isBookmarked.value
    // TODO: Persist bookmark state
  }
  
  const shareClue = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: props.clue.title,
          text: props.clue.description,
          url: window.location.href
        })
      } catch (err) {
        console.log('Share failed:', err)
      }
    } else {
      // Fallback: Copy to clipboard
      navigator.clipboard.writeText(window.location.href)
      // TODO: Show toast notification
    }
  }
  
  const printClue = () => {
    window.print()
  }
  
  const editClue = () => {
    emit('edit', props.clue)
  }
  
  const confirmDelete = () => {
    if (confirm('Are you sure you want to delete this clue? This action cannot be undone.')) {
      emit('delete', props.clue.id)
      handleClose()
    }
  }
  
  const openLightbox = () => {
    showLightbox.value = true
  }
  
  const closeLightbox = () => {
    showLightbox.value = false
  }
  
  const navigateToElement = (element) => {
    emit('navigate', element)
  }
  
  const handleClose = () => {
    isOpen.value = false
  }
  
  const retry = async () => {
    await loadClueDetails()
  }
  
  const loadClueDetails = async () => {
    if (!props.clueId && !props.clue) return
    
    isLoading.value = true
    error.value = null
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Load related elements
      relatedElements.value = [
        // Mock data - replace with API call
      ]
      
      // Load activities
      activities.value = [
        // Mock data - replace with API call
      ]
    } catch (err) {
      error.value = err.message || 'Failed to load clue details'
    } finally {
      isLoading.value = false
    }
  }
  
  // Lifecycle
  watch(() => props.modelValue, (newVal) => {
    if (newVal) {
      imageError.value = false
      imageLoaded.value = false
      loadClueDetails()
    }
  })
  
  onMounted(() => {
    if (props.modelValue) {
      loadClueDetails()
    }
  })
  </script>
  
  <style scoped>
  /* Enhanced button styles */
  .btn-primary {
    @apply inline-flex items-center justify-center rounded-md bg-mystery-accent px-4 py-2 text-sm font-medium text-white shadow-lg shadow-mystery-accent/25 transition-all hover:bg-mystery-accent/90 hover:shadow-xl hover:shadow-mystery-accent/30 focus:outline-none focus:ring-2 focus:ring-mystery-accent focus:ring-offset-2 focus:ring-offset-mystery-dark disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none;
  }
  
  .btn-secondary {
    @apply inline-flex items-center justify-center rounded-md border border-mystery-light bg-mystery-medium px-4 py-2 text-sm font-medium text-gray-300 transition-all hover:border-mystery-accent/50 hover:bg-mystery-light hover:text-white hover:shadow-lg hover:shadow-mystery-accent/10 focus:outline-none focus:ring-2 focus:ring-mystery-accent focus:ring-offset-2 focus:ring-offset-mystery-dark disabled:cursor-not-allowed disabled:opacity-50;
  }
  
  .btn-danger {
    @apply inline-flex items-center justify-center rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white transition-all hover:bg-red-700 hover:shadow-lg hover:shadow-red-600/25 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-mystery-dark disabled:cursor-not-allowed disabled:opacity-50;
  }
  
  /* Print styles */
  @media print {
    .no-print {
      display: none !important;
    }
  }
  
  /* Custom scrollbar for activity timeline */
  .overflow-y-auto::-webkit-scrollbar {
    width: 6px;
  }
  
  .overflow-y-auto::-webkit-scrollbar-track {
    background: rgba(15, 23, 42, 0.3);
  }
  
  .overflow-y-auto::-webkit-scrollbar-thumb {
    background: rgba(148, 163, 184, 0.3);
    border-radius: 3px;
  }
  
  .overflow-y-auto::-webkit-scrollbar-thumb:hover {
    background: rgba(148, 163, 184, 0.5);
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