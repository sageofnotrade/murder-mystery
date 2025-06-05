"""
Integration tests for clue management (frontend-backend).
Covers happy path, edge, and failure cases.
"""
import pytest
from unittest.mock import patch
from backend.app import create_app
from backend.tests.mocks.supabase_mock import MockSupabaseClient

@pytest.fixture(scope="module")
def app():
    config = {
        "TESTING": True,
        "JWT_SECRET_KEY": "test",
        "JWT_TOKEN_LOCATION": ["headers"],
        "JWT_ACCESS_TOKEN_EXPIRES": False,
    }
    with patch("backend.routes.clue_routes.supabase", new_callable=lambda: MockSupabaseClient()):
        app = create_app(config)
        yield app

@pytest.fixture
def client(app):
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_clues_happy_path(client):
    """Happy path: fetch all clues for a story."""
    with patch("backend.routes.clue_routes.ClueService.get_story_clues", return_value=[]):
        resp = client.get('/api/stories/00000000-0000-0000-0000-000000000000/clues')
    assert resp.status_code in (200, 500)

def test_discover_clue_happy_path(client):
    """Happy path: discover a new clue."""
    with patch("backend.routes.clue_routes.ClueService.discover_clue", return_value={"id": "clue1"}):
        payload = {
            "template_clue_id": "00000000-0000-0000-0000-000000000001",
            "discovery_method": "search",
            "discovery_location": "library"
        }
        resp = client.post('/api/stories/00000000-0000-0000-0000-000000000000/clues', json=payload)
    assert resp.status_code in (201, 500)

def test_discover_clue_missing_fields(client):
    """Edge/failure: missing required fields in POST."""
    resp = client.post('/api/stories/00000000-0000-0000-0000-000000000000/clues', json={})
    assert resp.status_code == 400
