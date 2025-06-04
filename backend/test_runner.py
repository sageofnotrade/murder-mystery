#!/usr/bin/env python3
"""
Simple test runner to demonstrate AI agent test functionality.
"""

import sys
import os
import unittest
from unittest.mock import patch, Mock
import json

# Add current directory to Python path
sys.path.append('.')

# Import agents
from agents.base_agent import BaseAgent
from agents.story_agent import StoryAgent
from agents.suspect_agent import SuspectAgent
from agents.clue_agent import ClueAgent

# Import our mock factories
from tests.mocks.llm_mock import (
    LLMMockFactory, 
    BraveSearchMockFactory, 
    Mem0MockFactory,
    create_full_agent_mocks
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
    
    with patch('agents.story_agent.mem0'), \
         patch('agents.story_agent.ModelRouter'), \
         patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
        
        # Create agent
        story_agent = StoryAgent(use_mem0=False)
        assert story_agent.agent_name == "StoryAgent"
        
        # Test with mocked Brave search
        with patch('agents.story_agent.requests.get') as mock_get:
            mock_get.return_value = BraveSearchMockFactory.create_success_mock()
            
            with patch.dict(os.environ, {"BRAVE_API_KEY": "test_brave_key"}):
                result = story_agent._brave_search("murder mystery")
                assert len(result) == 2
                assert "Murder Mystery Investigation Guide" in result[0]["title"]
    
    print("✅ StoryAgent mock test passed")

def test_suspect_agent_profile_generation():
    """Test SuspectAgent profile generation."""
    print("🔍 Testing SuspectAgent profile generation...")
    
    with patch('agents.suspect_agent.mem0'), \
         patch('agents.suspect_agent.ModelRouter'), \
         patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
        
        suspect_agent = SuspectAgent(use_mem0=False)
        
        # Mock LLM response for suspect generation
        mock_response_data = {
            "name": "John Doe",
            "background": "Former accountant with gambling debts",
            "occupation": "Accountant",
            "motive": "Financial desperation",
            "personality_traits": ["nervous", "evasive"]
        }
        
        with patch.object(suspect_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = LLMMockFactory.create_json_response_mock(mock_response_data)
            mock_get_model.return_value = mock_llm
            
            result = suspect_agent._llm_generate_suspect("Create suspect", {}, [])
            assert result.name == "John Doe"
            assert result.occupation == "Accountant"
            assert "nervous" in result.personality_traits
    
    print("✅ SuspectAgent profile generation test passed")

def test_clue_agent_analysis():
    """Test ClueAgent clue analysis."""
    print("🔍 Testing ClueAgent analysis...")
    
    with patch('agents.clue_agent.mem0'), \
         patch('agents.clue_agent.ModelRouter'), \
         patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
        
        clue_agent = ClueAgent(use_mem0=False)
        
        # Mock clue analysis response
        mock_analysis = {
            "forensic_details": "Blood type matches victim",
            "significance": 9,
            "reliability": 0.85,
            "connections": ["Links to suspect"]
        }
        
        sample_clue = {
            "type": "physical",
            "description": "Bloody knife",
            "location": "kitchen"
        }
        
        with patch.object(clue_agent.model_router, 'get_model') as mock_get_model:
            mock_llm = LLMMockFactory.create_json_response_mock(mock_analysis)
            mock_get_model.return_value = mock_llm
            
            result = clue_agent.analyze_clue(sample_clue, {})
            assert result["significance"] == 9
            assert result["reliability"] == 0.85
            assert "Blood type matches victim" in result["forensic_details"]
    
    print("✅ ClueAgent analysis test passed")

def test_error_handling():
    """Test error handling in agents."""
    print("🔍 Testing error handling...")
    
    with patch('agents.story_agent.mem0'), \
         patch('agents.story_agent.ModelRouter'), \
         patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
        
        story_agent = StoryAgent(use_mem0=False)
        
        # Test with API error
        with patch('agents.story_agent.requests.get') as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            with patch.dict(os.environ, {"BRAVE_API_KEY": "test_brave_key"}):
                result = story_agent._brave_search("test query")
                assert result == []  # Should return empty list on error
    
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