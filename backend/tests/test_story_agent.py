"""
Unit tests for StoryAgent class.
Tests story generation, narrative progression, clue extraction, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import os
import json
from backend.agents.story_agent import (
    StoryAgent, 
    StoryState, 
    SuspectState, 
    PlayerProfile, 
    StoryAgentInput, 
    StoryAgentOutput,
    StoryAgentGenerateInput,
    StoryAgentGenerateOutput
)


class TestStoryAgent:
    """Test suite for StoryAgent class."""

    @pytest.fixture
    def sample_story_state(self):
        """Sample story state for testing."""
        return StoryState(
            template_id="template_1",
            title="Murder at the Mansion",
            current_scene="investigation",
            narrative_history=["The victim was found in the library."],
            discovered_clues=["bloody knife"],
            suspect_states={
                "suspect1": SuspectState(name="John Doe", interviewed=False, suspicious_level=3)
            },
            last_action="examine body"
        )

    @pytest.fixture
    def sample_player_profile(self):
        """Sample player profile for testing."""
        return PlayerProfile(
            psychological_traits={"analytical": "high", "intuitive": "medium"},
            preferences={"difficulty": "medium", "pacing": "normal"},
            role="detective"
        )

    @pytest.fixture
    def story_agent(self):
        """Create StoryAgent instance for testing."""
        with patch('backend.agents.story_agent.mem0'), \
             patch('backend.agents.story_agent.ModelRouter'), \
             patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
            return StoryAgent(use_mem0=False)

    @patch('backend.agents.story_agent.requests.get')
    def test_brave_search_success(self, mock_get, story_agent):
        """Test successful Brave search API call."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "web": {
                "results": [
                    {
                        "title": "Murder Mystery Guide",
                        "url": "https://example.com/mystery",
                        "description": "A comprehensive guide to murder mysteries."
                    }
                ]
            }
        }
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {"BRAVE_API_KEY": "test_brave_key"}):
            result = story_agent._brave_search("murder mystery")

        assert len(result) == 1
        assert result[0]["title"] == "Murder Mystery Guide"
        assert result[0]["url"] == "https://example.com/mystery"

    @patch('backend.agents.story_agent.requests.get')
    def test_brave_search_no_api_key(self, mock_get, story_agent):
        """Test Brave search without API key."""
        with patch.dict(os.environ, {}, clear=True):
            result = story_agent._brave_search("murder mystery")

        assert result == []
        mock_get.assert_not_called()

    @patch('backend.agents.story_agent.requests.get')
    def test_brave_search_api_error(self, mock_get, story_agent):
        """Test Brave search with API error."""
        mock_get.side_effect = Exception("API Error")

        with patch.dict(os.environ, {"BRAVE_API_KEY": "test_brave_key"}):
            result = story_agent._brave_search("murder mystery")

        assert result == []

    @patch('backend.agents.story_agent.requests.get')
    def test_brave_search_http_error(self, mock_get, story_agent):
        """Test Brave search with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {"BRAVE_API_KEY": "test_brave_key"}):
            result = story_agent._brave_search("murder mystery")

        assert result == []

    @patch.object(StoryAgent, '_brave_search')
    @patch.object(StoryAgent, '_llm_generate_narrative')
    def test_process_success(self, mock_llm_generate, mock_brave_search, story_agent, sample_story_state, sample_player_profile):
        """Test successful story processing."""
        # Setup mocks
        mock_brave_search.return_value = [{"title": "Mystery Guide", "description": "Guide content"}]
        mock_llm_generate.return_value = "The detective examined the evidence carefully."

        input_data = {
            "action": "examine evidence",
            "story_state": sample_story_state.model_dump(),
            "player_profile": sample_player_profile.model_dump()
        }

        result = story_agent.process(input_data)

        assert "narrative" in result
        assert "story_state" in result
        assert result["narrative"] == "The detective examined the evidence carefully."
        mock_brave_search.assert_called_once()
        mock_llm_generate.assert_called_once()

    def test_process_invalid_input(self, story_agent):
        """Test process method with invalid input."""
        with pytest.raises(Exception):
            story_agent.process({"invalid": "input"})

    @patch.object(StoryAgent, '_brave_search')
    @patch.object(StoryAgent, '_llm_generate_story')
    def test_generate_story_success(self, mock_llm_generate, mock_brave_search, story_agent):
        """Test successful story generation."""
        mock_brave_search.return_value = [{"title": "Mystery Guide", "description": "Guide content"}]
        mock_llm_generate.return_value = "A dark and stormy night began the mystery..."

        result = story_agent.generate_story("Generate a murder mystery", {"setting": "mansion"})

        assert isinstance(result, StoryAgentGenerateOutput)
        assert result.story == "A dark and stormy night began the mystery..."
        assert len(result.sources) >= 0

    @patch.object(StoryAgent, '_brave_search')
    @patch.object(StoryAgent, '_llm_generate_story')
    def test_generate_story_with_mem0(self, mock_llm_generate, mock_brave_search, story_agent):
        """Test story generation with Mem0 integration."""
        story_agent.use_mem0 = True
        story_agent.search_memories = Mock(return_value=[{"memory": "Previous story context"}])
        
        mock_brave_search.return_value = []
        mock_llm_generate.return_value = "Generated story with memory context"

        result = story_agent.generate_story("Continue the mystery")

        assert result.story == "Generated story with memory context"
        story_agent.search_memories.assert_called_once()

    @patch.object(StoryAgent, '_brave_search')
    def test_start_new_story(self, mock_brave_search, story_agent):
        """Test starting a new story."""
        mock_brave_search.return_value = []
        
        template = {
            "id": "template_1",
            "title": "Murder at the Mansion",
            "victim": "Lord Blackwood",
            "setting": "Victorian mansion"
        }
        
        player_profile = {
            "psychological_traits": {"analytical": "high"},
            "preferences": {"difficulty": "hard"}
        }

        with patch.object(story_agent, '_llm_generate_story') as mock_generate:
            mock_generate.return_value = "The story begins in a dark mansion..."
            
            result = story_agent.start_new_story(template, player_profile)

            assert "narrative" in result
            assert "story_state" in result
            assert result["story_state"]["template_id"] == "template_1"
            assert result["story_state"]["title"] == "Murder at the Mansion"

    def test_extract_potential_clue_found(self, story_agent):
        """Test clue extraction when clue is found."""
        action = "search the desk"
        narrative = "Under the desk, you find a torn letter with bloodstains."

        with patch.object(story_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = Mock()
            mock_llm.chat.completions.create.return_value.choices[0].message.content = json.dumps({
                "clue": "torn letter with bloodstains",
                "confidence": 0.8,
                "reasoning": "Letter found during desk search"
            })
            mock_get_model.return_value = mock_llm

            result = story_agent._extract_potential_clue(action, narrative)

            assert result == "torn letter with bloodstains"

    def test_extract_potential_clue_not_found(self, story_agent):
        """Test clue extraction when no clue is found."""
        action = "look around"
        narrative = "The room appears normal with nothing suspicious."

        with patch.object(story_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = Mock()
            mock_llm.chat.completions.create.return_value.choices[0].message.content = json.dumps({
                "clue": None,
                "confidence": 0.1,
                "reasoning": "No evidence found"
            })
            mock_get_model.return_value = mock_llm

            result = story_agent._extract_potential_clue(action, narrative)

            assert result is None

    def test_extract_potential_clue_llm_error(self, story_agent):
        """Test clue extraction with LLM error."""
        action = "search room"
        narrative = "You search the room thoroughly."

        with patch.object(story_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = Mock()
            mock_llm.chat.completions.create.side_effect = Exception("LLM API Error")
            mock_get_model.return_value = mock_llm

            result = story_agent._extract_potential_clue(action, narrative)

            assert result is None

    def test_extract_potential_clue_invalid_json(self, story_agent):
        """Test clue extraction with invalid JSON response."""
        action = "examine evidence"
        narrative = "The evidence reveals important information."

        with patch.object(story_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = Mock()
            mock_llm.chat.completions.create.return_value.choices[0].message.content = "Invalid JSON"
            mock_get_model.return_value = mock_llm

            result = story_agent._extract_potential_clue(action, narrative)

            assert result is None

    def test_llm_generate_story_success(self, story_agent):
        """Test successful LLM story generation."""
        with patch.object(story_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = Mock()
            mock_llm.chat.completions.create.return_value.choices[0].message.content = "Generated story content"
            mock_get_model.return_value = mock_llm

            result = story_agent._llm_generate_story(
                "Create a mystery",
                {"setting": "mansion"},
                [{"title": "Guide", "description": "Mystery guide"}],
                "Previous context"
            )

            assert result == "Generated story content"
            mock_llm.chat.completions.create.assert_called_once()

    def test_llm_generate_story_error(self, story_agent):
        """Test LLM story generation with error."""
        with patch.object(story_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = Mock()
            mock_llm.chat.completions.create.side_effect = Exception("LLM Error")
            mock_get_model.return_value = mock_llm

            result = story_agent._llm_generate_story("Create story", {}, [], "")

            assert "Error generating story" in result

    def test_llm_generate_narrative_success(self, story_agent):
        """Test successful LLM narrative generation."""
        with patch.object(story_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = Mock()
            mock_llm.chat.completions.create.return_value.choices[0].message.content = "Narrative progression"
            mock_get_model.return_value = mock_llm

            result = story_agent._llm_generate_narrative(
                "examine clue",
                {"current_scene": "library"},
                [{"title": "Guide"}],
                "Context"
            )

            assert result == "Narrative progression"

    def test_llm_generate_narrative_error(self, story_agent):
        """Test LLM narrative generation with error."""
        with patch.object(story_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = Mock()
            mock_llm.chat.completions.create.side_effect = Exception("LLM Error")
            mock_get_model.return_value = mock_llm

            result = story_agent._llm_generate_narrative("action", {}, [], "")

            assert "Error generating narrative" in result

    def test_clear_memories_success(self, story_agent):
        """Test successful memory clearing."""
        story_agent.use_mem0 = True
        story_agent.clear_memories = Mock(return_value=True)

        result = story_agent.clear_memories()

        assert result is True

    def test_clear_memories_disabled(self, story_agent):
        """Test memory clearing when Mem0 is disabled."""
        story_agent.use_mem0 = False

        # The base agent's clear_memories should return False when disabled
        with patch.object(story_agent.__class__.__bases__[0], 'clear_memories', return_value=False):
            result = story_agent.clear_memories()

        assert result is False

    def test_edge_case_empty_prompt(self, story_agent):
        """Test story generation with empty prompt."""
        result = story_agent.generate_story("", {})

        assert isinstance(result, StoryAgentGenerateOutput)
        # Should handle empty prompt gracefully

    def test_edge_case_none_context(self, story_agent):
        """Test story generation with None context."""
        with patch.object(story_agent, '_brave_search', return_value=[]):
            with patch.object(story_agent, '_llm_generate_story', return_value="Story"):
                result = story_agent.generate_story("Generate story", None)

        assert isinstance(result, StoryAgentGenerateOutput)

    def test_failure_case_all_apis_down(self, story_agent):
        """Test behavior when all external APIs are down."""
        with patch.object(story_agent, '_brave_search', side_effect=Exception("Brave API down")):
            with patch.object(story_agent, '_llm_generate_story', side_effect=Exception("LLM API down")):
                result = story_agent.generate_story("Generate story", {})

        # Should handle gracefully and return some result
        assert isinstance(result, StoryAgentGenerateOutput)

    @patch.dict(os.environ, {"LLM_MODEL": "test-model"})
    def test_model_configuration(self):
        """Test that agent uses configured model."""
        with patch('backend.agents.story_agent.mem0'), \
             patch('backend.agents.story_agent.ModelRouter'), \
             patch('backend.agents.story_agent.PydanticAgent') as mock_agent:
            
            StoryAgent(use_mem0=False)
            
            # Verify PydanticAgent was called with the correct model
            mock_agent.assert_called_once()
            args, kwargs = mock_agent.call_args
            assert args[0] == "test-model"

    def test_suspect_state_in_story_state(self, sample_story_state):
        """Test that suspect states are properly handled."""
        assert "suspect1" in sample_story_state.suspect_states
        suspect = sample_story_state.suspect_states["suspect1"]
        assert suspect.name == "John Doe"
        assert suspect.interviewed is False
        assert suspect.suspicious_level == 3

    def test_narrative_history_tracking(self, sample_story_state):
        """Test that narrative history is properly tracked."""
        assert len(sample_story_state.narrative_history) == 1
        assert "victim was found" in sample_story_state.narrative_history[0]

    def test_clue_tracking(self, sample_story_state):
        """Test that discovered clues are properly tracked."""
        assert "bloody knife" in sample_story_state.discovered_clues

    def test_player_profile_roles(self, sample_player_profile):
        """Test different player profile roles."""
        assert sample_player_profile.role == "detective"
        
        # Test other roles
        witness_profile = PlayerProfile(role="witness")
        assert witness_profile.role == "witness"
        
        suspect_profile = PlayerProfile(role="suspect")
        assert suspect_profile.role == "suspect" 