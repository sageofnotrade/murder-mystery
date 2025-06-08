"""
SuspectAgent for the Murþrą application.
Handles suspect profile generation, dialogue, and behavior using web search and LLMs.
Enhanced with PydanticAI for better type safety and agent capabilities.
Uses ModelRouter to select appropriate models for different tasks:
- deepseek-r1t-chimera for reasoning/analysis
- mistral-nemo for writing/narrative

# Prompt/Model Strategy (2024-06-08):
# - System prompts are explicit, structured, and role-specific.
# - All LLM completions use ModelRouter:
#     - 'reasoning' (deepseek-r1t-chimera) for planning/analysis
#     - 'writing' (mistral-nemo) for dialogue/profile generation
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
from pydantic_ai.messages import ModelMessage

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
    def __init__(self, memory=None, use_mem0=True, user_id=None, mem0_config=None, model_message_cls=None):
        super().__init__("SuspectAgent", memory, use_mem0=use_mem0, user_id=user_id, mem0_config=mem0_config)

        # Initialize ModelRouter for intelligent model selection
        self.model_router = ModelRouter()

        # Allow injection of ModelMessage class for testability
        self.model_message_cls = model_message_cls or ModelMessage

        # Initialize PydanticAI agent
        self.pydantic_agent = self._create_pydantic_agent()
        self.dependencies = SuspectAgentDependencies(memory, use_mem0, user_id, mem0_config)

    def _create_pydantic_agent(self):
        """Create and configure the PydanticAI agent."""
        # Use the model router to get the appropriate model
        model = self.model_router.get_model_for_task("reasoning")
        
        # Create the agent with appropriate system prompt
        agent = PydanticAgent(
            model=model,  # Use the model from the router
            deps_type=SuspectAgentDependencies,
            output_type=Union[SuspectProfileOutput, SuspectDialogueOutput],
            system_prompt=(
                "You are an expert at creating and managing suspect characters in mystery stories. "
                "Create compelling, complex suspects with clear motivations and personalities. "
                "Include rich character details, potential alibis, and suspicious behaviors. "
                "The suspects should be memorable and have depth."
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
            {"role": "system", "content": planning_system_prompt},
            {"role": "user", "content": planning_user_prompt}
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
                {"role": "system", "content": writing_system_prompt},
                {"role": "user", "content": writing_user_prompt}
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
            print("[DEBUG] SuspectAgent writing_response.content:", repr(profile_text))

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
                print("[DEBUG] SuspectAgent parsed profile_dict:", profile_dict)
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
        import json
        from pydantic_ai.messages import ModelMessage
        
        # Extract player profile and adaptations from context (new feature)
        player_profile = context.get("player_profile", None)
        if player_profile:
            adaptations = player_profile.get_dialogue_adaptations()
            adaptations_str = json.dumps(adaptations, indent=2)
            cognitive_style = getattr(player_profile, "cognitive_style", None)
        else:
            adaptations_str = "{}"
            cognitive_style = None

        # Format context and suspect state for prompts
        context_str = json.dumps(context, indent=2) if context else "{}"
        suspect_state_str = json.dumps(suspect_state.model_dump(), indent=2)
        
        if not self.model_router.api_key:
            if self.use_mem0:
                self.update_memory("last_error", "Missing LLM API key")
            updated_state = suspect_state.model_copy()
            updated_state.interviewed = True
            return SuspectDialogueOutput(
                dialogue=f"\"I don't know anything about that,\" {suspect_state.name} says nervously.",
                updated_state=updated_state
            )
        
        # Planning prompt includes psychological adaptations (added from new)
        planning_system_prompt = (
            "You are an expert in criminal psychology and suspect behavior. "
            "Analyze the suspect's profile, state, the question, and the player's psychological profile and dialogue adaptations. "
            "Plan how the suspect would realistically respond based on their psychology, knowledge, emotional state, and player's cognitive and emotional style."
        )
        
        planning_user_prompt = (
            f"Plan a dialogue response for suspect {suspect_state.name} to this question: \"{question}\"\n\n"
            f"Current suspect state: {suspect_state_str}\n\n"
            f"Player dialogue adaptations: {adaptations_str}\n\n"
            f"Additional context: {context_str}\n\n"
            "Create a structured plan addressing:\n"
            "1. The suspect's likely psychological reaction to this question\n"
            "2. What information they would reveal or conceal\n"
            "3. Their emotional response and body language\n"
            "4. How this interaction might change their state\n"
            "5. Any potential contradictions or inconsistencies in their response\n"
            "6. How to adapt the dialogue style and pacing to the player's psychological profile"
        )
        
        planning_messages = [
            {"role": "system", "content": planning_system_prompt},
            {"role": "user", "content": planning_user_prompt}
        ]
        
        try:
            planning_response = self.model_router.complete(
                messages=planning_messages,
                task_type="reasoning",
                temperature=0.3,
                max_tokens=800
            )
            
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                self.update_memory("dialogue_planning_response", str(planning_response.content)[:500])
                self.update_memory("dialogue_planning_model", self.model_router.get_model_name_for_task("reasoning"))
            
            # Writing prompt with psychological adaptations + plan
            writing_system_prompt = (
                "You are an expert in criminal psychology and suspect behavior. "
                "Generate realistic dialogue for a suspect being questioned, based on their profile, state, the planning output, "
                "and the player's psychological adaptations. "
                "The dialogue should reflect personality, emotional state, and knowledge or secrets. "
                "Also update suspect's state after this interaction."
            )
            
            writing_user_prompt = (
                f"Generate dialogue for suspect {suspect_state.name} in response to: \"{question}\"\n\n"
                f"Current suspect state: {suspect_state_str}\n\n"
                f"Player dialogue adaptations: {adaptations_str}\n\n"
                f"Additional context: {context_str}\n\n"
                f"Response plan:\n{planning_response.content}\n\n"
                "Provide:\n"
                "1. The suspect's dialogue response\n"
                "2. An updated suspect state reflecting changes after this interaction\n"
                "3. Adapt dialogue style and pacing based on player's psychological profile"
            )
            
            writing_messages = [
                {"role": "system", "content": writing_system_prompt},
                {"role": "user", "content": writing_user_prompt}
            ]
            
            writing_response = self.model_router.complete(
                messages=writing_messages,
                task_type="writing",
                temperature=0.7,
                max_tokens=1000
            )
            
            print("[DEBUG] SuspectAgent dialogue writing_response.content:", repr(writing_response.content))
            
            dialogue_text = writing_response.content
            
            if not dialogue_text:
                if self.use_mem0:
                    self.update_memory("last_error", "Empty dialogue response from LLM")
                updated_state = suspect_state.model_copy()
                updated_state.interviewed = True
                return SuspectDialogueOutput(
                    dialogue=f"\"I don't know anything about that,\" {suspect_state.name} says nervously.",
                    updated_state=updated_state
                )
            
            try:
                response_dict = json.loads(dialogue_text)
                dialogue = response_dict.get("dialogue", "")
                updated_state_dict = response_dict.get("updated_state", {})
                updated_state = SuspectState(**updated_state_dict)
            except json.JSONDecodeError:
                dialogue = dialogue_text
                updated_state = suspect_state.model_copy()
                updated_state.interviewed = True
                
                # Infer emotional state from dialogue text (from original)
                lowered = dialogue_text.lower()
                if "nervous" in lowered or "fidgeting" in lowered:
                    updated_state.emotional_state = "nervous"
                elif "angry" in lowered or "shouting" in lowered:
                    updated_state.emotional_state = "angry"
                elif "calm" in lowered or "composed" in lowered:
                    updated_state.emotional_state = "calm"
                
                # Increase suspicious if contradictions detected
                if "contradiction" in lowered or "inconsistent" in lowered:
                    updated_state.suspicious_level += 1
                    if "Inconsistent statement detected" not in updated_state.contradictions:
                        updated_state.contradictions.append("Inconsistent statement detected")
            
            # Add suspicious level bump for analytical player (new feature)
            if cognitive_style == "analytical":
                updated_state.suspicious_level += 1
            
            return SuspectDialogueOutput(
                dialogue=dialogue,
                updated_state=updated_state
            )
        
        except Exception as e:
            error_msg = f"LLM dialogue generation error: {str(e)}"
            if self.use_mem0:
                self.update_memory("last_error", error_msg)
            
            updated_state = suspect_state.model_copy()
            updated_state.interviewed = True
            
            return SuspectDialogueOutput(
                dialogue=f"\"I don't know anything about that,\" {suspect_state.name} says nervously.",
                updated_state=updated_state
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