import os
from dotenv import load_dotenv
from agents.story_agent import StoryAgent
from agents.suspect_agent import SuspectAgent, SuspectState
from agents.clue_agent import ClueAgent
from agents.board_agent import BoardAgent
from agents.coordinator_agent import CoordinatorAgent
from agents.model_router import ModelRouter

# Load environment variables
load_dotenv()

# Ensure required environment variables are set
required_env_vars = {
    "OPENROUTER_API_KEY": "Your OpenRouter API key",
    "LLM_API_BASE": "https://openrouter.ai/api/v1",
    "REDIS_URL": "redis://localhost:6379/0"  # Optional, for caching
}

def check_environment():
    """Check if all required environment variables are set"""
    missing_vars = []
    for var, description in required_env_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in your .env file")
        return False
    return True

def test_story_agent():
    """Test the StoryAgent's LLM generation capabilities"""
    agent = StoryAgent(use_mem0=False)
    
    # Test story generation
    prompt = "Create a murder mystery set in a Victorian mansion"
    result = agent.generate_story(prompt)
    print("\n=== Story Generation Test ===")
    print(f"Prompt: {prompt}")
    print(f"Generated Story: {result.story}")
    print(f"Sources: {result.sources}")

def test_suspect_agent():
    """Test the suspect agent's profile generation capabilities."""
    print("\n=== Suspect Profile Generation Test ===")
    
    # Initialize the agent
    agent = SuspectAgent(use_mem0=False)
    
    # Test context
    context = {
        "crime": "museum theft",
        "location": "Metropolitan Museum of Art",
        "victim": "Curator James Wilson"
    }
    
    # Generate a suspect profile
    result = agent.generate_suspect("John Doe, art thief", context)
    
    # Print results
    print("\nGenerated Suspect Profile:")
    print(f"Name: {result.profile.name}")
    print(f"Background: {result.profile.background}")
    print(f"Occupation: {result.profile.occupation}")
    print(f"Motive: {result.profile.motive}")
    print(f"Alibi: {result.profile.alibi}")
    print(f"Personality Traits: {', '.join(result.profile.personality_traits)}")
    print(f"Relationship to Victim: {result.profile.relationship_to_victim}")
    print(f"Suspicious Behaviors: {', '.join(result.profile.suspicious_behaviors)}")
    print(f"Secrets: {', '.join(result.profile.secrets)}")
    print(f"\nSources: {result.sources}")
    
    # Test dialogue generation
    print("\n=== Suspect Dialogue Test ===")
    suspect_state = SuspectState(
        name=result.profile.name,
        interviewed=False,
        suspicious_level=0,
        known_information=[],
        contradictions=[],
        emotional_state="neutral"
    )
    
    dialogue_result = agent.generate_dialogue(
        "Where were you on the night of the theft?",
        suspect_state,
        context
    )
    
    print("\nGenerated Dialogue:")
    print(dialogue_result.dialogue)
    print(f"\nUpdated Suspect State:")
    print(f"Interviewed: {dialogue_result.updated_state.interviewed}")
    print(f"Suspicious Level: {dialogue_result.updated_state.suspicious_level}")
    print(f"Emotional State: {dialogue_result.updated_state.emotional_state}")

def test_clue_agent():
    """Test the ClueAgent's LLM generation capabilities"""
    agent = ClueAgent(use_mem0=False)
    
    # Test clue generation
    context = {
        "location": "Victorian mansion library",
        "crime_scene": "A body found in a locked room",
        "existing_clues": ["A broken window", "Footprints in the garden"]
    }
    result = agent.generate_clue(context)
    print("\n=== Clue Generation Test ===")
    print(f"Context: {context}")
    print(f"Generated Clue: {result}")

def test_board_agent():
    """Test the BoardAgent's LLM generation capabilities"""
    agent = BoardAgent(use_mem0=False)
    
    # Test board generation
    context = {
        "current_state": "Investigation in progress",
        "discovered_clues": ["A broken window", "Footprints in the garden"],
        "suspects": ["Professor Moriarty", "Lady Blackwood", "Dr. Watson"]
    }
    result = agent.generate_board("Create a board for the museum theft case", context)
    print("\n=== Board Generation Test ===")
    print(f"Context: {context}")
    print(f"Generated Board:")
    print(f"Elements: {len(result.board_state.elements)}")
    print(f"Connections: {len(result.board_state.connections)}")
    print(f"Sources: {len(result.sources)}")

def test_coordinator_agent():
    """Test the coordinator agent's ability to manage agent interactions."""
    print("\n=== Coordinator Agent Test ===")
    
    # Create test context
    context = {
        "action": "investigate_clue",
        "player_profile": {
            "cognitive_style": "analytical",
            "emotional_tendency": "neutral",
            "social_style": "methodical"
        },
        "story_state": {
            "agent_name": "StoryAgent",
            "current_scene": "library",
            "narrative": "The investigation continues in the library",
            "discovered_clues": ["broken_window", "footprints"]
        },
        "suspect_state": {
            "agent_name": "SuspectAgent",
            "suspect_profiles": {
                "professor": {
                    "name": "Professor Moriarty",
                    "background": "Retired mathematics professor"
                }
            }
        }
    }
    
    # Initialize and test coordinator
    agent = CoordinatorAgent(use_mem0=False)
    result = agent.synchronize(context)
    
    print("\nCoordinated State:")
    print(f"Success: {result.get('success', False)}")
    print(f"Conflicts Resolved: {len(result.get('conflicts_resolved', []))}")
    print(f"Recommendations: {result.get('recommendations', {})}")
    print(f"Sources: {result.get('sources', [])}")

def main():
    """Run all agent tests"""
    print("Starting LLM Generation Tests...")
    
    # Check environment variables first
    if not check_environment():
        return
    
    # Test each agent
    test_story_agent()
    test_suspect_agent()
    test_clue_agent()
    test_board_agent()
    test_coordinator_agent()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main() 