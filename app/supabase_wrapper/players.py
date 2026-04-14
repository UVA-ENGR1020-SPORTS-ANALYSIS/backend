from app.supabase_wrapper.client import get_client

def bulk_create_players(team_id: str, player_names: list[str]) -> list[dict] | None:
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

def update_player_in_db(player_id: str, player_name: str) -> dict | None:
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

        cur = res.data
        new_points   = cur["total_points"] + points
        new_makes    = cur["total_makes"] + (1 if made else 0)
        new_attempts = cur["total_attempts"] + 1
        new_pct      = round((new_makes / new_attempts) * 100, 2) if new_attempts > 0 else 0

        supabase.table("player").update({
            "total_points":   new_points,
            "total_makes":    new_makes,
            "total_attempts": new_attempts,
            "shooting_pct":   float(new_pct),
        }).eq("player_id", player_id).execute()

        return True
    except Exception as e:
        print("Error incrementing player stats:", e)
        return False

def get_player_stats_from_db(player_id: str) -> dict | None:
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
