from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.suspect_service import SuspectService
from backend.services.supabase_service import get_supabase_client
from backend.agents.suspect_agent import SuspectState, SuspectProfile
from pydantic import ValidationError
import logging
from werkzeug.exceptions import BadRequest

# Configure logging
logger = logging.getLogger(__name__)

suspect_bp = Blueprint('suspect_routes', __name__)

def get_suspect_service():
    """Get a SuspectService instance with the current Supabase client."""
    return SuspectService(get_supabase_client())

@suspect_bp.route('/suspects', methods=['GET'])
@jwt_required()
async def get_suspects():
    """Get all suspects for the current user/story."""
    user_id = get_jwt_identity()
    story_id = request.args.get('story_id')
    
    if not story_id:
        return jsonify({'error': 'story_id parameter is required'}), 400
    
    suspect_service = get_suspect_service()
    
    try:
        suspects = await suspect_service.get_story_suspects(story_id, user_id)
        return jsonify(suspects)
    except Exception as e:
        logger.error(f"Error getting suspects: {str(e)}")
        return jsonify({'error': str(e)}), 500

@suspect_bp.route('/suspects/<suspect_id>', methods=['GET'])
@jwt_required()
async def get_suspect(suspect_id):
    """Get a specific suspect profile."""
    user_id = get_jwt_identity()
    story_id = request.args.get('story_id')
    
    if not story_id:
        return jsonify({'error': 'story_id parameter is required'}), 400
    
    suspect_service = get_suspect_service()
    
    try:
        suspect = await suspect_service.get_suspect_profile(suspect_id, story_id, user_id)
        if not suspect:
            return jsonify({'error': 'Suspect not found'}), 404
        
        return jsonify(suspect)
    except Exception as e:
        logger.error(f"Error getting suspect {suspect_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@suspect_bp.route('/suspects', methods=['POST'])
@jwt_required()
async def create_suspect():
    """Create a new suspect."""
    user_id = get_jwt_identity()
    suspect_service = get_suspect_service()
    
    try:
        try:
            data = request.get_json(force=True, silent=True)
        except BadRequest:
            return jsonify({'error': 'Request body is required'}), 400
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        suspect = await suspect_service.create_suspect(user_id, data)
        return jsonify(suspect), 201
    except ValidationError as e:
        return jsonify({'error': 'Invalid suspect data', 'details': e.errors()}), 400
    except Exception as e:
        logger.error(f"Error creating suspect: {str(e)}")
        return jsonify({'error': str(e)}), 500

@suspect_bp.route('/suspects/<suspect_id>/dialogue', methods=['POST'])
@jwt_required()
async def post_dialogue(suspect_id):
    """Post dialogue and get suspect response."""
    user_id = get_jwt_identity()
    suspect_service = get_suspect_service()
    
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({'error': 'Question is required in request body'}), 400
        
        question = data['question']
        story_id = data.get('story_id')
        context = data.get('context', {})
        
        if not story_id:
            return jsonify({'error': 'story_id is required'}), 400
        
        # Verify user has access to this suspect/story
        suspect_profile = await suspect_service.get_suspect_profile(suspect_id, story_id, user_id)
        if not suspect_profile:
            return jsonify({'error': 'Suspect not found or access denied'}), 404
        
        # Generate dialogue response
        dialogue_result = await suspect_service.generate_dialogue(
            suspect_id, question, story_id, user_id, context
        )
        
        return jsonify(dialogue_result)
    except ValidationError as e:
        return jsonify({'error': 'Invalid request data', 'details': e.errors()}), 400
    except Exception as e:
        logger.error(f"Error posting dialogue to suspect {suspect_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@suspect_bp.route('/suspects/<suspect_id>/verify-alibi', methods=['POST'])
@jwt_required()
async def verify_alibi(suspect_id):
    """Verify suspect alibi."""
    user_id = get_jwt_identity()
    suspect_service = get_suspect_service()
    
    try:
        data = request.get_json()
        if not data or 'story_id' not in data:
            return jsonify({'error': 'story_id is required'}), 400
        
        story_id = data['story_id']
        alibi_details = data.get('alibi_details', {})
        evidence = data.get('evidence', [])
        
        # Verify user has access to this suspect/story
        suspect_profile = await suspect_service.get_suspect_profile(suspect_id, story_id, user_id)
        if not suspect_profile:
            return jsonify({'error': 'Suspect not found or access denied'}), 404
        
        # Verify alibi
        verification_result = await suspect_service.verify_alibi(
            suspect_id, story_id, user_id, alibi_details, evidence
        )
        
        return jsonify(verification_result)
    except ValidationError as e:
        return jsonify({'error': 'Invalid verification data', 'details': e.errors()}), 400
    except Exception as e:
        logger.error(f"Error verifying alibi for suspect {suspect_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@suspect_bp.route('/suspects/<suspect_id>/state', methods=['GET'])
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

@suspect_bp.route('/suspects/<suspect_id>/state', methods=['PUT'])
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

@suspect_bp.route('/suspects/<suspect_id>/motives', methods=['GET'])
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

@suspect_bp.route('/suspects/<suspect_id>/generate', methods=['POST'])
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