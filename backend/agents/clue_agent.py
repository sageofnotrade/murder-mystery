"""
ClueAgent for the Murþrą application.
Handles clue generation and updates using web search and LLMs.
Enhanced with PydanticAI for better type safety and agent capabilities.
Uses ModelRouter to select appropriate models for different tasks:
- deepseek-r1t-chimera for reasoning/analysis
- mistral-nemo for writing/narrative

# Prompt/Model Strategy (2024-06-08):
# - System prompts are explicit, structured, and role-specific.
# - All LLM completions use ModelRouter:
#     - 'reasoning' (deepseek-r1t-chimera) for clue analysis
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
    type: Optional[str] = None

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

class CluePresentationInput(BaseModel):
    """Input model for presenting clues."""
    model_config = ConfigDict(extra="ignore")

    clue: str
    player_profile: Optional[PsychologicalProfile] = Field(default_factory=create_default_profile)
    context: dict = Field(default_factory=dict)

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
    def __init__(self, memory=None, use_mem0=True, user_id=None, mem0_config=None, model_message_cls=None):
        super().__init__("ClueAgent", memory, use_mem0=use_mem0, user_id=user_id, mem0_config=mem0_config)

        # Initialize ModelRouter for intelligent model selection
        self.model_router = ModelRouter()

        # Always set to a concrete class, never a Union
        if model_message_cls is not None and not isinstance(model_message_cls, type):
            raise ValueError("model_message_cls must be a class, not a Union or instance")
        self.model_message_cls = model_message_cls or ModelMessage

        # Initialize PydanticAI agent
        self.pydantic_agent = self._create_pydantic_agent()
        self.dependencies = ClueAgentDependencies(self.mem0_client, use_mem0, user_id, mem0_config)

    def _create_pydantic_agent(self):
        """Create and configure the PydanticAI agent."""
        # Use the model router to get the appropriate model
        model = self.model_router.get_model_for_task("reasoning")  # Using reasoning model for clue analysis
        agent = PydanticAgent(
            model=model,  # Use the model from the router
            deps_type=ClueAgentDependencies,
            output_type=ClueGenerateOutput,  # Use only ClueGenerateOutput
            system_prompt=(
                "You are a forensic expert helping with a detective investigation. "
                "Create detailed descriptions of clues based on given prompts. "
                "Include physical characteristics, potential significance, and possible connections to the case. "
                "Be precise, analytical, and consider all possible interpretations of the evidence."
            ),
            retries=2  # Allow retries for better error handling
        )
        @agent.tool
        async def brave_search(ctx: RunContext[ClueAgentDependencies], query: str) -> list[dict]:
            """Search the web for information related to the query."""
            return self._brave_search(query)

        @agent.tool
        async def generate_clue_data(ctx, prompt: str, context: dict = None, search_results: list[dict] = None, memory_context: str = "") -> ClueData:
            search_results = search_results or self._brave_search(prompt)
            return self._llm_generate_clue_data(prompt, context or {}, search_results, memory_context)

        @agent.tool
        async def search_memories(ctx, query: str, limit: int = 3, threshold: float = 0.7, rerank: bool = True) -> list[dict]:
            if ctx.deps.use_mem0:
                return self.mem0_client.search(query, limit, threshold, rerank)
            return []

        @agent.tool
        async def update_memory(ctx, key: str, value: str) -> None:
            if ctx.deps.use_mem0:
                self.mem0_client.update(key, value)
        """Create a PydanticAgent for clue generation"""
        # Use the model router to get the appropriate model
        model = self.model_router.get_model_for_task("reasoning")  # Using reasoning model for clue analysis
        
        agent = PydanticAgent(
            model=model,  # Use the model from the router
            system_prompt="""You are an expert detective and clue analyst for a murder mystery game.
                Your task is to analyze and generate clues that are:
                1. Relevant to the mystery
                2. Detailed and specific
                3. Potentially misleading but fair
                4. Consistent with the story's tone and setting

                You MUST respond with a valid JSON object containing the following fields:
                - description: A brief description of the clue
                - details: Detailed analysis of the clue's significance
                - significance: How this clue relates to the mystery
                - related_clues: List of other clues this connects to
                - confidence_level: A number from 1-10 indicating how confident you are in this clue's relevance

                Example response format:
                {
                    "description": "A blood-stained handkerchief with embroidered initials",
                    "details": "The handkerchief appears to be made of fine silk, suggesting it belonged to someone of high social standing. The blood stains are fresh and the embroidery shows the initials 'L.B.'",
                    "significance": "This could link to Lady Blackwood, who was known to carry such handkerchiefs. The blood suggests it was used to clean up after the murder.",
                    "related_clues": ["The broken window", "Footprints in the garden"],
                    "confidence_level": 8
                }

                Remember: Your response MUST be a valid JSON object matching this format exactly.""",
            allow_retries=True
        )
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
            self.mem0_client.update("clue_prompt", prompt)
            if context:
                self.mem0_client.update("clue_context", str(context))
        try:
            # Prepare the prompt for the agent
            agent_prompt = f"""Analyze the following clue in the context of a murder mystery:

Location: {context.get('location', 'Unknown')}
Crime Scene: {context.get('crime_scene', 'Unknown')}
Existing Clues: {', '.join(context.get('existing_clues', []))}

Generate a new clue that fits this context. Your response MUST be a valid JSON object with the following structure:
{{
    "description": "A brief description of the clue",
    "details": "Detailed analysis of the clue's significance",
    "significance": "How this clue relates to the mystery",
    "related_clues": ["List", "of", "related", "clues"],
    "confidence_level": 8
}}

Remember: Your response MUST be a valid JSON object matching this format exactly."""

            # Run the agent synchronously
            result = self.pydantic_agent.run_sync(
                agent_prompt,
                deps=self.dependencies,
                model_settings={
                    "temperature": 0.7,
                    "max_tokens": 1000,
                    "response_format": {"type": "json_object"}
                }
            )

            # DEBUG: Print the raw LLM output
            print("[DEBUG] ClueAgent raw LLM output:", repr(getattr(result, 'output', None)))

            # Extract the clue from the result
            if hasattr(result, 'output'):
                try:
                    # Try to parse the output as JSON
                    if isinstance(result.output, str):
                        # Clean up the string before parsing
                        json_str = result.output.strip()
                        # Remove any trailing commas
                        json_str = json_str.rstrip(',')
                        clue_data = json.loads(json_str)
                    else:
                        clue_data = result.output

                    # If the clue is a ClueGenerateOutput, use it directly
                    if isinstance(clue_data, ClueGenerateOutput):
                        return clue_data
                    # If the clue is a dict, wrap it in ClueData and ClueGenerateOutput
                    if isinstance(clue_data, dict):
                        # If the description is a dict (e.g., context), fix it
                        if isinstance(clue_data.get('description'), dict):
                            clue_data['description'] = f"Clue: {prompt} (context: {context})"
                            clue_data['details'] = "No valid clue could be generated."
                        clue_data = ClueData(
                            description=clue_data.get('description', str(prompt)),
                            details=clue_data.get('details', "No details available."),
                            significance=clue_data.get('significance'),
                            related_to=clue_data.get('related_to', []),
                            confidence=clue_data.get('confidence'),
                            type="unknown"
                        )
                        return ClueGenerateOutput(clue=clue_data, sources=[r['url'] for r in search_results])
                    # If the clue is already a ClueData, wrap it
                    if isinstance(clue_data, ClueData):
                        return ClueGenerateOutput(clue=clue_data, sources=[r['url'] for r in search_results])
                    # Otherwise, fallback
                    return ClueGenerateOutput(
                        clue=ClueData(
                            description=str(prompt),
                            details="No valid clue could be generated.",
                            significance=None,
                            related_to=[],
                            confidence=None,
                            type="unknown"
                        ),
                        sources=[r['url'] for r in search_results]
                    )
                except (json.JSONDecodeError, AttributeError) as e:
                    print(f"[DEBUG] ClueAgent exception in JSON parsing: {e}")
                    print(f"[DEBUG] ClueAgent raw JSON string: {repr(result.output)}")
                    # Fall back to the original clue data
                    if hasattr(result.output, 'clue'):
                        if isinstance(result.output, ClueGenerateOutput):
                            clue_data = result.output.clue
                            return ClueOutput(clue=clue_data, sources=[])
                        else:
                            return ClueOutput(clue=result.output.clue, sources=[])

        except Exception as e:
            print(f"[DEBUG] ClueAgent exception in LLM call: {e}")
            result = None

        # Fallback to traditional method if PydanticAI fails or output is invalid
        print("[DEBUG] ClueAgent fallback path triggered. Result output:", repr(getattr(result, 'output', None)))
        search_results = self._brave_search(prompt)
        clue = self._llm_generate_clue(prompt, context, search_results)

        # If the clue is a ClueGenerateOutput, use it directly
        if isinstance(clue, ClueGenerateOutput):
            return clue
        # If the clue is a dict, wrap it in ClueData and ClueGenerateOutput
        if isinstance(clue, dict):
            # If the description is a dict (e.g., context), fix it
            if isinstance(clue.get('description'), dict):
                clue['description'] = f"Clue: {prompt} (context: {context})"
                clue['details'] = "No valid clue could be generated."
            clue_data = ClueData(
                description=clue.get('description', str(prompt)),
                details=clue.get('details', "No details available."),
                significance=clue.get('significance'),
                related_to=clue.get('related_to', []),
                confidence=clue.get('confidence'),
                type="unknown"
            )
            return ClueGenerateOutput(clue=clue_data, sources=[r['url'] for r in search_results])
        # If the clue is already a ClueData, wrap it
        if isinstance(clue, ClueData):
            return ClueGenerateOutput(clue=clue, sources=[r['url'] for r in search_results])
        # Otherwise, fallback
        return ClueGenerateOutput(
            clue=ClueData(
                description=str(prompt),
                details="No valid clue could be generated.",
                significance=None,
                related_to=[],
                confidence=None,
                type="unknown"
            ),
            sources=[r['url'] for r in search_results]
        )

    def _brave_search(self, query: str) -> list[dict]:
        load_dotenv()
        api_key = os.getenv("BRAVE_API_KEY")

        if not api_key:
            if self.mem0_client is not None:
                self.mem0_client.update("last_error", "Missing Brave API key")
            return []

        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {"Accept": "application/json", "X-Subscription-Token": api_key}
        params = {"q": query, "count": 5, "freshness": "month"}

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            self.mem0_client.update("last_search_response", data)
            results = [
                {
                    "title": r["title"],
                    "url": r["url"],
                    "snippet": r.get("description", ""),
                    "source": r.get("source", "")
                }
                for r in data.get("web", {}).get("results", [])
            ]
            self.mem0_client.update("last_search_count", len(results))
            return results
        except Exception as e:
            self.mem0_client.update("last_error", f"Brave Search API error: {str(e)}")
            return []

    def _llm_generate_clue_data(self, prompt: str, context: dict, search_results: list[dict], memory_context: str = "") -> ClueData:
        """
        Generate a clue using the ModelRouter.
        Uses deepseek-r1t-chimera for analytical reasoning about clues.

        Args:
            prompt (str): Description of the clue to analyze.
            context (dict): Context for the clue generation.
            search_results (list[dict]): Search results to enhance the clue generation.
            memory_context (str): Optional context from memory.

        Returns:
            ClueData: The generated clue data.
        """
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
            user_prompt = f"""Analyze the following clue in the context of a murder mystery:

Location: {context.get('location', 'Unknown')}
Crime Scene: {context.get('crime_scene', 'Unknown')}
Existing Clues: {', '.join(context.get('existing_clues', []))}

Generate a new clue that fits this context. Your response MUST be a valid JSON object with the following structure:
{{
    "description": "A brief description of the clue",
    "details": "Detailed analysis of the clue's significance",
    "significance": "How this clue relates to the mystery",
    "related_clues": ["List", "of", "related", "clues"],
    "confidence_level": 8
}}

Remember: Your response MUST be a valid JSON object matching this format exactly."""

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
            print(f"[DEBUG] model_message_cls type in _llm_generate_clue: {type(self.model_message_cls)}")
            messages = [
                self.model_message_cls(role="system", content=system_prompt),
                self.model_message_cls(role="user", content=user_prompt)
            ]

            # Generate the clue using the reasoning model via ModelRouter
            response = self.model_router.complete(
                messages=messages,
                task_type="reasoning",  # Use deepseek-r1t-chimera for analytical reasoning
                temperature=0.7,
                max_tokens=800
            )

            print("[DEBUG] ClueAgent response.content:", repr(response.content))

            # Store the response in memory for debugging if tracking is enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                self.mem0_client.update("last_llm_response", str(response)[:500])
                self.mem0_client.update("clue_analysis_model", self.model_router.get_model_name_for_task("reasoning"))
            content = response.content
            if not content:
                if self.use_mem0:
                    self.mem0_client.update("last_error", "Empty response from LLM")
                return ClueData(
                    description=prompt or "Unknown Clue",
                    details="Analysis pending.",
                    type="unknown"
                )

            # Try to parse structured data from the response
            try:
                # Look for JSON-like content in the response
                if "{" in content and "}" in content:
                    json_str = content[content.find("{"):content.rfind("}")+1]
                    clue_dict = json.loads(json_str)
                    print("[DEBUG] ClueAgent parsed clue_dict:", clue_dict)

                    # Create a ClueData object from the parsed JSON
                    try:
                        result = ClueData(
                            description=clue_dict.get("description", prompt),
                            details=clue_dict.get("details", "Unable to analyze this clue at the moment."),
                            significance=clue_dict.get("significance"),
                            related_to=clue_dict.get("related_to", []),
                            confidence=clue_dict.get("confidence"),
                            type="unknown",
                            **{k: v for k, v in clue_dict.items() if k not in ["description", "details", "significance", "related_to", "confidence"]}
                        )
                        return result
                    except Exception:
                        raise
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
                details=details,
                type="unknown"
            )

        except Exception as e:
            error_msg = f"PydanticAI clue model error: {str(e)}"
            if self.use_mem0:
                self.mem0_client.update("last_error", error_msg)
            return ClueData(
                description=prompt or "Unknown Clue",
                details="Unable to analyze this clue at the moment.",
                type="unknown"
            )

    def _llm_generate_clue(self, prompt: str, context: dict, search_results: list[dict]) -> dict:
        """
        Generate a clue using the ModelRouter.
        Uses deepseek-r1t-chimera for analytical reasoning about clues.
        Legacy method for backward compatibility.
        """
        import json

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
        user_prompt = f"""Analyze the following clue in the context of a murder mystery:

Location: {context.get('location', 'Unknown')}
Crime Scene: {context.get('crime_scene', 'Unknown')}
Existing Clues: {', '.join(context.get('existing_clues', []))}

Generate a new clue that fits this context. Your response MUST be a valid JSON object with the following structure:
{{
    "description": "A brief description of the clue",
    "details": "Detailed analysis of the clue's significance",
    "significance": "How this clue relates to the mystery",
    "related_clues": ["List", "of", "related", "clues"],
    "confidence_level": 8
}}

Remember: Your response MUST be a valid JSON object matching this format exactly."""

        # Add context if provided
        if context:
            user_prompt += "\nCase context:\n"
            for key, value in context.items():
                user_prompt += f"- {key}: {value}\n"

        # Add search results
        user_prompt += search_context

        # Prepare messages for the model
        print(f"[DEBUG] model_message_cls type in _llm_generate_clue: {type(self.model_message_cls)}")
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            # Generate the clue using the reasoning model via ModelRouter
            response = self.model_router.complete(
                messages=messages,
                task_type="reasoning",  # Use deepseek-r1t-chimera for analytical reasoning
                temperature=0.7,
                max_tokens=800
            )

            # Store the response in memory for debugging if tracking is enabled
            if self.use_mem0 and self.mem0_config.get("track_performance", True):
                self.mem0_client.update("last_llm_response", str(response)[:500])
                self.mem0_client.update("clue_generation_model", self.model_router.get_model_name_for_task("reasoning"))
            content = response.content
            if not content:
                self.mem0_client.update("last_error", "Empty response from LLM")
                return ClueGenerateOutput(
                    clue=ClueData(
                        description=str(prompt),
                        details=str(e),
                        significance=None,
                        related_to=[],
                        confidence=None,
                        type="unknown"
                    ),
                    sources=[]
                )

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
            return ClueGenerateOutput(
                clue=ClueData(
                    description=str(prompt),
                    details=str(e),
                    significance=None,
                    related_to=[],
                    confidence=None,
                    type="unknown"
                ),
                sources=[]
            )

        except Exception as e:
            if self.mem0_client is not None:
                self.mem0_client.update("last_error", f"ModelRouter error: {str(e)}")
            return ClueGenerateOutput(
                clue=ClueData(
                    description=str(prompt),
                    details=str(e),
                    significance=None,
                    related_to=[],
                    confidence=None,
                    type="unknown"
                ),
                sources=[]
            )

    def _llm_present_clue(self, clue: str, context: dict) -> str:
        """Present a clue in a way that matches the player's cognitive style."""
        # Get psychological adaptations
        player_profile = context.get("player_profile", create_default_profile())
        adaptations = player_profile.get_narrative_adaptations()
        
        # Create prompt with psychological adaptations
        prompt = f"""
        Present this clue in a way that matches the player's cognitive style:
        
        Clue: {clue}
        
        Psychological Adaptations:
        {json.dumps(adaptations, indent=2)}
        
        Requirements:
        1. Adapt clue presentation based on player's cognitive style
        2. For analytical players: Focus on logical connections and details
        3. For intuitive players: Emphasize patterns and implications
        4. Adjust complexity based on player's cognitive style
        5. Maintain mystery and engagement
        """
        
        # Use the model router to select appropriate model
        model = self.model_router.get_model_for_task("clue_presentation")
        
        try:
            response = model.generate(prompt)
            return response.strip()
        except Exception as e:
            print(f"Error presenting clue: {str(e)}")
            return f"You notice: {clue}"

    def analyze_clue(self, clue_data: dict, context: dict = None) -> dict:
        """Analyze a clue for deeper insights."""
        context = context or {}
        try:
            # Use the model router to analyze the clue
            result = self._llm_analyze_clue("Analyze this clue", clue_data, context)
            return result
        except Exception as e:
            return {
                "forensic_details": f"Error analyzing clue: {str(e)}",
                "connections": [],
                "significance": 0,
                "reliability": 0.0,
                "next_steps": []
            }

    def _llm_analyze_clue(self, prompt: str, clue_data: dict, context: dict = None) -> dict:
        """LLM-based clue analysis."""
        context = context or {}
        try:
            messages = [
                self.model_message_cls(role="system", content="You are a forensic analyst. Analyze the clue and provide forensic details, connections, significance, reliability, and next steps as JSON."),
                self.model_message_cls(role="user", content=f"Clue: {json.dumps(clue_data)}\nContext: {json.dumps(context)}")
            ]
            response = self.model_router.complete(
                messages=messages,
                task_type="reasoning",
                temperature=0.5,
                max_tokens=600
            )
            content = response.content
            if content and "{" in content and "}" in content:
                json_str = content[content.find("{"):content.rfind("}")+1]
                return json.loads(json_str)
            return {
                "forensic_details": content or "No details.",
                "connections": [],
                "significance": 0,
                "reliability": 0.0,
                "next_steps": []
            }
        except Exception as e:
            return {
                "forensic_details": f"Error analyzing clue: {str(e)}",
                "connections": [],
                "significance": 0,
                "reliability": 0.0,
                "next_steps": []
            }

    def find_connections(self, clues: list, context: dict = None) -> dict:
        """Find connections between clues."""
        context = context or {}
        try:
            result = self._llm_find_connections(clues, context)
            return result
        except Exception as e:
            return {
                "connections": [],
                "patterns": [],
                "contradictions": [],
                "timeline_implications": [],
                "error": f"Error finding connections: {str(e)}"
            }

    def _llm_find_connections(self, clues: list, context: dict = None) -> dict:
        """LLM-based connection finding between clues."""
        context = context or {}
        try:
            messages = [
                self.model_message_cls(role="system", content="You are a detective. Find connections, patterns, contradictions, and timeline implications between the provided clues. Respond as JSON."),
                self.model_message_cls(role="user", content=f"Clues: {json.dumps(clues)}\nContext: {json.dumps(context)}")
            ]
            response = self.model_router.complete(
                messages=messages,
                task_type="reasoning",
                temperature=0.5,
                max_tokens=800
            )
            content = response.content
            if content and "{" in content and "}" in content:
                json_str = content[content.find("{"):content.rfind("}")+1]
                return json.loads(json_str)
            return {
                "connections": [],
                "patterns": [],
                "contradictions": [],
                "timeline_implications": []
            }
        except Exception as e:
            return {
                "connections": [],
                "patterns": [],
                "contradictions": [],
                "timeline_implications": [],
                "error": f"Error finding connections: {str(e)}"
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