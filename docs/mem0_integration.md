# Mem0 Integration for Murþrą

This document describes how Mem0 is integrated into the Murþrą application for persistent memory across sessions.

## Overview

Mem0 provides a semantic memory system that allows agents to store and retrieve memories based on relevance. In Murþrą, we use Mem0 to:

1. Store narrative events and player actions
2. Remember character traits and preferences
3. Track discovered clues and evidence
4. Maintain continuity across game sessions
5. Enhance story generation with past context

## Setup

To use Mem0 in your development environment:

1. Sign up for a Mem0 account at [mem0.ai](https://mem0.ai)
2. Get your API key from the Mem0 dashboard
3. Add the API key to your `.env` file:
   ```
   MEM0_API_KEY=your-api-key-here
   ```
4. Install the Mem0 Python package:
   ```bash
   pip install mem0
   ```

## Usage in Agents

### BaseAgent

The `BaseAgent` class provides the foundation for Mem0 integration:

```python
from backend.agents.base_agent import BaseAgent

# Create an agent with Mem0 enabled
agent = BaseAgent("AgentName", use_mem0=True, user_id="player123")

# Store a memory
agent.update_memory("key", "value")

# Retrieve a memory
value = agent.get_memory("key")

# Search for relevant memories
memories = agent.search_memories("search query", limit=5, threshold=0.7)

# Clear all memories for the current user
success = agent.clear_memories()
```

### StoryAgent

The `StoryAgent` extends the Mem0 functionality with semantic search:

```python
from backend.agents.story_agent import StoryAgent

# Create a StoryAgent with Mem0 enabled
agent = StoryAgent(use_mem0=True, user_id="player123")

# Generate a story with memory enhancement
result = agent.generate_story("A detective in Paris", context={})
print(result.story)

# Clear all memories for the current user
success = agent.clear_memories()
```

### Custom Configuration

Both `BaseAgent` and `StoryAgent` support custom Mem0 configuration:

```python
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
```

### Memory Retrieval

Memories are retrieved using semantic search based on relevance to the current context, with support for reranking and configurable parameters:

```python
# Search for memories related to the current context
memories = agent.search_memories(
    query="detective investigating harbor",
    limit=5,                # Override config setting
    threshold=0.7,          # Override config setting
    rerank=True             # Override config setting
)
```

### Memory Integration in Story Generation

When generating stories or processing player actions, relevant memories are incorporated into the context:

1. Search for relevant memories based on the current context
2. Format the memories as additional context for the LLM
3. Generate the story or process the action with the enhanced context
4. Store the generated content as a new memory

## Database Integration

The Supabase database schema includes fields for storing Mem0 identifiers:

- `profiles.mem0_user_id`: Stores the Mem0 user ID for each player
- `stories.mem0_run_id`: Stores the Mem0 run ID for each story session

These fields enable consistent memory retrieval across sessions and devices.

## Memory Management

The Mem0 integration includes memory management features:

### Clearing Memories

Both `BaseAgent` and `StoryAgent` provide a `clear_memories()` method to delete all memories for the current user:

```python
# Clear all memories for the current user
success = agent.clear_memories()

# Check if clearing was successful
if success:
    print("All memories cleared successfully")
else:
    print("Failed to clear memories")
```

This is useful for:
- Starting fresh with a new story
- Removing outdated or irrelevant memories
- Testing and debugging
- Respecting user privacy by allowing data deletion

### Performance Tracking

The Mem0 integration includes performance tracking features:

- Generation time tracking
- Memory usage statistics
- Search relevance metrics
- Error logging

These metrics are stored as memories and can be retrieved for analysis:

```python
# Get performance metrics
generation_time = agent.get_memory("last_story_generation_time")
memory_count = agent.get_memory("last_memory_search_count")
```

## Examples

See the example files for complete demonstrations of using Mem0 with the StoryAgent:

- `examples/mem0_integration_example.py`: Basic usage example
- `examples/advanced_mem0_example.py`: Advanced configuration and usage

## Troubleshooting

- **API Key Issues**: Ensure your Mem0 API key is correctly set in the `.env` file
- **Connection Errors**: Check your internet connection and Mem0 service status
- **Memory Not Found**: Verify the user ID is consistent across sessions
- **Search Returns No Results**: Try lowering the threshold value (e.g., from 0.7 to 0.5)

## References

- [Mem0 Documentation](https://docs.mem0.ai)
- [Mem0 Python SDK](https://github.com/mem0ai/mem0-python)
- [Mem0 API Reference](https://docs.mem0.ai/api-reference)