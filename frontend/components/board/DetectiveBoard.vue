<template>
  <div class="detective-board-container">
    <!-- Board controls -->
    <div class="board-controls">
  <div class="control-group">
    <button @click="zoomIn">Zoom In</button>
    <button @click="zoomOut">Zoom Out</button>
    <button @click="resetView">Reset View</button>
    <button @click="undo" :disabled="!canUndo">Undo</button>
    <button @click="redo" :disabled="!canRedo">Redo</button>
    <button @click="saveBoard" :disabled="isSaving">Save</button>
    <button @click="loadBoard" :disabled="isLoading">Load</button>
    <button @click="resetBoardConfirm">Reset</button>
  </div>
  <div class="control-group">
    <button @click="addElement('suspect')">Add Suspect</button>
    <button @click="addElement('clue')">Add Clue</button>
    <button @click="addElement('location')">Add Location</button>
    <button @click="addElement('note')">Add Note</button>
    <button @click="startConnectionMode" :class="{ active: isConnecting }">Connect</button>
    <select v-model="selectedConnectionType" :disabled="!isConnecting" class="connection-type-select">
      <option v-for="type in connectionTypes" :key="type.value" :value="type.value">{{ type.label }}</option>
    </select>
  </div>
</div>
    <div v-if="isConnecting" class="connection-overlay" :style="{ borderLeft: '5px solid ' + connectionTypeColor }">
      <p>
        Click two elements to connect them as <strong>{{ connectionTypeLabel }}</strong>. 
        <span class="cancel-link" @click="cancelConnection">Cancel</span>
      </p>
    </div>
    <div v-if="isLoading" class="board-loading">Loading...</div>
    <!-- Board area with pan/zoom and absolutely positioned elements -->
    <div
      class="detective-board"
      ref="boardRef"
      @mousedown="onBoardMouseDown"
      @mousemove="onPan"
      @mouseup="endPan"
      @mouseleave="endPan"
    >
      <div
        class="board-content"
        :style="boardTransformStyle"
      >
        <!-- SVG connections layer -->
        <svg class="connections-layer" :width="boardWidth" :height="boardHeight">
          <ElementConnection
            v-for="connection in connections"
            :key="connection.id"
            :connection="connection"
            :elements="elements"
            :selected-element-id="selectedElementId"
            @edit-label="onEditConnectionLabel"
          />
          <!-- Delete button for each connection -->
          <g v-for="connection in connections" :key="'del-' + connection.id">
            <circle
              v-if="getConnectionMidpoint(connection)"
              :cx="getConnectionMidpoint(connection).x"
              :cy="getConnectionMidpoint(connection).y"
              r="12"
              fill="#fff"
              stroke="#d33"
              stroke-width="2"
              @click.stop="deleteConnection(connection.id)"
              style="cursor:pointer;"
            />
            <text
              v-if="getConnectionMidpoint(connection)"
              :x="getConnectionMidpoint(connection).x"
              :y="getConnectionMidpoint(connection).y + 4"
              text-anchor="middle"
              font-size="14"
              fill="#d33"
              style="pointer-events:none;"
            >×</text>
          </g>
          <!-- Temporary connection line while selecting -->
          <line
            v-if="isConnecting && connectionSource && tempMousePos"
            :x1="connectionSource.position.x + elementWidth/2"
            :y1="connectionSource.position.y + elementHeight/2"
            :x2="tempMousePos.x"
            :y2="tempMousePos.y"
            :stroke="connectionTypeColor"
            stroke-width="2"
            stroke-dasharray="6,4"
          />
        </svg>
        <!-- Board elements -->
        <component
           v-for="element in elements"
          :key="element.id"
          :is="getElementComponent(element.type)"
          :element="element"
          :style="getElementStyle(element)"
          @mousedown.stop="startDrag($event, element)"
          @click="onElementClick(element)"
          @delete="boardStore.deleteElement"
        />
      </div>
    </div>
    <div 
    v-if="selectedElement" 
    class="element-sidebar" 
    :class="`type-${selectedElement.type}`"
    ref="sidebarRef"
    :style="{ top: sidebarPosition.top + 'px', left: sidebarPosition.left + 'px' }"
    @mousedown.stop="startSidebarDrag"
  >

  <template v-if="selectedElement.type === 'suspect'">
    <SuspectProfile :suspect="selectedElement" />
  </template>
  <template v-else>
    <h3>Edit Element</h3>
    <label>Name:<input v-model="editElement.name" /></label>
   <label>Type:
       <input :value="capitalize(editElement.type)" disabled />
    </label>
    <label>Description:<textarea v-model="editElement.description" rows="2" /></label>
    <label>Notes:<textarea v-model="editElement.notes" rows="3" /></label>
    <div class="sidebar-actions">
      <button @click="saveElementEdit">Save</button>
      <button @click="closeSidebar">Close</button>
    </div>
  </template>
</div>
</div> 
</template>


<script setup>
import SuspectProfile from './SuspectProfile.vue';
import { ref, computed, onMounted, nextTick, reactive, watch } from 'vue';
import { useBoardStore } from '@/stores/boardStore';
import SuspectElement from './SuspectElement.vue';
import ClueElement from './ClueElement.vue';
import LocationElement from './LocationElement.vue';
import NoteElement from './NoteElement.vue';
import BoardElement from './BoardElement.vue';
import ElementConnection from './ElementConnection.vue';

const elementWidth = 120;
const elementHeight = 70;
const capitalize = (str) => str.charAt(0).toUpperCase() + str.slice(1);
const connectionTypes = [
  { value: 'thread', label: 'Thread', color: '#b33' },
  { value: 'logic', label: 'Logic', color: '#3366cc' },
  { value: 'alibi', label: 'Alibi', color: '#33a853' },
  { value: 'evidence', label: 'Evidence', color: '#fbbc05' },
];
const selectedConnectionType = ref('thread');
const connectionTypeLabel = computed(() => connectionTypes.find(t => t.value === selectedConnectionType.value)?.label || 'Thread');
const connectionTypeColor = computed(() => connectionTypes.find(t => t.value === selectedConnectionType.value)?.color || '#b33');

const selectedElementId = ref(null);

const zoom = ref(1);
const panOffset = ref({ x: 0, y: 0 });
const isPanning = ref(false);
const panStart = ref({ x: 0, y: 0 });

const isConnecting = ref(false);
const connectionSource = ref(null);
const tempMousePos = ref(null);

const zoomIn = () => { zoom.value = Math.min(zoom.value + 0.1, 2); };
const zoomOut = () => { zoom.value = Math.max(zoom.value - 0.1, 0.5); };
const resetView = () => {
  zoom.value = 1;
  panOffset.value = { x: 0, y: 0 };
};

const boardStore = useBoardStore();
const elements = computed(() => boardStore.elements);
const connections = computed(() => boardStore.connections);

const getElementComponent = (type) => {
  switch (type) {
    case 'suspect': return SuspectElement;
    case 'clue': return ClueElement;
    case 'location': return LocationElement;
    case 'note': return NoteElement;
    default: return BoardElement;
  }
};

const addElement = (type) => {
  if (!["suspect","clue","location","note"].includes(type)) return;
  boardStore.addElement({
    type,
    position: { x: 100, y: 100 },
    // Add more default properties as needed
  });
};

const boardRef = ref(null);
let dragging = null;
let dragOffset = { x: 0, y: 0 };

const startDrag = (event, element) => {
  dragging = element;
  dragOffset = {
    x: event.clientX - (element.position.x * zoom.value + panOffset.value.x),
    y: event.clientY - (element.position.y * zoom.value + panOffset.value.y),
  };
  window.addEventListener('mousemove', onDrag);
  window.addEventListener('mouseup', endDrag);
};

const onDrag = (event) => {
  if (!dragging) return;
  const boardRect = boardRef.value.getBoundingClientRect();
  // Adjust for pan and zoom
  const newX = (event.clientX - dragOffset.x - panOffset.value.x) / zoom.value;
  const newY = (event.clientY - dragOffset.y - panOffset.value.y) / zoom.value;
  dragging.position.x = Math.max(0, Math.min(newX, (boardRect.width - elementWidth) / zoom.value));
  dragging.position.y = Math.max(0, Math.min(newY, (boardRect.height - elementHeight) / zoom.value));
  boardStore.updateElement({ ...dragging });
};

const endDrag = () => {
  dragging = null;
  window.removeEventListener('mousemove', onDrag);
  window.removeEventListener('mouseup', endDrag);
  boardStore.saveElementPositions();
};

// Pan logic
const onBoardMouseDown = (event) => {
  // Deselect if clicking on empty board
  if (event.target === boardRef.value) {
    isPanning.value = true;
    panStart.value = { x: event.clientX, y: event.clientY };
    selectedElementId.value = null;
  }
};
const onPan = (event) => {
  if (isPanning.value) {
    const dx = event.clientX - panStart.value.x;
    const dy = event.clientY - panStart.value.y;
    panOffset.value = {
      x: panOffset.value.x + dx,
      y: panOffset.value.y + dy,
    };
    panStart.value = { x: event.clientX, y: event.clientY };
  }
  // For temp connection line
  if (isConnecting.value && connectionSource.value) {
    const boardRect = boardRef.value.getBoundingClientRect();
    tempMousePos.value = {
      x: (event.clientX - boardRect.left - panOffset.value.x) / zoom.value,
      y: (event.clientY - boardRect.top - panOffset.value.y) / zoom.value,
    };
  }
};
const endPan = () => {
  isPanning.value = false;
};

// Connection creation logic
const startConnectionMode = () => {
  isConnecting.value = true;
  connectionSource.value = null;
  tempMousePos.value = null;
};
const cancelConnection = () => {
  isConnecting.value = false;
  connectionSource.value = null;
  tempMousePos.value = null;
};
const onElementClick = (element) => {
  if (!isConnecting.value) {
    // Select/deselect element
    selectedElementId.value = selectedElementId.value === element.id ? null : element.id;
    return;
  }
  if (!connectionSource.value) {
    connectionSource.value = element;
  } else if (connectionSource.value.id !== element.id) {
    boardStore.addConnection({
      sourceId: connectionSource.value.id,
      targetId: element.id,
      type: selectedConnectionType.value,
    });
    isConnecting.value = false;
    connectionSource.value = null;
    tempMousePos.value = null;
  }
};
const deleteConnection = (id) => {
  boardStore.deleteConnection(id);
};

const getConnectionMidpoint = (connection) => {
  const source = elements.value.find(e => e.id === connection.sourceId);
  const target = elements.value.find(e => e.id === connection.targetId);
  if (!source || !target) return null;
  return {
    x: (source.position.x + target.position.x) / 2 + elementWidth / 2,
    y: (source.position.y + target.position.y) / 2 + elementHeight / 2,
  };
};

const getElementStyle = (element) => {
  return {
    position: 'absolute',
    left: element.position.x + 'px',
    top: element.position.y + 'px',
    cursor: isConnecting.value ? 'crosshair' : 'grab',
    zIndex: 10,
    border: selectedElementId.value === element.id ? '3px solid #33a' : isConnecting.value && connectionSource.value && connectionSource.value.id === element.id ? '2px solid #33a' : '',
    boxShadow: selectedElementId.value === element.id ? '0 0 8px #33a3' : '',
  };
};

const boardTransformStyle = computed(() => ({
  transform: `scale(${zoom.value}) translate(${panOffset.value.x / zoom.value}px, ${panOffset.value.y / zoom.value}px)`,
  width: '100%',
  height: '100%',
  position: 'relative',
}));

// Board size for SVG
const boardWidth = ref(1200);
const boardHeight = ref(800);

const onEditConnectionLabel = (connection) => {
  const newLabel = window.prompt('Edit connection label:', connection.label || '');
  if (newLabel !== null) {
    boardStore.updateConnection({ ...connection, label: newLabel });
  }
};

const canUndo = computed(() => boardStore.history.length > 0);
const canRedo = computed(() => boardStore.future.length > 0);
const undo = () => boardStore.undo();
const redo = () => boardStore.redo();

const selectedElement = computed(() => elements.value.find(e => e.id === selectedElementId.value));
const editElement = reactive({ name: '', type: '', description: '', notes: '', id: null });
watch(selectedElement, (el) => {
  if (el) {
    editElement.id = el.id;
    editElement.name = el.name || '';
    editElement.type = el.type || '';
    editElement.description = el.description || '';
    editElement.notes = el.notes || '';
  }
});
const saveElementEdit = () => {
  boardStore.updateElement({ ...selectedElement.value, ...editElement });
  closeSidebar();
};
const closeSidebar = () => {
  selectedElementId.value = null;
};

const isSaving = ref(false);
const isLoading = ref(false);
const saveBoard = async () => {
  isSaving.value = true;
  await boardStore.saveBoard();
  isSaving.value = false;
};
const loadBoard = async () => {
  isLoading.value = true;
  await boardStore.loadBoard();
  isLoading.value = false;
};
const resetBoardConfirm = () => {
  if (window.confirm('Are you sure you want to reset the board? This cannot be undone.')) {
    boardStore.resetBoard();
  }
};

const addTestSuspect = () => {
  boardStore.addElement({
    id: Date.now().toString(),
    type: 'suspect',
    name: 'John Doe',
    alibi: 'At the crime scene',
    motive: 'Revenge',
    traits: ['Aggressive', 'Secretive'],
    position: { x: 200, y: 150 },
    description: 'Test suspect inserted manually',
    notes: 'Watch closely',
  });
};

onMounted(async () => {
  if (!boardStore.isInitialized) boardStore.initializeBoard();
  await nextTick();
  if (boardRef.value) {
    boardWidth.value = boardRef.value.offsetWidth;
    boardHeight.value = boardRef.value.offsetHeight;
  }
});

const sidebarRef = ref(null);
let sidebarDragging = false;
let sidebarOffset = { x: 0, y: 0 };

const sidebarPosition = ref({ top: 100, left: 100 });

const startSidebarDrag = (event) => {
  if (!sidebarRef.value) return;

  sidebarDragging = true;
  const rect = sidebarRef.value.getBoundingClientRect();
  sidebarOffset = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top,
  };
  window.addEventListener('mousemove', onSidebarDrag);
  window.addEventListener('mouseup', endSidebarDrag);
};

const onSidebarDrag = (event) => {
  if (!sidebarDragging) return;
  sidebarPosition.value = {
    left: event.clientX - sidebarOffset.x,
    top: event.clientY - sidebarOffset.y,
  };
};

const endSidebarDrag = () => {
  sidebarDragging = false;
  window.removeEventListener('mousemove', onSidebarDrag);
  window.removeEventListener('mouseup', endSidebarDrag);
};
</script>

<style scoped>
.detective-board-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.board-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 1rem;
  background-color: #fceabb;
  border-bottom: 3px solid #d4aa00;
  z-index: 100;
  overflow-x: auto;
  max-width: 100vw;
  box-sizing: border-box;
}

.control-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: start;
}
.board-controls button,
.board-controls select {
  background-color: #fff5cc;
  color: #3b2f1c;
  border: 1px solid #caa35d;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  white-space: nowrap;
  font-weight: 600;
  font-family: 'Courier New', Courier, monospace;
  box-shadow: 2px 2px 5px #bfa263;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.board-controls button:hover,
.board-controls select:hover {
  background-color: #e0e0e0;
  color: #000;
}
.element-tools .active {
  background: #33a;
  color: #fff;
}
.connection-type-select {
  margin-left: 0.5em;
  padding: 0.2em 0.5em;
  border-radius: 4px;
  border: 1px solid #bbb;
  font-size: 1em;
}
.connection-overlay {
  background-color: #f3f8ff; /* soft blue */
  color: #222;
  padding: 0.7em 1.2em;
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.95rem;
  font-weight: 600;
  border-left: 5px solid #3366cc; /* thread color */
  border-radius: 6px;
  box-shadow: 1px 1px 5px #ccc;
  margin: 0.5rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.detective-board {
  flex: 1;
  background-color: #f7eec8;
  background-image: 
    repeating-linear-gradient(
      45deg,
      rgba(255, 244, 200, 0.4),
      rgba(255, 244, 200, 0.4) 10px,
      rgba(248, 232, 180, 0.4) 10px,
      rgba(248, 232, 180, 0.4) 20px
    ),
    radial-gradient(circle, rgba(200,160,100,0.07) 1px, transparent 1px);
  background-size: 20px 20px, 5px 5px;
  background-blend-mode: multiply;
  border: none;
  border-radius: 0;
}

.board-content {
  width: 100%;
  height: 100%;
  position: relative;
}
.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: auto;
  z-index: 1;
}
.element-sidebar {
  position: absolute;
  top: 2rem;
  right: 2rem;
  width: 300px;
  background: #fff;
  background-color: #fffbe7;
  border: 1px solid #ccc;
  color: #222;
  border: 1px solid #bbb;
  border-radius: 8px;
  color: #222;
  box-shadow: 0 4px 24px #0002;
  padding: 1.5em 1.5em 1em 1.5em;
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 0.7em;
}
.element-sidebar h3 {
  font-size: 1.1em;
  margin-bottom: 0.5em;
  color:rgb(6, 0, 0);
}
.element-sidebar label {
  display: flex;
  flex-direction: column;
  font-weight: 500;
  margin-bottom: 0.5em;
}
.element-sidebar input,
.element-sidebar select,
.element-sidebar textarea {
  margin-top: 0.2em;
  padding: 0.3em 0.5em;
  border-radius: 4px;
  border: 1px solid #bbb;
  font-size: 1em;
  color: #111;                 /* NEW */
  background-color: #fff;      /* Ensures readability */
}
.sidebar-actions {
  display: flex;
  gap: 1em;
  margin-top: 0.5em;
}
.board-loading {
  position: absolute;
  top: 2em;
  left: 50%;
  transform: translateX(-50%);
  background: #fffbe7;
  border: 1px solid #fbc02d;
  color: #bfa100;
  padding: 0.7em 2em;
  border-radius: 8px;
  font-size: 1.2em;
  z-index: 200;
  box-shadow: 0 2px 12px #0001;
}
.type-suspect {
  border-left: 5px solid #f88;
  background-color: #fff5f5;
}

.type-clue {
  border-left: 5px solid #88c;
  background-color: #f0f5ff;
}

.type-location {
  border-left: 5px solid #cc3;
  background-color: #ffffef;
}

.type-note {
  border-left: 5px solid #c8a2ff;
  background-color: #f9f0ff;
}
.cancel-link {
  color: #3366cc;
  text-decoration: underline;
  cursor: pointer;
  font-weight: 600;
  margin-left: 1em;
}
.cancel-link:hover {
  color: #003399;
}

@media (max-width: 600px) {
  .board-controls {
    flex-direction: column;
    align-items: stretch;
  }
}
</style> 