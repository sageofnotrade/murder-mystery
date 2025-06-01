// boardService.js - handles API calls for detective board

export const boardService = {
  async fetchBoardState() {
    // Placeholder: fetch board state from backend
    try {
      const res = await fetch('/api/board');
      if (!res.ok) throw new Error('Failed to fetch board state');
      return await res.json();
    } catch (e) {
      return { elements: [], connections: [] };
    }
  },
  async saveBoardState(state) {
    // Placeholder: save board state to backend
    try {
      const res = await fetch('/api/board', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(state),
      });
      if (!res.ok) throw new Error('Failed to save board state');
      return await res.json();
    } catch (e) {
      return { success: false };
    }
  },
}; 