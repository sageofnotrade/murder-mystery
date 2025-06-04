from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID

class ClueType(BaseModel):
    """Represents different types of clues in the mystery."""
    id: str
    name: str
    description: str
    category: str  # physical, logical, testimony, digital

class Clue(BaseModel):
    """Represents a clue in the mystery investigation."""
    id: Optional[str] = None
    type: str
    description: str
    location: Optional[str] = None
    discovered_by: Optional[str] = None
    discovery_time: Optional[datetime] = None
    significance: int = Field(default=5, ge=1, le=10)
    reliability: float = Field(default=0.8, ge=0.0, le=1.0)
    connections: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_data: Dict[str, Any] = Field(default_factory=dict)
    analysis_notes: str = ""
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class ClueAnalysis(BaseModel):
    """Represents the analysis of a clue."""
    clue_id: str
    forensic_details: List[str] = Field(default_factory=list)
    timeline_implications: List[str] = Field(default_factory=list)
    suspect_connections: List[Dict[str, Any]] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    confidence_score: float = Field(default=0.7, ge=0.0, le=1.0)

class ClueConnection(BaseModel):
    """Represents a connection between clues."""
    source_clue_id: str
    target_clue_id: str
    connection_type: str  # supports, contradicts, explains, leads_to
    strength: float = Field(default=0.5, ge=0.0, le=1.0)
    explanation: str = ""
    discovered_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        } 