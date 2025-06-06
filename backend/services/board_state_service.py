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

class BoardStateService(BaseService):
    """Service for managing board state-related operations."""
    
    def get_board_state(self, story_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get the current board state for a story."""
        try:
            self.log_operation("get_board_state", {
                "story_id": story_id,
                "user_id": user_id
            })
            
            # Validate user has access to story
            story = self.supabase.table('stories').select('*').eq('id', story_id).eq('user_id', user_id).execute()
            if not story.data:
                raise AuthorizationError("User does not have access to this story")
            
            # Get board state
            board_state = self.supabase.table('board_states').select('*').eq('story_id', story_id).execute()
            if not board_state.data:
                return None
            
            return board_state.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "get_board_state")
    
    def create_board_state(self, story_id: str, user_id: str) -> Dict[str, Any]:
        """Create a new board state for a story."""
        try:
            self.log_operation("create_board_state", {
                "story_id": story_id,
                "user_id": user_id
            })
            
            # Validate user has access to story
            story = self.supabase.table('stories').select('*').eq('id', story_id).eq('user_id', user_id).execute()
            if not story.data:
                raise AuthorizationError("User does not have access to this story")
            
            # Check if board state already exists
            existing = self.get_board_state(story_id, user_id)
            if existing:
                raise ValidationError("Board state already exists for this story")
            
            # Create initial board state
            board_state_data = {
                'id': str(uuid.uuid4()),
                'story_id': story_id,
                'user_id': user_id,
                'clues': [],
                'suspects': [],
                'locations': [],
                'connections': [],
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('board_states').insert(board_state_data).execute()
            if not result.data:
                raise APIError("Failed to create board state")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "create_board_state")
    
    def update_board_state(self, story_id: str, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update the board state for a story."""
        try:
            self.log_operation("update_board_state", {
                "story_id": story_id,
                "user_id": user_id,
                "updates": updates
            })
            
            # Verify board state exists
            board_state = self.get_board_state(story_id, user_id)
            if not board_state:
                raise ResourceNotFoundError("Board state not found")
            
            # Add update timestamp
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            # Update board state
            result = self.supabase.table('board_states').update(updates).eq('story_id', story_id).execute()
            if not result.data:
                raise APIError("Failed to update board state")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "update_board_state")
    
    def add_clue_to_board(self, story_id: str, user_id: str, clue_id: str, position: Dict[str, float]) -> Dict[str, Any]:
        """Add a clue to the board."""
        try:
            self.log_operation("add_clue_to_board", {
                "story_id": story_id,
                "user_id": user_id,
                "clue_id": clue_id,
                "position": position
            })
            
            # Get current board state
            board_state = self.get_board_state(story_id, user_id)
            if not board_state:
                raise ResourceNotFoundError("Board state not found")
            
            # Add clue to board
            clues = board_state.get('clues', [])
            clues.append({
                'id': clue_id,
                'position': position,
                'added_at': datetime.utcnow().isoformat()
            })
            
            updates = {
                'clues': clues,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('board_states').update(updates).eq('story_id', story_id).execute()
            if not result.data:
                raise APIError("Failed to add clue to board")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "add_clue_to_board")
    
    def add_suspect_to_board(self, story_id: str, user_id: str, suspect_id: str, position: Dict[str, float]) -> Dict[str, Any]:
        """Add a suspect to the board."""
        try:
            self.log_operation("add_suspect_to_board", {
                "story_id": story_id,
                "user_id": user_id,
                "suspect_id": suspect_id,
                "position": position
            })
            
            # Get current board state
            board_state = self.get_board_state(story_id, user_id)
            if not board_state:
                raise ResourceNotFoundError("Board state not found")
            
            # Add suspect to board
            suspects = board_state.get('suspects', [])
            suspects.append({
                'id': suspect_id,
                'position': position,
                'added_at': datetime.utcnow().isoformat()
            })
            
            updates = {
                'suspects': suspects,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('board_states').update(updates).eq('story_id', story_id).execute()
            if not result.data:
                raise APIError("Failed to add suspect to board")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "add_suspect_to_board")
    
    def add_location_to_board(self, story_id: str, user_id: str, location_id: str, position: Dict[str, float]) -> Dict[str, Any]:
        """Add a location to the board."""
        try:
            self.log_operation("add_location_to_board", {
                "story_id": story_id,
                "user_id": user_id,
                "location_id": location_id,
                "position": position
            })
            
            # Get current board state
            board_state = self.get_board_state(story_id, user_id)
            if not board_state:
                raise ResourceNotFoundError("Board state not found")
            
            # Add location to board
            locations = board_state.get('locations', [])
            locations.append({
                'id': location_id,
                'position': position,
                'added_at': datetime.utcnow().isoformat()
            })
            
            updates = {
                'locations': locations,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('board_states').update(updates).eq('story_id', story_id).execute()
            if not result.data:
                raise APIError("Failed to add location to board")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "add_location_to_board")
    
    def add_connection(self, story_id: str, user_id: str, source_id: str, target_id: str, 
                      connection_type: str) -> Dict[str, Any]:
        """Add a connection between two elements on the board."""
        try:
            self.log_operation("add_connection", {
                "story_id": story_id,
                "user_id": user_id,
                "source_id": source_id,
                "target_id": target_id,
                "connection_type": connection_type
            })
            
            # Get current board state
            board_state = self.get_board_state(story_id, user_id)
            if not board_state:
                raise ResourceNotFoundError("Board state not found")
            
            # Add connection
            connections = board_state.get('connections', [])
            connections.append({
                'id': str(uuid.uuid4()),
                'source_id': source_id,
                'target_id': target_id,
                'type': connection_type,
                'created_at': datetime.utcnow().isoformat()
            })
            
            updates = {
                'connections': connections,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('board_states').update(updates).eq('story_id', story_id).execute()
            if not result.data:
                raise APIError("Failed to add connection")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "add_connection")
    
    def remove_element_from_board(self, story_id: str, user_id: str, element_id: str, element_type: str) -> Dict[str, Any]:
        """Remove an element from the board."""
        try:
            self.log_operation("remove_element_from_board", {
                "story_id": story_id,
                "user_id": user_id,
                "element_id": element_id,
                "element_type": element_type
            })
            
            # Get current board state
            board_state = self.get_board_state(story_id, user_id)
            if not board_state:
                raise ResourceNotFoundError("Board state not found")
            
            # Remove element
            elements = board_state.get(element_type, [])
            elements = [e for e in elements if e['id'] != element_id]
            
            # Remove related connections
            connections = board_state.get('connections', [])
            connections = [c for c in connections if c['source_id'] != element_id and c['target_id'] != element_id]
            
            updates = {
                element_type: elements,
                'connections': connections,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('board_states').update(updates).eq('story_id', story_id).execute()
            if not result.data:
                raise APIError(f"Failed to remove {element_type} from board")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "remove_element_from_board")
    
    def update_element_position(self, story_id: str, user_id: str, element_id: str, 
                              element_type: str, position: Dict[str, float]) -> Dict[str, Any]:
        """Update the position of an element on the board."""
        try:
            self.log_operation("update_element_position", {
                "story_id": story_id,
                "user_id": user_id,
                "element_id": element_id,
                "element_type": element_type,
                "position": position
            })
            
            # Get current board state
            board_state = self.get_board_state(story_id, user_id)
            if not board_state:
                raise ResourceNotFoundError("Board state not found")
            
            # Update element position
            elements = board_state.get(element_type, [])
            for element in elements:
                if element['id'] == element_id:
                    element['position'] = position
                    break
            
            updates = {
                element_type: elements,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('board_states').update(updates).eq('story_id', story_id).execute()
            if not result.data:
                raise APIError(f"Failed to update {element_type} position")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "update_element_position") 