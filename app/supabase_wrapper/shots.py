from typing import Dict, Any, Optional
from app.supabase_wrapper.client import get_client

def record_shot_in_db(
    player_id: str, 
    team_id: str, 
    session_id: str,
    round_number: int,
    zone: int,
    is_make: bool,
    make_value: int,
    location_value: int,
    points: int
) -> Optional[str]:
    """Records a shot and returns the shot_id."""
    supabase = get_client()
    data = {
        "shot_player_id": player_id,
        "team_id": team_id,
        "session_id": session_id,
        "round_number": round_number,
        "zone": zone,
        "shot_made": is_make,
        "make_value": make_value,
        "location_value": location_value,
        "points": points
    }
    try:
        res = supabase.table("shots").insert(data).execute()
        if res.data:
            return res.data[0]["shot_id"]
    except Exception as e:
        print("Error recording shot:", e)
    return None

def set_team_round_finished(team_id: str, round_number: int) -> bool:
    """Marks a team as having finished round 1 or 2."""
    supabase = get_client()
    column = "round_1_finished" if round_number == 1 else "round_2_finished"
    try:
        supabase.table("teams").update({column: True}).eq("team_id", team_id).execute()
        return True
    except Exception as e:
        print(f"Error finishing round {round_number}:", e)
        return False

def get_team_stats(team_id: str, round_number: int = 1) -> Dict[str, Any]:
    """Gets total points and shots for a team in a specific round."""
    supabase = get_client()
    try:
        res = supabase.table("shots").select("*").eq("team_id", team_id).eq("round_number", round_number).execute()
        shots = res.data or []
        points = sum(s.get("points", 0) for s in shots)
        return {"shots": shots, "total_points": points}
    except Exception as e:
        print("Error getting team stats:", e)
        return {"shots": [], "total_points": 0}

def ban_opponent_zone(opponent_team_id: str, zone: int) -> bool:
    """Sets the banned zone for an opponent."""
    supabase = get_client()
    try:
        supabase.table("teams").update({"banned_zone": zone}).eq("team_id", opponent_team_id).execute()
        return True
    except Exception as e:
        print("Error banning zone:", e)
        return False
