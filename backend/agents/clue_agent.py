"""
ClueAgent for the Murþrą application.
Handles clue generation and updates using web search and LLMs.
Enhanced with PydanticAI for better type safety and agent capabilities.
Uses ModelRouter to select appropriate models for different tasks:
- deepseek-rit-chimera for reasoning/analysis
- mistral-nemo for writing/narrative
"""

from .base_agent import BaseAgent
from .model_router import ModelRouter
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

# --- Pydantic Models ---

class ClueInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    prompt: str
    context: dict = Field(default_factory=dict)

class ClueData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    description: str
    details: str
    significance: Optional[str] = None
    related_to: Optional[List[str]] = Field(default_factory=list)
    confidence: Optional[float] = None

class ClueOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    clue: Dict[str, Any]
    sources: List[str] = Field(default_factory=list)

class ClueGenerateInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    prompt: str
    context: dict = Field(default_factory=dict)

class ClueGenerateOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    clue: ClueData
    sources: List[str] = Field(default_factory=list)

# --- ClueAgent Dependencies ---

class ClueAgentDependencies:
    """Dependencies for the ClueAgent PydanticAI agent."""
    def __init__(self, memory=None, use_mem0=True, user_id=None, mem0_config=None):
        self.memory = memory
        self.use_mem0 = use_mem0
        self.user_id = user_id
        self.mem0_config = mem0_config or {}
        self.agent_name = "ClueAgent"

    def update_memory(self, key, value):
        """Update memory with key-value pair."""
        if self.use_mem0 and hasattr(self.memory, 'update'):
            self.memory.update(key, value)

    def search_memories(self, query, limit=3, threshold=0.7, rerank=True):
        """Search memories based on query."""
        if self.use_mem0 and hasattr(self.memory, 'search'):
            return self.memory.search(query, limit=limit, threshold=threshold, rerank=rerank)
        return []

# --- ClueAgent Implementation ---

class ClueAgent(BaseAgent):
    """Agent responsible for clue generation and updates."""
    def __init__(self, memory=None, use_mem0=True, user_id=None, mem0_config=None):
        super().__init__("ClueAgent", memory, use_mem0=use_mem0, user_id=user_id, mem0_config=mem0_config)

        # Initialize ModelRouter for intelligent model selection
        self.model_router = ModelRouter()

        # Initialize PydanticAI agent
        self.pydantic_agent = self._create_pydantic_agent()
        self.dependencies = ClueAgentDependencies(memory, use_mem0, user_id, mem0_config)

    def _create_pydantic_agent(self):
        """Create and configure the PydanticAI agent."""
        # Determine which model to use based on environment variables
        model_name = os.getenv("LLM_MODEL", "openai:gpt-4o")

        # Create the agent with appropriate system prompt
        agent = PydanticAgent(
            model_name,
            deps_type=ClueAgentDependencies,
            output_type=Union[ClueOutput, ClueGenerateOutput],
            system_prompt=(
                "You are a forensic expert helping with a detective investigation. "
                "Create detailed descriptions of clues based on given prompts. "
                "Include physical characteristics, potential significance, and possible connections to the case. "
                "Be precise, analytical, and consider all possible interpretations of the evidence."
            ),
            retries=2  # Allow retries for better error handling
        )

        # Register tools for the agent
        @agent.tool
        async def brave_search(ctx: RunContext[ClueAgentDependencies], query: str) -> list[dict]:
            """Search the web for information related to the query."""
            return self._brave_search(query)

        @agent.tool
        async def generate_clue_data(
            ctx: RunContext[ClueAgentDependencies],
            prompt: str,
            context: dict = None,
            search_results: list[dict] = None,
            memory_context: str = ""
        ) -> ClueData:
            """Generate a detailed clue based on the prompt and context."""
            search_results = search_results or self._brave_search(prompt)
            return self._llm_generate_clue_data(prompt, context or {}, search_results, memory_context)

        @agent.tool
        async def search_memories(
            ctx: RunContext[ClueAgentDependencies],
            query: str,
            limit: int = 3,
            threshold: float = 0.7,
            rerank: bool = True
        ) -> list[dict]:
            """Search memories based on the query."""
            if ctx.deps.use_mem0:
                return ctx.deps.search_memories(query, limit, threshold, rerank)
            return []

        @agent.tool
        async def update_memory(
            ctx: RunContext[ClueAgentDependencies],
            key: str,
            value: str
        ) -> None:
            """Update memory with key-value pair."""
            if ctx.deps.use_mem0:
                ctx.deps.update_memory(key, value)

        return agent

    def generate_clue(self, prompt: str, context: dict = None) -> ClueOutput:
        """
        Generate a clue using web search and LLM.

        Args:
            prompt (str): Description of the clue to analyze.
            context (dict): Optional context for the clue generation.

        Returns:
            ClueOutput: The generated clue and sources.
        """
        context = context or {}
        start_time = time.time()

        # Store the prompt in Mem0 for future reference
        if self.use_mem0:
            self.update_memory("clue_prompt", prompt)
            if context:
                self.update_memory("clue_context", str(context))

        # Try using PydanticAI agent first
        try:
            # Prepare the prompt for the agent
            agent_prompt = (
                f"Generate a detailed analysis for this clue: {prompt}\n"
            )

            # Add any additional context
            if context:
                agent_prompt += "Case context:\n"
                for key, value in context.items():
                    agent_prompt += f"- {key}: {value}\n"

            # Run the agent synchronously
            result = self.pydantic_agent.run_sync(
                agent_prompt,
                deps=self.dependencies,
                model_settings={"temperature": 0.7, "max_tokens": 800}
            )

            # Extract the clue from the result
            if hasattr(result.output, 'clue'):
                # If we got a ClueGenerateOutput
                if isinstance(result.output, ClueGenerateOutput):
                    clue_data = result.output.clue
                    sources = result.output.sources

                    # Convert to dictionary format for backward compatibility
                    clue_dict = {
                        "description": clue_data.description,
                        "details": clue_data.details,
                        "context": context
                    }

                    # Add optional fields if present
                    if clue_data.significance:
                        clue_dict["significance"] = clue_data.significance
                    if clue_data.related_to:
                        clue_dict["related_to"] = clue_data.related_to
                    if clue_data.confidence:
                        clue_dict["confidence"] = clue_data.confidence

                    # Store the generated clue in Mem0
                    if self.use_mem0 and self.mem0_config.get("store_summaries", True):
                        self.update_memory("generated_clue", clue_data.description)

                    return ClueOutput(clue=clue_dict, sources=sources)

                # If we got a ClueOutput directly
                elif isinstance(result.output, ClueOutput):
                    # Store the generated clue in Mem0
                    if self.use_mem0 and self.mem0_config.get("store_summaries", True):
                        self.update_memory("generated_clue", str(result.output.clue.get("description", "")))

                    return result.output

        except Exception as e:
            error_msg = f"PydanticAI clue agent error: {str(e)}"
            if self.use_mem0:
                self.update_memory("last_error", error_msg)

        # Fallback to traditional method if PydanticAI fails
        search_results = self._brave_search(prompt)
        clue = self._llm_generate_clue(prompt, context, search_results)

        # Track performance metrics if enabled
        if self.use_mem0 and self.mem0_config.get("track_performance", True):
            generation_time = time.time() - start_time
            self.update_memory("last_clue_generation_time", f"{generation_time:.2f} seconds")

        return ClueOutput(clue=clue, sources=[r['url'] for r in search_results])

    def _brave_search(self, query: str) -> list[dict]:
        # Get API key from environment or config
        import os
        from dotenv import load_dotenv

        load_dotenv()
        api_key = os.getenv("BRAVE_API_KEY")

        if not api_key:
            self.update_memory("last_error", "Missing Brave API key")
            return []

        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {"Accept": "application/json", "X-Subscription-Token": api_key}
        params = {"q": query, "count": 5, "freshness": "month"}

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            # Store the full response in memory for debugging
            self.update_memory("last_search_response", data)

            results = [
                {
                    "title": r["title"],
                    "url": r["url"],
                    "snippet": r.get("description", ""),
                    "source": r.get("source", "")
                }
                for r in data.get("web", {}).get("results", [])
            ]

            # Log the number of results found
            self.update_memory("last_search_count", len(results))
            return results

        except requests.RequestException as e:
            self.update_memory("last_error", f"Brave Search API error: {str(e)}")
            return []

    def _llm_generate_clue_data(self, prompt: str, context: dict, search_results: list[dict], memory_context: str = "") -> ClueData:
        """
        Generate a clue using the ModelRouter.
        Uses deepseek-rit-chimera for analytical reasoning about clues.

        Args:
            prompt (str): Description of the clue to analyze.
            context (dict): Context for the clue generation.
            search_results (list[dict]): Search results to enhance the clue generation.
            memory_context (str): Optional context from memory.

        Returns:
            ClueData: The generated clue data.
        """
        from pydantic_ai.messages import Message

        load_dotenv()

        # Format search results for the prompt
        search_context = ""
        if search_results:
            search_context = "\n\nRelevant information:\n"
            for i, result in enumerate(search_results, 1):
                if result.get("snippet"):
                    search_context += f"{i}. {result['title']}: {result['snippet']}\n"

        try:
            # Build system prompt
            system_prompt = (
                "You are a forensic expert helping with a detective investigation. "
                "Create a detailed description of the clue based on the given prompt. "
                "Include physical characteristics, potential significance, and possible connections to the case. "
                "Be precise, analytical, and consider all possible interpretations of the evidence."
            )

            # Build user prompt
            user_prompt = f"Analyze this clue: {prompt}\n"

            # Add context if provided
            if context:
                user_prompt += "\nCase context:\n"
                for key, value in context.items():
                    user_prompt += f"- {key}: {value}\n"

            # Add search results
            user_prompt += search_context

            # Add memory context if provided
            if memory_context:
                user_prompt += f"\n{memory_context}\n"

            # Prepare messages for the model
            messages = [
                Message(role="system", content=system_prompt),
                Message(role="user", content=user_prompt)
            ]

            # Generate the clue using the reasoning model via ModelRouter
            response = self.model_router.complete(
                messages=messages,
                task_type="reasoning",  # Use deepseek-rit-chimera for analytical reasoning
                temperature=0.7,
                max_tokens=800
            )

            # Store the response in memory for debugging if tracking is enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                self.update_memory("last_llm_response", str(response)[:500])
                self.update_memory("clue_analysis_model", self.model_router.get_model_name_for_task("reasoning"))

            # Extract the generated clue
            content = response.content

            if not content:
                if self.use_mem0:
                    self.update_memory("last_error", "Empty response from LLM")
                return ClueData(
                    description=prompt or "Unknown Clue",
                    details="Analysis pending."
                )

            # Try to parse structured data from the response
            try:
                # Look for JSON-like content in the response
                if "{" in content and "}" in content:
                    json_str = content[content.find("{"):content.rfind("}")+1]
                    clue_dict = json.loads(json_str)

                    # Create a ClueData object from the parsed JSON
                    return ClueData(
                        description=clue_dict.get("description", prompt),
                        details=clue_dict.get("details", content),
                        significance=clue_dict.get("significance"),
                        related_to=clue_dict.get("related_to", []),
                        confidence=clue_dict.get("confidence")
                    )
            except json.JSONDecodeError:
                # If JSON parsing fails, use the raw content
                pass

            # Extract key information from the text response
            lines = content.split('\n')
            description = prompt
            details = content

            # Try to find a description in the first few lines
            for line in lines[:3]:
                if len(line) > 10 and len(line) < 100:
                    description = line
                    break

            return ClueData(
                description=description,
                details=details
            )

        except Exception as e:
            error_msg = f"PydanticAI clue model error: {str(e)}"
            if self.use_mem0:
                self.update_memory("last_error", error_msg)

            # Fallback to a simple clue if model call fails
            return ClueData(
                description=prompt or "Unknown Clue",
                details="Unable to analyze this clue at the moment."
            )

    def _llm_generate_clue(self, prompt: str, context: dict, search_results: list[dict]) -> dict:
        """
        Generate a clue using the ModelRouter.
        Uses deepseek-rit-chimera for analytical reasoning about clues.
        Legacy method for backward compatibility.
        """
        import json
        from pydantic_ai.messages import Message

        # Format search results for the prompt
        search_context = ""
        if search_results:
            search_context = "\n\nRelevant information:\n"
            for i, result in enumerate(search_results, 1):
                if result.get("snippet"):
                    search_context += f"{i}. {result['title']}: {result['snippet']}\n"

        # Build system prompt
        system_prompt = (
            "You are a forensic expert helping with a detective investigation. "
            "Create a detailed description of the clue based on the given prompt. "
            "Include physical characteristics, potential significance, and possible connections to the case. "
            "Format your response as a JSON object with 'description' (brief summary) and 'details' (comprehensive analysis) fields."
        )

        # Build user prompt
        user_prompt = f"Analyze this clue: {prompt}\n"

        # Add context if provided
        if context:
            user_prompt += "\nCase context:\n"
            for key, value in context.items():
                user_prompt += f"- {key}: {value}\n"

        # Add search results
        user_prompt += search_context

        # Prepare messages for the model
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt)
        ]

        try:
            # Generate the clue using the reasoning model via ModelRouter
            response = self.model_router.complete(
                messages=messages,
                task_type="reasoning",  # Use deepseek-rit-chimera for analytical reasoning
                temperature=0.7,
                max_tokens=800
            )

            # Store the response in memory for debugging if tracking is enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                self.update_memory("last_llm_response", str(response)[:500])
                self.update_memory("clue_generation_model", self.model_router.get_model_name_for_task("reasoning"))

            # Extract the generated clue
            content = response.content

            if not content:
                self.update_memory("last_error", "Empty response from LLM")
                return {
                    "description": prompt or "Unknown Clue",
                    "details": "Analysis pending.",
                    "context": context
                }

            # Try to parse JSON from the response
            try:
                # Look for JSON-like content in the response
                if "{" in content and "}" in content:
                    json_str = content[content.find("{"):content.rfind("}")+1]
                    clue_data = json.loads(json_str)
                    # Ensure required fields exist
                    if "description" not in clue_data:
                        clue_data["description"] = prompt
                    if "details" not in clue_data:
                        clue_data["details"] = content
                    # Add context
                    clue_data["context"] = context
                    return clue_data
            except json.JSONDecodeError:
                # If JSON parsing fails, use the raw content
                pass

            # Fallback if JSON parsing failed
            return {
                "description": prompt or "Unknown Clue",
                "details": content,
                "context": context
            }

        except Exception as e:
            self.update_memory("last_error", f"ModelRouter error: {str(e)}")
            # Fallback to a simple clue if model call fails
            return {
                "description": prompt or "Unknown Clue",
                "details": "Unable to analyze this clue at the moment.",
                "context": context
            }

# --- Inline Tests ---
import unittest
from unittest.mock import patch, MagicMock

class ClueAgentTest(unittest.TestCase):
    def setUp(self):
        self.agent = ClueAgent(use_mem0=False)  # Disable Mem0 for testing

    def test_expected(self):
        # Patch the PydanticAI agent to avoid actual API calls
        with patch.object(self.agent, 'pydantic_agent') as mock_agent:
            # Mock the run_sync method to return a valid result
            mock_result = MagicMock()
            mock_result.output = ClueOutput(
                clue={
                    "description": "Bloody candlestick",
                    "details": "A metal candlestick with blood stains on the handle."
                },
                sources=[]
            )
            mock_agent.run_sync.return_value = mock_result

            # Call the method
            result = self.agent.generate_clue("Bloody candlestick", {})

            # Verify the result
            self.assertIn("description", result.clue)
            self.assertEqual(result.clue["description"], "Bloody candlestick")

    def test_edge_empty_prompt(self):
        # Patch the PydanticAI agent to avoid actual API calls
        with patch.object(self.agent, 'pydantic_agent') as mock_agent:
            # Mock the run_sync method to return a valid result
            mock_result = MagicMock()
            mock_result.output = ClueOutput(
                clue={
                    "description": "Unknown Clue",
                    "details": "No details available."
                },
                sources=[]
            )
            mock_agent.run_sync.return_value = mock_result

            # Call the method
            result = self.agent.generate_clue("", {})

            # Verify the result
            self.assertTrue(isinstance(result.clue, dict))

    def test_failure_brave_down(self):
        # Patch the PydanticAI agent to simulate failure
        with patch.object(self.agent, 'pydantic_agent') as mock_agent:
            # Make the agent raise an exception
            mock_agent.run_sync.side_effect = Exception("API Error")

            # Monkeypatch _brave_search to simulate failure
            original_search = self.agent._brave_search
            self.agent._brave_search = lambda _: []

            # Call the method
            result = self.agent.generate_clue("Torn photo", {})

            # Verify the result
            self.assertIn("description", result.clue)

            # Restore original method
            self.agent._brave_search = original_search

    def test_pydanticai_integration(self):
        # Test the PydanticAI integration with ClueGenerateOutput
        with patch.object(self.agent, 'pydantic_agent') as mock_agent:
            # Mock the run_sync method to return a ClueGenerateOutput
            mock_result = MagicMock()
            mock_result.output = ClueGenerateOutput(
                clue=ClueData(
                    description="Fingerprint on glass",
                    details="A partial fingerprint found on a drinking glass.",
                    significance="May identify the suspect",
                    related_to=["kitchen", "dining room"],
                    confidence=0.85
                ),
                sources=["https://example.com/forensics"]
            )
            mock_agent.run_sync.return_value = mock_result

            # Call the method
            result = self.agent.generate_clue("Fingerprint on glass", {})

            # Verify the result
            self.assertIn("description", result.clue)
            self.assertEqual(result.clue["description"], "Fingerprint on glass")
            self.assertIn("significance", result.clue)
            self.assertEqual(result.clue["significance"], "May identify the suspect")
            self.assertEqual(result.sources, ["https://example.com/forensics"])