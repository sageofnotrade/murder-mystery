from flask import Blueprint, request, jsonify
from uuid import UUID
from backend.services.clue_service import ClueService
from supabase import create_client, Client
import os
from backend.agents.models.clue_models import ClueCreate, ClueConnection

clue_bp = Blueprint('clue', __name__)

def get_supabase_client():
    return create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )

def get_clue_service():
    return ClueService(get_supabase_client())

@clue_bp.route('/stories/<story_id>/clues', methods=['GET'])
async def get_story_clues(story_id: str):
    """Get all clues for a story."""
    try:
        clues = await get_clue_service().get_story_clues(str(story_id), 'test-user')
        return jsonify([clue.dict() if hasattr(clue, 'dict') else clue for clue in clues]), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clue_bp.route('/stories/<story_id>/clues', methods=['POST'])
async def discover_clue(story_id: str):
    """Discover a new clue in the story."""
    try:
        data = request.get_json()
        required_fields = ['template_clue_id', 'discovery_method', 'discovery_location', 'type', 'description']
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields
            }), 400
        clue_data = ClueCreate(
            id=data['template_clue_id'],
            discovery_context=data['discovery_method'],
            location=data['discovery_location'],
            type=data['type'],
            description=data['description']
        )
        clue = await get_clue_service().discover_clue(str(story_id), 'test-user', clue_data)
        return jsonify(clue.dict() if hasattr(clue, 'dict') else clue), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clue_bp.route('/clues/<clue_id>/notes', methods=['PUT'])
async def update_clue_notes(clue_id: str):
    """Update notes for a discovered clue."""
    try:
        data = request.get_json()
        if 'notes' not in data:
            return jsonify({'error': 'Missing notes field'}), 400
        # Look up the clue to get its story_id
        clue = await get_clue_service().get_clue_details_by_id(str(clue_id))
        story_id = clue['story_id']
        updated_clue = await get_clue_service().update_clue_notes(story_id, str(clue_id), data['notes'], 'test-user')
        return jsonify(updated_clue.dict() if hasattr(updated_clue, 'dict') else updated_clue), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clue_bp.route('/clues/<clue_id>/connections', methods=['POST'])
async def add_clue_connection(clue_id: str):
    """Add a connection between two clues."""
    try:
        data = request.get_json()
        required_fields = ['connected_clue_id', 'connection_type', 'connection_details', 'story_id']
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields
            }), 400
        connection = ClueConnection(
            story_id=data['story_id'],
            source_clue_id=str(clue_id),
            target_clue_id=data['connected_clue_id'],
            relationship_type=data['connection_type'],
            description=data['connection_details'].get('reason', '')
        )
        clue_connection = await get_clue_service().add_clue_connection(data['story_id'], connection, 'test-user')
        return jsonify(clue_connection.dict() if hasattr(clue_connection, 'dict') else clue_connection), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clue_bp.route('/clues/<clue_id>/relevance', methods=['PUT'])
async def update_clue_relevance(clue_id: str):
    """Update the relevance score of a clue."""
    try:
        data = request.get_json()
        if 'relevance_score' not in data:
            return jsonify({'error': 'Missing relevance_score field'}), 400
        # Look up the clue to get its story_id
        clue = await get_clue_service().get_clue_details_by_id(str(clue_id))
        story_id = clue['story_id']
        updated_clue = await get_clue_service().update_clue_relevance(story_id, str(clue_id), float(data['relevance_score']), 'test-user')
        return jsonify(updated_clue.dict() if hasattr(updated_clue, 'dict') else updated_clue), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clue_bp.route('/clues/<clue_id>/connections', methods=['GET'])
async def get_clue_connections(clue_id: str):
    """Get all connections for a specific clue."""
    try:
        # Look up the clue to get its story_id
        clue = await get_clue_service().get_clue_details_by_id(str(clue_id))
        if not clue:
            return jsonify({'error': 'Clue not found'}), 404
        story_id = clue['story_id']
        connections = await get_clue_service().get_clue_connections(story_id, str(clue_id), 'test-user')
        if not connections:
            return jsonify({'error': 'No connections found'}), 404
        return jsonify([conn.dict() if hasattr(conn, 'dict') else conn for conn in connections]), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clue_bp.route('/clues/<clue_id>/red-herring', methods=['PUT'])
async def mark_clue_as_red_herring(clue_id: str):
    """Mark a clue as a red herring or not."""
    try:
        data = request.get_json()
        if 'is_red_herring' not in data:
            return jsonify({'error': 'Missing is_red_herring field'}), 400
        # Look up the clue to get its story_id
        clue = await get_clue_service().get_clue_details_by_id(str(clue_id))
        if not clue:
            return jsonify({'error': 'Clue not found'}), 404
        story_id = clue['story_id']
        updated_clue = await get_clue_service().mark_clue_as_red_herring(story_id, str(clue_id), 'test-user')
        return jsonify(updated_clue.dict() if hasattr(updated_clue, 'dict') else updated_clue), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500 