from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union, Literal
from datetime import datetime

class Suspect(BaseModel):
    name: str
    description: str
    motive: str
    alibi: str
    guilty: bool = False
    personality_traits: Dict[str, float] = Field(default_factory=dict)
    
class Clue(BaseModel):
    id: str
    description: str
    location: str
    related_suspects: List[str] = Field(default_factory=list)
    discovery_difficulty: float = 1.0
    type: Literal["physical", "testimony", "observation", "document"] 
    
class MysteryTemplate(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    setting: str
    time_period: str
    victim: Dict[str, str]
    suspects: List[Suspect]
    clues: List[Clue]
    red_herrings: List[Dict[str, str]] = Field(default_factory=list)
    difficulty: float = 1.0
    estimated_duration: str = "1 hour"
    version: str = "1.0.0"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None 