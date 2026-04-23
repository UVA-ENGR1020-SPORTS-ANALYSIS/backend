from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool
from app.supabase_wrapper.client import get_client
from app.models.schemas import (
    ShotRecord,
    SubmitShotRequest, 
    SubmitShotResponse, 
    FinishRoundRequest, 
    BanZoneRequest
)
from app.supabase_wrapper.shots import (
    record_shot_in_db,
    set_team_round_finished,
    get_team_stats,
    ban_opponent_zone
)
from app.supabase_wrapper.players import increment_player_stats

router = APIRouter(prefix="/api/game", tags=["game"])

def get_teams_for_session(session_id: str) -> list[dict]:
    supabase = get_client()
    res = supabase.table("teams").select("*").eq("current_session", session_id).execute()
    return res.data or []

def get_location_value(zone: int) -> int:
    """Helper to determine points based on zone/location."""
    # Assuming: 1 = Free Throw (1 pt), 2 & 3 = Inside Arc (2 pts), 4,5,6 = Outside Arc (3 pts)
    if zone == 1:
        return 1
    elif zone in [2, 3]:
        return 2
    elif zone in [4, 5, 6]:
        return 3
    return 0

@router.post("/shot", response_model=SubmitShotResponse)
async def submit_shot(shot: SubmitShotRequest):
    make_value = 1 if shot.shot_made else 0
    location_value = get_location_value(shot.zone)
    points = make_value * location_value

    shot_record = ShotRecord(
        player_id=str(shot.player_id),
        team_id=str(shot.team_id),
        session_id=str(shot.session_id),
        round_number=shot.round_number,
        zone=shot.zone,
        is_make=shot.shot_made,
        make_value=make_value,
        location_value=location_value,
        points=points
    )
    shot_id = await run_in_threadpool(record_shot_in_db, shot_record)

    if not shot_id:
        raise HTTPException(status_code=500, detail="Failed to record shot.")

    # Update the shooter's cumulative stats
    await run_in_threadpool(increment_player_stats, str(shot.player_id), points, shot.shot_made)

    return SubmitShotResponse(
        status="success",
        shot_id=shot_id,
        points_awarded=points
    )

@router.post("/finish_round")
async def finish_round(req: FinishRoundRequest):
    success = await run_in_threadpool(set_team_round_finished, str(req.team_id), req.round_number)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update round status.")
    return {"status": "success", "message": f"Round {req.round_number} finished."}

@router.get("/team_stats/{team_id}/{round_number}")
async def fetch_team_stats(team_id: str, round_number: int):
    stats = await run_in_threadpool(get_team_stats, team_id, round_number, True)
    return {
        "team_id": team_id,
        "round_number": round_number,
        "shots_taken": stats["shots_taken"],
        "points": stats["total_points"],
        "raw_shots": stats["shots"]
    }

@router.get("/opponent_stats/{session_id}/{my_team_id}")
async def get_opponent_stats(session_id: str, my_team_id: str):
    # Fetch all teams in the session
    try:
        teams = await run_in_threadpool(get_teams_for_session, session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch teams.")

    opponent_teams = [t for t in teams if t["team_id"] != my_team_id]
    if not opponent_teams:
        return {"status": "no_opponent", "data": None}

    opponent_team = opponent_teams[0]  # Assuming 1v1
    
    # Check if opponent is done with round 1
    if not opponent_team.get("round_1_finished"):
        return {"status": "waiting", "data": None}

    # Gather their stats
    stats = await run_in_threadpool(get_team_stats, opponent_team["team_id"], 1, True)
    
    return {
        "status": "ready",
        "opponent_team_id": opponent_team["team_id"],
        "shots_taken": stats["shots_taken"],
        "points": stats["total_points"],
        "raw_shots": stats["shots"]
    }

@router.post("/ban")
async def ban_zone(req: BanZoneRequest):
    success = await run_in_threadpool(ban_opponent_zone, str(req.opponent_team_id), req.zone)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to set banned zone.")
    return {"status": "success", "message": f"Banned zone {req.zone} for opponent."}
