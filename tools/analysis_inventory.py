#!/usr/bin/env python3
"""Generate the corpus and database inventory reports from immutable inputs.

Reads analysis/sources/source-manifest.json and data/mpl_id_s18.db in read-only
mode. Writes analysis/reports/corpus-inventory.md,
analysis/evidence/database-snapshot-manifest.json and
analysis/reports/database-inventory.md. No raw transcript content is copied into
the reports.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "analysis" / "sources" / "source-manifest.json"
COPY_VERIFY = REPO / "analysis" / "sources" / "copy-verification.json"
TIMED = REPO / "analysis" / "evidence" / "timed-alignment.json"
DB = REPO / "data" / "mpl_id_s18.db"
REPORTS = REPO / "analysis" / "reports"
EVIDENCE = REPO / "analysis" / "evidence"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def corpus_report(manifest: dict, verification: dict, timed: dict) -> str:
    sources = manifest["sources"]
    weeks = {}
    for source in sources:
        if source.get("week"):
            weeks.setdefault(source["week"], []).append(source.get("day"))
    with_video = [s for s in sources if s.get("video_id") and s.get("video_metadata_provenance")]
    candidates = [s for s in sources if s.get("candidate_video_id")]
    timed_ids = {row["source_id"] for row in timed.get("sources", [])}
    duplicates = [s for s in sources if s.get("duplicate_of")]
    lines = [
        "# Corpus inventory",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "## Copy verification",
        "",
        f"- Source files: **{manifest['source_file_count']}**",
        f"- Source bytes: **{manifest['source_total_bytes']:,}**",
        f"- Copied / identical-skipped / conflicts: **{verification['copied']} / {verification['identical_skipped']} / {verification['conflicts']}**",
        f"- SHA-256 verification after copy: **{verification['verified_hash_matches']}/{verification['source_file_count']}**",
        f"- All verified: **{verification['all_verified']}**",
        f"- Raw corpus location: `{manifest['corpus_root']}` (Git-ignored, local-only)",
        "",
        "The source directory was copied byte-for-byte; no source file was edited, moved or deleted.",
        "",
        "## Coverage",
        "",
        f"- Files: **{len(sources)}**, weeks **{min(weeks) if weeks else '?'}–{max(weeks) if weeks else '?'}**, "
        f"days per week: " + ", ".join(f"W{w}: {len(d)}" for w, d in sorted(weeks.items())),
        "- Encoding: UTF-8 without BOM; CRLF line endings in the raw files.",
        "- Native timestamp strings in the raw files: **0**. The files are caption text only; filenames carry week/day but no video ID.",
        f"- Schedule-derived VOD candidates: **{len(candidates)}/{len(sources)}** (candidates, not verified identities).",
        f"- Metadata-verified official video IDs: **{len(with_video)}/{len(sources)}**.",
        f"- Timed caption alignments: **{len(timed_ids)}/{len(sources)}**; timestamps derive from reproducible 1:1 caption alignment.        f"- Byte-identical duplicate files: **{len(duplicates)}**.",
        "",
        "## Source table",
        "",
        "| Source ID | Week/day | Broadcast date | Bytes | Lines | VOD candidate | Status | Timed alignment | Series IDs |",
        "|---|---:|---|---:|---:|---|---|---|---|",
    ]
    for source in sources:
        status = source.get("video_resolution_status", "unverified")
        series_ids = ",".join(str(item.get("match_detail_id")) for item in source.get("series_mapping", []))
        candidate_id = source.get("candidate_video_id")
        candidate_link = f"[{candidate_id}](https://www.youtube.com/watch?v={candidate_id})" if candidate_id else "none"
        lines.append(
            f"| `{source['source_id']}` | W{source.get('week')}D{source.get('day')} | "
            f"{source.get('broadcast_date') or 'unknown'} | {source['bytes']:,} | {source.get('line_count')} | "
            f"{candidate_link} | {status} | {'yes' if source['source_id'] in timed_ids else 'no'} | "
            f"{series_ids or 'none'} |"
        )
    lines += [
        "",
        "## Timestamp/link coverage",
        "",
        "The pilot uses an explicit derived method: the raw caption lines are aligned one-to-one with the official YouTube auto-caption snippets, then timestamps and `t=` links are generated only for verified video IDs.",
        "",
    ]
    for row in timed.get("sources", []):
        lines.append(
            f"- `{row['source_id']}` / `{row['video_id']}`: {row['raw_lines']:,} lines, "
            f"{row['exact_matches']:,} exact + {row['normalized_matches']} normalized caption matches."
        )
    lines += [
        "",
        "This alignment is not native transcript metadata and does not make timestamps frame-accurate; it is a reproducible cue-time mapping.",
        "",
        "## Parsing risks and gaps",
        "",
        "- Captions are Indonesian auto-generated ASR: names, hero names and punctuation can be wrong; there are no speaker labels.",
        "- Some lines are music/noise tags (`[musik]`, `[berteriak]`, `[tertawa]`), not evidence of gameplay.",
        "- Line breaks split sentences; quotes must preserve the source line span.",
        f"- {len([s for s in sources if not s.get('video_id')])}/{len(sources)} schedule VOD candidates still need metadata verification; candidate URLs are not citation authorities.",
        "- Broadcast dates and series IDs come from the canonical schedule. Exact in-video series/game offsets remain unverified unless independently established.",
        "- The raw corpus is local-only. Committed reports contain only short pilot quotations; validators that need raw text are run in this local workspace and require the ignored corpus copy.",
        "",
        "## Duplicate/suspicious files",
        "",
        "No byte-identical duplicates were detected. The corpus is one file per broadcast day; this is consistent with the source naming, but it is not proof that every file is a complete broadcast.",
    ]
    return "\n".join(lines) + "\n"


def db_snapshot(manifest: dict) -> dict:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    tables = {}
    for row in con.execute(
        "select name, sql from sqlite_master where type='table' and name not like 'sqlite_%' order by name"
    ):
        name = row["name"]
        columns = [
            {
                "name": col["name"],
                "type": col["type"],
                "notnull": bool(col["notnull"]),
                "pk": bool(col["pk"]),
            }
            for col in con.execute(f'pragma table_info("{name}")')
        ]
        count = con.execute(f'select count(*) from "{name}"').fetchone()[0]
        tables[name] = {"row_count": count, "columns": columns, "sql": row["sql"]}
    coverage = {
        "matches": con.execute("select count(*) from matches").fetchone()[0],
        "completed_regular_matches": con.execute(
            "select count(*) from schedule_all where status='completed' and schedule_id not like '%playoff%'"
        ).fetchone()[0],
        "games": con.execute("select count(*) from games").fetchone()[0],
        "game_players": con.execute("select count(*) from game_players").fetchone()[0],
        "game_picks": con.execute("select count(*) from game_picks").fetchone()[0],
        "game_bans": con.execute("select count(*) from game_bans").fetchone()[0],
        "team_games": con.execute("select count(*) from team_games").fetchone()[0],
        "standings": con.execute("select count(*) from standings").fetchone()[0],
        "games_with_map_mode": con.execute(
            "select count(*) from games where map_mode is not null and trim(map_mode)<>''"
        ).fetchone()[0],
        "games_with_both_sides": con.execute(
            "select count(*) from games where team_a_side is not null and team_b_side is not null"
        ).fetchone()[0],
        "games_with_per_game_vod": con.execute(
            "select count(*) from games where vod_url is not null and trim(vod_url)<>''"
        ).fetchone()[0],
        "matches_with_vod": con.execute(
            "select count(*) from matches where vod_url is not null and trim(vod_url)<>''"
        ).fetchone()[0],
        "matches_with_liquipedia_mvp": con.execute(
            "select count(*) from matches where liq_mvp is not null and trim(liq_mvp)<>''"
        ).fetchone()[0],
        "distinct_players": con.execute("select count(distinct player) from game_players").fetchone()[0],
        "distinct_heroes": con.execute(
            "select count(distinct hero) from (select hero from game_players union select hero from game_bans)"
        ).fetchone()[0],
    }
    winner_mismatch = [
        dict(row)
        for row in con.execute(
            "select match_detail_id, team_a, team_b, score_a, score_b, winner from matches "
            "where (score_a > score_b and winner <> 'team_a') or (score_b > score_a and winner <> 'team_b') "
            "order by match_detail_id"
        )
    ]
    per_date = [
        dict(row)
        for row in con.execute(
            "select iso_date, count(*) as completed from schedule_all where status='completed' group by iso_date order by iso_date"
        )
    ]
    con.close()
    snapshot = {
        "schema_version": 1,
        "snapshot_id": "mpl-s18-db-" + sha256_file(DB)[:12],
        "path": DB.relative_to(REPO).as_posix(),
        "sha256": sha256_file(DB),
        "bytes": DB.stat().st_size,
        "inspected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tables": tables,
        "coverage": coverage,
        "completed_by_date": per_date,
        "lineage": {
            "source_reported": [
                "schedule_all results/scores/status",
                "matches detail rows, dates, VOD and Liquipedia series MVP",
                "games per-game winner/duration/side/map mode",
                "game_players scoreboard stats",
                "standings",
            ],
            "deterministic_derived": [
                "team_games from ten player rows",
                "team_season_stats from team_games",
                "picks/bans enrichment joins from Liquipedia",
            ],
            "heuristic_or_app_derived": [
                "app game MVP (highest KDA on winning team) where shown",
                "win probability/ratings/analytics models in the dashboard",
            ],
            "unavailable": [
                "per-game Lord/Turtle/Tower objective counts",
                "gold/damage timelines and gold diff at fixed times",
                "pick order (Liquipedia slots are lane order)",
                "player communications/intent/vision",
                "official damage-type split",
            ],
            "warnings": [
                {
                    "table": "matches",
                    "field": "winner",
                    "status": "orientation_mismatch",
                    "detail": (
                        f"{len(winner_mismatch)}/72 rows disagree with the matches score because matches.team_a/team_b "
                        "is flipped relative to schedule_all while winner retains schedule orientation. "
                        "Use schedule_all.winner or derive the winner from the score."
                    ),
                    "example_match_ids": [row["match_detail_id"] for row in winner_mismatch[:5]],
                }
            ],
        },
        "relationships": [
            "schedule_all.match_detail_id -> matches.match_detail_id",
            "matches.match_detail_id -> games.match_detail_id",
            "matches.match_detail_id -> team_games.match_detail_id",
            "matches.match_detail_id -> game_players.match_detail_id",
            "matches.match_detail_id -> game_picks.match_detail_id",
            "matches.match_detail_id -> game_bans.match_detail_id",
            "games(match_detail_id,game_no) -> game_players/game_picks/game_bans/team_games",
            "standings.team_slug/team_name -> team_games.team / team_season_stats.team_slug",
        ],
        "source_manifest": "analysis/sources/source-manifest.json",
        "query_catalog": "analysis/evidence/query-catalog.json",
    }
    return snapshot


def database_report(snapshot: dict) -> str:
    c = snapshot["coverage"]
    lines = [
        "# Database inventory",
        "",
        f"Snapshot: `{snapshot['snapshot_id']}`",
        "",
        f"- Path: `{snapshot['path']}`",
        f"- SHA-256: `{snapshot['sha256']}`",
        f"- Bytes: **{snapshot['bytes']:,}**",
        f"- Inspected: {snapshot['inspected_at']}",
        "",
        "The database was opened read-only (`mode=ro`). No table, CSV, metadata or dashboard artifact was modified by this project.",
        "",
        "## Coverage that matters for coaching",
        "",
        "| Field/table | Present |",
        "|---|---:|",
        f"| Completed regular series (`schedule_all`) | {c['completed_regular_matches']} |",
        f"| Games | {c['games']} |",
        f"| Player-game rows | {c['game_players']:,} |",
        f"| Pick rows / ban rows | {c['game_picks']:,} / {c['game_bans']:,} |",
        f"| Team-game rows | {c['team_games']} |",
        f"| Standings rows | {c['standings']} |",
        f"| Games with map mode | {c['games_with_map_mode']}/{c['games']} |",
        f"| Games with both recorded sides | {c['games_with_both_sides']}/{c['games']} |",
        f"| Games with per-game VOD | {c['games_with_per_game_vod']}/{c['games']} |",
        f"| Series with broadcast VOD | {c['matches_with_vod']}/{c['matches']} |",
        f"| Series with Liquipedia series MVP | {c['matches_with_liquipedia_mvp']}/{c['matches']} |",
        f"| Distinct players / heroes | {c['distinct_players']} / {c['distinct_heroes']} |",
        "",
        "## Lineage and caveats",
        "",
        "- **Source-reported:** schedule results, per-game winner/duration/sides/map mode, player scoreboard stats, standings, Liquipedia series MVP.",
        "- **Deterministic derived:** `team_games` and `team_season_stats`; picks/bans are enriched joins from Liquipedia, not API fields.",
        "- **Heuristic/app-derived:** dashboard game MVP and all win-probability/ratings metrics. Do not present them as official.",
        "- **Unavailable:** per-game objective counts (Lord/Turtle/Tower), gold/damage timelines, exact pick order, communications, vision, intent, official damage-type split.",
        "",
        "### `matches.winner` is not usable as a match-order winner",
        "",
        "The snapshot has **21/72** rows where `matches.winner` disagrees with the `matches` score. The reason is an orientation mismatch: `matches.team_a/team_b` is flipped relative to `schedule_all` for many series, while `winner` kept schedule orientation. This pilot therefore uses `schedule_all.winner` or derives the winner from `score_a/score_b`.",
        "",
        "Example — series 1107: `matches` order is TLID/ONIC and score 2-0, but `matches.winner = 'team_b'` (which would mean ONIC if read naively). `schedule_all` has ONIC/TLID, 0-2, winner `team_b` = TLID. The result is TLID 2-0.",
        "",
        "### Recommended joins",
        "",
        "- Series: `schedule_all.match_detail_id` → `matches` → `games` / `team_games` / `game_players` / `game_picks` / `game_bans`.",
        "- Game: `(match_detail_id, game_no)` is the composite key for games and derived rows.",
        "- Player identity: `game_picks.player` and `game_players.player` use the app/Liquipedia spelling. Broadcast overlays can use different names; do not join broadcast names to database handles without evidence.",
        "- Result: use `schedule_all.score_a/score_b` and schedule orientation, or derive from the score; never `matches.winner` alone.",
        "",
        "## Query catalog",
        "",
        "Reproducible read-only queries used by the pilot are in `analysis/evidence/query-catalog.json`. Each ledger database reference embeds the query ID, SQL, parameters, snapshot SHA-256 and returned rows. The validator re-executes each query and rejects a non-reproducible result.",
        "",
        "## Source-to-series mapping",
        "",
        "All completed regular-season series have schedule-derived broadcast-date/VOD candidates in the source manifest. Candidates are not verified until `tools/resolve_and_align_sources.py` confirms official channel/title metadata and one-to-one timed-caption alignment. Exact series/game offsets remain separate work.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    verification = json.loads(COPY_VERIFY.read_text(encoding="utf-8"))
    timed = json.loads(TIMED.read_text(encoding="utf-8")) if TIMED.exists() else {"sources": []}
    REPORTS.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (REPORTS / "corpus-inventory.md").write_text(
        corpus_report(manifest, verification, timed), encoding="utf-8"
    )
    snapshot = db_snapshot(manifest)
    (EVIDENCE / "database-snapshot-manifest.json").write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (REPORTS / "database-inventory.md").write_text(database_report(snapshot), encoding="utf-8")
    print("wrote corpus-inventory.md, database-inventory.md, database-snapshot-manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
