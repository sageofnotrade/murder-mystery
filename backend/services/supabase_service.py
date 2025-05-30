from supabase import create_client, Client
import os
from functools import lru_cache

@lru_cache()
def get_supabase_client() -> Client:
    """Get a cached Supabase client instance."""
    return create_client(
        os.getenv('SUPABASE_URL', 'mock://supabase'),
        os.getenv('SUPABASE_KEY', 'mock-key')
    ) 