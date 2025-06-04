from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class MysteryTemplate(BaseModel):
    """Pydantic model for mystery templates."""
    
    id: Optional[str] = None
    title: str = Field(..., description="Title of the mystery template")
    description: str = Field(..., description="Description of the mystery template")
    difficulty: str = Field(default="medium", description="Difficulty level: easy, medium, hard")
    setting: str = Field(..., description="Setting where the mystery takes place")
    victim_profile: Dict[str, Any] = Field(default_factory=dict, description="Profile of the victim")
    suspect_profiles: List[Dict[str, Any]] = Field(default_factory=list, description="List of suspect profiles")
    clues: List[Dict[str, Any]] = Field(default_factory=list, description="List of clues in the mystery")
    solution: Dict[str, Any] = Field(default_factory=dict, description="Solution to the mystery")
    story_beats: List[str] = Field(default_factory=list, description="Key story progression points")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        } 