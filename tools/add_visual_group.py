#!/usr/bin/env python3
"""Append one captured boundary-review group to the visual-review plan.

The group is built from sidecars in an isolated capture directory. Existing
groups and frames are never modified; this is the pass-3 replacement for the
hardcoded pass-2 builder.

Usage:
    python tools/add_visual_group.py \
      --group-id G-P3-1062-2446 --boundary-id B-P3-1062-2446 \
      --match-id 1062 --source-id src-s18-w04d02 --candidate-seconds 2446 \
      --team-a DEWA --team-b ONIC \
      --capture-dir analysis/cache/video-frames/pass3/1062-2443-2449 \
      --promotion-requires-same-frame
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLAN = REPO / "analysis" / "evidence" / "visual-review-plan.json"
ALIASES = {
    "EVOS": ["EVOS"], "RRQ": ["RRQ", "RRQ HOSHI"], "NAVI": ["NAVI"],
    "AE": ["AE", "ALTER EGO"], "ONIC": ["ONIC"],
    "TLID": ["TLID", "TEAM LIQUID ID", "TEAM LIQUID"],
    "BTR": ["BTR", "BIGETRON", "VITALITY"], "GEEK": ["GEEK", "GEEKFAM"],
    "DEWA": ["DEWA", "DEWA UNITED"],
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--group-id", required=True)
    parser.add_argument("--boundary-id", required=True)
    parser.add_argument("--match-id", required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--candidate-seconds", type=float, required=True)
    parser.add_argument("--team-a", required=True)
    parser.add_argument("--team-b", required=True)
    parser.add_argument("--capture-dir", required=True)
    parser.add_argument("--promotion-requires-same-frame", action="store_true")
    parser.add_argument("--no-boundary", action="store_true",
                        help="add only the frame group; do not add a canonical boundary claim")
    parser.add_argument("--related-to-boundary", default=None,
                        help="attach the new group as related evidence to an existing boundary claim")
    parser.add_argument("--retire-boundary", default=None)
    parser.add_argument("--claim", default=None)
    parser.add_argument("--question", default=None)
    parser.add_argument("--plan", default=str(PLAN))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    plan_path = Path(args.plan)
    plan = load(plan_path)
    if any(g["group_id"] == args.group_id for g in plan["groups"]):
        raise SystemExit(f"group already exists: {args.group_id}")
    if any(b["boundary_id"] == args.boundary_id for b in plan["boundary_claims"]):
        raise SystemExit(f"boundary already exists: {args.boundary_id}")

    capture_dir = REPO / args.capture_dir
    sidecars = sorted(capture_dir.rglob("*.json"))
    rows = []
    for side_path in sidecars:
        if side_path.name.endswith("-capture-index.json"):
            continue
        side = load(side_path)
        if side.get("source_id") != args.source_id:
            continue
        if side.get("status") != "succeeded" and side.get("capture_status") != "derived":
            continue
        if not side.get("actual_seconds"):
            continue
        rows.append(side)
    if not rows:
        raise SystemExit(f"no successful sidecars for {args.source_id} in {capture_dir}")
    rows.sort(key=lambda row: float(row["actual_seconds"]))
    used_ids = {f["frame_id"] for g in plan["groups"] for f in g["frames"]}
    frames = []
    for side in rows:
        actual = float(side["actual_seconds"])
        png = str(side["output_path"]).replace("\\", "/")
        frame_id = f"DF3-{args.source_id.replace('src-s18-', '')}-{round(actual)}"
        if frame_id in used_ids:
            frame_id += "-crop"
        used_ids.add(frame_id)
        frames.append({
            "frame_id": frame_id,
            "path": png,
            "sidecar_path": png[:-4] + ".json",
            "capture_status": side.get("capture_status", side.get("status", "unknown")),
        })
    team_a = args.team_a.upper()
    team_b = args.team_b.upper()
    question = args.question or (
        f"These are {len(frames)} ordered frames from {args.source_id} near {args.candidate_seconds:.0f}s. "
        f"Candidate: series {args.match_id} {team_a} vs {team_b}, game 1. For each image, transcribe the "
        "match label, team names/logos, scoreboard, game clock or countdown, and describe the scene. "
        "In answers include: scene_type (gameplay, draft, pre-match, analyst desk, schedule, standings, "
        "map overview, post-game, promo, interview), teams (exact visible pairing or 'none'), match_label, "
        "clock_or_countdown (exact text), game1_started. Is a visible 00:00 game clock present together "
        "with the claimed pairing? A countdown or draft screen is confirmation only, not a game start."
    )
    claim = args.claim or (
        f"At the selected frames from {args.source_id} near {args.candidate_seconds:g}s, series "
        f"{args.match_id} ({team_a} vs {team_b}) shows a visible 00:00 game clock with the correct pairing."
    )
    group = {
        "group_id": args.group_id,
        "kind": "group",
        "claim_id": args.boundary_id,
        "claim": claim,
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
        "boundary_id": args.boundary_id,
        "match_detail_id": args.match_id,
        "source_id": args.source_id,
        "team_a": team_a,
        "team_b": team_b,
        "candidate_start_seconds": args.candidate_seconds,
        "frame_group": args.group_id,
        "claim": f"Series {args.match_id} ({team_a} vs {team_b}) starts at {args.candidate_seconds:g}s; "
                 "only a visible 00:00 game clock with the correct pairing promotes.",
        "status_effect": "no_change",
        "promotion_requires_same_frame": bool(args.promotion_requires_same_frame),
    }
    if args.retire_boundary:
        before = len(plan["boundary_claims"])
        plan["boundary_claims"] = [b for b in plan["boundary_claims"]
                                   if b["boundary_id"] != args.retire_boundary]
        if len(plan["boundary_claims"]) == before:
            raise SystemExit(f"retire target not found: {args.retire_boundary}")
    plan["groups"].append(group)
    if not args.no_boundary:
        plan["boundary_claims"].append(boundary)
    if args.related_to_boundary:
        target = next((b for b in plan["boundary_claims"]
                       if b["boundary_id"] == args.related_to_boundary), None)
        if target is None:
            raise SystemExit(f"related boundary not found: {args.related_to_boundary}")
        related = target.setdefault("related_groups", [])
        if args.group_id not in related:
            related.append(args.group_id)
    plan["updated_at"] = datetime.now(timezone.utc).isoformat()
    print(f"add {args.group_id}: {frames[0]['frame_id']} .. {frames[-1]['frame_id']} ({len(frames)} frames)")
    if args.no_boundary:
        print(f"group-only: no boundary claim for {args.boundary_id}")
    else:
        print(f"add {args.boundary_id}: candidate {args.candidate_seconds:g}s, same-frame promotion={bool(args.promotion_requires_same_frame)}")
    if args.dry_run:
        return 0
    tmp = plan_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(plan_path)
    print(f"wrote {plan_path}: {len(plan['groups'])} groups, {len(plan['boundary_claims'])} claims")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
