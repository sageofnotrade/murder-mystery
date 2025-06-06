from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import logging
import uuid
from .base_service import BaseService
from utils.error_handlers import (
    APIError, ValidationError, ResourceNotFoundError,
    AuthenticationError, AuthorizationError
)

logger = logging.getLogger(__name__)

class UserProgressService(BaseService):
    """Service for managing user progress-related operations."""
    
    def get_user_progress(self, user_id: str, story_id: str) -> Optional[Dict[str, Any]]:
        """Get a user's progress for a specific story."""
        try:
            self.log_operation("get_user_progress", {
                "user_id": user_id,
                "story_id": story_id
            })
            
            progress = self.supabase.table('user_progress').select('*').eq('user_id', user_id).eq('story_id', story_id).execute()
            if not progress.data:
                return None
            
            return progress.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "get_user_progress")
    
    def create_user_progress(self, user_id: str, story_id: str) -> Dict[str, Any]:
        """Create a new user progress record."""
        try:
            self.log_operation("create_user_progress", {
                "user_id": user_id,
                "story_id": story_id
            })
            
            # Check if progress already exists
            existing = self.get_user_progress(user_id, story_id)
            if existing:
                raise ValidationError("User progress already exists for this story")
            
            # Create initial progress
            progress_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'story_id': story_id,
                'discovered_clues': [],
                'interviewed_suspects': [],
                'current_location': 'start',
                'game_state': 'in_progress',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('user_progress').insert(progress_data).execute()
            if not result.data:
                raise APIError("Failed to create user progress")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "create_user_progress")
    
    def update_user_progress(self, user_id: str, story_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a user's progress."""
        try:
            self.log_operation("update_user_progress", {
                "user_id": user_id,
                "story_id": story_id,
                "updates": updates
            })
            
            # Verify progress exists
            progress = self.get_user_progress(user_id, story_id)
            if not progress:
                raise ResourceNotFoundError("User progress not found")
            
            # Add update timestamp
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            # Update progress
            result = self.supabase.table('user_progress').update(updates).eq('user_id', user_id).eq('story_id', story_id).execute()
            if not result.data:
                raise APIError("Failed to update user progress")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "update_user_progress")
    
    def add_discovered_clue(self, user_id: str, story_id: str, clue_id: str) -> Dict[str, Any]:
        """Add a discovered clue to user progress."""
        try:
            self.log_operation("add_discovered_clue", {
                "user_id": user_id,
                "story_id": story_id,
                "clue_id": clue_id
            })
            
            # Get current progress
            progress = self.get_user_progress(user_id, story_id)
            if not progress:
                raise ResourceNotFoundError("User progress not found")
            
            # Add clue to discovered clues if not already present
            discovered_clues = progress.get('discovered_clues', [])
            if clue_id not in discovered_clues:
                discovered_clues.append(clue_id)
                
                updates = {
                    'discovered_clues': discovered_clues,
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                result = self.supabase.table('user_progress').update(updates).eq('user_id', user_id).eq('story_id', story_id).execute()
                if not result.data:
                    raise APIError("Failed to update discovered clues")
                
                return result.data[0]
            
            return progress
            
        except Exception as e:
            self.handle_service_error(e, "add_discovered_clue")
    
    def add_interviewed_suspect(self, user_id: str, story_id: str, suspect_id: str) -> Dict[str, Any]:
        """Add an interviewed suspect to user progress."""
        try:
            self.log_operation("add_interviewed_suspect", {
                "user_id": user_id,
                "story_id": story_id,
                "suspect_id": suspect_id
            })
            
            # Get current progress
            progress = self.get_user_progress(user_id, story_id)
            if not progress:
                raise ResourceNotFoundError("User progress not found")
            
            # Add suspect to interviewed suspects if not already present
            interviewed_suspects = progress.get('interviewed_suspects', [])
            if suspect_id not in interviewed_suspects:
                interviewed_suspects.append(suspect_id)
                
                updates = {
                    'interviewed_suspects': interviewed_suspects,
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                result = self.supabase.table('user_progress').update(updates).eq('user_id', user_id).eq('story_id', story_id).execute()
                if not result.data:
                    raise APIError("Failed to update interviewed suspects")
                
                return result.data[0]
            
            return progress
            
        except Exception as e:
            self.handle_service_error(e, "add_interviewed_suspect")
    
    def update_game_state(self, user_id: str, story_id: str, game_state: str) -> Dict[str, Any]:
        """Update the game state in user progress."""
        try:
            self.log_operation("update_game_state", {
                "user_id": user_id,
                "story_id": story_id,
                "game_state": game_state
            })
            
            # Validate game state
            valid_states = ['in_progress', 'completed', 'failed']
            if game_state not in valid_states:
                raise ValidationError(f"Invalid game state. Must be one of: {', '.join(valid_states)}")
            
            # Update game state
            updates = {
                'game_state': game_state,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('user_progress').update(updates).eq('user_id', user_id).eq('story_id', story_id).execute()
            if not result.data:
                raise APIError("Failed to update game state")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "update_game_state")
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics across all stories."""
        try:
            self.log_operation("get_user_stats", {"user_id": user_id})
            
            # Get all progress records for user
            progress_records = self.supabase.table('user_progress').select('*').eq('user_id', user_id).execute()
            
            # Calculate statistics
            stats = {
                'total_stories_started': len(progress_records.data),
                'completed_stories': sum(1 for p in progress_records.data if p['game_state'] == 'completed'),
                'failed_stories': sum(1 for p in progress_records.data if p['game_state'] == 'failed'),
                'in_progress_stories': sum(1 for p in progress_records.data if p['game_state'] == 'in_progress'),
                'total_clues_discovered': sum(len(p.get('discovered_clues', [])) for p in progress_records.data),
                'total_suspects_interviewed': sum(len(p.get('interviewed_suspects', [])) for p in progress_records.data)
            }
            
            return stats
            
        except Exception as e:
            self.handle_service_error(e, "get_user_stats")
