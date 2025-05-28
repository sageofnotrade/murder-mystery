from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from typing import Dict, Any

from models.template_models import MysteryTemplate
from services.template_service import TemplateService

template_bp = Blueprint('templates', __name__)
template_service = TemplateService()

@template_bp.route('', methods=['GET'])
def get_all_templates():
    """Get all templates with optional pagination."""
    try:
        limit = request.args.get('limit', default=20, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        templates = template_service.get_all_templates(limit=limit, offset=offset)
        return jsonify({
            'success': True,
            'templates': [t.model_dump() for t in templates],
            'count': len(templates)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@template_bp.route('/<template_id>', methods=['GET'])
def get_template(template_id: str):
    """Get a specific template by ID."""
    try:
        template = template_service.get_template_by_id(template_id)
        
        if not template:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404
            
        return jsonify({
            'success': True,
            'template': template.model_dump()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@template_bp.route('', methods=['POST'])
def create_template():
    """Create a new template."""
    try:
        data = request.get_json()
        
        # Validate and create model instance
        template = MysteryTemplate(**data)
        
        # Save to database
        created_template = template_service.create_template(template)
        
        return jsonify({
            'success': True,
            'template': created_template.model_dump()
        }), 201
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@template_bp.route('/<template_id>', methods=['PUT'])
def update_template(template_id: str):
    """Update an existing template."""
    try:
        data = request.get_json()
        
        # Check if template exists
        existing_template = template_service.get_template_by_id(template_id)
        if not existing_template:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404
        
        # Update template
        updated_template = template_service.update_template(template_id, data)
        
        return jsonify({
            'success': True,
            'template': updated_template.model_dump()
        }), 200
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@template_bp.route('/<template_id>', methods=['DELETE'])
def delete_template(template_id: str):
    """Delete a template."""
    try:
        # Check if template exists
        existing_template = template_service.get_template_by_id(template_id)
        if not existing_template:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404
        
        # Delete template
        success = template_service.delete_template(template_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Template {template_id} deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete template'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@template_bp.route('/search', methods=['GET'])
def search_templates():
    """Search for templates by query."""
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 10, type=int)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400
            
        templates = template_service.search_templates(query, limit)
        
        return jsonify({
            'success': True,
            'templates': [t.model_dump() for t in templates],
            'count': len(templates)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 