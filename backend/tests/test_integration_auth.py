"""
Integration tests for authentication flows (frontend-backend).
Covers happy path, edge, and failure cases.
"""
import pytest
from unittest.mock import patch
from backend.app import create_app
from backend.tests.mocks.supabase_mock import MockSupabaseClient

def test_login_happy_path(client):
    """Happy path: login with valid credentials."""
    client, _ = client
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
