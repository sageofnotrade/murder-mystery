"""
Unit tests for BaseAgent class.
Tests memory operations, initialization, and error handling with mocked dependencies.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from backend.agents.base_agent import BaseAgent


class TestBaseAgent:
    """Test suite for BaseAgent class."""

    def test_init_without_mem0(self):
        """Test BaseAgent initialization without Mem0 integration."""
        agent = BaseAgent("TestAgent", use_mem0=False)
        
        assert agent.agent_name == "TestAgent"
        assert agent.use_mem0 is False
        assert agent.user_id is None
        assert agent.mem0_client is None

    def test_init_with_mem0_no_api_key(self):
        """Test BaseAgent initialization with Mem0 but no API key."""
        with patch.dict(os.environ, {}, clear=True):
            agent = BaseAgent("TestAgent", use_mem0=True, user_id="test_user")
            
            assert agent.agent_name == "TestAgent"
            assert agent.use_mem0 is False  # Should be disabled due to missing API key
            assert agent.user_id == "test_user"
            assert agent.mem0_client is None

    def test_init_with_mem0_no_user_id(self):
        """Test BaseAgent initialization with Mem0 but no user ID."""
        with patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
            agent = BaseAgent("TestAgent", use_mem0=True)
            
            assert agent.agent_name == "TestAgent"
            assert agent.use_mem0 is False  # Should be disabled due to missing user_id
            assert agent.user_id is None
            assert agent.mem0_client is None

    @patch('backend.agents.base_agent.mem0')
    def test_init_with_mem0_success(self, mock_mem0):
        """Test successful BaseAgent initialization with Mem0."""
        mock_client = Mock()
        mock_mem0.MemoryClient.return_value = mock_client
        
        with patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
            agent = BaseAgent("TestAgent", use_mem0=True, user_id="test_user")
            
            assert agent.agent_name == "TestAgent"
            assert agent.use_mem0 is True
            assert agent.user_id == "test_user"
            assert agent.mem0_client == mock_client
            
            # Verify MemoryClient was called with correct API key
            mock_mem0.MemoryClient.assert_called_once_with(api_key="test_key")

    @patch('backend.agents.base_agent.mem0')
    def test_init_with_mem0_import_error(self, mock_mem0):
        """Test BaseAgent initialization when mem0 import fails."""
        mock_mem0.side_effect = ImportError("mem0 not installed")
        
        with patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
            agent = BaseAgent("TestAgent", use_mem0=True, user_id="test_user")
            
            assert agent.agent_name == "TestAgent"
            assert agent.use_mem0 is False  # Should be disabled due to import error
            assert agent.user_id == "test_user"
            assert agent.mem0_client is None

    def test_init_with_custom_config(self):
        """Test BaseAgent initialization with custom Mem0 configuration."""
        custom_config = {
            "search_limit": 10,
            "search_threshold": 0.8,
            "rerank": False
        }
        
        agent = BaseAgent("TestAgent", use_mem0=False, mem0_config=custom_config)
        
        assert agent.mem0_config["search_limit"] == 10
        assert agent.mem0_config["search_threshold"] == 0.8
        assert agent.mem0_config["rerank"] is False
        # Default values should still be present
        assert agent.mem0_config["store_summaries"] is True

    def test_update_memory_disabled(self):
        """Test update_memory when Mem0 is disabled."""
        agent = BaseAgent("TestAgent", use_mem0=False)
        
        result = agent.update_memory("test_key", "test_value")
        
        assert result is False

    def test_update_memory_no_client(self):
        """Test update_memory when client is None."""
        agent = BaseAgent("TestAgent", use_mem0=True, user_id="test_user")
        agent.mem0_client = None
        
        result = agent.update_memory("test_key", "test_value")
        
        assert result is False

    @patch('backend.agents.base_agent.mem0')
    def test_update_memory_success(self, mock_mem0):
        """Test successful memory update."""
        mock_client = Mock()
        mock_mem0.MemoryClient.return_value = mock_client
        
        with patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
            agent = BaseAgent("TestAgent", use_mem0=True, user_id="test_user")
            
            result = agent.update_memory("test_key", "test_value")
            
            assert result is True
            mock_client.add.assert_called_once_with(
                messages="test_key: test_value",
                user_id="test_user",
                output_format="v1.1",
                version="v2"
            )

    @patch('backend.agents.base_agent.mem0')
    def test_update_memory_exception(self, mock_mem0):
        """Test memory update with exception."""
        mock_client = Mock()
        mock_client.add.side_effect = Exception("API Error")
        mock_mem0.MemoryClient.return_value = mock_client
        
        with patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
            agent = BaseAgent("TestAgent", use_mem0=True, user_id="test_user")
            
            result = agent.update_memory("test_key", "test_value")
            
            assert result is False

    def test_get_memory_disabled(self):
        """Test get_memory when Mem0 is disabled."""
        agent = BaseAgent("TestAgent", use_mem0=False)
        
        result = agent.get_memory("test_key")
        
        assert result is None

    @patch('backend.agents.base_agent.mem0')
    def test_get_memory_success(self, mock_mem0):
        """Test successful memory retrieval."""
        mock_client = Mock()
        mock_client.search.return_value = {
            'results': [
                {'memory': 'test_key: test_value'},
                {'memory': 'other_key: other_value'}
            ]
        }
        mock_mem0.MemoryClient.return_value = mock_client
        
        with patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
            agent = BaseAgent("TestAgent", use_mem0=True, user_id="test_user")
            
            result = agent.get_memory("test_key")
            
            assert result == "test_value"
            mock_client.search.assert_called_once()

    @patch('backend.agents.base_agent.mem0')
    def test_get_memory_not_found(self, mock_mem0):
        """Test memory retrieval when key is not found."""
        mock_client = Mock()
        mock_client.search.return_value = {
            'results': [
                {'memory': 'other_key: other_value'}
            ]
        }
        mock_mem0.MemoryClient.return_value = mock_client
        
        with patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
            agent = BaseAgent("TestAgent", use_mem0=True, user_id="test_user")
            
            result = agent.get_memory("test_key")
            
            assert result is None

    @patch('backend.agents.base_agent.mem0')
    def test_get_memory_exception(self, mock_mem0):
        """Test memory retrieval with exception."""
        mock_client = Mock()
        mock_client.search.side_effect = Exception("API Error")
        mock_mem0.MemoryClient.return_value = mock_client
        
        with patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
            agent = BaseAgent("TestAgent", use_mem0=True, user_id="test_user")
            
            result = agent.get_memory("test_key")
            
            assert result is None

    @patch('backend.agents.base_agent.mem0')
    def test_search_memories_success(self, mock_mem0):
        """Test successful memory search."""
        mock_client = Mock()
        mock_client.search.return_value = {
            'results': [
                {'memory': 'test memory 1', 'score': 0.9},
                {'memory': 'test memory 2', 'score': 0.8}
            ]
        }
        mock_mem0.MemoryClient.return_value = mock_client
        
        with patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
            agent = BaseAgent("TestAgent", use_mem0=True, user_id="test_user")
            
            result = agent.search_memories("test query", limit=5, threshold=0.7, rerank=True)
            
            assert len(result) == 2
            assert result[0]['memory'] == 'test memory 1'
            mock_client.search.assert_called_once()

    def test_search_memories_disabled(self):
        """Test search_memories when Mem0 is disabled."""
        agent = BaseAgent("TestAgent", use_mem0=False)
        
        result = agent.search_memories("test query")
        
        assert result == []

    @patch('backend.agents.base_agent.mem0')
    def test_clear_memories_success(self, mock_mem0):
        """Test successful memory clearing."""
        mock_client = Mock()
        mock_client.delete_all.return_value = True
        mock_mem0.MemoryClient.return_value = mock_client
        
        with patch.dict(os.environ, {"MEM0_API_KEY": "test_key"}):
            agent = BaseAgent("TestAgent", use_mem0=True, user_id="test_user")
            
            result = agent.clear_memories()
            
            assert result is True
            mock_client.delete_all.assert_called_once_with(user_id="test_user")

    def test_clear_memories_disabled(self):
        """Test clear_memories when Mem0 is disabled."""
        agent = BaseAgent("TestAgent", use_mem0=False)
        
        result = agent.clear_memories()
        
        assert result is False 