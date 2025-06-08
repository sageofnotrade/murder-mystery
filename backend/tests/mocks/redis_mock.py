from unittest.mock import MagicMock
import re

class MockRedisClient:
    def __init__(self):
        self.data = {}
        self.mock = MagicMock()

    def set(self, key, value, **kwargs):
        self.data[key] = value
        return self.mock.set(key, value)

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

    def flushdb(self):
        self.flushall()

    def scan_iter(self, pattern=None):
        if pattern is None:
            for key in self.data:
                yield key
        else:
            regex = re.compile('^' + pattern.replace('*', '.*') + '$')
            for key in self.data:
                if regex.match(key):
                    yield key 