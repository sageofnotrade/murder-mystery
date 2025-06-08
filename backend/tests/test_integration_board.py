# NOTE: Uses global app/client fixtures from conftest.py. Do not import create_app or define app/client fixtures here.
"""
Integration tests for board state sync (frontend-backend).
Covers happy path, edge, and failure cases.
"""
import pytest
from unittest.mock import patch
from backend.tests.mocks.redis_mock import MockRedisClient
from flask_jwt_extended import create_access_token

# Patch redis_client in backend.routes.board_state_routes for all tests in this file
redis_patch = patch('backend.routes.board_state_routes.redis_client', new=MockRedisClient())
redis_patch.start()

@pytest.fixture
def auth_headers(app):
    with app.app_context():
        token = create_access_token(identity="test-user")
    return {"Authorization": f"Bearer {token}"}

def test_board_state_sync_happy_path(client, auth_headers):
    client, _ = client
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
    client, _ = client
    resp = client.post('/api/board/test-mystery/sync', json={}, headers=auth_headers)
    assert resp.status_code == 400
    assert 'error' in resp.json

def test_board_state_sync_invalid_board_state(client, auth_headers):
    client, _ = client
    bad_state = {'foo': 'bar'}
    resp = client.post('/api/board/test-mystery/sync', json={'board_state': bad_state}, headers=auth_headers)
    assert resp.status_code == 400
    assert 'error' in resp.json
