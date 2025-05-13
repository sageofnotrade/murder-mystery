"""
Basic example demonstrating Mem0 integration with the StoryAgent.

This script shows how to use Mem0 for persistent memory in the StoryAgent.

Requirements:
- Set MEM0_API_KEY in your .env file
- Install required packages: pip install python-dotenv mem0
"""

import os
from dotenv import load_dotenv
from backend.agents.story_agent import StoryAgent

# Load environment variables
load_dotenv()

def main():
    # Check if Mem0 API key is set
    mem0_api_key = os.getenv("MEM0_API_KEY")
    if not mem0_api_key:
        print("Error: MEM0_API_KEY not found in environment variables.")
        print("Please set it in your .env file.")
        return
    
    # Create a unique user ID for this example
    user_id = "example_user_123"
    print(f"Using user ID: {user_id}")
    
    # Create a StoryAgent with Mem0 enabled
    print("\n--- Creating StoryAgent with Mem0 Enabled ---")
    agent = StoryAgent(use_mem0=True, user_id=user_id)
    
    # Store some memories
    print("\n--- Storing Memories ---")
    agent.update_memory("character_detective", "Detective James Morrison")
    agent.update_memory("character_suspect", "Marina owner with gambling debts")
    agent.update_memory("setting_location", "Coastal town of Blackwater Bay")
    
    # Generate a story with the initial context
    print("\n--- Generating Initial Story ---")
    result = agent.generate_story(
        "A detective investigating suspicious activity at a marina", 
        {"player_role": "detective"}
    )
    
    print("\nGenerated Story:")
    print(result.story[:500] + "..." if len(result.story) > 500 else result.story)
    
    # Demonstrate memory retrieval
    print("\n--- Retrieving Memories ---")
    detective = agent.get_memory("character_detective")
    suspect = agent.get_memory("character_suspect")
    location = agent.get_memory("setting_location")
    
    print(f"Detective: {detective}")
    print(f"Suspect: {suspect}")
    print(f"Location: {location}")
    
    # Search for memories
    print("\n--- Searching Memories ---")
    memories = agent.search_memories("marina detective")
    print(f"Found {len(memories)} memories")
    for i, memory in enumerate(memories[:3], 1):
        print(f"{i}. {memory.get('memory', '')}")
    
    # Generate another story with memory enhancement
    print("\n--- Generating Second Story with Memory Enhancement ---")
    result2 = agent.generate_story(
        "The detective continues the investigation at night", 
        {"player_role": "detective"}
    )
    
    print("\nSecond Generated Story:")
    print(result2.story[:500] + "..." if len(result2.story) > 500 else result2.story)
    
    # Clean up memories
    print("\n--- Cleaning Up Memories ---")
    agent.clear_memories()
    print("Memories cleared.")
    
    print("\nExample completed successfully!")

if __name__ == "__main__":
    main()