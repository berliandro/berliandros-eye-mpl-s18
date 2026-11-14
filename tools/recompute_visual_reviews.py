#!/usr/bin/env python3
"""Recompute frame dispositions and boundary decisions from stored DeepSeek outputs.

This does not call the API and does not create new visual evidence. It applies a
changed deterministic rule set to the observations/answers already recorded in
the ledger, preserving every screenshot hash and API request id.

Usage:
    python tools/recompute_visual_reviews.py \
        --plan analysis/evidence/visual-review-plan.json \
        --ledger analysis/evidence/deepseek-visual-reviews.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import deepseek_visual_review as dvr  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", default=str(REPO / "analysis" / "evidence" / "visual-review-plan.json"))
    parser.add_argument("--ledger", default=str(REPO / "analysis" / "evidence" / "deepseek-visual-reviews.json"))
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    ledger = json.loads(Path(args.ledger).read_text(encoding="utf-8"))
    groups = {g["group_id"]: g for g in plan["groups"]}
    frames = ledger.get("frames", [])

    changed = 0
    for frame in frames:
        group = groups.get(frame.get("group_id"))
        if not group:
            continue
        side_path = dvr.repo_path(frame.get("sidecar_path", ""))
        if side_path.exists():
            side = json.loads(side_path.read_text(encoding="utf-8"))
            for key in ("derived_from_path", "derived_from_sha256", "crop_box"):
                if side.get(key) is not None:
                    frame[key] = side[key]
            if side.get("width") and side.get("height"):
                frame.setdefault("video_width", side["width"])
                frame.setdefault("video_height", side["height"])
        if group.get("force_disposition"):
            # Preserve the forced rejection (failed capture) without appending the reason twice.
            continue
        output = {
            "observation": frame.get("observation", ""),
            "visible_text": frame.get("visible_text", []),
            "answers": frame.get("answers", {}),
            "model_disposition": frame.get("model_disposition", "inconclusive"),
            "confidence": frame.get("confidence", "low"),
            "limitations": frame.get("limitations", ""),
        }
        evaluation = dvr.evaluate_frame(group, output, frame)
        if evaluation["disposition"] != frame.get("disposition"):
            changed += 1
        for key in ("disposition", "model_disposition", "disposition_basis", "confidence",
                    "observation", "visible_text", "answers", "limitations", "checks"):
            frame[key] = evaluation[key]

    by_group: dict[str, list[dict]] = {}
    for frame in frames:
        by_group.setdefault(frame.get("group_id", ""), []).append(frame)

    boundary_reviews = []
    for boundary in plan.get("boundary_claims", []):
        records = by_group.get(boundary["frame_group"], [])
        related = []
        for rid in boundary.get("related_groups", []):
            related.extend(by_group.get(rid, []))
        boundary_reviews.append(dvr.decide_boundary(boundary, records, related, records, related))

    ledger["boundary_reviews"] = boundary_reviews
    ledger["summary"] = dvr.summarize(frames, boundary_reviews)
    ledger["recomputed_at"] = dvr.now_iso()
    ledger["recompute_note"] = (
        "Frame dispositions and boundary decisions recomputed from stored API observations after the "
        "negation/scene/related-frame/game-number/pre-show rules were corrected. No new API call and no new screenshot."
    )
    out = Path(args.out) if args.out else Path(args.ledger)
    dvr.atomic_write_json(out, ledger)
    print(json.dumps({"changed_frame_dispositions": changed, **ledger["summary"]}, indent=2))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
