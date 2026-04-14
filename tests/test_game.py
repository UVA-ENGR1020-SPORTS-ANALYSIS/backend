from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

@patch("app.routes.game.get_client")
def test_get_opponent_stats_exception(mock_get_client):
    # Setup mock to raise an exception
    mock_get_client.return_value.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("Mock DB error")

    response = client.get("/api/game/opponent_stats/mock_session/mock_team")

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to fetch teams."
