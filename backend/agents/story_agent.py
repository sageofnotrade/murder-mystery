"""
StoryAgent class for generating and managing interactive mystery stories.
Enhanced with PydanticAI for better type safety and agent capabilities.
Uses ModelRouter to select appropriate models for different tasks:
- deepseek-r1t-chimera for reasoning/analysis
- mistral-nemo for writing/narrative

# Prompt/Model Strategy (2024-06-08):
# - System prompts are explicit, structured, and role-specific.
# - All LLM completions use ModelRouter:
#     - 'reasoning' (deepseek-r1t-chimera) for planning/analysis
#     - 'writing' (mistral-nemo) for narrative generation
# - Parameters tuned: temperature=0.3 for planning, 0.7 for narrative; max_tokens set per step.
# - Prompts include context, player profile, and clear output format instructions.
# - Inline comments explain prompt structure and model routing choices.
"""

from .base_agent import BaseAgent
from .model_router import ModelRouter
from .models.psychological_profile import (
    PsychologicalProfile, create_default_profile,
    CognitiveStyle, EmotionalTendency, SocialStyle, TraitIntensity, PsychologicalTrait
)
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Any, Annotated, Union
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

class SuspectState(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    interviewed: bool = False
    suspicious_level: int = 0

class StoryState(BaseModel):
    model_config = ConfigDict(extra="ignore")

    template_id: Optional[str] = None
    title: str
    current_scene: str = "introduction"
    narrative_history: List[str] = Field(default_factory=list)
    discovered_clues: List[str] = Field(default_factory=list)
    suspect_states: Dict[str, SuspectState] = Field(default_factory=dict)
    last_action: Optional[str] = None

class PlayerProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")

    psychological_profile: PsychologicalProfile = Field(
        default_factory=create_default_profile
    )
    preferences: Dict[str, str] = Field(default_factory=dict)
    role: str = ""  # Can be "detective", "suspect", "witness", etc.

class StoryAgentInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    action: str
    story_state: StoryState
    player_profile: PlayerProfile

class StoryAgentOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    narrative: str
    story_state: StoryState

class StoryAgentGenerateInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    prompt: str
    context: dict = Field(default_factory=dict)

class StoryAgentGenerateOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    story: str
    sources: list[str] = Field(default_factory=list)

# --- StoryAgent Dependencies ---

class StoryAgentDependencies:
    """Dependencies for the StoryAgent PydanticAI agent."""
    def __init__(self, memory=None, use_mem0=True, user_id=None, mem0_config=None):
        self.memory = memory
        self.use_mem0 = use_mem0
        self.user_id = user_id
        self.mem0_config = mem0_config or {}
        self.agent_name = "StoryAgent"

    def update_memory(self, key, value):
        """Update memory with key-value pair."""
        if self.use_mem0 and hasattr(self.memory, 'update'):
            self.memory.update(key, value)

    def search_memories(self, query, limit=3, threshold=0.7, rerank=True):
        """Search memories based on query."""
        if self.use_mem0 and hasattr(self.memory, 'search'):
            return self.memory.search(query, limit=limit, threshold=threshold, rerank=rerank)
        return []

# --- StoryAgent Implementation ---

class StoryAgent(BaseAgent):
    """Agent responsible for narrative generation and progression."""
    def __init__(self, memory=None, use_mem0=True, user_id=None, mem0_config=None):
        super().__init__("StoryAgent", memory, use_mem0=use_mem0, user_id=user_id, mem0_config=mem0_config)

        # Initialize ModelRouter for intelligent model selection
        self.model_router = ModelRouter()

        # Initialize PydanticAI agent
        self.pydantic_agent = self._create_pydantic_agent()
        self.dependencies = StoryAgentDependencies(memory, use_mem0, user_id, mem0_config)

    def _create_pydantic_agent(self):
        """Create and configure the PydanticAI agent."""
        # Use the model router to get the appropriate model
        model = self.model_router.get_model_for_task("writing")
        
        # Create the agent with appropriate system prompt
        agent = PydanticAgent(
            model=model,  # Use the model from the router
            deps_type=StoryAgentDependencies,
            output_type=Union[StoryAgentOutput, StoryAgentGenerateOutput],
            system_prompt=(
                "You are a creative mystery writer specializing in detective fiction. "
                "Create engaging, atmospheric detective stories based on the given prompts. "
                "Include rich sensory details, compelling characters, and intriguing plot elements. "
                "The story should have a noir feel with unexpected twists."
            ),
            retries=2  # Allow retries for better error handling
        )

        # Register tools for the agent
        @agent.tool
        async def brave_search(ctx: RunContext[StoryAgentDependencies], query: str) -> list[dict]:
            """Search the web for information related to the query."""
            return self._brave_search(query)

        @agent.tool
        async def generate_narrative(
            ctx: RunContext[StoryAgentDependencies],
            action: str,
            context: dict,
            search_results: list[dict],
            memory_context: str = ""
        ) -> str:
            """Generate narrative progression based on player action and story context."""
            return self._llm_generate_narrative(action, context, search_results, memory_context)

        @agent.tool
        async def generate_story(
            ctx: RunContext[StoryAgentDependencies],
            prompt: str,
            context: dict = None,
            search_results: list[dict] = None,
            memory_context: str = ""
        ) -> str:
            """Generate a complete story based on the prompt and context."""
            search_results = search_results or self._brave_search(prompt)
            return self._llm_generate_story(prompt, context or {}, search_results, memory_context)

        @agent.tool
        async def extract_potential_clue(
            ctx: RunContext[StoryAgentDependencies],
            action: str,
            narrative: str
        ) -> Optional[str]:
            """Extract a potential clue from the narrative based on the action."""
            return self._extract_potential_clue(action, narrative)

        @agent.tool
        async def search_memories(
            ctx: RunContext[StoryAgentDependencies],
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
            ctx: RunContext[StoryAgentDependencies],
            key: str,
            value: str
        ) -> None:
            """Update memory with key-value pair."""
            if ctx.deps.use_mem0:
                ctx.deps.update_memory(key, value)

        return agent

    def process(self, input_data: dict) -> dict:
        """Process input data and generate narrative text.
        Args:
            input_data (dict): Should match StoryAgentInput
        Returns:
            dict: Output matching StoryAgentOutput
        """
        # Parse input using Pydantic
        parsed_input = StoryAgentInput(**input_data)
        action = parsed_input.action
        story_state = parsed_input.story_state
        player_profile = parsed_input.player_profile

        # Store the action in Mem0 for future reference
        if self.use_mem0:
            self.update_memory(f"action_{len(story_state.narrative_history)}", action)

        # Build context for narrative generation
        context = {
            "current_scene": story_state.current_scene,
            "last_action": story_state.last_action,
            "title": story_state.title,
            "discovered_clues": story_state.discovered_clues,
            "player_role": player_profile.role,
            "player_traits": player_profile.psychological_profile.traits,
            "player_preferences": player_profile.preferences
        }

        # Add suspect information if available
        suspects_context = {}
        for suspect_id, suspect in story_state.suspect_states.items():
            suspects_context[suspect_id] = {
                "name": suspect.name,
                "interviewed": suspect.interviewed,
                "suspicious_level": suspect.suspicious_level
            }
        context["suspects"] = suspects_context

        # Generate narrative based on action and context
        player_role = player_profile.role
        if player_role == "detective":
            search_query = f"detective {action} mystery story progression"
        elif player_role == "suspect":
            search_query = f"suspect {action} mystery story progression"
        elif player_role == "witness":
            search_query = f"witness {action} mystery story progression"
        else:
            search_query = f"{player_role} {action} mystery story progression"

        # Try using PydanticAI agent first
        try:
            # Prepare the prompt for the agent
            agent_prompt = (
                f"Generate a narrative response for the player's action: {action}\n"
                f"Player role: {player_role}\n"
                f"Current scene: {story_state.current_scene}\n"
                f"Last action: {story_state.last_action or 'None'}\n"
                f"Title: {story_state.title}\n"
                f"Discovered clues: {', '.join(story_state.discovered_clues) if story_state.discovered_clues else 'None'}"
            )

            # Run the agent synchronously
            result = self.pydantic_agent.run_sync(
                agent_prompt,
                deps=self.dependencies,
                model_settings={"temperature": 0.7, "max_tokens": 500}
            )

            # Extract the narrative from the result
            if isinstance(result.output, StoryAgentOutput):
                narrative = result.output.narrative
                # Use the updated story state from the agent if available
                updated_story_state = result.output.story_state

                # Merge the updated story state with our current one
                story_state.last_action = action
                story_state.narrative_history.append(narrative)

                # Update discovered clues if any new ones were found
                for clue in updated_story_state.discovered_clues:
                    if clue not in story_state.discovered_clues:
                        story_state.discovered_clues.append(clue)

                # Update suspect states if they changed
                for suspect_id, suspect in updated_story_state.suspect_states.items():
                    if suspect_id in story_state.suspect_states:
                        story_state.suspect_states[suspect_id] = suspect
            else:
                # If we got a StoryAgentGenerateOutput instead, use the story as narrative
                narrative = result.output.story

                # Update state
                story_state.last_action = action
                story_state.narrative_history.append(narrative)

                # Check for scene transitions based on action
                if "interview" in action.lower() or "question" in action.lower():
                    # Update suspect interview status if interviewing a suspect
                    for suspect_id, suspect in story_state.suspect_states.items():
                        if suspect.name.lower() in action.lower():
                            story_state.suspect_states[suspect_id].interviewed = True
                            break

                # Check for clue discovery based on action
                if "examine" in action.lower() or "inspect" in action.lower() or "search" in action.lower():
                    # This would be more sophisticated in production, using LLM to determine if a clue was found
                    potential_clue = self._extract_potential_clue(action, narrative)
                    if potential_clue and potential_clue not in story_state.discovered_clues:
                        story_state.discovered_clues.append(potential_clue)

            # Store the narrative in Mem0 for future reference
            if self.use_mem0:
                self.update_memory(f"narrative_{len(story_state.narrative_history)}", narrative)

            return StoryAgentOutput(narrative=narrative, story_state=story_state).model_dump()

        except Exception as e:
            # Fallback to traditional method if PydanticAI fails
            if self.use_mem0:
                self.update_memory("last_error", f"PydanticAI error: {str(e)}")

            # Retrieve relevant memories to enhance the narrative
            memory_context = ""
            if self.use_mem0:
                # Search for relevant memories based on the action and context
                memory_results = self.search_memories(
                    query=action,
                    limit=self.mem0_config.get("search_limit", 3),
                    threshold=self.mem0_config.get("search_threshold", 0.7),
                    rerank=self.mem0_config.get("rerank", True)
                )
                if memory_results:
                    memory_context = "\n\nRelevant past events:\n"
                    for i, result in enumerate(memory_results, 1):
                        memory_content = result.get("memory", "")
                        if memory_content:
                            memory_context += f"{i}. {memory_content}\n"

            search_results = self._brave_search(search_query)
            narrative = self._llm_generate_narrative(action, context, search_results, memory_context)

            # Update state
            story_state.last_action = action
            story_state.narrative_history.append(narrative)

            # Store the narrative in Mem0 for future reference
            if self.use_mem0:
                self.update_memory(f"narrative_{len(story_state.narrative_history)}", narrative)

            # Check for scene transitions based on action
            if "interview" in action.lower() or "question" in action.lower():
                # Update suspect interview status if interviewing a suspect
                for suspect_id, suspect in story_state.suspect_states.items():
                    if suspect.name.lower() in action.lower():
                        story_state.suspect_states[suspect_id].interviewed = True
                        break

            # Check for clue discovery based on action
            if "examine" in action.lower() or "inspect" in action.lower() or "search" in action.lower():
                # This would be more sophisticated in production, using LLM to determine if a clue was found
                potential_clue = self._extract_potential_clue(action, narrative)
                if potential_clue and potential_clue not in story_state.discovered_clues:
                    story_state.discovered_clues.append(potential_clue)

            return StoryAgentOutput(narrative=narrative, story_state=story_state).model_dump()

    def start_new_story(self, template: dict, player_profile: dict) -> dict:
        """Start a new story based on a template and player profile.
        Args:
            template (dict): The mystery template
            player_profile (dict): The player's psychological profile
        Returns:
            dict: The initial story state (StoryState)
        """
        import json  # for memory storage if used

        # Ensure psychological profile is included and parsed
        if isinstance(player_profile, dict):
            if "psychological_profile" not in player_profile:
                player_profile["psychological_profile"] = create_default_profile()
            else:
                player_profile["psychological_profile"] = PsychologicalProfile(**player_profile["psychological_profile"])
        parsed_profile = PlayerProfile(**player_profile) if isinstance(player_profile, dict) else player_profile

        # Optional: Store in memory
        if self.use_mem0:
            self.update_memory("template", json.dumps(template))
            self.update_memory("player_profile", json.dumps(player_profile))

        # Choose initial scene based on role
        role_to_scene = {
            "suspect": "suspect_introduction",
            "witness": "witness_introduction",
        }
        initial_scene = role_to_scene.get(parsed_profile.role, "introduction")

        # Build suspect states
        suspect_states = {}
        for suspect in template.get("suspects", []):
            suspect_id = suspect.get("id") or suspect.get("name")
            is_player = parsed_profile.role == "suspect" and suspect.get("is_player", False)
            suspect_states[suspect_id] = SuspectState(
                name=suspect.get("name", "Unknown"),
                suspicious_level=0 if is_player else suspect.get("initial_suspicion", 0)
            )

        # Initialize story state
        story_state = StoryState(
            template_id=template.get("id"),
            title=template.get("title", "Untitled Mystery"),
            current_scene=initial_scene,
            narrative_history=[],
            discovered_clues=[],
            suspect_states=suspect_states
        )

        # Return the clean, initialized story state
        return story_state.model_dump()

    def generate_story(self, prompt: str, context: dict = None) -> StoryAgentGenerateOutput:
        """
        Generate a story using Brave Search and an LLM.
        Args:
            prompt (str): The story prompt from the user.
            context (dict): Optional context for the story.
        Returns:
            StoryAgentGenerateOutput: The generated story and sources.
        """
        context = context or {}
        start_time = time.time()

        # Store the prompt in Mem0 for future reference
        if self.use_mem0:
            self.update_memory("story_prompt", prompt)
            if context:
                self.update_memory("story_context", str(context))

        # Try using PydanticAI agent first
        try:
            # Prepare the prompt for the agent
            agent_prompt = (
                f"Generate a complete detective story based on this prompt: {prompt}\n"
                f"Player role: {context.get('player_role', 'detective')}\n"
            )

            # Add any additional context
            if context:
                agent_prompt += "Additional context:\n"
                for key, value in context.items():
                    if key != 'player_role':  # Already included above
                        agent_prompt += f"- {key}: {value}\n"

            # Run the agent synchronously
            result = self.pydantic_agent.run_sync(
                agent_prompt,
                deps=self.dependencies,
                model_settings={"temperature": 0.7, "max_tokens": 1500}
            )

            # Extract the story from the result
            if isinstance(result.output, StoryAgentGenerateOutput):
                story = result.output.story
                sources = result.output.sources
            else:
                # If we got a StoryAgentOutput instead, use the narrative as the story
                story = result.output.narrative
                # Search the web to get sources
                search_results = self._brave_search(prompt)
                sources = [r['url'] for r in search_results]

            # Store the generated story in Mem0
            if self.use_mem0 and self.mem0_config.get("store_summaries", True):
                self.update_memory("generated_story", story[:500] + "..." if len(story) > 500 else story)

                # Track performance metrics if enabled
                if self.mem0_config.get("track_performance", True):
                    generation_time = time.time() - start_time
                    self.update_memory("last_story_generation_time", f"{generation_time:.2f} seconds")

            return StoryAgentGenerateOutput(
                story=story,
                sources=sources
            )

        except Exception as e:
            # Fallback to traditional method if PydanticAI fails
            if self.use_mem0:
                self.update_memory("last_error", f"PydanticAI error in generate_story: {str(e)}")

            # Retrieve relevant memories to enhance the story
            memory_context = ""
            if self.use_mem0:
                # Search for relevant memories based on the prompt
                memory_results = self.search_memories(
                    query=prompt,
                    limit=self.mem0_config.get("search_limit", 3),
                    threshold=self.mem0_config.get("search_threshold", 0.7),
                    rerank=self.mem0_config.get("rerank", True)
                )
                if memory_results:
                    memory_context = "\n\nRelevant past events:\n"
                    for i, result in enumerate(memory_results, 1):
                        memory_content = result.get("memory", "")
                        if memory_content:
                            memory_context += f"{i}. {memory_content}\n"

            # 1. Search the web using Brave Search API
            search_results = self._brave_search(prompt)
            # 2. Use LLM to generate a story with memory enhancement
            story = self._llm_generate_story(prompt, context, search_results, memory_context)

            # Store the generated story in Mem0
            if self.use_mem0 and self.mem0_config.get("store_summaries", True):
                self.update_memory("generated_story", story[:500] + "..." if len(story) > 500 else story)

                # Track performance metrics if enabled
                if self.mem0_config.get("track_performance", True):
                    generation_time = time.time() - start_time
                    self.update_memory("last_story_generation_time", f"{generation_time:.2f} seconds")
                    self.update_memory("last_memory_search_count", str(len(memory_results) if 'memory_results' in locals() else 0))

            return StoryAgentGenerateOutput(
                story=story,
                sources=[r['url'] for r in search_results]
            )

    def clear_memories(self) -> bool:
        """
        Clear all memories for the current user.
        This method is inherited from BaseAgent but exposed here for direct access.

        Returns:
            bool: Success status
        """
        # Call the inherited clear_memories method from BaseAgent
        return super().clear_memories()

    def _llm_generate_story(self, prompt: str, context: dict, search_results: list[dict], memory_context: str = "") -> str:
        """
        Generate a story using the ModelRouter.
        Uses a two-step process:
        1. First, use deepseek-r1t-chimera to analyze and plan the story (reasoning)
        2. Then, use mistral-nemo to write the actual story (writing)
        """
        # Format search results for the prompt
        search_context = ""
        if search_results:
            search_context = "\n\nRelevant information:\n"
            for i, result in enumerate(search_results, 1):
                if result.get("snippet"):
                    search_context += f"{i}. {result['title']}: {result['snippet']}\n"

        # Add memory context if available
        if memory_context:
            search_context += memory_context

        # Determine player role from context
        player_role = context.get("player_role", "detective")

        # STEP 1: Use deepseek-r1t-chimera for story planning and analysis
        planning_system_prompt = (
            "You are an expert story planner and analyst. "
            "Your task is to create a detailed plan for a detective story. "
            f"The player will take on the role of a {player_role.upper()} in the mystery. "
            "Include the following elements in your plan:\n"
            "1. Main characters and their motivations\n"
            "2. Setting and atmosphere\n"
            "3. Crime or mystery to be solved\n"
            "4. Key plot points and twists\n"
            "5. Clues and red herrings\n"
            "6. Resolution\n"
            "Be detailed and analytical. This is a planning document, not the final story."
        )

        planning_user_prompt = f"Create a detailed plan for a detective story based on: {prompt}\n"

        # Add context if provided
        if context:
            planning_user_prompt += "\nIncorporate these elements:\n"
            for key, value in context.items():
                planning_user_prompt += f"- {key}: {value}\n"

        # Add search results and memory context
        planning_user_prompt += search_context

        # Create messages for the planning model
        planning_messages = [
            {"role": "system", "content": planning_system_prompt},
            {"role": "user", "content": planning_user_prompt}
        ]

        try:
            # Generate the story plan using the reasoning model
            planning_response = self.model_router.complete(
                messages=planning_messages,
                task_type="reasoning",
                temperature=0.3,  # Lower temperature for planning
                max_tokens=1000
            )

            # Store the planning response in memory for debugging if tracking is enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                self.update_memory("story_planning_response", str(planning_response.content)[:500])
                self.update_memory("planning_model_used", self.model_router.get_model_name_for_task("reasoning"))

            # Extract the story plan
            story_plan = planning_response.content

            if not story_plan:
                if self.use_mem0:
                    self.update_memory("last_error", "Empty planning response from LLM")
                story_plan = f"A mystery about {prompt} with unexpected twists and compelling characters."

            # STEP 2: Use mistral-nemo to write the actual story based on the plan
            # Build system prompt based on player role
            if player_role == "detective":
                writing_system_prompt = (
                    "You are a creative mystery writer specializing in detective fiction. "
                    "Create an engaging, atmospheric detective story based on the given story plan. "
                    "The player will take on the role of a DETECTIVE investigating the case. "
                    "Include rich sensory details, compelling characters, and intriguing plot elements. "
                    "The story should have a noir feel with unexpected twists."
                )
            elif player_role == "suspect":
                writing_system_prompt = (
                    "You are a creative mystery writer specializing in psychological thrillers. "
                    "Create an engaging, atmospheric story based on the given story plan. "
                    "The player will take on the role of a SUSPECT in the case, navigating the investigation while dealing with their own involvement. "
                    "Include rich sensory details, compelling characters, and intriguing plot elements. "
                    "The story should have a tense, paranoid feel with moral ambiguity."
                )
            elif player_role == "witness":
                writing_system_prompt = (
                    "You are a creative mystery writer specializing in witness perspectives. "
                    "Create an engaging, atmospheric story based on the given story plan. "
                    "The player will take on the role of a WITNESS to the crime, with their own unique perspective and potentially crucial information. "
                    "Include rich sensory details, compelling characters, and intriguing plot elements. "
                    "The story should have an intimate, personal feel with elements of danger and revelation."
                )
            else:
                writing_system_prompt = (
                    "You are a creative mystery writer specializing in diverse perspectives. "
                    "Create an engaging, atmospheric story based on the given story plan. "
                    f"The player will take on the role of a {player_role.upper()} in the mystery. "
                    "Include rich sensory details, compelling characters, and intriguing plot elements. "
                    "The story should have a unique feel appropriate to the character's role."
                )

            writing_user_prompt = (
                f"Write a detective story based on this plan:\n\n{story_plan}\n\n"
                "Make the story engaging, atmospheric, and intriguing. "
                "Include sensory details and compelling dialogue."
            )

            # Create messages for the writing model
            writing_messages = [
                {"role": "system", "content": writing_system_prompt},
                {"role": "user", "content": writing_user_prompt}
            ]

            # Generate the story using the writing model
            writing_response = self.model_router.complete(
                messages=writing_messages,
                task_type="writing",
                temperature=0.7,  # Higher temperature for creative writing
                max_tokens=1500
            )

            # Store the writing response in memory for debugging if tracking is enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                self.update_memory("story_writing_response", str(writing_response.content)[:500])
                self.update_memory("writing_model_used", self.model_router.get_model_name_for_task("writing"))

            # Extract the generated story
            story = writing_response.content

            if not story:
                if self.use_mem0:
                    self.update_memory("last_error", "Empty writing response from LLM")
                return f"A mystery about {prompt} that needs to be solved."

            return story

        except Exception as e:
            # Log the error and return a simple story
            error_msg = f"ModelRouter error: {str(e)}"
            if self.use_mem0:
                self.update_memory("last_error", error_msg)
            return f"A detective story involving {prompt}. The mystery deepens as clues are discovered."

    def _llm_generate_narrative(self, action: str, context: dict, search_results: list[dict], memory_context: str = "") -> str:
            """
            Generate narrative progression using the ModelRouter.
            Integrates psychological adaptations from the player's profile into both the planning and writing steps.
            Uses a two-step process:
            1. First, use deepseek-r1t-chimera to analyze the action and plan the narrative (reasoning)
            2. Then, use mistral-nemo to write the actual narrative (writing)
            """
            import json

            # Extract psychological adaptations from the player's profile
            profile = context.get("player_profile", {}).get("psychological_profile", create_default_profile())
            adaptations = profile.get_narrative_adaptations()

            # Prepare psychological prompt requirements
            psychological_guidelines = """
        Requirements for narrative adaptation:
        1. Adapt the narrative style based on the psychological profile
        2. Maintain story coherence and pacing
        3. Include relevant details based on the player's cognitive style
        4. Adjust emotional content based on the player's emotional tendency
        5. Match the interaction pace to the player's social style
        """
            formatted_adaptations = json.dumps(adaptations, indent=2)

            # Format context for the prompt
            context_str = json.dumps(context, indent=2)

            # Format search results
            search_context = ""
            if search_results:
                search_context = "\n\nRelevant information for narrative progression:\n"
                for i, result in enumerate(search_results[:3], 1):
                    if result.get("snippet"):
                        search_context += f"{i}. {result['snippet']}\n"

            # Add memory context if available
            if memory_context:
                search_context += memory_context

            # Determine player role from context
            player_role = context.get("player_role", "detective")

            # STEP 1: Use deepseek-r1t-chimera for action analysis and narrative planning
            planning_system_prompt = (
                "You are an expert narrative analyst and planner. "
                "Your task is to analyze the player's action and plan the next part of the narrative. "
                f"The player is a {player_role.upper()} in this mystery story. "
                "Consider the following in your analysis:\n"
                "1. What is the player trying to accomplish with this action?\n"
                "2. What might they discover or learn?\n"
                "3. How might other characters react?\n"
                "4. What sensory details would be important to include?\n"
                "5. What emotional tone should the narrative have?\n"
                "6. What potential clues or plot developments could emerge?\n"
                "Be detailed and analytical. This is a planning document, not the final narrative.\n"
                "\nPsychological Adaptations (for planning):\n"
                f"{formatted_adaptations}\n{psychological_guidelines}"
            )

            planning_user_prompt = (
                f"Analyze this player action and plan the next narrative segment:\n\n"
                f"Player action: {action}\n\n"
                f"Current story context:\n{context_str}{search_context}"
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
                    self.update_memory("narrative_planning_response", str(planning_response.content)[:500])
                    self.update_memory("narrative_planning_model", self.model_router.get_model_name_for_task("reasoning"))

                narrative_plan = planning_response.content

                if not narrative_plan:
                    if self.use_mem0:
                        self.update_memory("last_error", "Empty narrative planning response from LLM")
                    narrative_plan = f"The player has decided to {action}. This advances the investigation."

                # STEP 2: Use mistral-nemo to write the actual narrative based on the plan
                if player_role == "detective":
                    writing_system_prompt = (
                        "You are an expert detective fiction writer creating an interactive mystery story. "
                        "Generate the next part of the narrative based on the player's action and the provided narrative plan. "
                        "The player is a DETECTIVE investigating the case. "
                        "Write in second person perspective ('You notice...', 'You decide...'). "
                        "Keep the narrative tense, atmospheric, and intriguing. Include sensory details and character reactions. "
                        "The tone should match the psychological profile of the player.\n"
                        f"\nPsychological Adaptations (for writing):\n{formatted_adaptations}\n{psychological_guidelines}"
                    )
                elif player_role == "suspect":
                    writing_system_prompt = (
                        "You are an expert mystery writer creating an interactive story. "
                        "Generate the next part of the narrative based on the player's action and the provided narrative plan. "
                        "The player is a SUSPECT in the case, trying to navigate the investigation while hiding or revealing their own involvement. "
                        "Write in second person perspective ('You notice...', 'You decide...'). "
                        "Keep the narrative tense, atmospheric, and intriguing. Include sensory details and character reactions. "
                        "The tone should match the psychological profile of the player.\n"
                        f"\nPsychological Adaptations (for writing):\n{formatted_adaptations}\n{psychological_guidelines}"
                    )
                elif player_role == "witness":
                    writing_system_prompt = (
                        "You are an expert mystery writer creating an interactive story. "
                        "Generate the next part of the narrative based on the player's action and the provided narrative plan. "
                        "The player is a WITNESS to the crime, with their own perspective and potentially crucial information. "
                        "Write in second person perspective ('You notice...', 'You decide...'). "
                        "Keep the narrative tense, atmospheric, and intriguing. Include sensory details and character reactions. "
                        "The tone should match the psychological profile of the player.\n"
                        f"\nPsychological Adaptations (for writing):\n{formatted_adaptations}\n{psychological_guidelines}"
                    )
                else:
                    writing_system_prompt = (
                        "You are an expert mystery writer creating an interactive story. "
                        "Generate the next part of the narrative based on the player's action and the provided narrative plan. "
                        f"The player is a {player_role.upper()} in the mystery. "
                        "Write in second person perspective ('You notice...', 'You decide...'). "
                        "Keep the narrative tense, atmospheric, and intriguing. Include sensory details and character reactions. "
                        "The tone should match the psychological profile of the player.\n"
                        f"\nPsychological Adaptations (for writing):\n{formatted_adaptations}\n{psychological_guidelines}"
                    )

                writing_user_prompt = (
                    f"The player has decided to: {action}\n\n"
                    f"Based on this narrative plan, write the next part of the story (2-3 paragraphs):\n\n{narrative_plan}"
                )

                writing_messages = [
                    {"role": "system", "content": writing_system_prompt},
                    {"role": "user", "content": writing_user_prompt}
                ]

                writing_response = self.model_router.complete(
                    messages=writing_messages,
                    task_type="writing",
                    temperature=0.7,
                    max_tokens=500
                )

                if self.use_mem0 and self.mem0_config.get("track_performance", True):
                    self.update_memory("narrative_writing_response", str(writing_response.content)[:500])
                    self.update_memory("narrative_writing_model", self.model_router.get_model_name_for_task("writing"))

                narrative = writing_response.content

                if not narrative:
                    if self.use_mem0:
                        self.update_memory("last_error", "Empty narrative writing response from LLM")
                    return f"You decided to {action}. The investigation continues as you search for more clues."

                return narrative

            except Exception as e:
                print(f"Error generating narrative: {str(e)}")
                return "The story continues..."

    def _extract_potential_clue(self, action: str, narrative: str) -> Optional[str]:
        """
        Extract potential clue from the narrative based on the action using ModelRouter.
        Uses deepseek-r1t-chimera for reasoning about potential clues.
        """
        # Try using ModelRouter to extract clues
        try:
            from pydantic import BaseModel

            # Define a model for the clue extraction
            class ClueExtraction(BaseModel):
                clue: Optional[str] = None
                confidence: float = 0.0
                reasoning: str = ""

            # Create system prompt for clue extraction
            system_prompt = (
                "You are an expert detective and forensic analyst specializing in identifying clues in narratives. "
                "Extract any potential clues from the narrative based on the player's action. "
                "Be precise and analytical in your reasoning. "
                "If no clear clue is present, indicate that with a null clue and low confidence."
            )

            # Create user prompt for clue extraction
            user_prompt = (
                f"Player action: {action}\n\n"
                f"Narrative: {narrative}\n\n"
                "Extract any potential clues from this narrative. "
                "Format your response as JSON with the following fields:\n"
                "- clue: The extracted clue, or null if none found\n"
                "- confidence: A number between 0.0 and 1.0 indicating your confidence\n"
                "- reasoning: Your reasoning for identifying this as a clue"
            )

            # Create messages for the reasoning model
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # Use the reasoning model to extract clues
            response = self.model_router.complete(
                messages=messages,
                task_type="reasoning",  # Use deepseek-r1t-chimera for analytical reasoning
                temperature=0.2,  # Lower temperature for more consistent results
                max_tokens=500
            )

            # Store the response in memory for debugging if tracking is enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                self.update_memory("clue_extraction_response", str(response.content)[:500])
                self.update_memory("clue_extraction_model", self.model_router.get_model_name_for_task("reasoning"))

            # Try to parse the response as a ClueExtraction object
            try:
                import json
                # Extract JSON from the response content
                content = response.content
                # Sometimes the model might wrap the JSON in ```json and ``` markers
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].strip()

                # Parse the JSON
                extraction_data = json.loads(content)
                extraction = ClueExtraction(**extraction_data)

                # If a clue was found with sufficient confidence, return it
                if extraction.clue and extraction.confidence > 0.5:
                    return extraction.clue
            except Exception as json_error:
                # Log the JSON parsing error but continue with the fallback method
                if self.use_mem0:
                    self.update_memory("clue_json_parsing_error", str(json_error))

            # If no clue was found or confidence is low, fall back to keyword-based extraction

        except Exception as e:
            # Log the error but continue with the fallback method
            if self.use_mem0:
                self.update_memory("clue_extraction_error", str(e))

        # Fallback: Simple keyword-based extraction
        potential_clue = None

        # Look for sentences containing clue-related words
        clue_keywords = ["found", "discovered", "noticed", "spotted", "uncovered", "revealed"]
        sentences = narrative.split(". ")

        for sentence in sentences:
            lower_sentence = sentence.lower()
            if any(keyword in lower_sentence for keyword in clue_keywords):
                # Extract noun phrases after the keyword as potential clues
                # This is a simplified approach; in production, use NLP or LLM
                words = sentence.split()
                if len(words) >= 3:
                    potential_clue = sentence.strip()
                    break

        # If no clue found with keywords, check what's being examined
        if not potential_clue and ("examine" in action.lower() or "inspect" in action.lower()):
            # Extract what's being examined from the action
            action_parts = action.split()
            if len(action_parts) >= 2:
                examined_object = " ".join(action_parts[1:])
                potential_clue = f"Examined {examined_object}"

        return potential_clue

    def _brave_search(self, query: str) -> list[dict]:
        """
        Query the Brave Search API and return a list of results.
        Uses direct API call only (removes pydantic_ai BraveSearch dependency).
        """
        # Fallback: Direct API call
        import os
        from dotenv import load_dotenv

        load_dotenv()
        api_key = os.getenv("BRAVE_API_KEY")

        if not api_key:
            if self.use_mem0:
                self.update_memory("last_error", "Missing Brave API key")
            return []

        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {"Accept": "application/json", "X-Subscription-Token": api_key}
        params = {"q": query, "count": 5, "freshness": "month"}

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            # Store the search response in memory if tracking is enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                self.update_memory("last_search_query", query)
                self.update_memory("last_search_count", str(len(data.get("web", {}).get("results", []))))
                self.update_memory("search_method", "direct_brave_api")

            results = [
                {
                    "title": r["title"],
                    "url": r["url"],
                    "snippet": r.get("description", ""),
                    "source": r.get("source", "")
                }
                for r in data.get("web", {}).get("results", [])
            ]

            return results

        except requests.RequestException as e:
            error_msg = f"Brave Search API error: {str(e)}"
            if self.use_mem0:
                self.update_memory("last_error", error_msg)
            return []

# --- Inline Tests (if no tests dir available) ---
import unittest

class StoryAgentTest(unittest.TestCase):
    def setUp(self):
        self.agent = StoryAgent()

    def test_expected(self):
        result = self.agent.generate_story("A detective in Paris", {})
        self.assertTrue(len(result.story) > 0)

    def test_suspect_role(self):
        result = self.agent.generate_story("A murder at the mansion", {"player_role": "suspect"})
        self.assertTrue(len(result.story) > 0)

    def test_witness_role(self):
        result = self.agent.generate_story("A mysterious disappearance", {"player_role": "witness"})
        self.assertTrue(len(result.story) > 0)

    def test_edge_empty_prompt(self):
        result = self.agent.generate_story("", {})
        self.assertTrue(isinstance(result.story, str))

    def test_failure_brave_down(self):
        # Monkeypatch _brave_search to simulate failure
        original_search = self.agent._brave_search
        self.agent._brave_search = lambda _: []  # Ignore the query parameter
        result = self.agent.generate_story("A mystery", {})
        self.assertTrue(len(result.story) > 0)
        # Restore original method
        self.agent._brave_search = original_search

    def test_clear_memories(self):
        # Create an agent with Mem0 enabled for testing
        test_agent = StoryAgent(use_mem0=True, user_id="test_user_clear_memories")

        # Store a test memory
        if test_agent.use_mem0:
            test_agent.update_memory("test_key", "test_value")

            # Clear memories
            result = test_agent.clear_memories()

            # Check if clearing was successful
            self.assertTrue(result)

            # Try to retrieve the cleared memory (should return None)
            retrieved_value = test_agent.get_memory("test_key")
            self.assertIsNone(retrieved_value)

    def test_psychological_profile_integration(self):
        """Test that psychological profile is properly integrated into narrative generation."""
        # Create a test profile with specific traits
        profile = PsychologicalProfile(
            cognitive_style=CognitiveStyle.ANALYTICAL,
            emotional_tendency=EmotionalTendency.RESERVED,
            social_style=SocialStyle.DIRECT,
            traits={
                "curiosity": PsychologicalTrait(
                    name="curiosity",
                    intensity=TraitIntensity.HIGH,
                    description="Strong desire to explore and discover",
                    narrative_impact={
                        "clue_presentation": "detailed",
                        "mystery_pacing": "methodical"
                    },
                    dialogue_impact={
                        "question_style": "thorough",
                        "interaction_approach": "investigative"
                    }
                )
            }
        )

        # Create test input
        input_data = {
            "action": "examine the crime scene",
            "story_state": {
                "current_scene": "crime_scene",
                "narrative_history": [],
                "discovered_clues": []
            },
            "player_profile": {
                "psychological_profile": profile.dict(),
                "role": "detective"
            }
        }

        # Process the input
        result = self.agent.process(input_data)

        # Verify the result contains narrative and updated story state
        self.assertIn("narrative", result)
        self.assertIn("story_state", result)
        
        # Verify the narrative reflects psychological adaptations
        narrative = result["narrative"]
        self.assertIn("examine", narrative.lower())
        self.assertIn("crime scene", narrative.lower())

    def test_default_profile_creation(self):
        """Test that default profile is created when none is provided."""
        input_data = {
            "action": "look around",
            "story_state": {
                "current_scene": "room",
                "narrative_history": [],
                "discovered_clues": []
            },
            "player_profile": {
                "role": "detective"
            }
        }

        result = self.agent.process(input_data)
        self.assertIn("narrative", result)
        self.assertIn("story_state", result)

    def test_profile_adaptations(self):
        """Test that different psychological profiles result in different narrative styles."""
        # Create two different profiles
        analytical_profile = PsychologicalProfile(
            cognitive_style=CognitiveStyle.ANALYTICAL,
            emotional_tendency=EmotionalTendency.RESERVED,
            social_style=SocialStyle.DIRECT
        )

        intuitive_profile = PsychologicalProfile(
            cognitive_style=CognitiveStyle.INTUITIVE,
            emotional_tendency=EmotionalTendency.EXPRESSIVE,
            social_style=SocialStyle.INDIRECT
        )

        # Test with analytical profile
        analytical_input = {
            "action": "investigate the room",
            "story_state": {
                "current_scene": "room",
                "narrative_history": [],
                "discovered_clues": []
            },
            "player_profile": {
                "psychological_profile": analytical_profile.dict(),
                "role": "detective"
            }
        }

        # Test with intuitive profile
        intuitive_input = {
            "action": "investigate the room",
            "story_state": {
                "current_scene": "room",
                "narrative_history": [],
                "discovered_clues": []
            },
            "player_profile": {
                "psychological_profile": intuitive_profile.dict(),
                "role": "detective"
            }
        }

        # Get results for both profiles
        analytical_result = self.agent.process(analytical_input)
        intuitive_result = self.agent.process(intuitive_input)

        # Verify that the narratives are different
        self.assertNotEqual(
            analytical_result["narrative"],
            intuitive_result["narrative"]
        )