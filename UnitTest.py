
import unittest

from io import StringIO
from IndividualPassMap_CompleteTournament import plot_pass_maps, get_user_input  
from unittest.mock import patch, MagicMock
class TestPlotPassMaps(unittest.TestCase):

    @patch('builtins.input', side_effect=['competition_id', 'season_id', 'home_team'])
    def test_get_user_input(self, mock_input):
        expected_result = ('competition_id', 'season_id', 'home_team')
        self.assertEqual(get_user_input(), expected_result)

    @patch('IndividualPassMap_CompleteTournament.sb.events')
    @patch('IndividualPassMap_CompleteTournament.parser.lineup')
    @patch('sys.stdout', new_callable=StringIO)
    def test_plot_pass_maps(self, mock_stdout, mock_lineup, mock_events):
        # Mock data
        home_team = 'Home Team'
        away_team = 'Away Team'
        mock_events.return_value = MagicMock()  
        mock_lineup.return_value = MagicMock()  
        
        # Call the function
        plot_pass_maps(home_team, away_team, mock_events.return_value, mock_lineup.return_value)

        # Check if expected output is in the printed output
        self.assertIn(f'{home_team}: Pass Receipt Heatmap', mock_stdout.getvalue())

if __name__ == '__main__':
    unittest.main()