from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.story_service import StoryService
from backend.services.supabase_service import get_supabase_client

story_bp = Blueprint('story_routes', __name__)

def get_story_service():
    """Get a StoryService instance with the current Supabase client."""
    return StoryService(get_supabase_client())

@story_bp.route('/api/stories', methods=['GET'])
@jwt_required()
async def get_stories():
    """Get all stories for the current user."""
    user_id = get_jwt_identity()
    story_service = get_story_service()
    
    try:
        stories = await story_service.get_user_stories(user_id)
        return jsonify(stories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@story_bp.route('/api/stories/<story_id>', methods=['GET'])
@jwt_required()
async def get_story(story_id):
    """Get a specific story."""
    user_id = get_jwt_identity()
    story_service = get_story_service()
    
    try:
        story = await story_service.get_story(story_id, user_id)
        return jsonify(story)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@story_bp.route('/api/stories', methods=['POST'])
@jwt_required()
async def create_story():
    """Create a new story."""
    user_id = get_jwt_identity()
    story_service = get_story_service()
    
    try:
        data = request.get_json()
        story = await story_service.create_story(user_id, data)
        return jsonify(story), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@story_bp.route('/api/stories/<story_id>/progress', methods=['GET'])
@jwt_required()
async def get_story_progress(story_id):
    """Get the progress of a story."""
    user_id = get_jwt_identity()
    story_service = get_story_service()
    
    try:
        progress = await story_service.get_story_progress(story_id, user_id)
        return jsonify(progress)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@story_bp.route('/api/stories/<story_id>/actions', methods=['POST'])
@jwt_required()
async def perform_action(story_id):
    """Perform an action in the story."""
    user_id = get_jwt_identity()
    story_service = get_story_service()
    
    try:
        data = request.get_json()
        result = await story_service.perform_action(story_id, user_id, data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@story_bp.route('/api/stories/<story_id>/choices', methods=['POST'])
@jwt_required()
async def make_choice(story_id):
    """Make a choice in the story."""
    user_id = get_jwt_identity()
    story_service = get_story_service()
    
    try:
        data = request.get_json()
        result = await story_service.make_choice(story_id, user_id, data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500 