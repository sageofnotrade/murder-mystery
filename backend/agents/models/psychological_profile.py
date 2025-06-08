"""
Psychological profiling models and utilities for Murþrą.
Defines the structure and behavior of psychological traits that influence the narrative and character interactions.
Includes Big Five personality model integration for comprehensive personality assessment.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional
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

class BigFiveTrait(str, Enum):
    """Big Five personality traits."""
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"

class BigFiveScore(BaseModel):
    """Score for a Big Five personality trait."""
    model_config = ConfigDict(extra="ignore")

    trait: BigFiveTrait
    score: float = Field(ge=1.0, le=5.0, description="Score from 1.0 to 5.0")

    @property
    def level(self) -> str:
        """Get descriptive level based on score."""
        if self.score >= 4.5:
            return "very_high"
        elif self.score >= 3.5:
            return "high"
        elif self.score >= 2.5:
            return "moderate"
        elif self.score >= 1.5:
            return "low"
        else:
            return "very_low"

    @property
    def narrative_impact(self) -> Dict[str, str]:
        """Get narrative impact based on trait and score level."""
        impacts = {
            BigFiveTrait.OPENNESS: {
                "very_high": {"mystery_complexity": "very_high", "clue_obscurity": "high", "theory_encouragement": "maximum"},
                "high": {"mystery_complexity": "high", "clue_obscurity": "moderate", "theory_encouragement": "high"},
                "moderate": {"mystery_complexity": "moderate", "clue_obscurity": "moderate", "theory_encouragement": "moderate"},
                "low": {"mystery_complexity": "low", "clue_obscurity": "low", "theory_encouragement": "minimal"},
                "very_low": {"mystery_complexity": "very_low", "clue_obscurity": "very_low", "theory_encouragement": "none"}
            },
            BigFiveTrait.CONSCIENTIOUSNESS: {
                "very_high": {"detail_tracking": "meticulous", "evidence_organization": "systematic", "investigation_approach": "methodical"},
                "high": {"detail_tracking": "thorough", "evidence_organization": "organized", "investigation_approach": "structured"},
                "moderate": {"detail_tracking": "adequate", "evidence_organization": "moderate", "investigation_approach": "balanced"},
                "low": {"detail_tracking": "casual", "evidence_organization": "loose", "investigation_approach": "flexible"},
                "very_low": {"detail_tracking": "minimal", "evidence_organization": "chaotic", "investigation_approach": "impulsive"}
            },
            BigFiveTrait.EXTRAVERSION: {
                "very_high": {"social_interaction": "dominant", "npc_engagement": "aggressive", "group_dynamics": "leadership"},
                "high": {"social_interaction": "active", "npc_engagement": "proactive", "group_dynamics": "participatory"},
                "moderate": {"social_interaction": "balanced", "npc_engagement": "moderate", "group_dynamics": "cooperative"},
                "low": {"social_interaction": "reserved", "npc_engagement": "cautious", "group_dynamics": "observational"},
                "very_low": {"social_interaction": "withdrawn", "npc_engagement": "minimal", "group_dynamics": "isolated"}
            },
            BigFiveTrait.AGREEABLENESS: {
                "very_high": {"suspect_treatment": "trusting", "conflict_resolution": "peaceful", "moral_flexibility": "high"},
                "high": {"suspect_treatment": "empathetic", "conflict_resolution": "diplomatic", "moral_flexibility": "moderate"},
                "moderate": {"suspect_treatment": "fair", "conflict_resolution": "balanced", "moral_flexibility": "moderate"},
                "low": {"suspect_treatment": "skeptical", "conflict_resolution": "direct", "moral_flexibility": "low"},
                "very_low": {"suspect_treatment": "suspicious", "conflict_resolution": "confrontational", "moral_flexibility": "rigid"}
            },
            BigFiveTrait.NEUROTICISM: {
                "very_high": {"stress_response": "overwhelmed", "decision_confidence": "very_low", "pressure_handling": "poor"},
                "high": {"stress_response": "anxious", "decision_confidence": "low", "pressure_handling": "difficult"},
                "moderate": {"stress_response": "manageable", "decision_confidence": "moderate", "pressure_handling": "adequate"},
                "low": {"stress_response": "calm", "decision_confidence": "high", "pressure_handling": "good"},
                "very_low": {"stress_response": "unflappable", "decision_confidence": "very_high", "pressure_handling": "excellent"}
            }
        }
        return impacts.get(self.trait, {}).get(self.level, {})

class BigFiveProfile(BaseModel):
    """Complete Big Five personality profile."""
    model_config = ConfigDict(extra="ignore")

    openness: BigFiveScore
    conscientiousness: BigFiveScore
    extraversion: BigFiveScore
    agreeableness: BigFiveScore
    neuroticism: BigFiveScore

    def get_dominant_traits(self, threshold: float = 3.5) -> List[BigFiveTrait]:
        """Get traits that score above the threshold."""
        dominant = []
        for score in [self.openness, self.conscientiousness, self.extraversion, self.agreeableness, self.neuroticism]:
            if score.score >= threshold:
                dominant.append(score.trait)
        return dominant

    def get_narrative_adaptations(self) -> Dict[str, str]:
        """Get combined narrative adaptations from all Big Five traits."""
        adaptations = {}
        for score in [self.openness, self.conscientiousness, self.extraversion, self.agreeableness, self.neuroticism]:
            adaptations.update(score.narrative_impact)
        return adaptations

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
    big_five: Optional[BigFiveProfile] = Field(
        default=None,
        description="Big Five personality assessment results"
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

        # Add Big Five adaptations if available
        if self.big_five:
            big_five_adaptations = self.big_five.get_narrative_adaptations()
            adaptations.update(big_five_adaptations)
            adaptations["big_five_scores"] = {
                "openness": self.big_five.openness.score,
                "conscientiousness": self.big_five.conscientiousness.score,
                "extraversion": self.big_five.extraversion.score,
                "agreeableness": self.big_five.agreeableness.score,
                "neuroticism": self.big_five.neuroticism.score
            }

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

        # Add Big Five dialogue adaptations if available
        if self.big_five:
            # Big Five traits influence dialogue style
            if self.big_five.extraversion.score >= 3.5:
                adaptations["social_confidence"] = "high"
                adaptations["conversation_initiation"] = "proactive"
            else:
                adaptations["social_confidence"] = "low"
                adaptations["conversation_initiation"] = "reactive"

            if self.big_five.agreeableness.score >= 3.5:
                adaptations["conflict_approach"] = "diplomatic"
                adaptations["suspect_questioning"] = "gentle"
            else:
                adaptations["conflict_approach"] = "direct"
                adaptations["suspect_questioning"] = "aggressive"

            if self.big_five.neuroticism.score >= 3.5:
                adaptations["emotional_stability"] = "low"
                adaptations["pressure_response"] = "stressed"
            else:
                adaptations["emotional_stability"] = "high"
                adaptations["pressure_response"] = "calm"

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

def calculate_big_five_from_responses(responses: Dict[str, float]) -> BigFiveProfile:
    """Calculate Big Five personality scores from questionnaire responses."""

    # Question mapping to Big Five traits
    # Each question ID maps to (trait, weight) where weight can be positive or negative
    question_mapping = {
        # Openness questions
        "openness_1": (BigFiveTrait.OPENNESS, 1.0),  # enjoy unraveling complex puzzles
        "openness_2": (BigFiveTrait.OPENNESS, 1.0),  # imagine alternate endings
        "openness_3": (BigFiveTrait.OPENNESS, 1.0),  # explore strange theories
        "openness_4": (BigFiveTrait.OPENNESS, 1.0),  # quirky characters catch attention
        "openness_5": (BigFiveTrait.OPENNESS, 1.0),  # notice tiny details

        # Conscientiousness questions
        "conscientiousness_1": (BigFiveTrait.CONSCIENTIOUSNESS, 1.0),  # prefer clear plan
        "conscientiousness_2": (BigFiveTrait.CONSCIENTIOUSNESS, 1.0),  # take notes and records
        "conscientiousness_3": (BigFiveTrait.CONSCIENTIOUSNESS, 1.0),  # see tasks through
        "conscientiousness_4": (BigFiveTrait.CONSCIENTIOUSNESS, 1.0),  # frustrated by recklessness
        "conscientiousness_5": (BigFiveTrait.CONSCIENTIOUSNESS, 1.0),  # double-check clues

        # Extraversion questions
        "extraversion_1": (BigFiveTrait.EXTRAVERSION, 1.0),  # energized by new people
        "extraversion_2": (BigFiveTrait.EXTRAVERSION, 1.0),  # volunteer to question suspects
        "extraversion_3": (BigFiveTrait.EXTRAVERSION, 1.0),  # enjoy center of action
        "extraversion_4": (BigFiveTrait.EXTRAVERSION, 1.0),  # act on instinct
        "extraversion_5": (BigFiveTrait.EXTRAVERSION, 1.0),  # prefer group work

        # Agreeableness questions
        "agreeableness_1": (BigFiveTrait.AGREEABLENESS, 1.0),  # give benefit of doubt
        "agreeableness_2": (BigFiveTrait.AGREEABLENESS, 1.0),  # keep the peace
        "agreeableness_3": (BigFiveTrait.AGREEABLENESS, 1.0),  # feel bad accusing
        "agreeableness_4": (BigFiveTrait.AGREEABLENESS, 1.0),  # understand motives
        "agreeableness_5": (BigFiveTrait.AGREEABLENESS, 1.0),  # help cover mistakes

        # Neuroticism questions
        "neuroticism_1": (BigFiveTrait.NEUROTICISM, 1.0),  # second-guess decisions
        "neuroticism_2": (BigFiveTrait.NEUROTICISM, 1.0),  # get nervous under pressure
        "neuroticism_3": (BigFiveTrait.NEUROTICISM, 1.0),  # take things personally
        "neuroticism_4": (BigFiveTrait.NEUROTICISM, 1.0),  # lose sleep over mysteries
        "neuroticism_5": (BigFiveTrait.NEUROTICISM, 1.0),  # worry about missing obvious
    }

    # Calculate scores for each trait
    trait_scores = {trait: [] for trait in BigFiveTrait}

    for question_id, response_value in responses.items():
        if question_id in question_mapping:
            trait, weight = question_mapping[question_id]
            weighted_score = response_value * weight
            trait_scores[trait].append(weighted_score)

    # Calculate average scores
    final_scores = {}
    for trait in BigFiveTrait:
        if trait_scores[trait]:
            final_scores[trait] = sum(trait_scores[trait]) / len(trait_scores[trait])
        else:
            final_scores[trait] = 3.0  # Default neutral score

    # Create BigFiveProfile
    return BigFiveProfile(
        openness=BigFiveScore(trait=BigFiveTrait.OPENNESS, score=final_scores[BigFiveTrait.OPENNESS]),
        conscientiousness=BigFiveScore(trait=BigFiveTrait.CONSCIENTIOUSNESS, score=final_scores[BigFiveTrait.CONSCIENTIOUSNESS]),
        extraversion=BigFiveScore(trait=BigFiveTrait.EXTRAVERSION, score=final_scores[BigFiveTrait.EXTRAVERSION]),
        agreeableness=BigFiveScore(trait=BigFiveTrait.AGREEABLENESS, score=final_scores[BigFiveTrait.AGREEABLENESS]),
        neuroticism=BigFiveScore(trait=BigFiveTrait.NEUROTICISM, score=final_scores[BigFiveTrait.NEUROTICISM])
    )

def create_profile_from_questionnaire(responses: Dict[str, float]) -> PsychologicalProfile:
    """Create a complete psychological profile from questionnaire responses."""
    big_five = calculate_big_five_from_responses(responses)

    # Derive cognitive style from Big Five
    if big_five.openness.score >= 3.5:
        cognitive_style = CognitiveStyle.INTUITIVE
    else:
        cognitive_style = CognitiveStyle.ANALYTICAL

    # Derive emotional tendency from Big Five
    if big_five.neuroticism.score >= 3.5:
        emotional_tendency = EmotionalTendency.EXPRESSIVE
    elif big_five.neuroticism.score <= 2.5:
        emotional_tendency = EmotionalTendency.RESERVED
    else:
        emotional_tendency = EmotionalTendency.MODERATE

    # Derive social style from Big Five
    if big_five.extraversion.score >= 3.5:
        social_style = SocialStyle.DIRECT
    elif big_five.extraversion.score <= 2.5:
        social_style = SocialStyle.INDIRECT
    else:
        social_style = SocialStyle.BALANCED

    return PsychologicalProfile(
        cognitive_style=cognitive_style,
        emotional_tendency=emotional_tendency,
        social_style=social_style,
        big_five=big_five,
        traits={
            "curiosity": PsychologicalTrait(
                name="curiosity",
                intensity=TraitIntensity.HIGH if big_five.openness.score >= 3.5 else TraitIntensity.MODERATE,
                description="Natural inclination to explore and discover",
                narrative_impact={
                    "clue_presentation": "immediate" if big_five.openness.score >= 4.0 else "gradual",
                    "mystery_pacing": "fast" if big_five.openness.score >= 4.0 else "engaging"
                },
                dialogue_impact={
                    "question_style": "intense" if big_five.openness.score >= 4.0 else "inquisitive",
                    "interaction_approach": "exploratory"
                }
            ),
            "empathy": PsychologicalTrait(
                name="empathy",
                intensity=TraitIntensity.HIGH if big_five.agreeableness.score >= 3.5 else TraitIntensity.MODERATE,
                description="Ability to understand and share feelings",
                narrative_impact={
                    "character_depth": "high" if big_five.agreeableness.score >= 3.5 else "moderate",
                    "emotional_content": "rich" if big_five.agreeableness.score >= 3.5 else "balanced"
                },
                dialogue_impact={
                    "response_style": "empathetic",
                    "interaction_tone": "understanding"
                }
            ),
            "perceptiveness": PsychologicalTrait(
                name="perceptiveness",
                intensity=TraitIntensity.HIGH if big_five.conscientiousness.score >= 3.5 else TraitIntensity.MODERATE,
                description="Keen observation skills",
                narrative_impact={
                    "detail_level": "very_high" if big_five.conscientiousness.score >= 4.0 else "high",
                    "clue_presentation": "immediate" if big_five.conscientiousness.score >= 4.0 else "gradual"
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