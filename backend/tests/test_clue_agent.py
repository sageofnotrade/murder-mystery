import unittest
from backend.agents.clue_agent import ClueAgent
from backend.agents.models.psychological_profile import (
    PsychologicalProfile,
    create_default_profile,
    TraitIntensity,
    CognitiveStyle,
    EmotionalTendency,
    SocialStyle
)
from unittest.mock import patch, MagicMock

class TestClueAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ClueAgent()
        self.default_profile = create_default_profile()
        
    def test_clue_presentation_with_profile(self):
        """Test presenting a clue with a psychological profile."""
        clue = "A bloody knife was found in the kitchen sink."
        
        result = self.agent._llm_present_clue(
            clue=clue,
            context={"player_profile": self.default_profile}
        )
        
        self.assertIsInstance(result, str)
        self.assertIn(clue, result)
        
    def test_cognitive_style_adaptation(self):
        """Test that cognitive style affects clue presentation."""
        # Create profiles with different cognitive styles
        analytical_profile = create_default_profile()
        analytical_profile.cognitive_style = CognitiveStyle.ANALYTICAL
        
        intuitive_profile = create_default_profile()
        intuitive_profile.cognitive_style = CognitiveStyle.INTUITIVE
        
        clue = "The victim's diary was found open to a page dated the day before the murder."
        
        # Present clue with different profiles
        analytical_result = self.agent._llm_present_clue(
            clue=clue,
            context={"player_profile": analytical_profile}
        )
        
        intuitive_result = self.agent._llm_present_clue(
            clue=clue,
            context={"player_profile": intuitive_profile}
        )
        
        # Compare presentations
        self.assertNotEqual(analytical_result, intuitive_result)
        
    def test_emotional_tendency_adaptation(self):
        """Test that emotional tendency affects clue presentation."""
        # Create profiles with different emotional tendencies
        reserved_profile = create_default_profile()
        reserved_profile.emotional_tendency = EmotionalTendency.RESERVED
        
        expressive_profile = create_default_profile()
        expressive_profile.emotional_tendency = EmotionalTendency.EXPRESSIVE
        
        clue = "The victim's last words were written in blood on the wall."
        
        # Present clue with different profiles
        reserved_result = self.agent._llm_present_clue(
            clue=clue,
            context={"player_profile": reserved_profile}
        )
        
        expressive_result = self.agent._llm_present_clue(
            clue=clue,
            context={"player_profile": expressive_profile}
        )
        
        # Compare presentations
        self.assertNotEqual(reserved_result, expressive_result)
        
    def test_trait_intensity_impact(self):
        """Test that trait intensity affects clue presentation."""
        # Create profiles with different trait intensities
        high_curiosity_profile = create_default_profile()
        high_curiosity_profile.traits["curiosity"] = TraitIntensity.VERY_HIGH
        
        low_curiosity_profile = create_default_profile()
        low_curiosity_profile.traits["curiosity"] = TraitIntensity.VERY_LOW
        
        clue = "A mysterious package arrived at the victim's house the morning of the murder."
        
        # Present clue with different profiles
        high_curiosity_result = self.agent._llm_present_clue(
            clue=clue,
            context={"player_profile": high_curiosity_profile}
        )
        
        low_curiosity_result = self.agent._llm_present_clue(
            clue=clue,
            context={"player_profile": low_curiosity_profile}
        )
        
        # Compare presentations
        self.assertNotEqual(high_curiosity_result, low_curiosity_result)
        
    def test_clue_complexity_adaptation(self):
        """Test that clue complexity is adapted based on profile."""
        # Create profiles with different cognitive styles
        analytical_profile = create_default_profile()
        analytical_profile.cognitive_style = CognitiveStyle.ANALYTICAL
        
        intuitive_profile = create_default_profile()
        intuitive_profile.cognitive_style = CognitiveStyle.INTUITIVE
        
        complex_clue = "The victim's computer shows multiple failed login attempts from an IP address that matches the suspect's phone."
        
        # Present complex clue with different profiles
        analytical_result = self.agent._llm_present_clue(
            clue=complex_clue,
            context={"player_profile": analytical_profile}
        )
        
        intuitive_result = self.agent._llm_present_clue(
            clue=complex_clue,
            context={"player_profile": intuitive_profile}
        )
        
        # Compare presentations
        self.assertNotEqual(analytical_result, intuitive_result)

# Mock OpenAIModel and OpenAIProvider
@patch('backend.agents.model_router.OpenAIModel')
@patch('backend.agents.model_router.OpenAIProvider')
def test_clue_agent_functionality(mock_openai_provider, mock_openai_model):
    # Setup mock behavior
    mock_openai_model.return_value = MagicMock()
    mock_openai_provider.return_value = MagicMock()

    # Initialize ClueAgent
    clue_agent = ClueAgent()

    # Test a basic functionality
    result = clue_agent.some_method()  # Replace with an actual method call
    assert result is not None

if __name__ == '__main__':
    unittest.main() 