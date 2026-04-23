from unittest.mock import MagicMock, patch

from app.models.schemas import ShotRecord
from app.supabase_wrapper.shots import get_team_stats, record_shot_in_db


def make_select_eq_eq_table(data: list[dict]) -> MagicMock:
    table = MagicMock()
    select_query = MagicMock()
    team_filter = MagicMock()
    round_filter = MagicMock()
    response = MagicMock()
    response.data = data

    table.select.return_value = select_query
    select_query.eq.return_value = team_filter
    team_filter.eq.return_value = round_filter
    round_filter.execute.return_value = response
    return table


def sample_shot_record() -> ShotRecord:
    return ShotRecord(
        player_id="player-1",
        team_id="team-1",
        session_id="session-1",
        round_number=1,
        zone=4,
        is_make=True,
        make_value=1,
        location_value=3,
        points=3,
    )


@patch("app.supabase_wrapper.shots.get_client")
def test_record_shot_in_db_success(mock_get_client):
    supabase = MagicMock()
    mock_get_client.return_value = supabase
    supabase.table.return_value.insert.return_value.execute.return_value.data = [
        {"shot_id": "shot-1"}
    ]

    result = record_shot_in_db(sample_shot_record())

    assert result == "shot-1"
    supabase.table.assert_called_once_with("shots")
    supabase.table.return_value.insert.assert_called_once_with({
        "shot_player_id": "player-1",
        "team_id": "team-1",
        "session_id": "session-1",
        "round_number": 1,
        "zone": 4,
        "shot_made": True,
        "make_value": 1,
        "location_value": 3,
        "points": 3,
    })


@patch("app.supabase_wrapper.shots.get_client")
def test_record_shot_in_db_returns_none_without_inserted_data(mock_get_client):
    supabase = MagicMock()
    mock_get_client.return_value = supabase
    supabase.table.return_value.insert.return_value.execute.return_value.data = []

    assert record_shot_in_db(sample_shot_record()) is None


@patch("app.supabase_wrapper.shots.get_client")
def test_get_team_stats_uses_aggregate_query(mock_get_client):
    supabase = MagicMock()
    mock_get_client.return_value = supabase
    query = supabase.table.return_value.select.return_value.eq.return_value.eq.return_value
    query.execute.return_value.data = [{"total_points": 8, "shots_taken": 3}]

    result = get_team_stats("team-1", 1)

    assert result == {"shots": [], "shots_taken": 3, "total_points": 8}
    supabase.table.assert_called_once_with("shots")
    supabase.table.return_value.select.assert_called_once_with(
        "total_points:points.sum(),shots_taken:shot_id.count()"
    )


@patch("app.supabase_wrapper.shots.get_client")
def test_get_team_stats_can_include_raw_shots(mock_get_client):
    supabase = MagicMock()
    mock_get_client.return_value = supabase
    stats_table = make_select_eq_eq_table([{"total_points": 3, "shots_taken": 1}])
    raw_shot = {"shot_id": "shot-1", "zone": 4, "shot_made": True, "points": 3}
    shots_table = make_select_eq_eq_table([raw_shot])
    supabase.table.side_effect = [stats_table, shots_table]

    result = get_team_stats("team-1", 1, include_shots=True)

    assert result == {"shots": [raw_shot], "shots_taken": 1, "total_points": 3}
    assert supabase.table.call_count == 2


@patch("app.supabase_wrapper.shots.get_client")
def test_get_team_stats_falls_back_when_aggregate_query_fails(mock_get_client):
    supabase = MagicMock()
    mock_get_client.return_value = supabase

    stats_table = make_select_eq_eq_table([])
    stats_table.select.return_value.eq.return_value.eq.return_value.execute.side_effect = Exception("aggregate disabled")
    fallback_table = make_select_eq_eq_table([{"points": 2}, {"points": 3}])
    supabase.table.side_effect = [stats_table, fallback_table]

    result = get_team_stats("team-1", 1)

    assert result == {"shots": [], "shots_taken": 2, "total_points": 5}
    assert supabase.table.call_count == 2
