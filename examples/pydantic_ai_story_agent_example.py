"""
Example script demonstrating the use of the PydanticAI-enhanced StoryAgent.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.story_agent import StoryAgent, PlayerProfile, StoryState

# Load environment variables
load_dotenv()

def main():
    """Run a simple example of the StoryAgent with PydanticAI."""
    print("Initializing StoryAgent with PydanticAI...")
    
    # Create a StoryAgent instance
    agent = StoryAgent(use_mem0=True, user_id="example_user")
    
    # Create a simple template
    template = {
        "id": "example_mystery",
        "title": "The Missing Artifact",
        "suspects": [
            {"id": "suspect1", "name": "Professor Smith", "initial_suspicion": 2},
            {"id": "suspect2", "name": "Curator Johnson", "initial_suspicion": 1},
            {"id": "suspect3", "name": "Security Guard Davis", "initial_suspicion": 3}
        ]
    }
    
    # Create a player profile
    player_profile = {
        "psychological_traits": {
            "analytical": "high",
            "intuitive": "medium",
            "risk_taking": "low"
        },
        "preferences": {
            "story_pace": "moderate",
            "complexity": "high",
            "theme": "historical"
        },
        "role": "detective"
    }
    
    # Start a new story
    print("\nStarting a new story...")
    story_state_dict = agent.start_new_story(template, player_profile)
    story_state = StoryState(**story_state_dict)
    
    print(f"Story title: {story_state.title}")
    print(f"Current scene: {story_state.current_scene}")
    print(f"Suspects: {', '.join([suspect.name for suspect in story_state.suspect_states.values()])}")
    
    # Generate a story
    print("\nGenerating a story...")
    story_result = agent.generate_story(
        "A valuable ancient artifact has disappeared from the museum. The security cameras were disabled, and there are three main suspects.",
        {"player_role": "detective", "setting": "modern museum", "time_period": "present day"}
    )
    
    print("\nGenerated Story:")
    print(story_result.story[:500] + "..." if len(story_result.story) > 500 else story_result.story)
    print(f"\nSources: {', '.join(story_result.sources[:3])}")
    
    # Process player actions
    print("\nProcessing player actions...")
    
    # First action
    action1 = "examine the display case where the artifact was kept"
    input_data1 = {
        "action": action1,
        "story_state": story_state,
        "player_profile": PlayerProfile(**player_profile)
    }
    
    result1 = agent.process(input_data1)
    story_state = StoryState(**result1["story_state"])
    
    print(f"\nAction: {action1}")
    print(f"Narrative: {result1['narrative'][:300]}...")
    print(f"Discovered clues: {', '.join(story_state.discovered_clues)}")
    
    # Second action
    action2 = "interview Professor Smith about his whereabouts during the theft"
    input_data2 = {
        "action": action2,
        "story_state": story_state,
        "player_profile": PlayerProfile(**player_profile)
    }
    
    result2 = agent.process(input_data2)
    story_state = StoryState(**result2["story_state"])
    
    print(f"\nAction: {action2}")
    print(f"Narrative: {result2['narrative'][:300]}...")
    
    # Check if the suspect was interviewed
    for suspect_id, suspect in story_state.suspect_states.items():
        if "Smith" in suspect.name:
            print(f"Professor Smith interviewed: {suspect.interviewed}")
    
    print("\nExample completed successfully!")

if __name__ == "__main__":
    main()
