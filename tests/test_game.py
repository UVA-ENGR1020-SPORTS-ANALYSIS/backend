from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch, MagicMock

from app.main import app

client = TestClient(app)

def test_get_opponent_stats_exception():
    with patch("app.routes.game.get_client") as mock_get_client:
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("Mocked exception")
        mock_get_client.return_value = mock_supabase

        response = client.get("/api/game/opponent_stats/session123/teamABC")

        assert response.status_code == 500
        assert response.json() == {"detail": "Failed to fetch teams."}
