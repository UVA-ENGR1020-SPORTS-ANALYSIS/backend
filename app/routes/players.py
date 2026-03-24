from fastapi import APIRouter
from app.models.player import Player

router = APIRouter(prefix="/api/players", tags=["players"])

@router.get("/{player_id}")
async def get_player_stats(player_id: str):
    # TODO: Fetch player stats from DB (naming rule `player:ID_NUMBER`)
    return {
        "player_id": player_id,
        "name": f"Player {player_id}",
        "team": "TBD",
        "total_points": 0,
        "total_assists": 0
    }

@router.post("")
async def create_player(player: Player):
    # TODO: Save player to DB
    return {
        "status": "created",
        "player": player
    }

@router.put("/{player_id}")
async def update_player(player_id: str, player: Player):
    # TODO: Update player in DB
    return {
        "status": "updated",
        "player_id": player_id,
        "player": player
    }
