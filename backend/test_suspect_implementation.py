#!/usr/bin/env python3
"""
Simple test script to verify suspect implementation works.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all suspect-related modules can be imported."""
    try:
        print("Testing SuspectAgent import...")
        from agents.suspect_agent import SuspectAgent, SuspectState, SuspectProfile
        print("✓ SuspectAgent imports successful")
        
        print("Testing SuspectService import...")
        from services.suspect_service import SuspectService
        print("✓ SuspectService imports successful")
        
        print("Testing suspect models import...")
        from models.suspect_models import (
            CreateSuspectRequest, 
            DialogueRequest, 
            SuspectEmotionalState
        )
        print("✓ Suspect models imports successful")
        
        print("Testing suspect routes import...")
        from routes.suspect_routes import suspect_bp
        print("✓ Suspect routes imports successful")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_suspect_agent():
    """Test basic SuspectAgent functionality."""
    try:
        print("\nTesting SuspectAgent basic functionality...")
        from agents.suspect_agent import SuspectAgent, SuspectState
        
        # Create agent without memory for testing
        agent = SuspectAgent(use_mem0=False)
        print("✓ SuspectAgent created successfully")
        
        # Test suspect state creation
        state = SuspectState(
            name="Test Suspect",
            interviewed=False,
            suspicious_level=0,
            known_information=[],
            contradictions=[],
            emotional_state=None
        )
        print("✓ SuspectState created successfully")
        
        return True
    except Exception as e:
        print(f"✗ SuspectAgent test error: {e}")
        return False

def test_pydantic_models():
    """Test Pydantic model validation."""
    try:
        print("\nTesting Pydantic models...")
        from models.suspect_models import CreateSuspectRequest, DialogueRequest
        
        # Test CreateSuspectRequest
        create_req = CreateSuspectRequest(
            story_id="test-story",
            name="Test Suspect",
            profile_data={"occupation": "Teacher"}
        )
        print("✓ CreateSuspectRequest validation successful")
        
        # Test DialogueRequest
        dialogue_req = DialogueRequest(
            question="Where were you last night?",
            story_id="test-story",
            context={"style": "aggressive"}
        )
        print("✓ DialogueRequest validation successful")
        
        return True
    except Exception as e:
        print(f"✗ Pydantic models test error: {e}")
        return False

def main():
    """Run all tests."""
    print("=== Testing Suspect Implementation ===\n")
    
    results = []
    results.append(test_imports())
    results.append(test_suspect_agent())
    results.append(test_pydantic_models())
    
    print(f"\n=== Test Results ===")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✓ All tests passed! Suspect implementation looks good.")
        return 0
    else:
        print("✗ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 