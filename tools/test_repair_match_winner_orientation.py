#!/usr/bin/env python3
"""Unit tests for safe match winner orientation repair."""
import csv
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from repair_match_winner_orientation import RepairError, winner_for_score, inspect_database, rewrite_matches_csv


class WinnerFunctionTests(unittest.TestCase):
    def test_winner_relative_to_detail_order(self):
        self.assertEqual(winner_for_score(2, 0), "team_a")
        self.assertEqual(winner_for_score(0, 2), "team_b")
        self.assertEqual(winner_for_score("1", "2"), "team_b")

    def test_tied_and_malformed_scores_rejected(self):
        for pair in ((1, 1), (None, 2), ("x", 0)):
            with self.subTest(pair=pair), self.assertRaises(RepairError):
                winner_for_score(*pair)


class DatabasePlanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "matches.db"
        con = sqlite3.connect(self.db)
        con.execute("""CREATE TABLE matches(
            match_detail_id TEXT, team_a TEXT, team_b TEXT,
            score_a INTEGER, score_b INTEGER, winner TEXT
        )""")
        con.executemany("INSERT INTO matches VALUES(?,?,?,?,?,?)", [
            ("1","A","B",2,0,"team_a"),
            ("2","C","D",2,0,"team_b"),
            ("3","E","F",0,2,"team_a"),
            ("4","G","H",1,2,"team_b"),
        ])
        con.commit()
        con.close()

    def test_preview_only_plans_actual_mismatches(self):
        rows, updates = inspect_database(self.db)
        self.assertEqual(len(rows), 4)
        self.assertEqual([u["match_detail_id"] for u in updates], ["2","3"])
        self.assertEqual([u["new_winner"] for u in updates], ["team_a","team_b"])

    def test_csv_rewrite_preserves_columns_and_refuses_scope_mismatch(self):
        p = Path(self.tmp.name) / "matches.csv"
        rows, updates = inspect_database(self.db)
        with p.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["match_detail_id","team_a","team_b","score_a","score_b","winner","vod_url"])
            w.writeheader()
            w.writerows([
                {"match_detail_id":"1","team_a":"A","team_b":"B","score_a":"2","score_b":"0","winner":"team_a","vod_url":"url1"},
                {"match_detail_id":"2","team_a":"C","team_b":"D","score_a":"2","score_b":"0","winner":"team_b","vod_url":"url2"},
                {"match_detail_id":"3","team_a":"E","team_b":"F","score_a":"0","score_b":"2","winner":"team_a","vod_url":"url3"},
                {"match_detail_id":"4","team_a":"G","team_b":"H","score_a":"1","score_b":"2","winner":"team_b","vod_url":"url4"},
            ])
        repaired, count = rewrite_matches_csv(p, rows)
        self.assertEqual(count, 2)
        parsed = list(csv.DictReader(repaired.splitlines()))
        self.assertEqual([r["winner"] for r in parsed], ["team_a","team_a","team_b","team_b"])
        self.assertEqual([r["vod_url"] for r in parsed], ["url1","url2","url3","url4"])
        with p.open("w",encoding="utf-8",newline="") as f:
            w=csv.writer(f);w.writerow(["match_detail_id","team_a","team_b","score_a","score_b","winner"]);w.writerow(["1","A","B","2","0","team_a"])
        with self.assertRaises(RepairError):
            rewrite_matches_csv(p, rows)


if __name__ == "__main__":
    unittest.main(verbosity=2)
