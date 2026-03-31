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
