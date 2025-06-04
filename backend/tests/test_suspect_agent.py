"""
Unit tests for SuspectAgent class.
Tests suspect profile generation, dialogue generation, and behavioral analysis.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import json
from backend.agents.suspect_agent import (
    SuspectAgent,
    SuspectProfile,
    SuspectState,
    SuspectProfileInput,
    SuspectProfileOutput,
    SuspectDialogueInput,
    SuspectDialogueOutput
)


class TestSuspectAgent:
    """Test suite for SuspectAgent class."""

    @pytest.fixture
    def sample_suspect_profile(self):
        """Sample suspect profile for testing."""
        return SuspectProfile(
            name="John Doe",
            background="Former accountant with gambling debts",
            occupation="Accountant",
            motive="Financial desperation",
            alibi="Claims to be at the casino",
            personality_traits=["nervous", "evasive", "intelligent"],
            relationship_to_victim="Business partner",
            suspicious_behaviors=["avoiding eye contact", "sweating"],
            secrets=["Hidden gambling addiction", "Embezzled funds"]
        )

    @pytest.fixture
    def sample_suspect_state(self):
        """Sample suspect state for testing."""
        return SuspectState(
            name="John Doe",
            interviewed=True,
            suspicious_level=7,
            known_information=["Has gambling debts", "Was at victim's office"],
            contradictions=["Time of alibi doesn't match", "Nervous behavior"],
            emotional_state="anxious"
        )

    @pytest.fixture
    def suspect_agent(self):
        """Create SuspectAgent instance for testing."""
        with patch('backend.agents.suspect_agent.mem0'), \
             patch('backend.agents.suspect_agent.ModelRouter'), \
             patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
            return SuspectAgent(use_mem0=False)

    @patch('backend.agents.suspect_agent.requests.get')
    def test_brave_search_success(self, mock_get, suspect_agent):
        """Test successful Brave search API call."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "web": {
                "results": [
                    {
                        "title": "Criminal Psychology Guide",
                        "url": "https://example.com/psychology",
                        "description": "Understanding criminal behavior patterns."
                    }
                ]
            }
        }
        mock_get.return_value = mock_response

        with patch.dict(os.environ, {"BRAVE_API_KEY": "test_brave_key"}):
            result = suspect_agent._brave_search("criminal psychology")

        assert len(result) == 1
        assert result[0]["title"] == "Criminal Psychology Guide"

    @patch('backend.agents.suspect_agent.requests.get')
    def test_brave_search_no_api_key(self, mock_get, suspect_agent):
        """Test Brave search without API key."""
        with patch.dict(os.environ, {}, clear=True):
            result = suspect_agent._brave_search("suspect profile")

        assert result == []
        mock_get.assert_not_called()

    @patch('backend.agents.suspect_agent.requests.get')
    def test_brave_search_api_error(self, mock_get, suspect_agent):
        """Test Brave search with API error."""
        mock_get.side_effect = Exception("API Error")

        with patch.dict(os.environ, {"BRAVE_API_KEY": "test_brave_key"}):
            result = suspect_agent._brave_search("suspect behavior")

        assert result == []

    def test_llm_generate_suspect_success(self, suspect_agent, sample_suspect_profile):
        """Test successful LLM suspect profile generation."""
        mock_response = {
            "name": "John Doe",
            "background": "Former accountant with gambling debts",
            "occupation": "Accountant",
            "motive": "Financial desperation",
            "alibi": "Claims to be at the casino",
            "personality_traits": ["nervous", "evasive", "intelligent"],
            "relationship_to_victim": "Business partner",
            "suspicious_behaviors": ["avoiding eye contact", "sweating"],
            "secrets": ["Hidden gambling addiction", "Embezzled funds"]
        }

        with patch.object(suspect_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = Mock()
            mock_llm.chat.completions.create.return_value.choices[0].message.content = json.dumps(mock_response)
            mock_get_model.return_value = mock_llm

            result = suspect_agent._llm_generate_suspect(
                "Create a suspect profile for an accountant",
                {"setting": "corporate office"},
                [{"title": "Guide", "description": "Psychology guide"}]
            )

            assert isinstance(result, SuspectProfile)
            assert result.name == "John Doe"
            assert result.occupation == "Accountant"
            assert result.motive == "Financial desperation"
            assert "nervous" in result.personality_traits

    def test_llm_generate_suspect_error(self, suspect_agent):
        """Test LLM suspect generation with error."""
        with patch.object(suspect_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = Mock()
            mock_llm.chat.completions.create.side_effect = Exception("LLM Error")
            mock_get_model.return_value = mock_llm

            result = suspect_agent._llm_generate_suspect("Create suspect", {}, [])

            # Should return a basic SuspectProfile with error indication
            assert isinstance(result, SuspectProfile)
            assert "Error generating" in result.background or result.name == "Unknown"

    def test_llm_generate_suspect_invalid_json(self, suspect_agent):
        """Test LLM suspect generation with invalid JSON response."""
        with patch.object(suspect_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = Mock()
            mock_llm.chat.completions.create.return_value.choices[0].message.content = "Invalid JSON"
            mock_get_model.return_value = mock_llm

            result = suspect_agent._llm_generate_suspect("Create suspect", {}, [])

            assert isinstance(result, SuspectProfile)
            # Should handle gracefully with fallback values

    def test_llm_generate_dialogue_success(self, suspect_agent, sample_suspect_state):
        """Test successful dialogue generation."""
        mock_response = {
            "dialogue": "I-I was at the casino all night, you can check with the dealers!",
            "updated_state": {
                "name": "John Doe",
                "interviewed": True,
                "suspicious_level": 8,
                "known_information": ["Has gambling debts", "Was at victim's office", "Defensive about alibi"],
                "contradictions": ["Time of alibi doesn't match", "Nervous behavior", "Story changed"],
                "emotional_state": "defensive"
            }
        }

        with patch.object(suspect_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = Mock()
            mock_llm.chat.completions.create.return_value.choices[0].message.content = json.dumps(mock_response)
            mock_get_model.return_value = mock_llm

            result = suspect_agent._llm_generate_dialogue(
                "Where were you last night?",
                sample_suspect_state,
                {"interrogation_style": "aggressive"}
            )

            assert isinstance(result, SuspectDialogueOutput)
            assert "casino" in result.dialogue.lower()
            assert result.updated_state.suspicious_level == 8
            assert result.updated_state.emotional_state == "defensive"

    def test_llm_generate_dialogue_error(self, suspect_agent, sample_suspect_state):
        """Test dialogue generation with error."""
        with patch.object(suspect_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = Mock()
            mock_llm.chat.completions.create.side_effect = Exception("LLM Error")
            mock_get_model.return_value = mock_llm

            result = suspect_agent._llm_generate_dialogue("Question?", sample_suspect_state, {})

            assert isinstance(result, SuspectDialogueOutput)
            assert "Error generating dialogue" in result.dialogue

    @patch.object(SuspectAgent, '_brave_search')
    @patch.object(SuspectAgent, '_llm_generate_suspect')
    def test_generate_suspect_success(self, mock_llm_generate, mock_brave_search, suspect_agent, sample_suspect_profile):
        """Test successful suspect generation."""
        mock_brave_search.return_value = [{"title": "Psychology Guide", "description": "Criminal psychology"}]
        mock_llm_generate.return_value = sample_suspect_profile

        result = suspect_agent.generate_suspect("Create an accountant suspect", {"setting": "office"})

        assert isinstance(result, SuspectProfileOutput)
        assert result.profile.name == "John Doe"
        assert result.profile.occupation == "Accountant"
        assert len(result.sources) >= 0
        mock_brave_search.assert_called_once()
        mock_llm_generate.assert_called_once()

    @patch.object(SuspectAgent, '_brave_search')
    @patch.object(SuspectAgent, '_llm_generate_suspect')
    def test_generate_suspect_with_mem0(self, mock_llm_generate, mock_brave_search, suspect_agent, sample_suspect_profile):
        """Test suspect generation with Mem0 integration."""
        suspect_agent.use_mem0 = True
        suspect_agent.search_memories = Mock(return_value=[{"memory": "Previous suspect patterns"}])
        suspect_agent.update_memory = Mock()

        mock_brave_search.return_value = []
        mock_llm_generate.return_value = sample_suspect_profile

        result = suspect_agent.generate_suspect("Create suspect with memory context")

        assert isinstance(result, SuspectProfileOutput)
        suspect_agent.search_memories.assert_called_once()
        suspect_agent.update_memory.assert_called()

    @patch.object(SuspectAgent, '_llm_generate_dialogue')
    def test_generate_dialogue_success(self, mock_llm_generate, suspect_agent, sample_suspect_state):
        """Test successful dialogue generation."""
        mock_dialogue_output = SuspectDialogueOutput(
            dialogue="I don't know anything about that!",
            updated_state=sample_suspect_state
        )
        mock_llm_generate.return_value = mock_dialogue_output

        result = suspect_agent.generate_dialogue(
            "What do you know about the murder?",
            sample_suspect_state,
            {"tone": "aggressive"}
        )

        assert isinstance(result, SuspectDialogueOutput)
        assert result.dialogue == "I don't know anything about that!"
        mock_llm_generate.assert_called_once()

    @patch.object(SuspectAgent, '_llm_generate_dialogue')
    def test_generate_dialogue_with_mem0(self, mock_llm_generate, suspect_agent, sample_suspect_state):
        """Test dialogue generation with memory context."""
        suspect_agent.use_mem0 = True
        suspect_agent.search_memories = Mock(return_value=[{"memory": "Previous dialogue patterns"}])
        suspect_agent.update_memory = Mock()

        mock_dialogue_output = SuspectDialogueOutput(
            dialogue="Response with memory context",
            updated_state=sample_suspect_state
        )
        mock_llm_generate.return_value = mock_dialogue_output

        result = suspect_agent.generate_dialogue("Question?", sample_suspect_state)

        assert result.dialogue == "Response with memory context"
        suspect_agent.search_memories.assert_called_once()
        suspect_agent.update_memory.assert_called()

    def test_suspect_profile_validation(self, sample_suspect_profile):
        """Test that suspect profile model validation works."""
        # Test valid profile
        assert sample_suspect_profile.name == "John Doe"
        assert sample_suspect_profile.occupation == "Accountant"
        assert len(sample_suspect_profile.personality_traits) == 3
        assert len(sample_suspect_profile.secrets) == 2

        # Test profile with minimal required fields
        minimal_profile = SuspectProfile(
            name="Jane Smith",
            background="Unknown background"
        )
        assert minimal_profile.name == "Jane Smith"
        assert minimal_profile.occupation is None
        assert minimal_profile.personality_traits == []

    def test_suspect_state_validation(self, sample_suspect_state):
        """Test that suspect state model validation works."""
        assert sample_suspect_state.name == "John Doe"
        assert sample_suspect_state.interviewed is True
        assert sample_suspect_state.suspicious_level == 7
        assert len(sample_suspect_state.known_information) == 2
        assert sample_suspect_state.emotional_state == "anxious"

        # Test state with minimal fields
        minimal_state = SuspectState(name="Test Suspect")
        assert minimal_state.name == "Test Suspect"
        assert minimal_state.interviewed is False
        assert minimal_state.suspicious_level == 0
        assert minimal_state.known_information == []

    def test_suspicious_level_boundaries(self):
        """Test suspicious level handling with boundary values."""
        # Test normal range
        state = SuspectState(name="Test", suspicious_level=5)
        assert state.suspicious_level == 5

        # Test boundary values
        low_state = SuspectState(name="Test", suspicious_level=0)
        assert low_state.suspicious_level == 0

        high_state = SuspectState(name="Test", suspicious_level=10)
        assert high_state.suspicious_level == 10

    def test_personality_traits_handling(self, sample_suspect_profile):
        """Test personality traits list handling."""
        assert "nervous" in sample_suspect_profile.personality_traits
        assert "evasive" in sample_suspect_profile.personality_traits
        assert len(sample_suspect_profile.personality_traits) == 3

        # Test empty traits
        profile_no_traits = SuspectProfile(
            name="Test",
            background="Background",
            personality_traits=[]
        )
        assert profile_no_traits.personality_traits == []

    def test_edge_case_empty_prompt(self, suspect_agent):
        """Test suspect generation with empty prompt."""
        with patch.object(suspect_agent, '_brave_search', return_value=[]):
            with patch.object(suspect_agent, '_llm_generate_suspect') as mock_generate:
                mock_generate.return_value = SuspectProfile(name="Default", background="Default")
                
                result = suspect_agent.generate_suspect("", {})

        assert isinstance(result, SuspectProfileOutput)

    def test_edge_case_none_context(self, suspect_agent):
        """Test suspect generation with None context."""
        with patch.object(suspect_agent, '_brave_search', return_value=[]):
            with patch.object(suspect_agent, '_llm_generate_suspect') as mock_generate:
                mock_generate.return_value = SuspectProfile(name="Test", background="Test")
                
                result = suspect_agent.generate_suspect("Create suspect", None)

        assert isinstance(result, SuspectProfileOutput)

    def test_failure_case_all_apis_down(self, suspect_agent):
        """Test behavior when all external APIs are down."""
        with patch.object(suspect_agent, '_brave_search', side_effect=Exception("Brave API down")):
            with patch.object(suspect_agent, '_llm_generate_suspect', side_effect=Exception("LLM API down")):
                result = suspect_agent.generate_suspect("Create suspect", {})

        # Should handle gracefully and return some result
        assert isinstance(result, SuspectProfileOutput)

    def test_dialogue_emotional_state_progression(self, sample_suspect_state):
        """Test that emotional state can change during dialogue."""
        initial_state = "anxious"
        assert sample_suspect_state.emotional_state == initial_state

        # Test state update
        updated_state = sample_suspect_state.model_copy(update={"emotional_state": "angry"})
        assert updated_state.emotional_state == "angry"
        assert updated_state.name == sample_suspect_state.name  # Other fields preserved

    def test_contradictions_tracking(self, sample_suspect_state):
        """Test that contradictions are properly tracked."""
        assert len(sample_suspect_state.contradictions) == 2
        assert "Time of alibi doesn't match" in sample_suspect_state.contradictions

        # Test adding new contradiction
        new_contradictions = sample_suspect_state.contradictions + ["New contradiction"]
        updated_state = sample_suspect_state.model_copy(update={"contradictions": new_contradictions})
        assert len(updated_state.contradictions) == 3

    def test_known_information_accumulation(self, sample_suspect_state):
        """Test that known information accumulates properly."""
        assert len(sample_suspect_state.known_information) == 2
        
        # Test adding new information
        new_info = sample_suspect_state.known_information + ["New information discovered"]
        updated_state = sample_suspect_state.model_copy(update={"known_information": new_info})
        assert len(updated_state.known_information) == 3

    @patch.dict(os.environ, {"LLM_MODEL": "test-model"})
    def test_model_configuration(self):
        """Test that agent uses configured model."""
        with patch('backend.agents.suspect_agent.mem0'), \
             patch('backend.agents.suspect_agent.ModelRouter'), \
             patch('backend.agents.suspect_agent.PydanticAgent') as mock_agent:
            
            SuspectAgent(use_mem0=False)
            
            # Verify PydanticAgent was called with the correct model
            mock_agent.assert_called_once()
            args, kwargs = mock_agent.call_args
            assert args[0] == "test-model"

    def test_suspect_relationship_types(self):
        """Test different types of relationships to victim."""
        relationships = [
            "Business partner",
            "Family member",
            "Friend",
            "Romantic partner",
            "Employee",
            "Stranger"
        ]
        
        for relationship in relationships:
            profile = SuspectProfile(
                name="Test Suspect",
                background="Test background",
                relationship_to_victim=relationship
            )
            assert profile.relationship_to_victim == relationship

    def test_suspicious_behaviors_variety(self):
        """Test variety of suspicious behaviors."""
        behaviors = [
            "avoiding eye contact",
            "sweating profusely",
            "fidgeting",
            "changing story",
            "defensive responses",
            "nervous laughter"
        ]
        
        profile = SuspectProfile(
            name="Test Suspect",
            background="Test background",
            suspicious_behaviors=behaviors
        )
        assert len(profile.suspicious_behaviors) == len(behaviors)
        assert "avoiding eye contact" in profile.suspicious_behaviors

    def test_motive_categories(self):
        """Test different motive categories."""
        motives = [
            "Financial gain",
            "Revenge",
            "Jealousy",
            "Self-defense",
            "Covering up crime",
            "Mental illness"
        ]
        
        for motive in motives:
            profile = SuspectProfile(
                name="Test Suspect",
                background="Test background",
                motive=motive
            )
            assert profile.motive == motive 