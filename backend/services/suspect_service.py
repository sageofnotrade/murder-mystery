"""
SuspectService for managing suspect data and interactions.
Integrates with SuspectAgent for AI-driven dialogue and analysis.
"""

from typing import Dict, Any, List, Optional
import uuid
import logging
from backend.agents.suspect_agent import (
    SuspectAgent, 
    SuspectProfile, 
    SuspectState, 
    SuspectProfileOutput,
    SuspectDialogueOutput
)
from backend.services.supabase_service import get_supabase_client
from supabase import Client
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class SuspectService:
    """Service for handling suspect operations and integrating with SuspectAgent."""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.suspect_agent = SuspectAgent(use_mem0=True)
    
    async def get_story_suspects(self, story_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get all suspects for a specific story."""
        try:
            # Query suspects for the story, ensuring user has access
            response = self.supabase.table('suspects').select('*').eq('story_id', story_id).execute()
            
            # Verify user has access to the story
            story_response = self.supabase.table('stories').select('user_id').eq('id', story_id).execute()
            if not story_response.data or story_response.data[0]['user_id'] != user_id:
                raise ValueError("User does not have access to this story")
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting suspects for story {story_id}: {str(e)}")
            raise
    
    async def get_suspect_profile(self, suspect_id: str, story_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific suspect profile."""
        try:
            # Verify user has access to the story
            story_response = self.supabase.table('stories').select('user_id').eq('id', story_id).execute()
            if not story_response.data or story_response.data[0]['user_id'] != user_id:
                return None
            
            # Get suspect profile
            response = self.supabase.table('suspects').select('*').eq('id', suspect_id).eq('story_id', story_id).execute()
            
            if response.data:
                suspect_data = response.data[0]
                # Parse JSON fields if they exist
                if 'profile_data' in suspect_data and suspect_data['profile_data']:
                    if isinstance(suspect_data['profile_data'], str):
                        suspect_data['profile_data'] = json.loads(suspect_data['profile_data'])
                return suspect_data
            return None
        except Exception as e:
            logger.error(f"Error getting suspect profile {suspect_id}: {str(e)}")
            raise
    
    async def create_suspect(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new suspect."""
        try:
            suspect_id = str(uuid.uuid4())
            story_id = data.get('story_id')
            
            if not story_id:
                raise ValueError("story_id is required")
            
            # Verify user has access to the story
            story_response = self.supabase.table('stories').select('user_id').eq('id', story_id).execute()
            if not story_response.data or story_response.data[0]['user_id'] != user_id:
                raise ValueError("User does not have access to this story")
            
            # Create suspect record
            suspect_record = {
                'id': suspect_id,
                'story_id': story_id,
                'name': data.get('name', 'Unknown Suspect'),
                'profile_data': json.dumps(data.get('profile_data', {})),
                'state_data': json.dumps({
                    'name': data.get('name', 'Unknown Suspect'),
                    'interviewed': False,
                    'suspicious_level': 0,
                    'known_information': [],
                    'contradictions': [],
                    'emotional_state': None
                }),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            response = self.supabase.table('suspects').insert(suspect_record).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise ValueError("Failed to create suspect")
                
        except Exception as e:
            logger.error(f"Error creating suspect: {str(e)}")
            raise
    
    async def generate_dialogue(self, suspect_id: str, question: str, story_id: str, 
                              user_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate dialogue response from a suspect."""
        try:
            # Get current suspect state
            suspect_data = await self.get_suspect_profile(suspect_id, story_id, user_id)
            if not suspect_data:
                raise ValueError("Suspect not found or access denied")
            
            # Parse suspect state
            state_data = suspect_data.get('state_data', {})
            if isinstance(state_data, str):
                state_data = json.loads(state_data)
            
            suspect_state = SuspectState(**state_data)
            
            # Generate dialogue using SuspectAgent
            dialogue_output = self.suspect_agent.generate_dialogue(
                question=question,
                suspect_state=suspect_state,
                context=context or {}
            )
            
            # Update suspect state in database
            updated_state_data = dialogue_output.updated_state.model_dump()
            update_response = self.supabase.table('suspects').update({
                'state_data': json.dumps(updated_state_data),
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', suspect_id).execute()
            
            # Log dialogue interaction
            await self._log_dialogue_interaction(suspect_id, story_id, question, dialogue_output.dialogue)
            
            return {
                'suspect_id': suspect_id,
                'question': question,
                'dialogue': dialogue_output.dialogue,
                'updated_state': updated_state_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating dialogue for suspect {suspect_id}: {str(e)}")
            raise
    
    async def verify_alibi(self, suspect_id: str, story_id: str, user_id: str,
                          alibi_details: Dict[str, Any], evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify a suspect's alibi."""
        try:
            # Get current suspect data
            suspect_data = await self.get_suspect_profile(suspect_id, story_id, user_id)
            if not suspect_data:
                raise ValueError("Suspect not found or access denied")
            
            # Parse current profile
            profile_data = suspect_data.get('profile_data', {})
            if isinstance(profile_data, str):
                profile_data = json.loads(profile_data)
            
            current_alibi = profile_data.get('alibi', '')
            
            # Use SuspectAgent to analyze alibi consistency
            context = {
                'current_alibi': current_alibi,
                'alibi_details': alibi_details,
                'evidence': evidence,
                'verification_type': 'alibi_check'
            }
            
            # Create a verification question
            verification_question = f"I need to verify your alibi. You said {current_alibi}. Can you provide more details about where you were and who can confirm this?"
            
            # Get current suspect state
            state_data = suspect_data.get('state_data', {})
            if isinstance(state_data, str):
                state_data = json.loads(state_data)
            suspect_state = SuspectState(**state_data)
            
            # Generate dialogue for verification
            dialogue_output = self.suspect_agent.generate_dialogue(
                question=verification_question,
                suspect_state=suspect_state,
                context=context
            )
            
            # Analyze alibi consistency (simplified logic)
            inconsistencies = []
            verification_score = 100  # Start with perfect score
            
            # Check for contradictions in the response
            if 'contradiction' in dialogue_output.dialogue.lower():
                inconsistencies.append("Contradictory statements detected")
                verification_score -= 30
            
            # Check if emotional state suggests deception
            if dialogue_output.updated_state.emotional_state in ['nervous', 'anxious', 'defensive']:
                inconsistencies.append("Suspect appears nervous or defensive")
                verification_score -= 20
            
            # Check evidence consistency
            if evidence:
                for piece in evidence:
                    if not piece.get('supports_alibi', True):
                        inconsistencies.append(f"Evidence conflicts: {piece.get('description', 'Unknown')}")
                        verification_score -= 25
            
            verification_result = {
                'suspect_id': suspect_id,
                'alibi_verified': verification_score >= 70,
                'verification_score': max(0, verification_score),
                'inconsistencies': inconsistencies,
                'dialogue_response': dialogue_output.dialogue,
                'updated_state': dialogue_output.updated_state.model_dump(),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Update suspect state
            update_response = self.supabase.table('suspects').update({
                'state_data': json.dumps(dialogue_output.updated_state.model_dump()),
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', suspect_id).execute()
            
            # Log verification attempt
            await self._log_verification_attempt(suspect_id, story_id, verification_result)
            
            return verification_result
            
        except Exception as e:
            logger.error(f"Error verifying alibi for suspect {suspect_id}: {str(e)}")
            raise
    
    async def get_suspect_state(self, suspect_id: str, story_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get the current investigation state of a suspect."""
        try:
            suspect_data = await self.get_suspect_profile(suspect_id, story_id, user_id)
            if not suspect_data:
                return None
            
            state_data = suspect_data.get('state_data', {})
            if isinstance(state_data, str):
                state_data = json.loads(state_data)
            
            return state_data
        except Exception as e:
            logger.error(f"Error getting suspect state {suspect_id}: {str(e)}")
            raise
    
    async def update_suspect_state(self, suspect_id: str, story_id: str, user_id: str,
                                  state_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update the investigation state of a suspect."""
        try:
            # Get current state
            current_state_data = await self.get_suspect_state(suspect_id, story_id, user_id)
            if not current_state_data:
                raise ValueError("Suspect not found or access denied")
            
            # Merge updates
            updated_state_data = {**current_state_data, **state_updates}
            
            # Validate the updated state
            try:
                updated_state = SuspectState(**updated_state_data)
                validated_data = updated_state.model_dump()
            except Exception as e:
                raise ValueError(f"Invalid state data: {str(e)}")
            
            # Update in database
            update_response = self.supabase.table('suspects').update({
                'state_data': json.dumps(validated_data),
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', suspect_id).execute()
            
            return validated_data
            
        except Exception as e:
            logger.error(f"Error updating suspect state {suspect_id}: {str(e)}")
            raise
    
    async def explore_motives(self, suspect_id: str, story_id: str, user_id: str) -> Dict[str, Any]:
        """Explore potential motives for a suspect."""
        try:
            suspect_data = await self.get_suspect_profile(suspect_id, story_id, user_id)
            if not suspect_data:
                raise ValueError("Suspect not found or access denied")
            
            # Parse profile data
            profile_data = suspect_data.get('profile_data', {})
            if isinstance(profile_data, str):
                profile_data = json.loads(profile_data)
            
            # Use SuspectAgent to analyze motives
            prompt = f"Analyze potential motives for suspect {suspect_data['name']}"
            context = {
                'profile': profile_data,
                'analysis_type': 'motive_exploration'
            }
            
            # Generate a comprehensive motive analysis
            motive_analysis = self.suspect_agent.generate_suspect(
                prompt=prompt,
                context=context
            )
            
            return {
                'suspect_id': suspect_id,
                'current_motive': profile_data.get('motive'),
                'potential_motives': motive_analysis.profile.motive,
                'psychological_profile': motive_analysis.profile.personality_traits,
                'relationship_factors': motive_analysis.profile.relationship_to_victim,
                'behavioral_indicators': motive_analysis.profile.suspicious_behaviors,
                'analysis_sources': motive_analysis.sources,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error exploring motives for suspect {suspect_id}: {str(e)}")
            raise
    
    async def generate_suspect_profile(self, suspect_id: str, story_id: str, user_id: str,
                                     prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate or regenerate a suspect profile using AI."""
        try:
            # Use SuspectAgent to generate profile
            profile_output = self.suspect_agent.generate_suspect(
                prompt=prompt,
                context=context
            )
            
            # Update suspect in database
            profile_data = profile_output.profile.model_dump()
            update_response = self.supabase.table('suspects').update({
                'name': profile_output.profile.name,
                'profile_data': json.dumps(profile_data),
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', suspect_id).execute()
            
            return {
                'suspect_id': suspect_id,
                'generated_profile': profile_data,
                'sources': profile_output.sources,
                'generation_prompt': prompt,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating suspect profile {suspect_id}: {str(e)}")
            raise
    
    async def _log_dialogue_interaction(self, suspect_id: str, story_id: str, 
                                      question: str, response: str):
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
            
            # Insert into dialogue_logs table (assuming it exists)
            response = self.supabase.table('suspect_interactions').insert(log_record).execute()
        except Exception as e:
            # Log error but don't fail the main operation
            logger.warning(f"Failed to log dialogue interaction: {str(e)}")
    
    async def _log_verification_attempt(self, suspect_id: str, story_id: str, 
                                       verification_result: Dict[str, Any]):
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
            
            response = self.supabase.table('suspect_interactions').insert(log_record).execute()
        except Exception as e:
            logger.warning(f"Failed to log verification attempt: {str(e)}") 