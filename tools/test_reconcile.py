"""Regression tests for the committed cross-view reconciliation gate."""
import json
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
from reconcile import build_report, canonical_maps, canon  # noqa: E402
from season import resolve  # noqa: E402


class ReconciliationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_report("s18")

    def test_all_nine_teams_reconcile(self):
        self.assertTrue(self.report["ok"], self.report["failures"])
        self.assertEqual(len(self.report["rows"]), 9)
        self.assertTrue(all(r["ok"] for r in self.report["rows"]))

    def test_match_and_game_records_are_separate(self):
        for r in self.report["rows"]:
            o, d = r["official"], r["derived"]
            self.assertEqual((o["match_win"], o["match_lose"]), (d["match_win"], d["match_lose"]), r["team"])
            self.assertEqual((o["game_win"], o["game_lose"]), (d["game_win"], d["game_lose"]), r["team"])
        # Both definitions are present and not silently substituted.
        total_match_wins = sum(r["official"]["match_win"] for r in self.report["rows"])
        total_game_wins = sum(r["official"]["game_win"] for r in self.report["rows"])
        self.assertEqual(total_match_wins, 72)
        self.assertEqual(total_game_wins, 174)

    def test_game_appearances_balanced(self):
        i = self.report["integrity"]
        self.assertTrue(i["appearance_balance"])
        self.assertEqual(i["team_game_appearances"], 348)
        self.assertEqual(i["included_games"], 174)
        self.assertTrue(i["all_games_have_one_winner"])
        self.assertTrue(i["all_teams_present"])

    def test_explicit_regular_season_scope(self):
        self.assertIn("regular-season", self.report["scope"])
        self.assertEqual(self.report["integrity"]["included_matches"], 72)

    def test_final_regular_snapshot_is_complete(self):
        paths = resolve("s18")
        cfg = json.loads(Path(paths["config"]).read_text(encoding="utf-8"))
        self.assertEqual(self.report["integrity"]["included_matches"],
                         cfg["totalRegularFixtures"])
        self.assertEqual(self.report["integrity"]["included_games"], 174)
        self.assertFalse(self.report["excluded"], self.report["excluded"])

    def test_alias_variants_resolve_one_identity(self):
        paths = resolve("s18")
        cfg = json.loads(Path(paths["config"]).read_text(encoding="utf-8"))
        aliases = canonical_maps(cfg)
        for raw in ("Team Liquid ID", "TLID", "team-liquid-id", "  Team Liquid ID  "):
            self.assertEqual(canon(raw, aliases), "TLID")
        for raw in ("Alter Ego Esports", "AE", "alter ego"):
            self.assertEqual(canon(raw, aliases), "AE")


if __name__ == "__main__":
    unittest.main(verbosity=1)
