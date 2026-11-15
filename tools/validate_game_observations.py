#!/usr/bin/env python3
"""Validate game-transcript observations against the fetched game transcripts.

Usage:
    python tools/validate_game_observations.py
    python tools/validate_game_observations.py --observations analysis/evidence/game-observations/1037.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import stats_query as sq

REPO = Path(__file__).resolve().parent.parent
DEFAULT_DIR = REPO / "analysis" / "evidence" / "game-observations"
MANIFEST = REPO / "analysis" / "evidence" / "game-transcript-manifest.json"
REQUIRED = [
    "record_type", "observation_id", "match_detail_id", "game_no", "source_id",
    "video_id", "snippet_start", "snippet_end", "start_s", "end_s", "quote",
    "quote_sha256", "claim", "claim_type", "topic", "entities", "confidence", "status",
]
ID_RE = re.compile(r"^GOBS-(\d{4})-G([1-3])-(\d{3})$")
SOURCE_RE = re.compile(r"^src-game-([A-Za-z0-9_-]{11})$")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observations", help="one JSONL file; default: all files in game-observations/")
    args = parser.parse_args(argv)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    by_video = {row["video_id"]: row for row in manifest["games"] if row.get("status") == "ok"}
    paths = [Path(args.observations)] if args.observations else sorted(DEFAULT_DIR.glob("*.jsonl"))
    if not paths:
        print("no observation files found")
        return 1

    teams = {str(row["team"]).upper() for row in sq.all_team_season().rows}
    players = {str(row["player"]).upper() for row in sq.all_player_season().rows}
    heroes = {str(row["hero"]).casefold() for row in sq.all_hero_stats().rows}

    errors: list[str] = []
    warnings: list[str] = []
    seen_ids: set[str] = set()
    total = 0
    for path in paths:
        for line_no, row in enumerate(load_jsonl(path), 1):
            total += 1
            label = f"{path.name}:{line_no}"
            missing = [key for key in REQUIRED if key not in row]
            if missing:
                errors.append(f"{label}: missing keys {missing}")
                continue
            observation_id = str(row["observation_id"])
            if observation_id in seen_ids:
                errors.append(f"{label}: duplicate observation_id {observation_id}")
            seen_ids.add(observation_id)
            match_id = str(row["match_detail_id"])
            game_no = int(row["game_no"])
            video_id = str(row["video_id"])
            source_id = str(row["source_id"])
            source_match = SOURCE_RE.match(source_id)
            if not source_match or source_match.group(1) != video_id:
                errors.append(f"{label}: source_id/video_id mismatch")
            if not ID_RE.match(observation_id):
                errors.append(f"{label}: bad observation_id")
            elif ID_RE.match(observation_id).groups()[:2] != (match_id, str(game_no)):
                errors.append(f"{label}: observation_id does not match match/game")
            transcript_row = by_video.get(video_id)
            if not transcript_row:
                errors.append(f"{label}: video_id not in successful transcript manifest")
                continue
            if str(transcript_row["match_detail_id"]) != match_id or int(transcript_row["game_no"]) != game_no:
                errors.append(f"{label}: manifest match/game mismatch for {video_id}")
            transcript_path = REPO / transcript_row["path"]
            snippets = json.loads(transcript_path.read_text(encoding="utf-8"))["snippets"]
            joined = " ".join(str(s["text"]) for s in snippets)
            quote = str(row["quote"])
            offset = joined.find(quote)
            if offset < 0:
                errors.append(f"{label}: quote not found in transcript")
                continue
            actual_hash = hashlib.sha256(quote.encode("utf-8")).hexdigest()
            if actual_hash != row["quote_sha256"]:
                errors.append(f"{label}: quote_sha256 mismatch")
            s0, s1 = int(row["snippet_start"]), int(row["snippet_end"])
            if not (0 <= s0 <= s1 < len(snippets)):
                errors.append(f"{label}: snippet range out of bounds")
                continue
            starts = []
            pos = 0
            for snippet in snippets:
                starts.append(pos)
                pos += len(str(snippet["text"])) + 1
            quote_end = offset + len(quote)
            if offset < starts[s0] or quote_end > starts[s1] + len(str(snippets[s1]["text"])):
                errors.append(f"{label}: quote falls outside snippet_start..snippet_end")
            expected_start = float(snippets[s0]["start"])
            expected_end = float(snippets[s1]["start"]) + float(snippets[s1]["duration"])
            if abs(float(row["start_s"]) - expected_start) > 0.11:
                errors.append(f"{label}: start_s {row['start_s']} != {expected_start:.3f}")
            if abs(float(row["end_s"]) - expected_end) > 0.11:
                errors.append(f"{label}: end_s {row['end_s']} != {expected_end:.3f}")
            entities = row.get("entities") or {}
            for team in entities.get("teams") or []:
                if str(team).upper() not in teams:
                    warnings.append(f"{label}: unknown team {team}")
            for player in entities.get("players") or []:
                if str(player).upper() not in players:
                    warnings.append(f"{label}: unknown player {player}")
            for hero in entities.get("heroes") or []:
                if str(hero).casefold() not in heroes:
                    warnings.append(f"{label}: unknown hero {hero}")

    summary = {
        "files": len(paths),
        "observations": total,
        "errors": len(errors),
        "warnings": len(warnings),
        "error_messages": errors,
        "warning_messages": warnings,
    }
    print(json.dumps(summary, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
