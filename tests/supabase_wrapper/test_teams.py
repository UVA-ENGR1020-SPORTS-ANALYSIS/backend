import pytest
from unittest.mock import patch, MagicMock

from app.supabase_wrapper.teams import set_team_ready

@patch("app.supabase_wrapper.teams.get_client")
def test_set_team_ready_success(mock_get_client):
    """
    Test set_team_ready when supabase executes successfully.
    """
    mock_supabase = MagicMock()
    mock_get_client.return_value = mock_supabase

    # Configure the mock chain: supabase.table().update().eq().execute()
    mock_table = MagicMock()
    mock_update = MagicMock()
    mock_eq = MagicMock()
    mock_execute = MagicMock()

    mock_supabase.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_eq.execute.return_value = mock_execute

    team_id = "test_team_id"
    is_ready = True

    result = set_team_ready(team_id, is_ready)

    assert result is True
    mock_supabase.table.assert_called_once_with("teams")
    mock_table.update.assert_called_once_with({"is_ready": is_ready})
    mock_update.eq.assert_called_once_with("team_id", team_id)
    mock_eq.execute.assert_called_once()

@patch("app.supabase_wrapper.teams.get_client")
def test_set_team_ready_error(mock_get_client):
    """
    Test set_team_ready when supabase throws an exception.
    """
    mock_supabase = MagicMock()
    mock_get_client.return_value = mock_supabase

    # Configure the mock chain to raise an exception on execute()
    mock_table = MagicMock()
    mock_update = MagicMock()
    mock_eq = MagicMock()

    mock_supabase.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_eq.execute.side_effect = Exception("Test Database Error")

    team_id = "test_team_id"
    is_ready = True

    result = set_team_ready(team_id, is_ready)

    assert result is False
    mock_supabase.table.assert_called_once_with("teams")
    mock_table.update.assert_called_once_with({"is_ready": is_ready})
    mock_update.eq.assert_called_once_with("team_id", team_id)
    mock_eq.execute.assert_called_once()
