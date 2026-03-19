from pydantic import BaseModel

class Shot(BaseModel):
    game_session_id: str
    player_id: str
    player_team_id: str
    shot_made: bool
    score_value: int
    score_zone: int
    x_coordinate: float
    y_coordinate: float