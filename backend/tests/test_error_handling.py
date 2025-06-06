# when executed, will encounter AssertionError: assert 422 == 404

import pytest
import json
import logging
from unittest.mock import patch, MagicMock
from backend.app import create_app
from utils.error_handlers import (
    APIError, ValidationError, ResourceNotFoundError,
    AuthenticationError, AuthorizationError
)

app = create_app()

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def mock_supabase_auth():
    """Mock Supabase auth validation for all tests."""
    mock_client = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 'test-user-id'
    mock_user.email = 'test@example.com'
    mock_client.auth.get_user.return_value = mock_user
    with patch('backend.services.supabase_service.get_supabase_client', return_value=mock_client):
        yield mock_client

def test_get_stories_invalid_user(client, auth_headers):
    with patch('backend.routes.story_routes.get_story_service') as mock_service:
        mock_service.return_value.get_user_stories.side_effect = ResourceNotFoundError('User not found')
        response = client.get('/api/stories', headers=auth_headers)
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['data'] is None
        assert data['error'] == 'User not found'

def test_get_story_not_found(client, auth_headers):
    with patch('backend.routes.story_routes.get_story_service') as mock_service:
        mock_service.return_value.get_story_sync.side_effect = ResourceNotFoundError('Story not found')
        response = client.get('/api/stories/123', headers=auth_headers)
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['data'] is None
        assert data['error'] == 'Story not found'

def test_create_story_missing_data(client, auth_headers):
    with patch('backend.routes.story_routes.get_story_service') as mock_service:
        mock_service.return_value.create_story_sync.side_effect = ValidationError('Missing required fields')
        response = client.post('/api/stories', json={}, headers=auth_headers)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['data'] is None
        assert 'Missing required fields' in data['error']

def test_perform_action_invalid_story(client, auth_headers):
    with patch('backend.routes.story_routes.get_story_service') as mock_service:
        mock_service.return_value.perform_action_sync.side_effect = ResourceNotFoundError('Invalid story')
        response = client.post('/api/stories/123/actions', json={'action': 'test'}, headers=auth_headers)
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['data'] is None
        assert data['error'] == 'Invalid story'

def test_make_choice_invalid_story(client, auth_headers):
    with patch('backend.routes.story_routes.get_story_service') as mock_service:
        mock_service.return_value.make_choice_sync.side_effect = ResourceNotFoundError('Invalid story')
        response = client.post('/api/stories/123/choices', json={'choice': 'test'}, headers=auth_headers)
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['data'] is None
        assert data['error'] == 'Invalid story' 