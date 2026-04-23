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

def _extract_teams_count(session: dict) -> int:
    embedded_teams = session.pop("teams", None)
    if not embedded_teams:
        return 0

    first_entry = embedded_teams[0] if isinstance(embedded_teams, list) else embedded_teams
    if isinstance(first_entry, dict):
        return int(first_entry.get("count") or 0)

    return 0

def get_session_by_code_with_team_count(session_code: int) -> tuple[Optional[dict], int]:
    """
    Fetches the session and joined team count together when the Supabase
    relationship metadata supports embedded counts.
    """
    supabase = get_client()
    try:
        session_res = (
            supabase.table("sessions")
            .select("*, teams(count)")
            .eq("session_code", session_code)
            .execute()
        )

        if not session_res.data:
            return None, 0

        session = dict(session_res.data[0])
        return session, _extract_teams_count(session)
    except Exception:
        session = get_session_by_code(session_code)
        if not session:
            return None, 0

        from app.supabase_wrapper.teams import get_teams_count_by_session
        return session, get_teams_count_by_session(session["session_id"])
