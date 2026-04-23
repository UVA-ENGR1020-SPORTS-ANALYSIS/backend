from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_update_player_requires_admin_key(monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "secret")

    response = client.put(
        "/api/players/123e4567-e89b-12d3-a456-426614174000",
        json={
            "player_id": "123e4567-e89b-12d3-a456-426614174000",
            "player_team_id": "123e4567-e89b-12d3-a456-426614174111",
            "player_name": "Alice",
        },
    )

    assert response.status_code == 401
