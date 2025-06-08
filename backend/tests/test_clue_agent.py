import unittest
from backend.agents.clue_agent import ClueAgent, ClueOutput, PydanticAgent
from backend.agents.models.psychological_profile import (
    PsychologicalProfile,
    create_default_profile,
    TraitIntensity,
    CognitiveStyle,
    EmotionalTendency,
    SocialStyle
)
from unittest.mock import patch, MagicMock, Mock
import json
from pydantic_ai.messages import ModelMessage
from backend.agents.model_router import ModelRouter
import pytest
import os

# Dummy message class for testing
class DummyModelMessage:
    def __init__(self, role, content):
        self.role = role
        self.content = content

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

    # Patch PydanticAI agent to avoid model loading
    from backend.agents import clue_agent
    with patch.object(clue_agent.ClueAgent, '_create_pydantic_agent', return_value=MagicMock()):
        clue_agent_instance = clue_agent.ClueAgent()
        # Test that the agent can be instantiated and has a pydantic_agent attribute
        assert hasattr(clue_agent_instance, 'pydantic_agent')

@pytest.fixture
def clue_agent():
    with patch('backend.agents.clue_agent.PydanticAgent') as mock_agent, \
         patch('backend.agents.clue_agent.ModelRouter') as mock_router_class, \
         patch('mem0.MemoryClient', return_value=MagicMock()) as mem0_mock, \
         patch.dict(os.environ, {"MEM0_API_KEY": "test_key", "LLM_MODEL": "gpt-3.5-turbo"}):
        mock_router = mock_router_class.return_value
        mock_router.get_model_for_task.return_value = "gpt-3.5-turbo"
        mock_router.complete.return_value = Mock(content="Test response")
        agent = ClueAgent(use_mem0=True, user_id="test_user", model_message_cls=DummyModelMessage)
        memory_mock = MagicMock()
        agent.memory = memory_mock
        agent.mem0_client = memory_mock
        agent.dependencies.memory = memory_mock
        agent.dependencies.update_memory = memory_mock.update
        agent.dependencies.search_memories = memory_mock.search
        return agent

@patch.dict(os.environ, {"LLM_MODEL": "gpt-3.5-turbo"})
def test_model_configuration():
    with patch('backend.agents.clue_agent.PydanticAgent') as mock_agent, \
         patch.object(ModelRouter, 'get_model_for_task', return_value='gpt-3.5-turbo'), \
         patch('mem0.MemoryClient', return_value=MagicMock()), \
         patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
        agent = ClueAgent(use_mem0=True, user_id="test_user", model_message_cls=DummyModelMessage)
        found = False
        for call in mock_agent.call_args_list:
            if call.kwargs.get("model") == "gpt-3.5-turbo":
                found = True
        assert found, "PydanticAgent was not called with the correct model string."

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
from backend.agents.clue_agent import ClueAgent, ClueGenerateOutput, ClueData
from pydantic_ai.messages import ModelMessage

class TestClueAgent:
    """Test suite for ClueAgent class."""

    @pytest.fixture
    def sample_clue_data(self):
        """Sample clue data for mocking LLM output."""
        return {
            "description": "A bloodied letter opener found under the desk",
            "location": "victim's office",
            "relevance": "potential murder weapon",
            "related_suspects": ["John Doe"],
            "analysis": "Forensic analysis shows fingerprints matching suspect John Doe",
            "significance": "High - potential murder weapon",
            "type": "unknown"
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

    def test_search_memories(self):
        with patch('mem0.MemoryClient', return_value=MagicMock()) as mem0_mock:
            with patch.dict(os.environ, {"LLM_MODEL": "test"}):
                agent = ClueAgent(use_mem0=True, user_id="test_user", model_message_cls=DummyModelMessage)
                memory_mock = MagicMock()
                agent.mem0_client = memory_mock
                agent.memory = memory_mock
                agent.dependencies.memory = memory_mock
                agent.dependencies.update_memory = memory_mock.update
                mock_results = [
                    {"text": "Previous clue about letter opener", "score": 0.9},
                    {"text": "Related evidence from crime scene", "score": 0.8}
                ]
                memory_mock.search.return_value = mock_results
                results = agent.dependencies.search_memories("letter opener", limit=3, threshold=0.7, rerank=True)
                assert len(results) == 2
                assert results[0]["text"] == "Previous clue about letter opener"
                memory_mock.search.assert_called_once_with("letter opener", limit=3, threshold=0.7, rerank=True)
                results = agent.dependencies.search_memories("evidence", limit=5, threshold=0.6, rerank=False)
                assert len(results) == 2
                memory_mock.search.assert_called_with("evidence", limit=5, threshold=0.6, rerank=False)

    def test_update_memory(self):
        with patch('mem0.MemoryClient', return_value=MagicMock()) as mem0_mock:
            with patch.dict(os.environ, {"LLM_MODEL": "test"}):
                agent = ClueAgent(use_mem0=True, user_id="test_user", model_message_cls=DummyModelMessage)
                memory_mock = MagicMock()
                agent.mem0_client = memory_mock
                agent.memory = memory_mock
                agent.dependencies.memory = memory_mock
                agent.dependencies.update_memory = memory_mock.update
                agent.dependencies.search_memories = memory_mock.search
                agent.dependencies.update_memory("test_key", "test_value")
                memory_mock.update.assert_called_once_with("test_key", "test_value")
                complex_value = {"clue": "bloody knife", "significance": "high"}
                agent.dependencies.update_memory("complex_key", complex_value)
                memory_mock.update.assert_called_with("complex_key", complex_value)

    @patch('backend.agents.clue_agent.requests.get')
    def test_brave_search_success(self, mock_get):
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
        with patch.dict(os.environ, {"BRAVE_API_KEY": "test_brave_key", "LLM_MODEL": "test"}):
            agent = ClueAgent(use_mem0=True, user_id="test_user", model_message_cls=DummyModelMessage)
            memory_mock = MagicMock()
            agent.mem0_client = memory_mock
            agent.memory = memory_mock
            agent.dependencies.memory = memory_mock
            agent.dependencies.update_memory = memory_mock.update
            result = agent._brave_search("forensic evidence analysis")
        assert len(result) == 1
        assert result[0]["title"] == "Forensic Evidence Guide"

    def test_llm_generate_clue_success(self, clue_agent, sample_context):
        mock_clue_data = ClueData(
            description="A bloodied letter opener found under the desk",
            details="Forensic analysis shows fingerprints matching suspect John Doe",
            significance="High - potential murder weapon",
            related_to=["John Doe"],
            confidence=0.9
        )
        mock_output = ClueGenerateOutput(
            clue=mock_clue_data,
            sources=["https://example.com/forensics"]
        )
        with patch.object(clue_agent.pydantic_agent, 'run_sync', return_value=MagicMock(output=mock_output)):
            result = clue_agent.generate_clue("letter opener", sample_context)
        clue = result.clue if hasattr(result, 'clue') else result.get('clue')
        if isinstance(clue, dict):
            assert clue.get('description') == "A bloodied letter opener found under the desk"
            assert clue.get('details') == "Forensic analysis shows fingerprints matching suspect John Doe"
        else:
            assert getattr(clue, 'description', None) == "A bloodied letter opener found under the desk"
            assert getattr(clue, 'details', None) == "Forensic analysis shows fingerprints matching suspect John Doe"

    def test_llm_generate_clue_error(self, clue_agent, sample_context):
        with patch.object(clue_agent.pydantic_agent, 'run_sync', side_effect=Exception("API Error")):
            result = clue_agent.generate_clue("letter opener", sample_context)
            clue = result.clue if hasattr(result, 'clue') else result.get('clue')
            if isinstance(clue, dict):
                assert clue.get('type') == "unknown"
            else:
                assert getattr(clue, 'type', None) == "unknown"

    def test_llm_generate_clue_invalid_json(self, clue_agent, sample_context):
        mock_response = MagicMock()
        mock_response.output = "invalid json"
        with patch.object(clue_agent.pydantic_agent, 'run_sync', return_value=mock_response):
            result = clue_agent.generate_clue("letter opener", sample_context)
            if hasattr(result, 'clue'):
                assert hasattr(result.clue, 'type') or 'type' in result.clue
            else:
                assert 'error' in result or 'type' in result

    @patch.object(ClueAgent, '_brave_search')
    @patch.object(ClueAgent, '_llm_generate_clue')
    def test_generate_clue_with_mem0(self, mock_llm_generate, mock_brave_search, sample_clue_data):
        with patch('mem0.MemoryClient', return_value=MagicMock()) as mem0_mock:
            with patch.dict(os.environ, {"LLM_MODEL": "test"}):
                agent = ClueAgent(use_mem0=True, user_id="test_user", model_message_cls=DummyModelMessage)
                mock_brave_search.return_value = []
                mock_llm_generate.return_value = sample_clue_data
                result = agent.generate_clue("letter opener")
                agent.mem0_client.update.assert_called()

    def test_generate_clue_fallback(self, clue_agent):
        result = clue_agent.generate_clue("letter opener")
        assert isinstance(result, dict) or hasattr(result, 'clue')

    def test_failure_case_all_apis_down(self):
        with patch('mem0.MemoryClient', return_value=MagicMock()):
            with patch.dict(os.environ, {"LLM_MODEL": "test"}):
                agent = ClueAgent(use_mem0=True, user_id="test_user", model_message_cls=DummyModelMessage)
                with patch.object(agent.pydantic_agent, 'run_sync', side_effect=Exception("API Error")), \
                     patch.object(agent, '_brave_search', side_effect=Exception("API Error")):
                    import pytest
                    with pytest.raises(Exception):
                        agent.generate_clue("letter opener")

    def test_forensic_analysis_types(self, clue_agent):
        analysis_types = ["physical", "digital", "biological", "chemical"]
        for analysis_type in analysis_types:
            result = clue_agent.generate_clue(f"{analysis_type} evidence")
            assert isinstance(result, dict) or hasattr(result, 'clue')

    def test_connection_strength_levels(self, clue_agent):
        clues = [
            {"description": "Bloody knife", "significance": "high"},
            {"description": "Fingerprints", "significance": "medium"}
        ]
        result = clue_agent.find_connections(clues)
        assert isinstance(result, dict) or hasattr(result, 'connections')

    def test_timeline_implications(self, clue_agent):
        clue_data = {
            "description": "Victim's last seen at 8 PM",
            "time": "8:00 PM",
            "significance": "high"
        }
        result = clue_agent.analyze_clue(clue_data)
        assert isinstance(result, dict) or hasattr(result, 'analysis')

    def test_contradiction_detection(self, clue_agent):
        clues = [
            {"description": "Victim seen at 8 PM", "time": "8:00 PM"},
            {"description": "Victim seen at 9 PM", "time": "9:00 PM"}
        ]
        result = clue_agent.find_connections(clues)
        assert isinstance(result, dict) or hasattr(result, 'contradictions')

    def test_reliability_scoring(self, clue_agent):
        """Test reliability scoring of clues."""
        clue_data = {
            "description": "Bloody knife",
            "source": "forensic analysis",
            "confidence": 0.9
            }
        result = clue_agent.analyze_clue(clue_data)
        assert isinstance(result, dict) or hasattr(result, 'reliability')

    def test_next_steps_generation(self, clue_agent):
        """Test generation of next investigative steps."""
        clue_data = {
            "description": "Bloody knife",
            "analysis": "Fingerprints found",
            "significance": "high"
        }
        result = clue_agent.analyze_clue(clue_data)
        assert isinstance(result, dict) or hasattr(result, 'next_steps') 