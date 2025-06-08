from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.story_service import StoryService
from backend.services.supabase_service import get_supabase_client
from uuid import UUID
from backend.agents.models.story_models import StoryState

story_bp = Blueprint('story_routes', __name__)

def get_story_service():
    """Get a StoryService instance with the current Supabase client."""
    return StoryService(get_supabase_client())

@story_bp.route('/stories', methods=['GET'])
@jwt_required()
def get_stories():
    print('DEBUG: Entered get_stories route')
    user_id = get_jwt_identity()
    print(f'DEBUG: user_id={user_id}')
    story_service = get_story_service()
    try:
        stories = story_service.get_user_stories(user_id)
        print(f'DEBUG: stories={stories}')
        return jsonify(stories)
    except Exception as e:
        if 'not found' in str(e).lower() or isinstance(e, ValueError):
            return jsonify({'error': str(e)}), 404
        print(f'ERROR in get_stories: {e}')
        return jsonify({'error': str(e)}), 500

@story_bp.route('/stories/<story_id>', methods=['GET'])
@jwt_required()
def get_story(story_id):
    print('DEBUG: Entered get_story route')
    user_id = get_jwt_identity()
    print(f'DEBUG: user_id={user_id}, story_id={story_id}')
    story_service = get_story_service()
    try:
        story = story_service.get_story_sync(story_id, user_id)
        print(f'DEBUG: story={story}')
        return jsonify(story)
    except Exception as e:
        if 'not found' in str(e).lower() or isinstance(e, ValueError):
            return jsonify({'error': str(e)}), 404
        print(f'ERROR in get_story: {e}')
        return jsonify({'error': str(e)}), 500

@story_bp.route('/stories', methods=['POST'])
@jwt_required()
def create_story():
    print('DEBUG: Entered create_story route')
    user_id = get_jwt_identity()
    print(f'DEBUG: user_id={user_id}')
    story_service = get_story_service()
    try:
        data = request.get_json()
        print(f'DEBUG: request data={data}')
        story = story_service.create_story_sync(user_id, data)
        print(f'DEBUG: created story={story}')
        return jsonify(story), 201
    except Exception as e:
        if 'not found' in str(e).lower() or isinstance(e, ValueError):
            return jsonify({'error': str(e)}), 404
        print(f'ERROR in create_story: {e}')
        return jsonify({'error': str(e)}), 500

@story_bp.route('/stories/<story_id>/progress', methods=['GET'])
@jwt_required()
def get_story_progress(story_id):
    """Get the progress of a story."""
    user_id = get_jwt_identity()
    story_service = get_story_service()
    try:
        progress = story_service.get_story_progress_sync(story_id, user_id)
        return jsonify(progress)
    except Exception as e:
        if 'not found' in str(e).lower() or isinstance(e, ValueError):
            return jsonify({'error': str(e)}), 404
        return jsonify({'error': str(e)}), 500

@story_bp.route('/stories/<story_id>/actions', methods=['POST'])
@jwt_required()
def perform_action(story_id):
    """Perform an action in the story."""
    user_id = get_jwt_identity()
    story_service = get_story_service()
    try:
        data = request.get_json()
        result = story_service.perform_action_sync(story_id, user_id, data)
        return jsonify(result)
    except Exception as e:
        if 'not found' in str(e).lower() or isinstance(e, ValueError):
            return jsonify({'error': str(e)}), 404
        return jsonify({'error': str(e)}), 500

@story_bp.route('/stories/<story_id>/choices', methods=['POST'])
@jwt_required()
def make_choice(story_id):
    """Make a choice in the story."""
    user_id = get_jwt_identity()
    story_service = get_story_service()
    try:
        data = request.get_json()
        result = story_service.make_choice_sync(story_id, user_id, data)
        return jsonify(result)
    except Exception as e:
        if 'not found' in str(e).lower() or isinstance(e, ValueError):
            return jsonify({'error': str(e)}), 404
        return jsonify({'error': str(e)}), 500

@story_bp.route('/stories/<story_id>/save', methods=['POST'])
@jwt_required()
def save_story(story_id):
    """Save the current state of a story."""
    user_id = get_jwt_identity()
    story_service = get_story_service()
    try:
        data = request.get_json()
        # Validate and construct StoryState from data
        story = StoryState(**data)
        story.id = story_id  # Ensure the ID matches the URL
        story_service.save_story_state_sync(story, user_id)  # Use sync version for test compatibility
        return jsonify({'message': 'Story state saved successfully.'}), 200
    except Exception as e:
        if 'not found' in str(e).lower() or isinstance(e, ValueError):
            return jsonify({'error': str(e)}), 404
        return jsonify({'error': str(e)}), 500 