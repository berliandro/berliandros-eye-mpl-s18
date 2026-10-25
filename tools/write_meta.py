"""Write a season provenance record (meta.json) from the committed database.

Records what a build was made from. Does not modify the database, so it is safe
to run against the published artifact.
"""
import json
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from season import resolve

season = resolve("s18")
con = sqlite3.connect(season["database"])
con.row_factory = sqlite3.Row
tables = [r[0] for r in con.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in tables}
cfg = json.loads(Path(season["config"]).read_text(encoding="utf-8"))
schedule = [dict(r) for r in con.execute(
    "SELECT schedule_id, team_a, team_b, score_a, score_b, status, match_detail_id "
    "FROM schedule_all")]
def playoff(row):
    sid = str(row.get("schedule_id") or "").lower()
    return "playoff" in sid or (row.get("team_a") == "TBD" and row.get("team_b") == "TBD")
regular = [r for r in schedule if not playoff(r)]
completed = [r for r in regular if str(r.get("status")) == "completed"]
expected_games = 0
for r in completed:
    try:
        expected_games += int(r.get("score_a")) + int(r.get("score_b"))
    except (TypeError, ValueError):
        pass
official_match_wins = con.execute("SELECT COALESCE(SUM(match_win),0) FROM standings").fetchone()[0]
official_game_wins = con.execute("SELECT COALESCE(SUM(game_win),0) FROM standings").fetchone()[0]
expected_regular = int(cfg["totalRegularFixtures"])
detail_matches = counts.get("matches", 0)
games_count = counts.get("games", 0)
final = (cfg.get("regularSeasonStatus") == "final" and
         len(completed) == expected_regular == detail_matches and
         games_count == expected_games == official_game_wins and
         official_match_wins == len(completed))
latest = con.execute(
    "SELECT MAX(iso_date) FROM matches WHERE status='completed'").fetchone()[0]
quality_path = Path(season["meta"]).parent / "quality.json"
quality = {}
if quality_path.exists():
    try:
        quality = json.loads(quality_path.read_text(encoding="utf-8"))
    except Exception:
        quality = {}
try:
    commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                     cwd=str(season["database"].parents[1])).decode().strip()
except Exception:
    commit = ""

meta = {
    "schema_version": 1,
    "season_id": season["id"],
    "display_name": season["displayName"],
    "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "layout": season["layout"],
    "snapshot_status": "final" if final else "partial",
    "snapshot_scope": "completed regular season; playoffs excluded",
    "verified_as_of": latest,
    "sources": {
        "hub": "https://mpl.mlbbhub.com/api/v1/id",
        "liquipedia": "https://liquipedia.net/mobilelegends/api.php",
        "liquipedia_page": "MPL/Indonesia/Season_18/Regular_Season",
    },
    "expected": {
        "regular_fixtures": expected_regular,
        "playoff_fixtures": int(cfg["playoffMatches"]),
        "completed_fixtures": len(completed),
        "games_from_scores": expected_games,
    },
    "reconciliation": {
        "official_match_wins": official_match_wins,
        "official_game_wins": official_game_wins,
        "detail_matches": detail_matches,
        "games_rows": games_count,
        "team_game_rows": counts.get("team_games", 0),
        "reconciled": final,
    },
    "quality": {
        "draft_conflicts": quality.get("draft_conflicts", []),
        "unresolved_draft_conflicts": quality.get("unresolved_draft_conflicts", []),
        "ban_set_conflicts": quality.get("ban_set_conflicts", []),
        "blank_bans_removed_by_enrichment": quality.get(
            "blank_bans_removed_by_enrichment", 0),
        "sides_filled_from_liquipedia": quality.get(
            "sides_filled_from_liquipedia", 0),
        "missing_sides": quality.get("missing_sides", 0),
        "missing_lanes": quality.get("missing_lanes", 0),
        "missing_map_modes": quality.get("missing_map_modes", 0),
        "games_without_ten_bans": quality.get("games_without_ten_bans", []),
    },
    "row_counts": counts,
    "build_commit": commit,
}
out = season["meta"]
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("wrote", out)
print(json.dumps(counts, indent=2))
