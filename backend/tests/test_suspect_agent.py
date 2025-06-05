import unittest
from backend.agents.suspect_agent import SuspectAgent
from backend.agents.models.psychological_profile import (
    PsychologicalProfile,
    create_default_profile,
    TraitIntensity,
    CognitiveStyle,
    EmotionalTendency,
    SocialStyle
)

class TestSuspectAgent(unittest.TestCase):
    def setUp(self):
        self.agent = SuspectAgent()
        self.default_profile = create_default_profile()
        
    def test_dialogue_generation_with_profile(self):
        """Test generating dialogue with a psychological profile."""
        question = "Where were you on the night of the murder?"
        suspect_state = {
            "name": "John Doe",
            "interviewed": False,
            "suspicious_level": 0,
            "emotional_state": "calm"
        }
        
        result = self.agent._llm_generate_dialogue(
            question=question,
            suspect_state=suspect_state,
            context={"player_profile": self.default_profile}
        )
        
        self.assertIn("dialogue", result)
        self.assertIn("updated_state", result)
        
    def test_profile_adaptation(self):
        """Test that different profiles result in different dialogue styles."""
        # Create two different profiles
        direct_profile = create_default_profile()
        direct_profile.social_style = SocialStyle.DIRECT
        
        indirect_profile = create_default_profile()
        indirect_profile.social_style = SocialStyle.INDIRECT
        
        question = "What do you know about the victim?"
        suspect_state = {
            "name": "Jane Smith",
            "interviewed": False,
            "suspicious_level": 0,
            "emotional_state": "nervous"
        }
        
        # Generate dialogue with different profiles
        direct_result = self.agent._llm_generate_dialogue(
            question=question,
            suspect_state=suspect_state,
            context={"player_profile": direct_profile}
        )
        
        indirect_result = self.agent._llm_generate_dialogue(
            question=question,
            suspect_state=suspect_state,
            context={"player_profile": indirect_profile}
        )
        
        # Compare dialogues
        self.assertNotEqual(direct_result["dialogue"], indirect_result["dialogue"])
        
    def test_emotional_adaptation(self):
        """Test that emotional tendency affects dialogue."""
        # Create profiles with different emotional tendencies
        reserved_profile = create_default_profile()
        reserved_profile.emotional_tendency = EmotionalTendency.RESERVED
        
        expressive_profile = create_default_profile()
        expressive_profile.emotional_tendency = EmotionalTendency.EXPRESSIVE
        
        question = "How did you feel when you heard about the murder?"
        suspect_state = {
            "name": "Bob Wilson",
            "interviewed": False,
            "suspicious_level": 0,
            "emotional_state": "distressed"
        }
        
        # Generate dialogue with different profiles
        reserved_result = self.agent._llm_generate_dialogue(
            question=question,
            suspect_state=suspect_state,
            context={"player_profile": reserved_profile}
        )
        
        expressive_result = self.agent._llm_generate_dialogue(
            question=question,
            suspect_state=suspect_state,
            context={"player_profile": expressive_profile}
        )
        
        # Compare dialogues
        self.assertNotEqual(reserved_result["dialogue"], expressive_result["dialogue"])
        
    def test_cognitive_adaptation(self):
        """Test that cognitive style affects dialogue complexity."""
        # Create profiles with different cognitive styles
        analytical_profile = create_default_profile()
        analytical_profile.cognitive_style = CognitiveStyle.ANALYTICAL
        
        intuitive_profile = create_default_profile()
        intuitive_profile.cognitive_style = CognitiveStyle.INTUITIVE
        
        question = "What do you think happened?"
        suspect_state = {
            "name": "Alice Brown",
            "interviewed": False,
            "suspicious_level": 0,
            "emotional_state": "thoughtful"
        }
        
        # Generate dialogue with different profiles
        analytical_result = self.agent._llm_generate_dialogue(
            question=question,
            suspect_state=suspect_state,
            context={"player_profile": analytical_profile}
        )
        
        intuitive_result = self.agent._llm_generate_dialogue(
            question=question,
            suspect_state=suspect_state,
            context={"player_profile": intuitive_profile}
        )
        
        # Compare dialogues
        self.assertNotEqual(analytical_result["dialogue"], intuitive_result["dialogue"])

if __name__ == '__main__':
    unittest.main() 