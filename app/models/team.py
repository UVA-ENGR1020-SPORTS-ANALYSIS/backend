from pydantic import BaseModel

class Team(BaseModel):
    team_id: str
    wins: int = 0
    losses: int = 0
