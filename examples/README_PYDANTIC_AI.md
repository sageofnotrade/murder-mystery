# Using PydanticAI with StoryAgent

This document explains how to use PydanticAI with the StoryAgent in the Murder Mystery project.

## What is PydanticAI?

PydanticAI is a Python agent framework designed to make it easier to build production-grade applications with Generative AI. It provides:

- Integration with various LLM providers (OpenAI, Anthropic, Gemini, Mistral, etc.)
- Type-safe agent development with Pydantic models
- Function tools for agents to use
- Structured output validation
- Streaming capabilities
- Advanced error handling and retry mechanisms

## Installation

To use PydanticAI with the StoryAgent, you need to install the required dependencies:

```bash
pip install -r requirements.txt
```

## How It Works

The StoryAgent has been enhanced with PydanticAI to provide better type safety, error handling, and performance. The integration works at multiple levels:

### 1. High-Level Agent Integration

- The StoryAgent creates a PydanticAI agent during initialization
- The agent is configured with tools that map to the StoryAgent's methods
- When processing user actions or generating stories, the StoryAgent tries to use the PydanticAI agent first
- If the PydanticAI agent fails for any reason, the StoryAgent falls back to its traditional methods

### 2. Direct Model Integration

- The `_llm_generate_story` and `_llm_generate_narrative` methods use PydanticAI's model interfaces directly
- This allows for easy switching between different LLM providers (OpenAI, Anthropic, Mistral)
- The code automatically selects the appropriate model based on the `LLM_MODEL` environment variable

### 3. Specialized Agents for Specific Tasks

- The `_extract_potential_clue` method uses a specialized PydanticAI agent for clue extraction
- This agent is configured with a specific output type (ClueExtraction) for structured results
- It provides confidence scores and reasoning for extracted clues

### 4. Common Tools Integration

- The `_brave_search` method attempts to use PydanticAI's common tools for web search
- If available, it uses the BraveSearch tool from PydanticAI
- Otherwise, it falls back to direct API calls

## Example Usage

See the `pydantic_ai_story_agent_example.py` file for a complete example of using the PydanticAI-enhanced StoryAgent.

```python
from backend.agents.story_agent import StoryAgent

# Create a StoryAgent instance
agent = StoryAgent(use_mem0=True, user_id="example_user")

# Generate a story
story_result = agent.generate_story(
    "A valuable ancient artifact has disappeared from the museum.",
    {"player_role": "detective", "setting": "modern museum"}
)

print(story_result.story)
```

## Environment Variables

The StoryAgent with PydanticAI uses the following environment variables:

- `LLM_MODEL`: The model to use (e.g., "openai:gpt-4o", "anthropic:claude-3-5-sonnet-latest", "mistral:mistral-medium")
- `OPENAI_API_KEY`: API key for OpenAI models
- `ANTHROPIC_API_KEY`: API key for Anthropic models
- `MISTRAL_API_KEY`: API key for Mistral models
- `BRAVE_API_KEY`: API key for Brave Search
- `OPENROUTER_API_KEY` or `TOGETHER_API_KEY`: Alternative API keys for the fallback methods

## Model Selection

The StoryAgent supports multiple LLM providers through PydanticAI. You can specify which model to use by setting the `LLM_MODEL` environment variable with the following format:

```
provider:model_name
```

For example:
- `openai:gpt-4o` - Uses OpenAI's GPT-4o model
- `anthropic:claude-3-5-sonnet-latest` - Uses Anthropic's Claude 3.5 Sonnet model
- `mistral:mistral-medium` - Uses Mistral's Medium model

The code will automatically select the appropriate model interface based on this prefix.

## Benefits of Using PydanticAI

1. **Type Safety**: Better type checking and validation through Pydantic models
2. **Error Handling**: Improved error handling with built-in retry mechanisms
3. **Flexibility**: Seamless support for multiple LLM providers with a unified interface
4. **Performance**: Potential performance improvements through optimized API calls
5. **Maintainability**: Cleaner code structure with separation of concerns
6. **Structured Output**: Guaranteed output formats through Pydantic validation
7. **Advanced Features**: Access to streaming, conversation history, and more

## Troubleshooting

If you encounter issues with PydanticAI:

1. Check that all required environment variables are set
2. Ensure you have the correct versions of dependencies installed
3. Look for error messages in the logs (the StoryAgent stores errors in memory if Mem0 is enabled)
4. Try using the traditional methods by forcing an exception in the PydanticAI code path

## Advanced Usage

### Streaming Responses

PydanticAI supports streaming responses, which can be useful for real-time UI updates:

```python
async def stream_story():
    agent = StoryAgent(use_mem0=True)

    # Create a streaming agent run
    async with agent.pydantic_agent.run_stream(
        "Generate a detective story about a missing diamond",
        deps=agent.dependencies
    ) as response:
        async for chunk in response.iter_text():
            print(chunk, end="", flush=True)  # Stream to console or UI
```

### Custom Model Settings

You can customize model behavior by passing settings:

```python
result = agent.generate_story(
    "A murder in a locked room",
    {"player_role": "detective"},
    model_settings={
        "temperature": 0.9,  # Higher creativity
        "max_tokens": 2000,  # Longer story
        "top_p": 0.95
    }
)
```

### Using Different Models for Different Tasks

The StoryAgent is designed to use different models for different tasks:

- Story generation: Typically uses larger models like GPT-4 or Claude
- Narrative progression: Can use medium-sized models like Mistral Medium
- Clue extraction: Uses more precise models with lower temperature

You can customize this behavior by modifying the environment variables or the code directly.
