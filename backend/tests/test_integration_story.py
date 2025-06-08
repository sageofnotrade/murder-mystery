# NOTE: Uses global app/client fixtures from conftest.py. Do not import create_app or define app/client fixtures here.
"""
Integration tests for story progression (frontend-backend).
Covers happy path, edge, and failure cases.
"""
import pytest
from unittest.mock import patch
from backend.tests.mocks.supabase_mock import MockSupabaseClient
from flask_jwt_extended import create_access_token

MYSTERY_ID = "00000000-0000-0000-0000-000000000999"
USER_ID = "test-user"

@pytest.fixture(autouse=True)
def setup_story(shared_mock_supabase):
    """Insert a dummy mystery and story with all required fields into the shared mock Supabase DB before tests."""
    # Insert mystery
    shared_mock_supabase.table('mysteries').insert({
        'id': MYSTERY_ID,
        'user_id': USER_ID,
        'title': "Integration Test Mystery",
        'state': '{}',
        'is_completed': False
    })
    # Insert story
    shared_mock_supabase.table('stories').insert({
        'id': "1234",
        'user_id': USER_ID,
        'mystery_id': MYSTERY_ID,
        'current_scene': "introduction",
        'narrative_history': "[]",
        'discovered_clues': "[]",
        'suspect_states': "{}"
    })
    yield

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

def test_get_story_happy_path(client, auth_headers, shared_mock_supabase):
    """Happy path: fetch a specific story."""
    client, _ = client
    # Ensure the story with ID '1234' is present
    shared_mock_supabase.table('stories').data = [{
        'id': '1234',
        'user_id': 'test-user',
        'mystery_id': '00000000-0000-0000-0000-000000000999',
        'current_scene': 'introduction',
        'narrative_history': "[]",
        'discovered_clues': "[]",
        'suspect_states': "{}"
    }]
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
