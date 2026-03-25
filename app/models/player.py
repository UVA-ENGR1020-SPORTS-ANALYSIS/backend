from pydantic import BaseModel

class Player(BaseModel):
    player_id: str
    player_team_id: str
    player_name: str
    player_stats: dict