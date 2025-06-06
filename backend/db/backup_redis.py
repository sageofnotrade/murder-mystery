"""
Backup Redis keys for Murþrą project.
Backs up all story, board, and LLM cache keys to a JSON file.
Usage: python backup_redis.py [REDIS_URL] [OUTPUT_FILE]
"""
import sys
import redis
import json
from datetime import datetime

REDIS_URL = sys.argv[1] if len(sys.argv) > 1 else 'redis://localhost:6379/0'
OUTPUT_FILE = sys.argv[2] if len(sys.argv) > 2 else f"redis_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

r = redis.from_url(REDIS_URL, decode_responses=True)

# Keys to backup
patterns = ["story:*", "board_state:*", "llm_cache:*"]
backup = {}
for pattern in patterns:
    for key in r.scan_iter(pattern):
        backup[key] = r.get(key)

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(backup, f, indent=2)

print(f"Backed up {len(backup)} keys to {OUTPUT_FILE}")
