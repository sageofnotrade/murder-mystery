"""
Integration tests for board state sync (frontend-backend).
Covers happy path, edge, and failure cases.
"""
import pytest
from unittest.mock import patch
from backend.app import create_app
from backend.tests.mocks.redis_mock import MockRedisClient
from flask_jwt_extended import create_access_token

@pytest.fixture(scope="module")
def app():
    config = {
        "TESTING": True,
        "JWT_SECRET_KEY": "test",
        "JWT_TOKEN_LOCATION": ["headers"],
        "JWT_ACCESS_TOKEN_EXPIRES": False,
        "JWT_HEADER_NAME": "Authorization",
        "JWT_HEADER_TYPE": "Bearer",
        # Add any other JWT settings your app expects
    }
    with patch("backend.routes.board_state_routes.redis_client", new_callable=lambda: MockRedisClient()):
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

def test_board_state_sync_happy_path(client, auth_headers):
    board_state = {
        'elements': {},
        'connections': {},
        'notes': {},
        'layout': {},
        'last_update': '2024-06-01T12:00:00Z'
    }
    resp = client.post('/api/board/test-mystery/sync', json={'board_state': board_state}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json['status'] == 'ok'
    assert resp.json['board_state'] == board_state

def test_board_state_sync_missing_board_state(client, auth_headers):
    resp = client.post('/api/board/test-mystery/sync', json={}, headers=auth_headers)
    assert resp.status_code == 400
    assert 'error' in resp.json

def test_board_state_sync_invalid_board_state(client, auth_headers):
    bad_state = {'foo': 'bar'}
    resp = client.post('/api/board/test-mystery/sync', json={'board_state': bad_state}, headers=auth_headers)
    assert resp.status_code == 400
    assert 'error' in resp.json
