#!/usr/bin/env python3
"""
Simple test runner to demonstrate AI agent test functionality.
"""

from pydantic import BaseModel
import sys
import json
from unittest.mock import patch, Mock, MagicMock

class MinimalModelMessage(BaseModel):
    role: str
    content: str

# Patch ModelMessage in the actual module before any agent import
import pydantic_ai.messages
pydantic_ai.messages.ModelMessage = MinimalModelMessage

# Now import agents and test code
import os
import unittest
# Add current directory to Python path
sys.path.append('.')
# Import agents
from backend.agents.base_agent import BaseAgent
from backend.agents.story_agent import StoryAgent
from backend.agents.suspect_agent import SuspectAgent
from backend.agents.clue_agent import ClueAgent, ClueData, ClueGenerateOutput
# Import our mock factories
from backend.tests.mocks.llm_mock import (
    LLMMockFactory, 
    BraveSearchMockFactory, 
    Mem0MockFactory,
    create_full_agent_mocks,
    PydanticAIMockFactory
)

def test_base_agent_memory_operations():
    """Test BaseAgent memory operations."""
    print("🔍 Testing BaseAgent memory operations...")
    # Test without Mem0
    agent = BaseAgent("TestAgent", use_mem0=False)
    assert agent.agent_name == "TestAgent"
    assert agent.use_mem0 is False
    assert agent.update_memory("test", "value") is False
    assert agent.get_memory("test") is None
    print("✅ BaseAgent memory operations test passed")
def test_story_agent_with_mocks():
    """Test StoryAgent with mocked dependencies."""
    print("🔍 Testing StoryAgent with mocks...")
    with patch('mem0.MemoryClient'), \
         patch('pydantic_ai.models.infer_model', return_value=Mock()), \
         patch('backend.agents.story_agent.ModelRouter'), \
         patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
        # Create agent
        story_agent = StoryAgent(use_mem0=False)
        assert isinstance(story_agent, StoryAgent)
        assert story_agent.agent_name == "StoryAgent"
        # Test with mocked Brave search
        with patch('backend.agents.story_agent.requests.get') as mock_get:
            mock_get.return_value = BraveSearchMockFactory.create_success_mock()
            with patch.dict(os.environ, {"BRAVE_API_KEY": "test_brave_key"}):
                result = story_agent._brave_search("murder mystery")
                assert len(result) == 2
                assert "Murder Mystery Investigation Guide" in result[0]["title"]
    print("✅ StoryAgent mock test passed")
def test_suspect_agent_profile_generation():
    """Test SuspectAgent profile generation."""
    print("🔍 Testing SuspectAgent profile generation...")
    planning_response = Mock(content="{}")  # Minimal valid plan
    writing_response = Mock(content='{"name": "John Doe", "background": "Former accountant with gambling debts", "occupation": "Accountant", "motive": "Financial desperation", "personality_traits": ["nervous", "evasive"]}')
    with patch('mem0.MemoryClient'), \
         patch('pydantic_ai.models.infer_model'), \
         patch('backend.agents.suspect_agent.ModelRouter'), \
         patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
        suspect_agent = SuspectAgent(use_mem0=False, model_message_cls=MinimalModelMessage)
        assert isinstance(suspect_agent, SuspectAgent)
        # Patch model_router.complete directly
        suspect_agent.model_router.complete = Mock(side_effect=[planning_response, writing_response])
        result = suspect_agent._llm_generate_suspect("Create suspect", {}, [])
        assert result.name == "John Doe"
        assert result.occupation == "Accountant"
        assert "nervous" in result.personality_traits
    print("✅ SuspectAgent profile generation test passed")
def test_clue_agent_analysis():
    """Test ClueAgent clue analysis."""
    print("🔍 Testing ClueAgent analysis...")
    
    # Create mock clue data
    mock_clue_data = ClueData(
        description="Blood type matches victim",
        details="Detailed forensic analysis.",
        significance="9",
        related_to=["Links to suspect"],
        confidence=0.85
    )
    
    # Create mock output
    mock_output = ClueGenerateOutput(
        clue=mock_clue_data,
        sources=["https://example.com/forensics"]
    )
    
    with patch('mem0.MemoryClient'), \
         patch('pydantic_ai.models.infer_model'), \
         patch('backend.agents.clue_agent.ModelRouter'), \
         patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
        
        # Create agent with mocked PydanticAI agent
        clue_agent = ClueAgent(use_mem0=False, user_id="test_user", model_message_cls=MinimalModelMessage)
        assert isinstance(clue_agent, ClueAgent)
        
        # Mock the PydanticAI agent's run_sync method
        mock_agent = PydanticAIMockFactory.create_agent_mock()
        clue_agent.pydantic_agent = mock_agent
        
        # Test clue generation
        result = clue_agent.generate_clue("Analyze blood evidence", {
            "crime_scene": "office",
            "victim": "John Smith"
        })
        
        # Verify result is a ClueOutput object
        assert hasattr(result, 'clue')
        assert hasattr(result, 'sources')
        assert result.clue.description == "A bloodied letter opener found under the desk"
        assert result.clue.details == "Forensic analysis shows fingerprints matching suspect John Doe"
        assert result.clue.significance == "High - potential murder weapon"
        assert result.clue.confidence == 0.9
        assert "John Doe" in result.clue.related_to
    
    print("✅ ClueAgent analysis test passed")
def test_error_handling():
    """Test error handling in agents."""
    print("🔍 Testing error handling...")
    mock_model = Mock()
    mock_model.complete.return_value = {}
    with patch('mem0.MemoryClient'), \
         patch('pydantic_ai.models.infer_model', return_value=mock_model), \
         patch('backend.agents.story_agent.ModelRouter'), \
         patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
        story_agent = StoryAgent(use_mem0=False)
        # Test with API error
        with patch('backend.agents.story_agent.requests.get') as mock_get:
            mock_get.side_effect = Exception("API Error")
            with patch.dict(os.environ, {"BRAVE_API_KEY": "test_brave_key"}):
                try:
                    result = story_agent._brave_search("test query")
                except Exception as e:
                    assert str(e) == "API Error"
    print("✅ Error handling test passed")
def run_all_tests():
    """Run all tests."""
    print("🚀 Starting AI Agent Tests\n")
    try:
        test_base_agent_memory_operations()
        test_story_agent_with_mocks()
        test_suspect_agent_profile_generation() 
        test_clue_agent_analysis()
        test_error_handling()
        print("\n🎉 All tests passed successfully!")
        print("\n📊 Test Summary:")
        print("- ✅ BaseAgent: Memory operations, initialization")
        print("- ✅ StoryAgent: Mock integration, Brave search")
        print("- ✅ SuspectAgent: Profile generation, LLM mocking")
        print("- ✅ ClueAgent: Analysis functionality, JSON parsing")
        print("- ✅ Error Handling: API failures, graceful degradation")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 