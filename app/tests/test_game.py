from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app

client = TestClient(app)

@patch("app.routes.game.record_shot_in_db")
def test_submit_shot_db_failure(mock_record_shot):
    # Mock record_shot_in_db to return None, simulating a failure
    mock_record_shot.return_value = None

    response = client.post("/api/game/shot", json={
        "player_id": "123e4567-e89b-12d3-a456-426614174000",
        "team_id": "123e4567-e89b-12d3-a456-426614174001",
        "session_id": "123e4567-e89b-12d3-a456-426614174002",
        "round_number": 1,
        "zone": 1,
        "shot_made": True
    })

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to record shot."

@patch("app.routes.game.record_shot_in_db")
def test_submit_shot_success(mock_record_shot):
    # Mock record_shot_in_db to return a mock shot ID
    mock_record_shot.return_value = "mock_shot_id_123"

    response = client.post("/api/game/shot", json={
        "player_id": "123e4567-e89b-12d3-a456-426614174000",
        "team_id": "123e4567-e89b-12d3-a456-426614174001",
        "session_id": "123e4567-e89b-12d3-a456-426614174002",
        "round_number": 1,
        "zone": 4, # 3 pointer zone
        "shot_made": True
    })

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["shot_id"] == "mock_shot_id_123"
    assert data["points_awarded"] == 3
