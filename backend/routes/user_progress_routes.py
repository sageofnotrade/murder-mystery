"""
Flask routes for user progress saving/loading functionality.
Provides comprehensive endpoints for progress management, achievements, and analytics.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.user_progress_service import UserProgressService
from backend.services.supabase_service import get_supabase_client
from backend.models.user_progress_models import (
    SaveProgressRequest, LoadProgressRequest, BackupProgressRequest,
    RestoreProgressRequest, AchievementType, ProgressError
)
from pydantic import ValidationError
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

user_progress_bp = Blueprint('user_progress_routes', __name__)

def get_progress_service():
    """Get a UserProgressService instance with the current Supabase client."""
    return UserProgressService(get_supabase_client())

@user_progress_bp.route('/progress', methods=['GET'])
@jwt_required()
def get_user_progress():
    """Get complete user progress including all mysteries and achievements."""
    user_id = get_jwt_identity()
    progress_service = get_progress_service()
    
    try:
        include_details = request.args.get('include_details', 'true').lower() == 'true'
        user_progress = progress_service.get_user_progress(user_id, include_mystery_details=include_details)
        
        return jsonify(user_progress.model_dump())
    except Exception as e:
        logger.error(f"Error getting user progress for {user_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_progress_bp.route('/progress/summary', methods=['GET'])
@jwt_required()
def get_progress_summary():
    """Get summary of user's overall progress."""
    user_id = get_jwt_identity()
    progress_service = get_progress_service()
    
    try:
        summary = progress_service.get_progress_summary(user_id)
        return jsonify(summary.model_dump())
    except Exception as e:
        logger.error(f"Error getting progress summary for {user_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_progress_bp.route('/progress/save', methods=['POST'])
@jwt_required()
def save_progress():
    """Save user progress for a specific mystery."""
    user_id = get_jwt_identity()
    progress_service = get_progress_service()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Validate request data
        save_request = SaveProgressRequest(**data)
        
        # Save progress
        result = progress_service.save_progress(user_id, save_request)
        
        return jsonify(result.model_dump()), 201
    except ValidationError as e:
        return jsonify({'error': 'Invalid request data', 'details': e.errors()}), 400
    except Exception as e:
        logger.error(f"Error saving progress for {user_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_progress_bp.route('/progress/load', methods=['POST'])
@jwt_required()
def load_progress():
    """Load user progress for a specific mystery or overall progress."""
    user_id = get_jwt_identity()
    progress_service = get_progress_service()
    
    try:
        data = request.get_json()
        if not data:
            data = {}
        
        # Validate request data
        load_request = LoadProgressRequest(**data)
        
        # Load progress
        result = progress_service.load_progress(user_id, load_request)
        
        return jsonify(result.model_dump())
    except ValidationError as e:
        return jsonify({'error': 'Invalid request data', 'details': e.errors()}), 400
    except Exception as e:
        logger.error(f"Error loading progress for {user_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_progress_bp.route('/progress/mystery/<mystery_id>', methods=['GET'])
@jwt_required()
def get_mystery_progress(mystery_id):
    """Get progress for a specific mystery."""
    user_id = get_jwt_identity()
    progress_service = get_progress_service()
    
    try:
        mystery_progress = progress_service.get_mystery_progress(user_id, mystery_id)
        
        if not mystery_progress:
            return jsonify({'error': 'Mystery progress not found'}), 404
        
        return jsonify(mystery_progress.model_dump())
    except Exception as e:
        logger.error(f"Error getting mystery progress for {user_id}, mystery {mystery_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_progress_bp.route('/progress/mystery/<mystery_id>', methods=['POST'])
@jwt_required()
def create_mystery_progress(mystery_id):
    """Create new progress tracking for a mystery."""
    user_id = get_jwt_identity()
    progress_service = get_progress_service()
    
    try:
        mystery_progress = progress_service.create_mystery_progress(user_id, mystery_id)
        return jsonify(mystery_progress.model_dump()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error creating mystery progress for {user_id}, mystery {mystery_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_progress_bp.route('/progress/mystery/<mystery_id>/checkpoints', methods=['GET'])
@jwt_required()
def get_mystery_checkpoints(mystery_id):
    """Get available checkpoints for a mystery."""
    user_id = get_jwt_identity()
    progress_service = get_progress_service()
    
    try:
        mystery_progress = progress_service.get_mystery_progress(user_id, mystery_id)
        
        if not mystery_progress:
            return jsonify({'error': 'Mystery progress not found'}), 404
        
        checkpoints = []
        for name, data in mystery_progress.checkpoint_data.items():
            checkpoints.append({
                'name': name,
                'timestamp': data.get('timestamp'),
                'save_id': data.get('save_id')
            })
        
        # Sort by timestamp
        checkpoints.sort(key=lambda x: x['timestamp'] if x['timestamp'] else '', reverse=True)
        
        return jsonify({
            'mystery_id': mystery_id,
            'checkpoints': checkpoints,
            'total_count': len(checkpoints)
        })
    except Exception as e:
        logger.error(f"Error getting checkpoints for {user_id}, mystery {mystery_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_progress_bp.route('/progress/mystery/<mystery_id>/checkpoints/<checkpoint_name>', methods=['GET'])
@jwt_required()
def load_checkpoint(mystery_id, checkpoint_name):
    """Load a specific checkpoint for a mystery."""
    user_id = get_jwt_identity()
    progress_service = get_progress_service()
    
    try:
        load_request = LoadProgressRequest(
            mystery_id=mystery_id,
            checkpoint_name=checkpoint_name
        )
        
        result = progress_service.load_progress(user_id, load_request)
        
        if not result.mystery_progress:
            return jsonify({'error': 'Checkpoint not found'}), 404
        
        return jsonify(result.model_dump())
    except Exception as e:
        logger.error(f"Error loading checkpoint {checkpoint_name} for {user_id}, mystery {mystery_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_progress_bp.route('/progress/achievements', methods=['GET'])
@jwt_required()
def get_achievements():
    """Get user's achievements."""
    user_id = get_jwt_identity()
    progress_service = get_progress_service()
    
    try:
        user_progress = progress_service.get_user_progress(user_id, include_mystery_details=False)
        
        return jsonify({
            'achievements': [achievement.model_dump() for achievement in user_progress.achievements],
            'total_points': user_progress.achievement_points,
            'achievement_count': len(user_progress.achievements)
        })
    except Exception as e:
        logger.error(f"Error getting achievements for {user_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_progress_bp.route('/progress/achievements/<achievement_type>', methods=['POST'])
@jwt_required()
def award_achievement(achievement_type):
    """Award an achievement to the user."""
    user_id = get_jwt_identity()
    progress_service = get_progress_service()
    
    try:
        # Validate achievement type
        try:
            achievement_enum = AchievementType(achievement_type)
        except ValueError:
            return jsonify({'error': f'Invalid achievement type: {achievement_type}'}), 400
        
        data = request.get_json() or {}
        mystery_id = data.get('mystery_id')
        
        achievement = progress_service.award_achievement(user_id, achievement_enum, mystery_id)
        
        return jsonify({
            'achievement': achievement.model_dump(),
            'newly_earned': True  # Could be modified to check if already existed
        }), 201
    except Exception as e:
        logger.error(f"Error awarding achievement {achievement_type} to {user_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_progress_bp.route('/progress/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """Get user's game statistics."""
    user_id = get_jwt_identity()
    progress_service = get_progress_service()
    
    try:
        user_progress = progress_service.get_user_progress(user_id, include_mystery_details=False)
        
        return jsonify(user_progress.statistics.model_dump())
    except Exception as e:
        logger.error(f"Error getting statistics for {user_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_progress_bp.route('/progress/current-mystery', methods=['GET'])
@jwt_required()
def get_current_mystery():
    """Get the user's current mystery progress."""
    user_id = get_jwt_identity()
    progress_service = get_progress_service()
    
    try:
        user_progress = progress_service.get_user_progress(user_id, include_mystery_details=False)
        
        if not user_progress.current_mystery_id:
            return jsonify({'error': 'No current mystery'}), 404
        
        mystery_progress = progress_service.get_mystery_progress(user_id, user_progress.current_mystery_id)
        
        if not mystery_progress:
            return jsonify({'error': 'Current mystery progress not found'}), 404
        
        return jsonify(mystery_progress.model_dump())
    except Exception as e:
        logger.error(f"Error getting current mystery for {user_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_progress_bp.route('/progress/current-mystery', methods=['PUT'])
@jwt_required()
def set_current_mystery():
    """Set the user's current mystery."""
    user_id = get_jwt_identity()
    progress_service = get_progress_service()
    
    try:
        data = request.get_json()
        if not data or 'mystery_id' not in data:
            return jsonify({'error': 'mystery_id is required'}), 400
        
        mystery_id = data['mystery_id']
        
        # Verify mystery exists and user has access
        mystery_progress = progress_service.get_mystery_progress(user_id, mystery_id)
        if not mystery_progress:
            # Create new progress if doesn't exist
            mystery_progress = progress_service.create_mystery_progress(user_id, mystery_id)
        
        # Update current mystery
        progress_service.update_current_mystery(user_id, mystery_id)
        
        return jsonify({
            'current_mystery_id': mystery_id,
            'mystery_progress': mystery_progress.model_dump()
        })
    except Exception as e:
        logger.error(f"Error setting current mystery for {user_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_progress_bp.route('/progress/backup', methods=['POST'])
@jwt_required()
def create_backup():
    """Create a backup of user progress."""
    user_id = get_jwt_identity()
    progress_service = get_progress_service()
    
    try:
        data = request.get_json() or {}
        backup_request = BackupProgressRequest(**data)
        
        # TODO: Implement backup functionality
        # For now, return a placeholder response
        return jsonify({
            'backup_id': f"backup_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'created_at': datetime.utcnow().isoformat(),
            'message': 'Backup functionality coming soon'
        }), 201
    except ValidationError as e:
        return jsonify({'error': 'Invalid backup request', 'details': e.errors()}), 400
    except Exception as e:
        logger.error(f"Error creating backup for {user_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_progress_bp.route('/progress/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    """Get analytics data for user progress."""
    user_id = get_jwt_identity()
    progress_service = get_progress_service()
    
    try:
        user_progress = progress_service.get_user_progress(user_id)
        
        # Calculate analytics
        total_mysteries = len(user_progress.mystery_progress)
        completed_mysteries = sum(1 for p in user_progress.mystery_progress.values() 
                                if p.status.value == 'completed')
        
        # Average completion time for completed mysteries
        completed_times = [p.time_played_minutes for p in user_progress.mystery_progress.values() 
                          if p.status.value == 'completed' and p.time_played_minutes > 0]
        avg_completion_time = sum(completed_times) / len(completed_times) if completed_times else 0
        
        # Favorite difficulty
        difficulty_counts = {}
        for progress in user_progress.mystery_progress.values():
            diff = progress.difficulty.value
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
        
        favorite_difficulty = max(difficulty_counts.items(), key=lambda x: x[1])[0] if difficulty_counts else 'beginner'
        
        analytics = {
            'user_id': user_id,
            'session_count': total_mysteries,  # Approximate
            'average_session_duration': avg_completion_time,
            'favorite_mystery_type': 'detective',  # Placeholder
            'peak_play_times': ['evening'],  # Placeholder
            'difficulty_preference': favorite_difficulty,
            'completion_patterns': {
                'total_started': total_mysteries,
                'total_completed': completed_mysteries,
                'completion_rate': (completed_mysteries / total_mysteries * 100) if total_mysteries > 0 else 0
            },
            'improvement_metrics': {
                'average_hints_used': sum(p.hints_used for p in user_progress.mystery_progress.values()) / total_mysteries if total_mysteries > 0 else 0,
                'average_wrong_deductions': sum(p.wrong_deductions for p in user_progress.mystery_progress.values()) / total_mysteries if total_mysteries > 0 else 0
            }
        }
        
        return jsonify(analytics)
    except Exception as e:
        logger.error(f"Error getting analytics for {user_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_progress_bp.route('/progress/reset', methods=['POST'])
@jwt_required()
def reset_progress():
    """Reset user progress (with confirmation)."""
    user_id = get_jwt_identity()
    progress_service = get_progress_service()
    
    try:
        data = request.get_json() or {}
        confirm = data.get('confirm', False)
        
        if not confirm:
            return jsonify({'error': 'Confirmation required to reset progress'}), 400
        
        # TODO: Implement progress reset functionality
        # For now, return a placeholder response
        return jsonify({
            'message': 'Progress reset functionality coming soon',
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error resetting progress for {user_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Error handling for progress-specific errors
@user_progress_bp.errorhandler(ValidationError)
def handle_validation_error(e):
    """Handle Pydantic validation errors."""
    return jsonify({
        'error': 'Validation error',
        'details': e.errors(),
        'timestamp': datetime.utcnow().isoformat()
    }), 400

@user_progress_bp.errorhandler(Exception)
def handle_general_error(e):
    """Handle general errors."""
    logger.error(f"Unhandled error in progress routes: {str(e)}")
    return jsonify({
        'error': 'Internal server error',
        'message': str(e),
        'timestamp': datetime.utcnow().isoformat()
    }), 500 