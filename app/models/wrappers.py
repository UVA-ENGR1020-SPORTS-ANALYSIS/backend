from pydantic import BaseModel
from uuid import UUID
from typing import Optional

# 1. Sessions Wrapper
class Session(BaseModel):
    session_id: UUID
    session_code: int
    status: str

# 2. Teams Wrapper
class Team(BaseModel):
    team_id: UUID
    current_session: UUID  # Foreign key linking to Sessions
    total_points: int

# 3. Player Wrapper
class Player(BaseModel):
    player_id: UUID
    player_team_id: UUID   # Foreign key linking to Teams
    player_name: str

# 4. Shots Wrapper
class Shot(BaseModel):
    shot_id: UUID
    shot_player_id: UUID   # Foreign key linking to Player
    shot_made: bool
    zone: int