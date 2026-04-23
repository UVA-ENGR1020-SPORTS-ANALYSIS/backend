from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool
from app.models.player import Player
from app.security import require_admin_key
from app.supabase_wrapper.players import (
    update_player_in_db,
    get_player_stats_from_db,
    get_players_by_team,
)

router = APIRouter(prefix="/api/players", tags=["players"])

@router.get("/team/{team_id}")
async def get_team_players(team_id: str):
    """Returns all players and their stats for a given team."""
    players = await run_in_threadpool(get_players_by_team, team_id)
    return {"team_id": team_id, "players": players}

@router.get("/{player_id}")
async def get_player_stats(player_id: str):
    """Returns a single player's stats."""
    stats = await run_in_threadpool(get_player_stats_from_db, player_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Player not found")
    return stats

@router.post("")
async def create_player(player: Player):
    # TODO: Save player to DB
    return {
        "status": "created",
        "player": player
    }

@router.put("/{player_id}")
async def update_player(player_id: str, player: Player, _: None = Depends(require_admin_key)):
    updated = await run_in_threadpool(update_player_in_db, player_id, player.player_name)

    if updated is None:
        raise HTTPException(status_code=404, detail=f"Player {player_id} not found.")

    return {
        "status": "updated",
        "player_id": player_id,
        "player": updated
    }
