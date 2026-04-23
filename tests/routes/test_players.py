from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest

from app.main import app

client = TestClient(app)

@patch('app.routes.players.get_player_stats_from_db')
def test_get_player_stats_success(mock_get_player_stats):
    mock_stats = {
        "player_id": "test_player_1",
        "points": 10,
        "rebounds": 5
    }
    mock_get_player_stats.return_value = mock_stats

    response = client.get("/api/players/test_player_1")

    assert response.status_code == 200
    assert response.json() == mock_stats
    mock_get_player_stats.assert_called_once_with("test_player_1")

@patch('app.routes.players.get_player_stats_from_db')
def test_get_player_stats_not_found(mock_get_player_stats):
    mock_get_player_stats.return_value = None

    response = client.get("/api/players/non_existent_player")

    assert response.status_code == 404
    assert response.json()["detail"] == "Player not found"
    mock_get_player_stats.assert_called_once_with("non_existent_player")

@patch('app.routes.players.get_players_by_team')
def test_get_team_players_success(mock_get_players_by_team):
    mock_players = [
        {"player_id": "p1", "player_name": "Player 1"},
        {"player_id": "p2", "player_name": "Player 2"}
    ]
    mock_get_players_by_team.return_value = mock_players

    response = client.get("/api/players/team/team_123")

    assert response.status_code == 200
    assert response.json() == {
        "team_id": "team_123",
        "players": mock_players
    }
    mock_get_players_by_team.assert_called_once_with("team_123")

@patch('app.routes.players.get_players_by_team')
def test_get_team_players_empty(mock_get_players_by_team):
    mock_get_players_by_team.return_value = []

    response = client.get("/api/players/team/team_empty")

    assert response.status_code == 200
    assert response.json() == {
        "team_id": "team_empty",
        "players": []
    }
    mock_get_players_by_team.assert_called_once_with("team_empty")
