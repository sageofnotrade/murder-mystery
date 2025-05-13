# Murþrą Backend

This directory contains the Flask backend for the Murþrą murder mystery application.

## Technology Stack

- Flask API server
- Supabase for authentication and database
- Redis for caching
- Archon MCP for AI agent orchestration
- Pydantic AI for LLM integration
- Mem0 for persistent memory and context enhancement

## Setup Instructions

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the development server:
   ```bash
   flask run
   ```

## Directory Structure

- `app.py`: Main Flask application
- `config.py`: Configuration settings
- `routes/`: API endpoints
- `models/`: Database models
- `services/`: Business logic
- `agents/`: AI agent implementations
- `utils/`: Utility functions
- `tests/`: Unit and integration tests

## API Endpoints

- `/api/auth`: Authentication endpoints
- `/api/users`: User management
- `/api/mysteries`: Mystery template management
- `/api/stories`: Story progression
- `/api/clues`: Clue and evidence management
- `/api/board`: Detective board state management
