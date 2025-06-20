from supabase import create_client, Client
from app.core.config import get_settings
from functools import lru_cache

@lru_cache
def get_supabase() -> Client:
    st = get_settings()
    print(f"Supabase URL: {st.supabase_url}")
    print(f"Supabase Key: {st.supabase_key[:8]}...")  # print partial key only
    return create_client(st.supabase_url, st.supabase_key)
