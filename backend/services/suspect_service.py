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

class SuspectService(BaseService):
    """Service for managing suspect-related operations."""
    
    def get_suspects(self, story_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get all suspects for a story."""
        try:
            self.log_operation("get_suspects", {"story_id": story_id, "user_id": user_id})
            
            # Validate user has access to story
            story = self.supabase.table('stories').select('*').eq('id', story_id).eq('user_id', user_id).execute()
            if not story.data:
                raise AuthorizationError("User does not have access to this story")
            
            # Get suspects
            suspects = self.supabase.table('suspects').select('*').eq('story_id', story_id).execute()
            return suspects.data
            
        except Exception as e:
            self.handle_service_error(e, "get_suspects")
    
    def get_suspect_profile(self, suspect_id: str, story_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific suspect's profile."""
        try:
            self.log_operation("get_suspect_profile", {
                "suspect_id": suspect_id,
                "story_id": story_id,
                "user_id": user_id
            })
            
            # Validate user has access to story
            story = self.supabase.table('stories').select('*').eq('id', story_id).eq('user_id', user_id).execute()
            if not story.data:
                raise AuthorizationError("User does not have access to this story")
            
            # Get suspect
            suspect = self.supabase.table('suspects').select('*').eq('id', suspect_id).eq('story_id', story_id).execute()
            if not suspect.data:
                raise ResourceNotFoundError(f"Suspect {suspect_id} not found")
            
            return suspect.data[0]
                
        except Exception as e:
            self.handle_service_error(e, "get_suspect_profile")
    
    def generate_dialogue(self, suspect_id: str, question: str, story_id: str, 
                              user_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate dialogue with a suspect."""
        try:
            self.log_operation("generate_dialogue", {
                "suspect_id": suspect_id,
                "story_id": story_id,
                "user_id": user_id
            })
            
            # Validate required fields
            self.validate_required_fields(
                {"suspect_id": suspect_id, "question": question, "story_id": story_id},
                ["suspect_id", "question", "story_id"]
            )
            
            # Verify suspect exists
            suspect = self.get_suspect_profile(suspect_id, story_id, user_id)
            if not suspect:
                raise ResourceNotFoundError(f"Suspect {suspect_id} not found")
            
            # Generate dialogue (implementation depends on your AI integration)
            # This is a placeholder - replace with actual implementation
            response = {
                "text": f"Response to: {question}",
                "emotional_state": "neutral",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Log the interaction
            self._log_dialogue_interaction(suspect_id, story_id, question, response["text"])
            
            return response
            
        except Exception as e:
            self.handle_service_error(e, "generate_dialogue")
    
    def verify_alibi(self, suspect_id: str, story_id: str, user_id: str,
                          alibi_details: Dict[str, Any], evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify a suspect's alibi."""
        try:
            self.log_operation("verify_alibi", {
                "suspect_id": suspect_id,
                "story_id": story_id,
                "user_id": user_id
            })
            
            # Validate required fields
            self.validate_required_fields(
                {"suspect_id": suspect_id, "story_id": story_id, "alibi_details": alibi_details},
                ["suspect_id", "story_id", "alibi_details"]
            )
            
            # Verify suspect exists
            suspect = self.get_suspect_profile(suspect_id, story_id, user_id)
            if not suspect:
                raise ResourceNotFoundError(f"Suspect {suspect_id} not found")
            
            # Verify alibi (implementation depends on your AI integration)
            # This is a placeholder - replace with actual implementation
            verification_result = {
                "alibi_verified": True,
                "verification_score": 0.8,
                "inconsistencies": [],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Log the verification attempt
            self._log_verification_attempt(suspect_id, story_id, verification_result)
            
            return verification_result
            
        except Exception as e:
            self.handle_service_error(e, "verify_alibi")
    
    def _log_dialogue_interaction(self, suspect_id: str, story_id: str, 
                                question: str, response: str) -> None:
        """Log dialogue interaction for analytics."""
        try:
            log_record = {
                'id': str(uuid.uuid4()),
                'suspect_id': suspect_id,
                'story_id': story_id,
                'interaction_type': 'dialogue',
                'question': question,
                'response': response,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.supabase.table('suspect_interactions').insert(log_record).execute()
            self.log_operation("log_dialogue_interaction", {"suspect_id": suspect_id})
            
        except Exception as e:
            # Log error but don't fail the main operation
            logger.warning(f"Failed to log dialogue interaction: {str(e)}")
    
    def _log_verification_attempt(self, suspect_id: str, story_id: str, 
                                verification_result: Dict[str, Any]) -> None:
        """Log alibi verification attempt."""
        try:
            log_record = {
                'id': str(uuid.uuid4()),
                'suspect_id': suspect_id,
                'story_id': story_id,
                'interaction_type': 'alibi_verification',
                'verification_score': verification_result['verification_score'],
                'verified': verification_result['alibi_verified'],
                'inconsistencies': json.dumps(verification_result['inconsistencies']),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.supabase.table('suspect_interactions').insert(log_record).execute()
            self.log_operation("log_verification_attempt", {"suspect_id": suspect_id})
            
        except Exception as e:
            # Log error but don't fail the main operation
            logger.warning(f"Failed to log verification attempt: {str(e)}") 
