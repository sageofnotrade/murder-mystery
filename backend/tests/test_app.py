import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

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