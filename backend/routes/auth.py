from flask import Blueprint, jsonify, request
from supabase import create_client, Client
import os
from backend.config import get_config
from werkzeug.exceptions import HTTPException
import re

auth_bp = Blueprint('auth', __name__)

# Get configuration
config = get_config()

# Initialize Supabase client
supabase: Client = create_client(
    config.SUPABASE_URL,
    config.SUPABASE_KEY
)

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password):
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

@auth_bp.before_request
def check_content_type():
    """Check if the request has the correct content type."""
    if request.method in ['POST', 'PUT']:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 415

@auth_bp.errorhandler(Exception)
def handle_error(error):
    """Global error handler for the auth blueprint."""
    if isinstance(error, HTTPException):
        response = {
            'error': error.description,
            'status_code': error.code
        }
        return jsonify(response), error.code
    
    # Handle Supabase specific errors
    if 'Invalid login credentials' in str(error):
        return jsonify({'error': 'Invalid email or password'}), 401
    if 'User already registered' in str(error):
        return jsonify({'error': 'Email already registered'}), 409
    
    # Handle unexpected errors
    return jsonify({'error': 'An unexpected error occurred'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
        
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
    
    return jsonify({
        'user': response.user,
        'session': response.session
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
        
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
        
    is_valid, message = validate_password(password)
    if not is_valid:
        return jsonify({'error': message}), 400
    
    response = supabase.auth.sign_up({
        "email": email,
        "password": password
    })
    
    return jsonify({
        'message': 'Registration successful',
        'user': response.user
    }), 201

@auth_bp.route('/logout', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
        
    token = auth_header.split(' ')[1]
    response = supabase.auth.sign_out()
    
    return jsonify({'message': 'Successfully logged out'}), 200

@auth_bp.route('/validate', methods=['POST'])
def validate_token():
    """Validate a JWT token from Supabase."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
        
    token = auth_header.split(' ')[1]
    user = supabase.auth.get_user(token)
    
    return jsonify({
        'valid': True,
        'user': {
            'id': user.user.id,
            'email': user.user.email
        }
    }), 200
