from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app

client = TestClient(app)


def test_check_session_uses_combined_session_lookup():
    session = {
        "session_id": "123e4567-e89b-12d3-a456-426614174000",
        "session_code": 123456,
        "target_team": 2,
    }

    with patch("app.routes.connect.get_session_by_code_with_team_count") as mock_lookup:
        mock_lookup.return_value = (session, 1)

        response = client.get("/api/connect/123456")

    assert response.status_code == 200
    assert response.json()["current_teams_count"] == 1
    mock_lookup.assert_called_once_with(123456)


def test_join_session_as_team_rejects_empty_player_names():
    response = client.post(
        "/api/connect",
        json={
            "session_id": "123e4567-e89b-12d3-a456-426614174000",
            "player_names": [],
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "A team must have at least one player."}


def test_join_session_as_team_success():
    session = {
        "session_id": "123e4567-e89b-12d3-a456-426614174000",
        "session_code": 123456,
        "target_team": 2,
    }
    team_id = "123e4567-e89b-12d3-a456-426614174111"
    players = [
        {"player_id": "123e4567-e89b-12d3-a456-426614174201", "player_name": "Alice"},
        {"player_id": "123e4567-e89b-12d3-a456-426614174202", "player_name": "Bob"},
    ]

    with patch("app.routes.connect.get_session_by_code_with_team_count") as mock_lookup:
        with patch("app.routes.connect.create_team") as mock_create_team:
            with patch(
                "app.routes.connect.bulk_create_players"
            ) as mock_bulk_create_players:
                mock_lookup.return_value = (session, 1)
                mock_create_team.return_value = team_id
                mock_bulk_create_players.return_value = players

                response = client.post(
                    "/api/connect",
                    json={"session_code": 123456, "player_names": ["Alice", "Bob"]},
                )

    assert response.status_code == 200
    assert response.json()["team_id"] == team_id
    assert response.json()["players"] == players
    mock_lookup.assert_called_once_with(123456)
    mock_create_team.assert_called_once_with(session["session_id"])
    mock_bulk_create_players.assert_called_once_with(team_id, ["Alice", "Bob"])


def test_join_session_as_team_room_full():
    session = {
        "session_id": "123e4567-e89b-12d3-a456-426614174000",
        "session_code": 123456,
        "target_team": 2,
    }

    with patch("app.routes.connect.get_session_by_code_with_team_count") as mock_lookup:
        mock_lookup.return_value = (session, 2)
        response = client.post(
            "/api/connect",
            json={
                "session_code": 123456,
                "player_names": ["Alice"],
            },
        )

    assert response.status_code == 403
    assert response.json() == {"detail": "Room is already full."}


def test_join_session_as_team_missing_session():
    response = client.post(
        "/api/connect",
        json={
            "player_names": ["Alice"],
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Must provide session_id or session_code."}


def test_join_session_as_team_session_not_found():
    with patch("app.routes.connect.get_session_by_code_with_team_count") as mock_lookup:
        mock_lookup.return_value = (None, 0)
        response = client.post(
            "/api/connect",
            json={
                "session_code": 123456,
                "player_names": ["Alice"],
            },
        )

    assert response.status_code == 404
    assert response.json() == {"detail": "Session not found."}


def test_join_session_as_team_create_team_fails():
    session = {
        "session_id": "123e4567-e89b-12d3-a456-426614174000",
        "session_code": 123456,
        "target_team": 2,
    }

    with patch("app.routes.connect.get_session_by_code_with_team_count") as mock_lookup:
        with patch("app.routes.connect.create_team") as mock_create_team:
            mock_lookup.return_value = (session, 1)
            mock_create_team.return_value = None
            response = client.post(
                "/api/connect",
                json={
                    "session_code": 123456,
                    "player_names": ["Alice"],
                },
            )

    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to create team."}


def test_join_session_as_team_insert_players_fails():
    session = {
        "session_id": "123e4567-e89b-12d3-a456-426614174000",
        "session_code": 123456,
        "target_team": 2,
    }
    team_id = "123e4567-e89b-12d3-a456-426614174111"

    with patch("app.routes.connect.get_session_by_code_with_team_count") as mock_lookup:
        with patch("app.routes.connect.create_team") as mock_create_team:
            with patch(
                "app.routes.connect.bulk_create_players"
            ) as mock_bulk_create_players:
                mock_lookup.return_value = (session, 1)
                mock_create_team.return_value = team_id
                mock_bulk_create_players.return_value = None
                response = client.post(
                    "/api/connect",
                    json={
                        "session_code": 123456,
                        "player_names": ["Alice"],
                    },
                )

    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to insert players into the team."}


def test_check_session_not_found():
    with patch("app.routes.connect.get_session_by_code_with_team_count") as mock_lookup:
        mock_lookup.return_value = (None, 0)
        response = client.get("/api/connect/123456")

    assert response.status_code == 404
    assert response.json() == {"detail": "Session not found"}


def test_check_session_room_full():
    session = {
        "session_id": "123e4567-e89b-12d3-a456-426614174000",
        "session_code": 123456,
        "target_team": 2,
    }
    with patch("app.routes.connect.get_session_by_code_with_team_count") as mock_lookup:
        mock_lookup.return_value = (session, 2)
        response = client.get("/api/connect/123456")

    assert response.status_code == 403
    assert response.json() == {"detail": "Room is already full."}


def test_toggle_team_ready_success():
    with patch("app.routes.connect.set_team_ready") as mock_set_ready:
        mock_set_ready.return_value = True
        response = client.post(
            "/api/connect/123e4567-e89b-12d3-a456-426614174111/ready",
            json={"is_ready": True},
        )

    assert response.status_code == 200
    assert response.json() == {"status": "success", "is_ready": True}


def test_toggle_team_ready_failure():
    with patch("app.routes.connect.set_team_ready") as mock_set_ready:
        mock_set_ready.return_value = False
        response = client.post(
            "/api/connect/123e4567-e89b-12d3-a456-426614174111/ready",
            json={"is_ready": True},
        )

    assert response.status_code == 404
    assert response.json() == {"detail": "Team not found or could not update status."}


def test_join_session_as_team_0_players_with_session_code():
    session = {
        "session_id": "123e4567-e89b-12d3-a456-426614174000",
        "session_code": 123456,
        "target_team": 2,
    }

    with patch("app.routes.connect.get_session_by_code_with_team_count") as mock_lookup:
        mock_lookup.return_value = (session, 1)
        response = client.post(
            "/api/connect",
            json={
                "session_code": 123456,
                "player_names": [],
            },
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "A team must have at least one player."}
