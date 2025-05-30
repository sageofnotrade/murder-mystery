import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

def pytest_configure(config):
    # Patch Supabase client at the module level
    patch('supabase._sync.client.create_client', return_value=MagicMock()).start()
    # Patch Redis client at the module level
    patch('redis.Redis', return_value=MagicMock()).start()

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