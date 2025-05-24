from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime
from uuid import UUID

class PlayerAction(BaseModel):
    action_type: Literal["choice", "free_text", "examine", "interact"]
    content: str
    target_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class NarrativeSegment(BaseModel):
    id: str
    text: str
    character: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
class StoryChoice(BaseModel):
    id: str
    text: str
    consequences: Optional[str] = None
    
class StoryState(BaseModel):
    id: Optional[UUID] = None
    mystery_id: UUID
    current_scene: str
    narrative_history: List[NarrativeSegment] = Field(default_factory=list)
    discovered_clues: List[Dict[str, Any]] = Field(default_factory=list)
    suspect_states: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    player_choices: List[StoryChoice] = Field(default_factory=list)
    last_action: Optional[PlayerAction] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class StoryResponse(BaseModel):
    story_id: UUID
    narrative: str
    choices: List[StoryChoice]
    discovered_clues: List[Dict[str, Any]]
    suspect_states: Dict[str, Dict[str, Any]]
    current_scene: str
    timestamp: datetime = Field(default_factory=datetime.now) 