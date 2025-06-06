from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from backend.config import get_config
from flask_jwt_extended import JWTManager
from utils.error_handlers import (
    handle_api_error, handle_validation_error, handle_general_error,
    APIError, ValidationError
)
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Load environment variables
load_dotenv()

# Import routes
from backend.routes.auth import auth_bp
from backend.routes.template_routes import template_bp
from backend.routes.story_routes import story_bp
from backend.routes.clue_routes import clue_bp
from backend.routes.suspect_routes import suspect_bp
from backend.routes.user_progress_routes import user_progress_bp
from backend.routes.board_state_routes import board_state_bp
# from backend.routes.users import users_bp
# from backend.routes.mysteries import mysteries_bp
# from backend.routes.board import board_bp

def create_app(config_overrides=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure logging
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Murthra startup')
    
    # Get configuration
    config = get_config()

    # Configure app
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['SUPABASE_URL'] = config.SUPABASE_URL
    app.config['SUPABASE_KEY'] = config.SUPABASE_KEY
    app.config['REDIS_URL'] = config.REDIS_URL
    app.config['REDIS_TOKEN'] = config.REDIS_TOKEN

    # Apply any overrides (for testing)
    if config_overrides:
        app.config.update(config_overrides)

    # Initialize extensions
    CORS(app)
    jwt = JWTManager(app)
    
    # Register error handlers
    app.register_error_handler(APIError, handle_api_error)
    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(Exception, handle_general_error)
    
    # Add response processor to ensure consistent response format
    @app.after_request
    def after_request(response):
        if response.is_json:
            data = response.get_json()
            if 'data' not in data:
                # Wrap non-error responses in the expected format
                response.set_data(jsonify({
                    'data': data,
                    'error': None,
                    'status_code': response.status_code,
                    'timestamp': datetime.utcnow().isoformat()
                }).get_data())
        return response
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(template_bp, url_prefix='/api')
    app.register_blueprint(story_bp, url_prefix='/api')
    app.register_blueprint(clue_bp, url_prefix='/api')
    app.register_blueprint(suspect_bp, url_prefix='/api')
    app.register_blueprint(user_progress_bp, url_prefix='/api')
    app.register_blueprint(board_state_bp, url_prefix='/api')
    # app.register_blueprint(users_bp, url_prefix='/api/users')
    # app.register_blueprint(mysteries_bp, url_prefix='/api/mysteries')
    # app.register_blueprint(board_bp, url_prefix='/api/board')

    @app.route('/')
    def index():
        return jsonify({
            'message': 'Welcome to the Murþrą API',
            'status': 'online',
            'version': '0.1.0'
        })

    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'services': {
                'supabase': app.config.get('SUPABASE_URL') is not None,
                'redis': app.config.get('REDIS_URL') is not None
            }
        })

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
