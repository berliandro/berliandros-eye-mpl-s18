"""Liquipedia match-block parser regression tests (Area 3).

Covers parse_liq_matches(), validate_build() and publish_build() from
tools/build_s18_db.py using inline fixtures only — no network; filesystem
use is confined to temporary directories. Usage:
    python tools/test_liqparse.py
Exit 0 = pass.
"""
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
from build_s18_db import (parse_liq_matches, validate_build, publish_build, TABLES,
                          attach_mvps, canon_team, clean_bans, SCHEMA)


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


TOY = {"totalRegularFixtures": 2, "regularSeasonStatus": "final",
       "playoffMatches": 1, "aliases": {}, "teams": ["A", "B"]}


def memdb(fill=True):
    con = sqlite3.connect(":memory:")
    con.executescript(SCHEMA)
    if fill:
        con.executemany("INSERT INTO standings VALUES(?,?,?,?,?,?,?,?,?)", [
            (1, "Alpha", "a", 6, 2, 0, 4, 1, 3),
            (2, "Beta", "b", 0, 0, 2, 1, 4, -3),
        ])
        con.executemany(
            "INSERT INTO schedule_all VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", [
            ("reg-1", "A", "B", 2, 0, "2026-01-01", "2026-01-01", "2026-01-01T10:00:00", "completed", "team_a", "", "1", ""),
            ("reg-2", "B", "A", 1, 2, "2026-01-02", "2026-01-02", "2026-01-02T10:00:00", "completed", "team_b", "", "2", ""),
            ("po-1", "TBD", "TBD", None, None, "2026-02-01", "2026-02-01", "2026-02-01T10:00:00", "upcoming", "", "", "", ""),
        ])
        con.executemany("INSERT INTO matches VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", [
            ("1", "reg-1", "A", "B", 2, 0, "Jan 1", "2026-01-01", "2026-01-01T10:00:00", "completed", "team_a", "", "", "MVP1"),
            ("2", "reg-2", "B", "A", 1, 2, "Jan 2", "2026-01-02", "2026-01-02T10:00:00", "completed", "team_b", "", "", "MVP2"),
        ])
        con.executemany("INSERT INTO games VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", [
            ("1", 1, "A", "B", 10, 5, "team_a", "10:00", 600, "blue", "red", "", "Prime"),
            ("1", 2, "A", "B", 10, 5, "team_a", "10:00", 600, "red", "blue", "", "Prime"),
            ("2", 1, "B", "A", 10, 5, "team_a", "10:00", 600, "blue", "red", "", "Prime"),
            ("2", 2, "B", "A", 5, 10, "team_b", "10:00", 600, "red", "blue", "", "Prime"),
            ("2", 3, "B", "A", 5, 10, "team_b", "10:00", 600, "blue", "red", "", "Prime"),
        ])
        for mid, gn, ta, tb, winner in (
            ("1", 1, "A", "B", "team_a"), ("1", 2, "A", "B", "team_a"),
            ("2", 1, "B", "A", "team_a"), ("2", 2, "B", "A", "team_b"),
            ("2", 3, "B", "A", "team_b"),
        ):
            players = []
            for team, prefix in ((ta, "a"), (tb, "b")):
                for i in range(5):
                    players.append((mid, gn, team, f"{prefix}{i}", "MID",
                                    f"H{prefix}{i}", 1, 0, 0, 1, 100, 10, 10,
                                    10, 10, None, "[]", "[]", None))
            con.executemany(
                "INSERT INTO game_players VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                players)
            con.execute("INSERT INTO game_bans VALUES(?,?,?,?,?)", (mid, gn, "A", "H9", 1))
            for team, opp, win in ((ta, tb, 1 if winner == "team_a" else 0),
                                   (tb, ta, 1 if winner == "team_b" else 0)):
                con.execute("INSERT INTO team_games VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (mid, gn, team, opp, 1, 1, 0, 0, 100, 10, 10, 10, 1, win, "Prime", 600))
        con.execute("INSERT INTO player_season_stats VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    ("a0", "A", "a", "MID", 5, 5, 1, 0, 0, 0, 0, 1, "1"))
        con.execute("INSERT INTO hero_stats VALUES(?,?,?,?,?,?)", ("H1", "", 5, 0, 4, "80%"))
    return con


class BanFilterTest(unittest.TestCase):
    def test_blank_and_duplicate_ban_ids_never_become_rows(self):
        self.assertEqual(clean_bans(["", "   ", None, "Atlas", "Atlas"]), ["Atlas"])
        self.assertEqual(clean_bans(None), [])
        self.assertEqual(clean_bans(["Fanny", "fanny"]), ["Fanny", "fanny"])


class ValidateTest(unittest.TestCase):
    def test_valid_build_passes(self):
        self.assertEqual(validate_build(memdb(True), [], {}, TOY), [])

    def test_missing_tables_reported(self):
        con = memdb(False)
        con.execute("DROP TABLE games")
        probs = validate_build(con, [], {}, TOY)
        self.assertTrue(any("missing table games" in p for p in probs))

    def test_empty_tables_reported(self):
        con = memdb(True)
        con.execute("DELETE FROM games")
        probs = validate_build(con, [], {}, TOY)
        self.assertTrue(any("games empty" in p or "games has" in p for p in probs))

    def test_failed_fetches_block_publish(self):
        probs = validate_build(memdb(True), [("1099", "boom")], {}, TOY)
        self.assertTrue(any("1099" in p for p in probs))

    def test_malformed_playoffs_block_publish(self):
        probs = validate_build(memdb(True), [], [], TOY)
        self.assertTrue(any("playoffs" in p for p in probs))

    def test_wrong_schedule_count_reported(self):
        con = memdb(True)
        con.execute("DELETE FROM schedule_all WHERE schedule_id='po-1'")
        probs = validate_build(con, [], {}, TOY)
        self.assertTrue(any("schedule_all has 2 rows" in p or "playoff schedule" in p for p in probs))

    def test_expected_counts_derive_from_season(self):
        con = memdb(True)
        self.assertEqual(validate_build(con, [], {}, TOY), [])
        probs = validate_build(con, [], {}, {"totalRegularFixtures": 1, "playoffMatches": 1})
        self.assertTrue(any("regular schedule has 2 rows, expected 1" in p for p in probs))

    def test_final_phase_blocks_missing_completed_result(self):
        con = memdb(True)
        con.execute("UPDATE schedule_all SET status='upcoming' WHERE schedule_id='reg-2'")
        probs = validate_build(con, [], {}, TOY)
        self.assertTrue(any("final phase requires 2 completed regular fixtures, found 1" in p
                            for p in probs), probs)

    def test_in_progress_phase_can_publish_partial(self):
        con = memdb(True)
        con.execute("UPDATE schedule_all SET status='upcoming' WHERE schedule_id='reg-2'")
        con.execute("DELETE FROM matches WHERE match_detail_id='2'")
        con.execute("DELETE FROM games WHERE match_detail_id='2'")
        con.execute("DELETE FROM team_games WHERE match_detail_id='2'")
        con.execute("UPDATE standings SET match_win=1,match_lose=0,game_win=2,game_lose=0 "
                    "WHERE team_slug='a'")
        con.execute("UPDATE standings SET match_win=0,match_lose=1,game_win=0,game_lose=2 "
                    "WHERE team_slug='b'")
        partial = dict(TOY, regularSeasonStatus="in-progress")
        self.assertEqual(validate_build(con, [], {}, partial), [])

    def test_duplicate_completed_detail_id_blocks_publish(self):
        con = memdb(True)
        con.execute("UPDATE schedule_all SET match_detail_id='1' WHERE schedule_id='reg-2'")
        probs = validate_build(con, [], {}, TOY)
        self.assertTrue(any("duplicate match detail id 1" in p for p in probs), probs)

    def test_missing_completed_detail_blocks_publish(self):
        con = memdb(True)
        con.execute("DELETE FROM matches WHERE match_detail_id='2'")
        probs = validate_build(con, [], {}, TOY)
        self.assertTrue(any("missing completed detail ids: 2" in p for p in probs), probs)

    def test_missing_game_detail_blocks_publish(self):
        con = memdb(True)
        con.execute("DELETE FROM games WHERE match_detail_id='1' AND game_no=2")
        probs = validate_build(con, [], {}, TOY)
        self.assertTrue(any("detail 1 has 1 games, expected 2" in p for p in probs), probs)

    def test_series_score_game_winners_mismatch_blocks(self):
        con = memdb(True)
        con.execute("UPDATE games SET winner='team_b' WHERE match_detail_id='1' AND game_no=1")
        probs = validate_build(con, [], {}, TOY)
        self.assertTrue(any("game winners do not match series score" in p for p in probs), probs)

    def test_missing_player_row_blocks_publish(self):
        con = memdb(True)
        con.execute("DELETE FROM game_players WHERE match_detail_id='1' AND game_no=1 "
                    "AND player='a0'")
        probs = validate_build(con, [], {}, TOY)
        self.assertTrue(any("exactly ten player rows" in p for p in probs), probs)

    def test_unreconciled_standings_block_publish(self):
        con = memdb(True)
        con.execute("UPDATE standings SET game_win=3 WHERE team_slug='a'")
        probs = validate_build(con, [], {}, TOY)
        self.assertTrue(any("A game_win" in p for p in probs), probs)


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
