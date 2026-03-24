from pydantic import BaseModel

class Team(BaseModel):
    team_id: str
    wins: int = 0
    losses: int = 0
    team_name: str
    team_players: list[Player]
    
