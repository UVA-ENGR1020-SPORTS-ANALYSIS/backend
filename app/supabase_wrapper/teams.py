from typing import Optional
from app.supabase_wrapper.client import get_client

def get_teams_count_by_session(session_id: str) -> int:
    """
    Returns the number of teams for a session.
    """
    supabase = get_client()
    teams_res = (
        supabase.table("teams")
        .select("team_id", count="exact")
        .eq("current_session", session_id)
        .execute()
    )
    if teams_res.count is not None:
        return teams_res.count
    return len(teams_res.data or [])

def create_team(session_uuid: str) -> Optional[str]:
    """
    Creates a team and returns the new team_id.
    """
    supabase = get_client()
    team_insert = supabase.table("teams").insert({"current_session": session_uuid}).execute()
    
    if not team_insert.data:
        return None
        
    return team_insert.data[0]["team_id"]

def set_team_ready(team_id: str, is_ready: bool) -> bool:
    """
    Updates the is_ready status of a team.
    """
    supabase = get_client()
    # Force generic execution without checking res.data in case it's suppressed
    try:
        supabase.table("teams").update({"is_ready": is_ready}).eq("team_id", team_id).execute()
        return True
    except Exception as e:
        print("Update Ready Error:", e)
        return False
