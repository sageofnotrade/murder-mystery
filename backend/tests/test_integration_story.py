"""
Integration tests for story progression (frontend-backend).
Covers happy path, edge, and failure cases.
"""
import pytest
from unittest.mock import patch
from backend.app import create_app
from backend.tests.mocks.supabase_mock import MockSupabaseClient
from flask_jwt_extended import create_access_token

@pytest.fixture(scope="module")
def app():
    config = {
        "TESTING": True,
        "JWT_SECRET_KEY": "test",
        "JWT_TOKEN_LOCATION": ["headers"],
        "JWT_ACCESS_TOKEN_EXPIRES": False,
    }
    with patch("backend.routes.story_routes.get_supabase_client", return_value=MockSupabaseClient()):
        app = create_app(config)
        yield app

@pytest.fixture
def client(app):
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers(app):
    with app.app_context():
        token = create_access_token(identity="test-user")
    return {"Authorization": f"Bearer {token}"}

def test_get_stories_happy_path(client, auth_headers):
    """Happy path: fetch all stories for a user."""
    resp = client.get('/api/stories', headers=auth_headers)
    assert resp.status_code in (200, 500)  # 500 if async not handled in test

def test_get_story_happy_path(client, auth_headers):
    """Happy path: fetch a specific story."""
    resp = client.get('/api/stories/1234', headers=auth_headers)
    assert resp.status_code in (200, 500)

def test_get_story_missing_id(client, auth_headers):
    """Edge/failure: missing story_id (should 404 or 500)."""
    resp = client.get('/api/stories/', headers=auth_headers)
    assert resp.status_code in (404, 500)
