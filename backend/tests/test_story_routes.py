from unittest.mock import patch, MagicMock, AsyncMock
# Patch Supabase client at a higher level to bypass validation
supabase_create_client_patch = patch('supabase._sync.client.create_client', return_value=MagicMock())
supabase_create_client_patch.start()

import pytest
from uuid import uuid4, UUID
from flask import Flask
from backend.routes.story_routes import story_bp, get_supabase_client, get_story_service
from backend.agents.models.story_models import StoryState, PlayerAction, StoryChoice, StoryResponse
import json
from backend.app import app
from datetime import datetime
import unittest
from fastapi.testclient import TestClient
from backend.agents.models.psychological_profile import (
    PsychologicalProfile,
    create_default_profile,
    TraitIntensity,
    CognitiveStyle,
    EmotionalTendency,
    SocialStyle
)

# Mock Supabase client at module level
mock_supabase = MagicMock()
mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None
mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{'id': str(uuid4())}]
mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = None

# Mock Redis client at module level
mock_redis = MagicMock()
mock_redis.get.return_value = None
mock_redis.set.return_value = True

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.register_blueprint(story_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_story_service():
    with patch('routes.story_routes.get_story_service') as mock:
        mock_service = MagicMock()
        mock_service.create_story = AsyncMock()
        mock_service.get_story = AsyncMock()
        mock_service.process_action = AsyncMock()
        mock_service.get_available_choices = AsyncMock()
        mock_service.save_story_state = AsyncMock()
        mock.return_value = mock_service
        yield mock_service

@pytest.fixture
def auth_headers():
    return {'Authorization': 'Bearer test-token'}

@pytest.fixture
def sample_story_data():
    return {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'user_id': 'user123',
        'mystery_id': 'mystery123',
        'title': 'Test Story',
        'current_scene': 'introduction',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'narrative_history': [],
        'discovered_clues': [],
        'suspect_states': {}
    }

@pytest.fixture
def sample_action_data():
    return {
        'action_type': 'examine',
        'content': 'Look at the desk',
        'target_id': 'desk1'
    }

@pytest.fixture
def sample_choice_data():
    return {
        'choice_text': 'Open the drawer',
        'consequences': {'reveals_clue': 'clue1'}
    }

@pytest.mark.asyncio
async def test_create_story(client, mock_story_service, auth_headers):
    # Mock the JWT identity
    with patch('flask_jwt_extended.get_jwt_identity', return_value='test-user'):
        # Mock the story service response
        story_id = uuid4()
        mock_story = StoryState(
            id=story_id,
            mystery_id=uuid4(),
            user_id='test-user',
            current_scene='introduction'
        )
        mock_story_service.create_story.return_value = mock_story

        # Make the request
        response = client.post(
            '/stories',
            json={'mystery_id': str(uuid4())},
            headers=auth_headers
        )

        # Assert response
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'story_id' in data
        assert data['story_id'] == str(story_id)

@pytest.mark.asyncio
async def test_get_story(client, mock_story_service, auth_headers):
    # Mock the JWT identity
    with patch('flask_jwt_extended.get_jwt_identity', return_value='test-user'):
        # Mock the story service response
        story_id = uuid4()
        mock_story = StoryState(
            id=story_id,
            mystery_id=uuid4(),
            user_id='test-user',
            current_scene='introduction'
        )
        mock_story_service.get_story.return_value = mock_story

        # Make the request
        response = client.get(
            f'/stories/{story_id}',
            headers=auth_headers
        )

        # Assert response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == str(story_id)
        assert data['current_scene'] == 'introduction'

@pytest.mark.asyncio
async def test_process_action(client, mock_story_service, auth_headers):
    # Mock the JWT identity
    with patch('flask_jwt_extended.get_jwt_identity', return_value='test-user'):
        # Mock the story service response
        story_id = uuid4()
        mock_response = StoryResponse(
            story_id=story_id,
            narrative="Test narrative",
            choices=[
                StoryChoice(id="1", text="Choice 1"),
                StoryChoice(id="2", text="Choice 2")
            ],
            discovered_clues=[],
            suspect_states={},
            current_scene="test_scene"
        )
        mock_story_service.process_action.return_value = mock_response

        # Make the request
        response = client.post(
            f'/stories/{story_id}/actions',
            json={
                'action_type': 'examine',
                'content': 'Look at the bookshelf'
            },
            headers=auth_headers
        )

        # Assert response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['story_id'] == str(story_id)
        assert 'narrative' in data
        assert len(data['choices']) == 2

@pytest.mark.asyncio
async def test_get_choices(client, mock_story_service, auth_headers):
    # Mock the JWT identity
    with patch('flask_jwt_extended.get_jwt_identity', return_value='test-user'):
        # Mock the story service response
        story_id = uuid4()
        mock_choices = [
            StoryChoice(id='1', text='Continue investigation'),
            StoryChoice(id='2', text='Examine clues')
        ]
        mock_story_service.get_available_choices.return_value = mock_choices

        # Make the request
        response = client.get(
            f'/stories/{story_id}/choices',
            headers=auth_headers
        )

        # Assert response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        assert data[0]['id'] == '1'
        assert data[1]['id'] == '2'

@pytest.mark.asyncio
async def test_save_story(client, mock_story_service, auth_headers):
    # Mock the JWT identity
    with patch('flask_jwt_extended.get_jwt_identity', return_value='test-user'):
        # Mock the story service response
        story_id = uuid4()
        mock_story = StoryState(
            id=story_id,
            mystery_id=uuid4(),
            user_id='test-user',
            current_scene='introduction'
        )
        mock_story_service.get_story.return_value = mock_story
        mock_story_service.save_story_state.return_value = None

        # Make the request
        response = client.post(
            f'/stories/{story_id}/save',
            headers=auth_headers
        )

        # Assert response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Story state saved successfully'

@pytest.mark.asyncio
async def test_unauthorized_access(client, mock_story_service, auth_headers):
    # Mock the JWT identity
    with patch('flask_jwt_extended.get_jwt_identity', return_value='test-user'):
        # Mock the story service to raise an unauthorized error
        story_id = uuid4()
        mock_story_service.get_story.side_effect = Exception("Unauthorized access to story")

        # Make the request
        response = client.get(
            f'/stories/{story_id}',
            headers=auth_headers
        )

        # Assert response
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data

@pytest.mark.asyncio
async def test_invalid_story_id(client, mock_story_service, auth_headers):
    # Mock the JWT identity
    with patch('flask_jwt_extended.get_jwt_identity', return_value='test-user'):
        # Make the request with an invalid UUID
        response = client.get(
            '/stories/invalid-uuid',
            headers=auth_headers
        )

        # Assert response
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

async def test_get_stories(client, auth_headers, mock_supabase, sample_story_data):
    """Test getting all stories for a user."""
    # Set up mock data
    mock_supabase.table.return_value.select.return_value.execute.return_value = {
        'data': [sample_story_data]
    }
    
    # Make request
    response = await client.get('/api/stories', headers=auth_headers)
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['title'] == 'Test Story'

async def test_get_story(client, auth_headers, mock_supabase, sample_story_data):
    """Test getting a specific story."""
    # Set up mock data
    mock_supabase.table.return_value.select.return_value.execute.return_value = {
        'data': [sample_story_data]
    }
    
    # Make request
    response = await client.get(
        f'/api/stories/{sample_story_data["id"]}',
        headers=auth_headers
    )
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == 'Test Story'

async def test_create_story(client, auth_headers, mock_supabase, sample_story_data):
    """Test creating a new story."""
    # Set up mock data
    mock_supabase.table.return_value.insert.return_value.execute.return_value = {
        'data': [sample_story_data]
    }
    
    # Make request
    response = await client.post(
        '/api/stories',
        headers=auth_headers,
        json={'mystery_id': 'mystery123'}
    )
    
    # Check response
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == 'Test Story'

async def test_get_story_progress(client, auth_headers, mock_supabase):
    """Test getting story progress."""
    # Set up mock data
    mock_supabase.table.return_value.select.return_value.execute.return_value = {
        'data': [{'game_progress': 0.5}]
    }
    
    # Make request
    response = await client.get(
        '/api/stories/123e4567-e89b-12d3-a456-426614174000/progress',
        headers=auth_headers
    )
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['game_progress'] == 0.5

async def test_perform_action(client, auth_headers, mock_supabase, sample_action_data):
    """Test performing an action in the story."""
    # Set up mock data
    mock_supabase.table.return_value.insert.return_value.execute.return_value = {
        'data': [{
            'id': 'action1',
            'story_id': '123e4567-e89b-12d3-a456-426614174000',
            **sample_action_data
        }]
    }
    
    # Make request
    response = await client.post(
        '/api/stories/123e4567-e89b-12d3-a456-426614174000/actions',
        headers=auth_headers,
        json=sample_action_data
    )
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['action_type'] == 'examine'

async def test_make_choice(client, auth_headers, mock_supabase, sample_choice_data):
    """Test making a choice in the story."""
    # Set up mock data
    mock_supabase.table.return_value.insert.return_value.execute.return_value = {
        'data': [{
            'id': 'choice1',
            'story_id': '123e4567-e89b-12d3-a456-426614174000',
            **sample_choice_data
        }]
    }
    
    # Make request
    response = await client.post(
        '/api/stories/123e4567-e89b-12d3-a456-426614174000/choices',
        headers=auth_headers,
        json=sample_choice_data
    )
    
    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['choice_text'] == 'Open the drawer'

class TestStoryRoutes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.default_profile = create_default_profile()
        
    def test_start_story_with_profile(self):
        """Test starting a story with a psychological profile."""
        response = self.client.post(
            "/api/story/start",
            json={
                "player_profile": {
                    "psychological_profile": self.default_profile.dict()
                }
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("narrative", data)
        self.assertIn("story_state", data)
        
    def test_process_action_with_profile(self):
        """Test processing an action with a psychological profile."""
        # First start a story
        start_response = self.client.post(
            "/api/story/start",
            json={
                "player_profile": {
                    "psychological_profile": self.default_profile.dict()
                }
            }
        )
        story_id = start_response.json()["story_state"]["id"]
        
        # Then process an action
        response = self.client.post(
            f"/api/story/{story_id}/action",
            json={
                "action": "look around",
                "player_profile": {
                    "psychological_profile": self.default_profile.dict()
                }
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("narrative", data)
        self.assertIn("story_state", data)
        
    def test_profile_adaptation(self):
        """Test that different profiles result in different narratives."""
        # Create two different profiles
        analytical_profile = create_default_profile()
        analytical_profile.cognitive_style = CognitiveStyle.ANALYTICAL
        
        intuitive_profile = create_default_profile()
        intuitive_profile.cognitive_style = CognitiveStyle.INTUITIVE
        
        # Start stories with different profiles
        analytical_response = self.client.post(
            "/api/story/start",
            json={
                "player_profile": {
                    "psychological_profile": analytical_profile.dict()
                }
            }
        )
        
        intuitive_response = self.client.post(
            "/api/story/start",
            json={
                "player_profile": {
                    "psychological_profile": intuitive_profile.dict()
                }
            }
        )
        
        # Compare narratives
        analytical_narrative = analytical_response.json()["narrative"]
        intuitive_narrative = intuitive_response.json()["narrative"]
        
        self.assertNotEqual(analytical_narrative, intuitive_narrative)
        
    def test_profile_validation(self):
        """Test that invalid profiles are rejected."""
        response = self.client.post(
            "/api/story/start",
            json={
                "player_profile": {
                    "psychological_profile": {
                        "cognitive_style": "INVALID_STYLE"
                    }
                }
            }
        )
        self.assertEqual(response.status_code, 422)

if __name__ == '__main__':
    unittest.main() 