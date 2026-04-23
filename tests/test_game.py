from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest

from app.main import app
from app.models.schemas import ShotRecord

client = TestClient(app)

# Helper function to generate a valid test payload
def get_valid_payload():
    return {
        "player_id": "123e4567-e89b-12d3-a456-426614174001",
        "team_id": "123e4567-e89b-12d3-a456-426614174002",
        "session_id": "123e4567-e89b-12d3-a456-426614174003",
        "round_number": 1,
        "zone": 1,
        "shot_made": True
    }

@patch('app.routes.game.increment_player_stats')
@patch('app.routes.game.record_shot_in_db')
def test_submit_shot_success_make(mock_record_shot, mock_increment_player_stats):
    # Setup mock to return a valid UUID string
    mock_record_shot.return_value = "123e4567-e89b-12d3-a456-426614174004"

    payload = get_valid_payload()
    payload["zone"] = 1
    payload["shot_made"] = True

    response = client.post("/api/game/shot", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["shot_id"] == "123e4567-e89b-12d3-a456-426614174004"
    assert data["points_awarded"] == 1

    # Verify the mock was called correctly
    mock_record_shot.assert_called_once_with(ShotRecord(
        player_id=payload["player_id"],
        team_id=payload["team_id"],
        session_id=payload["session_id"],
        round_number=payload["round_number"],
        zone=payload["zone"],
        is_make=payload["shot_made"],
        make_value=1,
        location_value=1,
        points=1
    ))
    mock_increment_player_stats.assert_called_once_with(payload["player_id"], 1, True)

@patch('app.routes.game.increment_player_stats')
@patch('app.routes.game.record_shot_in_db')
def test_submit_shot_success_miss(mock_record_shot, mock_increment_player_stats):
    mock_record_shot.return_value = "123e4567-e89b-12d3-a456-426614174005"

    payload = get_valid_payload()
    payload["zone"] = 2  # Inside arc (2 pts if made)
    payload["shot_made"] = False  # Missed

    response = client.post("/api/game/shot", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["shot_id"] == "123e4567-e89b-12d3-a456-426614174005"
    assert data["points_awarded"] == 0

    mock_record_shot.assert_called_once_with(ShotRecord(
        player_id=payload["player_id"],
        team_id=payload["team_id"],
        session_id=payload["session_id"],
        round_number=payload["round_number"],
        zone=payload["zone"],
        is_make=payload["shot_made"],
        make_value=0,
        location_value=2,
        points=0
    ))
    mock_increment_player_stats.assert_called_once_with(payload["player_id"], 0, False)

@patch('app.routes.game.increment_player_stats')
@patch('app.routes.game.record_shot_in_db')
def test_submit_shot_different_zones(mock_record_shot, mock_increment_player_stats):
    mock_record_shot.return_value = "fake-id"

    # Test zone 3 (2 points)
    payload_zone3 = get_valid_payload()
    payload_zone3["zone"] = 3
    payload_zone3["shot_made"] = True
    response = client.post("/api/game/shot", json=payload_zone3)
    assert response.status_code == 200
    assert response.json()["points_awarded"] == 2

    # Test zone 4 (3 points)
    payload_zone4 = get_valid_payload()
    payload_zone4["zone"] = 4
    payload_zone4["shot_made"] = True
    response = client.post("/api/game/shot", json=payload_zone4)
    assert response.status_code == 200
    assert response.json()["points_awarded"] == 3
    assert mock_increment_player_stats.call_count == 2



@patch('app.routes.game.record_shot_in_db')
def test_submit_shot_db_failure(mock_record_shot):
    # Setup mock to return None, simulating DB failure
    mock_record_shot.return_value = None

    payload = get_valid_payload()

    response = client.post("/api/game/shot", json=payload)

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to record shot."

def test_submit_shot_invalid_payload():
    # Missing required fields like player_id, team_id, etc.
    invalid_payload = {
        "zone": 1,
        "shot_made": True
    }

    response = client.post("/api/game/shot", json=invalid_payload)

    # FastAPI automatically validates and returns 422 for invalid payloads
    assert response.status_code == 422
