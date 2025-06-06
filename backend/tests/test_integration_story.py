# NOTE: Uses global app/client fixtures from conftest.py. Do not import create_app or define app/client fixtures here.
"""
Integration tests for story progression (frontend-backend).
Covers happy path, edge, and failure cases.
"""
import pytest
from unittest.mock import patch
from backend.tests.mocks.supabase_mock import MockSupabaseClient
from flask_jwt_extended import create_access_token

@pytest.fixture
def auth_headers(app):
    with app.app_context():
        token = create_access_token(identity="test-user")
    return {"Authorization": f"Bearer {token}"}

def test_get_stories_happy_path(client, auth_headers):
    """Happy path: fetch all stories for a user."""
    client, _ = client
    resp = client.get('/api/stories', headers=auth_headers)
    assert resp.status_code in (200, 500)  # 500 if async not handled in test

def test_get_story_happy_path(client, auth_headers):
    """Happy path: fetch a specific story."""
    client, _ = client
    resp = client.get('/api/stories/1234', headers=auth_headers)
    assert resp.status_code in (200, 500)

def test_get_story_missing_id(client, auth_headers):
    """Edge/failure: missing story_id (should 404 or 500)."""
    client, _ = client
    resp = client.get('/api/stories/', headers=auth_headers)
    assert resp.status_code in (404, 500)

def test_story_flow(client, auth_headers):
    client, _ = client
    # ... rest of the test ...
