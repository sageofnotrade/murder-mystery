"""
Integration tests for authentication flows (frontend-backend).
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
    with patch("backend.routes.auth.supabase", new_callable=lambda: MockSupabaseClient()):
        app = create_app(config)
        yield app

@pytest.fixture
def client(app):
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_happy_path(client):
    """Happy path: login with valid credentials."""
    resp = client.post('/api/auth/login', json={"email": "test@example.com", "password": "Password123"})
    assert resp.status_code == 200
    assert 'user' in resp.json
    assert 'session' in resp.json

def test_login_missing_fields(client):
    """Edge/failure: login with missing fields."""
    resp = client.post('/api/auth/login', json={})
    assert resp.status_code == 400
    assert 'error' in resp.json

def test_register_happy_path(client):
    """Happy path: register with valid credentials."""
    resp = client.post('/api/auth/register', json={"email": "newuser@example.com", "password": "Password123"})
    assert resp.status_code in (201, 200)
    assert 'user' in resp.json or 'message' in resp.json

def test_register_invalid_email(client):
    """Edge/failure: register with invalid email."""
    resp = client.post('/api/auth/register', json={"email": "bademail", "password": "Password123"})
    assert resp.status_code == 400
    assert 'error' in resp.json
