from pydantic import BaseModel
from typing import Optional

class Player(BaseModel):
    player_id: str
    player_team_id: str
    player_name: str
    total_points: Optional[int] = 0
    total_makes: Optional[int] = 0
    total_attempts: Optional[int] = 0
    shooting_pct: Optional[float] = 0.0