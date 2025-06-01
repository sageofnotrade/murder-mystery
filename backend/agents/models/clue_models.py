from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime

class ClueBase(BaseModel):
    id: str
    description: str
    location: str
    type: Literal["physical", "testimony", "observation", "document"]
    
class ClueCreate(ClueBase):
    discovery_context: Optional[str] = None
    
class ClueInDB(ClueBase):
    story_id: str
    discovery_context: Optional[str] = None
    discovered_at: datetime = Field(default_factory=datetime.now)
    
class ClueDetail(ClueInDB):
    analysis: Optional[Dict[str, Any]] = None
    related_suspects: List[str] = Field(default_factory=list)
    
class ClueConnection(BaseModel):
    id: Optional[str] = None
    story_id: str
    source_clue_id: str
    target_clue_id: str
    relationship_type: str
    description: str
    created_at: Optional[datetime] = None
    
class ClueAnalysisRequest(BaseModel):
    context: Optional[str] = None
    focus_areas: Optional[List[str]] = None 