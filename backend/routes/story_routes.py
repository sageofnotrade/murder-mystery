from flask import Blueprint, request, jsonify
from uuid import UUID
from services.story_service import StoryService
from models.story_models import PlayerAction, StoryResponse
from supabase import create_client, Client
import os

story_bp = Blueprint('story', __name__)

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Initialize story service
story_service = StoryService(supabase)

@story_bp.route('/stories', methods=['POST'])
async def create_story():
    """Create a new story instance."""
    try:
        data = request.get_json()
        mystery_id = UUID(data['mystery_id'])
        
        story = await story_service.create_story(mystery_id)
        return jsonify({
            'message': 'Story created successfully',
            'story_id': str(story.id)
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@story_bp.route('/stories/<story_id>', methods=['GET'])
async def get_story(story_id: str):
    """Get the current state of a story."""
    try:
        story = await story_service.get_story(UUID(story_id))
        return jsonify(story.dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@story_bp.route('/stories/<story_id>/actions', methods=['POST'])
async def process_action(story_id: str):
    """Process a player action and update the story state."""
    try:
        data = request.get_json()
        action = PlayerAction(**data)
        
        response = await story_service.process_action(UUID(story_id), action)
        return jsonify(response.dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@story_bp.route('/stories/<story_id>/choices', methods=['GET'])
async def get_choices(story_id: str):
    """Get available choices for the current story state."""
    try:
        choices = await story_service.get_available_choices(UUID(story_id))
        return jsonify([choice.dict() for choice in choices]), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@story_bp.route('/stories/<story_id>/save', methods=['POST'])
async def save_story(story_id: str):
    """Save the current state of a story."""
    try:
        story = await story_service.get_story(UUID(story_id))
        await story_service.save_story_state(story)
        return jsonify({'message': 'Story state saved successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500 