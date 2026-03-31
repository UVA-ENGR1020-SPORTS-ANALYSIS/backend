import os
from fastapi import HTTPException
from supabase import create_client, Client

def get_client() -> Client:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        raise HTTPException(status_code=500, detail="Supabase env variables missing.")
    return create_client(url, key)
