#!/usr/bin/env python3
"""Validate the DeepSeek visual-review ledger.

Checks the review contract, screenshot hashes, historical frame coverage,
boundary decisions, and the no-human-review rule. In local mode it verifies
that each referenced frame still hashes to the recorded SHA-256. In CI mode the
git-ignored media cache may be absent; missing local files are warnings, while
all ledger-internal checks still run.

Usage:
    python tools/validate_visual_reviews.py [--repo-root PATH] [--ci]
Exit code: 0 if valid, 1 otherwise.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "analysis" / "evidence" / "deepseek-visual-reviews.json"
SMOKE = REPO / "analysis" / "evidence" / "deepseek-vision-smoke-opencode-go.json"
PLAN = REPO / "analysis" / "evidence" / "visual-review-plan.json"
VISUAL = REPO / "analysis" / "evidence" / "visual-review.json"
OFFSETS = REPO / "analysis" / "evidence" / "game-offsets.json"

DISPOSITIONS = {"used", "rejected", "context-only", "inconclusive"}
CONFIDENCES = {"high", "med", "low"}
EFFECTS = {"no_change", "candidate_rejected", "partial_context_only", "visual_confirmation"}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
ALLOWED_PROVIDERS = {"deepseek", "opencode", "opencode-go"}
NEGATIVE_REVIEWER = ("human", "manual", "opencode multimodal", "operator")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text_lf(path: Path) -> str:
    """Hash a committed text artifact with LF endings so every checkout agrees."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def is_hex64(value) -> bool:
    return isinstance(value, str) and bool(HEX64.match(value))


def is_iso(value) -> bool:
    return isinstance(value, str) and bool(ISO.match(value))


def check_record(record: dict, *, frame_root: Path | None = None) -> list[str]:
    """Validate one frame record. Pure enough for adversarial tests."""
    errors = []
    fid = record.get("frame_id", "<missing>")
    if not record.get("frame_id"):
        errors.append("frame record missing frame_id")
    if record.get("review_status") != "reviewed":
        errors.append(f"{fid}: review_status is not 'reviewed'")
    if record.get("reviewer") != "deepseek":
        errors.append(f"{fid}: reviewer is not 'deepseek'")
    if str(record.get("model", "")).lower().find("deepseek") < 0:
        errors.append(f"{fid}: model is not a DeepSeek model")
    if record.get("provider") not in ALLOWED_PROVIDERS:
        errors.append(f"{fid}: unexpected provider {record.get('provider')!r}")
    if not is_iso(record.get("reviewed_at")):
        errors.append(f"{fid}: reviewed_at is not ISO-8601")
    if not is_hex64(record.get("screenshot_sha256")):
        errors.append(f"{fid}: screenshot_sha256 is not a 64-char lowercase hex digest")
    if not record.get("api_request_id"):
        errors.append(f"{fid}: missing api_request_id (no API pixel-inspection evidence)")
    if record.get("disposition") not in DISPOSITIONS:
        errors.append(f"{fid}: invalid disposition {record.get('disposition')!r}")
    if record.get("confidence") not in CONFIDENCES:
        errors.append(f"{fid}: invalid confidence {record.get('confidence')!r}")
    if len(str(record.get("observation", "")).strip()) < 10:
        errors.append(f"{fid}: observation is empty or too short")
    if "limitations" not in record:
        errors.append(f"{fid}: missing limitations field")
    if record.get("capture_status") == "failed" and record.get("disposition") != "rejected":
        errors.append(f"{fid}: failed capture must be disposition=rejected")
    if record.get("capture_status") == "failed" and not record.get("limitations"):
        errors.append(f"{fid}: failed capture must record a limitation")
    if record.get("derived_from_path"):
        if not is_hex64(record.get("derived_from_sha256")):
            errors.append(f"{fid}: derived frame missing derived_from_sha256")
        if not record.get("crop_box"):
            errors.append(f"{fid}: derived frame missing crop_box")
    if frame_root is not None:
        frame_rel = record.get("path")
        if frame_rel:
            frame_path = frame_root / frame_rel
            if frame_path.exists():
                actual = sha256_file(frame_path)
                if actual != record.get("screenshot_sha256"):
                    errors.append(f"{fid}: local screenshot hash mismatch")
                if record.get("derived_from_path"):
                    src = frame_root / record["derived_from_path"]
                    if src.exists() and sha256_file(src) != record.get("derived_from_sha256"):
                        errors.append(f"{fid}: derived_from_sha256 mismatch")
            else:
                errors.append(f"{fid}: local frame missing (strict mode)")
    return errors


def check_smoke(smoke: dict, *, frame_root: Path | None = None) -> list[str]:
    errors = []
    if smoke.get("status") != "passed":
        errors.append("smoke_test: status is not 'passed'")
    if smoke.get("reviewer") != "deepseek":
        errors.append("smoke_test: reviewer is not 'deepseek'")
    if "deepseek" not in str(smoke.get("model", "")).lower():
        errors.append("smoke_test: model is not DeepSeek")
    checks = smoke.get("checks") or {}
    required = {"text_deepseek_vision", "text_smoke_test_4729", "shape_orange", "shape_bottom_right"}
    for key in required:
        if checks.get(key) is not True:
            errors.append(f"smoke_test: check {key} did not pass")
    if not is_hex64(smoke.get("image_sha256")):
        errors.append("smoke_test: invalid image hash")
    if not smoke.get("api_request_id"):
        errors.append("smoke_test: missing api_request_id")
    if frame_root is not None and smoke.get("image_path"):
        p = frame_root / smoke["image_path"]
        if p.exists() and sha256_file(p) != smoke.get("image_sha256"):
            errors.append("smoke_test: local image hash mismatch")
    return errors


def check_historical_coverage(ledger: dict, visual: dict) -> list[str]:
    errors = []
    by_history = {f.get("historical_frame_id"): f for f in ledger.get("frames", [])
                  if f.get("historical_frame_id")}
    for frame in visual.get("frames", []):
        fid = frame.get("frame_id")
        hist_status = frame.get("review_status")
        disposition = frame.get("disposition")
        needs_review = (
            hist_status == "reviewed" or
            frame.get("capture_status") == "failed" or
            disposition in {"used", "used-as-context-only", "rejected", "not-used"}
        )
        if not needs_review:
            continue
        rec = by_history.get(fid)
        if not rec:
            errors.append(f"historical frame {fid}: no DeepSeek review record")
            continue
        if rec.get("review_status") != "reviewed":
            errors.append(f"historical frame {fid}: DeepSeek record not reviewed")
        expected = frame.get("output_sha256")
        if expected and rec.get("screenshot_sha256") != expected:
            errors.append(f"historical frame {fid}: screenshot hash does not match visual-review.json")
        if frame.get("capture_status") == "failed" and rec.get("disposition") != "rejected":
            errors.append(f"historical frame {fid}: failed capture not rejected by DeepSeek")
    return errors


def check_boundaries(ledger: dict, offsets: dict) -> tuple[list[str], list[str]]:
    errors = []
    warnings = []
    series_by_id = {}
    for sid, source in offsets.get("sources", {}).items():
        for series in source.get("series", []):
            series_by_id[series["match_detail_id"]] = (sid, series)
    frame_by_id = {f["frame_id"]: f for f in ledger.get("frames", [])}
    for boundary in ledger.get("boundary_reviews", []):
        bid = boundary.get("boundary_id")
        sid, series = series_by_id.get(boundary.get("match_detail_id"), (None, None))
        if series is None:
            errors.append(f"{bid}: unknown match_detail_id")
            continue
        if boundary.get("source_id") != sid:
            errors.append(f"{bid}: source_id mismatch")
        if boundary.get("team_a") != series.get("team_a") or boundary.get("team_b") != series.get("team_b"):
            errors.append(f"{bid}: team pairing mismatch")
        if boundary.get("candidate_start_seconds") != series.get("start_seconds"):
            errors.append(f"{bid}: candidate_start_seconds does not match game-offsets.json")
        if boundary.get("disposition") not in DISPOSITIONS:
            errors.append(f"{bid}: invalid disposition")
        if boundary.get("status_effect") not in EFFECTS:
            errors.append(f"{bid}: invalid status_effect")
        for key in ("series_pairing", "game1_start"):
            sub = boundary.get(key) or {}
            if sub.get("disposition") not in DISPOSITIONS:
                errors.append(f"{bid}: invalid {key}.disposition")
            if not sub.get("evidence"):
                errors.append(f"{bid}: missing {key}.evidence")
        for fid in boundary.get("frame_ids", []):
            if fid not in frame_by_id:
                errors.append(f"{bid}: frame_id {fid} not in ledger")
            elif frame_by_id[fid].get("screenshot_sha256") not in boundary.get("frame_sha256", []):
                errors.append(f"{bid}: frame hash for {fid} not listed")
        for fid in boundary.get("related_frame_ids", []):
            if fid not in frame_by_id:
                errors.append(f"{bid}: related frame {fid} not in ledger")
        if boundary.get("disposition") == "used":
            if boundary.get("series_pairing", {}).get("disposition") != "used":
                errors.append(f"{bid}: used boundary without used series pairing")
            if boundary.get("game1_start", {}).get("disposition") != "used":
                errors.append(f"{bid}: used boundary without used game-1 start")
        if boundary.get("status_effect") == "candidate_rejected" and series.get("status") in {
            "boundary_verified", "game_boundary_verified", "visually_verified", "visually_reviewed"
        }:
            errors.append(f"{bid}: visual review rejects a candidate that game-offsets marks verified")
        if boundary.get("disposition") == "context-only" and series.get("status") in {
            "boundary_verified", "game_boundary_verified"
        }:
            warnings.append(f"{bid}: transcript-verified offset only partially confirmed visually")
        if series.get("status") in {"visually_verified", "visually_reviewed", "game_boundary_verified"}:
            if boundary.get("disposition") != "used" or boundary.get("game1_start", {}).get("disposition") != "used":
                errors.append(f"{bid}: visually verified boundary lacks a used DeepSeek game-1 record")
    return errors, warnings


def check_plan_coverage(ledger: dict, plan: dict) -> list[str]:
    errors = []
    ledger_ids = {f.get("frame_id") for f in ledger.get("frames", [])}
    plan_ids = {f.get("frame_id") for g in plan.get("groups", []) for f in g.get("frames", [])}
    missing = plan_ids - ledger_ids
    extra = ledger_ids - plan_ids
    if missing:
        errors.append(f"plan frames missing from ledger: {sorted(missing)}")
    if extra:
        errors.append(f"ledger frames not in plan: {sorted(extra)}")
    by_group: dict[str, list[dict]] = {}
    for frame in ledger.get("frames", []):
        by_group.setdefault(frame.get("group_id", ""), []).append(frame)
    for group in plan.get("groups", []):
        recs = by_group.get(group["group_id"], [])
        if len(recs) != len(group.get("frames", [])):
            errors.append(f"{group['group_id']}: frame count mismatch")
        for frame, rec in zip(group.get("frames", []), recs):
            if frame.get("path") and rec.get("path") and frame["path"] != rec["path"]:
                errors.append(f"{group['group_id']}: plan/ledger path mismatch for {frame.get('frame_id')}")
    boundary_groups = {b.get("frame_group") for b in plan.get("boundary_claims", [])}
    for gid in boundary_groups:
        if gid not in by_group:
            errors.append(f"boundary references missing group {gid}")
    return errors


def check_summary(ledger: dict) -> list[str]:
    errors = []
    frames = ledger.get("frames", [])
    boundaries = ledger.get("boundary_reviews", [])
    summary = ledger.get("summary", {})
    if summary.get("frames_reviewed") != len(frames):
        errors.append("summary.frames_reviewed mismatch")
    if summary.get("boundary_reviews") != len(boundaries):
        errors.append("summary.boundary_reviews mismatch")
    counts = {d: 0 for d in DISPOSITIONS}
    for frame in frames:
        counts[frame.get("disposition")] = counts.get(frame.get("disposition"), 0) + 1
    if summary.get("frame_dispositions") != counts:
        errors.append("summary.frame_dispositions mismatch")
    bcounts = {d: 0 for d in DISPOSITIONS}
    for boundary in boundaries:
        bcounts[boundary.get("disposition")] = bcounts.get(boundary.get("disposition"), 0) + 1
    if summary.get("boundary_dispositions") != bcounts:
        errors.append("summary.boundary_dispositions mismatch")
    if summary.get("candidate_rejections") != sum(
            1 for b in boundaries if b.get("status_effect") == "candidate_rejected"):
        errors.append("summary.candidate_rejections mismatch")
    if summary.get("visual_confirmations") != sum(
            1 for b in boundaries if b.get("status_effect") == "visual_confirmation"):
        errors.append("summary.visual_confirmations mismatch")
    return errors


def validate_ledger(ledger: dict, visual: dict, offsets: dict, plan: dict,
                    *, frame_root: Path | None = None) -> tuple[list[str], list[str]]:
    errors = []
    warnings = []
    if ledger.get("reviewer") != "deepseek":
        errors.append("ledger reviewer is not 'deepseek'")
    if ledger.get("review_mode") != "api-pixel-inspection-only":
        errors.append("ledger review_mode is not api-pixel-inspection-only")
    if ledger.get("human_review") is not False:
        errors.append("ledger human_review must be false")
    if not str(ledger.get("model", "")).lower().startswith("deepseek"):
        errors.append("ledger model is not DeepSeek")
    if ledger.get("provider") not in ALLOWED_PROVIDERS:
        errors.append("ledger provider is not an allowed DeepSeek transport")
    if not is_iso(ledger.get("generated_at")):
        errors.append("ledger generated_at is not ISO-8601")
    for frame in ledger.get("frames", []):
        errors.extend(check_record(frame, frame_root=frame_root))
    errors.extend(check_smoke(ledger.get("smoke_test", {}), frame_root=frame_root))
    errors.extend(check_historical_coverage(ledger, visual))
    boundary_errors, boundary_warnings = check_boundaries(ledger, offsets)
    errors.extend(boundary_errors)
    warnings.extend(boundary_warnings)
    errors.extend(check_plan_coverage(ledger, plan))
    errors.extend(check_summary(ledger))
    # No human/manual reviewer labels anywhere in the review records.
    for frame in ledger.get("frames", []):
        reviewer = str(frame.get("reviewer", "")).lower()
        if any(term in reviewer for term in NEGATIVE_REVIEWER):
            errors.append(f"frame {frame.get('frame_id')}: human/manual reviewer label")
    for boundary in ledger.get("boundary_reviews", []):
        for key in ("reviewer", "approved_by", "human_reviewer"):
            value = str(boundary.get(key, "")).lower()
            if value and any(term in value for term in NEGATIVE_REVIEWER):
                errors.append(f"boundary {boundary.get('boundary_id')}: human/manual label")
    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO))
    parser.add_argument("--ci", action="store_true", help="allow missing git-ignored local frames")
    parser.add_argument("--ledger", default=None)
    parser.add_argument("--visual", default=None)
    parser.add_argument("--offsets", default=None)
    parser.add_argument("--plan", default=None)
    parser.add_argument("--smoke", default=None)
    args = parser.parse_args(argv)

    root = Path(args.repo_root)
    ledger_path = Path(args.ledger) if args.ledger else root / "analysis" / "evidence" / "deepseek-visual-reviews.json"
    visual_path = Path(args.visual) if args.visual else root / "analysis" / "evidence" / "visual-review.json"
    offsets_path = Path(args.offsets) if args.offsets else root / "analysis" / "evidence" / "game-offsets.json"
    plan_path = Path(args.plan) if args.plan else root / "analysis" / "evidence" / "visual-review-plan.json"
    smoke_path = Path(args.smoke) if args.smoke else root / "analysis" / "evidence" / "deepseek-vision-smoke-opencode-go.json"

    errors = []
    warnings = []
    for label, path in (("ledger", ledger_path), ("visual-review", visual_path),
                        ("game-offsets", offsets_path), ("plan", plan_path), ("smoke", smoke_path)):
        if not path.exists():
            errors.append(f"missing {label}: {path}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1
    ledger = load_json(ledger_path)
    visual = load_json(visual_path)
    offsets = load_json(offsets_path)
    plan = load_json(plan_path)
    smoke = load_json(smoke_path)
    # The ledger embeds its smoke record; the standalone file is the reproducible source.
    if ledger.get("smoke_test", {}).get("image_sha256") != smoke.get("image_sha256"):
        errors.append("ledger smoke_test does not match the standalone smoke record")
    if ledger.get("plan_sha256") and ledger.get("plan_sha256") != sha256_text_lf(plan_path):
        errors.append("ledger plan_sha256 does not match the current visual-review-plan.json")
    if smoke.get("model") not in (ledger.get("models_used") or []):
        errors.append("smoke-test model is not listed in ledger.models_used")
    frame_root = None if args.ci else root
    e, w = validate_ledger(ledger, visual, offsets, plan, frame_root=frame_root)
    errors.extend(e)
    warnings.extend(w)

    print("=== DeepSeek Visual Review Validation ===")
    print(f"frames: {len(ledger.get('frames', []))}")
    print(f"boundaries: {len(ledger.get('boundary_reviews', []))}")
    print(f"errors: {len(errors)}")
    print(f"warnings: {len(warnings)}")
    for warning in warnings[:20]:
        print(f"  WARN: {warning}")
    for error in errors:
        print(f"  ERROR: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
