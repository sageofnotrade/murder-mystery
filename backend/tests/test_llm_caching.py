"""
Unit tests for Redis caching of LLM responses in ModelRouter (BE-009).
Covers cache hit, miss, and fallback cases.
"""
import pytest
import json
from backend.agents.model_router import ModelRouter
from pydantic_ai.messages import ModelMessage
from backend.tests.mocks.redis_mock import MockRedisClient
import redis
from unittest.mock import patch, MagicMock

class DummyMessage:
    def __init__(self, role, content):
        self.role = role
        self.content = content

class DummyResult:
    def __init__(self, content):
        self.content = content
    def model_dump(self):
        return {"content": self.content}

@pytest.fixture
def router():
    return ModelRouter()

@pytest.fixture(scope="module")
def redis_client():
    # Patch redis.from_url to use MockRedisClient
    with patch('redis.from_url', return_value=MockRedisClient()):
        yield MockRedisClient()

@patch('redis.from_url', return_value=MockRedisClient())
def test_llm_cache_miss_and_set(mock_redis_from_url, router, mocker):
    router.redis_client.flushdb()
    dummy_result = DummyResult("test output")
    mock_model = MagicMock()
    mock_model.complete = MagicMock(return_value=dummy_result)
    mocker.patch.object(router, "get_model_for_task", return_value=mock_model)
    messages = [DummyMessage(role="user", content="What is the capital of France?")]
    result = router.complete(messages, "reasoning", user_id="test-user")
    assert result.content == "test output"
    keys = list(router.redis_client.scan_iter("llm_cache:*"))
    assert len(keys) == 1
    cached = json.loads(router.redis_client.get(keys[0]))
    assert cached == {"content": "test output"}

@patch('redis.from_url', return_value=MockRedisClient())
def test_llm_cache_hit(mock_redis_from_url, router, mocker):
    # Prime the cache with a successful call
    dummy_result = DummyResult("test output")
    mock_model = MagicMock()
    mock_model.complete = MagicMock(return_value=dummy_result)
    mocker.patch.object(router, "get_model_for_task", return_value=mock_model)
    messages = [DummyMessage(role="user", content="What is the capital of France?")]
    router.complete(messages, "reasoning", user_id="test-user")
    # Now patch to raise if called (should not be called)
    mock_model.complete = MagicMock(side_effect=Exception("Should not call LLM on cache hit"))
    mocker.patch.object(router, "get_model_for_task", return_value=mock_model)
    result = router.complete(messages, "reasoning", user_id="test-user")
    assert result["content"] == "test output"

@patch('redis.from_url', return_value=MockRedisClient())
def test_llm_cache_fallback_on_corruption(mock_redis_from_url, router, mocker):
    keys = list(router.redis_client.scan_iter("llm_cache:*"))
    if keys:
        router.redis_client.set(keys[0], b"not-json")
    dummy_result2 = DummyResult("new output")
    mock_model = MagicMock()
    mock_model.complete = MagicMock(return_value=dummy_result2)
    mocker.patch.object(router, "get_model_for_task", return_value=mock_model)
    messages = [DummyMessage(role="user", content="What is the capital of France?")]
    result = router.complete(messages, "reasoning", user_id="test-user")
    assert result.content == "new output"
