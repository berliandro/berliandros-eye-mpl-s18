#!/usr/bin/env python3
"""Build the canonical evidence-store manifest and reconciliation note.

Resolves the split between the older pilot ledger and the 27-source transcript
observation ledgers. The transcript ledgers are canonical for broadcast
observations; the pilot ledger is frozen as a claim-level pilot store.

Usage:
    python tools/build_canonical_store.py
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
EVIDENCE = REPO / "analysis" / "evidence"
OBSERVATIONS = EVIDENCE / "transcript-observations"
SEGMENTS = EVIDENCE / "transcript-segments"
PILOT = EVIDENCE / "pilot-ledger.jsonl"
VISUAL = EVIDENCE / "deepseek-visual-reviews.json"
DB = REPO / "analysis" / "snapshots" / "mpl_id_s18_regular.db"
OUT_JSON = EVIDENCE / "canonical-store.json"
OUT_MD = REPO / "analysis" / "reports" / "evidence-store.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_hash(paths: list[Path]) -> str:
    rows = [f"{path.name}:{sha256(path)}" for path in sorted(paths)]
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    obs_paths = sorted(OBSERVATIONS.glob("*.jsonl"))
    seg_paths = sorted(SEGMENTS.glob("*.jsonl"))
    obs_rows = [row for path in obs_paths for row in read_jsonl(path)]
    seg_rows = [row for path in seg_paths for row in read_jsonl(path)]
    pilot_rows = read_jsonl(PILOT)

    obs_status = Counter(str(row.get("status")) for row in obs_rows)
    obs_ids = [str(row.get("observation_id")) for row in obs_rows if row.get("record_type") == "observation"]
    variant_ids = [oid for oid in obs_ids if not re.match(r"^TOBS-\d{4}-G\d+-\d+$", oid)]
    variant_accepted = sum(
        1 for row in obs_rows
        if row.get("status") == "accepted" and not re.match(r"^TOBS-\d{4}-G\d+-\d+$", str(row.get("observation_id")))
    )
    pilot_types = Counter(str(row.get("record_type")) for row in pilot_rows)
    pilot_ids = [str(row.get("id")) for row in pilot_rows]

    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "authority": "transcript-observations",
        "summary": {
            "transcript_observation_files": len(obs_paths),
            "transcript_segment_files": len(seg_paths),
            "transcript_rows": len(obs_rows),
            "transcript_statuses": dict(obs_status),
            "transcript_id_variants": len(variant_ids),
            "transcript_id_variants_accepted": variant_accepted,
            "pilot_rows": len(pilot_rows),
            "pilot_record_types": dict(pilot_types),
            "pilot_scope_matches": ["1036", "1037", "1107"],
        },
        "stores": {
            "canonical_database": {
                "path": "analysis/snapshots/mpl_id_s18_regular.db",
                "sha256": sha256(DB),
                "status": "canonical",
                "scope": "72 completed series, 174 games, source-reported scoreboard and schedule data",
            },
            "transcript_observations": {
                "paths": ["analysis/evidence/transcript-observations/"],
                "files": len(obs_paths),
                "rows": len(obs_rows),
                "status_counts": dict(obs_status),
                "manifest_sha256": manifest_hash(obs_paths),
                "status": "canonical",
                "scope": "27 sources; atomic quote-level broadcast observations",
            },
            "transcript_segments": {
                "paths": ["analysis/evidence/transcript-segments/"],
                "files": len(seg_paths),
                "rows": len(seg_rows),
                "manifest_sha256": manifest_hash(seg_paths),
                "status": "canonical",
                "scope": "27 bounded segment ledgers with raw line and cue ranges",
            },
            "pilot_ledger": {
                "path": "analysis/evidence/pilot-ledger.jsonl",
                "rows": len(pilot_rows),
                "record_types": dict(pilot_types),
                "sha256": sha256(PILOT),
                "status": "frozen_legacy",
                "scope": "3 pilot series (1036, 1037, 1107); claim-level observations, insights and audits",
                "superseded_for": "new broadcast observations",
                "still_authoritative_for": [
                    "pilot insight and audit records INS-*, AUD-*",
                    "1037 semantic evidence, which has no transcript source",
                    "the 8 pilot segments and their visual/database references",
                ],
            },
            "visual_reviews": {
                "path": "analysis/evidence/deepseek-visual-reviews.json",
                "sha256": sha256(VISUAL),
                "status": "canonical_for_visual_claims",
                "scope": "DeepSeek-only frame and boundary reviews; 0 visually verified",
            },
        },
        "id_conventions": {
            "canonical_observation": "^TOBS-<match_id>-G<game_no>-<sequence>$",
            "known_variant": "^TOBS-src-s18-w<week>d<day>-<match_id>-g1-<sequence>$",
            "known_variant_count": len(variant_ids),
            "known_variant_ids": sorted(variant_ids),
            "pilot_claim_ids": "^OBS-<match_id>-<label>$",
            "policy": "Do not rename existing IDs. The variant is schema-valid (prefix TOBS-) and is referenced from Markdown; new records must use the canonical form.",
        },
        "reconciliation": {
            "duplicate_record_ids": sorted(set(obs_ids) & set(pilot_ids)),
            "decision": "Staging transcript ledgers are the canonical store for new broadcast observations. The pilot ledger is frozen and remains authoritative only for the 3 pilot analyses and for 1037, which has no transcript source.",
            "alias_policy": "No automatic aliasing: pilot observations are claim-level and transcript observations are quote-level, so a one-to-one alias would be false precision. References stay store-qualified.",
        },
        "rules": [
            "New transcript observations go to analysis/evidence/transcript-observations/ and must pass tools/validate_transcript_ledger.py.",
            "Never append new records to analysis/evidence/pilot-ledger.jsonl.",
            "Cite pilot records as pilot-store records; cite transcript records by TOBS id.",
            "Statistics always come from tools/stats_query.py with query_id and snapshot hash.",
            "Visual claims come only from the DeepSeek visual ledger and require a same-frame literal 00:00.",
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    s = payload["summary"]
    lines = [
        "# Evidence store reconciliation",
        "",
        "**Decision:** the 27-source transcript observation ledgers are the canonical store for broadcast evidence. "
        "The older `analysis/evidence/pilot-ledger.jsonl` is a frozen claim-level pilot store, not a duplicate.",
        "",
        "## Canonical stores",
        "",
        "| Store | Rows | Status | Scope |",
        "|---|---:|---|---|",
        f"| `analysis/snapshots/mpl_id_s18_regular.db` | 174 games | canonical | source-reported regular-season schedule and scoreboard snapshot |",
        f"| `analysis/evidence/transcript-observations/` | {s['transcript_rows']} | canonical | 27 sources; atomic quote-level observations ({s['transcript_statuses'].get('accepted', 0)} accepted) |",
        f"| `analysis/evidence/transcript-segments/` | {len(seg_rows)} | canonical | 27 bounded segment ledgers |",
        f"| `analysis/evidence/pilot-ledger.jsonl` | {s['pilot_rows']} | frozen legacy | 3 pilot series; claim-level observations, insights and audits |",
        f"| `analysis/evidence/deepseek-visual-reviews.json` | see ledger | canonical for visual claims | DeepSeek reviews; 0 visually verified |",
        "",
        "## Why the pilot ledger is not merged",
        "",
        "- Pilot records are claim-level (`OBS-1036-DRAFT`, `INS-*`, `AUD-*`); staging records are quote-level (`TOBS-*`). "
        "A one-to-one alias would be false precision.",
        "- Series 1037 has **no transcript source**. Its pilot observations are the only semantic evidence for that series, "
        "so the store cannot be discarded.",
        "- The pilot ledger also holds the 8 pilot segments and the visual/database references used by the pilot audits.",
        "- No record IDs are shared between the two stores.",
        "",
        "## Rules for future work",
        "",
        "1. New transcript observations go to `analysis/evidence/transcript-observations/` and must pass `tools/validate_transcript_ledger.py`.",
        "2. Never append new records to `pilot-ledger.jsonl`.",
        "3. Cite transcript records by `TOBS-*` id and pilot records as pilot-store records; keep the store qualifier.",
        "4. Statistics always come from `tools/stats_query.py` with `query_id` and snapshot hash.",
        "5. Visual claims come only from the DeepSeek visual ledger and require a same-frame literal `00:00`.",
        "",
        "## Known ID variant",
        "",
        f"- {s['transcript_id_variants']} observation records ({s['transcript_id_variants_accepted']} accepted) from `src-s18-w03d02` use "
        "`TOBS-src-s18-w03d02-1055-g1-<seq>` instead of `TOBS-<match>-G<game>-<seq>`.",
        "- They are schema-valid (`TOBS-` prefix) and referenced from Markdown. Do not rename them; use the canonical form for new records.",
        "",
        "## Evidence",
        "",
        "- Machine-readable manifest: `analysis/evidence/canonical-store.json`",
        "- Coverage matrix: `analysis/reports/coverage-matrix.md`",
        "- Validator: `tools/validate_transcript_ledger.py`",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "transcript_rows": len(obs_rows),
        "transcript_statuses": dict(obs_status),
        "pilot_rows": len(pilot_rows),
        "pilot_types": dict(pilot_types),
        "id_variants": len(variant_ids),
        "duplicate_ids": payload["reconciliation"]["duplicate_record_ids"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
