from flask import Blueprint, request, jsonify
from uuid import UUID
from backend.services.clue_service import ClueService
from supabase import create_client, Client
import os

clue_bp = Blueprint('clue', __name__)

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Initialize clue service
clue_service = ClueService(supabase)

@clue_bp.route('/stories/<story_id>/clues', methods=['GET'])
async def get_story_clues(story_id: str):
    """Get all clues for a story."""
    try:
        clues = await clue_service.get_story_clues(UUID(story_id))
        return jsonify(clues), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clue_bp.route('/stories/<story_id>/clues', methods=['POST'])
async def discover_clue(story_id: str):
    """Discover a new clue in the story."""
    try:
        data = request.get_json()
        required_fields = ['template_clue_id', 'discovery_method', 'discovery_location']
        
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields
            }), 400

        clue = await clue_service.discover_clue(
            UUID(story_id),
            UUID(data['template_clue_id']),
            data['discovery_method'],
            data['discovery_location']
        )
        return jsonify(clue), 201
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

        clue = await clue_service.update_clue_notes(UUID(clue_id), data['notes'])
        return jsonify(clue), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clue_bp.route('/clues/<clue_id>/connections', methods=['POST'])
async def add_clue_connection(clue_id: str):
    """Add a connection between two clues."""
    try:
        data = request.get_json()
        required_fields = ['connected_clue_id', 'connection_type', 'connection_details']
        
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields
            }), 400

        clue = await clue_service.add_clue_connection(
            UUID(clue_id),
            UUID(data['connected_clue_id']),
            data['connection_type'],
            data['connection_details']
        )
        return jsonify(clue), 201
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

        clue = await clue_service.update_clue_relevance(UUID(clue_id), float(data['relevance_score']))
        return jsonify(clue), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clue_bp.route('/clues/<clue_id>/connections', methods=['GET'])
async def get_clue_connections(clue_id: str):
    """Get all connections for a specific clue."""
    try:
        connections = await clue_service.get_clue_connections(UUID(clue_id))
        return jsonify(connections), 200
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

        clue = await clue_service.mark_clue_as_red_herring(UUID(clue_id), bool(data['is_red_herring']))
        return jsonify(clue), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500 