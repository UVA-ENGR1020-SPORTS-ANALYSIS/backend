from app.supabase_wrapper.client import get_client

def get_teams_count_by_session(session_id: str) -> int:
    """
    Returns the number of teams for a session.
    """
    supabase = get_client()
    teams_res = supabase.table("teams").select("team_id").eq("current_session", session_id).execute()
    return len(teams_res.data)

def create_team(session_uuid: str) -> str | None:
    """
    Creates a team and returns the new team_id.
    """
    supabase = get_client()
    team_insert = supabase.table("teams").insert({"current_session": session_uuid}).execute()
    
    if not team_insert.data:
        return None
        
    return team_insert.data[0]["team_id"]
