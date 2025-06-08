# NOTE: Uses global app/client fixtures from conftest.py. Do not import create_app or define app/client fixtures here.
"""
Unit tests for board state synchronization API (BE-008).
Covers expected, edge, and failure cases.
"""
import json
import pytest
from flask_jwt_extended import create_access_token

@pytest.mark.usefixtures('auth_headers')
def test_get_board_state_not_found(client, auth_headers):
    client, _ = client
    resp = client.get('/api/board/test-mystery', headers=auth_headers)
    assert resp.status_code == 404
    assert resp.json['error'] == 'Board state not found'

def test_sync_and_get_board_state(client, auth_headers):
    client, _ = client
    # Happy path: sync then get
    board_state = {
        'elements': {},
        'connections': {},
        'notes': {},
        'layout': {},
        'last_update': '2024-06-01T12:00:00Z'
    }
    # Sync (POST)
    resp = client.post('/api/board/test-mystery/sync',
                      headers=auth_headers,
                      json={'board_state': board_state})
    assert resp.status_code == 200
    assert resp.json['status'] == 'ok'
    # Get (GET)
    resp2 = client.get('/api/board/test-mystery', headers=auth_headers)
    assert resp2.status_code == 200
    assert resp2.json['last_update'] == '2024-06-01T12:00:00Z'

def test_sync_board_state_invalid_payload(client, auth_headers):
    client, _ = client
    # Failure: missing board_state
    resp = client.post('/api/board/test-mystery/sync',
                      headers=auth_headers,
                      json={})
    assert resp.status_code == 400
    assert 'Missing board_state' in resp.json['error']
    # Failure: invalid board_state structure
    resp2 = client.post('/api/board/test-mystery/sync',
                       headers=auth_headers,
                       json={'board_state': {'bad': 'data'}})
    try:
        assert resp2.status_code == 400
        assert (
            'Invalid board_state' in resp2.json['error'] or
            'missing required keys' in resp2.json['error']
        )
    except AssertionError:
        print('DEBUG: status_code', resp2.status_code)
        print('DEBUG: json', resp2.json)
        raise
