#!/usr/bin/env python3
"""Deterministically rebuild analysis/evidence/visual-review-status.json.

Reads game-offsets.json and the DeepSeek visual-review ledger, maps every one
of the 72 series to a reconciliation row, and rewrites the derived status file.
The single promoted series is identified by its offset status
("visually_verified") plus anchor metadata; its evidence is taken from the
matching "used" anchor frame in the ledger. No new evidence is invented.

Usage:
    python tools/build_visual_review_status.py
Re-running with unchanged inputs produces byte-identical output.
"""
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EVIDENCE = REPO / "analysis" / "evidence"
OFFSETS_PATH = EVIDENCE / "game-offsets.json"
LEDGER_PATH = EVIDENCE / "deepseek-visual-reviews.json"
OUTPUT_PATH = EVIDENCE / "visual-review-status.json"

DESCRIPTION = (
    "Derived reconciliation of game-offsets.json against the DeepSeek visual-review "
    "ledger. This file makes rejections and unpromoted reviews visible without "
    "silently changing canonical offset statuses."
)
NO_CANDIDATE_EVIDENCE = (
    "No team-paired series cue found in the timed captions; no screenshot target "
    "was added. The offset remains null and must not be cited with a timestamp."
)
NOT_REVIEWED_EVIDENCE = (
    "No boundary review was recorded for this non-null offset; visual status is "
    "not_reviewed."
)

DISPOSITION_TO_STATUS = {
    "used": "visually_verified",
    "rejected": "rejected",
    "context-only": "context-only",
    "inconclusive": "inconclusive",
}
ANCHOR_FIELDS = (
    "visual_anchor",
    "anchor_frame_id",
    "anchor_frame_sha256",
    "anchor_seconds",
    "visible_clock",
    "inferred_start_seconds",
    "reviewer",
    "model",
    "api_request_id",
    "promotion_note",
)
CATEGORY_ARRAYS = (
    ("rejected_candidates", "rejected"),
    ("context_only", "context-only"),
    ("inconclusive", "inconclusive"),
    ("no_candidate_waivers", "no_candidate_waiver"),
    ("not_reviewed", "not_reviewed"),
)


def sha256_text_lf(path):
    """Hash a committed text file with LF endings so a CRLF checkout and CI agree."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def base_row(source_id, offset):
    return {
        "match_detail_id": offset["match_detail_id"],
        "source_id": source_id,
        "team_a": offset.get("team_a"),
        "team_b": offset.get("team_b"),
        "start_seconds": offset.get("start_seconds"),
        "offset_status": offset.get("status"),
    }


def boundary_row(source_id, offset, boundary):
    disposition = boundary.get("disposition")
    if disposition not in DISPOSITION_TO_STATUS:
        raise ValueError(f"unknown boundary disposition for {offset['match_detail_id']}: {disposition!r}")
    row = base_row(source_id, offset)
    row.update({
        "visual_status": DISPOSITION_TO_STATUS[disposition],
        "deepseek_disposition": disposition,
        "candidate_start_seconds": boundary.get("candidate_start_seconds"),
        "frame_group": boundary.get("frame_group"),
        "frame_ids": boundary.get("frame_ids", []),
        "frame_sha256": boundary.get("frame_sha256", []),
        "status_effect": boundary.get("status_effect"),
        "evidence": (boundary.get("observation") or "")[:300],
    })
    return row


def waiver_row(source_id, offset):
    null_start = offset.get("start_seconds") is None
    row = base_row(source_id, offset)
    row.update({
        "visual_status": "no_candidate_waiver" if null_start else "not_reviewed",
        "deepseek_disposition": "inconclusive" if null_start else None,
        "candidate_start_seconds": None,
        "frame_group": None,
        "frame_ids": [],
        "frame_sha256": [],
        "status_effect": None,
        "evidence": NO_CANDIDATE_EVIDENCE if null_start else NOT_REVIEWED_EVIDENCE,
    })
    return row


def promoted_row(source_id, offset, frames):
    frame_id = offset.get("anchor_frame_id")
    anchor = frames.get(frame_id)
    if anchor is None:
        raise ValueError(f"promoted series {offset['match_detail_id']}: anchor frame {frame_id!r} missing from ledger")
    sha = anchor.get("screenshot_sha256")
    if sha != offset.get("anchor_frame_sha256"):
        raise ValueError(f"promoted series {offset['match_detail_id']}: anchor frame SHA mismatch")
    if anchor.get("disposition") != "used":
        raise ValueError(f"promoted series {offset['match_detail_id']}: anchor frame is not disposition 'used'")
    row = base_row(source_id, offset)
    row.update({
        "visual_status": "visually_verified",
        "deepseek_disposition": anchor["disposition"],
        "candidate_start_seconds": offset.get("anchor_seconds", offset.get("start_seconds")),
        "frame_group": anchor.get("group_id"),
        "frame_ids": [frame_id],
        "frame_sha256": [sha],
        "status_effect": "boundary_promoted",
        "evidence": (anchor.get("observation") or "")[:300],
    })
    for field in ANCHOR_FIELDS:
        if field in offset:
            row[field] = offset[field]
    return row


def main():
    offsets = load_json(OFFSETS_PATH)
    ledger = load_json(LEDGER_PATH)
    boundaries = {b["match_detail_id"]: b for b in ledger.get("boundary_reviews", [])}
    frames = {f["frame_id"]: f for f in ledger.get("frames", [])}

    rows = []
    for source_id, source in offsets["sources"].items():
        for offset in source["series"]:
            mid = offset["match_detail_id"]
            if offset.get("status") == "visually_verified":
                rows.append(promoted_row(source_id, offset, frames))
            elif mid in boundaries:
                rows.append(boundary_row(source_id, offset, boundaries[mid]))
            else:
                rows.append(waiver_row(source_id, offset))

    def count(status):
        return sum(1 for row in rows if row["visual_status"] == status)

    output = {
        "schema_version": 1,
        "generated_at": ledger.get("recomputed_at") or ledger.get("generated_at"),
        "description": DESCRIPTION,
        "game_offsets_path": "analysis/evidence/game-offsets.json",
        "game_offsets_sha256": sha256_text_lf(OFFSETS_PATH),
        "ledger_path": "analysis/evidence/deepseek-visual-reviews.json",
        "ledger_sha256": sha256_text_lf(LEDGER_PATH),
        "reviewer": ledger.get("reviewer", "deepseek"),
        "no_human_review": ledger.get("human_review") is not True,
        "summary": {
            "series_total": len(rows),
            "visually_verified": count("visually_verified"),
            "rejected": count("rejected"),
            "context_only": count("context-only"),
            "inconclusive": count("inconclusive"),
            "no_candidate_waiver": count("no_candidate_waiver"),
            "not_reviewed": count("not_reviewed"),
            "frame_reviews": len(ledger.get("frames", [])),
            "boundary_reviews": len(ledger.get("boundary_reviews", [])),
        },
    }
    for key, status in CATEGORY_ARRAYS:
        output[key] = [row for row in rows if row["visual_status"] == status]
    output["series"] = rows

    OUTPUT_PATH.write_bytes((json.dumps(output, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({
        "output": str(OUTPUT_PATH.relative_to(REPO).as_posix()),
        "game_offsets_sha256": output["game_offsets_sha256"],
        "ledger_sha256": output["ledger_sha256"],
        "summary": output["summary"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
