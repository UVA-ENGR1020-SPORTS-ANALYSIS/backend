from typing import Dict, Any, Optional
from app.supabase_wrapper.client import get_client
from app.models.schemas import ShotRecord

SHOT_SELECT_COLUMNS = (
    "shot_id,shot_player_id,team_id,session_id,round_number,"
    "zone,shot_made,make_value,location_value,points"
)

def record_shot_in_db(shot: ShotRecord) -> Optional[str]:
    """Records a shot and returns the shot_id."""
    supabase = get_client()
    data = {
        "shot_player_id": shot.player_id,
        "team_id": shot.team_id,
        "session_id": shot.session_id,
        "round_number": shot.round_number,
        "zone": shot.zone,
        "shot_made": shot.is_make,
        "make_value": shot.make_value,
        "location_value": shot.location_value,
        "points": shot.points
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

def get_team_stats(team_id: str, round_number: Optional[int] = 1, include_shots: bool = False) -> Dict[str, Any]:
    """Gets total points and shots for a team.

    If round_number is None, aggregates across ALL rounds for the team.
    Otherwise filters to the given round.
    """
    supabase = get_client()
    try:
        stats_query = (
            supabase.table("shots")
            .select("total_points:points.sum(),shots_taken:shot_id.count()")
            .eq("team_id", team_id)
        )
        if round_number is not None:
            stats_query = stats_query.eq("round_number", round_number)
        stats_res = stats_query.execute()
        row = stats_res.data[0] if stats_res.data else {}
        points = row.get("total_points") or 0
        shots_taken = row.get("shots_taken") or 0
        shots = []

        if include_shots:
            shots_query = (
                supabase.table("shots")
                .select(SHOT_SELECT_COLUMNS)
                .eq("team_id", team_id)
            )
            if round_number is not None:
                shots_query = shots_query.eq("round_number", round_number)
            shots_res = shots_query.execute()
            shots = shots_res.data or []
            shots_taken = shots_taken or len(shots)

        return {"shots": shots, "shots_taken": int(shots_taken), "total_points": int(points)}
    except Exception as e:
        print("Error getting team stats:", e)
        try:
            fallback_columns = SHOT_SELECT_COLUMNS if include_shots else "points"
            fallback_query = (
                supabase.table("shots")
                .select(fallback_columns)
                .eq("team_id", team_id)
            )
            if round_number is not None:
                fallback_query = fallback_query.eq("round_number", round_number)
            fallback_res = fallback_query.execute()
            fallback_shots = fallback_res.data or []
            return {
                "shots": fallback_shots if include_shots else [],
                "shots_taken": len(fallback_shots),
                "total_points": sum(int(shot.get("points") or 0) for shot in fallback_shots),
            }
        except Exception as fallback_error:
            print("Error getting fallback team stats:", fallback_error)
        return {"shots": [], "shots_taken": 0, "total_points": 0}

def ban_opponent_zone(opponent_team_id: str, zone: int) -> bool:
    """Sets the banned zone for an opponent."""
    supabase = get_client()
    try:
        supabase.table("teams").update({"banned_zone": zone}).eq("team_id", opponent_team_id).execute()
        return True
    except Exception as e:
        print("Error banning zone:", e)
        return False
