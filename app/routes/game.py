from fastapi import APIRouter
from app.models.shot import Shot

router = APIRouter(prefix="/api/game", tags=["game"])

@router.get("/{session_id}/score")
async def get_score(session_id: str):
    # TODO: Fetch current score from DB (e.g. game:live)
    return {
        "session_id": session_id,
        "home_score": 0,
        "away_score": 0,
        "possession": "home"
    }

@router.post("/shot")
async def record_shot(shot: Shot):
    # TODO: Logic to save shot to game:shot_log and update scores
    return {
        "status": "recorded",
        "shot": shot
    }

@router.patch("/{session_id}/possession")
async def update_possession(session_id: str, team_id: str):
    # TODO: Update possession in DB
    return {
        "status": "updated",
        "session_id": session_id,
        "possession": team_id
    }

@router.get("/{session_id}/log")
async def get_game_log(session_id: str):
    # TODO: Fetch all shots for this session from DB
    return {
        "session_id": session_id,
        "shots": []
    }
