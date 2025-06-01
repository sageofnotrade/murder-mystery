<template>
  <div class="detective-board-container">
    <!-- Board controls -->
    <div class="board-controls">
      <button @click="zoomIn">Zoom In</button>
      <button @click="zoomOut">Zoom Out</button>
      <button @click="resetView">Reset View</button>
      <button @click="undo" :disabled="!canUndo">Undo</button>
      <button @click="redo" :disabled="!canRedo">Redo</button>
      <button @click="saveBoard" :disabled="isSaving">Save</button>
      <button @click="loadBoard" :disabled="isLoading">Load</button>
      <button @click="resetBoardConfirm">Reset</button>
      <div class="element-tools">
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
    <div v-if="isConnecting" class="connection-overlay">
      <p>
        Select two elements to connect as <b>{{ connectionTypeLabel }}</b>.
        <button @click="cancelConnection">Cancel</button>
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
        />
      </div>
    </div>
    <div v-if="selectedElement" class="element-sidebar">
      <h3>Edit Element</h3>
      <label>Name:<input v-model="editElement.name" /></label>
      <label>Type:
        <select v-model="editElement.type">
          <option value="suspect">Suspect</option>
          <option value="clue">Clue</option>
          <option value="location">Location</option>
          <option value="note">Note</option>
        </select>
      </label>
      <label>Description:<textarea v-model="editElement.description" rows="2" /></label>
      <label>Notes:<textarea v-model="editElement.notes" rows="3" /></label>
      <div class="sidebar-actions">
        <button @click="saveElementEdit">Save</button>
        <button @click="closeSidebar">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
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

onMounted(async () => {
  if (!boardStore.isInitialized) boardStore.initializeBoard();
  await nextTick();
  if (boardRef.value) {
    boardWidth.value = boardRef.value.offsetWidth;
    boardHeight.value = boardRef.value.offsetHeight;
  }
});
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
  gap: 1rem;
  margin-bottom: 1rem;
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
  background: #eef;
  padding: 0.5em 1em;
  border-radius: 6px;
  margin-bottom: 0.5em;
  font-size: 1em;
}
.detective-board {
  flex: 1;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 8px;
  position: relative;
  overflow: hidden;
  user-select: none;
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
  border: 1px solid #bbb;
  border-radius: 8px;
  box-shadow: 0 4px 24px #0002;
  padding: 1.5em 1.5em 1em 1.5em;
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 0.7em;
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
</style> 