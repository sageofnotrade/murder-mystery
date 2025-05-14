# Team Member 3 - Milestone 2 Task Guide

## Your Tasks Overview

| Task ID | Title | Estimate | Dependencies |
|---------|-------|----------|-------------|
| BE-005 | Develop story progression endpoints | 8h | BE-004 |
| DB-002 | Implement mystery template schema | 3h | SETUP-003 |
| **Total** | | **11h** | |

## Task Details and Implementation Guide

### DB-002: Implement mystery template schema

#### Description
Design and implement the database schema for mystery templates in Supabase. This schema will store the structured templates that define the framework for each murder mystery, including characters, locations, clues, and narrative elements.

#### Implementation Steps

1. **Review Supabase setup (SETUP-003)**
   - Familiarize yourself with the existing Supabase project
   - Understand the authentication and user schema

2. **Design the mystery template schema**
   - Plan the table structure for templates
   - Define relationships between templates and other entities
   - Consider versioning and template variations

3. **Create tables in Supabase**
   - Use the Supabase dashboard or SQL editor
   - Define primary keys, foreign keys, and indexes
   - Set up appropriate constraints

4. **Set up Row Level Security (RLS) policies**
   - Define who can create, read, update, and delete templates
   - Implement policies for different user roles

5. **Create database functions and triggers**
   - Add any necessary functions for template management
   - Set up triggers for audit logging or state changes

6. **Document the schema**
   - Create an ERD (Entity Relationship Diagram)
   - Document table structures and relationships
   - Add comments to tables and columns

#### Example Schema SQL

```sql
-- Create mystery templates table
CREATE TABLE mystery_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    setting TEXT NOT NULL,
    time_period TEXT NOT NULL,
    difficulty FLOAT NOT NULL DEFAULT 1.0,
    estimated_duration TEXT NOT NULL DEFAULT '1 hour',
    version TEXT NOT NULL DEFAULT '1.0.0',
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id)
);

-- Create victims table
CREATE TABLE template_victims (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID REFERENCES mystery_templates(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    background TEXT NOT NULL,
    cause_of_death TEXT NOT NULL,
    discovery_details TEXT NOT NULL
);

-- Create suspects table
CREATE TABLE template_suspects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID REFERENCES mystery_templates(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    background TEXT NOT NULL,
    motive TEXT NOT NULL,
    alibi TEXT NOT NULL,
    is_guilty BOOLEAN NOT NULL DEFAULT FALSE,
    personality_traits JSONB NOT NULL DEFAULT '{}'::JSONB
);

-- Create clues table
CREATE TABLE template_clues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID REFERENCES mystery_templates(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    location TEXT NOT NULL,
    discovery_difficulty FLOAT NOT NULL DEFAULT 1.0,
    clue_type TEXT NOT NULL CHECK (clue_type IN ('physical', 'testimony', 'observation', 'document')),
    related_suspects JSONB NOT NULL DEFAULT '[]'::JSONB,
    is_red_herring BOOLEAN NOT NULL DEFAULT FALSE
);

-- Create locations table
CREATE TABLE template_locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID REFERENCES mystery_templates(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    significance TEXT NOT NULL
);

-- Create RLS policies
ALTER TABLE mystery_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE template_victims ENABLE ROW LEVEL SECURITY;
ALTER TABLE template_suspects ENABLE ROW LEVEL SECURITY;
ALTER TABLE template_clues ENABLE ROW LEVEL SECURITY;
ALTER TABLE template_locations ENABLE ROW LEVEL SECURITY;

-- Policy for reading published templates (anyone can read)
CREATE POLICY "Anyone can read published templates"
ON mystery_templates FOR SELECT
USING (is_published = TRUE);

-- Policy for template creators
CREATE POLICY "Creators can do anything with their templates"
ON mystery_templates FOR ALL
USING (auth.uid() = created_by);

-- Similar policies for related tables...

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updated_at
CREATE TRIGGER update_mystery_templates_updated_at
BEFORE UPDATE ON mystery_templates
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

#### Resources
- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Row Level Security in Supabase](https://supabase.com/docs/guides/auth/row-level-security)
- [Database Schema Design Best Practices](https://www.postgresql.org/docs/current/ddl.html)

---

### BE-005: Develop story progression endpoints

#### Description
Create backend API endpoints that handle story progression, including starting new stories, processing player actions, generating narrative responses, and managing the story state. These endpoints will connect the frontend narrative interface with the AI agents.

#### Implementation Steps

1. **Review mystery template storage (BE-004)**
   - Understand how templates are stored and retrieved
   - Note the API patterns and authentication methods

2. **Design the story progression API**
   - Plan the endpoints needed for story management
   - Define request/response formats
   - Consider error handling and edge cases

3. **Create Pydantic models for story state**
   ```bash
   # Create models file
   touch backend/models/story_models.py
   ```

4. **Implement Flask routes for story progression**
   ```bash
   # Create story routes file
   touch backend/routes/story_routes.py
   ```

5. **Create service layer for story operations**
   ```bash
   # Create story service
   touch backend/services/story_service.py
   ```

6. **Implement story state management**
   - Create functions to initialize story state
   - Add methods to update state based on actions
   - Implement state persistence in Supabase

7. **Integrate with StoryAgent**
   - Connect endpoints to the StoryAgent
   - Pass user actions to the agent
   - Return narrative responses

8. **Add authentication and authorization**
   - Ensure endpoints require authentication
   - Verify user has access to the requested story

9. **Implement caching for performance**
   - Cache frequent narrative responses
   - Use Redis for temporary state storage

10. **Write unit tests**
    ```bash
    # Create test file
    touch backend/tests/test_story_routes.py
    ```

#### Example API Endpoints

```
POST /api/stories - Start a new story
GET /api/stories/{id} - Get current story state
POST /api/stories/{id}/actions - Submit a player action
GET /api/stories/{id}/narrative - Get the current narrative
POST /api/stories/{id}/save - Save the current story state
GET /api/stories/{id}/choices - Get available player choices
```

#### Example Story Models

```python
# Example Pydantic models for story state
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime

class PlayerAction(BaseModel):
    action_type: Literal["choice", "free_text", "examine", "interact"]
    content: str
    target_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class NarrativeSegment(BaseModel):
    id: str
    text: str
    character: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
class StoryChoice(BaseModel):
    id: str
    text: str
    consequences: Optional[str] = None
    
class StoryState(BaseModel):
    id: Optional[str] = None
    user_id: str
    template_id: str
    current_scene: str
    narrative_history: List[NarrativeSegment] = Field(default_factory=list)
    discovered_clues: List[str] = Field(default_factory=list)
    suspect_states: Dict[str, Any] = Field(default_factory=dict)
    player_actions: List[PlayerAction] = Field(default_factory=list)
    available_choices: List[StoryChoice] = Field(default_factory=list)
    allow_free_input: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

#### Example Route Implementation

```python
# Example Flask route for story actions
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.story_service import StoryService
from backend.models.story_models import PlayerAction

story_routes = Blueprint('story_routes', __name__)
story_service = StoryService()

@story_routes.route('/api/stories/<story_id>/actions', methods=['POST'])
@jwt_required()
def submit_action(story_id):
    user_id = get_jwt_identity()
    
    # Validate request data
    data = request.get_json()
    try:
        action = PlayerAction(
            action_type=data['action_type'],
            content=data['content'],
            target_id=data.get('target_id')
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    # Process the action
    try:
        result = story_service.process_action(story_id, user_id, action)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

#### Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/latest/)
- [RESTful API Design](https://restfulapi.net/)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [Redis Python Client](https://redis.io/docs/clients/python/)

## Testing Your Work

### DB-002 Testing
1. Connect to Supabase and verify the schema:
   ```bash
   # Use the Supabase dashboard or SQL editor
   # Run queries to check table structure
   SELECT * FROM information_schema.tables WHERE table_schema = 'public';
   ```
2. Test inserting sample data:
   ```sql
   -- Insert a test template
   INSERT INTO mystery_templates (title, description, setting, time_period)
   VALUES ('Test Template', 'A test mystery', 'Victorian London', '1890s')
   RETURNING id;
   ```
3. Test RLS policies:
   ```bash
   # Test as different users to verify policies
   ```

### BE-005 Testing
1. Run the Flask development server:
   ```bash
   cd backend
   flask run
   ```
2. Use Postman or curl to test API endpoints:
   ```bash
   # Example: Start a new story
   curl -X POST http://localhost:5000/api/stories \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"template_id": "TEMPLATE_ID"}'
   
   # Example: Submit an action
   curl -X POST http://localhost:5000/api/stories/STORY_ID/actions \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"action_type": "free_text", "content": "Examine the bookshelf"}'
   ```
3. Run unit tests:
   ```bash
   cd backend
   pytest tests/test_story_routes.py
   ```

## Deliverables

### DB-002 Deliverables
- Complete mystery template schema in Supabase
- RLS policies for security
- Database functions and triggers
- Schema documentation

### BE-005 Deliverables
- Story state Pydantic models
- Flask routes for story progression
- Story service layer
- Integration with StoryAgent
- Unit tests for all endpoints

## Communication

If you encounter any blockers or have questions:
- Post in the #milestone-2 Slack channel
- Tag the project lead for urgent issues
- Document any design decisions or assumptions in your PR description

Good luck with your tasks! Remember to commit your work regularly and create pull requests for review.
