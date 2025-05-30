from unittest.mock import patch, MagicMock, AsyncMock
# Patch Supabase client at a higher level to bypass validation
supabase_create_client_patch = patch('supabase._sync.client.create_client', return_value=MagicMock())
supabase_create_client_patch.start()

import pytest
from uuid import uuid4, UUID
from flask import Flask
from routes.story_routes import story_bp, get_supabase_client, get_story_service
from models.story_models import StoryState, PlayerAction, StoryChoice, StoryResponse
import json
from app import app

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
def sample_story():
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "mystery_id": "123e4567-e89b-12d3-a456-426614174001",
        "state": "active",
        "current_scene": "intro",
        "choices": ["choice1", "choice2"]
    }

@pytest.fixture
def sample_action():
    return {
        "action_type": "investigate",
        "target": "clue1"
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