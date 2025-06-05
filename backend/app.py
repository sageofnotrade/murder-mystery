from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from config import get_config

# Load environment variables
load_dotenv()

def create_app(test_config=None):
    """Create and configure the Flask application."""
    # Create Flask app
    app = Flask(__name__)
    CORS(app)

    # Get configuration
    if test_config is None:
        config = get_config()
        app.config['SECRET_KEY'] = config.SECRET_KEY
        app.config['SUPABASE_URL'] = config.SUPABASE_URL
        app.config['SUPABASE_KEY'] = config.SUPABASE_KEY
        app.config['REDIS_URL'] = config.REDIS_URL
        app.config['REDIS_TOKEN'] = config.REDIS_TOKEN
    else:
        # Override with test configuration
        app.config.update(test_config)

    # Import routes
    from routes.auth import auth_bp
    from routes.template_routes import template_bp
    from routes.story_routes import story_bp
    from routes.clue_routes import clue_bp
    from routes.suspect_routes import suspect_bp
    from routes.user_progress_routes import user_progress_bp
    # from routes.users import users_bp
    # from routes.mysteries import mysteries_bp
    # from routes.board import board_bp

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(template_bp, url_prefix='/api/templates')
    app.register_blueprint(story_bp, url_prefix='/api')
    app.register_blueprint(clue_bp, url_prefix='/api')
    app.register_blueprint(suspect_bp, url_prefix='/api')
    app.register_blueprint(user_progress_bp, url_prefix='/api')
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

# Create app instance for direct execution
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
