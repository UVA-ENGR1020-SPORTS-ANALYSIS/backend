from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from app.main import app


client = TestClient(app)


def test_create_session_falls_back_when_supabase_fails():
    with patch("app.routes.sessions.get_client", side_effect=Exception("no db")):
        response = client.post("/api/sessions", json={"team_count": 2})

    assert response.status_code == 200
    body = response.json()
    assert 100000 <= body["session_code"] <= 999999
    assert body["session_id"]


def test_create_session_returns_503_when_candidates_are_exhausted():
    supabase = MagicMock()
    sessions_table = MagicMock()
    supabase.table.return_value = sessions_table
    sessions_table.select.return_value.in_.return_value.execute.return_value.data = [
        {"session_code": 111111}
    ]

    with patch("app.routes.sessions.get_client", return_value=supabase):
        with patch("app.routes.sessions.random.randint", return_value=111111):
            response = client.post("/api/sessions", json={"team_count": 2})

    assert response.status_code == 503
    assert response.json() == {"detail": "Could not generate a unique session code. Try again."}
    sessions_table.insert.assert_not_called()


def test_get_session_details_rejects_non_integer_session_code():
    response = client.get("/api/sessions/not-a-number")

    assert response.status_code == 422


def test_list_sessions_requires_admin_key(monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "secret")

    response = client.get("/api/sessions")

    assert response.status_code == 401


def test_list_sessions_sanitizes_admin_response(monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "secret")
    sessions = [{"session_code": 123456, "status": "waiting", "target_team": 2}]

    with patch("app.routes.sessions.list_sessions_records", return_value={"sessions": sessions}) as mock_list:
        response = client.get("/api/sessions", headers={"X-Admin-Key": "secret"})

    assert response.status_code == 200
    assert response.json() == {"sessions": sessions}
    assert "session_id" not in response.json()["sessions"][0]
    mock_list.assert_called_once_with()


def test_end_session_requires_admin_key(monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "secret")

    response = client.delete("/api/sessions/123e4567-e89b-12d3-a456-426614174000")

    assert response.status_code == 401
