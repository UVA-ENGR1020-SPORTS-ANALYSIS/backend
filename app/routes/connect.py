import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client

router = APIRouter(prefix="/api/connect", tags=["connect"])

# Define Supabase connection logic (lazy-loaded so it doesn't crash if env vars aren't set yet)
def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        raise HTTPException(status_code=500, detail="Supabase env variables missing.")
    return create_client(url, key)

class JoinSessionRequest(BaseModel):
    session_code: str
    player_name: str
    # Added team_id: according to the new schema, a Player belongs to a Team, 
    # so the frontend must specify which team the player is joining in this session.
    team_id: str 

@router.get("/{session_code}")
async def check_session(session_code: str):
    """
    Checks if a session is valid and grab the game information (including team IDs)
    so the frontend knows what teams are available to join.
    """
    supabase = get_supabase()
    
    # Fetch session from the 'games' table
    response = supabase.table("games").select("*").eq("session_id", session_code).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Session not found in games table")
        
    game = response.data[0]
    
    # Optional: check if the game is actually waiting for players
    # if game["status"] != "waiting":
    #     raise HTTPException(status_code=403, detail="Game is already in progress or finished")
    
    return {
        "status": "valid",
        "session_code": session_code,
        "message": f"Session {session_code} is active and ready to join",
        "game_info": game  # returns home_team_id and away_team_id for the frontend to use
    }

@router.post("")
async def join_session(request: JoinSessionRequest):
    """
    Validates the player's name and inserts them into the DB under the selected team.
    """
    supabase = get_supabase()
    
    # Step 1: Ensure the game exists and the team belongs to this game
    game_res = supabase.table("games").select("*").eq("session_id", request.session_code).execute()
    if not game_res.data:
        raise HTTPException(status_code=404, detail="Session not found.")
        
    game = game_res.data[0]
    
    # Validate the team_id is actually part of this game
    if request.team_id not in [game["home_team_id"], game["away_team_id"]]:
        raise HTTPException(
            status_code=400, 
            detail="The chosen team does not belong to this game session."
        )

    # Step 2: Query the chosen team's roster to check for player name duplicates
    players_res = supabase.table("players").select("name").eq("team_id", request.team_id).execute()
    existing_names = [p["name"] for p in players_res.data]
    
    if request.player_name in existing_names:
        raise HTTPException(
            status_code=400,
            detail=f"The name '{request.player_name}' is already taken in this team. Please choose another one."
        )
        
    # Step 3: Insert the new player into the 'players' table
    new_player_data = {
        "team_id": request.team_id,
        "name": request.player_name,
        # Based on your image, jersey_number is still in the schema as int4. 
        # You can pass 0 if you are auto-generating indices instead.
        "jersey_number": 0, 
        "total_points": 0,
        "total_assists": 0,
        "total_rebounds": 0,
        "total_steals": 0
    }
    
    insert_res = supabase.table("players").insert(new_player_data).execute()
    
    if not insert_res.data:
        raise HTTPException(status_code=500, detail="Failed to insert player into Database.")
        
    new_player = insert_res.data[0]
    
    # Step 4: Return success with the player's unique UUID
    return {
        "status": "success",
        "message": f"Player {request.player_name} successfully joined!",
        "player_data": new_player,
        "player_token": new_player["player_id"] # This is the UUID PK from Supabase
    }
