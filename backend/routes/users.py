from flask import Blueprint, request, jsonify
import os
from supabase import create_client
import logging
from flask_jwt_extended import jwt_required, get_jwt_identity

users_bp = Blueprint('users', __name__)

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(supabase_url, supabase_key)

logger = logging.getLogger(__name__)

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
        logger.error(f'ERROR in get_profile: {e}')
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
        logger.error(f'ERROR in create_profile: {e}')
        return jsonify({'error': str(e)}), 500

@users_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    user_id = get_jwt_identity()
    users_service = get_users_service()
    try:
        users = users_service.get_users(user_id)
        return jsonify({'data': users, 'error': None})
    except Exception as e:
        logger.error(f'ERROR in get_users: {e}')
        if 'not found' in str(e).lower() or isinstance(e, ValueError):
            return jsonify({'data': None, 'error': str(e)}), 404
        return jsonify({'data': None, 'error': str(e)}), 500

@users_bp.route('/users/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current_user_id = get_jwt_identity()
    users_service = get_users_service()
    try:
        user = users_service.get_user(user_id, current_user_id)
        return jsonify({'data': user, 'error': None})
    except Exception as e:
        logger.error(f'ERROR in get_user: {e}')
        if 'not found' in str(e).lower() or isinstance(e, ValueError):
            return jsonify({'data': None, 'error': str(e)}), 404
        return jsonify({'data': None, 'error': str(e)}), 500

@users_bp.route('/users/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user_id = get_jwt_identity()
    users_service = get_users_service()
    try:
        data = request.get_json()
        user = users_service.update_user(user_id, current_user_id, data)
        return jsonify({'data': user, 'error': None})
    except Exception as e:
        logger.error(f'ERROR in update_user: {e}')
        if 'not found' in str(e).lower() or isinstance(e, ValueError):
            return jsonify({'data': None, 'error': str(e)}), 404
        return jsonify({'data': None, 'error': str(e)}), 500
