from fastapi import APIRouter, HTTPException

from app.supabase_wrapper.sessions import get_session_by_code
from app.supabase_wrapper.teams import get_teams_count_by_session, create_team
from app.supabase_wrapper.players import bulk_create_players

from app.models.schemas import (
    CheckSessionResponse,
    JoinTeamRequest,
    JoinTeamResponse
)

router = APIRouter(prefix="/api/connect", tags=["connect"])

@router.get("/{session_code}", response_model=CheckSessionResponse)
async def check_session(session_code: int):
    """
    Checks if a room (session_code) exists before the frontend allows typing player names.
    """
    session = get_session_by_code(session_code)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Optional: fetch how many teams are already in this room
    teams_count = get_teams_count_by_session(session["session_id"])
    
    if teams_count >= session.get("target_team", 2):
        raise HTTPException(status_code=403, detail="Room is already full.")
    
    return CheckSessionResponse(
        status="valid",
        session_code=session_code,
        session_id=session["session_id"],
        current_teams_count=teams_count,
        message="Room is ready. Please enter your team's players."
    )

@router.post("", response_model=JoinTeamResponse)
async def join_session_as_team(request: JoinTeamRequest):
    """
    Registers an entire team from one computer Interface.
    Creates a Team record, and bulk creates the Player records.
    """
    # 1. Verify Session (Supports both session_id directly or session_code fallback)
    session_uuid = request.session_id
    
    if not session_uuid:
        if not request.session_code:
            raise HTTPException(status_code=400, detail="Must provide session_id or session_code.")
        session = get_session_by_code(request.session_code)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found.")
        session_uuid = session["session_id"]
        
        # Check if session is full
        current_teams_count = get_teams_count_by_session(session_uuid)
        if current_teams_count >= session.get("target_team", 2):
            raise HTTPException(status_code=403, detail="Room is already full.")
    
    # 2. Add players constraint (a team must have at least one player)
    if len(request.player_names) == 0:
        raise HTTPException(status_code=400, detail="A team must have at least one player.")

    # 3. Create a Team in the database linked to this Session
    new_team_id = create_team(str(session_uuid))
    if not new_team_id:
        raise HTTPException(status_code=500, detail="Failed to create team.")
    
    # 4. Prepare data for all players and bulk insert them into `player` table
    inserted_players = bulk_create_players(new_team_id, request.player_names)
    if not inserted_players:
        raise HTTPException(status_code=500, detail="Failed to insert players into the team.")
        
    # 5. Return the bundle to the frontend computer so it can render the Shot Selection interface
    return JoinTeamResponse(
        status="success",
        team_id=new_team_id,
        players=inserted_players,
        message=f"Team created with {len(inserted_players)} players."
    )
