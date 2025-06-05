"""
Unit tests for Redis caching of LLM responses in ModelRouter (BE-009).
Covers cache hit, miss, and fallback cases.
"""
import pytest
import json
from backend.agents.model_router import ModelRouter
from pydantic_ai.messages import ModelMessage
import redis

@pytest.fixture(scope="module")
def router():
    return ModelRouter()

@pytest.fixture(scope="module")
def redis_client():
    REDIS_URL = "redis://localhost:6379/0"
    return redis.from_url(REDIS_URL)

def test_llm_cache_miss_and_set(router, redis_client, mocker):
    # Clear cache
    redis_client.flushdb()
    # Mock model.complete to return a dummy result
    dummy_result = {"content": "test output"}
    mocker.patch.object(router.get_model_for_task("reasoning"), "complete", return_value=dummy_result)
    messages = [Message(role="user", content="What is the capital of France?")]
    # First call: should be a cache miss
    result = router.complete(messages, "reasoning", user_id="test-user")
    assert result == dummy_result
    # Check cache directly
    keys = list(redis_client.scan_iter("llm_cache:*"))
    assert len(keys) == 1
    cached = json.loads(redis_client.get(keys[0]))
    assert cached == dummy_result

def test_llm_cache_hit(router, redis_client, mocker):
    # Mock model.complete to raise if called (should not be called)
    mocker.patch.object(router.get_model_for_task("reasoning"), "complete", side_effect=Exception("Should not call LLM on cache hit"))
    messages = [Message(role="user", content="What is the capital of France?")]
    # Second call: should be a cache hit
    result = router.complete(messages, "reasoning", user_id="test-user")
    assert result["content"] == "test output"

def test_llm_cache_fallback_on_corruption(router, redis_client, mocker):
    # Corrupt the cache
    keys = list(redis_client.scan_iter("llm_cache:*"))
    if keys:
        redis_client.set(keys[0], b"not-json")
    # Mock model.complete to return a new dummy result
    dummy_result2 = {"content": "new output"}
    mocker.patch.object(router.get_model_for_task("reasoning"), "complete", return_value=dummy_result2)
    messages = [Message(role="user", content="What is the capital of France?")]
    result = router.complete(messages, "reasoning", user_id="test-user")
    assert result == dummy_result2
