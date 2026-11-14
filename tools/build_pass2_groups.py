#!/usr/bin/env python3
"""Add pass-2 boundary review groups to the visual-review plan.

For each requested match id, finds the freshly captured frames for the
candidate offset (three ordered frames at t-5, t, t+5), appends one frame
group and one boundary claim to analysis/evidence/visual-review-plan.json,
and prints a summary.

Frames are discovered from sidecars, not filenames, so the requested and
actual capture times stay authoritative.

Usage:
    python tools/build_pass2_groups.py --match-ids 1042,1044,... \
        --captured-after 2026-11-02T14:43:00+00:00
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLAN = REPO / "analysis" / "evidence" / "visual-review-plan.json"
OFFSETS = REPO / "analysis" / "evidence" / "game-offsets.json"
FRAME_ROOT = REPO / "analysis" / "cache" / "video-frames"

ALIASES = {
    "EVOS": ["EVOS"],
    "RRQ": ["RRQ", "RRQ HOSHI"],
    "NAVI": ["NAVI"],
    "AE": ["AE", "ALTER EGO"],
    "ONIC": ["ONIC"],
    "TLID": ["TLID", "TEAM LIQUID ID", "TEAM LIQUID", "LIQUID ID"],
    "BTR": ["BTR", "BIGETRON", "VITALITY"],
    "GEEK": ["GEEK", "GEEKFAM"],
    "DEWA": ["DEWA", "DEWA UNITED"],
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def find_candidate(matches: list[dict], source_id: str, seconds: float) -> dict | None:
    best = None
    for item in matches:
        delta = abs(float(item.get("requested_seconds", -1)) - seconds)
        if delta > 2:
            continue
        if best is None or delta < best[0]:
            best = (delta, item)
    return best[1] if best else None


def captured_frames(source_id: str, seconds: float, after: str) -> list[dict]:
    matches = []
    for side_path in sorted(FRAME_ROOT.glob(f"{source_id}/*.json")):
        try:
            side = load(side_path)
        except (OSError, ValueError):
            continue
        if str(side.get("captured_at", "")) < after:
            continue
        matches.append(side)
    chosen = find_candidate(matches, source_id, seconds)
    if not chosen:
        raise SystemExit(f"no captured frame for {source_id} @ {seconds}s after {after}")
    requested = float(chosen["requested_seconds"])
    # The capture tool writes exactly three frames per around-seconds request.
    trio = [m for m in matches
            if abs(float(m.get("requested_seconds", -1)) - requested) < 0.01]
    trio.sort(key=lambda m: float(m["actual_seconds"]))
    if len(trio) != 3:
        raise SystemExit(f"expected 3 frames for {source_id} @ {seconds}s, found {len(trio)}")
    frames = []
    for side in trio:
        png = side["output_path"].replace("\\", "/")
        frames.append({
            "frame_id": f"DF2-{source_id.replace('src-s18-', '')}-{round(float(side['actual_seconds']))}",
            "path": png,
            "sidecar_path": png[:-4] + ".json",
            "capture_status": side.get("status", "unknown"),
        })
    return frames


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--match-ids", required=True,
                        help="comma-separated match_detail_id values")
    parser.add_argument("--captured-after", default="2026-11-02T14:43:00+00:00")
    parser.add_argument("--plan", default=str(PLAN))
    parser.add_argument("--offsets", default=str(OFFSETS))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    wanted = [m.strip() for m in args.match_ids.split(",") if m.strip()]
    plan = load(Path(args.plan))
    offsets = load(Path(args.offsets))
    by_id = {}
    for source_id, source in offsets["sources"].items():
        for series in source["series"]:
            by_id[series["match_detail_id"]] = (source_id, source, series)

    existing_groups = {g["group_id"] for g in plan["groups"]}
    existing_boundaries = {b["boundary_id"] for b in plan["boundary_claims"]}
    added = []
    for match_id in wanted:
        source_id, source, series = by_id[match_id]
        seconds = series["start_seconds"]
        if seconds is None:
            raise SystemExit(f"{match_id}: null offset, not a pass-2 target")
        group_id = f"G-P2-{match_id}-{seconds}"
        boundary_id = f"B-P2-{match_id}-{seconds}"
        if group_id in existing_groups or boundary_id in existing_boundaries:
            print(f"skip {group_id}: already planned")
            continue
        team_a, team_b = series["team_a"].upper(), series["team_b"].upper()
        frames = captured_frames(source_id, float(seconds), args.captured_after)
        question = (
            f"These are three ordered frames from {source_id} near {seconds}s. "
            f"Candidate: series {match_id} {team_a} vs {team_b}, game 1, starts at {seconds}s. "
            "For each image, transcribe the match label, team names/logos, scoreboard, clock or "
            "countdown, and describe the scene. In answers include: scene_type (one of gameplay, "
            "draft, pre-match, analyst desk, schedule, standings, map overview, post-game, promo, "
            "interview); teams (the exact visible pairing, e.g. 'A vs B', or 'none'); match_label; "
            "clock_or_countdown (exact text); game1_started (yes/no and why). "
            "Is the claimed pairing visible? Is a game-1 draft or a 00:00 game clock visible?"
        )
        group = {
            "group_id": group_id,
            "kind": "group",
            "claim_id": boundary_id,
            "claim": (
                f"At ~{seconds}s the broadcast shows series {match_id} "
                f"({team_a} vs {team_b}) at the game-1 boundary."
            ),
            "question": question,
            "frames": frames,
            "rule": {
                "type": "required_text",
                "required": [
                    {"name": f"team_{team_a.lower()}", "any": ALIASES.get(team_a, [team_a])},
                    {"name": f"team_{team_b.lower()}", "any": ALIASES.get(team_b, [team_b])},
                ],
                "fallback": "context-only",
            },
            "max_disposition": None,
        }
        boundary = {
            "boundary_id": boundary_id,
            "match_detail_id": match_id,
            "source_id": source_id,
            "team_a": team_a,
            "team_b": team_b,
            "candidate_start_seconds": seconds,
            "frame_group": group_id,
            "claim": (
                f"Series {match_id} ({team_a} vs {team_b}) starts at {seconds}s; game 1 boundary."
            ),
            "status_effect": "no_change",
        }
        plan["groups"].append(group)
        plan["boundary_claims"].append(boundary)
        added.append((match_id, group_id, [f["frame_id"] for f in frames]))
        print(f"add {group_id}: {frames[0]['frame_id']} .. {frames[-1]['frame_id']}")

    if not added:
        print("nothing to add")
        return 0
    plan["updated_at"] = datetime.now(timezone.utc).isoformat()
    if args.dry_run:
        print(f"dry run: would append {len(added)} groups")
        return 0
    tmp = Path(args.plan).with_suffix(".json.tmp")
    tmp.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(args.plan)
    print(f"wrote {args.plan}: {len(plan['groups'])} groups, "
          f"{len(plan['boundary_claims'])} boundary claims")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
