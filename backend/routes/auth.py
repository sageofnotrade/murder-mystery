from flask import Blueprint, request, jsonify
import os
from supabase import create_client

auth_bp = Blueprint('auth', __name__)

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(supabase_url, supabase_key)

@auth_bp.route('/validate', methods=['POST'])
def validate_token():
    """Validate a JWT token from Supabase."""
    try:
        # Get the token from the request
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 400
        
        # Validate the token with Supabase
        # This is a simplified example - in a real app, you'd use proper JWT validation
        user = supabase.auth.get_user(token)
        
        return jsonify({
            'valid': True,
            'user': {
                'id': user.user.id,
                'email': user.user.email
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 401
