"""
Example script demonstrating the use of the PydanticAI-enhanced CoordinatorAgent.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.coordinator_agent import (
    CoordinatorAgent, 
    StoryAgentState, 
    SuspectAgentState, 
    ClueAgentState, 
    BoardAgentState
)

# Load environment variables
load_dotenv()

def main():
    """Run a simple example of the CoordinatorAgent with PydanticAI."""
    print("Initializing CoordinatorAgent with PydanticAI...")
    
    # Create a CoordinatorAgent instance
    agent = CoordinatorAgent(use_mem0=True, user_id="example_user")
    
    # Create sample agent states
    story_state = StoryAgentState(
        agent_name="StoryAgent",
        current_scene="The Museum",
        narrative="Detective Smith examines the empty display case where the artifact was stolen.",
        discovered_clues=["fingerprints", "disabled_camera"],
        state_data={
            "title": "The Missing Artifact",
            "suspect_states": {
                "suspect1": {
                    "name": "Professor Johnson",
                    "interviewed": True,
                    "suspicion_level": 3
                },
                "suspect2": {
                    "name": "Curator Williams",
                    "interviewed": False,
                    "suspicion_level": 2
                }
            }
        }
    )
    
    suspect_state = SuspectAgentState(
        agent_name="SuspectAgent",
        suspect_profiles={
            "suspect1": {
                "name": "Professor Johnson",
                "description": "An archaeology professor with expertise in ancient artifacts",
                "motive": "Academic recognition",
                "alibi": "Claims to have been at a conference"
            },
            # Note: suspect2 is missing from suspect profiles but exists in story state
        },
        dialogue_history={
            "suspect1": [
                "I was at the conference all evening, you can check with the organizers."
            ]
        },
        state_data={}
    )
    
    clue_state = ClueAgentState(
        agent_name="ClueAgent",
        clues={
            "fingerprints": {
                "name": "Fingerprints on Display Case",
                "description": "Partial fingerprints found on the edge of the display case",
                "type": "physical",
                "relevance": "high"
            },
            "disabled_camera": {
                "name": "Disabled Security Camera",
                "description": "The security camera was disabled at 10:30 PM",
                "type": "electronic",
                "relevance": "high"
            }
        },
        connections=[
            {"from": "fingerprints", "to": "suspect1", "strength": "medium"}
        ],
        state_data={}
    )
    
    board_state = BoardAgentState(
        agent_name="BoardAgent",
        board_elements={
            "element_fingerprints": {
                "type": "clue",
                "clue_id": "fingerprints",
                "name": "Fingerprints on Display Case",
                "position": {"x": 100, "y": 100},
                "size": {"width": 150, "height": 100},
                "color": "#f0f0f0"
            }
            # Note: disabled_camera clue is missing from the board
        },
        visual_connections=[],
        state_data={}
    )
    
    # Prepare input for synchronization
    input_data = {
        "story_state": story_state.model_dump(),
        "suspect_state": suspect_state.model_dump(),
        "clue_state": clue_state.model_dump(),
        "board_state": board_state.model_dump(),
        "action": "interview Professor Johnson about his alibi",
        "context": {
            "player_role": "detective",
            "investigation_stage": "initial"
        }
    }
    
    # Synchronize agent states
    print("\nSynchronizing agent states...")
    result = agent.synchronize(input_data)
    
    # Print the results
    print("\nConflicts detected and resolved:")
    for conflict in result.get("conflicts_resolved", []):
        print(f"- {conflict.get('conflict_type')}: {conflict.get('description')}")
        print(f"  Resolution: {conflict.get('resolution')}")
    
    # Get recommendations for next actions
    print("\nGetting recommendations for next actions...")
    recommendations = agent.recommend_actions(input_data)
    
    print("\nRecommendations:")
    for agent_name, recommendation in recommendations.get("recommendations", {}).items():
        print(f"- {agent_name}: {recommendation}")
    
    print("\nExample completed.")

if __name__ == "__main__":
    main()
