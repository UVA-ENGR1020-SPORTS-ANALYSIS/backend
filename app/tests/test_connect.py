from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest

from app.main import app
from app.models.schemas import CheckSessionResponse

client = TestClient(app)

def test_check_session_success():
    """Test successful check_session where session exists and is not full."""
    mock_session = {
        "session_id": "123e4567-e89b-12d3-a456-426614174000",
        "session_code": 123456,
        "target_team": 2
    }

    with patch("app.routes.connect.get_session_by_code") as mock_get_session:
        with patch("app.routes.connect.get_teams_count_by_session") as mock_get_teams_count:
            mock_get_session.return_value = mock_session
            mock_get_teams_count.return_value = 1  # Less than target_team (2)

            response = client.get("/api/connect/123456")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "valid"
            assert data["session_code"] == 123456
            assert data["session_id"] == "123e4567-e89b-12d3-a456-426614174000"
            assert data["current_teams_count"] == 1
            mock_get_session.assert_called_once_with(123456)
            mock_get_teams_count.assert_called_once_with("123e4567-e89b-12d3-a456-426614174000")

def test_check_session_not_found():
    """Test check_session when the session code doesn't exist."""
    with patch("app.routes.connect.get_session_by_code") as mock_get_session:
        mock_get_session.return_value = None

        response = client.get("/api/connect/999999")

        assert response.status_code == 404
        assert response.json() == {"detail": "Session not found"}
        mock_get_session.assert_called_once_with(999999)

def test_check_session_full():
    """Test check_session when the session has reached its target team count."""
    mock_session = {
        "session_id": "123e4567-e89b-12d3-a456-426614174000",
        "session_code": 123456,
        "target_team": 2
    }

    with patch("app.routes.connect.get_session_by_code") as mock_get_session:
        with patch("app.routes.connect.get_teams_count_by_session") as mock_get_teams_count:
            mock_get_session.return_value = mock_session
            mock_get_teams_count.return_value = 2  # Equal to target_team (2)

            response = client.get("/api/connect/123456")

            assert response.status_code == 403
            assert response.json() == {"detail": "Room is already full."}
            mock_get_session.assert_called_once_with(123456)
            mock_get_teams_count.assert_called_once_with("123e4567-e89b-12d3-a456-426614174000")

def test_check_session_full_default_target():
    """Test check_session when the session has reached its target team count but target_team is not set in DB."""
    mock_session = {
        "session_id": "123e4567-e89b-12d3-a456-426614174000",
        "session_code": 123456,
        # missing "target_team", so it defaults to 2
    }

    with patch("app.routes.connect.get_session_by_code") as mock_get_session:
        with patch("app.routes.connect.get_teams_count_by_session") as mock_get_teams_count:
            mock_get_session.return_value = mock_session
            mock_get_teams_count.return_value = 2  # Equal to default target_team (2)

            response = client.get("/api/connect/123456")

            assert response.status_code == 403
            assert response.json() == {"detail": "Room is already full."}
            mock_get_session.assert_called_once_with(123456)
            mock_get_teams_count.assert_called_once_with("123e4567-e89b-12d3-a456-426614174000")
