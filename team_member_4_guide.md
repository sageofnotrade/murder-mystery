# Team Member 4 - Milestone 2 Task Guide

## Your Tasks Overview

| Task ID | Title | Estimate | Dependencies |
|---------|-------|----------|-------------|
| FE-006 | Implement basic detective board UI | 10h | FE-003 |
| AI-010 | Create mystery template parser and populator | 6h | AI-001 |
| **Total** | | **16h** | |

## Task Details and Implementation Guide

### FE-006: Implement basic detective board UI

#### Description
Create the visual detective board interface that allows users to organize clues, suspects, and evidence in a visual, interactive format. This board will serve as the visual investigation tool complementing the narrative interface.

#### Implementation Steps

1. **Review existing UI components (FE-003)**
   - Examine the authentication UI to maintain design consistency
   - Note the styling patterns and component structure

2. **Design the detective board layout**
   - Create a wireframe for the board layout
   - Plan for different element types (suspects, clues, locations, etc.)
   - Consider responsive design for different screen sizes

3. **Set up required libraries**
   ```bash
   # Install Vue Draggable
   npm install vuedraggable
   
   # Install D3.js for connections
   npm install d3
   ```

4. **Implement Vue components**
   ```bash
   # Create the main board component
   touch frontend/components/board/DetectiveBoard.vue
   
   # Create board element components
   touch frontend/components/board/BoardElement.vue
   touch frontend/components/board/SuspectElement.vue
   touch frontend/components/board/ClueElement.vue
   touch frontend/components/board/LocationElement.vue
   touch frontend/components/board/NoteElement.vue
   
   # Create connection component
   touch frontend/components/board/ElementConnection.vue
   ```

5. **Implement the board page**
   ```bash
   # Create the board page
   touch frontend/pages/mystery/board.vue
   ```

6. **Create Pinia store for board state**
   ```bash
   # Create store for board data
   touch frontend/stores/boardStore.js
   ```

7. **Implement draggable functionality**
   - Add drag-and-drop capabilities for board elements
   - Implement position saving and loading

8. **Create connection visualization**
   - Implement SVG lines between connected elements
   - Add functionality to create and delete connections

9. **Create API service for board interactions**
   ```bash
   # Create API service
   touch frontend/services/boardService.js
   ```

10. **Implement board controls**
    - Add zoom and pan functionality
    - Create toolbar for adding new elements
    - Add search and filter capabilities

#### Example Board Component Structure

```vue
<!-- Example DetectiveBoard.vue structure -->
<template>
  <div class="detective-board-container" ref="boardContainer">
    <!-- Board controls -->
    <div class="board-controls">
      <button @click="zoomIn">Zoom In</button>
      <button @click="zoomOut">Zoom Out</button>
      <button @click="resetView">Reset View</button>
      <div class="element-tools">
        <button @click="addElement('suspect')">Add Suspect</button>
        <button @click="addElement('clue')">Add Clue</button>
        <button @click="addElement('location')">Add Location</button>
        <button @click="addElement('note')">Add Note</button>
      </div>
    </div>
    
    <!-- The actual board -->
    <div 
      class="detective-board" 
      ref="board"
      @mousedown="startPan"
      @mousemove="pan"
      @mouseup="endPan"
      @mouseleave="endPan"
      :style="boardStyle"
    >
      <!-- SVG layer for connections -->
      <svg class="connections-layer" ref="connectionsLayer">
        <ElementConnection 
          v-for="connection in connections"
          :key="connection.id"
          :connection="connection"
          :elements="elements"
          @delete="deleteConnection"
        />
      </svg>
      
      <!-- Elements layer -->
      <draggable 
        v-model="elements" 
        item-key="id"
        :animation="200"
        @end="saveElementPositions"
        class="elements-layer"
      >
        <template #item="{element}">
          <component 
            :is="getElementComponent(element.type)"
            :element="element"
            @update="updateElement"
            @delete="deleteElement"
            @connect="startConnection"
            @select="selectElement"
          />
        </template>
      </draggable>
      
      <!-- Connection creation overlay (shown when creating connections) -->
      <div v-if="isConnecting" class="connection-overlay">
        <p>Select another element to connect</p>
        <button @click="cancelConnection">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useBoardStore } from '@/stores/boardStore';
import draggable from 'vuedraggable';
import ElementConnection from './ElementConnection.vue';
import SuspectElement from './SuspectElement.vue';
import ClueElement from './ClueElement.vue';
import LocationElement from './LocationElement.vue';
import NoteElement from './NoteElement.vue';

// Store
const boardStore = useBoardStore();

// Refs
const board = ref(null);
const boardContainer = ref(null);
const connectionsLayer = ref(null);

// State
const zoom = ref(1);
const panOffset = ref({ x: 0, y: 0 });
const isPanning = ref(false);
const panStart = ref({ x: 0, y: 0 });
const isConnecting = ref(false);
const connectionSource = ref(null);

// Computed
const elements = computed(() => boardStore.elements);
const connections = computed(() => boardStore.connections);
const boardStyle = computed(() => ({
  transform: `scale(${zoom.value}) translate(${panOffset.value.x}px, ${panOffset.value.y}px)`,
}));

// Methods
const getElementComponent = (type) => {
  switch (type) {
    case 'suspect': return SuspectElement;
    case 'clue': return ClueElement;
    case 'location': return LocationElement;
    case 'note': return NoteElement;
    default: return BoardElement;
  }
};

const zoomIn = () => {
  zoom.value = Math.min(zoom.value + 0.1, 2);
};

const zoomOut = () => {
  zoom.value = Math.max(zoom.value - 0.1, 0.5);
};

const resetView = () => {
  zoom.value = 1;
  panOffset.value = { x: 0, y: 0 };
};

const startPan = (event) => {
  // Only start panning if not interacting with an element
  if (event.target === board.value || event.target === connectionsLayer.value) {
    isPanning.value = true;
    panStart.value = { x: event.clientX, y: event.clientY };
  }
};

const pan = (event) => {
  if (isPanning.value) {
    const dx = event.clientX - panStart.value.x;
    const dy = event.clientY - panStart.value.y;
    panOffset.value = {
      x: panOffset.value.x + dx / zoom.value,
      y: panOffset.value.y + dy / zoom.value,
    };
    panStart.value = { x: event.clientX, y: event.clientY };
  }
};

const endPan = () => {
  isPanning.value = false;
};

const addElement = (type) => {
  boardStore.addElement({
    type,
    position: {
      x: 100,
      y: 100,
    },
    // Other properties based on type
  });
};

const updateElement = (element) => {
  boardStore.updateElement(element);
};

const deleteElement = (elementId) => {
  boardStore.deleteElement(elementId);
};

const saveElementPositions = () => {
  boardStore.saveElementPositions();
};

const startConnection = (elementId) => {
  isConnecting.value = true;
  connectionSource.value = elementId;
};

const selectElement = (elementId) => {
  if (isConnecting.value && connectionSource.value !== elementId) {
    // Create connection between connectionSource and this element
    boardStore.addConnection({
      sourceId: connectionSource.value,
      targetId: elementId,
      type: 'standard',
    });
    isConnecting.value = false;
    connectionSource.value = null;
  }
};

const cancelConnection = () => {
  isConnecting.value = false;
  connectionSource.value = null;
};

const deleteConnection = (connectionId) => {
  boardStore.deleteConnection(connectionId);
};

// Lifecycle
onMounted(async () => {
  if (!boardStore.isInitialized) {
    await boardStore.initializeBoard();
  }
});
</script>
```

#### Resources
- [Vue.js Composition API](https://vuejs.org/guide/introduction.html)
- [Vue Draggable](https://github.com/SortableJS/vue.draggable.next)
- [D3.js Documentation](https://d3js.org/)
- [SVG in Vue.js](https://vuejs.org/guide/extras/rendering-mechanism.html#rendering-pipeline)
- [Pinia State Management](https://pinia.vuejs.org/core-concepts/)

---

### AI-010: Create mystery template parser and populator

#### Description
Develop a system that can parse mystery templates and populate them with dynamic content based on player profiles and preferences. This will transform the static template structure into a personalized mystery ready for gameplay.

#### Implementation Steps

1. **Review PydanticAI setup (AI-001)**
   - Understand the PydanticAI framework integration
   - Note the patterns used for agent implementation

2. **Design the template parser architecture**
   - Plan the parsing and population workflow
   - Define interfaces between components
   - Consider error handling and validation

3. **Create Pydantic models for templates**
   ```bash
   # Create models file
   touch backend/agents/models/template_models.py
   ```

4. **Implement template parser class**
   ```bash
   # Create parser class
   touch backend/agents/template_parser.py
   ```

5. **Create template populator with PydanticAI**
   ```bash
   # Create populator class
   touch backend/agents/template_populator.py
   ```

6. **Implement player profile integration**
   - Add methods to analyze player profiles
   - Create logic to match profile traits to template elements

7. **Create dynamic content generators**
   - Implement functions to generate names, descriptions, etc.
   - Add methods to create coherent narrative elements

8. **Add validation and consistency checks**
   - Ensure populated templates maintain logical consistency
   - Validate all required fields are properly populated

9. **Implement caching for performance**
   - Cache frequently used template elements
   - Store partially populated templates

10. **Write unit tests**
    ```bash
    # Create test file
    touch backend/tests/test_template_parser.py
    ```

#### Example Template Parser Implementation

```python
# Example template_parser.py
from typing import Dict, Any, List, Optional
from pydantic import ValidationError
from backend.agents.models.template_models import MysteryTemplate, PopulatedMysteryTemplate
from backend.services.supabase_service import SupabaseService

class TemplateParser:
    def __init__(self, supabase_service: Optional[SupabaseService] = None):
        self.supabase_service = supabase_service or SupabaseService()
    
    async def get_template(self, template_id: str) -> MysteryTemplate:
        """Retrieve a template from the database by ID."""
        template_data = await self.supabase_service.get_template(template_id)
        if not template_data:
            raise ValueError(f"Template with ID {template_id} not found")
        
        try:
            return MysteryTemplate.model_validate(template_data)
        except ValidationError as e:
            raise ValueError(f"Invalid template data: {str(e)}")
    
    def validate_template(self, template: MysteryTemplate) -> List[str]:
        """Validate a template for completeness and consistency."""
        errors = []
        
        # Check for required elements
        if not template.suspects:
            errors.append("Template must have at least one suspect")
        
        if not template.clues:
            errors.append("Template must have at least one clue")
        
        # Check for logical consistency
        guilty_suspects = [s for s in template.suspects if s.guilty]
        if not guilty_suspects:
            errors.append("Template must have at least one guilty suspect")
        
        # Check for clue connections
        for clue in template.clues:
            if clue.related_suspects and not any(
                suspect.id in clue.related_suspects for suspect in template.suspects
            ):
                errors.append(f"Clue {clue.id} references non-existent suspects")
        
        return errors
    
    def extract_template_variables(self, template: MysteryTemplate) -> Dict[str, Any]:
        """Extract all variables that need to be populated in the template."""
        variables = {}
        
        # Extract variables from template text fields
        for field_name, field_value in template.model_dump().items():
            if isinstance(field_value, str) and "{{" in field_value and "}}" in field_value:
                # Extract variables like {{variable_name}}
                import re
                matches = re.findall(r"{{(.*?)}}", field_value)
                for match in matches:
                    variables[match.strip()] = None
        
        # Extract variables from nested objects
        for suspect in template.suspects:
            for field_name, field_value in suspect.model_dump().items():
                if isinstance(field_value, str) and "{{" in field_value and "}}" in field_value:
                    import re
                    matches = re.findall(r"{{(.*?)}}", field_value)
                    for match in matches:
                        variables[match.strip()] = None
        
        # Do the same for clues, locations, etc.
        
        return variables
```

#### Example Template Populator Implementation

```python
# Example template_populator.py
from typing import Dict, Any, Optional
from pydanticai import OpenAIModel, PydanticAIModel
from backend.agents.models.template_models import MysteryTemplate, PopulatedMysteryTemplate
from backend.agents.models.player_models import PlayerProfile
from backend.agents.template_parser import TemplateParser

class TemplatePopulator:
    def __init__(self, model_router=None):
        # Use the model router from AI-001 setup
        self.model_router = model_router
        self.parser = TemplateParser()
    
    async def populate_template(
        self, 
        template: MysteryTemplate, 
        player_profile: PlayerProfile
    ) -> PopulatedMysteryTemplate:
        """Populate a template with content based on player profile."""
        # Extract variables that need to be populated
        variables = self.parser.extract_template_variables(template)
        
        # Generate values for variables based on player profile
        populated_variables = await self._generate_variable_values(variables, template, player_profile)
        
        # Replace variables in the template
        populated_template = self._replace_template_variables(template, populated_variables)
        
        # Validate the populated template
        errors = self.parser.validate_template(populated_template)
        if errors:
            raise ValueError(f"Populated template validation failed: {', '.join(errors)}")
        
        return populated_template
    
    async def _generate_variable_values(
        self, 
        variables: Dict[str, Any],
        template: MysteryTemplate,
        player_profile: PlayerProfile
    ) -> Dict[str, str]:
        """Generate values for template variables using PydanticAI."""
        # Define the PydanticAI model for variable generation
        class VariableGenerator(PydanticAIModel):
            variable_name: str
            template_context: str
            player_traits: Dict[str, float]
            player_preferences: Dict[str, Any]
            
            def _llm_generate_value(self) -> str:
                """Generate a value for the variable based on context and player profile."""
                # This will be implemented by PydanticAI
                pass
        
        # Create a model instance using the appropriate LLM
        model = self.model_router.get_model_for_task("creative")
        
        # Generate values for each variable
        populated_variables = {}
        for var_name in variables:
            generator = VariableGenerator(
                variable_name=var_name,
                template_context=self._get_context_for_variable(var_name, template),
                player_traits=player_profile.psychological_traits,
                player_preferences=player_profile.preferences
            )
            
            value = await generator._llm_generate_value(model=model)
            populated_variables[var_name] = value
        
        return populated_variables
    
    def _get_context_for_variable(self, variable_name: str, template: MysteryTemplate) -> str:
        """Get relevant context from the template for a specific variable."""
        # Implementation to extract context based on variable name
        # This helps the LLM understand what kind of value to generate
        context = f"Template title: {template.title}\n"
        context += f"Setting: {template.setting}, Time period: {template.time_period}\n"
        
        # Add specific context based on variable name
        if "suspect" in variable_name:
            context += "This variable is related to a suspect character.\n"
        elif "victim" in variable_name:
            context += "This variable is related to the victim character.\n"
        elif "motive" in variable_name:
            context += "This variable is related to a character's motive for murder.\n"
        
        return context
    
    def _replace_template_variables(
        self, 
        template: MysteryTemplate, 
        variables: Dict[str, str]
    ) -> PopulatedMysteryTemplate:
        """Replace variables in the template with generated values."""
        # Create a copy of the template
        template_dict = template.model_dump()
        
        # Helper function to replace variables in a string
        def replace_vars(text):
            if not isinstance(text, str):
                return text
            
            for var_name, value in variables.items():
                placeholder = f"{{{{{var_name}}}}}"
                text = text.replace(placeholder, value)
            return text
        
        # Replace variables in all string fields
        for field_name, field_value in template_dict.items():
            if isinstance(field_value, str):
                template_dict[field_name] = replace_vars(field_value)
            elif isinstance(field_value, list):
                # Handle lists (like suspects, clues, etc.)
                for i, item in enumerate(field_value):
                    if isinstance(item, dict):
                        for k, v in item.items():
                            if isinstance(v, str):
                                field_value[i][k] = replace_vars(v)
        
        # Create a populated template
        return PopulatedMysteryTemplate.model_validate(template_dict)
```

#### Resources
- [PydanticAI Documentation](https://github.com/pydantic/pydanticai)
- [Pydantic Documentation](https://docs.pydantic.dev/latest/)
- [Python String Templating](https://docs.python.org/3/library/string.html#template-strings)
- [Python Regular Expressions](https://docs.python.org/3/library/re.html)

## Testing Your Work

### FE-006 Testing
1. Run the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```
2. Navigate to the detective board page
3. Test dragging and positioning elements
4. Test creating and deleting connections
5. Test zoom and pan functionality
6. Verify mobile responsiveness using browser dev tools

### AI-010 Testing
1. Create a test script:
   ```bash
   # Create test script
   touch backend/scripts/test_template_parser.py
   ```
2. Run the test script:
   ```bash
   cd backend
   python scripts/test_template_parser.py
   ```
3. Run unit tests:
   ```bash
   cd backend
   pytest tests/test_template_parser.py
   ```

## Deliverables

### FE-006 Deliverables
- Complete detective board components
- Draggable element functionality
- Connection visualization
- Board controls (zoom, pan, add elements)
- Pinia store for board state

### AI-010 Deliverables
- Template parser class
- Template populator with PydanticAI integration
- Player profile integration
- Dynamic content generation
- Unit tests for parser and populator

## Communication

If you encounter any blockers or have questions:
- Post in the #milestone-2 Slack channel
- Tag the project lead for urgent issues
- Document any design decisions or assumptions in your PR description

Good luck with your tasks! Remember to commit your work regularly and create pull requests for review.
