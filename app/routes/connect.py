from fastapi import APIRouter

router = APIRouter(prefix="/api/connect", tags=["connect"])

@router.get("/{session_code}")
async def check_session(session_code: str):
    # TODO: Logic to check if session_code exists in DB
    return {
        "status": "valid",
        "session_code": session_code,
        "message": f"Session {session_code} is active and ready to join"
    }

@router.post("")
async def join_session(session_code: str, player_name: str):
    # TODO: Logic to add player to session in DB
    return {
        "status": "success",
        "message": f"Player {player_name} joined session {session_code}"
    }
