from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add the project root directory to Python path when running directly
if __name__ == '__main__':
    project_root = str(Path(__file__).parent.parent)
    if project_root not in sys.path:
        sys.path.append(project_root)

from backend.config import get_config

# Load environment variables
load_dotenv()

# Import routes
from backend.routes.auth import auth_bp
from backend.routes.template_routes import template_bp
from backend.routes.story_routes import story_bp
from backend.routes.clue_routes import clue_bp

# Create Flask app
app = Flask(__name__)
CORS(app)

# Get configuration
config = get_config()

# Configure app
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['SUPABASE_URL'] = config.SUPABASE_URL
app.config['SUPABASE_KEY'] = config.SUPABASE_KEY
app.config['REDIS_URL'] = config.REDIS_URL
app.config['REDIS_TOKEN'] = config.REDIS_TOKEN

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(template_bp, url_prefix='/api/templates')
app.register_blueprint(story_bp, url_prefix='/api')
app.register_blueprint(clue_bp, url_prefix='/api')
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
            'supabase': config.SUPABASE_URL is not None,
            'redis': config.REDIS_URL is not None
        }
    })

if __name__ == '__main__':
    app.run(debug=True)
