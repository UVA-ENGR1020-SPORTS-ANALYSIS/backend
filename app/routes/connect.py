import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client

router = APIRouter(prefix="/api/connect", tags=["connect"])

def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        raise HTTPException(status_code=500, detail="Supabase env variables missing.")
    return create_client(url, key)

class JoinTeamRequest(BaseModel):
    session_code: int             # The 6-digit PIN to join the game
    player_names: list[str]       # An array of names like ["Alice", "Bob", "Charlie"]
    player_number: int            # The number of players in the team

@router.get("/{session_code}")
async def check_session(session_code: int):
    """
    Checks if a room (session_code) exists before the frontend allows typing player names.
    """
    supabase = get_supabase()
    
    session_res = supabase.table("sessions").select("*").eq("session_code", session_code).execute()
    
    if not session_res.data:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session = session_res.data[0]
    
    # Optional: fetch how many teams are already in this room
    teams_res = supabase.table("teams").select("team_id").eq("current_session", session["session_id"]).execute()
    
    return {
        "status": "valid",
        "session_code": session_code,
        "session_uuid": session["session_id"],
        "message": "Room is ready. Please enter your team's players.",
        "current_teams_count": len(teams_res.data) # Tells frontend how many computers are already joined
    }

@router.post("")
async def join_session_as_team(request: JoinTeamRequest):
    """
    Registers an entire team from one computer Interface.
    Creates a Team record, and bulk creates the Player records.
    """
    supabase = get_supabase()
    
    # 1. Verify Session
    session_res = supabase.table("sessions").select("session_id").eq("session_code", request.session_code).execute()
    if not session_res.data:
        raise HTTPException(status_code=404, detail="Session not found.")
    session_uuid = session_res.data[0]["session_id"]
    
    # 2. Add players constraint (a team must have at least one player)
    if len(request.player_names) == 0:
        raise HTTPException(status_code=400, detail="A team must have at least one player.")

    # 3. Create a Team in the database linked to this Session
    team_insert = supabase.table("teams").insert({"current_session": session_uuid}).execute()
    if not team_insert.data:
        raise HTTPException(status_code=500, detail="Failed to create team.")
    new_team_id = team_insert.data[0]["team_id"]
    
    # 4. Prepare data for all players and bulk insert them into `player` table
    players_data = [
        {"player_team_id": new_team_id, "player_name": name}
        for name in request.player_names
    ]
    
    players_insert = supabase.table("player").insert(players_data).execute()
    if not players_insert.data:
        raise HTTPException(status_code=500, detail="Failed to insert players into the team.")
        
    # 5. Return the bundle to the frontend computer so it can render the Shot Selection interface
    return {
        "status": "success",
        "message": f"Team created with {len(players_insert.data)} players.",
        "team_id": new_team_id,
        "players": players_insert.data
    }
