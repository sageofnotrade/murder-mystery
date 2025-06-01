from typing import Dict, Any
from pydantic import BaseModel

class PlayerProfile(BaseModel):
    psychological_traits: Dict[str, float]
    preferences: Dict[str, Any]
    play_history: Dict[str, Any]
