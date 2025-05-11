"""
Base agent class for the Murþrą application.
This serves as a placeholder until the actual Archon MCP framework is integrated.
"""

class BaseAgent:
    """Base class for all agents in the system."""
    
    def __init__(self, name, memory=None):
        """Initialize the agent.
        
        Args:
            name (str): The name of the agent
            memory (dict, optional): The agent's memory. Defaults to None.
        """
        self.name = name
        self.memory = memory or {}
    
    def process(self, input_data):
        """Process input data and return a response.
        
        Args:
            input_data (dict): The input data to process
            
        Returns:
            dict: The processed response
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def update_memory(self, key, value):
        """Update the agent's memory.
        
        Args:
            key (str): The memory key
            value (any): The memory value
        """
        self.memory[key] = value
    
    def get_memory(self, key, default=None):
        """Get a value from the agent's memory.
        
        Args:
            key (str): The memory key
            default (any, optional): The default value if the key doesn't exist. Defaults to None.
            
        Returns:
            any: The memory value
        """
        return self.memory.get(key, default)
    
    def clear_memory(self):
        """Clear the agent's memory."""
        self.memory = {}
