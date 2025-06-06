from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from supabase import Client
from backend.agents.models.story_models import StoryState
from backend.agents.models.clue_models import ClueCreate, ClueDetail, ClueConnection, ClueAnalysisRequest
from .base_service import BaseService
from utils.error_handlers import (
    APIError, ValidationError, ResourceNotFoundError,
    AuthenticationError, AuthorizationError
)
import json
import logging
import uuid

logger = logging.getLogger(__name__)

class ClueService(BaseService):
    def __init__(self, supabase: Client):
        super().__init__(supabase)

    async def discover_clue(self, story_id: UUID, template_clue_id: UUID, 
                          discovery_method: str, discovery_location: str) -> Dict[str, Any]:
        """Discover a new clue in the story."""
        try:
            # Get the template clue
            template_clue = await self.supabase.table('template_clues').select('*').eq('id', str(template_clue_id)).single().execute()
            if not template_clue.data:
                raise ValueError(f"Template clue {template_clue_id} not found")

            # Create the story clue
            clue_data = {
                'story_id': str(story_id),
                'template_clue_id': str(template_clue_id),
                'discovered_at': datetime.now().isoformat(),
                'discovery_method': discovery_method,
                'discovery_location': discovery_location,
                'relevance_score': 0.5,  # Default relevance
                'is_red_herring': template_clue.data.get('is_red_herring', False),
                'notes': None,
                'connections': []
            }

            result = await self.supabase.table('story_clues').insert(clue_data).execute()
            if not result.data:
                raise ValueError("Failed to create story clue")

            # Update story state to include the new clue
            story_state = await self.supabase.table('story_states').select('*').eq('story_id', str(story_id)).single().execute()
            if story_state.data:
                discovered_clues = story_state.data.get('discovered_clues', [])
                discovered_clues.append(str(template_clue_id))
                await self.supabase.table('story_states').update({
                    'discovered_clues': discovered_clues
                }).eq('story_id', str(story_id)).execute()

            return result.data[0]

        except Exception as e:
            raise ValueError(f"Error discovering clue: {str(e)}")

    async def get_story_clues(self, story_id: UUID) -> List[Dict[str, Any]]:
        """Get all clues for a story."""
        try:
            self.log_operation("get_story_clues", {"story_id": story_id})
            
            # Validate user has access to story
            story = self.supabase.table('stories').select('*').eq('id', story_id).execute()
            if not story.data:
                raise AuthorizationError("User does not have access to this story")
            
            result = await self.supabase.table('story_clues').select('*, template_clues(*)').eq('story_id', str(story_id)).execute()
            return result.data
        except Exception as e:
            self.handle_service_error(e, "get_story_clues")

    async def update_clue_notes(self, clue_id: UUID, notes: str) -> Dict[str, Any]:
        """Update notes for a discovered clue."""
        try:
            self.log_operation("update_clue_notes", {"clue_id": clue_id, "notes": notes})
            
            result = await self.supabase.table('story_clues').update({
                'notes': notes
            }).eq('id', str(clue_id)).execute()
            
            if not result.data:
                raise ValueError(f"Clue {clue_id} not found")
            
            return result.data[0]
        except Exception as e:
            self.handle_service_error(e, "update_clue_notes")

    async def add_clue_connection(self, clue_id: UUID, connected_clue_id: UUID, 
                                connection_type: str, connection_details: Dict[str, Any]) -> Dict[str, Any]:
        """Add a connection between two clues."""
        try:
            self.log_operation("add_clue_connection", {"clue_id": clue_id, "connected_clue_id": connected_clue_id, "connection_type": connection_type, "connection_details": connection_details})
            
            # Get current connections
            clue = await self.supabase.table('story_clues').select('connections').eq('id', str(clue_id)).single().execute()
            if not clue.data:
                raise ValueError(f"Clue {clue_id} not found")

            connections = clue.data.get('connections', [])
            
            # Add new connection
            new_connection = {
                'connected_clue_id': str(connected_clue_id),
                'connection_type': connection_type,
                'details': connection_details,
                'created_at': datetime.now().isoformat()
            }
            connections.append(new_connection)

            # Update clue with new connection
            result = await self.supabase.table('story_clues').update({
                'connections': connections
            }).eq('id', str(clue_id)).execute()

            if not result.data:
                raise ValueError("Failed to update clue connections")

            return result.data[0]
        except Exception as e:
            self.handle_service_error(e, "add_clue_connection")

    async def update_clue_relevance(self, clue_id: UUID, relevance_score: float) -> Dict[str, Any]:
        """Update the relevance score of a clue."""
        try:
            self.log_operation("update_clue_relevance", {"clue_id": clue_id, "relevance_score": relevance_score})
            
            if not 0 <= relevance_score <= 1:
                raise ValueError("Relevance score must be between 0 and 1")

            result = await self.supabase.table('story_clues').update({
                'relevance_score': relevance_score
            }).eq('id', str(clue_id)).execute()

            if not result.data:
                raise ValueError(f"Clue {clue_id} not found")

            return result.data[0]
        except Exception as e:
            self.handle_service_error(e, "update_clue_relevance")

    async def get_clue_connections(self, clue_id: UUID) -> List[Dict[str, Any]]:
        """Get all connections for a specific clue."""
        try:
            self.log_operation("get_clue_connections", {"clue_id": clue_id})
            
            clue = await self.supabase.table('story_clues').select('connections').eq('id', str(clue_id)).single().execute()
            if not clue.data:
                raise ValueError(f"Clue {clue_id} not found")

            return clue.data.get('connections', [])
        except Exception as e:
            self.handle_service_error(e, "get_clue_connections")

    async def mark_clue_as_red_herring(self, clue_id: UUID, is_red_herring: bool) -> Dict[str, Any]:
        """Mark a clue as a red herring or not."""
        try:
            self.log_operation("mark_clue_as_red_herring", {"clue_id": clue_id, "is_red_herring": is_red_herring})
            
            result = await self.supabase.table('story_clues').update({
                'is_red_herring': is_red_herring
            }).eq('id', str(clue_id)).execute()

            if not result.data:
                raise ValueError(f"Clue {clue_id} not found")

            return result.data[0]
        except Exception as e:
            self.handle_service_error(e, "mark_clue_as_red_herring")

    async def discover_clue(self, story_id: str, user_id: str, clue_data: ClueCreate) -> ClueDetail:
        """Discover a new clue in the story."""
        # Create clue record
        clue_record = {
            'id': str(uuid.uuid4()),
            'story_id': story_id,
            'template_clue_id': clue_data.id,
            'discovered_at': datetime.now().isoformat(),
            'discovery_method': clue_data.discovery_context,
            'discovery_location': clue_data.location,
            'relevance_score': 0.5,  # Initial score
            'is_red_herring': False,
            'notes': '',
            'connections': []
        }
        
        # Insert into database
        result = self.supabase.table('story_clues').insert(clue_record).execute()
        if not result.data:
            raise Exception("Failed to create clue record")
            
        return ClueDetail(**result.data[0])
        
    async def get_story_clues(self, story_id: str, user_id: str) -> List[ClueDetail]:
        """Get all discovered clues for a story."""
        result = self.supabase.table('story_clues')\
            .select('*')\
            .eq('story_id', story_id)\
            .execute()
            
        return [ClueDetail(**clue) for clue in result.data]
        
    async def get_clue_details(self, story_id: str, clue_id: str, user_id: str) -> ClueDetail:
        """Get detailed information about a specific clue."""
        result = self.supabase.table('story_clues')\
            .select('*')\
            .eq('story_id', story_id)\
            .eq('id', clue_id)\
            .execute()
            
        if not result.data:
            raise Exception("Clue not found")
            
        return ClueDetail(**result.data[0])
        
    async def update_clue_notes(self, story_id: str, clue_id: str, notes: str, user_id: str) -> ClueDetail:
        """Update the notes for a clue."""
        result = self.supabase.table('story_clues')\
            .update({'notes': notes})\
            .eq('story_id', story_id)\
            .eq('id', clue_id)\
            .execute()
            
        if not result.data:
            raise Exception("Failed to update clue notes")
            
        return ClueDetail(**result.data[0])
        
    async def add_clue_connection(self, story_id: str, connection: ClueConnection, user_id: str) -> ClueConnection:
        """Create a connection between two clues."""
        # Validate clues exist
        source = await self.get_clue_details(story_id, connection.source_clue_id, user_id)
        target = await self.get_clue_details(story_id, connection.target_clue_id, user_id)
        
        # Create connection record
        connection_record = {
            'id': str(uuid.uuid4()),
            'story_id': story_id,
            'source_clue_id': connection.source_clue_id,
            'target_clue_id': connection.target_clue_id,
            'relationship_type': connection.relationship_type,
            'description': connection.description,
            'created_at': datetime.now().isoformat()
        }
        
        # Insert into database
        result = self.supabase.table('clue_connections').insert(connection_record).execute()
        if not result.data:
            raise Exception("Failed to create clue connection")
            
        # Update clue connections
        await self._update_clue_connections(story_id, connection.source_clue_id, user_id)
        await self._update_clue_connections(story_id, connection.target_clue_id, user_id)
        
        return ClueConnection(**result.data[0])
        
    async def get_clue_connections(self, story_id: str, clue_id: str, user_id: str) -> List[ClueConnection]:
        """Get all connections for a clue."""
        result = self.supabase.table('clue_connections')\
            .select('*')\
            .eq('story_id', story_id)\
            .eq('source_clue_id', clue_id)\
            .execute()
            
        return [ClueConnection(**conn) for conn in result.data]
        
    async def update_clue_relevance(self, story_id: str, clue_id: str, relevance_score: float, user_id: str) -> ClueDetail:
        """Update the relevance score of a clue."""
        result = self.supabase.table('story_clues')\
            .update({'relevance_score': relevance_score})\
            .eq('story_id', story_id)\
            .eq('id', clue_id)\
            .execute()
            
        if not result.data:
            raise Exception("Failed to update clue relevance")
            
        return ClueDetail(**result.data[0])
        
    async def mark_clue_as_red_herring(self, story_id: str, clue_id: str, user_id: str) -> ClueDetail:
        """Mark a clue as a red herring."""
        result = self.supabase.table('story_clues')\
            .update({'is_red_herring': True})\
            .eq('story_id', story_id)\
            .eq('id', clue_id)\
            .execute()
            
        if not result.data:
            raise Exception("Failed to mark clue as red herring")
            
        return ClueDetail(**result.data[0])
        
    async def analyze_clue(self, story_id: str, clue_id: str, analysis_request: ClueAnalysisRequest, user_id: str) -> Dict[str, Any]:
        """Analyze a clue for deeper insights."""
        # Get clue details
        clue = await self.get_clue_details(story_id, clue_id, user_id)
        
        # Get related clues
        connections = await self.get_clue_connections(story_id, clue_id, user_id)
        
        # Get related suspects
        suspects_result = self.supabase.table('story_suspects')\
            .select('*')\
            .eq('story_id', story_id)\
            .execute()
            
        suspects = suspects_result.data
        
        # Perform analysis
        analysis = {
            'clue_details': clue.dict(),
            'related_clues': [conn.dict() for conn in connections],
            'related_suspects': suspects,
            'analysis_context': analysis_request.context,
            'focus_areas': analysis_request.focus_areas,
            'timestamp': datetime.now().isoformat()
        }
        
        return analysis
        
    async def _update_clue_connections(self, story_id: str, clue_id: str, user_id: str) -> None:
        """Update the connections list for a clue."""
        # Get all connections
        result = self.supabase.table('clue_connections')\
            .select('*')\
            .eq('story_id', story_id)\
            .eq('source_clue_id', clue_id)\
            .execute()
            
        # Update clue record
        self.supabase.table('story_clues')\
            .update({'connections': [conn['id'] for conn in result.data]})\
            .eq('story_id', story_id)\
            .eq('id', clue_id)\
            .execute()

    def get_clues(self, story_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get all clues for a story."""
        try:
            self.log_operation("get_clues", {"story_id": story_id, "user_id": user_id})
            
            # Validate user has access to story
            story = self.supabase.table('stories').select('*').eq('id', story_id).eq('user_id', user_id).execute()
            if not story.data:
                raise AuthorizationError("User does not have access to this story")
            
            # Get clues
            clues = self.supabase.table('clues').select('*').eq('story_id', story_id).execute()
            return clues.data
            
        except Exception as e:
            self.handle_service_error(e, "get_clues")
    
    def get_clue(self, clue_id: str, story_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific clue."""
        try:
            self.log_operation("get_clue", {
                "clue_id": clue_id,
                "story_id": story_id,
                "user_id": user_id
            })
            
            # Validate user has access to story
            story = self.supabase.table('stories').select('*').eq('id', story_id).eq('user_id', user_id).execute()
            if not story.data:
                raise AuthorizationError("User does not have access to this story")
            
            # Get clue
            clue = self.supabase.table('clues').select('*').eq('id', clue_id).eq('story_id', story_id).execute()
            if not clue.data:
                raise ResourceNotFoundError(f"Clue {clue_id} not found")
            
            return clue.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "get_clue")
    
    def create_clue(self, story_id: str, user_id: str, clue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new clue."""
        try:
            self.log_operation("create_clue", {
                "story_id": story_id,
                "user_id": user_id,
                "clue_data": clue_data
            })
            
            # Validate user has access to story
            story = self.supabase.table('stories').select('*').eq('id', story_id).eq('user_id', user_id).execute()
            if not story.data:
                raise AuthorizationError("User does not have access to this story")
            
            # Validate required fields
            self.validate_required_fields(
                clue_data,
                ["title", "description", "type", "location"]
            )
            
            # Add metadata
            clue_data.update({
                'id': str(uuid.uuid4()),
                'story_id': story_id,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            })
            
            # Create clue
            result = self.supabase.table('clues').insert(clue_data).execute()
            if not result.data:
                raise APIError("Failed to create clue")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "create_clue")
    
    def update_clue(self, clue_id: str, story_id: str, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing clue."""
        try:
            self.log_operation("update_clue", {
                "clue_id": clue_id,
                "story_id": story_id,
                "user_id": user_id,
                "updates": updates
            })
            
            # Verify clue exists and user has access
            clue = self.get_clue(clue_id, story_id, user_id)
            if not clue:
                raise ResourceNotFoundError(f"Clue {clue_id} not found")
            
            # Add update timestamp
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            # Update clue
            result = self.supabase.table('clues').update(updates).eq('id', clue_id).execute()
            if not result.data:
                raise APIError("Failed to update clue")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "update_clue")
    
    def delete_clue(self, clue_id: str, story_id: str, user_id: str) -> None:
        """Delete a clue."""
        try:
            self.log_operation("delete_clue", {
                "clue_id": clue_id,
                "story_id": story_id,
                "user_id": user_id
            })
            
            # Verify clue exists and user has access
            clue = self.get_clue(clue_id, story_id, user_id)
            if not clue:
                raise ResourceNotFoundError(f"Clue {clue_id} not found")
            
            # Delete clue
            result = self.supabase.table('clues').delete().eq('id', clue_id).execute()
            if not result.data:
                raise APIError("Failed to delete clue")
            
        except Exception as e:
            self.handle_service_error(e, "delete_clue")
    
    def link_clue_to_suspect(self, clue_id: str, suspect_id: str, story_id: str, 
                            user_id: str, relationship: str) -> Dict[str, Any]:
        """Link a clue to a suspect."""
        try:
            self.log_operation("link_clue_to_suspect", {
                "clue_id": clue_id,
                "suspect_id": suspect_id,
                "story_id": story_id,
                "user_id": user_id,
                "relationship": relationship
            })
            
            # Verify clue exists and user has access
            clue = self.get_clue(clue_id, story_id, user_id)
            if not clue:
                raise ResourceNotFoundError(f"Clue {clue_id} not found")
            
            # Verify suspect exists
            suspect = self.supabase.table('suspects').select('*').eq('id', suspect_id).eq('story_id', story_id).execute()
            if not suspect.data:
                raise ResourceNotFoundError(f"Suspect {suspect_id} not found")
            
            # Create relationship
            relationship_data = {
                'id': str(uuid.uuid4()),
                'clue_id': clue_id,
                'suspect_id': suspect_id,
                'story_id': story_id,
                'relationship': relationship,
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table('clue_suspect_relationships').insert(relationship_data).execute()
            if not result.data:
                raise APIError("Failed to link clue to suspect")
            
            return result.data[0]
            
        except Exception as e:
            self.handle_service_error(e, "link_clue_to_suspect")
    
    def get_clue_relationships(self, clue_id: str, story_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get all relationships for a clue."""
        try:
            self.log_operation("get_clue_relationships", {
                "clue_id": clue_id,
                "story_id": story_id,
                "user_id": user_id
            })
            
            # Verify clue exists and user has access
            clue = self.get_clue(clue_id, story_id, user_id)
            if not clue:
                raise ResourceNotFoundError(f"Clue {clue_id} not found")
            
            # Get relationships
            relationships = self.supabase.table('clue_suspect_relationships').select('*').eq('clue_id', clue_id).execute()
            return relationships.data
            
        except Exception as e:
            self.handle_service_error(e, "get_clue_relationships") 