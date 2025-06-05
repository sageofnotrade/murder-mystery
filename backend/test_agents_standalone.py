#!/usr/bin/env python3
"""
Standalone AI Agent Tests
Tests the agents without Flask app dependencies
"""

import sys
import os
import traceback
from unittest.mock import Mock, patch, MagicMock

# Add current directory to Python path
sys.path.append('.')
sys.path.append('./backend')
sys.path.append('../backend')

def test_mock_infrastructure():
    """Test that our mock infrastructure works."""
    try:
        print("  → Importing LLMMockFactory...")
        from tests.mocks.llm_mock import LLMMockFactory
        
        print("  → Creating OpenAI mock...")
        # Test basic LLM mock
        mock_llm = LLMMockFactory.create_openai_mock("Test response")
        response = mock_llm.chat.completions.create()
        assert response.choices[0].message.content == "Test response"
        
        print("✅ Mock infrastructure test passed")
        return True
    except Exception as e:
        print(f"❌ Mock infrastructure test failed: {e}")
        print(f"   Current working directory: {os.getcwd()}")
        print(f"   Python path: {sys.path[:3]}...")
        traceback.print_exc()
        return False

def test_models_import():
    """Test that our models can be imported."""
    try:
        print("  → Importing template models...")
        from models.template_models import MysteryTemplate, Suspect, Clue
        print("  → Importing story models...")
        from models.story_models import StoryState, PlayerAction, StoryChoice
        print("  → Importing clue models...")
        from models.clue_models import ClueAnalysis, ClueConnection
        
        print("  → Creating test models...")
        # Test basic model creation
        suspect = Suspect(
            name="John Doe",
            occupation="Butler", 
            background="Worked for the family for 10 years",
            motive="Financial desperation",
            alibi="Was in the kitchen",
            relationship_to_victim="Employee"
        )
        
        clue = Clue(
            type="physical",
            description="Bloody knife",
            location="Library",
            significance=8,
            reliability=0.9
        )
        
        template = MysteryTemplate(
            title="Test Mystery",
            description="A test mystery",
            setting="Mansion"
        )
        
        assert suspect.name == "John Doe"
        assert clue.type == "physical"
        assert template.title == "Test Mystery"
        
        print("✅ Models import test passed")
        return True
    except Exception as e:
        print(f"❌ Models import test failed: {e}")
        traceback.print_exc()
        return False

def test_agent_mocks():
    """Test agent-specific mocks without importing actual agents."""
    try:
        print("  → Testing agent-specific mocks...")
        from tests.mocks.llm_mock import LLMMockFactory
        import json
        
        # Test story agent mock
        print("  → Testing story agent mock...")
        story_mock = LLMMockFactory.create_story_response_mock()
        response = story_mock.chat.completions.create()
        story_data = json.loads(response.choices[0].message.content)
        assert "narrative" in story_data
        
        # Test suspect agent mock  
        print("  → Testing suspect agent mock...")
        suspect_mock = LLMMockFactory.create_suspect_response_mock()
        response = suspect_mock.chat.completions.create()
        suspect_data = json.loads(response.choices[0].message.content)
        assert suspect_data["name"] == "John Doe"
        
        # Test clue agent mock
        print("  → Testing clue agent mock...")
        clue_mock = LLMMockFactory.create_clue_analysis_mock()
        response = clue_mock.chat.completions.create()
        clue_data = json.loads(response.choices[0].message.content)
        assert clue_data["significance"] == 9
        
        print("✅ Agent mocks test passed")
        return True
    except Exception as e:
        print(f"❌ Agent mocks test failed: {e}")
        traceback.print_exc()
        return False

def test_basic_python_environment():
    """Test basic Python environment and dependencies."""
    try:
        print("  → Testing Python environment...")
        print(f"     Python version: {sys.version}")
        print(f"     Working directory: {os.getcwd()}")
        
        # Test basic imports
        import json
        import datetime
        from typing import Dict, List
        from unittest.mock import Mock
        
        # Test pydantic
        try:
            from pydantic import BaseModel
            print("     ✓ Pydantic available")
        except ImportError:
            print("     ✗ Pydantic not available")
            return False
            
        print("✅ Python environment test passed")
        return True
    except Exception as e:
        print(f"❌ Python environment test failed: {e}")
        return False

def run_standalone_tests():
    """Run all standalone tests."""
    print("🚀 Running Standalone AI Agent Tests")
    print(f"   Environment: Python {sys.version_info.major}.{sys.version_info.minor}")
    print(f"   Directory: {os.getcwd()}\n")
    
    tests = [
        test_basic_python_environment,
        test_mock_infrastructure,
        test_models_import,
        test_agent_mocks
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print(f"Running {test.__name__}...")
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            traceback.print_exc()
            failed += 1
        print()
    
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All standalone tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = run_standalone_tests()
    sys.exit(0 if success else 1) 