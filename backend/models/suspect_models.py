"""
Suspect models for database operations and API responses.
Complements the SuspectAgent Pydantic models for data persistence.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class SuspectInteractionType(str, Enum):
    """Types of suspect interactions."""
    DIALOGUE = "dialogue"
    ALIBI_VERIFICATION = "alibi_verification"
    MOTIVE_EXPLORATION = "motive_exploration"
    PROFILE_GENERATION = "profile_generation"

class SuspectEmotionalState(str, Enum):
    """Possible emotional states for suspects."""
    CALM = "calm"
    NERVOUS = "nervous"
    ANXIOUS = "anxious"
    DEFENSIVE = "defensive"
    ANGRY = "angry"
    COOPERATIVE = "cooperative"
    EVASIVE = "evasive"
    SUSPICIOUS = "suspicious"

class SuspectRecord(BaseModel):
    """Database model for suspect records."""
    model_config = ConfigDict(extra="ignore")
    
    id: str
    story_id: str
    name: str
    profile_data: Dict[str, Any] = Field(default_factory=dict)
    state_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

class SuspectInteractionLog(BaseModel):
    """Model for logging suspect interactions."""
    model_config = ConfigDict(extra="ignore")
    
    id: str
    suspect_id: str
    story_id: str
    interaction_type: SuspectInteractionType
    question: Optional[str] = None
    response: Optional[str] = None
    verification_score: Optional[int] = None
    verified: Optional[bool] = None
    inconsistencies: List[str] = Field(default_factory=list)
    timestamp: datetime

class CreateSuspectRequest(BaseModel):
    """Request model for creating a new suspect."""
    model_config = ConfigDict(extra="ignore")
    
    story_id: str
    name: str
    profile_data: Optional[Dict[str, Any]] = Field(default_factory=dict)

class DialogueRequest(BaseModel):
    """Request model for suspect dialogue."""
    model_config = ConfigDict(extra="ignore")
    
    question: str
    story_id: str
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class DialogueResponse(BaseModel):
    """Response model for suspect dialogue."""
    model_config = ConfigDict(extra="ignore")
    
    suspect_id: str
    question: str
    dialogue: str
    updated_state: Dict[str, Any]
    timestamp: datetime

class AlibiVerificationRequest(BaseModel):
    """Request model for alibi verification."""
    model_config = ConfigDict(extra="ignore")
    
    story_id: str
    alibi_details: Optional[Dict[str, Any]] = Field(default_factory=dict)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)

class AlibiVerificationResponse(BaseModel):
    """Response model for alibi verification."""
    model_config = ConfigDict(extra="ignore")
    
    suspect_id: str
    alibi_verified: bool
    verification_score: int
    inconsistencies: List[str]
    dialogue_response: str
    updated_state: Dict[str, Any]
    timestamp: datetime

class StateUpdateRequest(BaseModel):
    """Request model for updating suspect state."""
    model_config = ConfigDict(extra="ignore")
    
    story_id: str
    state_updates: Dict[str, Any]

class MotiveExplorationResponse(BaseModel):
    """Response model for motive exploration."""
    model_config = ConfigDict(extra="ignore")
    
    suspect_id: str
    current_motive: Optional[str]
    potential_motives: Optional[str]
    psychological_profile: List[str]
    relationship_factors: Optional[str]
    behavioral_indicators: List[str]
    analysis_sources: List[str]
    timestamp: datetime

class ProfileGenerationRequest(BaseModel):
    """Request model for generating suspect profiles."""
    model_config = ConfigDict(extra="ignore")
    
    story_id: str
    prompt: str
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ProfileGenerationResponse(BaseModel):
    """Response model for profile generation."""
    model_config = ConfigDict(extra="ignore")
    
    suspect_id: str
    generated_profile: Dict[str, Any]
    sources: List[str]
    generation_prompt: str
    timestamp: datetime

class SuspectListItem(BaseModel):
    """Model for suspect list items."""
    model_config = ConfigDict(extra="ignore")
    
    id: str
    name: str
    suspicious_level: int = 0
    interviewed: bool = False
    emotional_state: Optional[SuspectEmotionalState] = None
    last_interaction: Optional[datetime] = None

class SuspectSummary(BaseModel):
    """Summary model for suspect overview."""
    model_config = ConfigDict(extra="ignore")
    
    id: str
    name: str
    background: Optional[str] = None
    occupation: Optional[str] = None
    motive: Optional[str] = None
    alibi: Optional[str] = None
    suspicious_level: int = 0
    interviewed: bool = False
    total_interactions: int = 0
    last_interaction: Optional[datetime] = None

class SuspectAnalytics(BaseModel):
    """Analytics model for suspect behavior tracking."""
    model_config = ConfigDict(extra="ignore")
    
    suspect_id: str
    total_questions_asked: int
    total_contradictions: int
    average_emotional_state: str
    alibi_verification_attempts: int
    alibi_verification_success_rate: float
    motive_strength_score: int
    behavioral_consistency_score: int
    interaction_timeline: List[Dict[str, Any]]

class SuspectSearchQuery(BaseModel):
    """Model for suspect search queries."""
    model_config = ConfigDict(extra="ignore")
    
    story_id: str
    name_filter: Optional[str] = None
    min_suspicious_level: Optional[int] = None
    max_suspicious_level: Optional[int] = None
    interviewed_only: Optional[bool] = None
    emotional_state_filter: Optional[List[SuspectEmotionalState]] = None
    has_motive: Optional[bool] = None
    has_alibi: Optional[bool] = None

class ErrorResponse(BaseModel):
    """Standard error response model."""
    model_config = ConfigDict(extra="ignore")
    
    error: str
    details: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow) 