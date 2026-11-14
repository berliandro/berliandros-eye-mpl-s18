#!/usr/bin/env python3
"""Render the canonical database evidence block into every match report.

The block is deterministic and idempotent. It replaces only the
"## Game-level database context" section (or the existing marked block) and
never touches transcript observations, insights, or limits sections.

Usage:
    python tools/build_match_evidence.py
    python tools/build_match_evidence.py --check
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import stats_query as sq

REPO = Path(__file__).resolve().parent.parent
MATCHES = REPO / "analysis" / "matches"
PLAN_PATH = REPO / "analysis" / "evidence" / "transcript-pipeline-plan.json"
MARKER_START = "<!-- db-evidence:start -->"
MARKER_END = "<!-- db-evidence:end -->"
HEADING = "## Game-level database context"
LANE_ORDER = {"EXP": 0, "GOLD": 1, "JUNGLE": 2, "MID": 3, "ROAM": 4}


def fmt_int(value: Any) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "—"


def fmt_duration(seconds: Any) -> str:
    try:
        total = int(seconds)
    except (TypeError, ValueError):
        return "not recorded"
    return f"{total // 60}:{total % 60:02d}"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def find_report(match_id: str, plan_by_match: dict[str, dict[str, Any]]) -> Path | None:
    planned = plan_by_match.get(match_id)
    if planned:
        candidate = REPO / str(planned["match_report"])
        if candidate.is_file():
            return candidate
    matches = sorted(MATCHES.glob(f"{match_id}-*.md"))
    return matches[0] if matches else None


def group_by(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row[key])].append(row)
    return grouped


def render_block(
    match_id: str,
    schedule: dict[str, Any],
    games: list[dict[str, Any]],
    team_games: list[dict[str, Any]],
    player_lines: list[dict[str, Any]],
    picks: list[dict[str, Any]],
    bans: list[dict[str, Any]],
    mvp: str | None,
    plan: dict[str, Any] | None,
    accepted: int,
    snapshot_id: str,
    snapshot_sha: str,
) -> str:
    games_by_no = {int(game["game_no"]): game for game in games}
    teams_by_game = group_by(team_games, "game_no")
    players_by_game = group_by(player_lines, "game_no")
    picks_by_game = group_by(picks, "game_no")
    bans_by_game = group_by(bans, "game_no")
    missing_maps = sum(1 for game in games if not game.get("map_mode"))

    lines = [
        MARKER_START,
        HEADING,
        "",
        f"Database snapshot `{snapshot_id}` · SHA-256 `{snapshot_sha}`. "
        "Queries: `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`, `Q-MATCH-PLAYER-LINES`, `Q-GAME-PICKS`, `Q-GAME-BANS` "
        "(see `analysis/evidence/query-catalog.json`). These are source-reported scoreboard values, not official tournament tables.",
        "",
    ]
    if mvp:
        lines.append(f"**Series MVP (Liquipedia):** {mvp}.")
        lines.append("")

    for game_no in sorted(games_by_no):
        game = games_by_no[game_no]
        winner = game["team_a"] if game["winner"] == "team_a" else game["team_b"]
        map_label = game.get("map_mode") or "map not recorded"
        lines.append(f"### Game {game_no} — {winner} win · {fmt_duration(game.get('duration_sec'))} · {map_label}")
        lines.append("")
        side_a = game.get("team_a_side") or "side not recorded"
        side_b = game.get("team_b_side") or "side not recorded"
        vod = game.get("vod_url")
        vod_label = f"[VOD]({vod})" if vod else "VOD not recorded"
        lines.append(f"Sides: {game['team_a']} {side_a} / {game['team_b']} {side_b} · {vod_label}")
        lines.append("")

        team_rows = sorted(teams_by_game.get(str(game_no), []), key=lambda row: (row["team"] != game["team_a"], row["team"]))
        lines += [
            "| Team | K | D | A | Gold | Hero damage | Tower damage |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
        for row in team_rows:
            lines.append(
                f"| {row['team']} | {fmt_int(row.get('kills'))} | {fmt_int(row.get('deaths'))} | {fmt_int(row.get('assists'))} | "
                f"{fmt_int(row.get('gold'))} | {fmt_int(row.get('hero_damage'))} | {fmt_int(row.get('tower_damage'))} |"
            )
        lines.append("")

        player_rows = sorted(
            players_by_game.get(str(game_no), []),
            key=lambda row: (row["team"] != game["team_a"], row["team"], LANE_ORDER.get(str(row.get("lane", "")).upper(), 9), row["player"]),
        )
        lines += [
            "| Team | Player | Lane | Hero | K/D/A | KDA | Gold | Hero damage | Tower damage |",
            "|---|---|---|---|---:|---:|---:|---:|---:|",
        ]
        for row in player_rows:
            lines.append(
                f"| {row['team']} | {row['player']} | {row.get('lane') or '—'} | {row.get('hero') or '—'} | "
                f"{row.get('kills')}/{row.get('deaths')}/{row.get('assists')} | {row.get('kda')} | "
                f"{fmt_int(row.get('gold'))} | {fmt_int(row.get('hero_damage'))} | {fmt_int(row.get('tower_damage'))} |"
            )
        lines.append("")

        game_picks = picks_by_game.get(str(game_no), [])
        if game_picks:
            picked_by_team: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for row in game_picks:
                picked_by_team[str(row["team"])].append(row)
            lines.append("**Picks**")
            lines.append("")
            for team in sorted(picked_by_team, key=lambda name: (name != game["team_a"], name)):
                entries = sorted(picked_by_team[team], key=lambda row: int(row.get("slot") or 99))
                rendered = ", ".join(
                    f"{row['player']} ({row.get('lane') or '—'}, {row.get('hero') or '—'})" for row in entries
                )
                lines.append(f"- {team}: {rendered}")
            lines.append("")

        game_bans = bans_by_game.get(str(game_no), [])
        if game_bans:
            bans_by_side: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for row in game_bans:
                bans_by_side[str(row["side"])].append(row)
            parts = []
            for side in sorted(bans_by_side):
                heroes = ", ".join(row["hero"] for row in sorted(bans_by_side[side], key=lambda row: int(row.get("ban_order") or 99)))
                parts.append(f"{side} — {heroes}")
            lines.append(f"**Bans:** {' · '.join(parts)}")
            lines.append("")

    lines.append("Draft labels A/B are source draft order; picks are lane-order, not pick order.")
    lines.append("")
    if plan:
        source_id = plan.get("source_id")
        status = plan.get("status")
        lines.append(
            f"**Transcript coverage:** `{source_id}` ({status}); {accepted} accepted observations are carried in this report. "
            "Caster statements are commentary or observation, not database facts."
        )
    else:
        lines.append(
            "**Transcript coverage:** none. This series is database-only; no broadcast quote, timestamp, or caster claim is made."
        )
    map_note = f" Map mode is missing for {missing_maps} of {len(games)} games." if missing_maps else ""
    lines.append("")
    lines.append(
        "**Database limits:** no per-game objective counts, gold/damage timelines, vision, communications, or intent."
        + map_note
    )
    lines.append(MARKER_END)
    return "\n".join(lines)


def replace_section(text: str, block: str) -> str:
    if MARKER_START in text and MARKER_END in text:
        start = text.index(MARKER_START)
        end = text.index(MARKER_END, start) + len(MARKER_END)
        prefix = text[:start].rstrip()
        suffix = text[end:].lstrip("\n")
        return f"{prefix}\n\n{block}\n\n{suffix}"

    if HEADING in text:
        start = text.index(HEADING)
        next_heading = text.find("\n## ", start + len(HEADING))
        end = next_heading if next_heading != -1 else len(text)
        prefix = text[:start].rstrip()
        suffix = text[end:].lstrip("\n")
        return f"{prefix}\n\n{block}\n\n{suffix}"

    return f"{text.rstrip()}\n\n{block}\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report differences without writing")
    args = parser.parse_args(argv)

    schedule = sq.schedule_all()
    games_rows = sq.all_games().rows
    team_rows = sq.all_team_games().rows
    picks_rows = sq.all_picks().rows
    bans_rows = sq.all_bans().rows
    mvp_by_match = {str(row["match_detail_id"]): row.get("liq_mvp") for row in sq.all_match_details().rows}
    plan = read_json(PLAN_PATH)
    plan_by_match = {str(item["match_detail_id"]): item for item in plan.get("sources", [])}

    accepted_by_match: dict[str, int] = defaultdict(int)
    for item in plan.get("sources", []):
        ledger = REPO / str(item["observation_ledger"])
        if ledger.is_file():
            for row in read_jsonl(ledger):
                if row.get("status") == "accepted":
                    accepted_by_match[str(item["match_detail_id"])] += 1

    games_by_match = group_by(games_rows, "match_detail_id")
    teams_by_match = group_by(team_rows, "match_detail_id")
    picks_by_match = group_by(picks_rows, "match_detail_id")
    bans_by_match = group_by(bans_rows, "match_detail_id")

    written = 0
    unchanged = 0
    missing = []
    for schedule_row in schedule.rows:
        match_id = str(schedule_row["match_detail_id"])
        report = find_report(match_id, plan_by_match)
        if report is None:
            missing.append(match_id)
            continue
        player_lines = sq.match_player_lines(match_id).rows
        block = render_block(
            match_id=match_id,
            schedule=schedule_row,
            games=games_by_match.get(match_id, []),
            team_games=teams_by_match.get(match_id, []),
            player_lines=player_lines,
            picks=picks_by_match.get(match_id, []),
            bans=bans_by_match.get(match_id, []),
            mvp=mvp_by_match.get(match_id),
            plan=plan_by_match.get(match_id),
            accepted=accepted_by_match.get(match_id, 0),
            snapshot_id=schedule.snapshot_id,
            snapshot_sha=schedule.snapshot_sha256,
        )
        text = report.read_text(encoding="utf-8")
        updated = replace_section(text, block)
        if updated == text:
            unchanged += 1
            continue
        if not args.check:
            report.write_text(updated, encoding="utf-8")
        written += 1

    print(json.dumps({
        "mode": "check" if args.check else "write",
        "reports_changed": written,
        "reports_unchanged": unchanged,
        "missing_reports": missing,
        "games_rendered": len(games_rows),
        "matches_rendered": len(schedule.rows),
    }, indent=2))
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
