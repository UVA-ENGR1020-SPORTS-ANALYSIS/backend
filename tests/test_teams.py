import unittest
from unittest.mock import patch, MagicMock
from app.supabase_wrapper.teams import set_team_ready

class TestTeams(unittest.TestCase):
    @patch("app.supabase_wrapper.teams.get_client")
    def test_set_team_ready_success(self, mock_get_client):
        mock_supabase = MagicMock()
        mock_get_client.return_value = mock_supabase

        result = set_team_ready("team-123", True)

        self.assertTrue(result)
        mock_supabase.table.assert_called_once_with("teams")
        mock_supabase.table().update.assert_called_once_with({"is_ready": True})
        mock_supabase.table().update().eq.assert_called_once_with("team_id", "team-123")
        mock_supabase.table().update().eq().execute.assert_called_once()

    @patch("app.supabase_wrapper.teams.get_client")
    def test_set_team_ready_error(self, mock_get_client):
        mock_supabase = MagicMock()
        mock_get_client.return_value = mock_supabase
        mock_supabase.table.side_effect = Exception("Database error")

        result = set_team_ready("team-123", True)

        self.assertFalse(result)
        mock_supabase.table.assert_called_once_with("teams")

if __name__ == '__main__':
    unittest.main()
