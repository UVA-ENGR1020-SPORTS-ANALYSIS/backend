import pytest
from unittest.mock import patch, MagicMock

from app.supabase_wrapper.teams import create_team

@patch('app.supabase_wrapper.teams.get_client')
def test_create_team_success(mock_get_client):
    # Setup mock
    mock_supabase = MagicMock()
    mock_get_client.return_value = mock_supabase

    # Mocking the chain: table("teams").insert({"current_session": session_uuid}).execute()
    mock_execute = MagicMock()
    mock_execute.data = [{"team_id": "test_team_id"}]

    mock_insert = MagicMock()
    mock_insert.execute.return_value = mock_execute

    mock_table = MagicMock()
    mock_table.insert.return_value = mock_insert

    mock_supabase.table.return_value = mock_table

    # Execute
    session_uuid = "test_session_uuid"
    result = create_team(session_uuid)

    # Assert
    assert result == "test_team_id"
    mock_supabase.table.assert_called_once_with("teams")
    mock_table.insert.assert_called_once_with({"current_session": session_uuid})
    mock_insert.execute.assert_called_once()

@patch('app.supabase_wrapper.teams.get_client')
def test_create_team_no_data(mock_get_client):
    # Setup mock
    mock_supabase = MagicMock()
    mock_get_client.return_value = mock_supabase

    mock_execute = MagicMock()
    mock_execute.data = [] # No data returned

    mock_insert = MagicMock()
    mock_insert.execute.return_value = mock_execute

    mock_table = MagicMock()
    mock_table.insert.return_value = mock_insert

    mock_supabase.table.return_value = mock_table

    # Execute
    session_uuid = "test_session_uuid"
    result = create_team(session_uuid)

    # Assert
    assert result is None
    mock_supabase.table.assert_called_once_with("teams")
    mock_table.insert.assert_called_once_with({"current_session": session_uuid})
    mock_insert.execute.assert_called_once()
