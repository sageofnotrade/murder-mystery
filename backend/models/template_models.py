from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class Suspect(BaseModel):
    """Pydantic model for suspects in mystery templates."""
    id: Optional[str] = None
    name: str = Field(..., description="Name of the suspect")
    occupation: str = Field(..., description="Suspect's occupation")
    background: str = Field(..., description="Background information")
    motive: str = Field(..., description="Potential motive for the crime")
    alibi: str = Field(..., description="Suspect's alibi")
    personality_traits: List[str] = Field(default_factory=list, description="Personality traits")
    relationship_to_victim: str = Field(..., description="Relationship to the victim")
    suspicious_behavior: List[str] = Field(default_factory=list, description="Suspicious behaviors")

class Clue(BaseModel):
    """Pydantic model for clues in mystery templates."""
    id: Optional[str] = None
    type: str = Field(..., description="Type of clue (physical, logical, testimony, digital)")
    description: str = Field(..., description="Description of the clue")
    location: str = Field(..., description="Where the clue was found")
    significance: int = Field(default=5, ge=1, le=10, description="Significance level (1-10)")
    reliability: float = Field(default=0.8, ge=0.0, le=1.0, description="Reliability score")
    discovered_by: Optional[str] = None
    evidence_data: Dict[str, Any] = Field(default_factory=dict, description="Additional evidence data")

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