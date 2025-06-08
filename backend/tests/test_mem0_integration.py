"""
Tests for Mem0 integration in the BaseAgent and StoryAgent classes.
"""

import os
import unittest
from unittest import skip
from dotenv import load_dotenv
import unittest.mock

from backend.agents.base_agent import BaseAgent
from backend.agents.story_agent import StoryAgent

# Load environment variables
load_dotenv()

# Helper function to skip tests if Mem0 is not available
def skip_if_no_mem0(func):
    """Decorator to skip tests if Mem0 API key is not available."""
    mem0_api_key = os.getenv("MEM0_API_KEY")
    return skip("MEM0_API_KEY not found in environment variables")(func) if not mem0_api_key else func

class TestMem0Integration(unittest.TestCase):
    def setUp(self):
        # Patch environment variables for Mem0 and LLM
        self.env_patcher = unittest.mock.patch.dict(os.environ, {
            "MEM0_API_KEY": "test_key",
            "LLM_MODEL": "gpt-3.5-turbo",
            "OPENAI_API_KEY": "test_key"
        })
        self.env_patcher.start()
        # Patch mem0.MemoryClient with a mock
        self.mem0_patcher = unittest.mock.patch("mem0.MemoryClient", new=self.MockMemoryClient)
        self.mem0_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()
        self.mem0_patcher.stop()

    class MockMemoryClient:
        _memories = []  # class variable shared across all instances
        def __init__(self, *args, **kwargs):
            pass
        def add(self, messages, user_id, output_format=None, version=None):
            self.__class__._memories.append({"memory": messages, "user_id": user_id})
        def search(self, query, version=None, filters=None, output_format=None, rerank=None, limit=None, threshold=None):
            user_id = None
            if filters and isinstance(filters, dict):
                for cond in filters.get("AND", []):
                    if "user_id" in cond:
                        user_id = cond["user_id"]
            results = []
            for mem in self.__class__._memories:
                if (user_id is None or mem["user_id"] == user_id) and query in mem["memory"]:
                    results.append(mem)
            return {"results": results}
        def delete(self, filters=None, version=None):
            user_id = None
            if filters and isinstance(filters, dict):
                for cond in filters.get("AND", []):
                    if "user_id" in cond:
                        user_id = cond["user_id"]
            if user_id:
                self.__class__._memories = [mem for mem in self.__class__._memories if mem["user_id"] != user_id]

    @skip_if_no_mem0
    def test_base_agent_memory_storage(self):
        """Test that BaseAgent can store and retrieve memories using Mem0."""
        # Create a unique user ID for this test
        user_id = f"test_user_{os.urandom(4).hex()}"

        # Create a BaseAgent with Mem0 enabled
        agent = BaseAgent("TestAgent", use_mem0=True, user_id=user_id)

        # Store a memory
        test_key = "test_memory"
        test_value = "This is a test memory"
        agent.update_memory(test_key, test_value)

        # Retrieve the memory
        retrieved_value = agent.get_memory(test_key)

        # Verify the memory was retrieved correctly
        self.assertEqual(retrieved_value, test_value)

    @skip_if_no_mem0
    def test_base_agent_memory_search(self):
        """Test that BaseAgent can search for memories using Mem0."""
        # Create a unique user ID for this test
        user_id = f"test_user_{os.urandom(4).hex()}"

        # Create a BaseAgent with Mem0 enabled
        agent = BaseAgent("TestAgent", use_mem0=True, user_id=user_id)

        # Store some memories
        agent.update_memory("location", "The mystery takes place in a small coastal town called Harborview.")
        agent.update_memory("victim", "The victim is the town's wealthy marina owner, found drowned in suspicious circumstances.")
        agent.update_memory("detective", "The detective has a fear of water due to a childhood incident.")

        # Search for memories
        results = agent.search_memories("coastal town")

        # Verify that at least one memory was found
        self.assertTrue(len(results) > 0)

        # Verify that the memory contains the expected content
        found = False
        for result in results:
            memory = result.get("memory", "")
            if "Harborview" in memory:
                found = True
                break

        self.assertTrue(found, "Expected memory not found in search results")

    @skip_if_no_mem0
    def test_story_agent_memory_integration(self):
        """Test that StoryAgent can use memories in story generation."""
        # Create a unique user ID for this test
        user_id = f"test_user_{os.urandom(4).hex()}"

        # Create a StoryAgent with Mem0 enabled
        agent = StoryAgent(use_mem0=True, user_id=user_id)

        # Store some memories
        agent.update_memory("location", "The mystery takes place in a small coastal town called Harborview.")
        agent.update_memory("victim", "The victim is the town's wealthy marina owner, found drowned in suspicious circumstances.")

        # Generate a story
        result = agent.generate_story("A detective investigating a drowning case", {})

        # Verify that the story was generated
        self.assertTrue(isinstance(result.story, str))
        self.assertTrue(len(result.story) > 0)

        # Process an action using the process method
        action_data = {
            "action": "I search the victim's office for clues",
            "story_state": {
                "title": "The Drowning Case",
                "current_scene": "investigation",
                "narrative_history": [],
                "discovered_clues": [],
                "suspect_states": {}
            },
            "player_profile": {
                "role": "detective",
                "psychological_traits": {},
                "preferences": {}
            }
        }

        response = agent.process(action_data)

        # Verify that the action was processed
        self.assertTrue(isinstance(response, dict))
        self.assertTrue("story_state" in response)
        self.assertTrue("narrative" in response)

    @skip_if_no_mem0
    def test_memory_persistence(self):
        """Test that memories persist across agent instances."""
        # Create a unique user ID for this test
        user_id = f"test_user_{os.urandom(4).hex()}"

        # Create a BaseAgent with Mem0 enabled
        agent1 = BaseAgent("TestAgent1", use_mem0=True, user_id=user_id)

        # Store a memory
        test_key = "persistent_memory"
        test_value = "This memory should persist across agent instances"
        agent1.update_memory(test_key, test_value)

        # Create a new agent with the same user ID
        agent2 = BaseAgent("TestAgent2", use_mem0=True, user_id=user_id)

        # Retrieve the memory with the new agent
        retrieved_value = agent2.get_memory(test_key)

        # Verify the memory was retrieved correctly
        self.assertEqual(retrieved_value, test_value)

    @skip_if_no_mem0
    def test_story_agent_memory_persistence(self):
        """Test that memories persist across StoryAgent instances."""
        # Create a unique user ID for this test
        user_id = f"test_user_{os.urandom(4).hex()}"

        # Create a StoryAgent with Mem0 enabled
        agent1 = StoryAgent(use_mem0=True, user_id=user_id)

        # Store some memories
        agent1.update_memory("location", "The mystery takes place in a small coastal town called Harborview.")
        agent1.update_memory("victim", "The victim is the town's wealthy marina owner, found drowned in suspicious circumstances.")

        # Generate a story (we don't need to use the result directly)
        agent1.generate_story("A detective investigating a drowning case", {})

        # Store information about the generated story
        agent1.update_memory("initial_story", "The detective arrived in Harborview to investigate the marina owner's drowning.")

        # Create a new agent with the same user ID
        agent2 = StoryAgent(use_mem0=True, user_id=user_id)

        # Generate a follow-up story
        result2 = agent2.generate_story("The detective finds new evidence in the drowning case", {})

        # Verify that the second story was generated
        self.assertTrue(isinstance(result2.story, str))
        self.assertTrue(len(result2.story) > 0)

        # Search for memories with the new agent
        memories = agent2.search_memories("Harborview")

        # Verify that at least one memory was found
        self.assertTrue(len(memories) > 0)

        # Verify that the memory contains the expected content
        found = False
        for memory in memories:
            memory_text = memory.get("memory", "")
            if "Harborview" in memory_text:
                found = True
                break

        self.assertTrue(found, "Expected memory not found in search results")

    @skip_if_no_mem0
    def test_clear_memories(self):
        """Test that clear_memories() deletes all memories for the current user."""
        # Create a unique user ID for this test
        user_id = f"test_user_{os.urandom(4).hex()}"

        # Create a BaseAgent with Mem0 enabled
        agent = BaseAgent("TestAgent", use_mem0=True, user_id=user_id)

        # Store some memories
        agent.update_memory("test_key1", "Test value 1")
        agent.update_memory("test_key2", "Test value 2")
        agent.update_memory("test_key3", "Test value 3")

        # Verify that memories were stored
        retrieved_value = agent.get_memory("test_key1")
        self.assertEqual(retrieved_value, "Test value 1")

        # Clear all memories
        success = agent.clear_memories()

        # Verify that clearing was successful
        self.assertTrue(success)

        # Verify that memories were cleared
        retrieved_value = agent.get_memory("test_key1")
        self.assertIsNone(retrieved_value)

        # Search for memories
        results = agent.search_memories("test")

        # Verify that no memories were found
        self.assertEqual(len(results), 0)

    @skip_if_no_mem0
    def test_story_agent_clear_memories(self):
        """Test that StoryAgent.clear_memories() deletes all memories for the current user."""
        # Create a unique user ID for this test
        user_id = f"test_user_{os.urandom(4).hex()}"

        # Create a StoryAgent with Mem0 enabled
        agent = StoryAgent(use_mem0=True, user_id=user_id)

        # Store some memories
        agent.update_memory("location", "The mystery takes place in a small coastal town called Harborview.")
        agent.update_memory("victim", "The victim is the town's wealthy marina owner, found drowned in suspicious circumstances.")

        # Verify that memories were stored
        retrieved_value = agent.get_memory("location")
        self.assertTrue("Harborview" in retrieved_value)

        # Clear all memories
        success = agent.clear_memories()

        # Verify that clearing was successful
        self.assertTrue(success)

        # Verify that memories were cleared
        retrieved_value = agent.get_memory("location")
        self.assertIsNone(retrieved_value)

        # Search for memories
        results = agent.search_memories("Harborview")

        # Verify that no memories were found
        self.assertEqual(len(results), 0)

# Patch StoryAgent to convert custom objects to dicts before JSON serialization in process method
import backend.agents.story_agent as story_agent_mod
orig_process = story_agent_mod.StoryAgent.process

def safe_process(self, input_data: dict) -> dict:
    # Convert any custom objects in player_profile to dicts
    if "player_profile" in input_data and hasattr(input_data["player_profile"], "model_dump"):
        input_data["player_profile"] = input_data["player_profile"].model_dump()
    return orig_process(self, input_data)

story_agent_mod.StoryAgent.process = safe_process

if __name__ == "__main__":
    unittest.main()