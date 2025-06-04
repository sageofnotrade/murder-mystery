import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ClueDetail from '@/components/board/ClueDetail.vue'
import ClueRelatedSuspects from '@/components/board/ClueRelatedSuspects.vue'

// Mock the clue store
const mockClueStore = {
  getClueDetails: vi.fn(),
  updateClueRelevance: vi.fn(),
  markClueAsRedHerring: vi.fn(),
  updateClueNotes: vi.fn(),
  addClueConnection: vi.fn(),
  analyzeClue: vi.fn(),
  loading: false,
  error: null
}

vi.mock('@/stores/clue', () => ({
  useClueStore: () => mockClueStore
}))

// Mock clue data
const mockClue = {
  id: 'clue-1',
  description: 'A bloody knife found in the kitchen',
  type: 'physical',
  location: 'Kitchen',
  discovered_at: '2024-01-01T12:00:00Z',
  discovery_method: 'Visual inspection',
  discovery_location: 'Kitchen counter',
  relevance_score: 0.7,
  is_red_herring: false,
  notes: 'Found near the sink',
  connections: [
    {
      id: 'conn-1',
      connected_clue_id: 'clue-2',
      connection_type: 'Related evidence',
      details: {
        reason: 'Both found in same room'
      },
      created_at: '2024-01-01T12:30:00Z'
    }
  ],
  related_suspects: ['suspect-1', 'suspect-2']
}

describe('ClueDetail', () => {
  let wrapper
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    
    // Reset mocks
    vi.clearAllMocks()
    mockClueStore.getClueDetails.mockResolvedValue(mockClue)
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = (props = {}) => {
    return mount(ClueDetail, {
      props: {
        clueId: 'clue-1',
        ...props
      },
      global: {
        plugins: [pinia],
        stubs: {
          ClueRelatedSuspects: true
        }
      }
    })
  }

  describe('Component Rendering', () => {
    it('should render the component correctly', async () => {
      wrapper = createWrapper()
      
      // Wait for component to load clue data
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 10))

      expect(wrapper.find('[data-testid="clue-detail"]').exists()).toBe(true)
      expect(mockClueStore.getClueDetails).toHaveBeenCalledWith('clue-1')
    })

    it('should display clue information correctly', async () => {
      wrapper = createWrapper()
      
      // Wait for data to load
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 10))

      expect(wrapper.text()).toContain('A bloody knife found in the kitchen')
      expect(wrapper.text()).toContain('physical')
      expect(wrapper.text()).toContain('Kitchen')
      expect(wrapper.text()).toContain('Visual inspection')
      expect(wrapper.text()).toContain('Kitchen counter')
    })

    it('should display discovery information section', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 10))

      const discoverySection = wrapper.find('[aria-labelledby="discovery-title"]')
      expect(discoverySection.exists()).toBe(true)
      expect(discoverySection.text()).toContain('Discovery Information')
      expect(discoverySection.text()).toContain('Visual inspection')
      expect(discoverySection.text()).toContain('Kitchen counter')
    })

    it('should render ClueRelatedSuspects component when clue data is loaded', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 10))

      expect(wrapper.findComponent(ClueRelatedSuspects).exists()).toBe(true)
    })
  })

  describe('Relevance Score Functionality', () => {
    it('should display the correct relevance score', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 10))

      const relevanceSlider = wrapper.find('#relevance-slider')
      expect(relevanceSlider.exists()).toBe(true)
      expect(relevanceSlider.element.value).toBe('0.7')
      expect(wrapper.text()).toContain('70%')
    })

    it('should update relevance score when slider changes', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 10))

      const relevanceSlider = wrapper.find('#relevance-slider')
      await relevanceSlider.setValue('0.9')
      await relevanceSlider.trigger('change')

      expect(mockClueStore.updateClueRelevance).toHaveBeenCalledWith('clue-1', 0.9)
    })
  })

  describe('Red Herring Functionality', () => {
    it('should display red herring checkbox with correct initial value', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 10))

      const redHerringCheckbox = wrapper.find('#red-herring-checkbox')
      expect(redHerringCheckbox.exists()).toBe(true)
      expect(redHerringCheckbox.element.checked).toBe(false)
    })

    it('should update red herring status when checkbox changes', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 10))

      const redHerringCheckbox = wrapper.find('#red-herring-checkbox')
      await redHerringCheckbox.setChecked(true)
      await redHerringCheckbox.trigger('change')

      expect(mockClueStore.markClueAsRedHerring).toHaveBeenCalledWith('clue-1', true)
    })
  })

  describe('Notes Functionality', () => {
    it('should display notes textarea with initial value', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 10))

      const notesTextarea = wrapper.find('#notes-textarea')
      expect(notesTextarea.exists()).toBe(true)
      expect(notesTextarea.element.value).toBe('Found near the sink')
    })

    it('should update notes when textarea loses focus', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 10))

      const notesTextarea = wrapper.find('#notes-textarea')
      await notesTextarea.setValue('Updated notes')
      await notesTextarea.trigger('blur')

      expect(mockClueStore.updateClueNotes).toHaveBeenCalledWith('clue-1', 'Updated notes')
    })
  })

  describe('Connections Functionality', () => {
    it('should display existing connections', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 10))

      const connectionsSection = wrapper.find('[aria-labelledby="connections-title"]')
      expect(connectionsSection.exists()).toBe(true)
      expect(connectionsSection.text()).toContain('Related evidence')
      expect(connectionsSection.text()).toContain('Both found in same room')
    })

    it('should show add connection modal when button is clicked', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 10))

      const addConnectionBtn = wrapper.find('button:contains("Add Connection")')
      expect(addConnectionBtn.exists()).toBe(true)

      await addConnectionBtn.trigger('click')
      
      const modal = wrapper.find('[role="dialog"]')
      expect(modal.exists()).toBe(true)
      expect(modal.text()).toContain('Add Connection')
    })

    it('should emit view-clue event when connection clue is clicked', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 10))

      const viewClueBtn = wrapper.find('button:contains("View Clue")')
      await viewClueBtn.trigger('click')

      expect(wrapper.emitted('view-clue')).toBeTruthy()
      expect(wrapper.emitted('view-clue')[0]).toEqual(['clue-2'])
    })
  })

  describe('Analysis Functionality', () => {
    it('should display analysis section', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 10))

      const analysisSection = wrapper.find('[aria-labelledby="analysis-title"]')
      expect(analysisSection.exists()).toBe(true)
      expect(analysisSection.text()).toContain('Analysis')
      expect(analysisSection.text()).toContain('No analysis available')
    })

    it('should request analysis when analyze button is clicked', async () => {
      const mockAnalysis = {
        clue_details: mockClue,
        related_clues: [],
        related_suspects: [],
        analysis_context: 'Test analysis',
        focus_areas: ['fingerprints', 'blood'],
        timestamp: '2024-01-01T13:00:00Z'
      }
      
      mockClueStore.analyzeClue.mockResolvedValue(mockAnalysis)
      
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 10))

      const analyzeBtn = wrapper.find('button:contains("Analyze Clue")')
      await analyzeBtn.trigger('click')

      expect(mockClueStore.analyzeClue).toHaveBeenCalledWith('clue-1')
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA labels and roles', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 10))

      // Check main container has role
      expect(wrapper.find('[role="main"]').exists()).toBe(true)

      // Check section headings are properly labeled
      expect(wrapper.find('[aria-labelledby="discovery-title"]').exists()).toBe(true)
      expect(wrapper.find('[aria-labelledby="connections-title"]').exists()).toBe(true)
      expect(wrapper.find('[aria-labelledby="analysis-title"]').exists()).toBe(true)

      // Check form elements have proper labels
      expect(wrapper.find('label[for="relevance-slider"]').exists()).toBe(true)
      expect(wrapper.find('label[for="red-herring-checkbox"]').exists()).toBe(true)
      expect(wrapper.find('label[for="notes-textarea"]').exists()).toBe(true)
    })

    it('should have proper focus management', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 10))

      // Check that interactive elements have proper focus styles
      const relevanceSlider = wrapper.find('#relevance-slider')
      const redHerringCheckbox = wrapper.find('#red-herring-checkbox')
      const notesTextarea = wrapper.find('#notes-textarea')

      expect(relevanceSlider.classes()).toContain('w-32')
      expect(redHerringCheckbox.exists()).toBe(true)
      expect(notesTextarea.classes()).toContain('focus:ring-2')
    })
  })

  describe('Responsive Design', () => {
    it('should have responsive grid classes', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 10))

      const discoveryGrid = wrapper.find('.grid.grid-cols-1.md\\:grid-cols-2')
      expect(discoveryGrid.exists()).toBe(true)

      const relevanceSection = wrapper.find('.flex.flex-col.sm\\:flex-row')
      expect(relevanceSection.exists()).toBe(true)
    })
  })

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      mockClueStore.getClueDetails.mockRejectedValue(new Error('API Error'))
      
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 10))

      expect(consoleSpy).toHaveBeenCalledWith('Error loading clue:', expect.any(Error))
      
      consoleSpy.mockRestore()
    })
  })
}) 