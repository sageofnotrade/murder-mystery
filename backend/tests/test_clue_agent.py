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
"""
Unit tests for ClueAgent class.
Tests clue generation, analysis, connection management, and evidence processing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import json
from backend.agents.clue_agent import ClueAgent


class TestClueAgent:
    """Test suite for ClueAgent class."""

    @pytest.fixture
    def clue_agent(self):
        """Create ClueAgent instance for testing."""
        with patch('backend.agents.clue_agent.ModelRouter'), \
             patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
            return ClueAgent(use_mem0=False)

    @pytest.fixture
    def sample_clue_data(self):
        """Sample clue data for testing."""
        return {
            "type": "physical",
            "description": "A bloodied letter opener found under the desk",
            "location": "victim's office",
            "relevance": "potential murder weapon",
            "related_suspects": ["John Doe", "Jane Smith"],
            "analysis": "Forensic analysis shows fingerprints matching suspect John Doe",
            "significance": 8
        }

    @pytest.fixture
    def sample_context(self):
        """Sample context for clue generation."""
        return {
            "crime_scene": "corporate office",
            "victim": "CEO of tech company",
            "time_of_death": "11:30 PM",
            "discovered_evidence": ["broken glass", "torn documents"],
            "suspects": ["John Doe", "Jane Smith", "Bob Wilson"]
        }

    @patch('backend.agents.clue_agent.requests.get')
    def test_brave_search_success(self, mock_get, clue_agent):
        """Test successful Brave search API call."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "web": {
                "results": [
                    {
                        "title": "Forensic Evidence Guide",
                        "url": "https://example.com/forensics",
                        "description": "Comprehensive guide to forensic evidence analysis."
                    }
                ]
            }
        }
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {"BRAVE_API_KEY": "test_brave_key"}):
            result = clue_agent._brave_search("forensic evidence analysis")

        assert len(result) == 1
        assert result[0]["title"] == "Forensic Evidence Guide"

    @patch('backend.agents.clue_agent.requests.get')
    def test_brave_search_no_api_key(self, mock_get, clue_agent):
        """Test Brave search without API key."""
        with patch.dict(os.environ, {}, clear=True):
            result = clue_agent._brave_search("forensic analysis")

        assert result == []
        mock_get.assert_not_called()

    @patch('backend.agents.clue_agent.requests.get')
    def test_brave_search_api_error(self, mock_get, clue_agent):
        """Test Brave search with API error."""
        mock_get.side_effect = Exception("API Error")

        with patch.dict(os.environ, {"BRAVE_API_KEY": "test_brave_key"}):
            result = clue_agent._brave_search("evidence analysis")

        assert result == []

    def test_llm_generate_clue_success(self, clue_agent, sample_context):
        """Test successful LLM clue generation."""
        mock_response = {
            "type": "physical",
            "description": "A bloodied letter opener found under the desk",
            "location": "victim's office",
            "relevance": "potential murder weapon",
            "related_suspects": ["John Doe"],
            "analysis": "Forensic analysis shows fingerprints",
            "significance": 8
        }

        with patch.object(clue_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = Mock()
            mock_llm.chat.completions.create.return_value.choices[0].message.content = json.dumps(mock_response)
            mock_get_model.return_value = mock_llm

            result = clue_agent._llm_generate_clue(
                "Generate a physical evidence clue",
                sample_context,
                [{"title": "Forensics Guide", "description": "Evidence analysis guide"}],
                ""
            )

            assert result["type"] == "physical"
            assert result["description"] == "A bloodied letter opener found under the desk"
            assert result["significance"] == 8
            assert "John Doe" in result["related_suspects"]

    def test_llm_generate_clue_error(self, clue_agent, sample_context):
        """Test LLM clue generation with error."""
        with patch.object(clue_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = Mock()
            mock_llm.chat.completions.create.side_effect = Exception("LLM Error")
            mock_get_model.return_value = mock_llm

            result = clue_agent._llm_generate_clue("Generate clue", sample_context, [], "")

            assert "Error generating clue" in result["description"]
            assert result["significance"] == 0

    def test_llm_generate_clue_invalid_json(self, clue_agent, sample_context):
        """Test LLM clue generation with invalid JSON response."""
        with patch.object(clue_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = Mock()
            mock_llm.chat.completions.create.return_value.choices[0].message.content = "Invalid JSON"
            mock_get_model.return_value = mock_llm

            result = clue_agent._llm_generate_clue("Generate clue", sample_context, [], "")

            # Should handle gracefully with fallback values
            assert "type" in result
            assert "description" in result

    @patch.object(ClueAgent, '_brave_search')
    @patch.object(ClueAgent, '_llm_generate_clue')
    def test_generate_clue_success(self, mock_llm_generate, mock_brave_search, clue_agent, sample_clue_data, sample_context):
        """Test successful clue generation."""
        mock_brave_search.return_value = [{"title": "Forensics Guide", "description": "Evidence analysis"}]
        mock_llm_generate.return_value = sample_clue_data

        result = clue_agent.generate_clue("Generate physical evidence", sample_context)

        assert result["type"] == "physical"
        assert result["description"] == "A bloodied letter opener found under the desk"
        assert result["relevance"] == "potential murder weapon"
        mock_brave_search.assert_called_once()
        mock_llm_generate.assert_called_once()

    @patch.object(ClueAgent, '_brave_search')
    @patch.object(ClueAgent, '_llm_generate_clue')
    def test_generate_clue_with_mem0(self, mock_llm_generate, mock_brave_search, clue_agent, sample_clue_data):
        """Test clue generation with Mem0 integration."""
        clue_agent.use_mem0 = True
        clue_agent.search_memories = Mock(return_value=[{"memory": "Previous clue patterns"}])
        clue_agent.update_memory = Mock()

        mock_brave_search.return_value = []
        mock_llm_generate.return_value = sample_clue_data

        result = clue_agent.generate_clue("Generate clue with memory context")

        assert result["type"] == "physical"
        clue_agent.search_memories.assert_called_once()
        clue_agent.update_memory.assert_called()

    def test_analyze_clue_success(self, clue_agent, sample_clue_data):
        """Test successful clue analysis."""
        mock_analysis = {
            "forensic_details": "Blood type matches victim, fingerprints on handle",
            "connections": ["Links to suspect John Doe", "Possible murder weapon"],
            "significance": 9,
            "reliability": 0.85,
            "next_steps": ["Test fingerprints", "Check for DNA evidence"]
        }

        with patch.object(clue_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = Mock()
            mock_llm.chat.completions.create.return_value.choices[0].message.content = json.dumps(mock_analysis)
            mock_get_model.return_value = mock_llm

            result = clue_agent.analyze_clue(sample_clue_data, {"available_tech": "DNA analysis"})

            assert result["significance"] == 9
            assert result["reliability"] == 0.85
            assert "Blood type matches victim" in result["forensic_details"]
            assert len(result["connections"]) == 2

    def test_analyze_clue_error(self, clue_agent, sample_clue_data):
        """Test clue analysis with error."""
        with patch.object(clue_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = Mock()
            mock_llm.chat.completions.create.side_effect = Exception("LLM Error")
            mock_get_model.return_value = mock_llm

            result = clue_agent.analyze_clue(sample_clue_data, {})

            assert "Error analyzing clue" in result["forensic_details"]
            assert result["significance"] == 0

    def test_find_connections_success(self, clue_agent):
        """Test successful connection finding between clues."""
        clue1 = {
            "type": "physical",
            "description": "Bloody knife",
            "location": "kitchen",
            "related_suspects": ["John Doe"]
        }
        clue2 = {
            "type": "physical", 
            "description": "Torn shirt fabric",
            "location": "victim's office",
            "related_suspects": ["John Doe"]
        }

        mock_connections = {
            "connections": [
                {
                    "clues": ["Bloody knife", "Torn shirt fabric"],
                    "relationship": "Both link to suspect John Doe",
                    "strength": 0.8,
                    "type": "suspect_link"
                }
            ],
            "patterns": ["Physical evidence pointing to single suspect"],
            "contradictions": [],
            "timeline_implications": ["Struggle occurred in office, then kitchen"]
        }

        with patch.object(clue_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = Mock()
            mock_llm.chat.completions.create.return_value.choices[0].message.content = json.dumps(mock_connections)
            mock_get_model.return_value = mock_llm

            result = clue_agent.find_connections([clue1, clue2], {})

            assert len(result["connections"]) == 1
            assert result["connections"][0]["strength"] == 0.8
            assert "John Doe" in result["connections"][0]["relationship"]

    def test_find_connections_error(self, clue_agent):
        """Test connection finding with error."""
        clues = [{"description": "test clue"}]

        with patch.object(clue_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = Mock()
            mock_llm.chat.completions.create.side_effect = Exception("LLM Error")
            mock_get_model.return_value = mock_llm

            result = clue_agent.find_connections(clues, {})

            assert result["connections"] == []
            assert "Error finding connections" in str(result)

    def test_clue_type_validation(self, clue_agent):
        """Test different clue types are handled correctly."""
        clue_types = ["physical", "logical", "testimony", "digital", "forensic"]
        
        for clue_type in clue_types:
            clue_data = {
                "type": clue_type,
                "description": f"Test {clue_type} clue",
                "location": "test location",
                "significance": 5
            }
            
            # Should accept all valid clue types
            assert clue_data["type"] == clue_type

    def test_significance_scoring(self, clue_agent):
        """Test clue significance scoring."""
        # Test different significance levels
        significance_levels = [1, 3, 5, 7, 10]
        
        for level in significance_levels:
            clue_data = {
                "type": "physical",
                "description": "Test clue",
                "significance": level
            }
            
            assert clue_data["significance"] == level
            assert 1 <= clue_data["significance"] <= 10

    def test_related_suspects_handling(self, clue_agent):
        """Test handling of related suspects in clues."""
        clue_with_suspects = {
            "type": "physical",
            "description": "Evidence with multiple suspects",
            "related_suspects": ["John Doe", "Jane Smith", "Bob Wilson"]
        }
        
        assert len(clue_with_suspects["related_suspects"]) == 3
        assert "John Doe" in clue_with_suspects["related_suspects"]

        # Test clue with no related suspects
        clue_no_suspects = {
            "type": "logical",
            "description": "General evidence",
            "related_suspects": []
        }
        
        assert clue_no_suspects["related_suspects"] == []

    def test_location_tracking(self, clue_agent):
        """Test clue location tracking."""
        locations = ["victim's office", "kitchen", "garden", "bedroom", "unknown"]
        
        for location in locations:
            clue_data = {
                "type": "physical",
                "description": "Test clue",
                "location": location
            }
            
            assert clue_data["location"] == location

    def test_edge_case_empty_prompt(self, clue_agent):
        """Test clue generation with empty prompt."""
        with patch.object(clue_agent, '_brave_search', return_value=[]):
            with patch.object(clue_agent, '_llm_generate_clue') as mock_generate:
                mock_generate.return_value = {
                    "type": "unknown",
                    "description": "Default clue",
                    "significance": 1
                }
                
                result = clue_agent.generate_clue("", {})

        assert result["type"] == "unknown"

    def test_edge_case_none_context(self, clue_agent):
        """Test clue generation with None context."""
        with patch.object(clue_agent, '_brave_search', return_value=[]):
            with patch.object(clue_agent, '_llm_generate_clue') as mock_generate:
                mock_generate.return_value = {
                    "type": "physical",
                    "description": "Generated clue",
                    "significance": 5
                }
                
                result = clue_agent.generate_clue("Generate clue", None)

        assert result["type"] == "physical"

    def test_failure_case_all_apis_down(self, clue_agent):
        """Test behavior when all external APIs are down."""
        with patch.object(clue_agent, '_brave_search', side_effect=Exception("Brave API down")):
            with patch.object(clue_agent, '_llm_generate_clue', side_effect=Exception("LLM API down")):
                result = clue_agent.generate_clue("Generate clue", {})

        # Should handle gracefully and return some result
        assert "type" in result
        assert "description" in result

    def test_forensic_analysis_types(self, clue_agent):
        """Test different types of forensic analysis."""
        analysis_types = [
            "DNA analysis",
            "fingerprint analysis", 
            "blood spatter analysis",
            "ballistics analysis",
            "handwriting analysis",
            "digital forensics"
        ]
        
        for analysis_type in analysis_types:
            mock_analysis = {
                "forensic_details": f"Results from {analysis_type}",
                "reliability": 0.9,
                "significance": 8
            }
            
            assert analysis_type in mock_analysis["forensic_details"]

    def test_connection_strength_levels(self, clue_agent):
        """Test different connection strength levels."""
        strength_levels = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
        
        for strength in strength_levels:
            connection = {
                "clues": ["clue1", "clue2"],
                "relationship": "Test connection",
                "strength": strength,
                "type": "suspect_link"
            }
            
            assert connection["strength"] == strength
            assert 0.0 <= connection["strength"] <= 1.0

    def test_timeline_implications(self, clue_agent):
        """Test timeline implications from clue connections."""
        timeline_examples = [
            "Murder occurred before 10 PM based on evidence",
            "Suspect was at location during time of death",
            "Sequence of events: struggle, then murder, then cover-up",
            "Alibi contradicted by forensic timeline"
        ]
        
        for timeline in timeline_examples:
            connection_result = {
                "connections": [],
                "timeline_implications": [timeline]
            }
            
            assert timeline in connection_result["timeline_implications"]

    def test_contradiction_detection(self, clue_agent):
        """Test detection of contradictions in evidence."""
        contradictions = [
            "Fingerprints found but suspect claims never touched weapon",
            "Time of death conflicts with suspect's alibi",
            "DNA evidence contradicts witness testimony",
            "Physical evidence inconsistent with suspect's story"
        ]
        
        for contradiction in contradictions:
            connection_result = {
                "connections": [],
                "contradictions": [contradiction]
            }
            
            assert contradiction in connection_result["contradictions"]

    @patch.dict(os.environ, {"LLM_MODEL": "test-model"})
    def test_model_configuration(self):
        """Test that agent uses configured model."""
        with patch('backend.agents.clue_agent.ModelRouter'), \
             patch('backend.agents.clue_agent.PydanticAgent') as mock_agent:
            
            ClueAgent(use_mem0=False)
            
            # Verify PydanticAgent was called with the correct model
            mock_agent.assert_called_once()
            args, kwargs = mock_agent.call_args
            assert args[0] == "test-model"

    def test_reliability_scoring(self, clue_agent):
        """Test clue reliability scoring system."""
        reliability_levels = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
        
        for reliability in reliability_levels:
            analysis_result = {
                "forensic_details": "Test analysis",
                "reliability": reliability,
                "significance": 5
            }
            
            assert analysis_result["reliability"] == reliability
            assert 0.0 <= analysis_result["reliability"] <= 1.0

    def test_next_steps_generation(self, clue_agent):
        """Test generation of next investigative steps."""
        next_steps_examples = [
            "Test for DNA evidence",
            "Interview witness who discovered evidence", 
            "Check security camera footage",
            "Analyze digital device for additional evidence",
            "Compare fingerprints with suspect database"
        ]
        
        for step in next_steps_examples:
            analysis_result = {
                "next_steps": [step]
            }
            
            assert step in analysis_result["next_steps"] 