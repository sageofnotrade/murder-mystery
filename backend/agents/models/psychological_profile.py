"""
Psychological profiling models and utilities for Murþrą.
Defines the structure and behavior of psychological traits that influence the narrative and character interactions.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional, Union
from enum import Enum

class TraitIntensity(str, Enum):
    """Intensity levels for psychological traits."""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

    @property
    def narrative_impact(self) -> Dict[str, str]:
        """Return narrative impact based on intensity."""
        if self == TraitIntensity.VERY_HIGH:
            return {"detail_level": "very_high", "pacing": "fast"}
        elif self == TraitIntensity.HIGH:
            return {"detail_level": "high", "pacing": "dynamic"}
        elif self == TraitIntensity.MODERATE:
            return {"detail_level": "moderate", "pacing": "balanced"}
        elif self == TraitIntensity.LOW:
            return {"detail_level": "low", "pacing": "slow"}
        else:
            return {"detail_level": "very_low", "pacing": "very_slow"}

    @property
    def dialogue_impact(self) -> Dict[str, str]:
        """Return dialogue impact based on intensity."""
        if self == TraitIntensity.VERY_HIGH:
            return {"response_style": "intense", "interaction_approach": "aggressive"}
        elif self == TraitIntensity.HIGH:
            return {"response_style": "detailed", "interaction_approach": "exploratory"}
        elif self == TraitIntensity.MODERATE:
            return {"response_style": "balanced", "interaction_approach": "neutral"}
        elif self == TraitIntensity.LOW:
            return {"response_style": "passive", "interaction_approach": "reactive"}
        else:
            return {"response_style": "very_passive", "interaction_approach": "very_reactive"}

class CognitiveStyle(str, Enum):
    """Different cognitive processing styles."""
    ANALYTICAL = "analytical"
    INTUITIVE = "intuitive"
    BALANCED = "balanced"

class EmotionalTendency(str, Enum):
    """Emotional response tendencies."""
    RESERVED = "reserved"
    EXPRESSIVE = "expressive"
    MODERATE = "moderate"

class SocialStyle(str, Enum):
    """Social interaction preferences."""
    DIRECT = "direct"
    INDIRECT = "indirect"
    BALANCED = "balanced"

class PsychologicalTrait(BaseModel):
    """Model for individual psychological traits."""
    model_config = ConfigDict(extra="ignore")

    name: str
    intensity: TraitIntensity
    description: str
    narrative_impact: Dict[str, str] = Field(
        default_factory=dict,
        description="How this trait affects narrative elements"
    )
    dialogue_impact: Dict[str, str] = Field(
        default_factory=dict,
        description="How this trait affects dialogue and interactions"
    )

class PsychologicalProfile(BaseModel):
    """Complete psychological profile for a player."""
    model_config = ConfigDict(extra="ignore")

    cognitive_style: CognitiveStyle = Field(
        default=CognitiveStyle.ANALYTICAL,
        description="How the player processes information"
    )
    emotional_tendency: EmotionalTendency = Field(
        default=EmotionalTendency.MODERATE,
        description="How the player tends to respond emotionally"
    )
    social_style: SocialStyle = Field(
        default=SocialStyle.BALANCED,
        description="How the player prefers to interact socially"
    )
    traits: Dict[str, PsychologicalTrait] = Field(
        default_factory=dict,
        description="Specific psychological traits"
    )
    preferences: Dict[str, str] = Field(
        default_factory=dict,
        description="Player preferences for story elements"
    )

    def get_narrative_adaptations(self) -> Dict[str, str]:
        """Get narrative adaptations based on the profile."""
        adaptations = {}
        
        # Adapt based on cognitive style
        if self.cognitive_style == CognitiveStyle.ANALYTICAL:
            adaptations["detail_level"] = "high"
            adaptations["pacing"] = "methodical"
            adaptations["cognitive_style"] = "analytical"
        elif self.cognitive_style == CognitiveStyle.INTUITIVE:
            adaptations["detail_level"] = "moderate"
            adaptations["pacing"] = "dynamic"
            adaptations["cognitive_style"] = "intuitive"

        # Adapt based on emotional tendency
        if self.emotional_tendency == EmotionalTendency.RESERVED:
            adaptations["tone"] = "subtle"
            adaptations["emotional_content"] = "restrained"
            adaptations["emotional_tendency"] = "reserved"
        elif self.emotional_tendency == EmotionalTendency.EXPRESSIVE:
            adaptations["tone"] = "vivid"
            adaptations["emotional_content"] = "rich"
            adaptations["emotional_tendency"] = "expressive"

        # Adapt based on social style
        if self.social_style == SocialStyle.DIRECT:
            adaptations["dialogue_style"] = "straightforward"
            adaptations["interaction_pace"] = "quick"
        elif self.social_style == SocialStyle.INDIRECT:
            adaptations["dialogue_style"] = "nuanced"
            adaptations["interaction_pace"] = "measured"
        # Always include social_style
        adaptations["social_style"] = self.social_style.value

        # Add adaptations from individual traits
        for trait in self.traits.values():
            adaptations.update(trait.narrative_impact)

        # Add traits intensity mapping
        adaptations["traits"] = {k: (v if isinstance(v, str) else v.intensity.value if hasattr(v, 'intensity') else str(v)) for k, v in self.traits.items()}

        return adaptations

    def get_dialogue_adaptations(self) -> Dict[str, str]:
        """Get dialogue adaptations based on the profile."""
        adaptations = {}
        
        # Adapt based on cognitive style
        if self.cognitive_style == CognitiveStyle.ANALYTICAL:
            adaptations["response_style"] = "detailed"
            adaptations["question_preference"] = "specific"
            adaptations["cognitive_style"] = "analytical"
        elif self.cognitive_style == CognitiveStyle.INTUITIVE:
            adaptations["response_style"] = "concise"
            adaptations["question_preference"] = "open-ended"
            adaptations["cognitive_style"] = "intuitive"

        # Adapt based on emotional tendency
        if self.emotional_tendency == EmotionalTendency.RESERVED:
            adaptations["emotional_expression"] = "subtle"
            adaptations["reaction_style"] = "measured"
            adaptations["emotional_tendency"] = "reserved"
        elif self.emotional_tendency == EmotionalTendency.EXPRESSIVE:
            adaptations["emotional_expression"] = "vivid"
            adaptations["reaction_style"] = "immediate"
            adaptations["emotional_tendency"] = "expressive"

        # Adapt based on social style
        if self.social_style == SocialStyle.DIRECT:
            adaptations["communication_style"] = "direct"
            adaptations["confrontation_style"] = "straightforward"
        elif self.social_style == SocialStyle.INDIRECT:
            adaptations["communication_style"] = "diplomatic"
            adaptations["confrontation_style"] = "circumspect"
        # Always include social_style
        adaptations["social_style"] = self.social_style.value

        # Add adaptations from individual traits
        for trait in self.traits.values():
            adaptations.update(trait.dialogue_impact)

        # Add traits intensity mapping
        adaptations["traits"] = {k: (v if isinstance(v, str) else v.intensity.value if hasattr(v, 'intensity') else str(v)) for k, v in self.traits.items()}

        return adaptations

def create_default_profile() -> PsychologicalProfile:
    """Create a default psychological profile."""
    return PsychologicalProfile(
        cognitive_style=CognitiveStyle.ANALYTICAL,
        emotional_tendency=EmotionalTendency.RESERVED,
        social_style=SocialStyle.DIRECT,
        traits={
            "curiosity": PsychologicalTrait(
                name="curiosity",
                intensity=TraitIntensity.MODERATE,
                description="Natural inclination to explore and discover",
                narrative_impact={
                    "clue_presentation": "gradual",
                    "mystery_pacing": "engaging"
                },
                dialogue_impact={
                    "question_style": "inquisitive",
                    "interaction_approach": "exploratory"
                }
            ),
            "empathy": PsychologicalTrait(
                name="empathy",
                intensity=TraitIntensity.MODERATE,
                description="Ability to understand and share feelings",
                narrative_impact={
                    "character_depth": "moderate",
                    "emotional_content": "balanced"
                },
                dialogue_impact={
                    "response_style": "empathetic",
                    "interaction_tone": "understanding"
                }
            ),
            "perceptiveness": PsychologicalTrait(
                name="perceptiveness",
                intensity=TraitIntensity.MODERATE,
                description="Keen observation skills",
                narrative_impact={
                    "detail_level": "high",
                    "clue_presentation": "immediate"
                },
                dialogue_impact={
                    "observation_style": "detailed",
                    "interaction_approach": "observant"
                }
            )
        }
    )

# --- Tests ---
import unittest

class PsychologicalProfileTest(unittest.TestCase):
    def setUp(self):
        self.default_profile = create_default_profile()

    def test_default_profile_creation(self):
        """Test that default profile is created with expected values."""
        profile = create_default_profile()
        self.assertEqual(profile.cognitive_style, CognitiveStyle.ANALYTICAL)
        self.assertEqual(profile.emotional_tendency, EmotionalTendency.MODERATE)
        self.assertEqual(profile.social_style, SocialStyle.BALANCED)
        self.assertIn("curiosity", profile.traits)
        self.assertIn("empathy", profile.traits)

    def test_analytical_cognitive_style(self):
        """Test narrative adaptations for analytical cognitive style."""
        profile = PsychologicalProfile(
            cognitive_style=CognitiveStyle.ANALYTICAL,
            emotional_tendency=EmotionalTendency.MODERATE,
            social_style=SocialStyle.BALANCED
        )
        adaptations = profile.get_narrative_adaptations()
        self.assertEqual(adaptations["detail_level"], "high")
        self.assertEqual(adaptations["pacing"], "methodical")

    def test_intuitive_cognitive_style(self):
        """Test narrative adaptations for intuitive cognitive style."""
        profile = PsychologicalProfile(
            cognitive_style=CognitiveStyle.INTUITIVE,
            emotional_tendency=EmotionalTendency.MODERATE,
            social_style=SocialStyle.BALANCED
        )
        adaptations = profile.get_narrative_adaptations()
        self.assertEqual(adaptations["detail_level"], "moderate")
        self.assertEqual(adaptations["pacing"], "dynamic")

    def test_reserved_emotional_tendency(self):
        """Test narrative adaptations for reserved emotional tendency."""
        profile = PsychologicalProfile(
            cognitive_style=CognitiveStyle.ANALYTICAL,
            emotional_tendency=EmotionalTendency.RESERVED,
            social_style=SocialStyle.BALANCED
        )
        adaptations = profile.get_narrative_adaptations()
        self.assertEqual(adaptations["tone"], "subtle")
        self.assertEqual(adaptations["emotional_content"], "restrained")

    def test_expressive_emotional_tendency(self):
        """Test narrative adaptations for expressive emotional tendency."""
        profile = PsychologicalProfile(
            cognitive_style=CognitiveStyle.ANALYTICAL,
            emotional_tendency=EmotionalTendency.EXPRESSIVE,
            social_style=SocialStyle.BALANCED
        )
        adaptations = profile.get_narrative_adaptations()
        self.assertEqual(adaptations["tone"], "vivid")
        self.assertEqual(adaptations["emotional_content"], "rich")

    def test_direct_social_style(self):
        """Test narrative adaptations for direct social style."""
        profile = PsychologicalProfile(
            cognitive_style=CognitiveStyle.ANALYTICAL,
            emotional_tendency=EmotionalTendency.MODERATE,
            social_style=SocialStyle.DIRECT
        )
        adaptations = profile.get_narrative_adaptations()
        self.assertEqual(adaptations["dialogue_style"], "straightforward")
        self.assertEqual(adaptations["interaction_pace"], "quick")

    def test_indirect_social_style(self):
        """Test narrative adaptations for indirect social style."""
        profile = PsychologicalProfile(
            cognitive_style=CognitiveStyle.ANALYTICAL,
            emotional_tendency=EmotionalTendency.MODERATE,
            social_style=SocialStyle.INDIRECT
        )
        adaptations = profile.get_narrative_adaptations()
        self.assertEqual(adaptations["dialogue_style"], "nuanced")
        self.assertEqual(adaptations["interaction_pace"], "measured")

    def test_custom_trait_impact(self):
        """Test that custom traits affect narrative and dialogue adaptations."""
        profile = PsychologicalProfile(
            cognitive_style=CognitiveStyle.ANALYTICAL,
            emotional_tendency=EmotionalTendency.MODERATE,
            social_style=SocialStyle.BALANCED,
            traits={
                "perceptiveness": PsychologicalTrait(
                    name="perceptiveness",
                    intensity=TraitIntensity.HIGH,
                    description="Keen observation skills",
                    narrative_impact={
                        "detail_level": "very_high",
                        "clue_presentation": "immediate"
                    },
                    dialogue_impact={
                        "observation_style": "detailed",
                        "interaction_approach": "observant"
                    }
                )
            }
        )
        narrative_adaptations = profile.get_narrative_adaptations()
        dialogue_adaptations = profile.get_dialogue_adaptations()
        
        self.assertEqual(narrative_adaptations["detail_level"], "very_high")
        self.assertEqual(narrative_adaptations["clue_presentation"], "immediate")
        self.assertEqual(dialogue_adaptations["observation_style"], "detailed")
        self.assertEqual(dialogue_adaptations["interaction_approach"], "observant")

    def test_trait_intensity_impact(self):
        """Test that trait intensity affects adaptations."""
        # Create profiles with different intensities of the same trait
        high_curiosity = PsychologicalProfile(
            cognitive_style=CognitiveStyle.ANALYTICAL,
            emotional_tendency=EmotionalTendency.MODERATE,
            social_style=SocialStyle.BALANCED,
            traits={
                "curiosity": PsychologicalTrait(
                    name="curiosity",
                    intensity=TraitIntensity.VERY_HIGH,
                    description="Extremely curious",
                    narrative_impact={
                        "clue_presentation": "immediate",
                        "mystery_pacing": "fast"
                    },
                    dialogue_impact={
                        "question_style": "intense",
                        "interaction_approach": "aggressive"
                    }
                )
            }
        )

        low_curiosity = PsychologicalProfile(
            cognitive_style=CognitiveStyle.ANALYTICAL,
            emotional_tendency=EmotionalTendency.MODERATE,
            social_style=SocialStyle.BALANCED,
            traits={
                "curiosity": PsychologicalTrait(
                    name="curiosity",
                    intensity=TraitIntensity.LOW,
                    description="Minimal curiosity",
                    narrative_impact={
                        "clue_presentation": "gradual",
                        "mystery_pacing": "slow"
                    },
                    dialogue_impact={
                        "question_style": "passive",
                        "interaction_approach": "reactive"
                    }
                )
            }
        )

        # Compare adaptations
        high_adaptations = high_curiosity.get_narrative_adaptations()
        low_adaptations = low_curiosity.get_narrative_adaptations()

        self.assertNotEqual(
            high_adaptations["clue_presentation"],
            low_adaptations["clue_presentation"]
        )
        self.assertNotEqual(
            high_adaptations["mystery_pacing"],
            low_adaptations["mystery_pacing"]
        )

if __name__ == "__main__":
    unittest.main() 