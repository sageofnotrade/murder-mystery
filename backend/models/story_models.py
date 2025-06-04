from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID

class NarrativeSegment(BaseModel):
    """Represents a segment of the story narrative."""
    id: str
    text: str
    timestamp: datetime
    scene: Optional[str] = None
    action_type: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class StoryChoice(BaseModel):
    """Represents a choice available to the player."""
    id: str
    text: str
    consequences: Optional[Dict[str, Any]] = None
    enabled: bool = True

class PlayerAction(BaseModel):
    """Represents an action taken by the player."""
    action_type: str  # e.g., "investigate", "question", "analyze"
    content: str
    target: Optional[str] = None  # e.g., suspect name, clue id
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class StoryState(BaseModel):
    """Represents the current state of a story."""
    id: Optional[UUID] = None
    mystery_id: UUID
    user_id: str
    current_scene: str
    narrative_history: List[NarrativeSegment] = Field(default_factory=list)
    discovered_clues: List[Dict[str, Any]] = Field(default_factory=list)
    suspect_states: Dict[str, Any] = Field(default_factory=dict)
    player_choices: List[StoryChoice] = Field(default_factory=list)
    last_action: Optional[PlayerAction] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            UUID: lambda v: str(v) if v else None
        }

class StoryResponse(BaseModel):
    """Response object for story actions."""
    story_id: UUID
    narrative: str
    choices: List[StoryChoice]
    discovered_clues: List[Dict[str, Any]]
    suspect_states: Dict[str, Any]
    current_scene: str
    new_clue_found: bool = False
    scene_completed: bool = False
    
    class Config:
        json_encoders = {
            UUID: lambda v: str(v) if v else None
        }

 