"""Enrich a season database with Liquipedia per-game drafts, lane order and map.

The mlbbhub API exposes bans but no picks, per-game lane is null, and map mode
is absent. Liquipedia's Map template carries all three:
  t1h1..t1h5 / t2h1..t2h5  heroes in lane order (EXP, JUNGLE, MID, GOLD, ROAM)
  t1b1..t1b5 / t2b1..t2b5  bans in draft order
  mapmode, length, team1side/team2side, winner, vod

This script is idempotent: it adds the schema, clears and rebuilds game_picks,
sets lane/lane_source only from the Liquipedia slot, and re-exports CSVs.
It never invents a lane: an unmatched hero keeps its previous lane and is
reported.

Usage: python tools/enrich_drafts.py [--season s18] [--check-only]
"""
import argparse
import csv
import gzip
import json
import re
import sqlite3
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from season import resolve

LANES = ["EXP", "JUNGLE", "MID", "GOLD", "ROAM"]

# Liquipedia sometimes uses short hero names. Map only unambiguous abbreviations
# to the canonical DB spelling; anything else is reported, never guessed.
HERO_ALIASES = {
    "gatot": "Gatotkaca",
    "guin": "Guinevere",
    "haya": "Hayabusa",
    "lapu": "Lapu-Lapu",
    "yss": "Yi Sun-Shin",
    "yz": "Yu Zhong",
    "xborg": "X.Borg",
    "popol": "Popol and Kupa",
}

# The API stores one hero under two spellings: hero_stats says "Zetian" while
# per-player rows say "Wu/Zetian". Both have exactly 16 picks, so they are one
# hero. Fold the variant into the stats spelling; the mapping is explicit and
# reversible.
HERO_RENAMES = {
    "wuzetian": "Zetian",
    # Case-only variants split across the stats and per-game tables.
    "lapulapu": "Lapu-Lapu",
    "yisunshin": "Yi Sun-Shin",
    "cici": "Cici",
}

# Week 9 uses short map labels; expand them to the spellings used elsewhere in
# the same source. Unknown labels are kept verbatim.
MAP_MODE_ALIASES = {
    "fc": "Flying Cloud",
    "ht": "Healing Turtle",
    "rw": "Revealing Wisps",
}


def hero_key(name):
    """Stable comparison key: unifies regional spellings without renaming rows."""
    k = norm(name)
    alias = HERO_ALIASES.get(k)
    return norm(alias) if alias else k


def canonical_hero(h):
    """Fold known duplicate spellings into the canonical hero name."""
    return HERO_RENAMES.get(norm(h), h)
UA = {"User-Agent": "MPL-S18-research/1.0 (local ETL enrichment)",
      "Accept-Encoding": "gzip"}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def get_wikitext(api, page):
    q = urllib.parse.urlencode({"action": "parse", "page": page, "prop": "wikitext",
                                "format": "json", "origin": "*"})
    req = urllib.request.Request(f"{api}?{q}", headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        raw = r.read()
        if r.headers.get("Content-Encoding") == "gzip" or raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
    return json.loads(raw.decode("utf-8"))["parse"]["wikitext"]["*"]


def field(body, name):
    # The first template parameter has no leading pipe, so accept start-of-body.
    m = re.search(r"(?:^|\|)" + re.escape(name) + r"=([^\|\n\}]*)", body)
    return (m.group(1) if m else "").strip()


def parse_series(wt):
    """Return [{t1,t2,maps:[{no,body,fields...}]}] in page order."""
    blocks = re.findall(r"\|M\d+=\{\{Match([\s\S]*?)(?=\|M\d+=\{\{Match|\Z)", wt or "")
    out = []
    for b in blocks:
        t1 = (re.search(r"opponent1=\{\{TeamOpponent\|([^\}\|\n]+)", b) or [None, ""])[1].strip()
        t2 = (re.search(r"opponent2=\{\{TeamOpponent\|([^\}\|\n]+)", b) or [None, ""])[1].strip()
        maps = []
        for num, body in re.findall(r"\|map(\d+)=\{\{Map\|([\s\S]*?)\n\s*\}\}", b):
            if "finished=skip" in body:
                continue
            maps.append({
                "no": int(num),
                "body": body,
                "team1side": field(body, "team1side"),
                "team2side": field(body, "team2side"),
                "length": field(body, "length"),
                "winner": field(body, "winner"),
                "mapmode": field(body, "mapmode"),
                "vod": field(body, "vod"),
                "t1h": [field(body, f"t1h{k}") for k in range(1, 6)],
                "t2h": [field(body, f"t2h{k}") for k in range(1, 6)],
                "t1b": [field(body, f"t1b{k}") for k in range(1, 6)],
                "t2b": [field(body, f"t2b{k}") for k in range(1, 6)],
            })
        if not t1 and not t2 and not maps:
            continue
        out.append({"t1": t1, "t2": t2, "maps": maps})
    return out


def ensure_schema(con):
    cols = {r[1] for r in con.execute("PRAGMA table_info(games)")}
    if "map_mode" not in cols:
        con.execute("ALTER TABLE games ADD COLUMN map_mode TEXT")
    cols = {r[1] for r in con.execute("PRAGMA table_info(game_players)")}
    if "lane_source" not in cols:
        con.execute("ALTER TABLE game_players ADD COLUMN lane_source TEXT")
    cols = {r[1] for r in con.execute("PRAGMA table_info(game_bans)")}
    if "ban_order" not in cols:
        con.execute("ALTER TABLE game_bans ADD COLUMN ban_order INTEGER")
    con.execute("""CREATE TABLE IF NOT EXISTS game_picks(
        match_detail_id TEXT, game_no INTEGER, team TEXT, side TEXT,
        slot INTEGER, lane TEXT, hero TEXT, player TEXT,
        PRIMARY KEY(match_detail_id, game_no, team, slot))""")
    con.execute("CREATE INDEX IF NOT EXISTS ix_picks_game ON game_picks(match_detail_id, game_no)")
    con.commit()


def dedupe_bans(con):
    """Drop exact duplicate ban rows (the API occasionally repeats a hero)."""
    dupes = con.execute(
        "SELECT match_detail_id, game_no, side, hero, COUNT(*) FROM game_bans "
        "GROUP BY match_detail_id, game_no, side, hero HAVING COUNT(*) > 1").fetchall()
    removed = 0
    for mid, gn, side, hero, _ in dupes:
        ids = [r[0] for r in con.execute(
            "SELECT rowid FROM game_bans WHERE match_detail_id=? AND game_no=? AND side=? AND hero=? "
            "ORDER BY rowid", (mid, gn, side, hero))]
        for rid in ids[1:]:
            con.execute("DELETE FROM game_bans WHERE rowid=?", (rid,))
            removed += 1
    if removed:
        con.commit()
    return removed


def export_tables(con, csv_dir, tables):
    csv_dir.mkdir(parents=True, exist_ok=True)
    for tbl in tables:
        cur = con.execute(f"SELECT * FROM {tbl}")
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        with open(csv_dir / f"{tbl}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(cols)
            w.writerows(rows)
        print(f"csv {tbl}: {len(rows)} rows")


def main():
    ap = argparse.ArgumentParser(description="Enrich drafts, lanes and map mode.")
    ap.add_argument("--season", default="s18")
    ap.add_argument("--check-only", action="store_true",
                    help="report coverage without writing")
    args = ap.parse_args()

    season = resolve(args.season)
    cfg = json.loads(season["config"].read_text(encoding="utf-8"))
    api = cfg["endpoints"]["liquipediaApi"]
    page = cfg["endpoints"]["liquipediaSeasonPage"]
    aliases = cfg["aliases"]

    con = sqlite3.connect(season["database"])
    ensure_schema(con)

    # Unify hero spellings before lookups and before rebuilding picks.
    for table in ("game_players", "game_bans", "game_picks", "hero_stats"):
        for (h,) in con.execute(f"SELECT DISTINCT hero FROM {table}").fetchall():
            canonical = canonical_hero(h)
            if canonical != h:
                con.execute(f"UPDATE {table} SET hero=? WHERE hero=?", (canonical, h))
    con.commit()

    removed = dedupe_bans(con)
    if removed:
        print(f"duplicate ban rows removed: {removed}")

    # Canonical team keys, mirroring build_s18_db.canon_team.
    def canon(t):
        k = norm(t)
        return aliases.get(k, k).lower()

    db_matches = con.execute(
        "SELECT match_detail_id, team_a, team_b, score_a, score_b "
        "FROM matches ORDER BY iso_datetime, CAST(match_detail_id AS INTEGER)").fetchall()
    gp_heroes = {norm(h): h for (h,) in con.execute("SELECT DISTINCT hero FROM game_players")}
    db_heroes = dict(gp_heroes)
    db_heroes.update({norm(h): h for (h,) in con.execute("SELECT DISTINCT hero FROM hero_stats")})

    def canon_hero(name):
        key = norm(name)
        # Prefer the spelling actually present in player rows: some heroes are
        # split between the stats list and the per-game rows (e.g. Zetian).
        if key in gp_heroes:
            return gp_heroes[key]
        alias = HERO_ALIASES.get(key)
        if alias and norm(alias) in gp_heroes:
            return gp_heroes[norm(alias)]
        if key in db_heroes:
            return db_heroes[key]
        return db_heroes.get(norm(alias)) if alias else None

    print(f"fetch liquipedia {page} ...")
    series = parse_series(get_wikitext(api, page))
    print(f"liquipedia series: {len(series)}  db matches: {len(db_matches)}")

    used = set()
    pairs = []
    for s in series:
        key = frozenset((canon(s["t1"]), canon(s["t2"])))
        hit = None
        for m in db_matches:
            if m[0] in used:
                continue
            if frozenset((canon(m[1]), canon(m[2]))) == key:
                hit = m
                break
        if hit:
            used.add(hit[0])
            pairs.append((s, hit))
    print(f"series matched: {len(pairs)}/{len(series)}")

    unmatched = [s for s in series if not any(s is p[0] for p in pairs)]
    if unmatched:
        print("unmatched series (first 8):",
              [(s["t1"], s["t2"], len(s["maps"])) for s in unmatched[:8]])

    # Snapshot API bans before enrichment so the cross-source check compares the
    # original data, per side, instead of half-updated rows.
    api_bans = {}
    for mid_, gn_, side_, hero_ in con.execute(
            "SELECT match_detail_id, game_no, side, hero FROM game_bans"):
        api_bans.setdefault((mid_, gn_, side_), set()).add(hero_key(hero_))
    liq_bans = {}

    picks_rows = 0
    missing_examples = []
    lane_set = 0
    lane_missing = 0
    hero_missing = set()
    map_set = 0
    ban_mismatch = []
    score_mismatch = []

    picks = []
    for s, m in pairs:
        mid, ta = m[0], m[1]
        flipped = canon(s["t1"]) != canon(ta)
        # Series score cross-check from map winners.
        w1 = sum(1 for x in s["maps"] if x["winner"] == "1")
        w2 = sum(1 for x in s["maps"] if x["winner"] == "2")
        sa, sb = int(m[3] or 0), int(m[4] or 0)
        exp_a, exp_b = (w2, w1) if flipped else (w1, w2)
        if (sa, sb) != (exp_a, exp_b):
            score_mismatch.append((mid, f"{sa}-{sb}", f"{exp_a}-{exp_b}"))

        for mp in s["maps"]:
            gn = mp["no"]
            g = con.execute("SELECT team_a, team_b FROM games WHERE match_detail_id=? AND game_no=?",
                            (mid, gn)).fetchone()
            if not g:
                continue
            g_ta, g_tb = g
            if mp["mapmode"]:
                mode = MAP_MODE_ALIASES.get(norm(mp["mapmode"]), mp["mapmode"])
                con.execute("UPDATE games SET map_mode=? WHERE match_detail_id=? AND game_no=?",
                            (mode, mid, gn))
                map_set += 1

            for side_no, team_liq, heroes, bans in (
                (1, s["t1"], mp["t1h"], mp["t1b"]),
                (2, s["t2"], mp["t2h"], mp["t2b"]),
            ):
                team = g_ta if canon(team_liq) == canon(g_ta) else g_tb
                side_letter = "A" if team == g_ta else "B"
                side_name = mp["team1side"] if side_no == 1 else mp["team2side"]

                for slot, hero in enumerate(heroes, 1):
                    if not hero:
                        continue
                    ch = canon_hero(hero)
                    if not ch:
                        hero_missing.add(hero)
                        continue
                    row = con.execute(
                        "SELECT player FROM game_players WHERE match_detail_id=? AND game_no=? "
                        "AND team=? AND hero=? COLLATE NOCASE",
                        (mid, gn, team, ch)).fetchone()
                    player = row[0] if row else None
                    picks.append((mid, gn, team, side_name, slot, LANES[slot - 1], ch, player))
                    picks_rows += 1
                    if player:
                        con.execute(
                            "UPDATE game_players SET lane=?, lane_source='liq_slot' "
                            "WHERE match_detail_id=? AND game_no=? AND team=? AND player=? AND hero=?",
                            (LANES[slot - 1], mid, gn, team, player, ch))
                        lane_set += 1
                    else:
                        lane_missing += 1
                        if len(missing_examples) < 10:
                            missing_examples.append((mid, gn, team, ch))

                for order, hero in enumerate(bans, 1):
                    if not hero:
                        continue
                    ch = canon_hero(hero)
                    if not ch:
                        hero_missing.add(hero)
                        continue
                    liq_bans.setdefault((mid, gn, side_letter), set()).add(hero_key(ch))
                    # Match by normalized hero so regional spellings
                    # ("Wu/Zetian" vs "Zetian") update the API row instead of
                    # inserting a duplicate ban.
                    existing = con.execute(
                        "SELECT rowid, hero FROM game_bans WHERE match_detail_id=? AND game_no=? AND side=?",
                        (mid, gn, side_letter)).fetchall()
                    target = next((rid for rid, h in existing if hero_key(h) == hero_key(ch)), None)
                    if target is not None:
                        con.execute("UPDATE game_bans SET ban_order=? WHERE rowid=?", (order, target))
                    else:
                        con.execute(
                            "INSERT INTO game_bans(match_detail_id, game_no, side, hero, ban_order) "
                            "VALUES(?,?,?,?,?)", (mid, gn, side_letter, ch, order))

    # Cross-source ban agreement, per game and side, against the pre-enrichment
    # snapshot. This separates a genuine data conflict from a side mapping bug.
    for key, lib in liq_bans.items():
        api_set = api_bans.get(key)
        if api_set is None:
            ban_mismatch.append((key[0], key[1], key[2], "missing-api-side"))
        elif lib != api_set:
            ban_mismatch.append((key[0], key[1], key[2], sorted(lib ^ api_set)))

    total_games = con.execute("SELECT COUNT(*) FROM games").fetchone()[0]
    total_rows = con.execute("SELECT COUNT(*) FROM game_players").fetchone()[0]
    covered_games = len({(p[0], p[1]) for p in picks})
    lane_tagged = con.execute(
        "SELECT COUNT(*) FROM game_players WHERE lane_source='liq_slot'").fetchone()[0]
    print(f"\ngames: {total_games}  picks-covered games: {covered_games}")
    print(f"pick rows: {picks_rows}  lanes set: {lane_set}  players not found: {lane_missing}")
    if missing_examples:
        print(f"  missing examples: {missing_examples[:6]}")
    print(f"player rows with lane_source=liq_slot: {lane_tagged}/{total_rows}")
    print(f"map modes set: {map_set}  unresolved hero names: {sorted(hero_missing)[:10]}")
    print(f"score mismatches: {len(score_mismatch)} {score_mismatch[:5]}")
    print(f"ban set mismatches: {len(ban_mismatch)} {ban_mismatch[:5]}")

    if not args.check_only:
        con.execute("DELETE FROM game_picks")
        con.executemany("INSERT OR REPLACE INTO game_picks VALUES(?,?,?,?,?,?,?,?)", picks)
        con.commit()
        export_tables(con, season["csvDir"],
                      ["games", "game_players", "game_bans", "game_picks"])
    else:
        con.rollback()
        print("check-only: no writes committed")
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
