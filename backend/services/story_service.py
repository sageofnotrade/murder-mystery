from typing import List, Dict, Optional, Any
from datetime import datetime
from uuid import UUID
import json
from supabase import create_client, Client
from models.story_models import StoryState, PlayerAction, NarrativeSegment, StoryChoice, StoryResponse

class StoryService:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    async def create_story(self, mystery_id: UUID) -> StoryState:
        """Create a new story instance for a mystery."""
        # Get mystery template
        mystery = self.supabase.table('mysteries').select('*').eq('id', str(mystery_id)).single().execute()
        if not mystery.data:
            raise ValueError(f"Mystery {mystery_id} not found")

        # Initialize story state
        story_state = StoryState(
            mystery_id=mystery_id,
            current_scene="introduction",
            narrative_history=[],
            discovered_clues=[],
            suspect_states={},
            player_choices=[]
        )

        # Save to database
        result = self.supabase.table('stories').insert({
            'mystery_id': str(mystery_id),
            'current_scene': story_state.current_scene,
            'narrative_history': json.dumps([n.dict() for n in story_state.narrative_history]),
            'discovered_clues': json.dumps(story_state.discovered_clues),
            'suspect_states': json.dumps(story_state.suspect_states)
        }).execute()

        story_state.id = UUID(result.data[0]['id'])
        return story_state

    async def get_story(self, story_id: UUID) -> StoryState:
        """Retrieve a story's current state."""
        result = self.supabase.table('stories').select('*').eq('id', str(story_id)).single().execute()
        if not result.data:
            raise ValueError(f"Story {story_id} not found")

        data = result.data
        return StoryState(
            id=UUID(data['id']),
            mystery_id=UUID(data['mystery_id']),
            current_scene=data['current_scene'],
            narrative_history=[NarrativeSegment(**n) for n in json.loads(data['narrative_history'])],
            discovered_clues=json.loads(data['discovered_clues']),
            suspect_states=json.loads(data['suspect_states'])
        )

    async def process_action(self, story_id: UUID, action: PlayerAction) -> StoryResponse:
        """Process a player action and update the story state."""
        story = await self.get_story(story_id)
        
        # Update story state based on action
        story.last_action = action
        
        # TODO: Integrate with StoryAgent to generate narrative response
        # For now, return a mock response
        narrative = f"Processing {action.action_type} action: {action.content}"
        choices = [
            StoryChoice(id="1", text="Continue investigation"),
            StoryChoice(id="2", text="Examine clues")
        ]

        # Update database
        self.supabase.table('stories').update({
            'current_scene': story.current_scene,
            'narrative_history': json.dumps([n.dict() for n in story.narrative_history]),
            'discovered_clues': json.dumps(story.discovered_clues),
            'suspect_states': json.dumps(story.suspect_states)
        }).eq('id', str(story_id)).execute()

        return StoryResponse(
            story_id=story_id,
            narrative=narrative,
            choices=choices,
            discovered_clues=story.discovered_clues,
            suspect_states=story.suspect_states,
            current_scene=story.current_scene
        )

    async def save_story_state(self, story: StoryState) -> None:
        """Save the current state of a story."""
        self.supabase.table('stories').update({
            'current_scene': story.current_scene,
            'narrative_history': json.dumps([n.dict() for n in story.narrative_history]),
            'discovered_clues': json.dumps(story.discovered_clues),
            'suspect_states': json.dumps(story.suspect_states)
        }).eq('id', str(story.id)).execute()

    async def get_available_choices(self, story_id: UUID) -> List[StoryChoice]:
        """Get the available choices for the current story state."""
        story = await self.get_story(story_id)
        return story.player_choices 