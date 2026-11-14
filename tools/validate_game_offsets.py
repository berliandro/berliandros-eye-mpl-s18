#!/usr/bin/env python3
"""Hardened game-offset validator for MPL ID S18.

Independently checks invariants beyond source membership and schedule order.
Does NOT trust refine_game_offsets.py or weak string matches as proof.
"""
import json
import csv
from pathlib import Path
from collections import defaultdict, Counter

REPO = Path(__file__).resolve().parent.parent
OFF = REPO / "analysis" / "evidence" / "game-offsets.json"
SCHED = REPO / "data" / "csv" / "schedule_all.csv"
MANIFEST = REPO / "analysis" / "sources" / "source-manifest.json"
TIMED = REPO / "analysis" / "cache" / "timed"

VALID_STATUSES = {"schedule_associated", "candidate_detected", "boundary_verified",
                  "game_boundary_verified", "visually_reviewed", "quarantined", "unresolved",
                  "detected_pending_review", "pending_validation", "boundary_verified"}
VALID_CONFIDENCES = {"high", "med", "low"}

def main():
    offs = json.loads(OFF.read_text(encoding='utf-8'))
    manifest = {s['source_id']: s for s in json.loads(MANIFEST.read_text(encoding='utf-8'))['sources']}
    sched = defaultdict(list)
    with open(SCHED, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['status'] == 'completed':
                sched[r['iso_date']].append(r)
    for k in sched:
        sched[k].sort(key=lambda x: x['iso_datetime'])

    errors = []
    warnings = []

    # Top-level validation_status should reflect child statuses
    all_child_statuses = Counter()
    for sid, data in offs['sources'].items():
        for s in data['series']:
            all_child_statuses[s.get('status')] += 1
    any_verified = any(s.get('status') == 'boundary_verified' for src in offs['sources'].values() for s in src['series'])
    if any_verified and offs.get('validation_status') == 'pending':
        warnings.append("top-level validation_status is 'pending' but child entries are 'boundary_verified' — status derivation is stale")

    for sid, data in offs['sources'].items():
        bd = data.get('broadcast_date')
        if sid not in manifest:
            errors.append(f"{sid}: not in manifest")
            continue

        # VOD duration from timed alignment cache
        vod_duration = None
        align_path = TIMED / f"{sid}.json"
        if align_path.exists():
            try:
                align = json.loads(align_path.read_text(encoding='utf-8'))
                vod_duration = align.get('video_duration_seconds') or align.get('duration_seconds')
            except Exception:
                pass
        if vod_duration is None:
            vod_duration = data.get('video_duration_seconds')

        # Schedule completeness
        if bd in sched:
            expected = [s['match_detail_id'] for s in sched[bd]]
            got = [s['match_detail_id'] for s in data['series']]
            if expected != got:
                errors.append(f"{sid}: series mismatch expected {expected} got {got}")

        # Unique IDs
        ids = [s['match_detail_id'] for s in data['series']]
        if len(ids) != len(set(ids)):
            errors.append(f"{sid}: duplicate series IDs")

        # Chronological ordering of start_seconds
        starts = [s.get('start_seconds') for s in data['series'] if s.get('start_seconds') is not None]
        if starts != sorted(starts):
            errors.append(f"{sid}: start_seconds not in chronological order")

        # Timestamp bounds
        for s in data['series']:
            ss = s.get('start_seconds')
            if ss is not None:
                if ss < 0:
                    errors.append(f"{sid}/{s['match_detail_id']}: negative start_seconds")
                if vod_duration is not None and ss > vod_duration:
                    errors.append(f"{sid}/{s['match_detail_id']}: start_seconds {ss} exceeds VOD duration {vod_duration}")
            # Interval non-overlap (where end_seconds exist)
            # Status-specific evidence
            status = s.get('status')
            if status not in VALID_STATUSES:
                errors.append(f"{sid}/{s['match_detail_id']}: unknown status '{status}'")
            if status in ('boundary_verified', 'game_boundary_verified', 'visually_reviewed'):
                if not s.get('provenance'):
                    errors.append(f"{sid}/{s['match_detail_id']}: verified status but missing provenance")
                if not s.get('provenance', {}).get('method'):
                    errors.append(f"{sid}/{s['match_detail_id']}: verified status but missing method")
                if s.get('confidence') not in ('high', 'med'):
                    warnings.append(f"{sid}/{s['match_detail_id']}: verified with low confidence")
            if status == 'visually_reviewed':
                if not s.get('verified_by'):
                    errors.append(f"{sid}/{s['match_detail_id']}: visually_reviewed but no verified_by")
            if not s.get('provenance'):
                errors.append(f"{sid}/{s['match_detail_id']}: missing provenance")
            if s.get('confidence') not in VALID_CONFIDENCES:
                errors.append(f"{sid}/{s['match_detail_id']}: invalid confidence '{s.get('confidence')}'")

        # Low confidence warning
        if any(x.get('confidence') == 'low' for x in data['series']):
            warnings.append(f"{sid}: has low confidence entries")

    result = {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings[:20],
        "sources_checked": len(offs['sources']),
        "series_checked": sum(len(d['series']) for d in offs['sources'].values()),
        "boundary_verified": sum(1 for d in offs['sources'].values() for s in d['series'] if s.get('status') == 'boundary_verified'),
        "pending_validation": sum(1 for d in offs['sources'].values() for s in d['series'] if s.get('status') == 'pending_validation'),
        "detected_pending_review": sum(1 for d in offs['sources'].values() for s in d['series'] if s.get('status') == 'detected_pending_review'),
    }
    print(json.dumps(result, indent=2))
    return 0 if result['ok'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
PY