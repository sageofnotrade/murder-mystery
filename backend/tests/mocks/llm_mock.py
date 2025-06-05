"""
Mock factory for LLM and external API interactions.
Provides reusable mocks for testing AI agents.
"""

from unittest.mock import Mock, MagicMock
import json


class LLMMockFactory:
    """Factory for creating LLM mocks with realistic responses."""

    @staticmethod
    def create_openai_mock(response_content: str):
        """Create a mock OpenAI client with specified response content."""
        mock_llm = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        
        mock_message.content = response_content
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_llm.chat.completions.create.return_value = mock_response
        
        return mock_llm

    @staticmethod
    def create_json_response_mock(response_data: dict):
        """Create a mock that returns JSON-formatted response."""
        return LLMMockFactory.create_openai_mock(json.dumps(response_data))

    @staticmethod
    def create_error_mock(error_message: str = "API Error"):
        """Create a mock that raises an exception."""
        mock_llm = Mock()
        mock_llm.chat.completions.create.side_effect = Exception(error_message)
        return mock_llm

    @staticmethod
    def create_story_response_mock():
        """Create a mock with typical story generation response."""
        response_data = {
            "narrative": "The detective examined the evidence carefully, noting the peculiar angle of the wound.",
            "story_state": {
                "current_scene": "investigation",
                "discovered_clues": ["bloody knife", "torn fabric"],
                "suspect_states": {
                    "john_doe": {
                        "name": "John Doe",
                        "interviewed": False,
                        "suspicious_level": 5
                    }
                }
            }
        }
        return LLMMockFactory.create_json_response_mock(response_data)

    @staticmethod
    def create_suspect_response_mock():
        """Create a mock with typical suspect generation response."""
        response_data = {
            "name": "John Doe",
            "background": "Former accountant with gambling debts",
            "occupation": "Accountant",
            "motive": "Financial desperation",
            "alibi": "Claims to be at the casino",
            "personality_traits": ["nervous", "evasive", "intelligent"],
            "relationship_to_victim": "Business partner",
            "suspicious_behaviors": ["avoiding eye contact", "sweating"],
            "secrets": ["Hidden gambling addiction", "Embezzled funds"]
        }
        return LLMMockFactory.create_json_response_mock(response_data)

    @staticmethod
    def create_dialogue_response_mock():
        """Create a mock with typical dialogue generation response."""
        response_data = {
            "dialogue": "I-I was at the casino all night, you can check with the dealers!",
            "updated_state": {
                "name": "John Doe",
                "interviewed": True,
                "suspicious_level": 8,
                "known_information": ["Has gambling debts", "Was at victim's office"],
                "contradictions": ["Time of alibi doesn't match"],
                "emotional_state": "defensive"
            }
        }
        return LLMMockFactory.create_json_response_mock(response_data)

    @staticmethod
    def create_clue_response_mock():
        """Create a mock with typical clue generation response."""
        response_data = {
            "type": "physical",
            "description": "A bloodied letter opener found under the desk",
            "location": "victim's office",
            "relevance": "potential murder weapon",
            "related_suspects": ["John Doe"],
            "analysis": "Forensic analysis shows fingerprints",
            "significance": 8
        }
        return LLMMockFactory.create_json_response_mock(response_data)

    @staticmethod
    def create_clue_analysis_mock():
        """Create a mock with typical clue analysis response."""
        response_data = {
            "forensic_details": "Blood type matches victim, fingerprints on handle",
            "connections": ["Links to suspect John Doe", "Possible murder weapon"],
            "significance": 9,
            "reliability": 0.85,
            "next_steps": ["Test fingerprints", "Check for DNA evidence"]
        }
        return LLMMockFactory.create_json_response_mock(response_data)

    @staticmethod
    def create_clue_extraction_mock(clue_found: bool = True):
        """Create a mock for clue extraction from narrative."""
        if clue_found:
            response_data = {
                "clue": "torn letter with bloodstains",
                "confidence": 0.8,
                "reasoning": "Letter found during desk search"
            }
        else:
            response_data = {
                "clue": None,
                "confidence": 0.1,
                "reasoning": "No evidence found"
            }
        return LLMMockFactory.create_json_response_mock(response_data)


class BraveSearchMockFactory:
    """Factory for creating Brave Search API mocks."""

    @staticmethod
    def create_success_mock(results: list = None):
        """Create a successful Brave search response mock."""
        if results is None:
            results = [
                {
                    "title": "Murder Mystery Investigation Guide",
                    "url": "https://example.com/mystery-guide",
                    "description": "Comprehensive guide to solving murder mysteries and conducting investigations."
                },
                {
                    "title": "Forensic Evidence Analysis",
                    "url": "https://example.com/forensics",
                    "description": "Methods and techniques for analyzing forensic evidence in criminal cases."
                }
            ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "web": {
                "results": results
            }
        }
        return mock_response

    @staticmethod
    def create_error_mock(status_code: int = 404):
        """Create a Brave search error response mock."""
        mock_response = Mock()
        mock_response.status_code = status_code
        return mock_response

    @staticmethod
    def create_exception_mock(error_message: str = "API Error"):
        """Create a mock that raises an exception."""
        mock = Mock()
        mock.side_effect = Exception(error_message)
        return mock


class Mem0MockFactory:
    """Factory for creating Mem0 memory system mocks."""

    @staticmethod
    def create_memory_client_mock():
        """Create a mock Mem0 MemoryClient."""
        mock_client = Mock()
        
        # Mock successful operations
        mock_client.add.return_value = {"status": "success"}
        mock_client.search.return_value = {
            "results": [
                {"memory": "test_key: test_value", "score": 0.9},
                {"memory": "other_key: other_value", "score": 0.7}
            ]
        }
        mock_client.delete_all.return_value = True
        
        return mock_client

    @staticmethod
    def create_memory_search_results(memories: list = None):
        """Create mock memory search results."""
        if memories is None:
            memories = [
                {"memory": "Previous story context about mansion mystery", "score": 0.9},
                {"memory": "Suspect behavior patterns: nervous, evasive", "score": 0.8},
                {"memory": "Clue connections: physical evidence links", "score": 0.7}
            ]
        
        return {"results": memories}

    @staticmethod
    def create_empty_search_results():
        """Create empty memory search results."""
        return {"results": []}


class ModelRouterMockFactory:
    """Factory for creating ModelRouter mocks."""

    @staticmethod
    def create_model_router_mock():
        """Create a mock ModelRouter."""
        mock_router = Mock()
        
        # Default to returning OpenAI mock
        mock_router.get_model.return_value = LLMMockFactory.create_openai_mock("Default response")
        mock_router.select_model.return_value = "openai:gpt-4"
        
        return mock_router

    @staticmethod
    def create_with_llm_mock(llm_mock):
        """Create a ModelRouter mock that returns a specific LLM mock."""
        mock_router = Mock()
        mock_router.get_model.return_value = llm_mock
        mock_router.select_model.return_value = "openai:gpt-4"
        
        return mock_router


class PydanticAIMockFactory:
    """Factory for creating PydanticAI agent mocks."""

    @staticmethod
    def create_agent_mock():
        """Create a mock PydanticAI agent."""
        mock_agent = Mock()
        
        # Mock tool registration
        mock_agent.tool = Mock(return_value=lambda func: func)
        
        # Mock agent execution
        async def mock_run(*args, **kwargs):
            return {"result": "Mock agent result"}
        
        mock_agent.run = mock_run
        
        return mock_agent


# Convenience functions for common mock combinations

def create_full_agent_mocks():
    """Create a complete set of mocks for agent testing."""
    return {
        'mem0_client': Mem0MockFactory.create_memory_client_mock(),
        'model_router': ModelRouterMockFactory.create_model_router_mock(),
        'brave_search': BraveSearchMockFactory.create_success_mock(),
        'pydantic_agent': PydanticAIMockFactory.create_agent_mock()
    }


def create_story_agent_mocks():
    """Create mocks specifically for StoryAgent testing."""
    return {
        'mem0_client': Mem0MockFactory.create_memory_client_mock(),
        'model_router': ModelRouterMockFactory.create_with_llm_mock(
            LLMMockFactory.create_story_response_mock()
        ),
        'brave_search': BraveSearchMockFactory.create_success_mock(),
        'pydantic_agent': PydanticAIMockFactory.create_agent_mock()
    }


def create_suspect_agent_mocks():
    """Create mocks specifically for SuspectAgent testing."""
    return {
        'mem0_client': Mem0MockFactory.create_memory_client_mock(),
        'model_router': ModelRouterMockFactory.create_with_llm_mock(
            LLMMockFactory.create_suspect_response_mock()
        ),
        'brave_search': BraveSearchMockFactory.create_success_mock(),
        'pydantic_agent': PydanticAIMockFactory.create_agent_mock()
    }


def create_clue_agent_mocks():
    """Create mocks specifically for ClueAgent testing."""
    return {
        'mem0_client': Mem0MockFactory.create_memory_client_mock(),
        'model_router': ModelRouterMockFactory.create_with_llm_mock(
            LLMMockFactory.create_clue_response_mock()
        ),
        'brave_search': BraveSearchMockFactory.create_success_mock(),
        'pydantic_agent': PydanticAIMockFactory.create_agent_mock()
    } 