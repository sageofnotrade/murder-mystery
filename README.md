# murder-mystery
A personalized, AI-driven detective experience that adapts to the player's psychology and decisions, blending narrative storytelling with a visual investigation interface.

## StoryAgent: Web-Enhanced Story Generation with Advanced Memory

The `StoryAgent` now supports generating stories using real-world information via the Brave Search API and LLMs (Deepseek/Mistral), enhanced with Mem0 for persistent memory and advanced configuration options.

### Basic Usage

```python
from backend.agents.story_agent import StoryAgent

# Create a StoryAgent with Mem0 enabled
agent = StoryAgent(use_mem0=True, user_id="player123")

# Generate a story with memory enhancement
result = agent.generate_story("A detective in Paris", context={})
print(result.story)
```

### Advanced Memory Configuration

```python
from backend.agents.story_agent import StoryAgent

# Custom Mem0 configuration
mem0_config = {
    "search_limit": 7,           # Number of memories to retrieve
    "search_threshold": 0.6,     # Relevance threshold (0.0 to 1.0)
    "rerank": True,             # Use reranking for better relevance
    "store_summaries": True,    # Store summaries of generated content
    "track_performance": True,   # Track performance metrics
    "version": "v2"             # Mem0 API version
}

# Create agent with custom configuration
agent = StoryAgent(use_mem0=True, user_id="player123", mem0_config=mem0_config)

# Generate a story with enhanced memory capabilities
result = agent.generate_story("A detective investigating a murder at the harbor", {
    "player_role": "detective",
    "setting": "coastal town",
    "time": "foggy morning"
})
print(result.story)
```

### Memory Search and Retrieval

```python
# Search for memories with custom parameters
memories = agent.search_memories(
    query="detective harbor investigation",
    limit=5,                # Number of memories to retrieve
    threshold=0.7,          # Relevance threshold (0.0 to 1.0)
    rerank=True             # Use reranking for better relevance
)

# Process and use the memories
for memory in memories:
    print(memory.get("memory", ""))
```

See the `docs/mem0_integration.md` file for detailed documentation on the Mem0 integration.