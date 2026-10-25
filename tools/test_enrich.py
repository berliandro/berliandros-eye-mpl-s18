"""Offline tests for the Liquipedia draft/lane enrichment.

Covers the Map-template parser, hero identity folding, duplicate-ban repair and
a data-quality gate over the committed database. No network access.
"""
import sqlite3
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))

from enrich_drafts import (LANES, MAP_MODE_ALIASES, canonical_hero, dedupe_bans,
                           hero_key, parse_series, remove_blank_bans)
from season import resolve

FIXTURE = """|M1={{Match
|opponent1={{TeamOpponent|Alpha}}
|opponent2={{TeamOpponent|Beta}}
|map1={{Map|team1side=blue|team2side=red|length=16:51|winner=1|mapmode=Broken Walls
|t1h1=alpha1|t1h2=alpha2|t1h3=alpha3|t1h4=alpha4|t1h5=alpha5
|t1b1=aban1|t1b2=aban2|t1b3=aban3|t1b4=aban4|t1b5=aban5
|t2h1=beta1|t2h2=beta2|t2h3=beta3|t2h4=beta4|t2h5=beta5
|t2b1=bban1|t2b2=bban2|t2b3=bban3|t2b4=bban4|t2b5=bban5
}}
|map2={{Map|finished=skip
}}
}}"""


class ParseTest(unittest.TestCase):
    def test_map_fields_and_lane_order(self):
        series = parse_series(FIXTURE)
        self.assertEqual(len(series), 1)
        self.assertEqual((series[0]["t1"], series[0]["t2"]), ("Alpha", "Beta"))
        self.assertEqual(len(series[0]["maps"]), 1, "finished=skip map must be dropped")
        m = series[0]["maps"][0]
        self.assertEqual(m["no"], 1)
        self.assertEqual(m["team1side"], "blue")
        self.assertEqual(m["winner"], "1")
        self.assertEqual(m["mapmode"], "Broken Walls")
        self.assertEqual(m["t1h"], ["alpha1", "alpha2", "alpha3", "alpha4", "alpha5"])
        self.assertEqual(m["t2h"], ["beta1", "beta2", "beta3", "beta4", "beta5"])
        self.assertEqual(m["t1b"], ["aban1", "aban2", "aban3", "aban4", "aban5"])
        self.assertEqual(m["t2b"], ["bban1", "bban2", "bban3", "bban4", "bban5"])

    def test_malformed_input_is_empty(self):
        self.assertEqual(parse_series(""), [])
        self.assertEqual(parse_series("|M1={{Match|opponent1="), [])


class IdentityTest(unittest.TestCase):
    def test_short_hero_names_share_a_key(self):
        self.assertEqual(hero_key("gatot"), hero_key("Gatotkaca"))
        self.assertEqual(hero_key("yss"), hero_key("Yi Sun-Shin"))

    def test_zetian_variant_folds(self):
        self.assertEqual(canonical_hero("Wu/Zetian"), "Zetian")
        self.assertEqual(canonical_hero("Zetian"), "Zetian")

    def test_map_mode_aliases(self):
        self.assertEqual(MAP_MODE_ALIASES["fc"], "Flying Cloud")
        self.assertEqual(MAP_MODE_ALIASES["rw"], "Revealing Wisps")


class DedupeTest(unittest.TestCase):
    def test_blank_ban_is_not_a_ban(self):
        con = sqlite3.connect(":memory:")
        con.execute("CREATE TABLE game_bans(match_detail_id TEXT, game_no INTEGER, "
                    "side TEXT, hero TEXT, ban_order INTEGER)")
        con.executemany("INSERT INTO game_bans VALUES(?,?,?,?,?)", [
            ("1", 1, "A", "", None),
            ("1", 1, "A", "   ", None),
            ("1", 1, "A", None, None),
            ("1", 1, "A", "Atlas", 1),
        ])
        self.assertEqual(remove_blank_bans(con), 3)
        self.assertEqual(con.execute("SELECT COUNT(*) FROM game_bans").fetchone()[0], 1)
        con.close()

    def test_duplicate_ban_is_removed(self):
        con = sqlite3.connect(":memory:")
        con.execute("CREATE TABLE game_bans(match_detail_id TEXT, game_no INTEGER, "
                    "side TEXT, hero TEXT, ban_order INTEGER)")
        con.executemany("INSERT INTO game_bans VALUES(?,?,?,?,?)", [
            ("1", 1, "A", "Nolan", None),
            ("1", 1, "A", "Nolan", 4),
            ("1", 1, "A", "Baxia", 1),
        ])
        self.assertEqual(dedupe_bans(con), 1)
        self.assertEqual(con.execute("SELECT COUNT(*) FROM game_bans").fetchone()[0], 2)
        con.close()


class DataGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.season = resolve("s18")
        if not cls.season["database"].exists():
            raise unittest.SkipTest("database not built")
        cls.con = sqlite3.connect(cls.season["database"])

    @classmethod
    def tearDownClass(cls):
        cls.con.close()

    def test_completed_snapshot_counts(self):
        counts = {t: self.con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                  for t in ("matches", "games", "game_players", "game_picks",
                            "team_games", "standings")}
        self.assertEqual(counts["matches"], 72)
        self.assertEqual(counts["games"], 174)
        self.assertEqual(counts["game_players"], 1740)
        self.assertEqual(counts["game_picks"], 1740)
        self.assertEqual(counts["team_games"], 348)
        self.assertEqual(counts["standings"], 9)

    def test_no_blank_or_unassigned_picks(self):
        self.assertEqual(self.con.execute(
            "SELECT COUNT(*) FROM game_picks WHERE player IS NULL OR TRIM(player)='' "
            "OR hero IS NULL OR TRIM(hero)=''").fetchone()[0], 0)
        self.assertEqual(self.con.execute(
            "SELECT COUNT(*) FROM game_bans WHERE hero IS NULL OR TRIM(hero)=''").fetchone()[0], 0)

    def test_every_player_row_has_a_lane(self):
        missing = self.con.execute(
            "SELECT COUNT(*) FROM game_players WHERE lane IS NULL OR lane=''").fetchone()[0]
        self.assertEqual(missing, 0)
        bad = self.con.execute(
            "SELECT DISTINCT lane FROM game_players WHERE lane NOT IN (?,?,?,?,?)",
            LANES).fetchall()
        self.assertEqual(bad, [])

    def test_no_duplicate_bans(self):
        rows = self.con.execute(
            "SELECT match_detail_id, game_no, side, hero, COUNT(*) c FROM game_bans "
            "GROUP BY 1,2,3,4 HAVING c > 1").fetchall()
        self.assertEqual(rows, [])

    def test_no_variant_hero_names(self):
        rows = self.con.execute(
            "SELECT DISTINCT hero FROM game_players WHERE hero LIKE '%/%'").fetchall()
        self.assertEqual(rows, [])

    def test_picks_cover_every_game(self):
        games = self.con.execute("SELECT COUNT(*) FROM games").fetchone()[0]
        covered = self.con.execute(
            "SELECT COUNT(DISTINCT match_detail_id||'-'||game_no) FROM game_picks").fetchone()[0]
        self.assertEqual(covered, games)

    def test_each_game_has_ten_picks(self):
        rows = self.con.execute(
            "SELECT match_detail_id, game_no, COUNT(*) c FROM game_picks "
            "GROUP BY 1,2 HAVING c <> 10").fetchall()
        self.assertEqual(rows, [])

    def test_ban_order_is_complete(self):
        missing = self.con.execute(
            "SELECT COUNT(*) FROM game_bans WHERE ban_order IS NULL").fetchone()[0]
        self.assertEqual(missing, 0)

    def test_map_modes_are_normalized(self):
        rows = self.con.execute(
            "SELECT DISTINCT map_mode FROM games WHERE map_mode IN ('fc','ht','rw')").fetchall()
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main(verbosity=1)
