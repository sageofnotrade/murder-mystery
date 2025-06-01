from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# --- Nested Models ---

class Victim(BaseModel):
    name: str
    description: Optional[str] = None
    cause_of_death: Optional[str] = None
    time_of_death: Optional[str] = None
    found_by: Optional[str] = None
    background: Optional[str] = None
    relationship_to_player: Optional[str] = None

class CrimeScene(BaseModel):
    location: str
    locked_from: Optional[str] = None
    entry_points: Optional[List[str]] = None
    notable_features: Optional[List[str]] = None

class PlayerCharacter(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    occupation: Optional[str] = None
    known_motive: Optional[str] = None
    memory_state: Optional[str] = None
    physical_evidence: Optional[List[str]] = None
    is_player: Optional[bool] = None
    actual_guilt: Optional[str] = None
    truth: Optional[str] = None
    relationship_to_town: Optional[str] = None
    witness_perspective: Optional[str] = None
    limitations: Optional[List[str]] = None
    personal_stake: Optional[str] = None

class Investigator(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    personality: Optional[str] = None
    belief_in_player_guilt: Optional[float] = None
    interrogation_style: Optional[str] = None
    investigation_style: Optional[str] = None
    relationship_to_suspects: Optional[str] = None
    weakness: Optional[str] = None

class Townsperson(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None
    helpfulness: Optional[str] = None
    knowledge: Optional[str] = None
    attitude_to_player: Optional[str] = None

class MemoryFragment(BaseModel):
    id: Optional[str] = None
    trigger: Optional[str] = None
    content: Optional[str] = None
    emotional_tone: Optional[str] = None
    reliability: Optional[str] = None

class PlayerPhotograph(BaseModel):
    id: Optional[str] = None
    description: Optional[str] = None
    captured_evidence: Optional[str] = None
    clarity: Optional[str] = None
    enhancement_possible: Optional[bool] = None
    enhanced_reveals: Optional[str] = None
    contradicts: Optional[str] = None

class PlayerOption(BaseModel):
    benefits: Optional[List[str]] = None
    risks: Optional[List[str]] = None

class NarrativePath(BaseModel):
    trigger: Optional[str] = None
    requirements: Optional[List[str]] = None
    outcome: Optional[str] = None

class RedHerring(BaseModel):
    id: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    misleading_conclusion: Optional[str] = None
    actual_explanation: Optional[str] = None

class TimelineEvent(BaseModel):
    time: str
    event: str

class Solution(BaseModel):
    perpetrator: Optional[str] = None
    method: Optional[str] = None
    motive: Optional[str] = None
    key_evidence: Optional[List[str]] = None

# --- Existing Models (with updates) ---

class Suspect(BaseModel):
    id: Optional[str]
    name: str
    motive: Optional[str]
    alibi: Optional[str]
    guilty: bool
    relationship: Optional[str] = None
    alibi_strength: Optional[str] = None
    personality: Optional[str] = None
    secrets: Optional[List[str]] = None
    initial_suspicion: Optional[int] = None
    guilt_evidence: Optional[List[str]] = None
    red_herring: Optional[str] = None
    # Add more fields as needed

class Clue(BaseModel):
    id: Optional[str]
    type: str
    description: str
    found_at: Optional[str] = None
    location: Optional[str] = None
    relevance: Optional[str] = None
    related_suspects: Optional[List[str]] = None
    visibility: Optional[str] = None
    fingerprints: Optional[List[str]] = None
    matches: Optional[str] = None
    discovery_difficulty: Optional[str] = None
    source: Optional[str] = None
    reliability: Optional[str] = None
    accessible_to_player: Optional[bool] = None
    trigger: Optional[str] = None
    # Add more fields as needed

class MysteryTemplate(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: Optional[str]
    title: str
    description: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_time: Optional[str] = None
    player_role: Optional[str] = None
    psychological_profile_weights: Optional[Dict[str, float]] = None
    setting: Optional[Dict[str, Any]] = None
    victim: Optional[Victim] = None
    crime_scene: Optional[CrimeScene] = None
    player_character: Optional[PlayerCharacter] = None
    suspects: List[Suspect] = Field(default_factory=list)
    investigators: Optional[List[Investigator]] = None
    townspeople: Optional[List[Townsperson]] = None
    clues: List[Clue] = Field(default_factory=list)
    memory_fragments: Optional[List[MemoryFragment]] = None
    player_photographs: Optional[List[PlayerPhotograph]] = None
    red_herrings: Optional[List[RedHerring]] = None
    timeline: Optional[List[TimelineEvent]] = None
    solution: Optional[Solution] = None
    player_options: Optional[Dict[str, PlayerOption]] = None
    narrative_paths: Optional[Dict[str, NarrativePath]] = None
    narrative_hooks: Optional[List[str]] = None
    player_abilities: Optional[Dict[str, Any]] = None
    difficulty_adjustments: Optional[Dict[str, Any]] = None
    psychological_elements: Optional[Dict[str, str]] = None
    # Add more fields as needed

class PopulatedMysteryTemplate(MysteryTemplate):
    # Inherits all fields, but all variables should be filled
    pass
