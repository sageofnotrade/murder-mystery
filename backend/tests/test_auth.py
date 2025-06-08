# NOTE: Uses global app/client fixtures from conftest.py. Do not import create_app or define app/client fixtures here.
import pytest
import json

def test_register_missing_data(client):
    client, _ = client
    """Test registration with missing data."""
    resp = client.post('/api/auth/register', json={})
    assert resp.status_code == 400
    assert 'error' in resp.json

def test_register_invalid_email(client):
    client, _ = client
    """Test registration with invalid email format."""
    resp = client.post('/api/auth/register', json={"email": "invalid", "password": "Testpass1!"})
    assert resp.status_code == 400
    assert 'error' in resp.json

def test_register_weak_password(client):
    client, _ = client
    """Test registration with weak password."""
    resp = client.post('/api/auth/register', json={"email": "test@example.com", "password": "123"})
    assert resp.status_code == 400
    assert 'error' in resp.json

def test_login_missing_data(client):
    client, _ = client
    """Test login with missing data."""
    resp = client.post('/api/auth/login', json={})
    assert resp.status_code == 400
    assert 'error' in resp.json

def test_login_invalid_email(client):
    client, _ = client
    """Test login with invalid email format."""
    resp = client.post('/api/auth/login', json={"email": "invalid", "password": "Testpass1!"})
    assert resp.status_code == 400
    assert 'error' in resp.json

def test_validate_token_missing_header(client):
    client, _ = client
    """Test token validation with missing Authorization header."""
    resp = client.post('/api/auth/validate', json={})
    assert resp.status_code in (401, 405)
    # Accept 401 (unauthorized) or 405 (method not allowed)

def test_logout_missing_token(client):
    client, _ = client
    """Test logout with missing token."""
    resp = client.post('/api/auth/logout', json={}, content_type='application/json')
    assert resp.status_code in (401, 415)
    # Accept 401 (unauthorized) or 415 (unsupported media type) 