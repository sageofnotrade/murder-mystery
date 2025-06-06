from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.suspect_service import SuspectService
from services.supabase_service import get_supabase_client
from agents.suspect_agent import SuspectState, SuspectProfile
from utils.error_handlers import (
    APIError, ValidationError, ResourceNotFoundError,
    AuthenticationError, AuthorizationError
)
import logging

# Configure logging
logger = logging.getLogger(__name__)

suspect_bp = Blueprint('suspect_routes', __name__)

def get_suspect_service():
    """Get a SuspectService instance with the current Supabase client."""
    return SuspectService(get_supabase_client())

@suspect_bp.route('/suspects', methods=['GET'])
@jwt_required()
def get_suspects():
    """Get all suspects for a story."""
    try:
        story_id = request.args.get('story_id')
        if not story_id:
            raise ValidationError("story_id is required")
            
        user_id = get_jwt_identity()
        service = get_suspect_service()
        suspects = service.get_suspects(story_id, user_id)
        
        if not suspects:
            raise ResourceNotFoundError(f"No suspects found for story {story_id}")
            
        return jsonify(suspects)
        
    except APIError as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting suspects: {str(e)}")
        raise APIError("Failed to retrieve suspects")

@suspect_bp.route('/suspects/<suspect_id>', methods=['GET'])
@jwt_required()
def get_suspect(suspect_id):
    """Get a specific suspect's profile."""
    try:
        story_id = request.args.get('story_id')
        if not story_id:
            raise ValidationError("story_id is required")
            
        user_id = get_jwt_identity()
        service = get_suspect_service()
        suspect = service.get_suspect_profile(suspect_id, story_id, user_id)
        
        if not suspect:
            raise ResourceNotFoundError(f"Suspect {suspect_id} not found")
            
        return jsonify(suspect)
        
    except APIError as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting suspect {suspect_id}: {str(e)}")
        raise APIError("Failed to retrieve suspect profile")

@suspect_bp.route('/suspects/<suspect_id>/dialogue', methods=['POST'])
@jwt_required()
def generate_dialogue(suspect_id):
    """Generate dialogue with a suspect."""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")
            
        question = data.get('question')
        story_id = data.get('story_id')
        context = data.get('context', {})
        
        if not all([question, story_id]):
            raise ValidationError("question and story_id are required")
            
        user_id = get_jwt_identity()
        service = get_suspect_service()
        
        # Verify suspect exists
        suspect = service.get_suspect_profile(suspect_id, story_id, user_id)
        if not suspect:
            raise ResourceNotFoundError(f"Suspect {suspect_id} not found")
            
        response = service.generate_dialogue(suspect_id, question, story_id, user_id, context)
        return jsonify(response)
        
    except APIError as e:
        raise e
    except Exception as e:
        logger.error(f"Error generating dialogue for suspect {suspect_id}: {str(e)}")
        raise APIError("Failed to generate dialogue")

@suspect_bp.route('/suspects/<suspect_id>/verify-alibi', methods=['POST'])
@jwt_required()
def verify_alibi(suspect_id):
    """Verify a suspect's alibi."""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")
            
        story_id = data.get('story_id')
        alibi_details = data.get('alibi_details')
        evidence = data.get('evidence', [])
        
        if not all([story_id, alibi_details]):
            raise ValidationError("story_id and alibi_details are required")
            
        user_id = get_jwt_identity()
        service = get_suspect_service()
        
        # Verify suspect exists
        suspect = service.get_suspect_profile(suspect_id, story_id, user_id)
        if not suspect:
            raise ResourceNotFoundError(f"Suspect {suspect_id} not found")
            
        result = service.verify_alibi(suspect_id, story_id, user_id, alibi_details, evidence)
        return jsonify(result)
        
    except APIError as e:
        raise e
    except Exception as e:
        logger.error(f"Error verifying alibi for suspect {suspect_id}: {str(e)}")
        raise APIError("Failed to verify alibi")

@suspect_bp.route('/api/suspects/<suspect_id>/state', methods=['GET'])
@jwt_required()
async def get_suspect_state(suspect_id):
    """Get the current investigation state of a suspect."""
    user_id = get_jwt_identity()
    story_id = request.args.get('story_id')
    
    if not story_id:
        return jsonify({'error': 'story_id parameter is required'}), 400
    
    suspect_service = get_suspect_service()
    
    try:
        suspect_state = await suspect_service.get_suspect_state(suspect_id, story_id, user_id)
        if not suspect_state:
            return jsonify({'error': 'Suspect state not found'}), 404
        
        return jsonify(suspect_state)
    except Exception as e:
        logger.error(f"Error getting suspect state {suspect_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@suspect_bp.route('/api/suspects/<suspect_id>/state', methods=['PUT'])
@jwt_required()
async def update_suspect_state(suspect_id):
    """Update the investigation state of a suspect."""
    user_id = get_jwt_identity()
    suspect_service = get_suspect_service()
    
    try:
        data = request.get_json()
        if not data or 'story_id' not in data:
            return jsonify({'error': 'story_id is required'}), 400
        
        story_id = data['story_id']
        state_updates = data.get('state_updates', {})
        
        # Verify user has access to this suspect/story
        suspect_profile = await suspect_service.get_suspect_profile(suspect_id, story_id, user_id)
        if not suspect_profile:
            return jsonify({'error': 'Suspect not found or access denied'}), 404
        
        # Update suspect state
        updated_state = await suspect_service.update_suspect_state(
            suspect_id, story_id, user_id, state_updates
        )
        
        return jsonify(updated_state)
    except ValidationError as e:
        return jsonify({'error': 'Invalid state data', 'details': e.errors()}), 400
    except Exception as e:
        logger.error(f"Error updating suspect state {suspect_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@suspect_bp.route('/api/suspects/<suspect_id>/motives', methods=['GET'])
@jwt_required()
async def explore_motives(suspect_id):
    """Explore potential motives for a suspect."""
    user_id = get_jwt_identity()
    story_id = request.args.get('story_id')
    
    if not story_id:
        return jsonify({'error': 'story_id parameter is required'}), 400
    
    suspect_service = get_suspect_service()
    
    try:
        # Verify user has access to this suspect/story
        suspect_profile = await suspect_service.get_suspect_profile(suspect_id, story_id, user_id)
        if not suspect_profile:
            return jsonify({'error': 'Suspect not found or access denied'}), 404
        
        # Explore motives
        motives = await suspect_service.explore_motives(suspect_id, story_id, user_id)
        
        return jsonify(motives)
    except Exception as e:
        logger.error(f"Error exploring motives for suspect {suspect_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@suspect_bp.route('/api/suspects/<suspect_id>/generate', methods=['POST'])
@jwt_required()
async def generate_suspect_profile(suspect_id):
    """Generate or regenerate a suspect profile using AI."""
    user_id = get_jwt_identity()
    suspect_service = get_suspect_service()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        story_id = data.get('story_id')
        prompt = data.get('prompt', '')
        context = data.get('context', {})
        
        if not story_id:
            return jsonify({'error': 'story_id is required'}), 400
        
        # Generate suspect profile
        generated_profile = await suspect_service.generate_suspect_profile(
            suspect_id, story_id, user_id, prompt, context
        )
        
        return jsonify(generated_profile)
    except ValidationError as e:
        return jsonify({'error': 'Invalid generation data', 'details': e.errors()}), 400
    except Exception as e:
        logger.error(f"Error generating suspect profile {suspect_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500 