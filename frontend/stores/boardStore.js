import { defineStore } from 'pinia';
import { boardService } from '../services/boardService';

function cloneState(state) {
  return {
    elements: JSON.parse(JSON.stringify(state.elements)),
    connections: JSON.parse(JSON.stringify(state.connections)),
  };
}

export const useBoardStore = defineStore('board', {
  state: () => ({
    elements: [], // Array of board elements
    connections: [], // Array of connections between elements
    isInitialized: false,
    history: [],
    future: [],
  }),
  actions: {
    pushHistory() {
      this.history.push(cloneState(this));
      if (this.history.length > 50) this.history.shift(); // limit history size
      this.future = [];
    },
    undo() {
      if (this.history.length === 0) return;
      this.future.push(cloneState(this));
      const prev = this.history.pop();
      this.elements = [...prev.elements];
      this.connections = [...prev.connections];
    },
    redo() {
      if (this.future.length === 0) return;
      this.history.push(cloneState(this));
      const next = this.future.pop();
      this.elements = [...next.elements];
      this.connections = [...next.connections];
    },
    initializeBoard() {
      this.isInitialized = true;
      // Load initial board state if needed
      this.pushHistory();
    },
    addElement(element) {
      this.pushHistory();
      this.elements.push({ ...element }); // 🔥 keep the ID from the caller

    },
    updateElement(updated) {
      this.pushHistory();
      const idx = this.elements.findIndex(e => e.id === updated.id);
      if (idx !== -1) this.elements[idx] = { ...updated };
    },
    deleteElement(id) {
      this.pushHistory();
      this.elements = [...this.elements.filter(e => e.id !== id)];
      this.connections = [...this.connections.filter(c => c.sourceId !== id && c.targetId !== id)];
    },
    addConnection(connection) {
      this.pushHistory();
      this.connections.push({ ...connection, id: Date.now() });
    },
    deleteConnection(id) {
      this.pushHistory();
      this.connections = this.connections.filter(c => c.id !== id);
    },
    updateConnection(updated) {
      this.pushHistory();
      const idx = this.connections.findIndex(c => c.id === updated.id);
      if (idx !== -1) this.connections[idx] = { ...updated };
    },
    saveElementPositions() {
      // Placeholder for saving positions (e.g., to backend)
    },
    async loadBoard() {
      const data = await boardService.fetchBoardState();
      this.elements = [...(data.elements || [])];
      this.connections = [...(data.connections || [])];
      this.pushHistory();
    },
    async saveBoard() {
      await boardService.saveBoardState({ elements: this.elements, connections: this.connections });
    },
    resetBoard() {
      this.pushHistory();
      this.elements = [];
      this.connections = [];
    },
  },
}); 