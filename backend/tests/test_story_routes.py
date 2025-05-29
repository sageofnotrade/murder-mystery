import pytest
from uuid import uuid4
from flask import Flask
from routes.story_routes import story_bp
from models.story_models import StoryState, PlayerAction, StoryChoice
from unittest.mock import Mock, patch
import json

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
    with patch('routes.story_routes.story_service') as mock:
        yield mock

@pytest.fixture
def auth_headers():
    return {'Authorization': 'Bearer test-token'}

def test_create_story(client, mock_story_service, auth_headers):
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

def test_get_story(client, mock_story_service, auth_headers):
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

def test_process_action(client, mock_story_service, auth_headers):
    # Mock the JWT identity
    with patch('flask_jwt_extended.get_jwt_identity', return_value='test-user'):
        # Mock the story service response
        story_id = uuid4()
        mock_response = {
            'story_id': str(story_id),
            'narrative': 'As you examine the bookshelf, you notice a peculiar book that seems out of place. The spine is slightly worn, suggesting frequent use.',
            'choices': [
                {
                    'id': '1',
                    'text': 'Take a closer look at the worn book',
                    'consequences': 'This might reveal important information about the victim\'s interests.'
                },
                {
                    'id': '2',
                    'text': 'Check the surrounding area for other clues',
                    'consequences': 'You might find additional evidence in the vicinity.'
                }
            ],
            'discovered_clues': [
                {
                    'id': 'clue_1',
                    'description': 'A worn book on the bookshelf',
                    'significance': 'The book appears to have been frequently used by the victim.'
                }
            ],
            'suspect_states': {
                'butler': {
                    'suspicion_level': 0.3,
                    'last_seen': 'In the library, arranging books'
                }
            },
            'current_scene': 'library_investigation'
        }
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
        assert len(data['discovered_clues']) == 1
        assert 'suspect_states' in data
        assert data['current_scene'] == 'library_investigation'

def test_get_choices(client, mock_story_service, auth_headers):
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

def test_save_story(client, mock_story_service, auth_headers):
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

def test_unauthorized_access(client, mock_story_service, auth_headers):
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

def test_invalid_story_id(client, mock_story_service, auth_headers):
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