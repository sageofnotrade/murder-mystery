"""
Restore Redis keys for Murþrą project from a JSON backup file.
Usage: python restore_redis.py [REDIS_URL] [BACKUP_FILE]
"""
import sys
import redis
import json

REDIS_URL = sys.argv[1] if len(sys.argv) > 1 else 'redis://localhost:6379/0'
BACKUP_FILE = sys.argv[2] if len(sys.argv) > 2 else 'redis_backup.json'

r = redis.from_url(REDIS_URL, decode_responses=True)

with open(BACKUP_FILE, 'r', encoding='utf-8') as f:
    backup = json.load(f)

for key, value in backup.items():
    r.set(key, value)

print(f"Restored {len(backup)} keys from {BACKUP_FILE}")
