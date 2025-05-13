"""
Advanced example demonstrating Mem0 integration with custom configuration.

This script shows how to use Mem0 with custom configuration options
to fine-tune memory retrieval and storage for the StoryAgent.

Requirements:
- Set MEM0_API_KEY in your .env file
- Install required packages: pip install python-dotenv mem0
"""

import os
import time
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
    user_id = f"example_user_{int(time.time())}"
    print(f"Using user ID: {user_id}")
    
    # Advanced Mem0 configuration
    mem0_config = {
        "search_limit": 7,           # Retrieve more memories than default
        "search_threshold": 0.6,      # Lower threshold for more inclusive results
        "rerank": True,               # Use reranking for better relevance
        "store_summaries": True,      # Store summaries of generated content
        "track_performance": True,    # Track performance metrics
        "version": "v2"               # Use Mem0 API v2
    }
    
    # Create a StoryAgent with enhanced Mem0 configuration
    print("\n--- Creating StoryAgent with Advanced Mem0 Configuration ---")
    agent = StoryAgent(use_mem0=True, user_id=user_id, mem0_config=mem0_config)
    
    # Store a variety of memories with different contexts
    print("\n--- Storing Diverse Memories ---")
    agent.update_memory("character_detective", "Detective James Morrison, ex-military with PTSD")
    agent.update_memory("character_suspect", "Marina owner with gambling debts")
    agent.update_memory("character_witness", "Dock worker who saw strange lights")
    agent.update_memory("setting_location", "Coastal town of Blackwater Bay")
    agent.update_memory("setting_time", "Winter, during a week of heavy storms")
    agent.update_memory("setting_mood", "Tense, suspicious atmosphere among locals")
    agent.update_memory("clue_1", "Muddy boot prints leading to the water")
    agent.update_memory("clue_2", "Missing logbook with shipping records")
    agent.update_memory("clue_3", "Encrypted message on victim's computer")
    
    # Generate a story with the initial context
    print("\n--- Generating Initial Story ---")
    result = agent.generate_story(
        "A detective investigating suspicious activity at a marina", 
        {"player_role": "detective"}
    )
    
    print("\nGenerated Story:")
    print(result.story[:500] + "..." if len(result.story) > 500 else result.story)
    
    # Demonstrate memory search with different parameters
    print("\n--- Demonstrating Memory Search with Different Parameters ---")
    
    # 1. Default search (using config values)
    print("\n1. Default Search (using config values):")
    default_memories = agent.search_memories("detective marina investigation")
    print(f"Found {len(default_memories)} memories")
    for i, memory in enumerate(default_memories[:3], 1):
        print(f"{i}. {memory.get('memory', '')}")
    
    # 2. High relevance search
    print("\n2. High Relevance Search (threshold=0.8):")
    high_relevance = agent.search_memories("detective marina investigation", threshold=0.8)
    print(f"Found {len(high_relevance)} memories")
    for i, memory in enumerate(high_relevance[:3], 1):
        print(f"{i}. {memory.get('memory', '')}")
    
    # 3. More inclusive search
    print("\n3. More Inclusive Search (threshold=0.5, limit=10):")
    inclusive = agent.search_memories("detective marina investigation", threshold=0.5, limit=10)
    print(f"Found {len(inclusive)} memories")
    for i, memory in enumerate(inclusive[:5], 1):
        print(f"{i}. {memory.get('memory', '')}")
    
    # 4. Without reranking
    print("\n4. Without Reranking:")
    no_rerank = agent.search_memories("detective marina investigation", rerank=False)
    print(f"Found {len(no_rerank)} memories")
    for i, memory in enumerate(no_rerank[:3], 1):
        print(f"{i}. {memory.get('memory', '')}")
    
    # Generate a story with a different perspective
    print("\n--- Generating Story from Suspect Perspective ---")
    suspect_result = agent.generate_story(
        "A marina owner hiding evidence of smuggling", 
        {"player_role": "suspect"}
    )
    
    print("\nSuspect Perspective Story:")
    print(suspect_result.story[:500] + "..." if len(suspect_result.story) > 500 else suspect_result.story)
    
    # Demonstrate memory persistence by creating a new agent instance
    print("\n--- Demonstrating Memory Persistence ---")
    print("Creating a new agent instance with the same user ID...")
    
    # Create a new agent with the same user ID but different config
    new_config = {
        "search_limit": 5,
        "search_threshold": 0.7,
        "rerank": True
    }
    new_agent = StoryAgent(use_mem0=True, user_id=user_id, mem0_config=new_config)
    
    # Search for memories with the new agent
    print("\nSearching for memories with new agent instance:")
    new_memories = new_agent.search_memories("marina investigation")
    print(f"Found {len(new_memories)} memories")
    for i, memory in enumerate(new_memories[:5], 1):
        print(f"{i}. {memory.get('memory', '')}")
    
    # Clean up memories
    print("\n--- Cleaning Up Memories ---")
    agent.clear_memories()
    print("Memories cleared.")
    
    print("\nExample completed successfully!")

if __name__ == "__main__":
    main()