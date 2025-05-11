import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
    REDIS_URL = os.getenv('REDIS_REST_URL')
    REDIS_TOKEN = os.getenv('REDIS_REST_TOKEN')
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    # Use test databases/services here

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    # Add production-specific settings here

# Dictionary with different configuration environments
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Return the appropriate configuration object based on the environment."""
    env = os.getenv('FLASK_ENV', 'default')
    return config.get(env, config['default'])
