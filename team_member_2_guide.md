# Team Member 2 - Milestone 2 Task Guide

## Your Tasks Overview

| Task ID | Title | Estimate | Dependencies |
|---------|-------|----------|-------------|
| FE-005 | Develop narrative interface component | 8h | FE-003 |
| TEST-001 | Set up frontend testing framework | 3h | FE-001 |
| **Total** | | **11h** | |

## Task Details and Implementation Guide

### FE-005: Develop narrative interface component

#### Description
Create the narrative interface component that will display the story text, player choices, and allow for user interaction with the murder mystery narrative. This is a core component of the user experience, serving as the main storytelling interface.

#### Implementation Steps

1. **Review existing UI components (FE-003)**
   - Examine the authentication UI to maintain design consistency
   - Note the styling patterns and component structure

2. **Design the narrative interface layout**
   - Create a wireframe for the narrative display area
   - Plan for story text, user choices, and input field
   - Consider responsive design for different screen sizes

3. **Implement Vue components**
   ```bash
   # Create the main narrative component
   touch frontend/components/narrative/NarrativeInterface.vue
   # Create supporting components
   touch frontend/components/narrative/StoryText.vue
   touch frontend/components/narrative/ActionChoices.vue
   touch frontend/components/narrative/UserInput.vue
   touch frontend/components/narrative/NarrativeHistory.vue
   ```

4. **Implement the narrative page**
   ```bash
   # Create the narrative page
   touch frontend/pages/mystery/narrative.vue
   ```

5. **Create Pinia store for narrative state**
   ```bash
   # Create store for narrative data
   touch frontend/stores/narrativeStore.js
   ```

6. **Implement text animation and styling**
   - Add typewriter effect for story text (optional)
   - Style text with appropriate typography
   - Add visual cues for different narrative elements (dialogue, description, etc.)

7. **Create API service for narrative interactions**
   ```bash
   # Create API service
   touch frontend/services/narrativeService.js
   ```

8. **Implement user input handling**
   - Create form for free-text input
   - Add validation and submission logic
   - Handle API responses and update the narrative

9. **Add loading and transition states**
   - Show loading indicators during API calls
   - Add smooth transitions between narrative segments

10. **Implement narrative history**
    - Create scrollable history of past narrative segments
    - Allow users to review previous choices and outcomes

#### Example Narrative Component Structure

```vue
<!-- Example NarrativeInterface.vue structure -->
<template>
  <div class="narrative-container">
    <!-- Story display area -->
    <StoryText 
      :text="currentNarrativeSegment.text" 
      :character="currentNarrativeSegment.character"
      :animate="animateText" 
    />
    
    <!-- Action choices (if available) -->
    <ActionChoices 
      v-if="currentNarrativeSegment.choices.length > 0"
      :choices="currentNarrativeSegment.choices"
      @select-choice="handleChoiceSelection"
    />
    
    <!-- User input area -->
    <UserInput 
      v-if="allowUserInput"
      :placeholder="inputPlaceholder"
      @submit-input="handleUserInput"
      :isLoading="isSubmitting"
    />
    
    <!-- Narrative history -->
    <NarrativeHistory 
      :history="narrativeHistory"
      @view-history-item="scrollToHistoryItem"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useNarrativeStore } from '@/stores/narrativeStore';
import StoryText from './StoryText.vue';
import ActionChoices from './ActionChoices.vue';
import UserInput from './UserInput.vue';
import NarrativeHistory from './NarrativeHistory.vue';

// Store
const narrativeStore = useNarrativeStore();

// State
const isSubmitting = ref(false);
const animateText = ref(true);
const inputPlaceholder = ref('What would you like to do?');

// Computed
const currentNarrativeSegment = computed(() => narrativeStore.currentSegment);
const narrativeHistory = computed(() => narrativeStore.history);
const allowUserInput = computed(() => currentNarrativeSegment.value.allowInput);

// Methods
const handleChoiceSelection = async (choiceId) => {
  isSubmitting.value = true;
  await narrativeStore.submitChoice(choiceId);
  isSubmitting.value = false;
};

const handleUserInput = async (input) => {
  isSubmitting.value = true;
  await narrativeStore.submitUserInput(input);
  isSubmitting.value = false;
};

const scrollToHistoryItem = (index) => {
  // Implementation to scroll to a specific history item
};

// Lifecycle
onMounted(async () => {
  if (!narrativeStore.isInitialized) {
    await narrativeStore.initializeNarrative();
  }
});
</script>
```

#### Resources
- [Vue.js Composition API](https://vuejs.org/guide/introduction.html)
- [Tailwind CSS Typography](https://tailwindcss.com/docs/typography-plugin)
- [Pinia State Management](https://pinia.vuejs.org/core-concepts/)
- [GSAP Animation Library](https://greensock.com/gsap/)
- [Nuxt.js Pages](https://nuxt.com/docs/guide/directory-structure/pages)

---

### TEST-001: Set up frontend testing framework

#### Description
Set up a comprehensive testing framework for the frontend components, including unit tests, component tests, and end-to-end tests. This will ensure code quality and prevent regressions as the application grows.

#### Implementation Steps

1. **Review existing frontend project (FE-001)**
   - Understand the Vue.js/Nuxt.js project structure
   - Note any existing test configurations

2. **Install testing dependencies**
   ```bash
   # Install Vitest for unit and component testing
   npm install --save-dev vitest @vue/test-utils happy-dom

   # Install Cypress for end-to-end testing
   npm install --save-dev cypress
   ```

3. **Configure Vitest**
   ```bash
   # Create Vitest configuration
   touch vitest.config.js
   ```

4. **Configure Cypress**
   ```bash
   # Initialize Cypress
   npx cypress open
   ```

5. **Set up test directory structure**
   ```bash
   # Create test directories
   mkdir -p frontend/tests/unit
   mkdir -p frontend/tests/components
   mkdir -p frontend/cypress/e2e
   ```

6. **Create test utilities**
   ```bash
   # Create test utilities
   touch frontend/tests/utils/test-utils.js
   ```

7. **Set up mock services**
   ```bash
   # Create mock services for API calls
   touch frontend/tests/mocks/api-mocks.js
   ```

8. **Create example tests**
   ```bash
   # Create example unit test
   touch frontend/tests/unit/example.spec.js
   
   # Create example component test
   touch frontend/tests/components/example.spec.js
   
   # Create example E2E test
   touch frontend/cypress/e2e/example.cy.js
   ```

9. **Configure CI integration**
   ```bash
   # Create GitHub Actions workflow for tests
   mkdir -p .github/workflows
   touch .github/workflows/frontend-tests.yml
   ```

10. **Add npm scripts for testing**
    - Update package.json with test scripts

#### Example Vitest Configuration

```javascript
// vitest.config.js
import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'happy-dom',
    coverage: {
      reporter: ['text', 'json', 'html'],
    },
    include: ['./tests/**/*.spec.js'],
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
});
```

#### Example Component Test

```javascript
// tests/components/StoryText.spec.js
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import StoryText from '@/components/narrative/StoryText.vue';

describe('StoryText.vue', () => {
  it('renders story text correctly', () => {
    const text = 'This is a test narrative text.';
    const wrapper = mount(StoryText, {
      props: {
        text,
        character: null,
        animate: false,
      },
    });
    
    expect(wrapper.text()).toContain(text);
  });
  
  it('applies character styling when character is provided', () => {
    const text = 'Hello, detective.';
    const character = {
      name: 'Suspect',
      color: 'text-red-500',
    };
    
    const wrapper = mount(StoryText, {
      props: {
        text,
        character,
        animate: false,
      },
    });
    
    expect(wrapper.find('.character-name').text()).toContain(character.name);
    expect(wrapper.find('.character-dialogue').classes()).toContain(character.color);
  });
});
```

#### Example E2E Test

```javascript
// cypress/e2e/narrative.cy.js
describe('Narrative Interface', () => {
  beforeEach(() => {
    // Set up any authentication or state needed
    cy.login();
    cy.visit('/mystery/narrative');
  });
  
  it('displays the narrative text', () => {
    cy.get('.story-text').should('be.visible');
  });
  
  it('allows selecting a choice', () => {
    cy.get('.action-choice').first().click();
    cy.get('.story-text').should('contain', 'You decided to');
  });
  
  it('allows entering custom input', () => {
    const userInput = 'Examine the bookshelf';
    cy.get('.user-input input').type(userInput);
    cy.get('.user-input button').click();
    cy.get('.story-text').should('contain', 'You examine the bookshelf');
  });
});
```

#### Resources
- [Vitest Documentation](https://vitest.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Cypress Documentation](https://docs.cypress.io/)
- [Testing Vue Applications](https://vuejs.org/guide/scaling-up/testing.html)
- [GitHub Actions for CI/CD](https://docs.github.com/en/actions)

## Testing Your Work

### FE-005 Testing
1. Run the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```
2. Navigate to the narrative interface page
3. Test text display, animations, and styling
4. Test user input and choice selection
5. Verify mobile responsiveness using browser dev tools

### TEST-001 Testing
1. Run unit and component tests:
   ```bash
   npm run test:unit
   ```
2. Run end-to-end tests:
   ```bash
   npm run test:e2e
   ```
3. Check test coverage:
   ```bash
   npm run test:coverage
   ```

## Deliverables

### FE-005 Deliverables
- Complete narrative interface components
- Pinia store for narrative state
- API service for narrative interactions
- Responsive design for all device sizes

### TEST-001 Deliverables
- Configured testing frameworks (Vitest and Cypress)
- Test directory structure and utilities
- Example tests for each test type
- CI integration for automated testing
- Updated package.json with test scripts

## Communication

If you encounter any blockers or have questions:
- Post in the #milestone-2 Slack channel
- Tag the project lead for urgent issues
- Document any design decisions or assumptions in your PR description

Good luck with your tasks! Remember to commit your work regularly and create pull requests for review.
