"""
Base agent class with Mem0 integration for persistent memory.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Base agent class with Mem0 integration for persistent memory.
    
    Attributes:
        agent_name (str): Name of the agent
        use_mem0 (bool): Whether to use Mem0 for memory
        user_id (str): User ID for Mem0
        mem0_client: Mem0 client instance
    """
    
    def __init__(self, agent_name: str, memory=None, use_mem0: bool = False, user_id: Optional[str] = None, mem0_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base agent.
        
        Args:
            agent_name: Name of the agent
            memory: Optional memory object (for backward compatibility)
            use_mem0: Whether to use Mem0 for memory
            user_id: User ID for Mem0 (required if use_mem0 is True)
            mem0_config: Optional configuration for Mem0
        """
        if os.getenv("TEST_ENV"):
            self.agent_name = agent_name
            self.use_mem0 = False
            self.user_id = user_id
            self.mem0_client = None
            self.mem0_config = {}
            return
        
        self.agent_name = agent_name
        self.use_mem0 = use_mem0
        self.user_id = user_id
        self.mem0_client = None
        
        # Default Mem0 configuration
        self.mem0_config = {
            "search_limit": 5,           # Default number of memories to retrieve
            "search_threshold": 0.7,     # Default relevance threshold
            "rerank": True,             # Use reranking by default
            "store_summaries": True,    # Store summaries of generated content
            "track_performance": True,   # Track performance metrics
            "version": "v2"             # Use Mem0 API v2
        }
        
        # Update with user-provided config if any
        if mem0_config and isinstance(mem0_config, dict):
            self.mem0_config.update(mem0_config)
        
        # Initialize Mem0 if enabled
        if self.use_mem0:
            try:
                # Import Mem0 only if needed
                import mem0
                
                # Check for API key
                mem0_api_key = os.getenv("MEM0_API_KEY")
                if not mem0_api_key:
                    logger.warning("MEM0_API_KEY not found in environment variables. Disabling Mem0 integration.")
                    self.use_mem0 = False
                    return
                
                # Check for user ID
                if not self.user_id:
                    logger.warning("user_id is required for Mem0 integration. Disabling Mem0 integration.")
                    self.use_mem0 = False
                    return
                
                # Initialize Mem0 client
                self.mem0_client = mem0.MemoryClient(api_key=mem0_api_key)
                logger.info(f"Mem0 integration enabled for agent {agent_name} with user_id {user_id}")
                
                # Store agent initialization in memory if tracking is enabled
                if self.mem0_config.get("track_performance", True):
                    import time
                    self.update_memory("agent_initialized", f"{agent_name} initialized at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    self.update_memory("mem0_config", str(self.mem0_config))
                
            except ImportError:
                logger.warning("mem0 package not installed. Disabling Mem0 integration.")
                self.use_mem0 = False
        
        # After all assignments, force disable Mem0 in test env
        if os.getenv("TEST_ENV"):
            self.use_mem0 = False
            self.mem0_client = None
    
    def update_memory(self, key: str, value: str) -> bool:
        """
        Store or update a memory in Mem0.
        
        Args:
            key: Memory key/identifier
            value: Memory value/content
            
        Returns:
            bool: Success status
        """
        if not self.use_mem0 or not self.mem0_client:
            logger.warning("Mem0 integration is disabled. Memory not stored.")
            return False
        
        try:
            # Format the memory with key as a prefix for better retrieval
            memory = f"{key}: {value}"
            
            # Store the memory in Mem0
            # Note: Mem0 API expects 'messages' parameter for content
            self.mem0_client.add(
                messages=memory,
                user_id=self.user_id,
                output_format="v1.1",
                version="v2"
            )
            
            logger.info(f"Memory stored: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing memory: {str(e)}")
            return False
    
    def get_memory(self, key: str) -> Optional[str]:
        """
        Retrieve a memory from Mem0 by key.
        
        Args:
            key: Memory key/identifier
            
        Returns:
            str or None: Memory value if found, None otherwise
        """
        if not self.use_mem0 or not self.mem0_client:
            logger.warning("Mem0 integration is disabled. Cannot retrieve memory.")
            return None
        
        try:
            # Set up filters to retrieve memories for this specific user and key
            filters = {
                "AND": [
                    {
                        "user_id": self.user_id
                    }
                ]
            }
            
            # Search for the memory
            results = self.mem0_client.search(
                query=key,
                version=self.mem0_config.get("version", "v2"),
                filters=filters,
                output_format="v1.1",
                rerank=self.mem0_config.get("rerank", True)
            )
            
            # Process results based on format
            memory_results = results.get('results', []) if isinstance(results, dict) else results
            
            # Look for the memory with the matching key
            for result in memory_results:
                memory = result.get("memory", "")
                if memory.startswith(f"{key}:"):
                    # Extract the value part (after the colon and space)
                    value = memory[len(key) + 2:].strip()
                    return value
            
            logger.info(f"Memory not found: {key}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving memory: {str(e)}")
            return None
    
    def search_memories(self, query: str, limit: int = 5, threshold: float = 0.7, rerank: bool = True) -> List[Dict[str, Any]]:
        """
        Search for relevant memories in Mem0.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            threshold: Relevance threshold (0.0 to 1.0)
            rerank: Whether to use reranking to improve result relevance
            
        Returns:
            list: List of memory dictionaries with relevance scores
        """
        if not self.use_mem0 or not self.mem0_client:
            logger.warning("Mem0 integration is disabled. Cannot search memories.")
            return []
        
        try:
            # Set up filters to retrieve memories for this specific user
            filters = {
                "AND": [
                    {
                        "user_id": self.user_id
                    }
                ]
            }
            
            # Search for relevant memories with reranking for better relevance
            results = self.mem0_client.search(
                query=query,
                version="v2",
                filters=filters,
                limit=limit,
                threshold=threshold,
                output_format="v1.1",
                rerank=rerank
            )
            
            # Process results based on format
            if isinstance(results, dict):
                memory_results = results.get('results', [])
                logger.info(f"Found {len(memory_results)} memories for query: {query}")
                return memory_results
            else:
                logger.info(f"Found {len(results)} memories for query: {query}")
                return results
            
        except Exception as e:
            logger.error(f"Error searching memories: {str(e)}")
            return []
    
    def clear_memories(self) -> bool:
        """
        Clear all memories for the current user.
        
        Returns:
            bool: Success status
        """
        if not self.use_mem0 or not self.mem0_client:
            logger.warning("Mem0 integration is disabled. Cannot clear memories.")
            return False
        
        try:
            # Set up filters to retrieve memories for this specific user
            filters = {
                "AND": [
                    {
                        "user_id": self.user_id
                    }
                ]
            }
            
            # Delete all memories for this user
            self.mem0_client.delete(
                filters=filters,
                version=self.mem0_config.get("version", "v2")
            )
            
            # Log the memory clearing operation
            logger.info(f"Cleared all memories for user: {self.user_id}")
            
            # Track the clearing operation if performance tracking is enabled
            if self.mem0_config.get("track_performance", True):
                import time
                self.update_memory("memories_cleared", f"All memories cleared at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return True
            
        except Exception as e:
            error_msg = f"Error clearing memories: {str(e)}"
            logger.error(error_msg)
            
            # Track the error if performance tracking is enabled
            if self.mem0_config.get("track_performance", True):
                self.update_memory("memory_clear_error", error_msg)
                
            return False