# Murþrą Frontend

This directory contains the Vue.js/Nuxt.js frontend for the Murþrą murder mystery application.

## Technology Stack

- Vue.js 3 with Composition API
- Nuxt.js 3
- Pinia for state management
- Tailwind CSS for styling
- GSAP for animations
- Vue Draggable and D3.js for the detective board

## Setup Instructions

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## Directory Structure

- `assets/`: Static assets like images and global CSS
- `components/`: Reusable Vue components
- `layouts/`: Page layouts
- `pages/`: Application pages and routes
- `plugins/`: Vue plugins
- `store/`: Pinia stores for state management
- `utils/`: Utility functions
- `public/`: Public static files

## Features

- Dual interface modes:
  - Narrative Mode (text-based interaction)
  - Detective Board (visual corkboard interface)
- User authentication via Supabase
- Psychological profiling questionnaire
- Interactive detective board with draggable elements
- Suspect profiles and clue management

## Detective Board UI

A new visual detective board interface is being implemented at `pages/mystery/board.vue` using modular components in `components/board/`. This board allows users to organize clues, suspects, and evidence visually.

### Dependencies
- [vuedraggable](https://github.com/SortableJS/vue.draggable.next): For drag-and-drop board elements
- [d3](https://d3js.org/): For visualizing connections between elements

To install dependencies:
```bash
npm install vuedraggable d3
```
