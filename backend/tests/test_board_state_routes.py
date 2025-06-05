"""
Unit tests for board state synchronization API (BE-008).
Covers expected, edge, and failure cases.
"""
import json
import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from backend.app import create_app

@pytest.fixture(scope="module")
def app():
    return create_app({'TESTING': True})

@pytest.fixture
def client(app):
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_header():
    # Simulate a user with id 'test-user'
    token = create_access_token(identity='test-user')
    return {'Authorization': f'Bearer {token}'}

def test_get_board_state_not_found(client, auth_header):
    resp = client.get('/api/board/test-mystery', headers=auth_header)
    assert resp.status_code == 404
    assert resp.json['error'] == 'Board state not found'

def test_sync_and_get_board_state(client, auth_header):
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
                      headers=auth_header,
                      json={'board_state': board_state})
    assert resp.status_code == 200
    assert resp.json['status'] == 'ok'
    # Get (GET)
    resp2 = client.get('/api/board/test-mystery', headers=auth_header)
    assert resp2.status_code == 200
    assert resp2.json['last_update'] == '2024-06-01T12:00:00Z'

def test_sync_board_state_invalid_payload(client, auth_header):
    # Failure: missing board_state
    resp = client.post('/api/board/test-mystery/sync',
                      headers=auth_header,
                      json={})
    assert resp.status_code == 400
    assert 'Missing board_state' in resp.json['error']
    # Failure: invalid board_state structure
    resp2 = client.post('/api/board/test-mystery/sync',
                       headers=auth_header,
                       json={'board_state': {'bad': 'data'}})
    assert resp2.status_code == 400
    assert 'Invalid board_state' in resp2.json['error']
