#!/usr/bin/env python3
"""Build the single canonical coverage matrix for the MPL ID S18 project.

The matrix joins the canonical database snapshot, the 27-source transcript plan,
the transcript observation ledgers, the visual-review status, and the Markdown
page inventory. It is the only report that should be cited for project coverage.

Usage:
    python tools/build_coverage_matrix.py
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import stats_query as sq

REPO = Path(__file__).resolve().parent.parent
EVIDENCE = REPO / "analysis" / "evidence"
REPORTS = REPO / "analysis" / "reports"
MATCHES = REPO / "analysis" / "matches"
PLAN_PATH = EVIDENCE / "transcript-pipeline-plan.json"
VISUAL_PATH = EVIDENCE / "visual-review-status.json"
LEDGER_DIR = EVIDENCE / "transcript-observations"
PILOT_LEDGER = EVIDENCE / "pilot-ledger.jsonl"
OUT_JSON = EVIDENCE / "coverage-matrix.json"
OUT_MD = REPORTS / "coverage-matrix.md"

DB_MARKER = "<!-- db-evidence:start -->"
TRANSCRIPT_MARKER = "## Validated transcript observations"
TEAM_SYNTHESIS_MARKER = "## Evidence-backed profile"
HERO_SYNTHESIS_MARKER = "## Evidence-backed profile"
STRATEGY_MARKER = "## Evidence-backed analysis"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def count_pilot_store() -> dict[str, int]:
    rows = load_jsonl(PILOT_LEDGER)
    return dict(Counter(str(row.get("record_type")) for row in rows))


def load_transcript_observations(plan_by_source: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(LEDGER_DIR.glob("*.jsonl")):
        rows.extend(load_jsonl(path))
    accepted_by_match: dict[str, int] = defaultdict(int)
    for row in rows:
        if row.get("status") != "accepted":
            continue
        source_id = str(row.get("source_id", ""))
        match_id = str(plan_by_source.get(source_id, {}).get("match_detail_id", ""))
        if match_id:
            accepted_by_match[match_id] += 1
    return rows, dict(accepted_by_match)


def load_visual_by_match() -> dict[str, dict[str, Any]]:
    data = load_json(VISUAL_PATH)
    return {str(row["match_detail_id"]): row for row in data.get("series", [])}


def page_marker(path: Path, marker: str) -> bool:
    return marker in read_text(path)


def find_match_report(match_id: str, plan_by_match: dict[str, dict[str, Any]]) -> Path | None:
    planned = plan_by_match.get(match_id)
    if planned:
        candidate = REPO / str(planned["match_report"])
        if candidate.is_file():
            return candidate
    matches = sorted(MATCHES.glob(f"{match_id}-*.md"))
    return matches[0] if matches else None


def main() -> int:
    schedule = sq.schedule_all()
    games = sq.all_games()
    team_season = sq.all_team_season()
    player_season = sq.all_player_season()
    hero_stats = sq.all_hero_stats()

    plan = load_json(PLAN_PATH)
    plan_sources = plan.get("sources", [])
    plan_by_match = {str(item["match_detail_id"]): item for item in plan_sources}
    plan_by_source = {str(item["source_id"]): item for item in plan_sources}
    visual_by_match = load_visual_by_match()
    obs_rows, accepted_by_match = load_transcript_observations(plan_by_source)
    obs_status = Counter(str(row.get("status")) for row in obs_rows)
    entities = {"players": set(), "teams": set(), "heroes": set()}
    for row in obs_rows:
        if row.get("status") != "accepted":
            continue
        for key in entities:
            values = row.get("entities", {}).get(key) or []
            entities[key].update(str(value) for value in values)

    games_by_match: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for game in games.rows:
        games_by_match[str(game["match_detail_id"])].append(game)

    matches: list[dict[str, Any]] = []
    for row in schedule.rows:
        match_id = str(row["match_detail_id"])
        report = find_match_report(match_id, plan_by_match)
        text = read_text(report) if report else ""
        planned = plan_by_match.get(match_id)
        vrow = visual_by_match.get(match_id, {})
        games_for_match = games_by_match.get(match_id, [])
        has_db = DB_MARKER in text
        has_transcript = TRANSCRIPT_MARKER in text
        if planned and has_transcript and has_db:
            evidence_status = "transcript+db"
        elif has_db:
            evidence_status = "db-only"
        else:
            evidence_status = "incomplete"
        matches.append({
            "match_detail_id": match_id,
            "iso_date": row["iso_date"],
            "team_a": row["team_a"],
            "team_b": row["team_b"],
            "score": f"{row['score_a']}-{row['score_b']}",
            "games": len(games_for_match),
            "match_report": str(report.relative_to(REPO)).replace("\\", "/") if report else None,
            "report_exists": report is not None,
            "db_evidence": has_db,
            "transcript": {
                "covered": planned is not None,
                "source_id": planned.get("source_id") if planned else None,
                "status": planned.get("status") if planned else None,
                "observations_accepted": accepted_by_match.get(match_id, 0),
                "section_present": has_transcript,
            },
            "visual_status": vrow.get("visual_status", "not_reviewed"),
            "evidence_status": evidence_status,
        })

    team_pages = sorted((REPO / "analysis" / "teams").glob("*.md"))
    team_season_by_code = {str(row["team"]).upper(): row for row in team_season.rows}
    team_rows = []
    for page in team_pages:
        code = page.stem.upper()
        season = team_season_by_code.get(code, {})
        team_rows.append({
            "team": code,
            "page": str(page.relative_to(REPO)).replace("\\", "/"),
            "games": season.get("games"),
            "wins": season.get("wins"),
            "losses": season.get("losses"),
            "transcript_mentions": sum(1 for row in obs_rows if row.get("status") == "accepted" and code in (row.get("entities", {}).get("teams") or [])),
            "synthesis": page_marker(page, TEAM_SYNTHESIS_MARKER),
        })

    hero_pages = sorted((REPO / "analysis" / "heroes").glob("*.md"))
    hero_by_name = {str(row["hero"]).upper(): row for row in hero_stats.rows}
    hero_rows = []
    for page in hero_pages:
        name = page.stem.upper()
        stats = hero_by_name.get(name, {})
        hero_rows.append({
            "hero": page.stem,
            "page": str(page.relative_to(REPO)).replace("\\", "/"),
            "picks": stats.get("pick"),
            "bans": stats.get("ban"),
            "win_rate": stats.get("win_rate"),
            "synthesis": page_marker(page, HERO_SYNTHESIS_MARKER),
        })

    strategy_pages = sorted((REPO / "analysis" / "strategy").glob("*.md"))
    briefs = sorted((REPO / "analysis" / "coaching" / "teams").glob("*.md")) if (REPO / "analysis" / "coaching" / "teams").is_dir() else []
    head_coach = REPO / "analysis" / "coaching" / "head-coach-brief.md"

    database_players = {str(row["player"]).upper() for row in player_season.rows}
    database_heroes = {str(row["hero"]).upper() for row in hero_stats.rows}
    picked_heroes = {str(row["hero"]).upper() for row in sq.all_picks().rows}
    dossier_players = {re.sub(r"[^A-Z0-9]", "", path.stem.upper()) for path in (REPO / "analysis" / "players").glob("*.md")}
    normalized_database_players = {re.sub(r"[^A-Z0-9]", "", name) for name in database_players}

    summary = {
        "matches_total": len(matches),
        "reports_present": sum(1 for m in matches if m["report_exists"]),
        "db_evidence_blocks": sum(1 for m in matches if m["db_evidence"]),
        "transcript_matches": sum(1 for m in matches if m["transcript"]["covered"]),
        "transcript_complete": sum(1 for m in matches if m["transcript"]["status"] == "complete"),
        "transcript_partial": sum(1 for m in matches if m["transcript"]["status"] == "partial"),
        "db_only_matches": sum(1 for m in matches if not m["transcript"]["covered"]),
        "evidence_complete": sum(1 for m in matches if m["evidence_status"] in {"transcript+db", "db-only"}),
        "evidence_incomplete": sum(1 for m in matches if m["evidence_status"] == "incomplete"),
        "games_total": len(games.rows),
        "games_with_vod": sum(1 for g in games.rows if g.get("vod_url")),
        "games_with_map_mode": sum(1 for g in games.rows if g.get("map_mode")),
        "visual_verified": sum(1 for m in matches if m["visual_status"] == "visually_verified"),
        "visual_context_only": sum(1 for m in matches if m["visual_status"] == "context-only"),
        "visual_rejected": sum(1 for m in matches if m["visual_status"] == "rejected"),
        "visual_inconclusive": sum(1 for m in matches if m["visual_status"] == "inconclusive"),
        "visual_no_candidate": sum(1 for m in matches if m["visual_status"] == "no_candidate_waiver"),
        "player_dossiers": len(dossier_players),
        "database_players": len(database_players),
        "player_dossiers_missing": sorted(normalized_database_players - dossier_players),
        "players_in_transcript": len(entities["players"]),
        "teams": len(team_pages),
        "teams_with_synthesis": sum(1 for row in team_rows if row["synthesis"]),
        "hero_pages": len(hero_pages),
        "database_heroes": len(database_heroes),
        "heroes_picked": len(picked_heroes),
        "heroes_with_synthesis": sum(1 for row in hero_rows if row["synthesis"]),
        "strategy_pages": len(strategy_pages),
        "strategy_with_synthesis": sum(1 for page in strategy_pages if page_marker(page, STRATEGY_MARKER)),
        "team_briefs": len(briefs),
        "head_coach_brief": head_coach.is_file(),
        "transcript_rows": len(obs_rows),
        "transcript_accepted": obs_status.get("accepted", 0),
        "transcript_rejected": obs_status.get("rejected", 0),
        "transcript_resolved": obs_status.get("resolved", 0),
        "pilot_series": 3,
        "pilot_store": count_pilot_store(),
        "teams_in_transcript": len(entities["teams"]),
        "heroes_in_transcript": len(entities["heroes"]),
    }

    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "description": "Canonical coverage matrix for MPL ID S18. Joins the database snapshot, transcript plan and ledgers, visual status, and page inventory.",
        "snapshot_id": schedule.snapshot_id,
        "snapshot_sha256": schedule.snapshot_sha256,
        "definitions": {
            "match_evidence_pass": "The match report exists and contains the deterministic database evidence block; transcript coverage is recorded separately and must not be implied when absent.",
            "db_only": "No transcript source for this series; evidence is database-backed only.",
            "transcript": "A source ledger exists and the report carries validated transcript observations; partial sources are labeled.",
        },
        "summary": summary,
        "matches": matches,
        "teams": team_rows,
        "heroes": hero_rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# MPL S18 canonical coverage matrix",
        "",
        f"Generated by `tools/build_coverage_matrix.py`. Database snapshot `{schedule.snapshot_id}` (`{schedule.snapshot_sha256[:12]}…`).",
        "This report is the single source of truth for coverage. Older coverage summaries are historical.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Completed series | {summary['matches_total']} |",
        f"| Match reports present | {summary['reports_present']} |",
        f"| Database evidence blocks | {summary['db_evidence_blocks']} |",
        f"| Match evidence complete | {summary['evidence_complete']} / {summary['matches_total']} |",
        f"| Transcript-covered series | {summary['transcript_matches']} (complete {summary['transcript_complete']}, partial {summary['transcript_partial']}) |",
        f"| DB-only series (no transcript) | {summary['db_only_matches']} |",
        f"| Games | {summary['games_total']} |",
        f"| Games with VOD | {summary['games_with_vod']} |",
        f"| Games with map mode | {summary['games_with_map_mode']} |",
        f"| Visually verified boundaries | {summary['visual_verified']} |",
        f"| Context-only / rejected / inconclusive / waived | {summary['visual_context_only']} / {summary['visual_rejected']} / {summary['visual_inconclusive']} / {summary['visual_no_candidate']} |",
        f"| Accepted transcript observations | {summary['transcript_accepted']} |",
        f"| Players: dossiers / database / transcript mentions | {summary['player_dossiers']} / {summary['database_players']} / {summary['players_in_transcript']} |",
        f"| Teams: pages / with synthesis | {summary['teams']} / {summary['teams_with_synthesis']} |",
        f"| Heroes: pages / picked / with synthesis | {summary['hero_pages']} / {summary['heroes_picked']} / {summary['heroes_with_synthesis']} |",
        f"| Strategy pages: total / with synthesis | {summary['strategy_pages']} / {summary['strategy_with_synthesis']} |",
        f"| Team briefs / head-coach brief | {summary['team_briefs']} / {'yes' if summary['head_coach_brief'] else 'no'} |",
        "",
        "## Definitions",
        "",
        "- **Match evidence pass:** the report exists and contains the deterministic database block (result, games, team totals, player lines, draft). Transcript coverage is reported separately and never implied.",
        "- **DB-only:** no transcript source exists for that series; the block is the evidence.",
        "- **Transcript:** a validated source ledger exists and the report carries accepted observations; `partial` means the source window is not full gameplay.",
        "",
        "**Pilot store note:** 1036, 1037 and 1107 also have claim-level records in the frozen pilot ledger (`analysis/evidence/pilot-ledger.jsonl`). 1037 has **no transcript source**; its pilot observations are the only semantic evidence for that series. See `analysis/reports/evidence-store.md`.",
        "",
        "## Per-series coverage",
        "",
        "| Match | Date | Series | Score | Games | Transcript | Visual | DB block | Status |",
        "|---:|---|---|---|---:|---|---|---|---|",
    ]
    for m in matches:
        transcript = m["transcript"]
        if transcript["covered"]:
            transcript_label = f"{transcript['source_id']} ({transcript['status']})"
        else:
            transcript_label = "none"
        lines.append(
            f"| {m['match_detail_id']} | {m['iso_date']} | {m['team_a']} vs {m['team_b']} | {m['score']} | {m['games']} | "
            f"{transcript_label} | {m['visual_status']} | {'yes' if m['db_evidence'] else 'no'} | {m['evidence_status']} |"
        )

    lines += [
        "",
        "## Team coverage",
        "",
        "| Team | Games | W-L | Transcript mentions | Synthesis |",
        "|---|---:|---:|---:|---|",
    ]
    for row in team_rows:
        lines.append(
            f"| {row['team']} | {row['games']} | {row['wins']}-{row['losses']} | {row['transcript_mentions']} | "
            f"{'yes' if row['synthesis'] else 'index only'} |"
        )

    lines += [
        "",
        "## Hero page coverage",
        "",
        "| Hero | Picks | Bans | Win rate | Synthesis |",
        "|---|---:|---:|---:|---|",
    ]
    for row in hero_rows:
        lines.append(
            f"| {row['hero']} | {row['picks']} | {row['bans']} | {row['win_rate']} | {'yes' if row['synthesis'] else 'index only'} |"
        )

    pilot = summary["pilot_store"]
    lines += [
        "",
        "## Evidence stores",
        "",
        "| Store | Records | Status |",
        "|---|---:|---|",
        f"| `analysis/evidence/transcript-observations/` | {summary['transcript_rows']} rows ({summary['transcript_accepted']} accepted, {summary['transcript_rejected']} rejected, {summary['transcript_resolved']} resolved) | canonical staging store |",
        f"| `analysis/evidence/pilot-ledger.jsonl` | {sum(pilot.values())} rows ({pilot.get('observation', 0)} observations, {pilot.get('insight', 0)} insights, {pilot.get('audit', 0)} audits, {pilot.get('segment', 0)} segments) | legacy pilot store, superseded |",
        "",
        "## Limits",
        "",
        "- Transcript timestamps are caption-aligned, not frame-accurate; `src-s18-w09d02` is partial.",
        "- The database has no per-game objective counts, gold timelines, vision, communications, or intent. Objective claims stay qualitative or transcript-attributed.",
        "- Visual proof is separate: 0 same-frame `00:00` boundaries are verified.",
        "- This file reports coverage, not coaching conclusions. See the synthesis pages for interpretation.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
