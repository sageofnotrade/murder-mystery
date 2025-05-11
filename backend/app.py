from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routes (to be created later)
# from routes.auth import auth_bp
# from routes.users import users_bp
# from routes.mysteries import mysteries_bp
# from routes.stories import stories_bp
# from routes.clues import clues_bp
# from routes.board import board_bp

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configure app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SUPABASE_URL'] = os.getenv('SUPABASE_URL')
app.config['SUPABASE_KEY'] = os.getenv('SUPABASE_SERVICE_KEY')
app.config['REDIS_URL'] = os.getenv('REDIS_REST_URL')
app.config['REDIS_TOKEN'] = os.getenv('REDIS_REST_TOKEN')

# Register blueprints (to be uncommented later)
# app.register_blueprint(auth_bp, url_prefix='/api/auth')
# app.register_blueprint(users_bp, url_prefix='/api/users')
# app.register_blueprint(mysteries_bp, url_prefix='/api/mysteries')
# app.register_blueprint(stories_bp, url_prefix='/api/stories')
# app.register_blueprint(clues_bp, url_prefix='/api/clues')
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
            'supabase': os.getenv('SUPABASE_URL') is not None,
            'redis': os.getenv('REDIS_REST_URL') is not None
        }
    })

if __name__ == '__main__':
    app.run(debug=True)
