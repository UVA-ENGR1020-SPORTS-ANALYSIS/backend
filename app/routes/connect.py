from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/connect", tags=["connect"])

class JoinSessionRequest(BaseModel):
    session_code: str
    player_name: str

@router.get("/{session_code}")
async def check_session(session_code: str):
    # TODO: Fetch session from the database using session_code
    # TODO: If session does not exist or is inactive, raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "status": "valid",
        "session_code": session_code,
        "message": f"Session {session_code} is active and ready to join"
    }

@router.post("")
async def join_session(request: JoinSessionRequest):
    # TODO: Step 1. Fetch current session and its active players from the database
    # Placeholder for existing players in the session (replace with real DB query):
    existing_players_in_db = ["Alice", "Bob", "Test"] 
    
    # Step 2. Validate that the player name is not already taken in this session
    if request.player_name in existing_players_in_db:
        # If the name is taken, reject the request with a 400 Bad Request error
        raise HTTPException(
            status_code=400,
            detail=f"The name '{request.player_name}' is already taken in this session. Please choose another one."
        )
        
    # TODO: Step 3. Add the new player to the session in the database
    
    # Step 4. Send successful response with player details
    return {
        "status": "success",
        "message": f"Player {request.player_name} successfully joined session {request.session_code}",
        "player_token": "placeholder_token_123" # TODO: Return a real JWT or UUID from DB for the frontend to save
    }
