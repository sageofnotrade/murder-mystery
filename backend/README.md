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

## Error Handling and Logging

All backend routes and services now use a standardized error response format and logging:

- **Error Response Format:**  
  Every error response is returned as a JSON object with the following structure:
  ```json
  {
    "data": null,
    "error": "Error message here"
  }
  ```
  For successful responses, the format is:
  ```json
  {
    "data": <response_data>,
    "error": null
  }
  ```

- **Logging:**  
  All errors are logged using Python's `logging` module. Each route and service logs errors with a descriptive message, including the route name and error details.

- **Blueprint-Level Error Handlers:**  
  Where applicable, blueprint-level error handlers are used to catch unhandled exceptions and return a consistent error response.

- **Service Layer:**  
  The service layer (e.g., `BaseService`) provides common error handling and logging methods to ensure consistency across all services.
