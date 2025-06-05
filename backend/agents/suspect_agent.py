"""
SuspectAgent for the Murþrą application.
Handles suspect profile generation, dialogue, and behavior using web search and LLMs.
Enhanced with PydanticAI for better type safety and agent capabilities.
Uses ModelRouter to select appropriate models for different tasks:
- deepseek-r1t-chimera for reasoning/analysis
- mistral-nemo for writing/narrative
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
from pydantic_ai.messages import Message

# --- Pydantic Models ---

class SuspectProfile(BaseModel):
    """Model representing a suspect's profile."""
    model_config = ConfigDict(extra="ignore")

    name: str
    background: str
    occupation: Optional[str] = None
    motive: Optional[str] = None
    alibi: Optional[str] = None
    personality_traits: List[str] = Field(default_factory=list)
    relationship_to_victim: Optional[str] = None
    suspicious_behaviors: List[str] = Field(default_factory=list)
    secrets: List[str] = Field(default_factory=list)

class SuspectState(BaseModel):
    """Model representing a suspect's current state in the investigation."""
    model_config = ConfigDict(extra="ignore")

    name: str
    interviewed: bool = False
    suspicious_level: int = 0
    known_information: List[str] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
    emotional_state: Optional[str] = None

class SuspectProfileInput(BaseModel):
    """Input model for generating a suspect profile."""
    model_config = ConfigDict(extra="ignore")

    prompt: str
    context: dict = Field(default_factory=dict)

class SuspectProfileOutput(BaseModel):
    """Output model for a generated suspect profile."""
    model_config = ConfigDict(extra="ignore")

    profile: SuspectProfile
    sources: List[str] = Field(default_factory=list)

class SuspectDialogueInput(BaseModel):
    """Input model for generating suspect dialogue."""
    model_config = ConfigDict(extra="ignore")

    question: str
    suspect_state: SuspectState
    player_profile: Optional[PsychologicalProfile] = Field(default_factory=create_default_profile)
    context: dict = Field(default_factory=dict)

class SuspectDialogueOutput(BaseModel):
    """Output model for generated suspect dialogue."""
    model_config = ConfigDict(extra="ignore")

    dialogue: str
    updated_state: SuspectState

# --- SuspectAgent Dependencies ---

class SuspectAgentDependencies:
    """Dependencies for the SuspectAgent PydanticAI agent."""
    def __init__(self, memory=None, use_mem0=True, user_id=None, mem0_config=None):
        self.memory = memory
        self.use_mem0 = use_mem0
        self.user_id = user_id
        self.mem0_config = mem0_config or {}
        self.agent_name = "SuspectAgent"

    def update_memory(self, key, value):
        """Update memory with key-value pair."""
        if self.use_mem0 and hasattr(self.memory, 'update'):
            self.memory.update(key, value)

    def search_memories(self, query, limit=3, threshold=0.7, rerank=True):
        """Search memories based on query."""
        if self.use_mem0 and hasattr(self.memory, 'search'):
            return self.memory.search(query, limit=limit, threshold=threshold, rerank=rerank)
        return []

# --- SuspectAgent Implementation ---

class SuspectAgent(BaseAgent):
    """Agent responsible for suspect profile generation, dialogue, and behavior."""
    def __init__(self, memory=None, use_mem0=True, user_id=None, mem0_config=None):
        super().__init__("SuspectAgent", memory, use_mem0=use_mem0, user_id=user_id, mem0_config=mem0_config)

        # Initialize ModelRouter for intelligent model selection
        self.model_router = ModelRouter()

        # Initialize PydanticAI agent
        self.pydantic_agent = self._create_pydantic_agent()
        self.dependencies = SuspectAgentDependencies(memory, use_mem0, user_id, mem0_config)

    def _create_pydantic_agent(self):
        """Create and configure the PydanticAI agent."""
        # Determine which model to use based on environment variables
        model_name = os.getenv("LLM_MODEL", "openai:gpt-4o")

        # Create the agent with appropriate system prompt
        agent = PydanticAgent(
            model_name,
            deps_type=SuspectAgentDependencies,
            output_type=Union[SuspectProfileOutput, SuspectDialogueOutput],
            system_prompt=(
                "You are an expert criminal psychologist and detective specializing in suspect profiling. "
                "Create realistic, nuanced suspect profiles and generate believable dialogue for suspects "
                "under interrogation. Consider their psychology, background, and potential motives. "
                "Pay attention to subtle behavioral cues, contradictions, and emotional responses."
            ),
            retries=2  # Allow retries for better error handling
        )

        # Register tools for the agent
        @agent.tool
        async def brave_search(ctx: RunContext[SuspectAgentDependencies], query: str) -> list[dict]:
            """Search the web for information related to the query."""
            return self._brave_search(query)

        @agent.tool
        async def generate_suspect_profile(
            ctx: RunContext[SuspectAgentDependencies],
            prompt: str,
            context: dict = None,
            search_results: list[dict] = None
        ) -> SuspectProfile:
            """Generate a detailed suspect profile based on the prompt and context."""
            search_results = search_results or self._brave_search(prompt)
            return self._llm_generate_suspect(prompt, context or {}, search_results)

        @agent.tool
        async def generate_suspect_dialogue(
            ctx: RunContext[SuspectAgentDependencies],
            question: str,
            suspect_state: SuspectState,
            context: dict = None
        ) -> SuspectDialogueOutput:
            """Generate dialogue for a suspect based on the question and their current state."""
            return self._llm_generate_dialogue(question, suspect_state, context or {})

        @agent.tool
        async def search_memories(
            ctx: RunContext[SuspectAgentDependencies],
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
            ctx: RunContext[SuspectAgentDependencies],
            key: str,
            value: str
        ) -> None:
            """Update memory with key-value pair."""
            if ctx.deps.use_mem0:
                ctx.deps.update_memory(key, value)

        return agent

    def generate_suspect(self, prompt: str, context: dict = None) -> SuspectProfileOutput:
        """
        Generate a suspect profile using web search and LLM.

        Args:
            prompt (str): Description or name of the suspect.
            context (dict): Optional context for the suspect generation.

        Returns:
            SuspectProfileOutput: The generated suspect profile and sources.
        """
        context = context or {}
        start_time = time.time()

        # Store the prompt in Mem0 for future reference
        if self.use_mem0:
            self.update_memory("suspect_prompt", prompt)
            if context:
                self.update_memory("suspect_context", str(context))

        # Try using PydanticAI agent first
        try:
            # Prepare the prompt for the agent
            agent_prompt = f"Generate a detailed suspect profile for: {prompt}\n"

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

            # Extract the profile from the result
            if hasattr(result.output, 'profile'):
                profile = result.output.profile

                # Store the generated profile in Mem0
                if self.use_mem0 and self.mem0_config.get("store_summaries", True):
                    self.update_memory("generated_profile", str(profile)[:500])

                return SuspectProfileOutput(
                    profile=profile,
                    sources=result.output.sources if hasattr(result.output, 'sources') else []
                )

        except Exception as e:
            error_msg = f"PydanticAI agent error: {str(e)}"
            if self.use_mem0:
                self.update_memory("last_error", error_msg)

        # Fallback to traditional method if PydanticAI fails
        search_results = self._brave_search(prompt)
        profile = self._llm_generate_suspect(prompt, context, search_results)

        return SuspectProfileOutput(
            profile=profile,
            sources=[r['url'] for r in search_results]
        )

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
        params = {"q": query, "count": 5}

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            results = [
                {"title": r["title"], "url": r["url"], "snippet": r.get("description", "")}
                for r in data.get("web", {}).get("results", [])
            ]

            # Store search metadata in Mem0
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                self.update_memory("last_search_query", query)
                self.update_memory("last_search_result_count", str(len(results)))

            return results

        except Exception as e:
            if self.use_mem0:
                self.update_memory("last_error", f"Brave search error: {str(e)}")
            return []

    def _llm_generate_suspect(self, prompt: str, context: dict, search_results: list[dict]) -> SuspectProfile:
        """
        Generate a suspect profile using the ModelRouter.
        Uses a two-step process:
        1. First, use deepseek-r1t-chimera to analyze and plan the profile (reasoning)
        2. Then, use mistral-nemo to write the actual profile (writing)

        Args:
            prompt (str): Description or name of the suspect.
            context (dict): Context for the suspect generation.
            search_results (list[dict]): Search results to use as reference.

        Returns:
            SuspectProfile: The generated suspect profile.
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

        # Format context for the prompt
        context_str = json.dumps(context, indent=2) if context else "{}"

        if not self.model_router.api_key:
            if self.use_mem0:
                self.update_memory("last_error", "Missing LLM API key")
            # Fallback to a simple profile if API key is missing
            return SuspectProfile(
                name=prompt or "Unknown Suspect",
                background="No background information available.",
                personality_traits=["unknown"]
            )

        # First, create a planning prompt for the reasoning model
        planning_system_prompt = (
            "You are an expert criminal psychologist and detective specializing in suspect profiling. "
            "Analyze the given information and create a detailed plan for a suspect profile. "
            "Consider psychology, background, potential motives, and behavioral patterns. "
            "Focus on creating a realistic, nuanced profile with logical connections between elements."
        )

        planning_user_prompt = (
            f"Plan a detailed suspect profile for: {prompt}\n\n"
            f"Context: {context_str}\n"
            f"{search_context}\n\n"
            "Create a structured plan that addresses:\n"
            "1. Key background elements to include\n"
            "2. Potential motives based on the information\n"
            "3. Psychological traits that would be consistent\n"
            "4. Possible secrets or hidden information\n"
            "5. Relationship to the victim and other suspects\n"
            "6. Behavioral patterns that might indicate guilt or innocence"
        )

        planning_messages = [
            Message(role="system", content=planning_system_prompt),
            Message(role="user", content=planning_user_prompt)
        ]

        try:
            # Generate the profile plan using the reasoning model
            planning_response = self.model_router.complete(
                messages=planning_messages,
                task_type="reasoning",
                temperature=0.3,  # Lower temperature for planning
                max_tokens=800
            )

            # Store the planning response in memory for debugging if tracking is enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                self.update_memory("suspect_planning_response", str(planning_response.content)[:500])
                self.update_memory("suspect_planning_model", self.model_router.get_model_name_for_task("reasoning"))

            # Now, create a writing prompt for the writing model
            writing_system_prompt = (
                "You are an expert criminal psychologist and detective specializing in suspect profiling. "
                "Create a realistic, nuanced suspect profile based on the given information and plan. "
                "Format your response as a structured profile with name, background, occupation, motive, "
                "alibi, personality traits, relationship to victim, suspicious behaviors, and secrets."
            )

            writing_user_prompt = (
                f"Generate a detailed suspect profile for: {prompt}\n\n"
                f"Context: {context_str}\n"
                f"{search_context}\n\n"
                f"Profile plan:\n{planning_response.content}\n\n"
                "Provide a structured profile with the following fields:\n"
                "- name: The suspect's name\n"
                "- background: Their personal history and background\n"
                "- occupation: Their job or profession\n"
                "- motive: Potential motive for the crime\n"
                "- alibi: Their claimed alibi, if any\n"
                "- personality_traits: List of key personality traits\n"
                "- relationship_to_victim: How they knew or were connected to the victim\n"
                "- suspicious_behaviors: Any suspicious behaviors or actions\n"
                "- secrets: Hidden information or secrets they might be keeping"
            )

            writing_messages = [
                Message(role="system", content=writing_system_prompt),
                Message(role="user", content=writing_user_prompt)
            ]

            # Generate the profile using the writing model
            writing_response = self.model_router.complete(
                messages=writing_messages,
                task_type="writing",
                temperature=0.7,  # Higher temperature for creative writing
                max_tokens=1000
            )

            # Store the writing response in memory for debugging if tracking is enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                self.update_memory("suspect_writing_response", str(writing_response.content)[:500])
                self.update_memory("suspect_writing_model", self.model_router.get_model_name_for_task("writing"))

            # Extract the generated profile
            profile_text = writing_response.content

            if not profile_text:
                if self.use_mem0:
                    self.update_memory("last_error", "Empty response from LLM")
                return SuspectProfile(
                    name=prompt or "Unknown Suspect",
                    background="No background information available.",
                    personality_traits=["unknown"]
                )

            # Parse the profile text into a structured format
            try:
                # Try to parse as JSON first
                profile_dict = json.loads(profile_text)
                return SuspectProfile(**profile_dict)
            except json.JSONDecodeError:
                # If not JSON, try to extract structured information from text
                lines = profile_text.split("\n")
                profile_dict = {
                    "name": prompt or "Unknown Suspect",
                    "background": "Information extracted from text.",
                    "personality_traits": []
                }

                current_field = None
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Check for field headers
                    if line.lower().startswith("name:"):
                        profile_dict["name"] = line[5:].strip()
                        current_field = "name"
                    elif line.lower().startswith("background:"):
                        profile_dict["background"] = line[11:].strip()
                        current_field = "background"
                    elif line.lower().startswith("occupation:"):
                        profile_dict["occupation"] = line[11:].strip()
                        current_field = "occupation"
                    elif line.lower().startswith("motive:"):
                        profile_dict["motive"] = line[7:].strip()
                        current_field = "motive"
                    elif line.lower().startswith("alibi:"):
                        profile_dict["alibi"] = line[6:].strip()
                        current_field = "alibi"
                    elif line.lower().startswith("personality traits:") or line.lower().startswith("personality_traits:"):
                        profile_dict["personality_traits"] = []
                        current_field = "personality_traits"
                    elif line.lower().startswith("relationship to victim:") or line.lower().startswith("relationship_to_victim:"):
                        profile_dict["relationship_to_victim"] = line.split(":", 1)[1].strip()
                        current_field = "relationship_to_victim"
                    elif line.lower().startswith("suspicious behaviors:") or line.lower().startswith("suspicious_behaviors:"):
                        profile_dict["suspicious_behaviors"] = []
                        current_field = "suspicious_behaviors"
                    elif line.lower().startswith("secrets:"):
                        profile_dict["secrets"] = []
                        current_field = "secrets"
                    # Handle list items
                    elif line.startswith("-") and current_field in ["personality_traits", "suspicious_behaviors", "secrets"]:
                        item = line[1:].strip()
                        if item and current_field in profile_dict:
                            if isinstance(profile_dict[current_field], list):
                                profile_dict[current_field].append(item)
                    # Append to current field if it's a continuation
                    elif current_field:
                        if current_field in ["personality_traits", "suspicious_behaviors", "secrets"]:
                            if line and current_field in profile_dict:
                                if isinstance(profile_dict[current_field], list):
                                    profile_dict[current_field].append(line)
                        else:
                            if current_field in profile_dict and isinstance(profile_dict[current_field], str):
                                profile_dict[current_field] += " " + line

                return SuspectProfile(**profile_dict)

        except Exception as e:
            error_msg = f"LLM profile generation error: {str(e)}"
            if self.use_mem0:
                self.update_memory("last_error", error_msg)

            # Fallback to a simple profile
            return SuspectProfile(
                name=prompt or "Unknown Suspect",
                background="Error generating detailed profile.",
                personality_traits=["unknown"]
            )

    def _llm_generate_dialogue(self, question: str, suspect_state: SuspectState, context: dict) -> SuspectDialogueOutput:
        """Generate dialogue for a suspect based on the question and their current state."""
        # Get psychological adaptations
        player_profile = context.get("player_profile", create_default_profile())
        adaptations = player_profile.get_dialogue_adaptations()
        
        # Create prompt with psychological adaptations
        prompt = f"""
        Generate suspect dialogue based on:
        
        Question: {question}
        Suspect State: {json.dumps(suspect_state.dict(), indent=2)}
        
        Psychological Adaptations:
        {json.dumps(adaptations, indent=2)}
        
        Requirements:
        1. Adapt dialogue style based on player's psychological profile
        2. Consider player's cognitive style for information presentation
        3. Adjust emotional content based on player's emotional tendency
        4. Match interaction pace to player's social style
        5. Maintain suspect's personality and emotional state
        """
        
        # Use the model router to select appropriate model
        model = self.model_router.get_model_for_task("dialogue_generation")
        
        try:
            response = model.generate(prompt)
            dialogue = response.strip()
            
            # Update suspect state
            updated_state = suspect_state.copy()
            updated_state.interviewed = True
            
            # Adjust suspicious level based on psychological profile
            if player_profile.cognitive_style == "analytical":
                # Analytical players are more likely to spot inconsistencies
                updated_state.suspicious_level += 1
            
            return SuspectDialogueOutput(
                dialogue=dialogue,
                updated_state=updated_state
            )
        except Exception as e:
            print(f"Error generating dialogue: {str(e)}")
            return SuspectDialogueOutput(
                dialogue="The suspect remains silent.",
                updated_state=suspect_state
            )

    def generate_dialogue(self, question: str, suspect_state: SuspectState, context: dict = None) -> SuspectDialogueOutput:
        """
        Generate dialogue for a suspect based on the question and their current state.

        Args:
            question (str): The question being asked to the suspect.
            suspect_state (SuspectState): The current state of the suspect.
            context (dict): Additional context for the dialogue generation.

        Returns:
            SuspectDialogueOutput: The generated dialogue and updated suspect state.
        """
        context = context or {}

        # Store the question in Mem0 for future reference
        if self.use_mem0:
            self.update_memory("last_question", question)
            self.update_memory("suspect_state", str(suspect_state.model_dump()))

        # Try using PydanticAI agent first
        try:
            # Prepare the prompt for the agent
            agent_prompt = (
                f"Generate dialogue for suspect {suspect_state.name} in response to this question: \"{question}\"\n"
                f"Consider the suspect's current state and the context of the investigation."
            )

            # Run the agent synchronously
            result = self.pydantic_agent.run_sync(
                agent_prompt,
                deps=self.dependencies,
                model_settings={"temperature": 0.7, "max_tokens": 800}
            )

            # Extract the dialogue from the result
            if hasattr(result.output, 'dialogue') and hasattr(result.output, 'updated_state'):
                dialogue = result.output.dialogue
                updated_state = result.output.updated_state

                # Store the generated dialogue in Mem0
                if self.use_mem0 and self.mem0_config.get("store_summaries", True):
                    self.update_memory("generated_dialogue", dialogue[:500])

                return SuspectDialogueOutput(
                    dialogue=dialogue,
                    updated_state=updated_state
                )

        except Exception as e:
            error_msg = f"PydanticAI dialogue agent error: {str(e)}"
            if self.use_mem0:
                self.update_memory("last_error", error_msg)

        # Fallback to traditional method if PydanticAI fails
        return self._llm_generate_dialogue(question, suspect_state, context)

# --- Inline Tests ---
import unittest

class SuspectAgentTest(unittest.TestCase):
    def setUp(self):
        self.agent = SuspectAgent(use_mem0=False)  # Disable Mem0 for testing

    def test_generate_suspect(self):
        result = self.agent.generate_suspect("John Doe, art thief", {"crime": "museum theft"})
        self.assertIsInstance(result, SuspectProfileOutput)
        self.assertIsInstance(result.profile, SuspectProfile)
        self.assertEqual(result.profile.name, "John Doe, art thief")
        self.assertIsInstance(result.sources, list)

    def test_generate_dialogue(self):
        suspect_state = SuspectState(
            name="Jane Smith",
            interviewed=False,
            suspicious_level=2,
            known_information=["Was at the museum on the day of the theft"],
            contradictions=[],
            emotional_state="calm"
        )

        result = self.agent.generate_dialogue(
            "Where were you on the night of the theft?",
            suspect_state,
            {"crime": "museum theft"}
        )

        self.assertIsInstance(result, SuspectDialogueOutput)
        self.assertIsInstance(result.dialogue, str)
        self.assertIsInstance(result.updated_state, SuspectState)
        self.assertTrue(result.updated_state.interviewed)

    def test_edge_empty_prompt(self):
        result = self.agent.generate_suspect("", {})
        self.assertIsInstance(result.profile, SuspectProfile)
        self.assertTrue(result.profile.name in ["", "Unknown Suspect"])

    def test_failure_brave_down(self):
        # Mock the _brave_search method to simulate failure
        original_search = self.agent._brave_search
        self.agent._brave_search = lambda _: []  # Use underscore to indicate unused parameter

        result = self.agent.generate_suspect("Jane Doe", {})
        self.assertIsInstance(result.profile, SuspectProfile)

        # Restore the original method
        self.agent._brave_search = original_search