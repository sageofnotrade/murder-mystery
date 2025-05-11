from flask import Blueprint, request, jsonify
import os
from supabase import create_client

users_bp = Blueprint('users', __name__)

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(supabase_url, supabase_key)

@users_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get the user's profile."""
    try:
        # Get the user ID from the request
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'No user ID provided'}), 400
        
        # Get the user's profile from Supabase
        response = supabase.table('profiles').select('*').eq('user_id', user_id).execute()
        
        if not response.data:
            return jsonify({'error': 'User profile not found'}), 404
        
        return jsonify(response.data[0])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/profile', methods=['POST'])
def create_profile():
    """Create or update the user's profile."""
    try:
        # Get the data from the request
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'No user ID provided'}), 400
        
        # Check if the profile already exists
        response = supabase.table('profiles').select('*').eq('user_id', user_id).execute()
        
        if response.data:
            # Update the existing profile
            updated = supabase.table('profiles').update(data).eq('user_id', user_id).execute()
            return jsonify(updated.data[0])
        else:
            # Create a new profile
            created = supabase.table('profiles').insert(data).execute()
            return jsonify(created.data[0]), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
