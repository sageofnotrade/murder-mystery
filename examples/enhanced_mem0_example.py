"""
Enhanced Mem0 Integration Example for StoryAgent.

This script demonstrates the improved Mem0 integration in StoryAgent,
showcasing the enhanced memory capabilities and configuration options.

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
    user_id = f"example_user_{os.urandom(4).hex()}"
    print(f"Using user ID: {user_id}")
    
    # Custom Mem0 configuration
    mem0_config = {
        "search_limit": 7,           # Retrieve more memories
        "search_threshold": 0.6,     # Lower threshold for more results
        "rerank": True,              # Use reranking for better relevance
        "store_summaries": True,     # Store summaries of generated content
        "track_performance": True    # Track performance metrics
    }
    
    # Create a StoryAgent with enhanced Mem0 configuration
    agent = StoryAgent(use_mem0=True, user_id=user_id, mem0_config=mem0_config)
    print("\n--- Agent Initialized with Enhanced Mem0 Configuration ---")
    
    # Step 1: Store some initial memories with more context
    print("\n--- Storing Initial Memories with Enhanced Context ---")
    agent.update_memory("detective_trait", "The detective has a fear of water due to a childhood incident where they nearly drowned.")
    agent.update_memory("location", "The mystery takes place in a small coastal town called Harborview, known for its foggy mornings and secretive residents.")
    agent.update_memory("victim", "The victim is the town's wealthy marina owner, found drowned in suspicious circumstances with strange marks on their wrists.")
    agent.update_memory("suspect_1", "The harbormaster who had a long-standing dispute with the victim over property rights.")
    agent.update_memory("suspect_2", "The victim's business partner who stands to inherit the marina and was seen arguing with the victim the night before.")
    
    # Step 2: Generate a story with memory enhancement
    print("\n--- Generating Story with Memory Enhancement ---")
    story_result = agent.generate_story(
        "A detective investigating a suspicious drowning at a marina", 
        {"player_role": "detective", "setting": "coastal town", "time": "foggy morning"}
    )
    
    print("\nGenerated Story:")
    print(story_result.story[:300] + "..." if len(story_result.story) > 300 else story_result.story)
    print(f"\nSources: {', '.join(story_result.sources[:3])}")
    
    # Step 3: Search for memories with different parameters
    print("\n--- Searching Memories with Different Parameters ---")
    
    # Standard search
    standard_results = agent.search_memories("drowning marina")
    print(f"\nStandard Search Results (Default Parameters): {len(standard_results)} found")
    for i, result in enumerate(standard_results[:3], 1):
        print(f"{i}. {result.get('memory', '')} (relevance: {result.get('relevance', 0):.2f})")
    
    # Search with custom parameters
    custom_results = agent.search_memories("detective investigation", limit=3, threshold=0.5)
    print(f"\nCustom Search Results (limit=3, threshold=0.5): {len(custom_results)} found")
    for i, result in enumerate(custom_results[:3], 1):
        print(f"{i}. {result.get('memory', '')} (relevance: {result.get('relevance', 0):.2f})")
    
    # Step 4: Process a player action with memory context
    print("\n--- Processing Player Action with Memory Context ---")
    
    # Create a simple story state for the example
    from backend.agents.story_agent import StoryState, SuspectState, PlayerProfile
    
    story_state = StoryState(
        template_id="example_template",
        title="The Marina Mystery",
        current_scene="investigation",
        narrative_history=["You arrived at Harborview early in the morning, the fog rolling in from the sea."],
        discovered_clues=["Victim's appointment book"],
        suspect_states={
            "harbormaster": SuspectState(name="Captain Jenkins", interviewed=False, suspicious_level=2),
            "business_partner": SuspectState(name="Eleanor Wells", interviewed=False, suspicious_level=3)
        }
    )
    
    player_profile = PlayerProfile(
        psychological_traits={"analytical": "high", "empathetic": "medium"},
        preferences={"gore": "low", "supernatural": "none"},
        role="detective"
    )
    
    # Process the action
    action_result = agent.process({
        "action": "I want to interview Eleanor Wells about her business relationship with the victim",
        "story_state": story_state.model_dump(),
        "player_profile": player_profile.model_dump()
    })
    
    print("\nAction Result:")
    print(action_result["narrative"][:300] + "..." if len(action_result["narrative"]) > 300 else action_result["narrative"])
    
    # Step 5: Demonstrate memory persistence and enhanced retrieval
    print("\n--- Demonstrating Enhanced Memory Retrieval ---")
    
    # Search for memories related to the business partner
    business_partner_memories = agent.search_memories("Eleanor Wells business partner")
    print("\nMemories Related to Business Partner:")
    for i, memory in enumerate(business_partner_memories, 1):
        print(f"{i}. {memory.get('memory', '')}")
    
    # Search for memories related to the detective's traits
    detective_memories = agent.search_memories("detective traits")
    print("\nMemories Related to Detective Traits:")
    for i, memory in enumerate(detective_memories, 1):
        print(f"{i}. {memory.get('memory', '')}")
    
    # Step 6: Check performance tracking
    print("\n--- Memory Performance Tracking ---")
    performance_memories = agent.search_memories("memory_search")
    print("\nMemory Search Performance Records:")
    for i, memory in enumerate(performance_memories[:5], 1):
        print(f"{i}. {memory.get('memory', '')}")
    
    print("\nExample completed successfully!")

if __name__ == "__main__":
    main()