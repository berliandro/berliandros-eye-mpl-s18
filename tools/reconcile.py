"""Cross-view reconciliation gate for the committed MPL S18 snapshot.

The SQLite database is the canonical persisted snapshot. This tool derives
regular-season series and game records from the raw match/game rows and
compares them with the source-published standings table. It is intentionally
strict: when coverage is complete, a mismatch is a failure with an actionable
per-team diff.

Usage:
    python tools/reconcile.py [--season s18]
Exit 0 = reconciled, 1 = mismatch/invalid snapshot.
"""
import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
sys.path.insert(0, str(BASE))
from season import resolve  # noqa: E402


def norm(value):
    return "".join(ch for ch in str(value or "").lower() if ch.isalnum())


def canonical_maps(season):
    aliases = {norm(k): v for k, v in (season.get("aliases") or {}).items()}
    for code in season.get("teams") or []:
        aliases[norm(code)] = code
    return aliases


def canon(value, aliases):
    key = norm(value)
    return aliases.get(key, str(value or "").strip().upper())


def phase_is_playoff(row):
    label = str(row.get("schedule_id") or row.get("match_id") or "").lower()
    return "playoff" in label or (row.get("team_a") == "TBD" and row.get("team_b") == "TBD")


def derive_records(con, aliases):
    """Return per-team derived regular-season match/game records."""
    out = {}
    included = {"matches": [], "games": [], "excluded_matches": [], "excluded_games": []}
    for row in con.execute(
        "SELECT match_detail_id, schedule_id, team_a, team_b, score_a, score_b, status, winner "
        "FROM matches ORDER BY match_detail_id"
    ):
        m = dict(row)
        if m["status"] != "completed" or phase_is_playoff(m):
            included["excluded_matches"].append(m["match_detail_id"])
            continue
        a, b = canon(m["team_a"], aliases), canon(m["team_b"], aliases)
        sa, sb = m.get("score_a"), m.get("score_b")
        if a not in aliases.values() or b not in aliases.values() or a == b:
            raise ValueError(f"match {m['match_detail_id']} has invalid teams {m['team_a']!r}/{m['team_b']!r}")
        if not isinstance(sa, int) or not isinstance(sb, int) or sa == sb:
            raise ValueError(f"match {m['match_detail_id']} has no decisive score {sa!r}-{sb!r}")
        winner_code = a if sa > sb else b
        for team in (a, b):
            rec = out.setdefault(team, {"match_win": 0, "match_lose": 0, "game_win": 0, "game_lose": 0,
                                        "game_rows": 0, "match_ids": []})
            rec["match_ids"].append(str(m["match_detail_id"]))
            if team == winner_code:
                rec["match_win"] += 1
            else:
                rec["match_lose"] += 1
        included["matches"].append(str(m["match_detail_id"]))

    for row in con.execute(
        "SELECT g.match_detail_id, g.game_no, g.team_a, g.team_b, g.winner "
        "FROM games g JOIN matches m ON m.match_detail_id=g.match_detail_id "
        "ORDER BY g.match_detail_id, g.game_no"
    ):
        g = dict(row)
        m = con.execute("SELECT schedule_id, team_a, team_b, status FROM matches WHERE match_detail_id=?",
                        (g["match_detail_id"],)).fetchone()
        if m is None or m["status"] != "completed" or phase_is_playoff(dict(m)):
            included["excluded_games"].append(f"{g['match_detail_id']}:{g['game_no']}")
            continue
        a, b = canon(g["team_a"], aliases), canon(g["team_b"], aliases)
        if a not in aliases.values() or b not in aliases.values() or a == b:
            raise ValueError(f"game {g['match_detail_id']}:{g['game_no']} has invalid teams")
        if g["winner"] not in ("team_a", "team_b"):
            raise ValueError(f"game {g['match_detail_id']}:{g['game_no']} has invalid winner {g['winner']!r}")
        winner_code = a if g["winner"] == "team_a" else b
        for team in (a, b):
            rec = out.setdefault(team, {"match_win": 0, "match_lose": 0, "game_win": 0, "game_lose": 0,
                                        "game_rows": 0, "match_ids": []})
            rec["game_rows"] += 1
            if team == winner_code:
                rec["game_win"] += 1
            else:
                rec["game_lose"] += 1
        included["games"].append(f"{g['match_detail_id']}:{g['game_no']}")
    return out, included


def source_fingerprint(db_path):
    h = hashlib.sha256()
    with open(db_path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


def build_report(season_id="s18"):
    paths = resolve(season_id)
    config = json.loads(Path(paths["config"]).read_text(encoding="utf-8"))
    db_path = Path(paths["database"])
    aliases = canonical_maps(config)
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        official = {r["team_slug"].upper(): dict(r) for r in con.execute("SELECT * FROM standings")}
        derived, included = derive_records(con, aliases)
        rows = []
        failures = []
        for code in sorted(official):
            o = official[code]
            d = derived.get(code, {"match_win": 0, "match_lose": 0, "game_win": 0, "game_lose": 0,
                                   "game_rows": 0, "match_ids": []})
            checks = {
                "match_win": (o.get("match_win"), d["match_win"]),
                "match_lose": (o.get("match_lose"), d["match_lose"]),
                "game_win": (o.get("game_win"), d["game_win"]),
                "game_lose": (o.get("game_lose"), d["game_lose"]),
                "net_game_win": (o.get("net_game_win"), d["game_win"] - d["game_lose"]),
            }
            bad = {k: v for k, v in checks.items() if v[0] != v[1]}
            if bad:
                failures.append({"team": code, "diff": bad, "included_games": d["game_rows"],
                                 "match_ids": d["match_ids"]})
            rows.append({"team": code, "official": o, "derived": d, "ok": not bad})
        total_appearances = sum(r["derived"]["game_rows"] for r in rows)
        expected_appearances = 2 * len(included["games"])
        integrity = {
            "teams": len(rows),
            "included_matches": len(included["matches"]),
            "included_games": len(included["games"]),
            "team_game_appearances": total_appearances,
            "expected_appearances": expected_appearances,
            "appearance_balance": total_appearances == expected_appearances,
            "all_games_have_one_winner": all(
                r["derived"]["game_win"] + r["derived"]["game_lose"] == r["derived"]["game_rows"] for r in rows),
            "all_teams_present": set(official) == set(derived),
        }
        ok = not failures and all(v for k, v in integrity.items() if k in (
            "appearance_balance", "all_games_have_one_winner", "all_teams_present"))
        return {
            "ok": ok,
            "season": season_id,
            "snapshot": source_fingerprint(db_path),
            "database": str(db_path),
            "scope": "completed regular-season matches/games; playoffs excluded",
            "rows": rows,
            "failures": failures,
            "integrity": integrity,
            "excluded": included["excluded_matches"] + included["excluded_games"],
        }
    finally:
        con.close()


def print_report(report):
    print(f"Cross-view reconciliation · season {report['season']} · snapshot {report['snapshot']}")
    print(f"scope: {report['scope']}")
    print(f"{'Team':6} {'Match W-L(off)':>14} {'Match W-L(der)':>14} {'Game W-L(off)':>14} {'Game W-L(der)':>14}  OK")
    for r in report["rows"]:
        o, d = r["official"], r["derived"]
        print(f"{r['team']:6} {str(o.get('match_win'))+'-'+str(o.get('match_lose')):>14} "
              f"{str(d['match_win'])+'-'+str(d['match_lose']):>14} "
              f"{str(o.get('game_win'))+'-'+str(o.get('game_lose')):>14} "
              f"{str(d['game_win'])+'-'+str(d['game_lose']):>14}  {'PASS' if r['ok'] else 'FAIL'}")
    i = report["integrity"]
    print(f"included: {i['included_matches']} matches, {i['included_games']} games; "
          f"team appearances {i['team_game_appearances']} (expected {i['expected_appearances']})")
    for f in report["failures"]:
        print(f"FAIL {f['team']}: official/derived {f['diff']} · "
              f"included games={f['included_games']} · match ids={','.join(f['match_ids'])}")
    if report["excluded"]:
        print("excluded rows: " + ", ".join(report["excluded"]))
    print(("PASS" if report["ok"] else "FAIL") + " cross-view reconciliation")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--season", default="s18")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    report = build_report(args.season)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
