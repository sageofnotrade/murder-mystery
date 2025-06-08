"""
CoordinatorAgent for the Murþrą application.
Orchestrates inter-agent communication, maintains global consistency, and resolves conflicts.
Enhanced with PydanticAI for better type safety and agent capabilities.
Uses ModelRouter to select appropriate models for different tasks:
- deepseek-r1t-chimera for reasoning/analysis
- mistral-nemo for writing/narrative

# Prompt/Model Strategy (2024-06-08):
# - System prompts are explicit, structured, and role-specific.
# - All LLM completions use ModelRouter:
#     - 'reasoning' (deepseek-r1t-chimera) for conflict detection/resolution
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

class AgentState(BaseModel):
    """Base model for agent state."""
    model_config = ConfigDict(extra="ignore")

    agent_name: str
    timestamp: float = Field(default_factory=time.time)
    state_data: Dict[str, Any] = Field(default_factory=dict)

class StoryAgentState(AgentState):
    """State data from StoryAgent."""
    model_config = ConfigDict(extra="ignore")

    current_scene: Optional[str] = None
    narrative: Optional[str] = None
    discovered_clues: List[str] = Field(default_factory=list)

class SuspectAgentState(AgentState):
    """State data from SuspectAgent."""
    model_config = ConfigDict(extra="ignore")

    suspect_profiles: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    dialogue_history: Dict[str, List[str]] = Field(default_factory=dict)

class ClueAgentState(AgentState):
    """State data from ClueAgent."""
    model_config = ConfigDict(extra="ignore")

    clues: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    connections: List[Dict[str, str]] = Field(default_factory=list)

class BoardAgentState(AgentState):
    """State data from BoardAgent."""
    model_config = ConfigDict(extra="ignore")

    board_elements: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    visual_connections: List[Dict[str, str]] = Field(default_factory=list)

class ConflictResolution(BaseModel):
    """Model for conflict resolution."""
    model_config = ConfigDict(extra="ignore")

    conflict_type: str
    description: str
    resolution: str
    affected_agents: List[str]
    resolution_data: Dict[str, Any] = Field(default_factory=dict)

class CoordinatorInput(BaseModel):
    """Input for the CoordinatorAgent."""
    model_config = ConfigDict(extra="ignore")

    story_state: Optional[StoryAgentState] = None
    suspect_state: Optional[SuspectAgentState] = None
    clue_state: Optional[ClueAgentState] = None
    board_state: Optional[BoardAgentState] = None
    action: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)

class CoordinatorOutput(BaseModel):
    """Output from the CoordinatorAgent."""
    model_config = ConfigDict(extra="ignore")

    synchronized_state: Dict[str, Any]
    conflicts_resolved: List[ConflictResolution] = Field(default_factory=list)
    recommendations: Dict[str, Any] = Field(default_factory=dict)
    sources: List[str] = Field(default_factory=list)

class SynchronizationResult(BaseModel):
    """Result of a synchronization operation."""
    model_config = ConfigDict(extra="ignore")

    success: bool
    synchronized_state: Dict[str, Any]
    conflicts: List[Dict[str, Any]] = Field(default_factory=list)
    messages: List[str] = Field(default_factory=list)

class CoordinationInput(BaseModel):
    """Input model for coordinating agent interactions."""
    model_config = ConfigDict(extra="ignore")

    action: str
    player_profile: Optional[PsychologicalProfile] = Field(default_factory=create_default_profile)
    context: dict = Field(default_factory=dict)

# --- CoordinatorAgent Dependencies ---

class CoordinatorAgentDependencies:
    """Dependencies for the CoordinatorAgent PydanticAI agent."""
    def __init__(self, memory=None, use_mem0=True, user_id=None, mem0_config=None):
        self.memory = memory
        self.use_mem0 = use_mem0
        self.user_id = user_id
        self.mem0_config = mem0_config or {}
        self.agent_name = "CoordinatorAgent"

    def update_memory(self, key, value):
        """Update memory with key-value pair."""
        if self.use_mem0 and hasattr(self.memory, 'update'):
            self.memory.update(key, value)

    def search_memories(self, query, limit=3, threshold=0.7, rerank=True):
        """Search memories based on query."""
        if self.use_mem0 and hasattr(self.memory, 'search'):
            return self.memory.search(query, limit=limit, threshold=threshold, rerank=rerank)
        return []

# --- CoordinatorAgent Implementation ---

class CoordinatorAgent(BaseAgent):
    """Agent responsible for orchestrating inter-agent communication and maintaining global consistency."""
    def __init__(self, memory=None, use_mem0=True, user_id=None, mem0_config=None):
        super().__init__("CoordinatorAgent", memory, use_mem0=use_mem0, user_id=user_id, mem0_config=mem0_config)

        # Initialize ModelRouter for intelligent model selection
        self.model_router = ModelRouter()

        # Initialize PydanticAI agent
        self.pydantic_agent = self._create_pydantic_agent()
        self.dependencies = CoordinatorAgentDependencies(memory, use_mem0, user_id, mem0_config)

    def _create_pydantic_agent(self):
        """Create a PydanticAgent for coordination tasks"""
        agent = PydanticAgent(
            model="openai:gpt-3.5-turbo",  # Using a model that PydanticAI recognizes
            system_prompt="""You are an expert coordinator for mystery stories.
            Your task is to manage the flow of the investigation, ensuring that:
            - Player actions are properly handled
            - Story progression is logical and engaging
            - Clues and suspects are introduced at appropriate times
            - The mystery remains challenging but solvable""",
            allow_retries=True
        )
        return agent

    def synchronize(self, input_data: dict) -> dict:
        """
        Synchronize states from multiple agents and resolve conflicts.

        Args:
            input_data (dict): Should match CoordinatorInput

        Returns:
            dict: Output matching CoordinatorOutput
        """
        # Parse input using Pydantic
        parsed_input = CoordinatorInput(**input_data)

        # Store the synchronization request in Mem0 for future reference
        if self.use_mem0:
            self.update_memory(
                "sync_request",
                f"Synchronization requested at {time.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        start_time = time.time()

        # Collect all agent states into a single dictionary
        states = {}
        if parsed_input.story_state:
            states["story"] = parsed_input.story_state.model_dump()
        if parsed_input.suspect_state:
            states["suspect"] = parsed_input.suspect_state.model_dump()
        if parsed_input.clue_state:
            states["clue"] = parsed_input.clue_state.model_dump()
        if parsed_input.board_state:
            states["board"] = parsed_input.board_state.model_dump()

        # Add context if provided
        context = parsed_input.context or {}

        # Try using ModelRouter first
        try:
            # Use the LLM-based conflict detection and resolution
            conflicts = self._detect_conflicts(states)
            resolved_conflicts = []

            for conflict in conflicts:
                resolution = self._resolve_conflict(conflict, states)
                resolved_conflicts.append(resolution)

            # Apply resolutions to create synchronized state
            synchronized_state = self._apply_resolutions(states, resolved_conflicts)

            # Create the result
            result = SynchronizationResult(
                success=True,
                synchronized_state=synchronized_state,
                conflicts=[conflict for conflict in conflicts],
                messages=[f"Resolved conflict: {resolution.resolution}" for resolution in resolved_conflicts]
            )

            # If no conflicts were found, add a message
            if not conflicts:
                result.messages.append("No conflicts detected. States are already synchronized.")

            # If PydanticAI agent is needed as a fallback, uncomment this section
            # # Prepare the prompt for the agent
            # agent_prompt = (
            #     f"Synchronize the following agent states and resolve any conflicts:\n"
            #     f"- Story agent state: {'Present' if parsed_input.story_state else 'Not provided'}\n"
            #     f"- Suspect agent state: {'Present' if parsed_input.suspect_state else 'Not provided'}\n"
            #     f"- Clue agent state: {'Present' if parsed_input.clue_state else 'Not provided'}\n"
            #     f"- Board agent state: {'Present' if parsed_input.board_state else 'Not provided'}\n"
            # )
            #
            # if parsed_input.action:
            #     agent_prompt += f"\nLatest action: {parsed_input.action}\n"
            #
            # # Add any additional context
            # if context:
            #     agent_prompt += "\nAdditional context:\n"
            #     for key, value in context.items():
            #         agent_prompt += f"- {key}: {value}\n"
            #
            # # Run the agent synchronously
            # result = self.pydantic_agent.run_sync(
            #     agent_prompt,
            #     deps=self.dependencies,
            #     model_settings={"temperature": 0.5, "max_tokens": 1000}
            # )

            # Track performance metrics if enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                generation_time = time.time() - start_time
                self.update_memory("last_sync_time", f"{generation_time:.2f} seconds")

            return result.model_dump()

        except Exception as e:
            # Log the error
            error_msg = f"PydanticAI coordination error: {str(e)}"
            if self.use_mem0:
                self.update_memory("last_error", error_msg)

            # Fallback to traditional method
            conflicts = self._detect_conflicts(states)
            resolved_conflicts = []

            for conflict in conflicts:
                resolution = self._resolve_conflict(conflict, states)
                resolved_conflicts.append(resolution)

            # Apply resolutions to create synchronized state
            synchronized_state = self._apply_resolutions(states, resolved_conflicts)

            # Track performance metrics if enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                generation_time = time.time() - start_time
                self.update_memory("last_sync_time", f"{generation_time:.2f} seconds")

            return CoordinatorOutput(
                synchronized_state=synchronized_state,
                conflicts_resolved=resolved_conflicts,
                recommendations={},
                sources=[]
            ).model_dump()

    def _llm_detect_conflicts(self, states: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Use ModelRouter to detect conflicts between agent states.
        Uses deepseek-r1t-chimera for analytical reasoning.

        Args:
            states (Dict[str, Dict[str, Any]]): Dictionary of agent states

        Returns:
            List[Dict[str, Any]]: List of detected conflicts
        """
        import json

        # Format states for the prompt
        states_str = json.dumps(states, indent=2)

        # Create system prompt
        system_prompt = (
            "You are a coordination expert responsible for detecting conflicts between different agent states. "
            "Your task is to analyze the provided states and identify any inconsistencies, contradictions, "
            "or missing information that could cause problems in a multi-agent system. "
            "Focus on logical inconsistencies, data mismatches, and missing references between agents."
        )

        # Create user prompt
        user_prompt = (
            f"Analyze the following agent states and detect any conflicts or inconsistencies:\n\n"
            f"{states_str}\n\n"
            f"Return a list of conflicts in the following JSON format:\n"
            f"[\n"
            f"  {{\n"
            f"    \"type\": \"conflict_type\",\n"
            f"    \"description\": \"Description of the conflict\",\n"
            f"    \"affected_agents\": [\"agent1\", \"agent2\"],\n"
            f"    \"data\": {{\n"
            f"      \"relevant_field1\": \"value1\",\n"
            f"      \"relevant_field2\": \"value2\"\n"
            f"    }}\n"
            f"  }}\n"
            f"]\n"
            f"If no conflicts are found, return an empty list []."
        )

        # Prepare messages for the model
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            # Generate conflicts using the reasoning model
            response = self.model_router.complete(
                messages=messages,
                task_type="reasoning",  # Use deepseek-r1t-chimera for analytical reasoning
                temperature=0.3,  # Lower temperature for more consistent results
                max_tokens=1000
            )

            # Store the response in memory for debugging if tracking is enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                self.update_memory("conflict_detection_response", str(response.content)[:500])
                self.update_memory("conflict_detection_model", self.model_router.get_model_name_for_task("reasoning"))

            # Parse the response
            try:
                # Extract JSON from the response
                content = response.content
                # Find JSON array in the response
                start_idx = content.find("[")
                end_idx = content.rfind("]") + 1

                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    conflicts = json.loads(json_str)
                    return conflicts
                else:
                    # Fallback to traditional method if JSON parsing fails
                    if self.use_mem0:
                        self.update_memory("last_error", "Failed to parse conflicts from LLM response")
                    return self._detect_conflicts_traditional(states)
            except json.JSONDecodeError:
                # Fallback to traditional method if JSON parsing fails
                if self.use_mem0:
                    self.update_memory("last_error", "Failed to parse conflicts from LLM response")
                return self._detect_conflicts_traditional(states)

        except Exception as e:
            # Log the error
            error_msg = f"LLM conflict detection error: {str(e)}"
            if self.use_mem0:
                self.update_memory("last_error", error_msg)

            # Fallback to traditional method
            return self._detect_conflicts_traditional(states)

    def _detect_conflicts(self, states: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect conflicts between agent states.
        Uses ModelRouter for intelligent conflict detection.

        Args:
            states (Dict[str, Dict[str, Any]]): Dictionary of agent states

        Returns:
            List[Dict[str, Any]]: List of detected conflicts
        """
        # Use LLM-based conflict detection
        return self._llm_detect_conflicts(states)

    def _detect_conflicts_traditional(self, states: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Traditional rule-based method to detect conflicts between agent states.
        Used as a fallback if LLM-based detection fails.

        Args:
            states (Dict[str, Dict[str, Any]]): Dictionary of agent states

        Returns:
            List[Dict[str, Any]]: List of detected conflicts
        """
        conflicts = []

        # Check for conflicts between story and suspect states
        if "story" in states and "suspect" in states:
            story_state = states["story"]
            suspect_state = states["suspect"]

            # Check for suspect consistency
            if "suspect_states" in story_state.get("state_data", {}) and "suspect_profiles" in suspect_state:
                story_suspects = story_state["state_data"].get("suspect_states", {})
                suspect_profiles = suspect_state.get("suspect_profiles", {})

                # Check for suspects in story but not in profiles
                for suspect_id, suspect_data in story_suspects.items():
                    if suspect_id not in suspect_profiles:
                        conflicts.append({
                            "type": "missing_suspect",
                            "description": f"Suspect {suspect_id} exists in story but not in suspect profiles",
                            "affected_agents": ["story", "suspect"],
                            "data": {
                                "suspect_id": suspect_id,
                                "story_data": suspect_data
                            }
                        })

                # Check for inconsistent suspect data
                for suspect_id in set(story_suspects.keys()) & set(suspect_profiles.keys()):
                    story_suspect = story_suspects[suspect_id]
                    profile_suspect = suspect_profiles[suspect_id]

                    if story_suspect.get("name") != profile_suspect.get("name"):
                        conflicts.append({
                            "type": "inconsistent_suspect_name",
                            "description": f"Suspect {suspect_id} has different names in story and profiles",
                            "affected_agents": ["story", "suspect"],
                            "data": {
                                "suspect_id": suspect_id,
                                "story_name": story_suspect.get("name"),
                                "profile_name": profile_suspect.get("name")
                            }
                        })

        # Check for conflicts between story and clue states
        if "story" in states and "clue" in states:
            story_state = states["story"]
            clue_state = states["clue"]

            # Check for clue consistency
            if "discovered_clues" in story_state and "clues" in clue_state:
                discovered_clues = story_state.get("discovered_clues", [])
                clues = clue_state.get("clues", {})

                # Check for discovered clues not in clue database
                for clue_id in discovered_clues:
                    if clue_id not in clues:
                        conflicts.append({
                            "type": "missing_clue",
                            "description": f"Clue {clue_id} is discovered in story but not in clue database",
                            "affected_agents": ["story", "clue"],
                            "data": {
                                "clue_id": clue_id
                            }
                        })

        # Check for conflicts between clue and board states
        if "clue" in states and "board" in states:
            clue_state = states["clue"]
            board_state = states["board"]

            # Check for clue representation on board
            if "clues" in clue_state and "board_elements" in board_state:
                clues = clue_state.get("clues", {})
                board_elements = board_state.get("board_elements", {})

                # Check for clues not represented on board
                for clue_id, clue_data in clues.items():
                    found_on_board = False
                    for element_id, element_data in board_elements.items():
                        if element_data.get("type") == "clue" and element_data.get("clue_id") == clue_id:
                            found_on_board = True
                            break

                    if not found_on_board:
                        conflicts.append({
                            "type": "clue_not_on_board",
                            "description": f"Clue {clue_id} exists in clue database but not on board",
                            "affected_agents": ["clue", "board"],
                            "data": {
                                "clue_id": clue_id,
                                "clue_data": clue_data
                            }
                        })

        return conflicts

    def _llm_resolve_conflict(self, conflict: Dict[str, Any], states: Dict[str, Dict[str, Any]]) -> ConflictResolution:
        """
        Use ModelRouter to resolve a conflict between agent states.
        Uses deepseek-r1t-chimera for analytical reasoning.

        Args:
            conflict (Dict[str, Any]): Conflict to resolve
            states (Dict[str, Dict[str, Any]]): Dictionary of agent states

        Returns:
            ConflictResolution: Resolution for the conflict
        """
        import json

        # Format conflict and states for the prompt
        conflict_str = json.dumps(conflict, indent=2)
        states_str = json.dumps(states, indent=2)

        # Create system prompt
        system_prompt = (
            "You are a coordination expert responsible for resolving conflicts between different agent states. "
            "Your task is to analyze the provided conflict and agent states, then determine the best resolution "
            "that maintains consistency across the system. You should prioritize preserving the most important "
            "information while ensuring logical consistency."
        )

        # Create user prompt
        user_prompt = (
            f"Resolve the following conflict between agent states:\n\n"
            f"Conflict:\n{conflict_str}\n\n"
            f"Agent States:\n{states_str}\n\n"
            f"Return a resolution in the following JSON format:\n"
            f"{{\n"
            f"  \"conflict_type\": \"<type of conflict>\",\n"
            f"  \"description\": \"<description of the conflict>\",\n"
            f"  \"resolution\": \"<description of the resolution>\",\n"
            f"  \"affected_agents\": [\"<agent1>\", \"<agent2>\"],\n"
            f"  \"resolution_data\": {{\n"
            f"    \"action\": \"<action to take>\",\n"
            f"    \"<additional_field1>\": \"<value1>\",\n"
            f"    \"<additional_field2>\": \"<value2>\"\n"
            f"  }}\n"
            f"}}\n"
            f"The resolution_data should include all necessary information to implement the resolution."
        )

        # Prepare messages for the model
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            # Generate resolution using the reasoning model
            response = self.model_router.complete(
                messages=messages,
                task_type="reasoning",  # Use deepseek-r1t-chimera for analytical reasoning
                temperature=0.3,  # Lower temperature for more consistent results
                max_tokens=1000
            )

            # Store the response in memory for debugging if tracking is enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                self.update_memory("conflict_resolution_response", str(response.content)[:500])
                self.update_memory("conflict_resolution_model", self.model_router.get_model_name_for_task("reasoning"))

            # Parse the response
            try:
                # Extract JSON from the response
                content = response.content
                # Find JSON object in the response
                start_idx = content.find("{")
                end_idx = content.rfind("}") + 1

                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    resolution_data = json.loads(json_str)

                    # Create ConflictResolution object
                    return ConflictResolution(
                        conflict_type=resolution_data.get("conflict_type", conflict.get("type", "unknown")),
                        description=resolution_data.get("description", conflict.get("description", "")),
                        resolution=resolution_data.get("resolution", ""),
                        affected_agents=resolution_data.get("affected_agents", conflict.get("affected_agents", [])),
                        resolution_data=resolution_data.get("resolution_data", {})
                    )
                else:
                    # Fallback to traditional method if JSON parsing fails
                    if self.use_mem0:
                        self.update_memory("last_error", "Failed to parse resolution from LLM response")
                    return self._resolve_conflict_traditional(conflict, states)
            except json.JSONDecodeError:
                # Fallback to traditional method if JSON parsing fails
                if self.use_mem0:
                    self.update_memory("last_error", "Failed to parse resolution from LLM response")
                return self._resolve_conflict_traditional(conflict, states)

        except Exception as e:
            # Log the error
            error_msg = f"LLM conflict resolution error: {str(e)}"
            if self.use_mem0:
                self.update_memory("last_error", error_msg)

            # Fallback to traditional method
            return self._resolve_conflict_traditional(conflict, states)

    def _resolve_conflict(self, conflict: Dict[str, Any], states: Dict[str, Dict[str, Any]]) -> ConflictResolution:
        """
        Resolve a conflict between agent states.
        Uses ModelRouter for intelligent conflict resolution.

        Args:
            conflict (Dict[str, Any]): Conflict to resolve
            states (Dict[str, Dict[str, Any]]): Dictionary of agent states

        Returns:
            ConflictResolution: Resolution for the conflict
        """
        # Use LLM-based conflict resolution
        return self._llm_resolve_conflict(conflict, states)

    def _resolve_conflict_traditional(self, conflict: Dict[str, Any], states: Dict[str, Dict[str, Any]]) -> ConflictResolution:
        """
        Traditional rule-based method to resolve a conflict between agent states.
        Used as a fallback if LLM-based resolution fails.

        Args:
            conflict (Dict[str, Any]): Conflict to resolve
            states (Dict[str, Dict[str, Any]]): Dictionary of agent states

        Returns:
            ConflictResolution: Resolution for the conflict
        """
        conflict_type = conflict.get("type", "unknown")
        description = conflict.get("description", "")
        affected_agents = conflict.get("affected_agents", [])
        conflict_data = conflict.get("data", {})

        resolution_data = {}
        resolution = ""

        # Handle different conflict types
        if conflict_type == "missing_suspect":
            suspect_id = conflict_data.get("suspect_id")
            story_data = conflict_data.get("story_data", {})

            # Create a basic suspect profile based on story data
            resolution_data = {
                "action": "create_suspect_profile",
                "suspect_id": suspect_id,
                "profile": {
                    "name": story_data.get("name", f"Suspect {suspect_id}"),
                    "description": f"Auto-generated profile for {story_data.get('name', f'Suspect {suspect_id}')}",
                    "traits": story_data.get("traits", {}),
                    "background": "",
                    "motive": "",
                    "alibi": ""
                }
            }

            resolution = f"Created basic suspect profile for {story_data.get('name', f'Suspect {suspect_id}')}"

        elif conflict_type == "inconsistent_suspect_name":
            suspect_id = conflict_data.get("suspect_id")
            story_name = conflict_data.get("story_name")
            profile_name = conflict_data.get("profile_name")

            # Prefer the name from the story agent
            resolution_data = {
                "action": "update_suspect_profile",
                "suspect_id": suspect_id,
                "updates": {
                    "name": story_name
                }
            }

            resolution = f"Updated suspect name from '{profile_name}' to '{story_name}'"

        elif conflict_type == "missing_clue":
            clue_id = conflict_data.get("clue_id")

            # Create a placeholder clue
            resolution_data = {
                "action": "create_clue",
                "clue_id": clue_id,
                "clue": {
                    "name": f"Clue {clue_id}",
                    "description": f"Auto-generated clue for ID {clue_id}",
                    "type": "unknown",
                    "relevance": "unknown"
                }
            }

            resolution = f"Created placeholder clue for ID {clue_id}"

        elif conflict_type == "clue_not_on_board":
            clue_id = conflict_data.get("clue_id")
            clue_data = conflict_data.get("clue_data", {})

            # Create a board element for the clue
            element_id = f"element_{clue_id}"
            resolution_data = {
                "action": "create_board_element",
                "element_id": element_id,
                "element": {
                    "type": "clue",
                    "clue_id": clue_id,
                    "name": clue_data.get("name", f"Clue {clue_id}"),
                    "position": {"x": 100, "y": 100},  # Default position
                    "size": {"width": 150, "height": 100},  # Default size
                    "color": "#f0f0f0"  # Default color
                }
            }

            resolution = f"Added clue {clue_id} to the board"

        else:
            # Generic resolution for unknown conflict types
            resolution_data = {
                "action": "log_conflict",
                "conflict_type": conflict_type,
                "description": description
            }

            resolution = f"Logged unknown conflict type: {conflict_type}"

        return ConflictResolution(
            conflict_type=conflict_type,
            description=description,
            resolution=resolution,
            affected_agents=affected_agents,
            resolution_data=resolution_data
        )

    def _apply_resolutions(self, states: Dict[str, Dict[str, Any]], resolutions: List[ConflictResolution]) -> Dict[str, Any]:
        """
        Apply conflict resolutions to create a synchronized state.

        Args:
            states (Dict[str, Dict[str, Any]]): Dictionary of agent states
            resolutions (List[ConflictResolution]): List of conflict resolutions

        Returns:
            Dict[str, Any]: Synchronized state
        """
        # Create a deep copy of the states to avoid modifying the originals
        import copy
        synchronized_state = copy.deepcopy(states)

        # Apply each resolution
        for resolution in resolutions:
            action = resolution.resolution_data.get("action")

            if action == "create_suspect_profile":
                suspect_id = resolution.resolution_data.get("suspect_id")
                profile = resolution.resolution_data.get("profile", {})

                # Ensure suspect agent state exists
                if "suspect" not in synchronized_state:
                    synchronized_state["suspect"] = {"suspect_profiles": {}}
                elif "suspect_profiles" not in synchronized_state["suspect"]:
                    synchronized_state["suspect"]["suspect_profiles"] = {}

                # Add the profile
                synchronized_state["suspect"]["suspect_profiles"][suspect_id] = profile

            elif action == "update_suspect_profile":
                suspect_id = resolution.resolution_data.get("suspect_id")
                updates = resolution.resolution_data.get("updates", {})

                # Ensure suspect agent state exists
                if "suspect" in synchronized_state and "suspect_profiles" in synchronized_state["suspect"]:
                    if suspect_id in synchronized_state["suspect"]["suspect_profiles"]:
                        # Apply updates
                        synchronized_state["suspect"]["suspect_profiles"][suspect_id].update(updates)

            elif action == "create_clue":
                clue_id = resolution.resolution_data.get("clue_id")
                clue = resolution.resolution_data.get("clue", {})

                # Ensure clue agent state exists
                if "clue" not in synchronized_state:
                    synchronized_state["clue"] = {"clues": {}}
                elif "clues" not in synchronized_state["clue"]:
                    synchronized_state["clue"]["clues"] = {}

                # Add the clue
                synchronized_state["clue"]["clues"][clue_id] = clue

            elif action == "create_board_element":
                element_id = resolution.resolution_data.get("element_id")
                element = resolution.resolution_data.get("element", {})

                # Ensure board agent state exists
                if "board" not in synchronized_state:
                    synchronized_state["board"] = {"board_elements": {}}
                elif "board_elements" not in synchronized_state["board"]:
                    synchronized_state["board"]["board_elements"] = {}

                # Add the element
                synchronized_state["board"]["board_elements"][element_id] = element

        return synchronized_state

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

        try:
            # Construct the API request
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": api_key
            }
            params = {
                "q": query,
                "count": 5,
                "search_lang": "en"
            }

            # Make the request
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            # Parse the response
            data = response.json()
            results = []

            if "web" in data and "results" in data["web"]:
                for result in data["web"]["results"]:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("description", "")
                    })

            return results

        except Exception as e:
            if self.use_mem0:
                self.update_memory("last_error", f"Brave search error: {str(e)}")
            return []

    def _llm_recommend_actions(self, input_data: dict) -> dict:
        """
        Use ModelRouter to recommend actions for agents based on the current state.
        Uses deepseek-r1t-chimera for analytical reasoning.

        Args:
            input_data (dict): Should match CoordinatorInput

        Returns:
            dict: Recommendations for each agent
        """
        import json

        # Parse input using Pydantic
        parsed_input = CoordinatorInput(**input_data)

        # Collect all agent states into a single dictionary
        states = {}
        if parsed_input.story_state:
            states["story"] = parsed_input.story_state.model_dump()
        if parsed_input.suspect_state:
            states["suspect"] = parsed_input.suspect_state.model_dump()
        if parsed_input.clue_state:
            states["clue"] = parsed_input.clue_state.model_dump()
        if parsed_input.board_state:
            states["board"] = parsed_input.board_state.model_dump()

        # Format states for the prompt
        states_str = json.dumps(states, indent=2)

        # Add context if provided
        context = parsed_input.context or {}
        context_str = json.dumps(context, indent=2) if context else "No additional context provided."

        # Create system prompt
        system_prompt = (
            "You are a coordination expert responsible for recommending actions for multiple AI agents in a murder mystery game. "
            "Your task is to analyze the current state of each agent and recommend the most appropriate next actions "
            "that will advance the story, maintain consistency, and create an engaging experience for the player. "
            "Consider the relationships between agents and how their actions affect each other."
        )

        # Create user prompt
        user_prompt = (
            f"Based on the following agent states, recommend actions for each agent:\n\n"
            f"Agent States:\n{states_str}\n\n"
            f"Latest Action: {parsed_input.action or 'None'}\n\n"
            f"Additional Context:\n{context_str}\n\n"
            f"Return recommendations in the following JSON format:\n"
            f"{{\n"
            f"  \"recommendations\": {{\n"
            f"    \"story\": \"<recommended action for story agent>\",\n"
            f"    \"suspect\": \"<recommended action for suspect agent>\",\n"
            f"    \"clue\": \"<recommended action for clue agent>\",\n"
            f"    \"board\": \"<recommended action for board agent>\"\n"
            f"  }},\n"
            f"  \"reasoning\": \"<explanation of your recommendations>\",\n"
            f"  \"priority\": \"<which agent should act first>\"\n"
            f"}}\n"
        )

        # Prepare messages for the model
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            # Generate recommendations using the reasoning model
            response = self.model_router.complete(
                messages=messages,
                task_type="reasoning",  # Use deepseek-r1t-chimera for analytical reasoning
                temperature=0.5,  # Moderate temperature for creative but consistent results
                max_tokens=1000
            )

            # Store the response in memory for debugging if tracking is enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                self.update_memory("recommendation_response", str(response.content)[:500])
                self.update_memory("recommendation_model", self.model_router.get_model_name_for_task("reasoning"))

            # Parse the response
            try:
                # Extract JSON from the response
                content = response.content
                # Find JSON object in the response
                start_idx = content.find("{")
                end_idx = content.rfind("}") + 1

                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    recommendations = json.loads(json_str)
                    return recommendations
                else:
                    # Fallback to traditional method if JSON parsing fails
                    if self.use_mem0:
                        self.update_memory("last_error", "Failed to parse recommendations from LLM response")
                    return self._recommend_actions_traditional()
            except json.JSONDecodeError:
                # Fallback to traditional method if JSON parsing fails
                if self.use_mem0:
                    self.update_memory("last_error", "Failed to parse recommendations from LLM response")
                return self._recommend_actions_traditional()

        except Exception as e:
            # Log the error
            error_msg = f"LLM recommendation error: {str(e)}"
            if self.use_mem0:
                self.update_memory("last_error", error_msg)

            # Fallback to traditional method
            return self._recommend_actions_traditional()

    def _recommend_actions_traditional(self) -> dict:
        """
        Traditional rule-based method to recommend actions for agents.
        Used as a fallback if LLM-based recommendation fails.

        Returns:
            dict: Recommendations for each agent
        """
        return {
            "recommendations": {
                "story": "Continue narrative progression",
                "suspect": "Update suspect profiles",
                "clue": "Generate new clues",
                "board": "Synchronize with story state"
            },
            "reasoning": "Default recommendations based on standard mystery progression",
            "priority": "story"
        }

    def recommend_actions(self, input_data: dict) -> dict:
        """
        Recommend actions for agents based on the current state.
        Uses ModelRouter for intelligent action recommendations.

        Args:
            input_data (dict): Should match CoordinatorInput

        Returns:
            dict: Recommendations for each agent
        """
        # Parse input using Pydantic
        parsed_input = CoordinatorInput(**input_data)

        # Store the recommendation request in Mem0 for future reference
        if self.use_mem0:
            self.update_memory(
                "recommend_request",
                f"Recommendation requested at {time.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        start_time = time.time()

        # Try using LLM-based recommendation
        try:
            recommendations = self._llm_recommend_actions(input_data)

            # Track performance metrics if enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                generation_time = time.time() - start_time
                self.update_memory("last_recommend_time", f"{generation_time:.2f} seconds")

            return recommendations

        except Exception as e:
            # Log the error
            error_msg = f"Recommendation error: {str(e)}"
            if self.use_mem0:
                self.update_memory("last_error", error_msg)

            # Try using PydanticAI agent as a fallback
            try:
                # Prepare the prompt for the agent
                agent_prompt = (
                    f"Recommend actions for agents based on the current state:\n"
                    f"- Story agent state: {'Present' if parsed_input.story_state else 'Not provided'}\n"
                    f"- Suspect agent state: {'Present' if parsed_input.suspect_state else 'Not provided'}\n"
                    f"- Clue agent state: {'Present' if parsed_input.clue_state else 'Not provided'}\n"
                    f"- Board agent state: {'Present' if parsed_input.board_state else 'Not provided'}\n"
                )

                if parsed_input.action:
                    agent_prompt += f"\nLatest action: {parsed_input.action}\n"

                # Add any additional context
                context = parsed_input.context or {}
                if context:
                    agent_prompt += "\nAdditional context:\n"
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
                    self.update_memory("last_recommend_time", f"{generation_time:.2f} seconds")

                return result.model_dump()

            except Exception as e2:
                # Log the error
                error_msg = f"PydanticAI recommendation error: {str(e2)}"
                if self.use_mem0:
                    self.update_memory("last_error", error_msg)

                # Return a simple recommendation
                return self._recommend_actions_traditional()

    def _llm_coordinate_agents(self, action: str, context: dict) -> Dict[str, Any]:
        """Coordinate agent interactions based on player's psychological profile."""
        # Get psychological adaptations
        player_profile = context.get("player_profile", create_default_profile())
        adaptations = player_profile.get_narrative_adaptations()
        
        # Create prompt with psychological adaptations
        prompt = f"""
        Coordinate agent interactions based on:
        
        Action: {action}
        
        Psychological Adaptations:
        {json.dumps(adaptations, indent=2)}
        
        Requirements:
        1. Coordinate narrative flow based on player's cognitive style
        2. Adjust emotional content based on player's emotional tendency
        3. Match interaction pace to player's social style
        4. Ensure consistent psychological adaptation across all agents
        5. Maintain story coherence and engagement
        """
        
        # Use the model router to select appropriate model
        model = self.model_router.get_model_for_task("agent_coordination")
        
        try:
            response = model.generate(prompt)
            coordination_plan = json.loads(response.strip())
            return coordination_plan
        except Exception as e:
            print(f"Error coordinating agents: {str(e)}")
            return {
                "narrative_agent": {"action": "generate_narrative", "context": context},
                "suspect_agent": {"action": "generate_dialogue", "context": context},
                "clue_agent": {"action": "present_clue", "context": context},
                "board_agent": {"action": "update_board", "context": context}
            }
