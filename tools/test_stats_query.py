#!/usr/bin/env python3
"""Regression tests for tools/stats_query.py using the current S18 snapshot."""

from __future__ import annotations

import unittest

import stats_query as sq


class StatsQueryTest(unittest.TestCase):
    def test_match_result_1037(self):
        result = sq.match_result("1037")
        self.assertEqual(result.row_count, 1)
        row = result.rows[0]
        self.assertEqual(row["team_a"], "NAVI")
        self.assertEqual(row["team_b"], "AE")
        self.assertEqual(row["score_a"], 0)
        self.assertEqual(row["score_b"], 2)
        self.assertEqual(row["winner"], "team_b")
        self.assertTrue(result.snapshot_verified)

    def test_player_season(self):
        result = sq.player_season("MORENOOO")
        self.assertEqual(result.row_count, 1)
        row = result.rows[0]
        self.assertEqual(row["team"], "BIGETRON BY VIT")
        self.assertEqual(row["total_games"], 39)
        self.assertEqual(row["lane"], "MID")

    def test_player_season_is_case_insensitive(self):
        result = sq.player_season("morenooo")
        self.assertEqual(result.row_count, 1)
        self.assertEqual(result.rows[0]["player"], "MORENOOO")

    def test_team_season_matches_display_name(self):
        result = sq.team_season("BIGETRON BY VIT")
        self.assertEqual(result.row_count, 1)
        self.assertEqual(result.rows[0]["team"], "BTR")
        self.assertEqual(result.rows[0]["games"], 39)

    def test_game_players_has_ten_rows_and_items(self):
        result = sq.game_players("1037", "1")
        self.assertEqual(result.row_count, 10)
        self.assertTrue(all(row["items_json"] for row in result.rows))
        self.assertEqual({row["team"] for row in result.rows}, {"AE", "NAVI"})

    def test_unknown_query_is_rejected(self):
        with self.assertRaises(sq.StatsQueryError):
            sq.run_query("Q-NOT-A-QUERY", {})

    def test_player_filter_by_hero(self):
        result = sq.player_games("MORENOOO", hero="Ling")
        self.assertTrue(all(str(row["hero"]).upper() == "LING" for row in result.rows))
        self.assertIn("filtered in memory", result.provenance)

    def test_schedule_all_is_72_completed_series(self):
        result = sq.schedule_all()
        self.assertEqual(result.row_count, 72)
        self.assertEqual({row["match_detail_id"] for row in result.rows}, {str(i) for i in range(1036, 1108)})

    def test_all_games_is_174(self):
        result = sq.all_games()
        self.assertEqual(result.row_count, 174)
        self.assertEqual(sum(int(row["duration_sec"] or 0) > 0 for row in result.rows), 174)

    def test_match_player_lines_excludes_item_urls(self):
        result = sq.match_player_lines("1042")
        self.assertEqual(result.row_count, 30)
        self.assertNotIn("items_json", result.fields)
        self.assertNotIn("talents_json", result.fields)
        self.assertEqual({row["team"] for row in result.rows}, {"BTR", "GEEK"})

    def test_all_picks_and_bans(self):
        self.assertEqual(sq.all_picks().row_count, 1740)
        self.assertEqual(sq.all_bans().row_count, 1738)

    def test_all_season_aggregates(self):
        self.assertEqual(sq.all_team_season().row_count, 9)
        self.assertEqual(sq.all_player_season().row_count, 66)
        self.assertEqual(sq.all_hero_stats().row_count, 133)

    def test_all_match_details_has_72_mvps(self):
        result = sq.all_match_details()
        self.assertEqual(result.row_count, 72)
        self.assertTrue(any(row["liq_mvp"] for row in result.rows))


if __name__ == "__main__":
    unittest.main(verbosity=2)
