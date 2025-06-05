import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from flask import Flask
from backend.app import app as flask_app
from backend.tests.mocks.supabase_mock import MockSupabaseClient
from backend.tests.mocks.redis_mock import MockRedisClient

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

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
    with flask_app.app_context():
        yield flask_app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

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