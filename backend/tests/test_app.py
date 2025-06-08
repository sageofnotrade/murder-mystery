# NOTE: Uses global app/client fixtures from conftest.py. Do not import create_app or define app/client fixtures here.
import pytest
import json

def test_index_endpoint(client):
    client, _ = client
    """Test the main index endpoint."""
    resp = client.get('/')
    assert resp.status_code == 200
    assert resp.json['message'] == 'Welcome to the Murþrą API'

def test_health_endpoint(client):
    client, _ = client
    """Test the health check endpoint."""
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.json['status'] == 'healthy'

def test_invalid_endpoint(client):
    client, _ = client
    """Test accessing an invalid endpoint."""
    resp = client.get('/api/invalid')
    assert resp.status_code == 404 