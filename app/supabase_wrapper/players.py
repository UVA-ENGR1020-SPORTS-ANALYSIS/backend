from typing import Optional
from app.supabase_wrapper.client import get_client

def bulk_create_players(team_id: str, player_names: list[str]) -> Optional[list[dict]]:
    """
    Bulk inserts players linked to a team_id into the player table.
    Returns the inserted rows.
    """
    supabase = get_client()
    
    players_data = [
        {"player_team_id": team_id, "player_name": name}
        for name in player_names
    ]
    
    players_insert = supabase.table("player").insert(players_data).execute()
    
    if not players_insert.data:
        return None
        
    return players_insert.data

def create_player_in_db(player_data: dict) -> Optional[dict]:
    """
    Inserts a single player into the player table.
    Returns the inserted row.
    """
    supabase = get_client()
    
    result = supabase.table("player").insert(player_data).execute()
    
    if not result.data:
        return None
        
    return result.data[0]

def update_player_in_db(player_id: str, player_name: str) -> Optional[dict]:
    """
    Updates a player's name by player_id.
    Returns the updated row, or None if the player was not found.
    """
    supabase = get_client()

    result = (
        supabase.table("player")
        .update({"player_name": player_name})
        .eq("player_id", player_id)
        .execute()
    )

    if not result.data:
        return None

    return result.data[0]

def calculate_player_stat_update(current_stats: dict, points: int, made: bool) -> dict:
    total_points = int(current_stats.get("total_points") or 0) + points
    total_makes = int(current_stats.get("total_makes") or 0) + (1 if made else 0)
    total_attempts = int(current_stats.get("total_attempts") or 0) + 1
    shooting_pct = round((total_makes / total_attempts) * 100, 2) if total_attempts else 0

    return {
        "total_points": total_points,
        "total_makes": total_makes,
        "total_attempts": total_attempts,
        "shooting_pct": float(shooting_pct),
    }

def increment_player_stats(player_id: str, points: int, made: bool) -> bool:
    """
    Increments a player's cumulative stats after a shot.
    Updates total_points, total_makes, total_attempts, and recomputes shooting_pct.
    """
    supabase = get_client()
    try:
        res = supabase.table("player").select(
            "total_points, total_makes, total_attempts"
        ).eq("player_id", player_id).single().execute()

        if not res.data:
            return False

        supabase.table("player").update(
            calculate_player_stat_update(res.data, points, made)
        ).eq("player_id", player_id).execute()

        return True
    except Exception as e:
        print("Error incrementing player stats:", e)
        return False

def get_player_stats_from_db(player_id: str) -> Optional[dict]:
    """Fetches a single player's full record."""
    supabase = get_client()
    try:
        res = supabase.table("player").select("*").eq("player_id", player_id).single().execute()
        return res.data if res.data else None
    except Exception:
        return None

def get_players_by_team(team_id: str) -> list[dict]:
    """Fetches all players for a given team."""
    supabase = get_client()
    try:
        res = supabase.table("player").select("*").eq("player_team_id", team_id).execute()
        return res.data or []
    except Exception:
        return []
