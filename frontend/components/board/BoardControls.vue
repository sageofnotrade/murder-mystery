<template>
    <div class="board-controls-panel" :class="{ 'collapsed': isCollapsed }">
      <!-- Collapse Toggle -->
      <button 
        @click="isCollapsed = !isCollapsed"
        class="collapse-toggle"
        :aria-label="isCollapsed ? 'Expand controls' : 'Collapse controls'"
      >
        <ChevronIcon :class="{ 'rotated': isCollapsed }" />
      </button>
  
      <div v-show="!isCollapsed" class="controls-content">
        <!-- Search Section -->
        <div class="control-section search-section">
          <h3 class="section-title">
            <SearchIcon class="icon" />
            Search
          </h3>
          <div class="search-wrapper">
            <input
              type="text"
              v-model="searchQuery"
              placeholder="Search elements..."
              class="search-input"
              @input="handleSearch"
              aria-label="Search board elements"
            />
            <button 
              v-if="searchQuery" 
              @click="clearSearch"
              class="clear-button"
              aria-label="Clear search"
            >
              <XIcon class="icon-sm" />
            </button>
          </div>
          <div v-if="searchQuery" class="search-results">
            {{ filteredCount }} of {{ totalCount }} elements
          </div>
        </div>
  
        <!-- Filter Section -->
        <div class="control-section filter-section">
          <h3 class="section-title">
            <FilterIcon class="icon" />
            Filter by Type
          </h3>
          <div class="filter-chips">
            <button
              v-for="type in elementTypes"
              :key="type.value"
              @click="toggleTypeFilter(type.value)"
              :class="[
                'filter-chip',
                `type-${type.value}`,
                { 'active': typeFilters.includes(type.value) }
              ]"
              :aria-pressed="typeFilters.includes(type.value)"
            >
              <component :is="type.icon" class="chip-icon" />
              {{ type.label }}
              <span class="count">{{ getTypeCount(type.value) }}</span>
            </button>
          </div>
          <button 
            v-if="typeFilters.length > 0"
            @click="clearFilters"
            class="clear-filters-btn"
          >
            Clear Filters
          </button>
        </div>
  
        <!-- Grouping Section -->
        <div class="control-section group-section">
          <h3 class="section-title">
            <CollectionIcon class="icon" />
            Group By
          </h3>
          <div class="group-options">
            <label
              v-for="option in groupingOptions"
              :key="option.value"
              class="group-option"
            >
              <input
                type="radio"
                :value="option.value"
                v-model="groupBy"
                @change="handleGrouping"
                class="group-radio"
              />
              <span class="option-label">
                <component :is="option.icon" class="option-icon" />
                {{ option.label }}
              </span>
            </label>
          </div>
        </div>
  
        <!-- Status Filters (when grouped by status) -->
        <div v-if="groupBy === 'status'" class="control-section status-section">
          <h3 class="section-title">
            <TagIcon class="icon" />
            Status Filters
          </h3>
          <div class="status-filters">
            <label v-for="status in statusOptions" :key="status.value" class="status-option">
              <input
                type="checkbox"
                :value="status.value"
                v-model="statusFilters"
                @change="handleStatusFilter"
                class="status-checkbox"
              />
              <span class="status-label" :style="{ color: status.color }">
                {{ status.label }}
              </span>
            </label>
          </div>
        </div>
  
        <!-- Statistics -->
        <div class="control-section stats-section">
          <h3 class="section-title">
            <ChartBarIcon class="icon" />
            Board Statistics
          </h3>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-value">{{ totalElements }}</span>
              <span class="stat-label">Total Elements</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ totalConnections }}</span>
              <span class="stat-label">Connections</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ highRelevanceCount }}</span>
              <span class="stat-label">High Priority</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, watch } from 'vue'
  import { useBoardStore } from '@/stores/boardStore'
  import { 
    SearchIcon, 
    FilterIcon, 
    CollectionIcon,
    TagIcon,
    ChartBarIcon,
    XIcon,
    ChevronRightIcon as ChevronIcon,
    UserIcon,
    DocumentTextIcon,
    LocationMarkerIcon,
    PencilIcon,
    ViewGridIcon,
    StatusOnlineIcon,
    SparklesIcon
  } from '@heroicons/vue/outline'
  
  const boardStore = useBoardStore()
  
  // Component state
  const isCollapsed = ref(false)
  const searchQuery = ref('')
  const typeFilters = ref([])
  const statusFilters = ref([])
  const groupBy = ref('')
  
  // Element type configuration
  const elementTypes = [
    { value: 'suspect', label: 'Suspects', icon: UserIcon },
    { value: 'clue', label: 'Clues', icon: DocumentTextIcon },
    { value: 'location', label: 'Locations', icon: LocationMarkerIcon },
    { value: 'note', label: 'Notes', icon: PencilIcon }
  ]
  
  // Grouping options
  const groupingOptions = [
    { value: '', label: 'No Grouping', icon: ViewGridIcon },
    { value: 'type', label: 'By Type', icon: FilterIcon },
    { value: 'status', label: 'By Status', icon: StatusOnlineIcon },
    { value: 'relevance', label: 'By Relevance', icon: SparklesIcon }
  ]
  
  // Status options
  const statusOptions = [
    { value: 'new', label: 'New', color: '#3b82f6' },
    { value: 'investigating', label: 'Investigating', color: '#f59e0b' },
    { value: 'verified', label: 'Verified', color: '#10b981' },
    { value: 'dismissed', label: 'Dismissed', color: '#ef4444' },
    { value: 'unknown', label: 'Unknown', color: '#6b7280' }
  ]
  
  // Computed properties
  const totalElements = computed(() => boardStore.elements.length)
  const totalConnections = computed(() => boardStore.connections.length)
  const filteredCount = computed(() => boardStore.filteredElements.length)
  const totalCount = computed(() => boardStore.elements.length)
  
  const highRelevanceCount = computed(() => {
    return boardStore.elements.filter(el => (el.relevance || 0) >= 0.8).length
  })
  
  const getTypeCount = (type) => {
    return boardStore.elements.filter(el => el.type === type).length
  }
  
  // Search handlers
  const handleSearch = () => {
    boardStore.setSearchQuery(searchQuery.value)
  }
  
  const clearSearch = () => {
    searchQuery.value = ''
    boardStore.setSearchQuery('')
  }
  
  // Filter handlers
  const toggleTypeFilter = (type) => {
    const index = typeFilters.value.indexOf(type)
    if (index === -1) {
      typeFilters.value.push(type)
    } else {
      typeFilters.value.splice(index, 1)
    }
    boardStore.setTypeFilters(typeFilters.value)
  }
  
  const clearFilters = () => {
    typeFilters.value = []
    boardStore.setTypeFilters([])
  }
  
  // Status filter handler
  const handleStatusFilter = () => {
    boardStore.setStatusFilters(statusFilters.value)
  }
  
  // Grouping handler
  const handleGrouping = () => {
    boardStore.setGrouping(groupBy.value)
  }
  
  // Watch for external changes
  watch(() => boardStore.searchQuery, (newVal) => {
    searchQuery.value = newVal
  })
  
  watch(() => boardStore.typeFilters, (newVal) => {
    typeFilters.value = [...newVal]
  })
  
  watch(() => boardStore.grouping, (newVal) => {
    groupBy.value = newVal
  })
  </script>
  
  <style scoped>
  .board-controls-panel {
    position: fixed;
    top: 1rem;
    right: 1rem;
    width: 320px;
    max-height: calc(100vh - 2rem);
    background: rgba(15, 23, 42, 0.95);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(148, 163, 184, 0.1);
    border-radius: 12px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
    z-index: 100;
    transition: all 0.3s ease;
    overflow: hidden;
  }
  
  .board-controls-panel.collapsed {
    width: 48px;
    height: 48px;
  }
  
  .collapse-toggle {
    position: absolute;
    top: 0.75rem;
    right: 0.75rem;
    width: 32px;
    height: 32px;
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
    z-index: 10;
  }
  
  .collapse-toggle:hover {
    background: rgba(51, 65, 85, 0.8);
    border-color: rgba(148, 163, 184, 0.3);
  }
  
  .collapse-toggle svg {
    width: 16px;
    height: 16px;
    color: #94a3b8;
    transition: transform 0.3s ease;
  }
  
  .collapse-toggle svg.rotated {
    transform: rotate(180deg);
  }
  
  .controls-content {
    padding: 3.5rem 1.25rem 1.25rem;
    overflow-y: auto;
    max-height: calc(100vh - 2rem);
  }
  
  .control-section {
    margin-bottom: 1.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid rgba(148, 163, 184, 0.1);
  }
  
  .control-section:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
  }
  
  .section-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .icon {
    width: 16px;
    height: 16px;
    color: #94a3b8;
  }
  
  .icon-sm {
    width: 14px;
    height: 14px;
  }
  
  /* Search Section */
  .search-wrapper {
    position: relative;
  }
  
  .search-input {
    width: 100%;
    padding: 0.5rem 2.5rem 0.5rem 0.75rem;
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 8px;
    color: #e2e8f0;
    font-size: 0.875rem;
    transition: all 0.2s ease;
  }
  
  .search-input:focus {
    outline: none;
    border-color: #3b82f6;
    background: rgba(30, 41, 59, 0.8);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
  
  .clear-button {
    position: absolute;
    right: 0.5rem;
    top: 50%;
    transform: translateY(-50%);
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    color: #64748b;
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.2s ease;
  }
  
  .clear-button:hover {
    color: #e2e8f0;
    background: rgba(148, 163, 184, 0.1);
  }
  
  .search-results {
    margin-top: 0.5rem;
    font-size: 0.75rem;
    color: #94a3b8;
  }
  
  /* Filter Section */
  .filter-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .filter-chip {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.375rem 0.75rem;
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 9999px;
    color: #94a3b8;
    font-size: 0.75rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .filter-chip:hover {
    background: rgba(51, 65, 85, 0.6);
    border-color: rgba(148, 163, 184, 0.3);
  }
  
  .filter-chip.active {
    background: rgba(59, 130, 246, 0.2);
    border-color: #3b82f6;
    color: #60a5fa;
  }
  
  .filter-chip.type-suspect.active {
    background: rgba(239, 68, 68, 0.2);
    border-color: #ef4444;
    color: #f87171;
  }
  
  .filter-chip.type-clue.active {
    background: rgba(59, 130, 246, 0.2);
    border-color: #3b82f6;
    color: #60a5fa;
  }
  
  .filter-chip.type-location.active {
    background: rgba(16, 185, 129, 0.2);
    border-color: #10b981;
    color: #34d399;
  }
  
  .filter-chip.type-note.active {
    background: rgba(245, 158, 11, 0.2);
    border-color: #f59e0b;
    color: #fbbf24;
  }
  
  .chip-icon {
    width: 14px;
    height: 14px;
  }
  
  .count {
    font-size: 0.625rem;
    padding: 0.125rem 0.375rem;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 9999px;
  }
  
  .clear-filters-btn {
    margin-top: 0.75rem;
    padding: 0.375rem 0.75rem;
    background: transparent;
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 6px;
    color: #94a3b8;
    font-size: 0.75rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .clear-filters-btn:hover {
    border-color: rgba(148, 163, 184, 0.3);
    color: #e2e8f0;
  }
  
  /* Grouping Section */
  .group-options {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .group-option {
    display: flex;
    align-items: center;
    cursor: pointer;
  }
  
  .group-radio {
    margin-right: 0.5rem;
    cursor: pointer;
  }
  
  .option-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #94a3b8;
    font-size: 0.875rem;
    transition: color 0.2s ease;
  }
  
  .group-option:hover .option-label {
    color: #e2e8f0;
  }
  
  .group-radio:checked + .option-label {
    color: #60a5fa;
    font-weight: 500;
  }
  
  .option-icon {
    width: 16px;
    height: 16px;
  }
  
  /* Status Section */
  .status-filters {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .status-option {
    display: flex;
    align-items: center;
    cursor: pointer;
  }
  
  .status-checkbox {
    margin-right: 0.5rem;
    cursor: pointer;
  }
  
  .status-label {
    font-size: 0.875rem;
    font-weight: 500;
    transition: opacity 0.2s ease;
  }
  
  .status-option:hover .status-label {
    opacity: 0.8;
  }
  
  /* Statistics Section */
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
  }
  
  .stat-item {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(148, 163, 184, 0.1);
    border-radius: 8px;
    padding: 0.75rem;
    text-align: center;
  }
  
  .stat-value {
    display: block;
    font-size: 1.25rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 0.25rem;
  }
  
  .stat-label {
    display: block;
    font-size: 0.625rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  /* Responsive Design */
  @media (max-width: 768px) {
    .board-controls-panel {
      width: 100%;
      max-width: 100%;
      top: auto;
      bottom: 0;
      left: 0;
      right: 0;
      border-radius: 12px 12px 0 0;
      max-height: 70vh;
    }
  
    .controls-content {
      max-height: calc(70vh - 3rem);
    }
  
    .stats-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  
  /* Scrollbar Styling */
  .controls-content::-webkit-scrollbar {
    width: 6px;
  }
  
  .controls-content::-webkit-scrollbar-track {
    background: rgba(15, 23, 42, 0.3);
  }
  
  .controls-content::-webkit-scrollbar-thumb {
    background: rgba(148, 163, 184, 0.3);
    border-radius: 3px;
  }
  
  .controls-content::-webkit-scrollbar-thumb:hover {
    background: rgba(148, 163, 184, 0.5);
  }
  </style>