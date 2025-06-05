from unittest.mock import MagicMock

class MockRedisClient:
    def __init__(self):
        self.data = {}
        self.mock = MagicMock()

    def setex(self, key, ttl, value):
        self.data[key] = value
        return self.mock.setex(key, ttl, value)

    def get(self, key):
        return self.data.get(key)

    def delete(self, key):
        if key in self.data:
            del self.data[key]
        return self.mock.delete(key)

    def exists(self, key):
        return key in self.data

    def keys(self, pattern):
        return [k for k in self.data.keys() if pattern in k]

    def flushall(self):
        self.data.clear()
        return self.mock.flushall() 