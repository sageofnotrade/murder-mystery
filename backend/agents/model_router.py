"""
ModelRouter for the Murþrą application.
Routes requests to different models based on task type.
- Uses deepseek-r1t-chimera for reasoning/analysis tasks
- Uses mistral-nemo for writing/narrative tasks
"""

import os
from dotenv import load_dotenv
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.messages import ModelMessage
from typing import List, Dict, Any, Optional
import hashlib
import json
import redis
import logging

class ModelRouter:
    """
    A custom router that selects the appropriate model based on task type.
    - Uses deepseek-r1t-chimera for reasoning/analysis tasks
    - Uses mistral-nemo for writing/narrative tasks
    """
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenRouter base configuration
        self.api_base = os.getenv("LLM_API_BASE") or "https://openrouter.ai/api/v1"
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        
        # Debug print for API key (do not log in production)
        print("[DEBUG] OPENROUTER_API_KEY loaded:", self.api_key)
        
        if not self.api_key or self.api_key.strip() == "" or self.api_key.startswith("sk-" ) == False:
            raise ValueError("OPENROUTER_API_KEY environment variable is required and must be a valid key (starts with sk-)")
        
        # Set environment variable for OpenAI client
        os.environ["OPENAI_API_KEY"] = self.api_key
        
        # Create provider for OpenRouter with proper headers
        self.provider = OpenAIProvider(
            base_url=self.api_base,
            api_key=self.api_key
        )
        
        # Set headers after provider creation
        self.provider.headers = {
            "HTTP-Referer": "https://github.com/dallsszz/murder-mystery",  # Required by OpenRouter
            "X-Title": "Murder Mystery Game",  # Required by OpenRouter
            "Authorization": f"Bearer {self.api_key}",  # Required for authentication
            "Content-Type": "application/json",  # Required for API requests
            "OpenAI-Organization": "org-123",  # Required by OpenRouter
            "OpenAI-Project": "proj-123"  # Required by OpenRouter
        }
        
        # Set default parameters for OpenRouter
        self.provider.default_params = {
            "model": "deepseek/deepseek-r1-0528-qwen3-8b",  # Using DeepSeek model as default
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        # Initialize models with proper configuration
        self.reasoning_model = OpenAIModel(
            'mistralai/mistral-nemo',  # Using Mistral Nemo for reasoning
            provider=self.provider
        )
        
        self.writing_model = OpenAIModel(
            'mistralai/mistral-nemo',  # Using Mistral Nemo for writing
            provider=self.provider
        )
        
        # Set model routes after initialization
        self.reasoning_model.route = 'mistralai/mistral-nemo'  # OpenRouter route
        self.writing_model.route = 'mistralai/mistral-nemo'  # OpenRouter route
        
        # Default model (used when no specific task type is provided)
        self.default_model = self.reasoning_model
        
        # Redis setup (assumes REDIS_URL in env)
        REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client = redis.from_url(REDIS_URL)
        self.logger = logging.getLogger(__name__)
    
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
    
    def complete(self, messages: List[ModelMessage], task_type: str, **kwargs) -> Any:
        """
        Complete a prompt using the appropriate model for the task.
        Adds Redis caching for LLM responses.
        
        Args:
            messages (list): List of Message objects
            task_type (str): The type of task
            **kwargs: Additional arguments to pass to the model
            
        Returns:
            Response: The model response
        """
        model = self.get_model_for_task(task_type)
        
        # Set default parameters based on task type
        if task_type.lower() in ['reasoning', 'analysis', 'thinking', 'planning']:
            kwargs.setdefault('temperature', 0.3)  # Lower temperature for reasoning
            kwargs.setdefault('max_tokens', 1000)
        elif task_type.lower() in ['writing', 'narrative', 'content', 'story']:
            kwargs.setdefault('temperature', 0.7)  # Higher temperature for creative writing
            kwargs.setdefault('max_tokens', 2000)
        
        # --- Redis Caching Logic ---
        # Try to get user_id from kwargs or agent context
        user_id = kwargs.get('user_id')
        if not user_id:
            # Try to get from agent if passed
            agent = kwargs.get('agent')
            if agent and hasattr(agent, 'user_id'):
                user_id = agent.user_id
        # Serialize messages for hashing
        msg_str = json.dumps([m.model_dump() if hasattr(m, 'model_dump') else m.__dict__ for m in messages], sort_keys=True)
        key_base = f"llm:{user_id or ''}:{task_type}:{msg_str}"
        cache_key = hashlib.sha256(key_base.encode('utf-8')).hexdigest()
        redis_key = f"llm_cache:{cache_key}"
        # Check cache
        cached = self.redis_client.get(redis_key)
        if cached:
            self.logger.info(f"LLM cache hit for key {redis_key}")
            try:
                return json.loads(cached)
            except Exception:
                self.logger.warning(f"Corrupted cache for key {redis_key}, ignoring.")
        else:
            self.logger.info(f"LLM cache miss for key {redis_key}")
        # Call model and cache result
        result = model.complete(messages=messages, **kwargs)
        # Try to serialize result for cache
        try:
            result_json = result.model_dump() if hasattr(result, 'model_dump') else result.__dict__
            self.redis_client.set(redis_key, json.dumps(result_json), ex=3600)  # 1 hour expiry
        except Exception as e:
            self.logger.warning(f"Failed to cache LLM result: {e}")
        return result
    
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
            return "mistralai/mistral-nemo"
        elif model == self.writing_model:
            return "mistralai/mistral-nemo"
        else:
            return "unknown"
