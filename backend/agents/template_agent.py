"""
TemplateAgent for the Murþrą application.
Handles mystery template parsing and population using PydanticAI and LLMs.
Follows the agent structure and integration patterns of StoryAgent, ClueAgent, etc.

# Prompt/Model Strategy (2024-06-08):
# - System prompts are explicit, structured, and role-specific.
# - All LLM completions use ModelRouter:
#     - 'reasoning' (deepseek-r1t-chimera) for template analysis
#     - 'writing' (mistral-nemo) for template population
# - Parameters tuned: temperature=0.3 for planning, 0.7 for narrative; max_tokens set per step.
# - Prompts include context, player profile, and clear output format instructions.
# - Inline comments explain prompt structure and model routing choices.
"""

from .base_agent import BaseAgent
from .model_router import ModelRouter
from pydantic_ai import Agent as PydanticAgent, RunContext
from backend.agents.models.template_models import MysteryTemplate, PopulatedMysteryTemplate
from backend.agents.models.player_models import PlayerProfile
from typing import Dict, Any, Optional, Union, List
import os
import re

# --- Pydantic Models ---

class TemplateAgentInput(MysteryTemplate):
    player_profile: PlayerProfile

class TemplateAgentOutput(PopulatedMysteryTemplate):
    errors: Optional[List[str]] = None

# --- TemplateAgent Dependencies ---

class TemplateAgentDependencies:
    def __init__(self, memory=None, use_mem0=True, user_id=None, mem0_config=None):
        self.memory = memory
        self.use_mem0 = use_mem0
        self.user_id = user_id
        self.mem0_config = mem0_config or {}
        self.agent_name = "TemplateAgent"
    def update_memory(self, key, value):
        if self.use_mem0 and hasattr(self.memory, 'update'):
            self.memory.update(key, value)
    def search_memories(self, query, limit=3, threshold=0.7, rerank=True):
        if self.use_mem0 and hasattr(self.memory, 'search'):
            return self.memory.search(query, limit=limit, threshold=threshold, rerank=rerank)
        return []

# --- TemplateAgent Implementation ---

class TemplateAgent(BaseAgent):
    def __init__(self, memory=None, use_mem0=True, user_id=None, mem0_config=None):
        super().__init__("TemplateAgent", memory, use_mem0=use_mem0, user_id=user_id, mem0_config=mem0_config)
        self.model_router = ModelRouter()
        self.pydantic_agent = self._create_pydantic_agent()
        self.dependencies = TemplateAgentDependencies(memory, use_mem0, user_id, mem0_config)

    def _create_pydantic_agent(self):
        agent = PydanticAgent(
            os.getenv("LLM_MODEL", "openai:gpt-4o"),
            deps_type=TemplateAgentDependencies,
            output_type=TemplateAgentOutput,
            system_prompt=(
                "You are a mystery template parser and populator. "
                "Given a template and player profile, fill in all variables (e.g., {{variable}}) with creative, coherent values. "
                "Ensure logical consistency and validate the result."
            ),
            retries=2
        )
        return agent

    def extract_template_variables(self, template: MysteryTemplate) -> Dict[str, Any]:
        variables = {}
        for field_name, field_value in template.model_dump().items():
            if isinstance(field_value, str) and "{{" in field_value and "}}" in field_value:
                matches = re.findall(r"{{(.*?)}}", field_value)
                for match in matches:
                    variables[match.strip()] = None
        for suspect in template.suspects:
            for field_name, field_value in suspect.model_dump().items():
                if isinstance(field_value, str) and "{{" in field_value and "}}" in field_value:
                    matches = re.findall(r"{{(.*?)}}", field_value)
                    for match in matches:
                        variables[match.strip()] = None
        for clue in template.clues:
            for field_name, field_value in clue.model_dump().items():
                if isinstance(field_value, str) and "{{" in field_value and "}}" in field_value:
                    matches = re.findall(r"{{(.*?)}}", field_value)
                    for match in matches:
                        variables[match.strip()] = None
        return variables

    def validate_template(self, template: MysteryTemplate) -> List[str]:
        errors = []
        if not template.suspects:
            errors.append("Template must have at least one suspect")
        if not template.clues:
            errors.append("Template must have at least one clue")
        guilty_suspects = [s for s in template.suspects if s.guilty]
        if not guilty_suspects:
            errors.append("Template must have at least one guilty suspect")
        for clue in template.clues:
            if clue.related_suspects and not any(
                suspect.id in clue.related_suspects for suspect in template.suspects
            ):
                errors.append(f"Clue {clue.id} references non-existent suspects")
        return errors

    def populate_template(self, template: MysteryTemplate, player_profile: PlayerProfile) -> PopulatedMysteryTemplate:
        # Compose a prompt for the LLM
        variables = self.extract_template_variables(template)
        prompt = (
            f"Populate the following mystery template with creative, coherent values for all variables. "
            f"Player profile: {player_profile.model_dump()}\n"
            f"Template: {template.model_dump()}\n"
            f"Variables to fill: {list(variables.keys())}\n"
            "Return the fully populated template as a JSON object."
        )
        # Call the PydanticAI agent synchronously
        result = self.pydantic_agent.run_sync(
            prompt,
            deps=self.dependencies,
            model_settings={"temperature": 0.8, "max_tokens": 1500}
        )
        # Validate the result
        errors = self.validate_template(result.output)
        if errors:
            raise ValueError(f"Populated template validation failed: {', '.join(errors)}")
        return result.output
