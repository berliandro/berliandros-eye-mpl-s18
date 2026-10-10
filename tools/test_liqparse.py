"""Liquipedia match-block parser regression tests (Area 3).

Covers parse_liq_matches(), validate_build() and publish_build() from
tools/build_s18_db.py using inline fixtures only — no network; filesystem
use is confined to temporary directories. Usage:
    python tools/test_liqparse.py
Exit 0 = pass.
"""
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
from build_s18_db import parse_liq_matches, validate_build, publish_build, TABLES, attach_mvps, canon_team


def block(mid, t1, t2, date, mvp, winners):
    lines = [f"|M{mid}={{{{Match",
             f"|opponent1={{{{TeamOpponent|{t1}}}}}",
             f"|opponent2={{{{TeamOpponent|{t2}}}}}",
             f"|date={date}"]
    if mvp is not None:
        lines.append(f"|mvp={mvp}")
    for n, w in enumerate(winners, 1):
        lines.append(f"|map{n}={{{{Map|winner={w}|comment=Map}}}}")
    return "\n".join(lines)


BLK1 = block(1, "EVOS", "RRQ Hoshi", "Friday, 14 August 2026 - 15:00", "Alberttt", [1, 1])
BLK2 = block(2, "NAVI", "Alter Ego", "Friday, 14 August 2026 - 18:00", "Yazukee", [2, 2])


class ParseTest(unittest.TestCase):
    def test_one_block(self):
        out = parse_liq_matches(BLK1 + "\n")
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["t1"], "EVOS")
        self.assertEqual(out[0]["t2"], "RRQ Hoshi")
        self.assertEqual(out[0]["mvp"], "Alberttt")
        self.assertEqual(out[0]["score"], "2-0")
        self.assertIn("14 August 2026", out[0]["date"])

    def test_two_consecutive_blocks_not_merged(self):
        out = parse_liq_matches(BLK1 + "\n" + BLK2 + "\n")
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0]["t1"], "EVOS")
        self.assertEqual(out[1]["t1"], "NAVI")
        self.assertEqual(out[1]["score"], "0-2")
        self.assertNotIn("Yazukee", out[0]["mvp"])

    def test_final_block_at_end_of_input(self):
        # No trailing marker and no trailing newline: the final block that
        # the old lookahead-only regex dropped must be captured.
        out = parse_liq_matches(BLK1 + "\n" + BLK2)
        self.assertEqual(len(out), 2)
        self.assertEqual(out[1]["t1"], "NAVI")
        self.assertEqual(out[1]["mvp"], "Yazukee")

    def test_trailing_newline_variants(self):
        self.assertEqual(len(parse_liq_matches(BLK1 + "\n")), 1)
        self.assertEqual(len(parse_liq_matches(BLK1)), 1)
        self.assertEqual(len(parse_liq_matches(BLK1 + "\n\n")), 1)

    def test_missing_optional_mvp(self):
        out = parse_liq_matches(block(7, "A", "B", "Oct 1", None, [1, 2, 1]))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["mvp"], "")
        self.assertEqual(out[0]["score"], "2-1")

    def test_empty_and_malformed_input(self):
        self.assertEqual(parse_liq_matches(""), [])
        self.assertEqual(parse_liq_matches("no markers here\n"), [])
        self.assertEqual(parse_liq_matches(None), [])

    def test_undecided_series_score(self):
        out = parse_liq_matches(block(9, "A", "B", "Oct 9", "", []))
        self.assertEqual(out[0]["score"], "vs")


def memdb(fill=True):
    con = sqlite3.connect(":memory:")
    con.executescript("""
    CREATE TABLE matches(match_detail_id TEXT PRIMARY KEY);
    CREATE TABLE schedule_all(schedule_id TEXT PRIMARY KEY);
    CREATE TABLE games(match_detail_id TEXT, game_no INTEGER);
    CREATE TABLE game_players(match_detail_id TEXT, game_no INTEGER);
    CREATE TABLE game_bans(match_detail_id TEXT, game_no INTEGER);
    CREATE TABLE player_season_stats(player TEXT PRIMARY KEY);
    CREATE TABLE hero_stats(hero TEXT PRIMARY KEY);
    CREATE TABLE standings(rank INTEGER PRIMARY KEY);
    """)
    if fill:
        con.execute("INSERT INTO standings VALUES(1)")
        for i in range(80):
            con.execute("INSERT INTO schedule_all VALUES(?)", (f"id-{i}",))
        con.execute("INSERT INTO games VALUES('1',1)")
        con.execute("INSERT INTO game_players VALUES('1',1)")
        con.execute("INSERT INTO game_bans VALUES('1',1)")
        con.execute("INSERT INTO matches VALUES('1')")
        con.execute("INSERT INTO player_season_stats VALUES('P')")
        con.execute("INSERT INTO hero_stats VALUES('H')")
    return con


class ValidateTest(unittest.TestCase):
    def test_valid_build_passes(self):
        self.assertEqual(validate_build(memdb(True), [], {}), [])

    def test_missing_tables_reported(self):
        con = memdb(False)
        con.execute("DROP TABLE games")
        probs = validate_build(con, [], {})
        self.assertTrue(any("missing table games" in p for p in probs))

    def test_empty_tables_reported(self):
        con = memdb(True)
        con.execute("DELETE FROM games")
        probs = validate_build(con, [], {})
        self.assertTrue(any("games empty" in p for p in probs))

    def test_failed_fetches_block_publish(self):
        probs = validate_build(memdb(True), [("1099", "boom")], {})
        self.assertTrue(any("1099" in p for p in probs))

    def test_malformed_playoffs_block_publish(self):
        probs = validate_build(memdb(True), [], [])
        self.assertTrue(any("playoffs" in p for p in probs))

    def test_wrong_schedule_count_reported(self):
        con = memdb(True)
        con.execute("DELETE FROM schedule_all WHERE schedule_id='id-0'")
        probs = validate_build(con, [], {})
        self.assertTrue(any("79" in p for p in probs))

    def test_expected_counts_derive_from_season(self):
        con = memdb(True)
        toy = {"totalRegularFixtures": 78, "playoffMatches": 2}
        self.assertEqual(validate_build(con, [], {}, toy), [])
        probs = validate_build(con, [], {}, {"totalRegularFixtures": 6, "playoffMatches": 2})
        self.assertTrue(any("80" in p and "expected 8" in p for p in probs))


class PublishTest(unittest.TestCase):
    def make_staging(self, root):
        st = Path(root) / "staging"
        (st / "csv").mkdir(parents=True)
        (st / "mpl_id_s18.db").write_text("new-db")
        for tbl in TABLES:
            (st / "csv" / f"{tbl}.csv").write_text("new-" + tbl)
        (st / "playoffs.json").write_text("{}")
        old_db = Path(root) / "mpl_id_s18.db"
        old_db.write_text("old-db")
        old_csv = Path(root) / "csv"
        old_csv.mkdir()
        for tbl in TABLES:
            (old_csv / f"{tbl}.csv").write_text("old-" + tbl)
        old_po = Path(root) / "playoffs.json"
        old_po.write_text("old-po")
        return st, old_db, old_csv, old_po

    def test_publish_replaces_and_cleans_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            st, db, csvd, po = self.make_staging(tmp)
            publish_build(st, db, csvd, po)
            self.assertEqual(db.read_text(), "new-db")
            for tbl in TABLES:
                self.assertEqual((csvd / f"{tbl}.csv").read_text(), "new-" + tbl)
            self.assertEqual(po.read_text(), "{}")
            self.assertFalse(st.exists())

    def test_missing_staging_file_raises_and_keeps_old(self):
        with tempfile.TemporaryDirectory() as tmp:
            st, db, csvd, po = self.make_staging(tmp)
            (st / "csv" / "matches.csv").unlink()
            with self.assertRaises(Exception):
                publish_build(st, db, csvd, po)
            # the db was already replaced, but untouched targets must remain
            self.assertEqual((csvd / "standings.csv").read_text(), "old-standings")
            self.assertEqual(po.read_text(), "old-po")


class AttachMvpsTest(unittest.TestCase):
    def hub(self, did, a, b, dt):
        return {"match_detail_id": did, "team_a": a, "team_b": b, "iso_datetime": dt}

    def liq(self, t1, t2, mvp):
        return {"t1": t1, "t2": t2, "mvp": mvp}

    def test_pair_match_with_liquipedia_spellings(self):
        out = attach_mvps(
            [self.hub("1", "NAVI", "DEWA", "2026-09-04")],
            [self.liq("Natus Vincere", "Dewa United Esports", "Coolfire")])
        self.assertEqual(out, {"1": "Coolfire"})

    def test_duplicate_pairs_consume_in_order(self):
        out = attach_mvps(
            [self.hub("1", "NAVI", "DEWA", "2026-09-04"),
             self.hub("2", "DEWA", "NAVI", "2026-10-09")],
            [self.liq("Natus Vincere", "Dewa United Esports", "Coolfire"),
             self.liq("Dewa United Esports", "Natus Vincere", "Coolfire2")])
        self.assertEqual(out, {"1": "Coolfire", "2": "Coolfire2"})

    def test_unmatched_row_stays_blank(self):
        # No fallback attach: an unrelated leftover block must NOT leak in.
        out = attach_mvps(
            [self.hub("1", "DEWA", "NAVI", "2026-10-09")],
            [self.liq("RRQ Hoshi", "Team Liquid ID", "JOOOOO")])
        self.assertEqual(out, {"1": ""})

    def test_canon_team_spellings(self):
        self.assertEqual(canon_team("NAVI"), "navi")
        self.assertEqual(canon_team("Dewa United Esports"), "dewa")
        self.assertEqual(canon_team("Geek Fam ID"), "geek")
        self.assertEqual(canon_team("RRQ Hoshi"), "rrq")
        self.assertEqual(canon_team("Natus Vincere"), "navi")


if __name__ == "__main__":
    unittest.main(verbosity=2)
