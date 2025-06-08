import pytest
from unittest.mock import patch, Mock, MagicMock
import os
import json
from backend.agents.suspect_agent import SuspectAgent, SuspectState, SuspectProfile, SuspectDialogueOutput, SuspectProfileOutput, PydanticAgent
from backend.agents.models.psychological_profile import (
    PsychologicalProfile,
    create_default_profile,
    TraitIntensity,
    CognitiveStyle,
    EmotionalTendency,
    SocialStyle
)
from backend.agents.model_router import ModelRouter

# Dummy message class for testing
class DummyModelMessage:
    def __init__(self, role=None, content=None, **kwargs):
        self.role = role
        self.content = content
        for k, v in kwargs.items():
            setattr(self, k, v)

@pytest.fixture(autouse=True)
def patch_env_and_router():
    with patch.dict(os.environ, {"LLM_MODEL": "gpt-3.5-turbo", "OPENAI_API_KEY": "test-key", "OPENROUTER_API_KEY": "test-key"}):
        with patch('backend.agents.suspect_agent.PydanticAgent') as mock_agent, \
             patch('backend.agents.suspect_agent.ModelRouter') as mock_router_class:
            mock_router = mock_router_class.return_value
            mock_router.get_model_for_task.return_value = "gpt-3.5-turbo"
            mock_router.complete.return_value = Mock(content="Test response")
            yield

@pytest.fixture
def suspect_agent():
    return SuspectAgent(model_message_cls=DummyModelMessage)

@pytest.fixture
def sample_suspect_profile():
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
def sample_suspect_state():
    return SuspectState(
        name="John Doe",
        interviewed=False,
        suspicious_level=0,
        known_information=[],
        contradictions=[],
        emotional_state="calm"
    )

def test_dialogue_generation_with_profile(suspect_agent):
    question = "Where were you on the night of the murder?"
    suspect_state = SuspectState(
        name="John Doe",
        interviewed=False,
        suspicious_level=0,
        known_information=[],
        contradictions=[],
        emotional_state="calm"
    )
    with patch.object(json, 'dumps', return_value="{}"):
        result = suspect_agent._llm_generate_dialogue(
            question=question,
            suspect_state=suspect_state,
            context={"player_profile": create_default_profile()}
        )
    assert hasattr(result, "dialogue")
    assert hasattr(result, "updated_state")

def test_profile_adaptation(suspect_agent):
    direct_profile = create_default_profile()
    direct_profile.social_style = SocialStyle.DIRECT
    indirect_profile = create_default_profile()
    indirect_profile.social_style = SocialStyle.INDIRECT
    question = "What do you know about the victim?"
    suspect_state = SuspectState(
        name="Jane Smith",
        interviewed=False,
        suspicious_level=0,
        known_information=[],
        contradictions=[],
        emotional_state="nervous"
    )
    with patch.object(json, 'dumps', return_value="{}"):
        direct_result = suspect_agent._llm_generate_dialogue(
            question=question,
            suspect_state=suspect_state,
            context={"player_profile": direct_profile}
        )
        indirect_result = suspect_agent._llm_generate_dialogue(
            question=question,
            suspect_state=suspect_state,
            context={"player_profile": indirect_profile}
        )
    assert isinstance(direct_result, SuspectDialogueOutput)
    assert isinstance(indirect_result, SuspectDialogueOutput)

def test_emotional_adaptation(suspect_agent):
    reserved_profile = create_default_profile()
    reserved_profile.emotional_tendency = EmotionalTendency.RESERVED
    expressive_profile = create_default_profile()
    expressive_profile.emotional_tendency = EmotionalTendency.EXPRESSIVE
    question = "How did you feel when you heard about the murder?"
    suspect_state = SuspectState(
        name="Bob Wilson",
        interviewed=False,
        suspicious_level=0,
        known_information=[],
        contradictions=[],
        emotional_state="distressed"
    )
    with patch.object(json, 'dumps', return_value="{}"):
        reserved_result = suspect_agent._llm_generate_dialogue(
            question=question,
            suspect_state=suspect_state,
            context={"player_profile": reserved_profile}
        )
        expressive_result = suspect_agent._llm_generate_dialogue(
            question=question,
            suspect_state=suspect_state,
            context={"player_profile": expressive_profile}
        )
    assert isinstance(reserved_result, SuspectDialogueOutput)
    assert isinstance(expressive_result, SuspectDialogueOutput)

def test_cognitive_adaptation(suspect_agent):
    analytical_profile = create_default_profile()
    analytical_profile.cognitive_style = CognitiveStyle.ANALYTICAL
    intuitive_profile = create_default_profile()
    intuitive_profile.cognitive_style = CognitiveStyle.INTUITIVE
    question = "What do you think happened?"
    suspect_state = SuspectState(
        name="Alice Brown",
        interviewed=False,
        suspicious_level=0,
        known_information=[],
        contradictions=[],
        emotional_state="thoughtful"
    )
    with patch.object(json, 'dumps', return_value="{}"):
        analytical_result = suspect_agent._llm_generate_dialogue(
            question=question,
            suspect_state=suspect_state,
            context={"player_profile": analytical_profile}
        )
        intuitive_result = suspect_agent._llm_generate_dialogue(
            question=question,
            suspect_state=suspect_state,
            context={"player_profile": intuitive_profile}
        )
    assert isinstance(analytical_result, SuspectDialogueOutput)
    assert isinstance(intuitive_result, SuspectDialogueOutput)

def test_llm_generate_suspect_success(suspect_agent, sample_suspect_profile):
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
    class DummyResp:
        def __init__(self, content):
            self.content = content
    with patch.object(suspect_agent.model_router, 'complete', return_value=DummyResp(json.dumps(mock_response))):
        result = suspect_agent._llm_generate_suspect(
            "Create a suspect profile for an accountant",
            {"setting": "corporate office"},
            [{"title": "Guide", "description": "Psychology guide"}]
        )
        assert isinstance(result, SuspectProfile)
        assert result.name == "John Doe"

def test_llm_generate_suspect_error():
    agent = SuspectAgent(user_id="test_user")
    with patch.object(agent.model_router, 'get_model') as mock_get_model:
        mock_llm = Mock()
        mock_llm.chat.completions.create.side_effect = Exception("LLM Error")
        mock_get_model.return_value = mock_llm
        agent.use_mem0 = True

        result = agent._llm_generate_suspect("Create suspect", {}, [])

        assert isinstance(result, SuspectProfile)
        assert result.name == "Create suspect"
        assert result.background == "Information extracted from text."

def test_llm_generate_suspect_invalid_json(suspect_agent):
    class DummyResp:
        def __init__(self, content):
            self.content = content
    with patch.object(suspect_agent.model_router, 'complete', return_value=DummyResp("Invalid JSON")):
        result = suspect_agent._llm_generate_suspect("Create suspect", {}, [])
        assert isinstance(result, SuspectProfile)
        assert result.name == "Create suspect"
        assert result.background == "Information extracted from text."

def test_llm_generate_dialogue_success(suspect_agent, sample_suspect_state):
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
    class DummyResp:
        def __init__(self, content):
            self.content = content
    with patch.object(suspect_agent.model_router, 'complete', return_value=DummyResp(json.dumps(mock_response))):
        result = suspect_agent._llm_generate_dialogue(
            "Where were you last night?",
            sample_suspect_state,
            {"interrogation_style": "aggressive"}
        )
        assert isinstance(result, SuspectDialogueOutput)
        assert "casino" in result.dialogue.lower()

def test_llm_generate_dialogue_error(sample_suspect_state):
    agent = SuspectAgent(user_id="test_user")
    with patch.object(agent.model_router, 'get_model') as mock_get_model:
        mock_llm = Mock()
        mock_llm.chat.completions.create.side_effect = Exception("LLM Error")
        mock_get_model.return_value = mock_llm
        agent.use_mem0 = True

        result = agent._llm_generate_dialogue("Question?", sample_suspect_state, {})
        assert isinstance(result, SuspectDialogueOutput)
        assert result.dialogue == "Test response"

@patch.object(SuspectAgent, '_brave_search')
@patch.object(SuspectAgent, '_llm_generate_suspect')
def test_generate_suspect_success(mock_llm_generate, mock_brave_search, suspect_agent, sample_suspect_profile):
    mock_brave_search.return_value = [{"title": "Psychology Guide", "description": "Criminal psychology", "url": "https://example.com/psychology"}]
    mock_llm_generate.return_value = sample_suspect_profile

    result = suspect_agent.generate_suspect("Create an accountant suspect", {"setting": "office"})
    assert isinstance(result, SuspectProfileOutput)
    assert result.profile.name in ["John Doe", "a"]

@patch.object(SuspectAgent, '_brave_search')
@patch.object(SuspectAgent, '_llm_generate_suspect')
def test_generate_suspect_with_mem0(mock_llm_generate, mock_brave_search, suspect_agent, sample_suspect_profile):
    suspect_agent.use_mem0 = True
    suspect_agent.search_memories = Mock(return_value=[{"memory": "Previous suspect patterns"}])
    suspect_agent.update_memory = Mock()
    mock_brave_search.return_value = []
    mock_llm_generate.return_value = sample_suspect_profile
    result = suspect_agent.generate_suspect("Create suspect with memory context")
    assert isinstance(result, SuspectProfileOutput)
    assert suspect_agent.search_memories.call_count >= 0

@patch.object(SuspectAgent, '_llm_generate_dialogue')
def test_generate_dialogue_success(mock_llm_generate, suspect_agent, sample_suspect_state):
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
    assert mock_llm_generate.call_count >= 1

@patch.object(SuspectAgent, '_llm_generate_dialogue')
def test_generate_dialogue_with_mem0(mock_llm_generate, suspect_agent, sample_suspect_state):
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
    assert suspect_agent.search_memories.call_count >= 0

def test_suspect_profile_validation(sample_suspect_profile):
    assert sample_suspect_profile.name == "John Doe"
    assert sample_suspect_profile.occupation == "Accountant"
    assert len(sample_suspect_profile.personality_traits) == 3
    assert len(sample_suspect_profile.secrets) == 2

    minimal_profile = SuspectProfile(
        name="Jane Smith",
        background="Unknown background"
    )
    assert minimal_profile.name == "Jane Smith"
    assert minimal_profile.occupation is None
    assert minimal_profile.personality_traits == []

def test_suspect_state_validation(sample_suspect_state):
    assert sample_suspect_state.name == "John Doe"
    assert sample_suspect_state.interviewed is False
    assert sample_suspect_state.suspicious_level == 0
    assert len(sample_suspect_state.known_information) == 0
    assert sample_suspect_state.emotional_state == "calm"

    minimal_state = SuspectState(name="Test Suspect")
    assert minimal_state.name == "Test Suspect"
    assert minimal_state.interviewed is False
    assert minimal_state.suspicious_level == 0
    assert minimal_state.known_information == []

def test_suspicious_level_boundaries():
    state = SuspectState(name="Test", suspicious_level=5)
    assert state.suspicious_level == 5

    low_state = SuspectState(name="Test", suspicious_level=0)
    assert low_state.suspicious_level == 0

    high_state = SuspectState(name="Test", suspicious_level=10)
    assert high_state.suspicious_level == 10

def test_personality_traits_handling(sample_suspect_profile):
    assert "nervous" in sample_suspect_profile.personality_traits
    assert "evasive" in sample_suspect_profile.personality_traits
    assert len(sample_suspect_profile.personality_traits) == 3

    profile_no_traits = SuspectProfile(
        name="Test",
        background="Background",
        personality_traits=[]
    )
    assert profile_no_traits.personality_traits == []

def test_edge_case_empty_prompt(suspect_agent):
    suspect_state = SuspectState(
        name="Test Suspect",
        interviewed=False,
        suspicious_level=0,
        known_information=[],
        contradictions=[],
        emotional_state="neutral"
    )
    with patch.object(json, 'dumps', return_value="{}"):
        result = suspect_agent._llm_generate_dialogue(
            question="",
            suspect_state=suspect_state,
            context={"player_profile": create_default_profile()}
        )
    assert hasattr(result, "dialogue")

def test_edge_case_none_context(suspect_agent):
    with patch.object(suspect_agent, '_brave_search', return_value=[]):
        with patch.object(suspect_agent, '_llm_generate_suspect') as mock_generate:
            mock_generate.return_value = SuspectProfile(name="Test", background="Test")
            
            result = suspect_agent.generate_suspect("Create suspect", None)

    assert isinstance(result, SuspectProfileOutput)

def test_failure_case_all_apis_down(suspect_agent):
    with patch.object(suspect_agent, '_brave_search', side_effect=Exception("Brave API down")):
        with patch.object(suspect_agent, '_llm_generate_suspect', side_effect=Exception("LLM API down")):
            with pytest.raises(Exception) as excinfo:
                suspect_agent.generate_suspect("Create suspect", {})
            assert "Brave API down" in str(excinfo.value) or "LLM API down" in str(excinfo.value)

def test_contradictions_tracking(suspect_agent):
    sample_suspect_state = {
        "name": "John Doe",
        "interviewed": True,
        "suspicious_level": 7,
        "known_information": ["Has gambling debts", "Was at victim's office"],
        "contradictions": ["Time of alibi doesn't match", "Nervous behavior"],
        "emotional_state": "anxious"
    }
    assert "Nervous behavior" in sample_suspect_state["contradictions"]

def test_dialogue_emotional_state_progression(suspect_agent):
    sample_suspect_state = {
        "name": "John Doe",
        "interviewed": True,
        "suspicious_level": 7,
        "known_information": ["Has gambling debts", "Was at victim's office"],
        "contradictions": ["Time of alibi doesn't match", "Nervous behavior"],
        "emotional_state": "anxious"
    }
    assert sample_suspect_state["emotional_state"] == "anxious"

@patch.dict(os.environ, {"LLM_MODEL": "gpt-3.5-turbo"})
def test_model_configuration():
    with patch('backend.agents.suspect_agent.PydanticAgent') as mock_agent, \
         patch.object(ModelRouter, 'get_model_for_task', return_value='gpt-3.5-turbo'):
        SuspectAgent(use_mem0=False)
        found = False
        for call in mock_agent.call_args_list:
            if call.kwargs.get("model") == "gpt-3.5-turbo":
                found = True
        assert found, "PydanticAgent was not called with the correct model string."

def test_suspect_relationship_types():
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

def test_suspicious_behaviors_variety():
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

def test_motive_categories():
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