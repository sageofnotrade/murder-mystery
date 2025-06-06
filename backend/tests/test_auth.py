# NOTE: Uses global app/client fixtures from conftest.py. Do not import create_app or define app/client fixtures here.
import pytest
import json

def test_register_missing_data(client):
    """Test registration with missing data."""
    client, _ = client
    response = client.post(
        '/api/auth/register',
        json={},
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'No data provided'

def test_register_invalid_email(client):
    """Test registration with invalid email format."""
    client, _ = client
    response = client.post(
        '/api/auth/register',
        json={
            'email': 'invalid-email',
            'password': 'Test123!'
        },
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Invalid email format'

def test_register_weak_password(client):
    """Test registration with weak password."""
    client, _ = client
    response = client.post(
        '/api/auth/register',
        json={
            'email': 'test@example.com',
            'password': 'weak'
        },
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Password must be at least 8 characters long' in data['error']

def test_login_missing_data(client):
    """Test login with missing data."""
    client, _ = client
    response = client.post(
        '/api/auth/login',
        json={},
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'No data provided'

def test_login_invalid_email(client):
    """Test login with invalid email format."""
    client, _ = client
    response = client.post(
        '/api/auth/login',
        json={
            'email': 'invalid-email',
            'password': 'Test123!'
        },
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Invalid email format'

def test_validate_token_missing_header(client):
    """Test token validation with missing Authorization header."""
    client, _ = client
    response = client.post(
        '/api/auth/validate',
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'No token provided'

def test_logout_missing_token(client):
    """Test logout with missing token."""
    client, _ = client
    response = client.post(
        '/api/auth/logout',
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'No token provided' 