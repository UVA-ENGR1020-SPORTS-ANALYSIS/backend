from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.supabase_wrapper.sessions import get_session_by_code
from app.supabase_wrapper.teams import get_teams_count_by_session, create_team
from app.supabase_wrapper.players import bulk_create_players

router = APIRouter(prefix="/api/connect", tags=["connect"])

class JoinTeamRequest(BaseModel):
    session_code: int             # The 6-digit PIN to join the game
    player_names: list[str]       # An array of names like ["Alice", "Bob", "Charlie"]
    player_number: int            # The number of players in the team

@router.get("/{session_code}")
async def check_session(session_code: int):
    """
    Checks if a room (session_code) exists before the frontend allows typing player names.
    """
    session = get_session_by_code(session_code)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Optional: fetch how many teams are already in this room
    teams_count = get_teams_count_by_session(session["session_id"])
    
    return {
        "status": "valid",
        "session_code": session_code,
        "session_uuid": session["session_id"],
        "message": "Room is ready. Please enter your team's players.",
        "current_teams_count": teams_count # Tells frontend how many computers are already joined
    }

@router.post("")
async def join_session_as_team(request: JoinTeamRequest):
    """
    Registers an entire team from one computer Interface.
    Creates a Team record, and bulk creates the Player records.
    """
    # 1. Verify Session
    session = get_session_by_code(request.session_code)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    session_uuid = session["session_id"]
    
    # 2. Add players constraint (a team must have at least one player)
    if len(request.player_names) == 0:
        raise HTTPException(status_code=400, detail="A team must have at least one player.")

    # 3. Create a Team in the database linked to this Session
    new_team_id = create_team(session_uuid)
    if not new_team_id:
        raise HTTPException(status_code=500, detail="Failed to create team.")
    
    # 4. Prepare data for all players and bulk insert them into `player` table
    inserted_players = bulk_create_players(new_team_id, request.player_names)
    if not inserted_players:
        raise HTTPException(status_code=500, detail="Failed to insert players into the team.")
        
    # 5. Return the bundle to the frontend computer so it can render the Shot Selection interface
    return {
        "status": "success",
        "message": f"Team created with {len(inserted_players)} players.",
        "team_id": new_team_id,
        "players": inserted_players
    }
