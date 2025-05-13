"""
ModelRouter for the Murþrą application.
Routes requests to different models based on task type.
- Uses deepseek-rit-chimera for reasoning/analysis tasks
- Uses mistral-nemo for writing/narrative tasks
"""

import os
from dotenv import load_dotenv
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.messages import Message
from typing import List, Dict, Any, Optional

class ModelRouter:
    """
    A custom router that selects the appropriate model based on task type.
    - Uses deepseek-rit-chimera for reasoning/analysis tasks
    - Uses mistral-nemo for writing/narrative tasks
    """
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenRouter base configuration
        self.api_base = os.getenv("LLM_API_BASE") or "https://openrouter.ai/api/v1"
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        
        # Create provider for OpenRouter
        self.provider = OpenAIProvider(
            base_url=self.api_base,
            api_key=self.api_key,
        )
        
        # Initialize models
        self.reasoning_model = OpenAIModel(
            'tngtech/deepseek-rit-chimera:free',
            provider=self.provider,
        )
        
        self.writing_model = OpenAIModel(
            'mistralai/mistral-nemo:free',
            provider=self.provider,
        )
        
        # Default model (used when no specific task type is provided)
        self.default_model = self.reasoning_model
    
    def get_model_for_task(self, task_type: str) -> OpenAIModel:
        """
        Returns the appropriate model based on the task type.
        
        Args:
            task_type (str): The type of task ('reasoning', 'analysis', 'thinking', 'planning', 'writing', etc.)
            
        Returns:
            OpenAIModel: The appropriate PydanticAI model
        """
        if task_type.lower() in ['reasoning', 'analysis', 'thinking', 'planning']:
            return self.reasoning_model
        elif task_type.lower() in ['writing', 'narrative', 'content', 'story']:
            return self.writing_model
        else:
            # Default to reasoning model for unknown tasks
            return self.default_model
    
    def complete(self, messages: List[Message], task_type: str, **kwargs) -> Any:
        """
        Complete a prompt using the appropriate model for the task.
        
        Args:
            messages (list): List of Message objects
            task_type (str): The type of task
            **kwargs: Additional arguments to pass to the model
            
        Returns:
            Response: The model response
        """
        model = self.get_model_for_task(task_type)
        return model.complete(messages=messages, **kwargs)
    
    def get_model_name_for_task(self, task_type: str) -> str:
        """
        Returns the name of the model that would be used for the given task type.
        Useful for logging and debugging.
        
        Args:
            task_type (str): The type of task
            
        Returns:
            str: The name of the model
        """
        model = self.get_model_for_task(task_type)
        if model == self.reasoning_model:
            return "deepseek-rit-chimera"
        elif model == self.writing_model:
            return "mistral-nemo"
        else:
            return "unknown"
