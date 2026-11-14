#!/usr/bin/env python3
"""Audit captured visual evidence and write a reproducible inventory.

Scans the git-ignored frame cache, verifies sidecar hashes and capture status,
classifies frames covered by the DeepSeek review plan, and records excluded
scratch/failed captures. The cache is local-only; the committed JSON is a
snapshot for auditability.

Usage:
    python tools/audit_visual_evidence.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CACHE = REPO / "analysis" / "cache" / "video-frames"
PLAN = REPO / "analysis" / "evidence" / "visual-review-plan.json"
OUT = REPO / "analysis" / "evidence" / "visual-evidence-audit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not CACHE.exists():
        print(f"frame cache not found: {CACHE}; this audit is local-only", file=sys.stderr)
        return 1
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    plan_paths = {f["path"]: f["frame_id"] for g in plan["groups"] for f in g["frames"]}
    pngs = sorted(CACHE.rglob("*.png"))
    sidecars = sorted(p for p in CACHE.rglob("*.json") if not p.name.endswith("-capture-index.json"))

    official = []
    excluded = []
    hash_mismatches = []
    missing_sidecars = []
    for png in pngs:
        rel = str(png.relative_to(REPO)).replace("\\", "/")
        side = png.with_suffix(".json")
        data = json.loads(side.read_text(encoding="utf-8")) if side.exists() else {}
        digest = sha256(png)
        stored = data.get("output_sha256")
        row = {
            "path": rel,
            "sha256": digest,
            "bytes": png.stat().st_size,
            "sidecar_path": str(side.relative_to(REPO)).replace("\\", "/") if side.exists() else None,
            "sidecar_status": data.get("status"),
            "sidecar_hash": stored,
            "sidecar_hash_matches": (stored == digest) if stored else None,
            "requested_seconds": data.get("requested_seconds"),
            "actual_seconds": data.get("actual_seconds"),
            "capture_status": data.get("capture_status", data.get("status")),
            "error": data.get("error"),
            "derived_from_path": data.get("derived_from_path"),
        }
        if not side.exists():
            missing_sidecars.append(rel)
        elif stored and stored != digest:
            hash_mismatches.append(rel)
        if rel in plan_paths:
            row["frame_id"] = plan_paths[rel]
            official.append(row)
        else:
            excluded.append(row)

    sidecars_without_png = []
    for side in sidecars:
        if side.with_suffix(".png").exists():
            continue
        data = json.loads(side.read_text(encoding="utf-8"))
        sidecars_without_png.append({
            "sidecar_path": str(side.relative_to(REPO)).replace("\\", "/"),
            "status": data.get("status"),
            "error": data.get("error"),
            "requested_seconds": data.get("requested_seconds"),
            "actual_seconds": data.get("actual_seconds"),
            "source_id": data.get("source_id"),
        })

    failed_captures = [
        {
            "path": row["path"],
            "frame_id": row.get("frame_id"),
            "status": row.get("sidecar_status"),
            "error": row.get("error"),
        }
        for row in official + excluded
        if row.get("sidecar_status") == "failed"
    ]
    # Add sidecar-only failures.
    for row in sidecars_without_png:
        failed_captures.append({
            "path": row["sidecar_path"],
            "frame_id": None,
            "status": row.get("status"),
            "error": row.get("error"),
        })

    summary = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "cache_root": str(CACHE.relative_to(REPO)).replace("\\", "/"),
        "note": "Frame cache is Git-ignored and local-only. Hashes in this audit are computed from the local "
                "PNG bytes; the DeepSeek review ledger records the same hashes for reviewed frames.",
        "totals": {
            "png_frames": len(pngs),
            "sidecars": len(sidecars),
            "official_plan_frames": len(plan_paths),
            "official_frames_present": len(official),
            "excluded_frames": len(excluded),
            "hash_mismatches": len(hash_mismatches),
            "missing_sidecars": len(missing_sidecars),
            "sidecars_without_png": len(sidecars_without_png),
            "failed_captures": len(failed_captures),
        },
        "hash_mismatches": hash_mismatches,
        "missing_sidecars": missing_sidecars,
        "sidecars_without_png": sidecars_without_png,
        "failed_captures": failed_captures,
        "official_frames": official,
        "excluded_frames": excluded,
    }
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary["totals"], indent=2))
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
