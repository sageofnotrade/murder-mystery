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
