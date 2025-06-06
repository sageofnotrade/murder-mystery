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

class StoryService(BaseService):
    """Service for managing story-related operations."""
    
    def get_stories(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all stories for a user."""
        try:
            self.log_operation("get_stories", {"user_id": user_id})
            
            stories = self.supabase.table('stories').select('*').eq('user_id', user_id).execute()
            return stories.data
            
        except Exception as e:
            self.handle_service_error(e, "get_stories")
    
    def get_story(self, story_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific story."""
        try:
            self.log_operation("get_story", {
                "story_id": story_id,
                "user_id": user_id
            })
            
            story = self.supabase.table('stories').select('*').eq('id', story_id).eq('user_id', user_id).execute()
            if not story.data:
                raise ResourceNotFoundError(f"Story {story_id} not found")
            
            return story.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "get_story")
    
    def create_story(self, user_id: str, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new story."""
        try:
            self.log_operation("create_story", {
                "user_id": user_id,
                "story_data": story_data
            })
            
            # Validate required fields
            self.validate_required_fields(
                story_data,
                ["title", "description", "genre", "difficulty"]
            )
            
            # Add metadata
            story_data.update({
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'status': 'draft'
            })
            
            # Create story
            result = self.supabase.table('stories').insert(story_data).execute()
            if not result.data:
                raise APIError("Failed to create story")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "create_story")
    
    def update_story(self, story_id: str, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing story."""
        try:
            self.log_operation("update_story", {
                "story_id": story_id,
                "user_id": user_id,
                "updates": updates
            })
            
            # Verify story exists and user has access
            story = self.get_story(story_id, user_id)
            if not story:
                raise ResourceNotFoundError(f"Story {story_id} not found")
            
            # Add update timestamp
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            # Update story
            result = self.supabase.table('stories').update(updates).eq('id', story_id).execute()
            if not result.data:
                raise APIError("Failed to update story")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "update_story")
    
    def delete_story(self, story_id: str, user_id: str) -> None:
        """Delete a story."""
        try:
            self.log_operation("delete_story", {
                "story_id": story_id,
                "user_id": user_id
            })
            
            # Verify story exists and user has access
            story = self.get_story(story_id, user_id)
            if not story:
                raise ResourceNotFoundError(f"Story {story_id} not found")
            
            # Delete story
            result = self.supabase.table('stories').delete().eq('id', story_id).execute()
            if not result.data:
                raise APIError("Failed to delete story")
            
        except Exception as e:
            self.handle_service_error(e, "delete_story")
    
    def publish_story(self, story_id: str, user_id: str) -> Dict[str, Any]:
        """Publish a story."""
        try:
            self.log_operation("publish_story", {
                "story_id": story_id,
                "user_id": user_id
            })
            
            # Verify story exists and user has access
            story = self.get_story(story_id, user_id)
            if not story:
                raise ResourceNotFoundError(f"Story {story_id} not found")
            
            # Validate story is ready for publishing
            if not self._validate_story_for_publishing(story):
                raise ValidationError("Story is not ready for publishing")
            
            # Update story status
            updates = {
                'status': 'published',
                'published_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('stories').update(updates).eq('id', story_id).execute()
            if not result.data:
                raise APIError("Failed to publish story")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "publish_story")
    
    def _validate_story_for_publishing(self, story: Dict[str, Any]) -> bool:
        """Validate that a story is ready for publishing."""
        try:
            # Check required fields
            required_fields = ['title', 'description', 'genre', 'difficulty']
            for field in required_fields:
                if not story.get(field):
                    return False
            
            # Check story has at least one suspect
            suspects = self.supabase.table('suspects').select('*').eq('story_id', story['id']).execute()
            if not suspects.data:
                return False
            
            # Check story has at least one clue
            clues = self.supabase.table('clues').select('*').eq('story_id', story['id']).execute()
            if not clues.data:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating story for publishing: {str(e)}")
            return False
