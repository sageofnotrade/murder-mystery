import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from flask import Flask, Response
from backend.tests.mocks.supabase_mock import MockSupabaseClient
from backend.tests.mocks.redis_mock import MockRedisClient
import sys
import types

# Configure pytest-asyncio
# pytest_plugins = ('pytest_asyncio',)  # Moved to project root conftest.py

def pytest_configure(config):
    # Patch Supabase client at the module level
    patch('supabase._sync.client.create_client', return_value=MagicMock()).start()
    # Patch Redis client at the module level
    patch('redis.Redis', return_value=MagicMock()).start()
    config.option.asyncio_mode = "auto"

# Set test environment variables
@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
    os.environ['SUPABASE_KEY'] = 'test-key'
    os.environ['REDIS_HOST'] = 'localhost'
    os.environ['REDIS_PORT'] = '6379'
    os.environ['REDIS_DB'] = '0'
    yield
    # Clean up after tests
    os.environ.pop('FLASK_ENV', None)
    os.environ.pop('SUPABASE_URL', None)
    os.environ.pop('SUPABASE_KEY', None)
    os.environ.pop('REDIS_HOST', None)
    os.environ.pop('REDIS_PORT', None)
    os.environ.pop('REDIS_DB', None)

@pytest.fixture(autouse=True)
def patch_supabase_create_client():
    with patch('supabase._sync.client.create_client', return_value=MagicMock()):
        yield 

@pytest.fixture
def app():
    """Provide the Flask app instance for testing."""
    from unittest.mock import patch
    with patch('backend.routes.user_progress_routes.UserProgressService') as mock_service, \
         patch('backend.routes.user_progress_routes.jwt_required', lambda f: (print('jwt_required patched'), f)[1]), \
         patch('backend.routes.user_progress_routes.get_jwt_identity', lambda: 'user-123'):
        from backend.app import create_app
        app = create_app()
        with app.app_context():
            print('\nREGISTERED ROUTES:')
            for rule in app.url_map.iter_rules():
                print(rule)
            yield app

@pytest.fixture
def mock_service():
    """Provide the patched mock service for testing."""
    with patch('backend.routes.user_progress_routes.UserProgressService') as mock_service:
        yield mock_service

@pytest.fixture
def client(app, mock_service):
    """A test client for the app, and the mock service."""
    return app.test_client(), mock_service

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def mock_supabase():
    """Create a mock Supabase client."""
    return MockSupabaseClient()

@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    return MockRedisClient()

@pytest.fixture
def auth_headers():
    """Generate auth headers for testing protected endpoints."""
    return {
        'Authorization': 'Bearer mock-jwt-token'
    }

@pytest.fixture(autouse=True)
def add_json_property_to_response(monkeypatch):
    def json_property(self):
        from flask import json
        return json.loads(self.get_data(as_text=True))
    monkeypatch.setattr(Response, "json", property(json_property)) 