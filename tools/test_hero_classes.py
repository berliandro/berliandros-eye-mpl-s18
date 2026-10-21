"""Hero metadata gates: every played hero has a role, lane and damage type."""
import json
import sqlite3
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
from season import ROOT, resolve

LANES = {"EXP", "JUNGLE", "MID", "GOLD", "ROAM"}
DAMAGE = {"physical", "magic", "mixed", "unknown"}


class HeroClassesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / "data" / "global" / "hero_classes.json"
        cls.data = json.loads(path.read_text(encoding="utf-8"))
        cls.heroes = cls.data["heroes"]
        cls.season = resolve("s18")
        cls.con = sqlite3.connect(cls.season["database"])

    @classmethod
    def tearDownClass(cls):
        cls.con.close()

    def test_every_hero_has_role_and_lane(self):
        missing = [h for h, v in self.heroes.items()
                   if not v.get("primary_role") or not v.get("primary_lane")]
        self.assertEqual(missing, [])

    def test_every_picked_hero_is_covered(self):
        picked = {r[0] for r in self.con.execute("SELECT DISTINCT hero FROM game_picks")}
        self.assertEqual(sorted(picked - set(self.heroes)), [])

    def test_every_database_hero_is_covered(self):
        db = {r[0] for r in self.con.execute(
            "SELECT hero FROM hero_stats UNION SELECT hero FROM game_players")}
        self.assertEqual(sorted(db - set(self.heroes)), [])

    def test_lanes_and_damage_types_are_valid(self):
        bad_lanes = {h: v["primary_lane"] for h, v in self.heroes.items()
                     if v["primary_lane"] not in LANES}
        bad_damage = {h: v["damage_type"] for h, v in self.heroes.items()
                      if v["damage_type"] not in DAMAGE}
        self.assertEqual(bad_lanes, {})
        self.assertEqual(bad_damage, {})

    def test_no_unknown_damage_type(self):
        unknown = [h for h, v in self.heroes.items() if v["damage_type"] == "unknown"]
        self.assertEqual(unknown, [])

    def test_damage_type_is_labelled_as_derived(self):
        for h, v in self.heroes.items():
            self.assertEqual(v["damage_type_source"], "derived:ability_text", h)

    def test_empirical_lanes_match_picks(self):
        for hero, v in self.heroes.items():
            rows = dict(self.con.execute(
                "SELECT lane, COUNT(*) FROM game_picks WHERE hero=? GROUP BY lane", (hero,)))
            emp = {ln: d["picks"] for ln, d in v["lanes_empirical"].items()}
            self.assertEqual(emp, rows, hero)
            total = sum(rows.values())
            if total:
                for ln, d in v["lanes_empirical"].items():
                    self.assertAlmostEqual(d["share"], d["picks"] / total, places=3, msg=f"{hero} {ln}")


if __name__ == "__main__":
    unittest.main(verbosity=1)
