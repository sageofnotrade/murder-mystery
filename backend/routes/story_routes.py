from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.story_service import StoryService
from backend.services.supabase_service import get_supabase_client
from uuid import UUID
import logging
from utils.error_handlers import (
    APIError, ValidationError, ResourceNotFoundError,
    AuthenticationError, AuthorizationError
)

story_bp = Blueprint('story_routes', __name__)
logger = logging.getLogger(__name__)

def get_story_service():
    """Get a StoryService instance with the current Supabase client."""
    return StoryService(get_supabase_client())

@story_bp.route('/stories', methods=['GET'])
@jwt_required()
def get_stories():
    user_id = get_jwt_identity()
    story_service = get_story_service()
    try:
        stories = story_service.get_user_stories(user_id)
        return jsonify({'data': stories, 'error': None})
    except ResourceNotFoundError as e:
        logger.error(f'ERROR in get_stories: {e}')
        return jsonify({'data': None, 'error': str(e)}), 404
    except ValidationError as e:
        logger.error(f'ERROR in get_stories: {e}')
        return jsonify({'data': None, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f'ERROR in get_stories: {e}')
        return jsonify({'data': None, 'error': str(e)}), 500

@story_bp.route('/stories/<story_id>', methods=['GET'])
@jwt_required()
def get_story(story_id):
    user_id = get_jwt_identity()
    story_service = get_story_service()
    try:
        story = story_service.get_story_sync(story_id, user_id)
        return jsonify({'data': story, 'error': None})
    except ResourceNotFoundError as e:
        logger.error(f'ERROR in get_story: {e}')
        return jsonify({'data': None, 'error': str(e)}), 404
    except ValidationError as e:
        logger.error(f'ERROR in get_story: {e}')
        return jsonify({'data': None, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f'ERROR in get_story: {e}')
        return jsonify({'data': None, 'error': str(e)}), 500

@story_bp.route('/stories', methods=['POST'])
@jwt_required()
def create_story():
    user_id = get_jwt_identity()
    story_service = get_story_service()
    try:
        data = request.get_json()
        story = story_service.create_story_sync(user_id, data)
        return jsonify({'data': story, 'error': None}), 201
    except ResourceNotFoundError as e:
        logger.error(f'ERROR in create_story: {e}')
        return jsonify({'data': None, 'error': str(e)}), 404
    except ValidationError as e:
        logger.error(f'ERROR in create_story: {e}')
        return jsonify({'data': None, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f'ERROR in create_story: {e}')
        return jsonify({'data': None, 'error': str(e)}), 500

@story_bp.route('/stories/<story_id>/progress', methods=['GET'])
@jwt_required()
def get_story_progress(story_id):
    """Get the progress of a story."""
    user_id = get_jwt_identity()
    story_service = get_story_service()
    try:
        progress = story_service.get_story_progress_sync(story_id, user_id)
        return jsonify(progress)
    except ResourceNotFoundError as e:
        logger.error(f'ERROR in get_story_progress: {e}')
        return jsonify({'error': str(e)}), 404
    except ValidationError as e:
        logger.error(f'ERROR in get_story_progress: {e}')
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f'ERROR in get_story_progress: {e}')
        return jsonify({'error': str(e)}), 500

@story_bp.route('/stories/<story_id>/actions', methods=['POST'])
@jwt_required()
def perform_action(story_id):
    user_id = get_jwt_identity()
    story_service = get_story_service()
    try:
        data = request.get_json()
        result = story_service.perform_action_sync(story_id, user_id, data)
        return jsonify({'data': result, 'error': None})
    except ResourceNotFoundError as e:
        logger.error(f'ERROR in perform_action: {e}')
        return jsonify({'data': None, 'error': str(e)}), 404
    except ValidationError as e:
        logger.error(f'ERROR in perform_action: {e}')
        return jsonify({'data': None, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f'ERROR in perform_action: {e}')
        return jsonify({'data': None, 'error': str(e)}), 500

@story_bp.route('/stories/<story_id>/choices', methods=['POST'])
@jwt_required()
def make_choice(story_id):
    user_id = get_jwt_identity()
    story_service = get_story_service()
    try:
        data = request.get_json()
        result = story_service.make_choice_sync(story_id, user_id, data)
        return jsonify({'data': result, 'error': None})
    except ResourceNotFoundError as e:
        logger.error(f'ERROR in make_choice: {e}')
        return jsonify({'data': None, 'error': str(e)}), 404
    except ValidationError as e:
        logger.error(f'ERROR in make_choice: {e}')
        return jsonify({'data': None, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f'ERROR in make_choice: {e}')
        return jsonify({'data': None, 'error': str(e)}), 500 