# NOTE: Uses global app/client fixtures from conftest.py. Do not import create_app or define app/client fixtures here.
import pytest
import json

def test_index_endpoint(client):
    """Test the main index endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert 'status' in data
    assert 'version' in data
    assert data['status'] == 'online'
    assert data['version'] == '0.1.0'

def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data
    assert 'services' in data
    assert data['status'] == 'healthy'
    assert isinstance(data['services'], dict)
    assert 'supabase' in data['services']
    assert 'redis' in data['services']

def test_invalid_endpoint(client):
    """Test accessing an invalid endpoint."""
    response = client.get('/invalid-endpoint')
    assert response.status_code == 404 