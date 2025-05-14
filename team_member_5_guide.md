# Team Member 5 - Milestone 2 Task Guide

## Your Tasks Overview

| Task ID | Title | Estimate | Dependencies |
|---------|-------|----------|-------------|
| BE-006 | Implement clue management API | 6h | BE-005 |
| DB-003 | Create story state storage schema | 4h | DB-002 |
| TEST-002 | Create backend unit tests | 6h | BE-001 |
| **Total** | | **16h** | |

## Task Details and Implementation Guide

### TEST-002: Create backend unit tests

#### Description
Develop a comprehensive suite of unit tests for the backend Flask application. These tests will ensure the reliability and correctness of the API endpoints, services, and database interactions.

#### Implementation Steps

1. **Review Flask project structure (BE-001)**
   - Understand the existing Flask application structure
   - Note the patterns used for routes and controllers

2. **Set up testing framework**
   ```bash
   # Install pytest and related packages
   pip install pytest pytest-flask pytest-cov
   ```

3. **Create test configuration**
   ```bash
   # Create test configuration file
   touch backend/tests/conftest.py
   ```

4. **Set up test fixtures**
   - Create fixtures for Flask app
   - Set up database fixtures
   - Create authentication fixtures

5. **Implement tests for authentication endpoints**
   ```bash
   # Create auth test file
   touch backend/tests/test_auth.py
   ```

6. **Create tests for user profile endpoints**
   ```bash
   # Create user profile test file
   touch backend/tests/test_user_profiles.py
   ```

7. **Implement tests for template endpoints**
   ```bash
   # Create template test file
   touch backend/tests/test_templates.py
   ```

8. **Create mock services for testing**
   ```bash
   # Create mock services
   touch backend/tests/mocks/supabase_mock.py
   touch backend/tests/mocks/redis_mock.py
   ```

9. **Set up CI integration**
   ```bash
   # Create GitHub Actions workflow for tests
   mkdir -p .github/workflows
   touch .github/workflows/backend-tests.yml
   ```

10. **Add test coverage reporting**
    - Configure pytest-cov for coverage reports
    - Set up coverage thresholds

#### Example Test Configuration

```python
# conftest.py
import pytest
from flask import Flask
from backend import create_app
from backend.tests.mocks.supabase_mock import MockSupabaseClient
from backend.tests.mocks.redis_mock import MockRedisClient

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app({
        'TESTING': True,
        'SUPABASE_URL': 'mock://supabase',
        'SUPABASE_KEY': 'mock-key',
        'REDIS_URL': 'mock://redis',
    })
    
    # Set up app context
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def mock_supabase():
    """Create a mock Supabase client."""
    return MockSupabaseClient()

@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    return MockRedisClient()

@pytest.fixture
def auth_headers():
    """Generate auth headers for testing protected endpoints."""
    return {
        'Authorization': 'Bearer mock-jwt-token'
    }
```

#### Example Test File

```python
# test_templates.py
import pytest
import json
from backend.models.template_models import MysteryTemplate

def test_get_templates(client, auth_headers, mock_supabase, monkeypatch):
    """Test getting all templates."""
    # Set up mock data
    mock_templates = [
        {
            'id': '1',
            'title': 'Test Template 1',
            'description': 'A test template',
            'setting': 'Victorian London',
            'time_period': '1890s',
        },
        {
            'id': '2',
            'title': 'Test Template 2',
            'description': 'Another test template',
            'setting': 'Modern New York',
            'time_period': '2020s',
        }
    ]
    
    # Configure mock to return test data
    mock_supabase.table.return_value.select.return_value.execute.return_value = {
        'data': mock_templates
    }
    
    # Patch the Supabase client in the app
    from backend.services.supabase_service import SupabaseService
    monkeypatch.setattr(SupabaseService, 'client', mock_supabase)
    
    # Make request
    response = client.get('/api/templates', headers=auth_headers)
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert data[0]['title'] == 'Test Template 1'
    assert data[1]['title'] == 'Test Template 2'

def test_create_template(client, auth_headers, mock_supabase, monkeypatch):
    """Test creating a new template."""
    # Template data to create
    template_data = {
        'title': 'New Template',
        'description': 'A brand new template',
        'setting': 'Space Station',
        'time_period': '2150s',
        'suspects': [
            {
                'name': 'Commander Smith',
                'description': 'Station commander',
                'motive': 'Revenge',
                'alibi': 'Was on a video call',
                'guilty': True
            }
        ],
        'clues': [
            {
                'id': 'clue1',
                'description': 'Broken keycard',
                'location': 'Airlock',
                'type': 'physical'
            }
        ]
    }
    
    # Configure mock to return created template
    created_template = template_data.copy()
    created_template['id'] = '3'
    mock_supabase.table.return_value.insert.return_value.execute.return_value = {
        'data': [created_template]
    }
    
    # Patch the Supabase client in the app
    from backend.services.supabase_service import SupabaseService
    monkeypatch.setattr(SupabaseService, 'client', mock_supabase)
    
    # Make request
    response = client.post(
        '/api/templates',
        headers=auth_headers,
        json=template_data
    )
    
    # Check response
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['id'] == '3'
    assert data['title'] == 'New Template'
    assert len(data['suspects']) == 1
    assert len(data['clues']) == 1
```

#### Resources
- [Pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/2.0.x/testing/)
- [Pytest-Flask](https://pytest-flask.readthedocs.io/en/latest/)
- [Mocking in Python](https://docs.python.org/3/library/unittest.mock.html)
- [GitHub Actions for CI/CD](https://docs.github.com/en/actions)

---

### DB-003: Create story state storage schema

#### Description
Design and implement the database schema for storing story state in Supabase. This schema will track the current state of each player's mystery, including narrative progress, discovered clues, and character interactions.

#### Implementation Steps

1. **Review mystery template schema (DB-002)**
   - Understand the template schema structure
   - Note the relationships and data types

2. **Design the story state schema**
   - Plan the table structure for story state
   - Define relationships with users and templates
   - Consider performance and query patterns

3. **Create tables in Supabase**
   - Use the Supabase dashboard or SQL editor
   - Define primary keys, foreign keys, and indexes
   - Set up appropriate constraints

4. **Set up Row Level Security (RLS) policies**
   - Define who can access story state data
   - Implement policies for different user roles

5. **Create database functions and triggers**
   - Add any necessary functions for state management
   - Set up triggers for state changes

6. **Document the schema**
   - Create an ERD (Entity Relationship Diagram)
   - Document table structures and relationships
   - Add comments to tables and columns

#### Example Schema SQL

```sql
-- Create stories table
CREATE TABLE stories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    template_id UUID NOT NULL REFERENCES mystery_templates(id),
    title TEXT NOT NULL,
    current_scene TEXT NOT NULL,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create narrative history table
CREATE TABLE narrative_segments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    story_id UUID NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    character JSONB,
    sequence_number INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create player actions table
CREATE TABLE player_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    story_id UUID NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    action_type TEXT NOT NULL CHECK (action_type IN ('choice', 'free_text', 'examine', 'interact')),
    content TEXT NOT NULL,
    target_id TEXT,
    sequence_number INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create discovered clues table
CREATE TABLE discovered_clues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    story_id UUID NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    clue_id TEXT NOT NULL,
    discovery_context TEXT,
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create suspect states table
CREATE TABLE suspect_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    story_id UUID NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    suspect_id TEXT NOT NULL,
    state JSONB NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create story notes table (for player's personal notes)
CREATE TABLE story_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    story_id UUID NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create RLS policies
ALTER TABLE stories ENABLE ROW LEVEL SECURITY;
ALTER TABLE narrative_segments ENABLE ROW LEVEL SECURITY;
ALTER TABLE player_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE discovered_clues ENABLE ROW LEVEL SECURITY;
ALTER TABLE suspect_states ENABLE ROW LEVEL SECURITY;
ALTER TABLE story_notes ENABLE ROW LEVEL SECURITY;

-- Policy for story owners
CREATE POLICY "Users can only access their own stories"
ON stories FOR ALL
USING (auth.uid() = user_id);

-- Similar policies for related tables
CREATE POLICY "Users can only access their own narrative segments"
ON narrative_segments FOR ALL
USING (EXISTS (
    SELECT 1 FROM stories
    WHERE stories.id = narrative_segments.story_id
    AND stories.user_id = auth.uid()
));

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updated_at
CREATE TRIGGER update_stories_updated_at
BEFORE UPDATE ON stories
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for story_notes updated_at
CREATE TRIGGER update_story_notes_updated_at
BEFORE UPDATE ON story_notes
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

#### Resources
- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Row Level Security in Supabase](https://supabase.com/docs/guides/auth/row-level-security)
- [Database Schema Design Best Practices](https://www.postgresql.org/docs/current/ddl.html)

---

### BE-006: Implement clue management API

#### Description
Create backend API endpoints for managing clues in the murder mystery, including discovering clues, analyzing evidence, and tracking connections between clues and suspects. These endpoints will connect the frontend detective board with the AI agents.

#### Implementation Steps

1. **Review story progression endpoints (BE-005)**
   - Understand how story state is managed
   - Note the API patterns and authentication methods

2. **Design the clue management API**
   - Plan the endpoints needed for clue operations
   - Define request/response formats
   - Consider error handling and edge cases

3. **Create Pydantic models for clues**
   ```bash
   # Create models file
   touch backend/models/clue_models.py
   ```

4. **Implement Flask routes for clue management**
   ```bash
   # Create clue routes file
   touch backend/routes/clue_routes.py
   ```

5. **Create service layer for clue operations**
   ```bash
   # Create clue service
   touch backend/services/clue_service.py
   ```

6. **Implement clue discovery logic**
   - Create functions to discover new clues
   - Add methods to track discovered clues
   - Implement clue revelation based on player actions

7. **Integrate with ClueAgent**
   - Connect endpoints to the ClueAgent
   - Pass discovery requests to the agent
   - Return clue details and analysis

8. **Implement clue connection management**
   - Add endpoints for creating connections between clues
   - Create methods for suggesting connections
   - Implement validation for connections

9. **Add authentication and authorization**
   - Ensure endpoints require authentication
   - Verify user has access to the requested story

10. **Write unit tests**
    ```bash
    # Create test file
    touch backend/tests/test_clue_routes.py
    ```

#### Example API Endpoints

```
GET /api/stories/{id}/clues - Get all discovered clues for a story
POST /api/stories/{id}/clues/discover - Discover a new clue
GET /api/stories/{id}/clues/{clue_id} - Get details for a specific clue
POST /api/stories/{id}/clues/{clue_id}/analyze - Analyze a clue for deeper insights
POST /api/stories/{id}/clues/connections - Create a connection between clues
GET /api/stories/{id}/clues/connections - Get all clue connections
```

#### Example Clue Models

```python
# Example Pydantic models for clues
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime

class ClueBase(BaseModel):
    id: str
    description: str
    location: str
    type: Literal["physical", "testimony", "observation", "document"]
    
class ClueCreate(ClueBase):
    discovery_context: Optional[str] = None
    
class ClueInDB(ClueBase):
    story_id: str
    discovery_context: Optional[str] = None
    discovered_at: datetime = Field(default_factory=datetime.now)
    
class ClueDetail(ClueInDB):
    analysis: Optional[Dict[str, Any]] = None
    related_suspects: List[str] = Field(default_factory=list)
    
class ClueConnection(BaseModel):
    id: Optional[str] = None
    story_id: str
    source_clue_id: str
    target_clue_id: str
    relationship_type: str
    description: str
    created_at: Optional[datetime] = None
    
class ClueAnalysisRequest(BaseModel):
    context: Optional[str] = None
    focus_areas: Optional[List[str]] = None
```

#### Example Route Implementation

```python
# Example Flask route for clue discovery
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.clue_service import ClueService
from backend.models.clue_models import ClueCreate

clue_routes = Blueprint('clue_routes', __name__)
clue_service = ClueService()

@clue_routes.route('/api/stories/<story_id>/clues', methods=['GET'])
@jwt_required()
def get_clues(story_id):
    user_id = get_jwt_identity()
    
    try:
        clues = clue_service.get_discovered_clues(story_id, user_id)
        return jsonify(clues)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clue_routes.route('/api/stories/<story_id>/clues/discover', methods=['POST'])
@jwt_required()
def discover_clue(story_id):
    user_id = get_jwt_identity()
    
    # Validate request data
    data = request.get_json()
    try:
        clue_data = ClueCreate(
            id=data['id'],
            description=data['description'],
            location=data['location'],
            type=data['type'],
            discovery_context=data.get('discovery_context')
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    # Process the clue discovery
    try:
        result = clue_service.discover_clue(story_id, user_id, clue_data)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clue_routes.route('/api/stories/<story_id>/clues/<clue_id>/analyze', methods=['POST'])
@jwt_required()
def analyze_clue(story_id, clue_id):
    user_id = get_jwt_identity()
    
    # Get analysis parameters
    data = request.get_json() or {}
    
    # Process the clue analysis
    try:
        result = clue_service.analyze_clue(
            story_id, 
            user_id, 
            clue_id, 
            context=data.get('context'),
            focus_areas=data.get('focus_areas')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

#### Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/latest/)
- [RESTful API Design](https://restfulapi.net/)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)

## Testing Your Work

### TEST-002 Testing
1. Run the tests:
   ```bash
   cd backend
   pytest
   ```
2. Check test coverage:
   ```bash
   cd backend
   pytest --cov=backend
   ```
3. Run specific test files:
   ```bash
   cd backend
   pytest tests/test_templates.py
   ```

### DB-003 Testing
1. Connect to Supabase and verify the schema:
   ```bash
   # Use the Supabase dashboard or SQL editor
   # Run queries to check table structure
   SELECT * FROM information_schema.tables WHERE table_schema = 'public';
   ```
2. Test inserting sample data:
   ```sql
   -- Insert a test story
   INSERT INTO stories (user_id, template_id, title, current_scene)
   VALUES ('USER_ID', 'TEMPLATE_ID', 'Test Story', 'introduction')
   RETURNING id;
   ```
3. Test RLS policies:
   ```bash
   # Test as different users to verify policies
   ```

### BE-006 Testing
1. Run the Flask development server:
   ```bash
   cd backend
   flask run
   ```
2. Use Postman or curl to test API endpoints:
   ```bash
   # Example: Get all clues for a story
   curl -X GET http://localhost:5000/api/stories/STORY_ID/clues \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   
   # Example: Discover a new clue
   curl -X POST http://localhost:5000/api/stories/STORY_ID/clues/discover \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"id": "clue1", "description": "Bloodstained letter", "location": "Study", "type": "physical"}'
   ```
3. Run unit tests:
   ```bash
   cd backend
   pytest tests/test_clue_routes.py
   ```

## Deliverables

### TEST-002 Deliverables
- Complete test suite for backend endpoints
- Test fixtures and mocks
- CI integration for automated testing
- Test coverage reports

### DB-003 Deliverables
- Complete story state schema in Supabase
- RLS policies for security
- Database functions and triggers
- Schema documentation

### BE-006 Deliverables
- Clue management Pydantic models
- Flask routes for clue operations
- Clue service layer
- Integration with ClueAgent
- Unit tests for all endpoints

## Communication

If you encounter any blockers or have questions:
- Post in the #milestone-2 Slack channel
- Tag the project lead for urgent issues
- Document any design decisions or assumptions in your PR description

Good luck with your tasks! Remember to commit your work regularly and create pull requests for review.
