from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID

# ---------------------------------------------------------
# Connection & Joining Models
# ---------------------------------------------------------

class CheckSessionResponse(BaseModel):
    status: str
    session_code: int
    session_id: UUID
    current_teams_count: int
    message: str

class JoinTeamRequest(BaseModel):
    """
    Sent by frontend to register a team into an existing session.
    """
    player_names: List[str]
    session_id: Optional[UUID] = None
    session_code: Optional[int] = None
    team_count: Optional[int] = Field(None, description="The expected number of players/teams")

class ToggleReadyRequest(BaseModel):
    is_ready: bool

class JoinTeamResponse(BaseModel):
    """
    Returned by backend after cleanly creating a Team and its Players.
    """
    status: str
    team_id: UUID
    players: List[Dict[str, Any]]
    message: str

# ---------------------------------------------------------
# Admin / Game Management Models
# ---------------------------------------------------------

class CreateSessionRequest(BaseModel):
    creator_name: Optional[str] = None
    admin_password: Optional[str] = None
    team_count: Optional[int] = None

class CreateSessionResponse(BaseModel):
    session_code: int
    session_id: UUID

# ---------------------------------------------------------
# Gameplay / Shot Models
# ---------------------------------------------------------

class SubmitShotRequest(BaseModel):
    player_id: UUID
    team_id: UUID
    session_id: UUID
    round_number: int
    zone: int
    shot_made: bool

class SubmitShotResponse(BaseModel):
    status: str
    shot_id: str
    points_awarded: int

class FinishRoundRequest(BaseModel):
    team_id: UUID
    round_number: int

class BanZoneRequest(BaseModel):
    opponent_team_id: UUID
    zone: int
