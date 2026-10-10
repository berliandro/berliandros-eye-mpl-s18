"""Season configuration tests (Area 6): data/season.json is strictly valid,
fixture expectations derive from it, Season 18 invariants are pinned, and a
synthetic second configuration validates in isolation. No network.
Usage: python tools/test_config.py
Exit 0 = pass.
"""
import copy
import json
import sys
import unittest
from pathlib import Path

BASE = Path(__file__).parent
ROOT = BASE.parent
sys.path.insert(0, str(BASE))
from gen_dark import validate_season

CFG = json.loads((ROOT / "data" / "season.json").read_text(encoding="utf-8"))


class SchemaTest(unittest.TestCase):
    def test_committed_config_valid(self):
        self.assertEqual(validate_season(CFG), [])

    def test_not_an_object(self):
        self.assertTrue(validate_season([]))
        self.assertTrue(validate_season(None))

    def test_missing_field(self):
        for field in ("teams", "aliases", "totalTeams", "playoffSlots",
                      "upperBracketSlots", "tiebreakers", "endpoints", "model",
                      "cacheNamespace", "cacheSchema"):
            bad = copy.deepcopy(CFG)
            del bad[field]
            self.assertTrue(validate_season(bad), field)

    def test_duplicate_teams(self):
        bad = copy.deepcopy(CFG)
        bad["teams"] = bad["teams"] + ["NAVI"]
        self.assertTrue(validate_season(bad))

    def test_team_count_mismatch(self):
        bad = copy.deepcopy(CFG)
        bad["totalTeams"] = 8
        self.assertTrue(validate_season(bad))

    def test_invalid_slots(self):
        for ps, ub in ((0, 0), (9, 0), (6, 7), (6, -1)):
            bad = copy.deepcopy(CFG)
            bad["playoffSlots"], bad["upperBracketSlots"] = ps, ub
            self.assertTrue(validate_season(bad), f"slots {ps}/{ub}")

    def test_fixture_math_mismatch(self):
        bad = copy.deepcopy(CFG)
        bad["seriesPerTeam"] = 15
        self.assertTrue(validate_season(bad))
        bad = copy.deepcopy(CFG)
        bad["totalRegularFixtures"] = 71
        self.assertTrue(validate_season(bad))

    def test_alias_problems(self):
        bad = copy.deepcopy(CFG)
        del bad["aliases"]["rrq"]
        self.assertTrue(validate_season(bad))
        bad = copy.deepcopy(CFG)
        bad["aliases"]["zzz"] = "ZZZ"
        self.assertTrue(validate_season(bad))

    def test_bad_priors(self):
        for pw, pg in ((0, 0), (0, 4), (4, 4), (5, 4)):
            bad = copy.deepcopy(CFG)
            bad["model"]["priorWins"], bad["model"]["priorGames"] = pw, pg
            self.assertTrue(validate_season(bad), f"prior {pw}/{pg}")

    def test_empty_tiebreakers_and_endpoints(self):
        bad = copy.deepcopy(CFG)
        bad["tiebreakers"] = []
        self.assertTrue(validate_season(bad))
        bad = copy.deepcopy(CFG)
        bad["endpoints"]["hub"] = ""
        self.assertTrue(validate_season(bad))


class DerivedMathTest(unittest.TestCase):
    def test_fixture_counts_derive_and_match_s18(self):
        n = len(CFG["teams"])
        rr = CFG["roundRobinRounds"]
        self.assertEqual(CFG["seriesPerTeam"], rr * (n - 1))
        self.assertEqual(CFG["totalRegularFixtures"], rr * n * (n - 1) // 2)
        self.assertEqual(CFG["totalRegularFixtures"], 72)
        self.assertEqual(CFG["totalRegularFixtures"] + CFG["playoffMatches"], 80)
        self.assertEqual(CFG["seriesPerTeam"], 16)


class S18PinsTest(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(CFG["seasonId"], "s18")
        self.assertEqual(CFG["displayName"], "MPL Indonesia Season 18")

    def test_teams_exact(self):
        self.assertEqual(CFG["teams"], ["AE", "BTR", "DEWA", "EVOS", "GEEK",
                                       "NAVI", "ONIC", "RRQ", "TLID"])

    def test_slots_and_format(self):
        self.assertEqual(CFG["playoffSlots"], 6)
        self.assertEqual(CFG["upperBracketSlots"], 2)
        self.assertEqual(CFG["tiebreakers"], ["match_point", "net_game_win", "h2h"])
        self.assertEqual(CFG["matchFormat"], "BO3")

    def test_model_defaults(self):
        self.assertEqual(CFG["model"]["winProb"], "bradley-terry")
        self.assertEqual((CFG["model"]["priorWins"], CFG["model"]["priorGames"]), (2, 4))
        self.assertEqual(CFG["model"]["trials"], 2000)
        self.assertEqual(CFG["model"]["seed"], 20907)  # 0x51ab

    def test_endpoints_and_paths(self):
        self.assertEqual(CFG["endpoints"]["hub"], "https://mpl.mlbbhub.com/api/v1/id")
        self.assertEqual(CFG["endpoints"]["liquipediaSeasonPage"],
                         "MPL/Indonesia/Season_18/Regular_Season")
        self.assertEqual(CFG["database"], "data/mpl_id_s18.db")
        self.assertEqual(CFG["csvDir"], "data/csv")
        self.assertEqual(CFG["cacheNamespace"], "mpl-board")
        self.assertEqual(CFG["cacheSchema"], 1)


class SyntheticConfigTest(unittest.TestCase):
    def toy(self):
        return {
            "seasonId": "toy", "displayName": "Toy Season",
            "teams": ["AA", "BB", "CC", "DD"],
            "aliases": {"aa": "AA", "bb": "BB", "cc": "CC", "dd": "DD"},
            "totalTeams": 4, "roundRobinRounds": 1, "seriesPerTeam": 3,
            "totalRegularFixtures": 6, "playoffMatches": 2,
            "playoffSlots": 2, "upperBracketSlots": 1,
            "tiebreakers": ["match_point", "net_game_win", "h2h"],
            "matchFormat": "BO3", "seriesWinPoints": 1,
            "endpoints": {"hub": "https://example.invalid/x",
                          "liquipediaApi": "https://example.invalid/api.php",
                          "liquipediaSeasonPage": "Toy/Season"},
            "database": "data/toy.db", "csvDir": "data/toy-csv",
            "playoffsJson": "data/toy-playoffs.json",
            "cacheNamespace": "mpl-board", "cacheSchema": 1,
            "model": {"winProb": "even", "priorWins": 1, "priorGames": 2,
                      "trials": 100, "seed": 7},
        }

    def test_synthetic_config_validates_isolated(self):
        self.assertEqual(validate_season(self.toy()), [])
        # committed Season 18 file untouched by the exercise
        again = json.loads((ROOT / "data" / "season.json").read_text(encoding="utf-8"))
        self.assertEqual(again["seasonId"], "s18")
        self.assertEqual(validate_season(again), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
