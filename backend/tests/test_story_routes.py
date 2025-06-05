from backend.tests.mocks.supabase_mock import MockSupabaseClient
from unittest.mock import patch, MagicMock, AsyncMock
# Patch Supabase client globally for all tests in this module
supabase_client_patch1 = patch('backend.services.supabase_service.get_supabase_client', return_value=MockSupabaseClient())
supabase_client_patch1.start()
supabase_client_patch2 = patch('backend.routes.story_routes.get_supabase_client', return_value=MockSupabaseClient())
supabase_client_patch2.start()

pytest_plugins = ["pytest_asyncio"]
import pytest
from uuid import uuid4, UUID
from flask import Flask
from backend.routes.story_routes import story_bp, get_supabase_client, get_story_service
from backend.agents.models.story_models import StoryState, PlayerAction, StoryChoice, StoryResponse
import json
from backend.app import create_app
from datetime import datetime
import unittest
from fastapi.testclient import TestClient
from flask_jwt_extended import JWTManager, create_access_token
from backend.agents.models.psychological_profile import (
    PsychologicalProfile,
    create_default_profile,
    TraitIntensity,
    CognitiveStyle,
    EmotionalTendency,
    SocialStyle
)

@pytest.fixture(scope="module")
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.register_blueprint(story_bp, url_prefix='/api')
    jwt = JWTManager(app)
    return app

@pytest.fixture
def client(app):
    with app.app_context():
        yield app.test_client()

@pytest.fixture(scope="module")
def shared_mock_supabase():
    mock_supabase = MockSupabaseClient()
    with patch('backend.services.supabase_service.get_supabase_client', return_value=mock_supabase), \
         patch('backend.routes.story_routes.get_supabase_client', return_value=mock_supabase):
        yield mock_supabase

@pytest.fixture
def auth_headers(app):
    with app.app_context():
        token = create_access_token(identity='test-user')
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def sample_story_data():
    return {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'user_id': 'test-user',
        'mystery_id': str(uuid4()),
        'current_scene': 'introduction',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'narrative_history': json.dumps([]),
        'discovered_clues': json.dumps([]),
        'suspect_states': json.dumps({}),
        'player_choices': json.dumps([]),
        'last_action': None
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

@pytest.fixture
def mock_supabase():
    return MockSupabaseClient()

def test_get_stories(client, auth_headers, sample_story_data, shared_mock_supabase):
    """Test getting all stories for a user."""
    story_id = str(uuid4())
    mock_story = {
        'id': story_id,
        'user_id': 'test-user',
        'mystery_id': str(uuid4()),
        'current_scene': 'introduction',
        'narrative_history': json.dumps([]),
        'discovered_clues': json.dumps([]),
        'suspect_states': json.dumps({}),
        'player_choices': json.dumps([]),
        'last_action': None
    }
    shared_mock_supabase.table('stories').data = [mock_story]
    print('DEBUG: stories table before request:', shared_mock_supabase.table('stories').data)
    response = client.get('/api/stories', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['id'] == story_id
    assert data[0]['current_scene'] == 'introduction'

def test_get_story(client, auth_headers, sample_story_data, shared_mock_supabase):
    """Test getting a specific story."""
    story_id = str(uuid4())
    mock_story = {
        'id': story_id,
        'user_id': 'test-user',
        'mystery_id': str(uuid4()),
        'current_scene': 'introduction',
        'narrative_history': json.dumps([]),
        'discovered_clues': json.dumps([]),
        'suspect_states': json.dumps({}),
        'player_choices': json.dumps([]),
        'last_action': None
    }
    shared_mock_supabase.table('stories').data = [mock_story]
    print('DEBUG: stories table before request:', shared_mock_supabase.table('stories').data)
    response = client.get(
        f'/api/stories/{story_id}',
        headers=auth_headers
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == story_id
    assert data['current_scene'] == 'introduction'

def test_create_story(client, auth_headers, sample_story_data, shared_mock_supabase):
    """Test creating a new story."""
    mystery_id = str(uuid4())
    mock_mystery = {
        'id': mystery_id,
        'title': 'Test Mystery',
        'description': 'A test mystery',
        'created_at': sample_story_data['created_at'],
        'updated_at': sample_story_data['updated_at']
    }
    shared_mock_supabase.table('mysteries').data = [mock_mystery]
    print('DEBUG: mysteries table before request:', shared_mock_supabase.table('mysteries').data)
    response = client.post(
        '/api/stories',
        headers=auth_headers,
        json={'mystery_id': mystery_id}
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data
    assert 'current_scene' in data
    assert data['current_scene'] == 'introduction'

def test_get_story_progress(client, auth_headers, sample_story_data, shared_mock_supabase):
    story_id = str(uuid4())
    mock_story = sample_story_data.copy()
    mock_story['id'] = story_id
    shared_mock_supabase.table('stories').data = [mock_story]
    response = client.get(f'/api/stories/{story_id}/progress', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == story_id

def test_perform_action(client, auth_headers, sample_story_data, sample_action_data, shared_mock_supabase):
    story_id = str(uuid4())
    mock_story = sample_story_data.copy()
    mock_story['id'] = story_id
    shared_mock_supabase.table('stories').data = [mock_story]
    response = client.post(
        f'/api/stories/{story_id}/actions',
        headers=auth_headers,
        json=sample_action_data
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['story_id'] == story_id
    assert 'narrative' in data
    assert 'current_scene' in data

def test_make_choice(client, auth_headers, sample_story_data, sample_choice_data, shared_mock_supabase):
    story_id = str(uuid4())
    mock_story = sample_story_data.copy()
    mock_story['id'] = story_id
    shared_mock_supabase.table('stories').data = [mock_story]
    response = client.post(
        f'/api/stories/{story_id}/choices',
        headers=auth_headers,
        json={'choice_id': '1'}
    )
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