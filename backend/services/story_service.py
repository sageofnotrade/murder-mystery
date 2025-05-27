from typing import List, Dict, Optional, Any
from datetime import datetime
from uuid import UUID
import json
from supabase import create_client, Client
from models.story_models import StoryState, PlayerAction, NarrativeSegment, StoryChoice, StoryResponse
from redis import Redis
import os

class StoryError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class StoryService:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.redis = Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True
        )
        self.cache_ttl = int(os.getenv('STORY_CACHE_TTL', 3600))  # 1 hour default

    async def create_story(self, mystery_id: UUID, user_id: str) -> StoryState:
        """Create a new story instance for a mystery."""
        try:
            # Get mystery template
            mystery = self.supabase.table('mysteries').select('*').eq('id', str(mystery_id)).single().execute()
            if not mystery.data:
                raise StoryError(f"Mystery {mystery_id} not found", 404)

            # Initialize story state
            story_state = StoryState(
                mystery_id=mystery_id,
                user_id=user_id,
                current_scene="introduction",
                narrative_history=[],
                discovered_clues=[],
                suspect_states={},
                player_choices=[]
            )

            # Save to database
            result = self.supabase.table('stories').insert({
                'mystery_id': str(mystery_id),
                'user_id': user_id,
                'current_scene': story_state.current_scene,
                'narrative_history': json.dumps([n.dict() for n in story_state.narrative_history]),
                'discovered_clues': json.dumps(story_state.discovered_clues),
                'suspect_states': json.dumps(story_state.suspect_states)
            }).execute()

            story_state.id = UUID(result.data[0]['id'])
            
            # Cache the new story
            self._cache_story(story_state)
            
            return story_state
        except Exception as e:
            raise StoryError(f"Error creating story: {str(e)}")

    async def get_story(self, story_id: UUID, user_id: str) -> StoryState:
        """Retrieve a story's current state."""
        try:
            # Try cache first
            cached_story = self._get_cached_story(story_id)
            if cached_story:
                if cached_story.user_id != user_id:
                    raise StoryError("Unauthorized access to story", 403)
                return cached_story

            # If not in cache, get from database
            result = self.supabase.table('stories').select('*').eq('id', str(story_id)).single().execute()
            if not result.data:
                raise StoryError(f"Story {story_id} not found", 404)

            data = result.data
            if data['user_id'] != user_id:
                raise StoryError("Unauthorized access to story", 403)

            story_state = StoryState(
                id=UUID(data['id']),
                mystery_id=UUID(data['mystery_id']),
                user_id=data['user_id'],
                current_scene=data['current_scene'],
                narrative_history=[NarrativeSegment(**n) for n in json.loads(data['narrative_history'])],
                discovered_clues=json.loads(data['discovered_clues']),
                suspect_states=json.loads(data['suspect_states'])
            )

            # Cache the story
            self._cache_story(story_state)

            return story_state
        except StoryError:
            raise
        except Exception as e:
            raise StoryError(f"Error retrieving story: {str(e)}")

    async def process_action(self, story_id: UUID, action: PlayerAction, user_id: str) -> StoryResponse:
        """Process a player action and update the story state."""
        try:
            story = await self.get_story(story_id, user_id)
            
            # Update story state based on action
            story.last_action = action
            
            # Generate narrative response using StoryAgent
            agent_response = await self.story_agent.generate_narrative(
                action=action.content,
                context={
                    'player_role': 'detective',  # Default role, can be customized
                    'current_scene': story.current_scene,
                    'discovered_clues': story.discovered_clues,
                    'suspect_states': story.suspect_states,
                    'narrative_history': [n.text for n in story.narrative_history]
                }
            )

            # Create new narrative segment
            narrative_segment = NarrativeSegment(
                id=str(UUID()),
                text=agent_response.narrative,
                timestamp=datetime.now()
            )

            # Update story state with agent response
            story.narrative_history.append(narrative_segment)
            story.current_scene = agent_response.next_scene or story.current_scene
            
            # Update discovered clues if any new ones were found
            if agent_response.new_clues:
                story.discovered_clues.extend(agent_response.new_clues)
            
            # Update suspect states if they changed
            if agent_response.suspect_updates:
                story.suspect_states.update(agent_response.suspect_updates)

            # Update available choices
            story.player_choices = [
                StoryChoice(
                    id=str(i),
                    text=choice,
                    consequences=agent_response.choice_consequences.get(choice)
                )
                for i, choice in enumerate(agent_response.available_choices, 1)
            ]

            # Update database
            self.supabase.table('stories').update({
                'current_scene': story.current_scene,
                'narrative_history': json.dumps([n.dict() for n in story.narrative_history]),
                'discovered_clues': json.dumps(story.discovered_clues),
                'suspect_states': json.dumps(story.suspect_states)
            }).eq('id', str(story_id)).execute()

            # Update cache
            self._cache_story(story)

            return StoryResponse(
                story_id=story_id,
                narrative=agent_response.narrative,
                choices=story.player_choices,
                discovered_clues=story.discovered_clues,
                suspect_states=story.suspect_states,
                current_scene=story.current_scene
            )
        except StoryError:
            raise
        except Exception as e:
            raise StoryError(f"Error processing action: {str(e)}")

    async def save_story_state(self, story: StoryState, user_id: str) -> None:
        """Save the current state of a story."""
        try:
            if story.user_id != user_id:
                raise StoryError("Unauthorized access to story", 403)

            self.supabase.table('stories').update({
                'current_scene': story.current_scene,
                'narrative_history': json.dumps([n.dict() for n in story.narrative_history]),
                'discovered_clues': json.dumps(story.discovered_clues),
                'suspect_states': json.dumps(story.suspect_states)
            }).eq('id', str(story.id)).execute()

            # Update cache
            self._cache_story(story)
        except StoryError:
            raise
        except Exception as e:
            raise StoryError(f"Error saving story state: {str(e)}")

    async def get_available_choices(self, story_id: UUID, user_id: str) -> List[StoryChoice]:
        """Get the available choices for the current story state."""
        try:
            story = await self.get_story(story_id, user_id)
            return story.player_choices
        except StoryError:
            raise
        except Exception as e:
            raise StoryError(f"Error getting available choices: {str(e)}")

    def _cache_story(self, story: StoryState) -> None:
        """Cache a story state in Redis."""
        try:
            self.redis.setex(
                f"story:{story.id}",
                self.cache_ttl,
                json.dumps(story.dict())
            )
        except Exception as e:
            # Log cache error but don't fail the request
            print(f"Cache error: {str(e)}")

    def _get_cached_story(self, story_id: UUID) -> Optional[StoryState]:
        """Get a story state from cache."""
        try:
            cached = self.redis.get(f"story:{story_id}")
            if cached:
                return StoryState(**json.loads(cached))
            return None
        except Exception as e:
            # Log cache error but don't fail the request
            print(f"Cache error: {str(e)}")
            return None 