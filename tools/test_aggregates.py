"""Team aggregate gates: derived rows must reconcile with player rows."""
import sqlite3
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
from season import resolve


class AggregateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.season = resolve("s18")
        cls.con = sqlite3.connect(cls.season["database"])

    @classmethod
    def tearDownClass(cls):
        cls.con.close()

    def test_one_row_per_team_per_game(self):
        rows = self.con.execute(
            "SELECT match_detail_id, game_no, team, COUNT(*) c FROM team_games "
            "GROUP BY 1,2,3 HAVING c > 1").fetchall()
        self.assertEqual(rows, [])

    def test_two_teams_per_game(self):
        rows = self.con.execute(
            "SELECT match_detail_id, game_no, COUNT(*) c FROM team_games "
            "GROUP BY 1,2 HAVING c <> 2").fetchall()
        self.assertEqual(rows, [])

    def test_five_players_per_team_game(self):
        self.assertEqual(self.con.execute(
            "SELECT DISTINCT players FROM team_games").fetchall(), [(5,)])

    def test_team_totals_match_player_totals(self):
        for col in ("kills", "deaths", "assists", "gold", "hero_damage",
                    "damage_taken", "tower_damage"):
            team = self.con.execute(f"SELECT SUM({col}) FROM team_games").fetchone()[0]
            player = self.con.execute(f"SELECT SUM({col}) FROM game_players").fetchone()[0]
            self.assertEqual(team, player, col)

    def test_every_game_has_one_winner(self):
        rows = self.con.execute(
            "SELECT match_detail_id, game_no, SUM(win) w FROM team_games "
            "GROUP BY 1,2 HAVING w <> 1").fetchall()
        self.assertEqual(rows, [])

    def test_season_wins_match_standings(self):
        rows = self.con.execute(
            "SELECT s.team_slug, s.game_win, t.wins, s.game_lose, t.losses "
            "FROM standings s JOIN team_season_stats t ON t.team_slug = s.team_slug").fetchall()
        self.assertEqual(len(rows), 9)
        for slug, gw, tw, gl, tl in rows:
            self.assertEqual((gw, gl), (tw, tl), slug)

    def test_season_totals_match_team_games(self):
        for col in ("games", "wins", "losses", "kills", "deaths", "assists",
                    "gold", "hero_damage", "damage_taken", "tower_damage"):
            season = self.con.execute(f"SELECT SUM({col}) FROM team_season_stats").fetchone()[0]
            if col == "games":
                expected = self.con.execute("SELECT COUNT(*) FROM team_games").fetchone()[0]
            elif col == "wins":
                expected = self.con.execute("SELECT SUM(win) FROM team_games").fetchone()[0]
            elif col == "losses":
                expected = self.con.execute("SELECT SUM(1-win) FROM team_games").fetchone()[0]
            else:
                expected = self.con.execute(f"SELECT SUM({col}) FROM team_games").fetchone()[0]
            self.assertEqual(season, expected, col)

    def test_team_names_and_slugs_populated(self):
        rows = self.con.execute(
            "SELECT team FROM team_season_stats WHERE team_name IS NULL OR team_name='' "
            "OR team_slug IS NULL OR team_slug=''").fetchall()
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main(verbosity=1)
