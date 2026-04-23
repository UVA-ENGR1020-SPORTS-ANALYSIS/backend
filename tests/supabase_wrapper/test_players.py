from unittest.mock import MagicMock, patch
from app.supabase_wrapper.players import bulk_create_players, calculate_player_stat_update

# NOTE: The tests below are written to match the actual implementation in the repository
# (which uses the table 'player' and keys 'player_team_id', 'player_name')
# rather than the hypothetical code snippet in the issue description,
# ensuring we test the production schema bindings accurately without regressions.

def test_calculate_player_stat_update_for_make():
    result = calculate_player_stat_update(
        {"total_points": 4, "total_makes": 2, "total_attempts": 5},
        points=3,
        made=True,
    )

    assert result == {
        "total_points": 7,
        "total_makes": 3,
        "total_attempts": 6,
        "shooting_pct": 50.0,
    }

@patch("app.supabase_wrapper.players.get_client")
def test_bulk_create_players_success(mock_get_client):
    """
    Test bulk_create_players successfully inserts data and returns it.
    """
    mock_supabase = MagicMock()
    mock_get_client.return_value = mock_supabase

    mock_table = MagicMock()
    mock_insert = MagicMock()
    mock_execute = MagicMock()

    mock_supabase.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_insert.execute.return_value = mock_execute

    expected_data = [
        {"id": 1, "player_team_id": "team_1", "player_name": "Alice"},
        {"id": 2, "player_team_id": "team_1", "player_name": "Bob"}
    ]
    mock_execute.data = expected_data

    team_id = "team_1"
    player_names = ["Alice", "Bob"]

    result = bulk_create_players(team_id, player_names)

    assert result == expected_data
    mock_get_client.assert_called_once()
    mock_supabase.table.assert_called_once_with("player")
    mock_table.insert.assert_called_once_with([
        {"player_team_id": team_id, "player_name": "Alice"},
        {"player_team_id": team_id, "player_name": "Bob"}
    ])
    mock_insert.execute.assert_called_once()

@patch("app.supabase_wrapper.players.get_client")
def test_bulk_create_players_empty_names(mock_get_client):
    """
    Test bulk_create_players with an empty list of player names.
    The current codebase implementation executes an insert with an empty list.
    """
    mock_supabase = MagicMock()
    mock_get_client.return_value = mock_supabase

    mock_table = MagicMock()
    mock_insert = MagicMock()
    mock_execute = MagicMock()

    mock_supabase.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_insert.execute.return_value = mock_execute

    mock_execute.data = []

    team_id = "team_1"
    player_names = []

    result = bulk_create_players(team_id, player_names)

    assert result is None
    mock_get_client.assert_called_once()
    mock_supabase.table.assert_called_once_with("player")
    mock_table.insert.assert_called_once_with([])
    mock_insert.execute.assert_called_once()

@patch("app.supabase_wrapper.players.get_client")
def test_bulk_create_players_no_data(mock_get_client):
    """
    Test bulk_create_players when insert().execute() returns empty data.
    """
    mock_supabase = MagicMock()
    mock_get_client.return_value = mock_supabase

    mock_table = MagicMock()
    mock_insert = MagicMock()
    mock_execute = MagicMock()

    mock_supabase.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_insert.execute.return_value = mock_execute

    mock_execute.data = []

    team_id = "team_1"
    player_names = ["Alice", "Bob"]

    result = bulk_create_players(team_id, player_names)

    assert result is None
    mock_get_client.assert_called_once()
    mock_supabase.table.assert_called_once_with("player")
    mock_table.insert.assert_called_once_with([
        {"player_team_id": team_id, "player_name": "Alice"},
        {"player_team_id": team_id, "player_name": "Bob"}
    ])
    mock_insert.execute.assert_called_once()
