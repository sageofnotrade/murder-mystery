"""
BoardAgent for the Murþrą application.
Handles board state updates and visual connections using web search and LLMs.
Enhanced with PydanticAI for better type safety and agent capabilities.
Uses ModelRouter to select appropriate models for different tasks:
- deepseek-r1t-chimera for reasoning/analysis
- mistral-nemo for writing/narrative

# Prompt/Model Strategy (2024-06-08):
# - System prompts are explicit, structured, and role-specific.
# - All LLM completions use ModelRouter:
#     - 'reasoning' (deepseek-r1t-chimera) for planning/analysis
#     - 'writing' (mistral-nemo) for board update generation
# - Parameters tuned: temperature=0.3 for planning, 0.7 for narrative; max_tokens set per step.
# - Prompts include context, player profile, and clear output format instructions.
# - Inline comments explain prompt structure and model routing choices.
"""

from .base_agent import BaseAgent
from .model_router import ModelRouter
from .models.psychological_profile import PsychologicalProfile, create_default_profile
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional, List, Union, Annotated
import requests
import os
import json
import time
from dotenv import load_dotenv

# Import PydanticAI components
from pydantic_ai import Agent as PydanticAgent, RunContext, ModelRetry
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.mistral import MistralModel
from pydantic_ai.messages import ModelMessage
# --- Pydantic Models ---

class BoardElement(BaseModel):
    """Model representing an element on the detective board."""
    model_config = ConfigDict(extra="ignore")

    id: str
    type: str  # "clue", "suspect", "location", "note", etc.
    title: str
    description: Optional[str] = None
    position: Dict[str, float] = Field(default_factory=dict)  # x, y coordinates
    properties: Dict[str, Any] = Field(default_factory=dict)  # Additional properties

class BoardConnection(BaseModel):
    """Model representing a connection between elements on the board."""
    model_config = ConfigDict(extra="ignore")

    id: str
    source_id: str  # ID of the source element
    target_id: str  # ID of the target element
    type: str  # "causal", "temporal", "spatial", etc.
    label: Optional[str] = None
    strength: float = 1.0  # Connection strength (0.0 to 1.0)
    properties: Dict[str, Any] = Field(default_factory=dict)  # Additional properties

class BoardState(BaseModel):
    """Model representing the complete state of the detective board."""
    model_config = ConfigDict(extra="ignore")

    elements: Dict[str, BoardElement] = Field(default_factory=dict)
    connections: Dict[str, BoardConnection] = Field(default_factory=dict)
    notes: Dict[str, str] = Field(default_factory=dict)
    layout: Dict[str, Any] = Field(default_factory=dict)
    last_update: Optional[str] = None

class BoardUpdateInput(BaseModel):
    """Input model for generating a board update."""
    model_config = ConfigDict(extra="ignore")

    prompt: str
    context: dict = Field(default_factory=dict)

class BoardUpdateOutput(BaseModel):
    """Output model for a generated board update."""
    model_config = ConfigDict(extra="ignore")

    board_state: dict
    sources: List[str] = Field(default_factory=list)

class BoardGenerateOutput(BaseModel):
    """Output model for generating a complete board."""
    model_config = ConfigDict(extra="ignore")

    board_state: BoardState
    sources: List[str] = Field(default_factory=list)

class BoardInteractionInput(BaseModel):
    """Input model for board interactions."""
    model_config = ConfigDict(extra="ignore")

    action: str
    player_profile: Optional[PsychologicalProfile] = Field(default_factory=create_default_profile)
    context: dict = Field(default_factory=dict)

# --- BoardAgent Dependencies ---

class BoardAgentDependencies:
    """Dependencies for the BoardAgent PydanticAI agent."""
    def __init__(self, memory=None, use_mem0=True, user_id=None, mem0_config=None):
        self.memory = memory
        self.use_mem0 = use_mem0
        self.user_id = user_id
        self.mem0_config = mem0_config or {}
        self.agent_name = "BoardAgent"

    def update_memory(self, key, value):
        """Update memory with key-value pair."""
        if self.use_mem0 and hasattr(self.memory, 'update'):
            self.memory.update(key, value)

    def search_memories(self, query, limit=3, threshold=0.7, rerank=True):
        """Search memories based on query."""
        if self.use_mem0 and hasattr(self.memory, 'search'):
            return self.memory.search(query, limit=limit, threshold=threshold, rerank=rerank)
        return []

# --- BoardAgent Implementation ---

class BoardAgent(BaseAgent):
    """Agent responsible for board state updates and visual connections."""
    def __init__(self, memory=None, use_mem0=True, user_id=None, mem0_config=None):
        super().__init__("BoardAgent", memory, use_mem0=use_mem0, user_id=user_id, mem0_config=mem0_config)

        # Initialize ModelRouter for intelligent model selection
        self.model_router = ModelRouter()

        # Initialize PydanticAI agent
        self.pydantic_agent = self._create_pydantic_agent()
        self.dependencies = BoardAgentDependencies(memory, use_mem0, user_id, mem0_config)

    def _create_pydantic_agent(self):
        """Create a PydanticAgent for board state generation"""
        agent = PydanticAgent(
            model="openai:gpt-3.5-turbo",  # Using a model that PydanticAI recognizes
            system_prompt="""You are an expert in managing game board states for mystery stories.
            Your task is to generate and update board states that reflect the current state of the investigation.
            Each board state should:
            - Track discovered clues and their locations
            - Monitor suspect interviews and their outcomes
            - Record player progress and available actions
            - Maintain consistency with the story's timeline
            - Provide clear status updates for the player""",
            allow_retries=True
        )
        return agent

    def generate_board(self, prompt: str, context: dict = None) -> BoardGenerateOutput:
        """
        Generate a complete detective board from scratch using Brave Search and an LLM.

        Args:
            prompt (str): The board generation prompt from the user.
            context (dict): Optional context for the board generation.

        Returns:
            BoardGenerateOutput: The generated board state and sources.
        """
        context = context or {}
        start_time = time.time()

        # Store the prompt in Mem0 for future reference
        if self.use_mem0:
            self.update_memory("board_generation_prompt", prompt)
            if context:
                self.update_memory("board_generation_context", str(context))

        # Try using PydanticAI agent first
        try:
            # Prepare the prompt for the agent
            agent_prompt = (
                f"Generate a complete detective board based on this prompt: {prompt}\n"
            )

            # Add any additional context
            if context:
                agent_prompt += "Additional context:\n"
                for key, value in context.items():
                    agent_prompt += f"- {key}: {value}\n"

            # Run the agent synchronously
            result = self.pydantic_agent.run_sync(
                agent_prompt,
                deps=self.dependencies,
                model_settings={"temperature": 0.7, "max_tokens": 1500}
            )

            # Track performance metrics if enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                generation_time = time.time() - start_time
                self.update_memory("last_board_generation_time", f"{generation_time:.2f} seconds")
                self.update_memory("last_board_generation_model_used", os.getenv("LLM_MODEL", "openai:gpt-4o"))

            return result

        except Exception as e:
            # Log the error
            error_msg = f"PydanticAI board generation error: {str(e)}"
            if self.use_mem0:
                self.update_memory("last_error", error_msg)

            # Fallback to traditional method
            search_results = self._brave_search(prompt)

            # Create a basic board state with elements from search results
            elements = {}
            connections = {}
            notes = {"auto_generated": "This board was generated using fallback method."}

            # Add some basic elements based on search results
            for i, result in enumerate(search_results):
                element_id = f"clue_{i+1}"
                elements[element_id] = {
                    "id": element_id,
                    "type": "clue",
                    "title": result.get("title", f"Clue {i+1}"),
                    "description": result.get("snippet", "No description available."),
                    "position": {"x": 100 + (i * 200), "y": 100},
                    "properties": {"source": result.get("url", "")}
                }

            # Create a board state
            board_state = BoardState(
                elements=elements,
                connections=connections,
                notes=notes,
                layout={"auto_layout": True},
                last_update=time.strftime("%Y-%m-%d %H:%M:%S")
            )

            # Track performance metrics if enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                generation_time = time.time() - start_time
                self.update_memory("last_board_generation_time", f"{generation_time:.2f} seconds")

            return BoardGenerateOutput(board_state=board_state, sources=[r['url'] for r in search_results])

    def generate_board_update(self, prompt: str, context: dict = None) -> BoardUpdateOutput:
        """
        Generate a board update using Brave Search and an LLM.

        Args:
            prompt (str): The board update prompt from the user.
            context (dict): Optional context for the board update.

        Returns:
            BoardUpdateOutput: The generated board update and sources.
        """
        context = context or {}
        start_time = time.time()

        # Store the prompt in Mem0 for future reference
        if self.use_mem0:
            self.update_memory("board_update_prompt", prompt)
            if context:
                self.update_memory("board_update_context", str(context))

        # Try using PydanticAI agent first
        try:
            # Prepare the prompt for the agent
            agent_prompt = (
                f"Generate a board update based on this prompt: {prompt}\n"
            )

            # Add any additional context
            if context:
                agent_prompt += "Additional context:\n"
                for key, value in context.items():
                    agent_prompt += f"- {key}: {value}\n"

            # Run the agent synchronously
            result = self.pydantic_agent.run_sync(
                agent_prompt,
                deps=self.dependencies,
                model_settings={"temperature": 0.7, "max_tokens": 1000}
            )

            # Track performance metrics if enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                generation_time = time.time() - start_time
                self.update_memory("last_board_update_generation_time", f"{generation_time:.2f} seconds")
                self.update_memory("last_board_update_model_used", os.getenv("LLM_MODEL", "openai:gpt-4o"))

            return result

        except Exception as e:
            # Log the error
            error_msg = f"PydanticAI board update error: {str(e)}"
            if self.use_mem0:
                self.update_memory("last_error", error_msg)

            # Fallback to traditional method
            search_results = self._brave_search(prompt)
            board_state = self._llm_generate_board_update(prompt, context, search_results)

            # Track performance metrics if enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                generation_time = time.time() - start_time
                self.update_memory("last_board_update_generation_time", f"{generation_time:.2f} seconds")

            return BoardUpdateOutput(board_state=board_state, sources=[r['url'] for r in search_results])

    def _brave_search(self, query: str) -> list[dict]:
        """
        Search the web using Brave Search API.

        Args:
            query (str): The search query.

        Returns:
            list[dict]: List of search results with title, url, and snippet.
        """
        # Get API key from environment or config
        load_dotenv()
        api_key = os.getenv("BRAVE_API_KEY")

        if not api_key:
            if self.use_mem0:
                self.update_memory("last_error", "Missing Brave API key")
            return []

        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {"Accept": "application/json", "X-Subscription-Token": api_key}
        params = {"q": query, "count": 3}

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=5)
            resp.raise_for_status()
            data = resp.json()

            results = [
                {"title": r["title"], "url": r["url"], "snippet": r.get("description", "")}
                for r in data.get("web", {}).get("results", [])
            ]

            # Store search results in memory if tracking is enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                self.update_memory("last_search_query", query)
                self.update_memory("last_search_results_count", str(len(results)))

            return results

        except Exception as e:
            if self.use_mem0:
                self.update_memory("last_error", f"Brave search error: {str(e)}")
            return []

    def synchronize_with_story(self, story_state: dict, board_state: dict = None) -> BoardUpdateOutput:
        """
        Synchronize the board with the current story state.

        Args:
            story_state (dict): The current story state.
            board_state (dict): The current board state (optional).

        Returns:
            BoardUpdateOutput: The updated board state and sources.
        """
        start_time = time.time()

        # Store the synchronization request in Mem0 for future reference
        if self.use_mem0:
            self.update_memory("board_sync_request", f"Synchronizing board with story at {time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Extract relevant information from the story state
        title = story_state.get("title", "Untitled Mystery")
        current_scene = story_state.get("current_scene", "unknown")
        discovered_clues = story_state.get("discovered_clues", [])
        suspect_states = story_state.get("suspect_states", {})

        # Create a prompt for the synchronization
        prompt = f"Synchronize detective board with story progress. Title: {title}, Scene: {current_scene}"

        # Create context with story state information
        context = {
            "title": title,
            "current_scene": current_scene,
            "discovered_clues": discovered_clues,
            "suspect_states": suspect_states,
            "current_board_state": board_state
        }

        # Try using PydanticAI agent first
        try:
            # Prepare the prompt for the agent
            agent_prompt = (
                f"Synchronize the detective board with the current story state:\n"
                f"- Title: {title}\n"
                f"- Current scene: {current_scene}\n"
                f"- Discovered clues: {', '.join(discovered_clues) if discovered_clues else 'None'}\n"
                f"- Suspects: {len(suspect_states)} total\n"
            )

            # Add current board state if available
            if board_state:
                agent_prompt += "\nCurrent board state is provided in the context.\n"
            else:
                agent_prompt += "\nNo current board state available. Create a new board.\n"

            # Run the agent synchronously
            result = self.pydantic_agent.run_sync(
                agent_prompt,
                deps=self.dependencies,
                model_settings={"temperature": 0.7, "max_tokens": 1000}
            )

            # Track performance metrics if enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                generation_time = time.time() - start_time
                self.update_memory("last_board_sync_time", f"{generation_time:.2f} seconds")
                self.update_memory("last_board_sync_model_used", os.getenv("LLM_MODEL", "openai:gpt-4o"))

            return result

        except Exception as e:
            # Log the error
            error_msg = f"PydanticAI board synchronization error: {str(e)}"
            if self.use_mem0:
                self.update_memory("last_error", error_msg)

            # Fallback to traditional method
            search_results = self._brave_search(f"detective investigation {title} {' '.join(discovered_clues[:3])}")
            board_update = self._llm_generate_board_update(prompt, context, search_results)

            # Track performance metrics if enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                generation_time = time.time() - start_time
                self.update_memory("last_board_sync_time", f"{generation_time:.2f} seconds")

            return BoardUpdateOutput(board_state=board_update, sources=[r['url'] for r in search_results])

    def _llm_generate_board_update(self, prompt: str, context: dict, search_results: list[dict]) -> dict:
        """
        Generate a board update using ModelRouter.
        Uses a two-step process:
        1. First, use deepseek-r1t-chimera to analyze the board and plan the update (reasoning)
        2. Then, use mistral-nemo to write the actual board update (writing)

        Args:
            prompt (str): The board update prompt.
            context (dict): Context for the board update.
            search_results (list[dict]): Search results to incorporate.

        Returns:
            dict: The generated board state update.
        """
        # Format search results for the prompt
        search_context = ""
        if search_results:
            search_context = "\n\nRelevant information:\n"
            for i, result in enumerate(search_results, 1):
                if result.get("snippet"):
                    search_context += f"{i}. {result['title']}: {result['snippet']}\n"

        # Format context for the prompt
        context_str = json.dumps(context, indent=2)

        try:
            # Step 1: Use reasoning model to analyze and plan the board update
            planning_system_prompt = (
                "You are a detective specializing in visual investigation boards. "
                "Analyze the given prompt and context to plan a board update. "
                "Focus on identifying key elements, connections, and patterns that should be represented on the board. "
                "Your analysis will be used to generate a visual board update."
            )

            planning_user_prompt = (
                f"Analyze this board update request and plan the changes needed:\n\n"
                f"Prompt: {prompt}\n\n"
                f"Context: {context_str}\n"
                f"{search_context}\n\n"
                "Provide a detailed plan for updating the board, including:\n"
                "1. Key elements that should be added or modified\n"
                "2. Important connections between elements\n"
                "3. Visual organization suggestions\n"
                "4. Any patterns or insights that should be highlighted"
            )

            # Create messages for the reasoning model
            planning_messages = [
                ModelMessage(role="system", content=planning_system_prompt),
                ModelMessage(role="user", content=planning_user_prompt)
            ]

            # Generate the board update plan using the reasoning model
            planning_response = self.model_router.complete(
                messages=planning_messages,
                task_type="reasoning",  # Use deepseek-r1t-chimera for analytical reasoning
                temperature=0.3,  # Lower temperature for planning
                max_tokens=800
            )

            # Store the planning response in memory for debugging if tracking is enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                self.update_memory("board_planning_response", str(planning_response.content)[:500])
                self.update_memory("board_planning_model", self.model_router.get_model_name_for_task("reasoning"))

            # Step 2: Use writing model to generate the actual board update
            writing_system_prompt = (
                "You are a detective specializing in visual investigation boards. "
                "Create and update detective boards that visually represent cases, evidence, suspects, and connections. "
                "Focus on clear visual organization, logical connections between elements, and highlighting key relationships. "
                "Your board updates should help investigators see patterns and connections they might otherwise miss."
            )

            writing_user_prompt = (
                f"Generate a board update based on this prompt: {prompt}\n\n"
                f"Context: {context_str}\n"
                f"{search_context}\n\n"
                f"Board update plan:\n{planning_response.content}\n\n"
                "Respond with a JSON object representing the board state update. "
                "Include 'update' (summary of changes), 'elements' (any new or modified board elements), "
                "'connections' (any new or modified connections), and 'notes' (any additional notes)."
            )

            # Create messages for the writing model
            writing_messages = [
                ModelMessage(role="system", content=writing_system_prompt),
                ModelMessage(role="user", content=writing_user_prompt)
            ]

            # Generate the board update using the writing model
            writing_response = self.model_router.complete(
                messages=writing_messages,
                task_type="writing",  # Use mistral-nemo for creative writing
                temperature=0.7,  # Higher temperature for creative writing
                max_tokens=1000
            )

            # Store the writing response in memory for debugging if tracking is enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                self.update_memory("board_writing_response", str(writing_response.content)[:500])
                self.update_memory("board_writing_model", self.model_router.get_model_name_for_task("writing"))

            # Extract the generated board update
            board_update_text = writing_response.content

            # Try to parse the response as JSON
            try:
                board_state = json.loads(board_update_text)
                if not isinstance(board_state, dict):
                    board_state = {"update": board_update_text}
            except json.JSONDecodeError:
                # If not valid JSON, create a simple board state
                board_state = {
                    "update": board_update_text,
                    "elements": {},
                    "connections": {},
                    "notes": {"auto_generated": "The model did not return valid JSON."}
                }

            # Ensure the board state has the required fields
            if "update" not in board_state:
                board_state["update"] = prompt or "No update provided."
            if "elements" not in board_state:
                board_state["elements"] = {}
            if "connections" not in board_state:
                board_state["connections"] = {}
            if "notes" not in board_state:
                board_state["notes"] = {}

            # Add context to the board state
            board_state["context"] = context

            return board_state

        except Exception as e:
            error_msg = f"LLM board update error: {str(e)}"
            if self.use_mem0:
                self.update_memory("last_error", error_msg)

            # Fallback to a simple board state if model call fails
            snippets = " ".join([r["snippet"] for r in search_results if r.get("snippet")])
            return {
                "update": prompt or "No update provided.",
                "details": snippets or "No details found.",
                "context": context,
                "elements": {},
                "connections": {},
                "notes": {"error": error_msg}
            }

    def _llm_generate_board_response(self, action: str, context: dict) -> str:
        """Generate a board response that matches the player's social style."""
        # Get psychological adaptations
        player_profile = context.get("player_profile", create_default_profile())
        adaptations = player_profile.get_narrative_adaptations()
        
        # Create prompt with psychological adaptations
        prompt = f"""
        Generate a board response based on:
        
        Action: {action}
        
        Psychological Adaptations:
        {json.dumps(adaptations, indent=2)}
        
        Requirements:
        1. Adapt interaction style based on player's social style
        2. For direct players: Provide clear, straightforward responses
        3. For indirect players: Use more subtle, nuanced responses
        4. Match the pace of interaction to player's social style
        5. Maintain game flow and engagement
        """
        
        # Use the model router to select appropriate model
        model = self.model_router.get_model_for_task("board_interaction")
        
        try:
            response = model.generate(prompt)
            return response.strip()
        except Exception as e:
            print(f"Error generating board response: {str(e)}")
            return f"You {action}."

# --- Inline Tests ---
import unittest

class BoardAgentTest(unittest.TestCase):
    def setUp(self):
        self.agent = BoardAgent(use_mem0=False)  # Disable Mem0 for testing
        # Mock the PydanticAI agent to avoid actual API calls
        self.agent.pydantic_agent = None

    def test_expected(self):
        result = self.agent.generate_board_update("Connect clue to suspect", {})
        self.assertIn("update", result.board_state)
        self.assertIn("elements", result.board_state)
        self.assertIn("connections", result.board_state)

    def test_edge_empty_prompt(self):
        result = self.agent.generate_board_update("", {})
        self.assertTrue(isinstance(result.board_state, dict))
        self.assertIn("update", result.board_state)

    def test_failure_brave_down(self):
        # Store original method
        original_search = self.agent._brave_search
        # Replace with failing method
        self.agent._brave_search = lambda _: []  # Use underscore to indicate unused parameter
        try:
            result = self.agent.generate_board_update("Link evidence", {})
            self.assertIn("update", result.board_state)
            self.assertIn("elements", result.board_state)
            self.assertIn("connections", result.board_state)
        finally:
            # Restore original method
            self.agent._brave_search = original_search

    def test_with_context(self):
        context = {
            "case_title": "The Missing Artifact",
            "discovered_clues": ["fingerprint", "broken glass"]
        }
        result = self.agent.generate_board_update("Add new suspect connection", context)
        self.assertIn("context", result.board_state)
        self.assertEqual(result.board_state["context"], context)

    def test_generate_board(self):
        result = self.agent.generate_board("Create a board for the museum theft case")
        self.assertIsInstance(result, BoardGenerateOutput)
        self.assertIsInstance(result.board_state, BoardState)
        self.assertIsInstance(result.board_state.elements, dict)
        self.assertIsInstance(result.board_state.connections, dict)
        self.assertIsInstance(result.sources, list)

    def test_synchronize_with_story(self):
        # Create a mock story state
        story_state = {
            "title": "The Missing Artifact",
            "current_scene": "museum",
            "discovered_clues": ["fingerprint", "broken glass", "muddy footprint"],
            "suspect_states": {
                "suspect1": {"name": "Professor Smith", "interviewed": True, "suspicious_level": 3},
                "suspect2": {"name": "Security Guard", "interviewed": False, "suspicious_level": 1}
            }
        }

        # Create a mock board state
        board_state = {
            "elements": {
                "clue_1": {"id": "clue_1", "type": "clue", "title": "Fingerprint"}
            },
            "connections": {},
            "notes": {}
        }

        # Test synchronization with existing board state
        result = self.agent.synchronize_with_story(story_state, board_state)
        self.assertIsInstance(result, BoardUpdateOutput)
        self.assertIn("update", result.board_state)

        # Test synchronization without existing board state
        result = self.agent.synchronize_with_story(story_state)
        self.assertIsInstance(result, BoardUpdateOutput)
        self.assertIn("update", result.board_state)