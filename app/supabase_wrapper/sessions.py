from typing import Optional
from app.supabase_wrapper.client import get_client

def get_session_by_code(session_code: int) -> Optional[dict]:
    """
    Queries the sessions table for a given session code.
    Returns the session dictionary if found, otherwise None.
    """
    supabase = get_client()
    session_res = supabase.table("sessions").select("*").eq("session_code", session_code).execute()
    
    if not session_res.data:
        return None
        
    return session_res.data[0]
