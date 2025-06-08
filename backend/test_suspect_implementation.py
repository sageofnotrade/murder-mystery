#!/usr/bin/env python3
"""
Simple test script to verify suspect implementation works.
"""

import sys
import os
import unittest.mock as mock

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
        from backend.routes.suspect_routes import suspect_bp
        print("✓ Suspect routes imports successful")
    except Exception as e:
        print(f"✗ Import error: {e}")
        assert False, f"Import error: {e}"

def test_suspect_agent():
    """Test basic SuspectAgent functionality."""
    try:
        print("\nTesting SuspectAgent basic functionality...")
        with mock.patch.dict(os.environ, {"LLM_MODEL": "test"}):
            with mock.patch('pydantic_ai.Agent'):
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
    except Exception as e:
        print(f"✗ SuspectAgent test error: {e}")
        assert False, f"SuspectAgent test error: {e}"

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
    except Exception as e:
        print(f"✗ Pydantic models test error: {e}")
        assert False, f"Pydantic models test error: {e}" 