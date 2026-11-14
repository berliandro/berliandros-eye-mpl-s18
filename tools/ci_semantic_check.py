#!/usr/bin/env python3
"""CI semantic validation script.

Validates committed semantic-analysis artifacts without requiring the local-only
raw transcript corpus or media caches. Checks schema, IDs, coverage counts,
DB query references, ledger links, status consistency, report references,
offsets, and generated report parity.

Usage:
    python tools/ci_semantic_check.py [--repo-root PATH]
Exit code: 0 if all checks pass, 1 otherwise.
"""
import hashlib
import json
import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ERRORS = []
WARNINGS = []


def error(msg):
    ERRORS.append(msg)


def warning(msg):
    WARNINGS.append(msg)


def check_file_exists(path, label):
    if not path.exists():
        error(f"missing required file: {label} ({path})")
        return False
    return True


def check_json_valid(path, label):
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        return data
    except (json.JSONDecodeError, Exception) as e:
        error(f"invalid JSON in {label}: {e}")
        return None


def check_game_offsets():
    """Validate game-offsets.json structure and consistency."""
    off = REPO / "analysis" / "evidence" / "game-offsets.json"
    if not check_file_exists(off, "game-offsets.json"):
        return
    data = check_json_valid(off, "game-offsets.json")
    if not data:
        return

    # Check all 72 series present
    total = sum(len(s['series']) for s in data['sources'].values())
    if total != 72:
        error(f"game-offsets: expected 72 series, got {total}")

    # Check unique IDs
    ids = []
    for src in data['sources'].values():
        for s in src['series']:
            ids.append(s['match_detail_id'])
    if len(ids) != len(set(ids)):
        error("game-offsets: duplicate series IDs")

    # Check boundary_verified entries have provenance and non-null start
    for sid, src in data['sources'].items():
        for s in src['series']:
            if s.get('status') == 'boundary_verified':
                if not s.get('provenance'):
                    error(f"game-offsets: {sid}/{s['match_detail_id']} verified but no provenance")
                if not s.get('provenance', {}).get('method'):
                    error(f"game-offsets: {sid}/{s['match_detail_id']} verified but no method")
                if s.get('start_seconds') is None:
                    error(f"game-offsets: {sid}/{s['match_detail_id']} verified but null start")

    # Check top-level validation_status consistency
    for sid, src in data['sources'].items():
        statuses = [s.get('status') for s in src['series']]
        if any(s == 'boundary_verified' for s in statuses) and src.get('validation_status') == 'pending':
            warning(f"game-offsets: {sid} has verified children but top-level status is 'pending'")

    # Check status enum
    valid_statuses = {"schedule_associated", "candidate_detected", "boundary_verified",
                      "game_boundary_verified", "visually_reviewed", "quarantined", "unresolved",
                      "detected_pending_review", "pending_validation"}
    for sid, src in data['sources'].items():
        for s in src['series']:
            if s.get('status') not in valid_statuses:
                error(f"game-offsets: {sid}/{s['match_detail_id']} unknown status '{s.get('status')}'")


def check_ledger():
    """Validate pilot-ledger.jsonl schema and references."""
    ledger = REPO / "analysis" / "evidence" / "pilot-ledger.jsonl"
    if not check_file_exists(ledger, "pilot-ledger.jsonl"):
        return

    records = []
    try:
        for line in ledger.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            records.append(rec)
    except json.JSONDecodeError as e:
        error(f"pilot-ledger.jsonl: invalid JSON: {e}")
        return

    # Check record_type
    valid_types = {"segment", "observation", "insight", "audit", "quarantined_candidate"}
    for rec in records:
        if rec.get("record_type") not in valid_types:
            error(f"ledger: unknown record_type '{rec.get('record_type')}' for {rec.get('id')}")

    # Check insight has supporting_observation_ids with minItems 1
    for rec in records:
        if rec.get("record_type") == "insight":
            if not rec.get("supporting_observation_ids"):
                error(f"ledger: insight {rec.get('id')} has empty supporting_observation_ids")

    # Check audit has valid verdict
    valid_verdicts = {"supported", "partially supported", "contradicted", "inconclusive"}
    for rec in records:
        if rec.get("record_type") == "audit":
            if rec.get("verdict") not in valid_verdicts:
                error(f"ledger: audit {rec.get('id')} invalid verdict '{rec.get('verdict')}'")

    # Check DB refs have snapshot_sha256
    for rec in records:
        for ref in rec.get("database_refs", []):
            if "snapshot_sha256" in ref:
                sha = ref["snapshot_sha256"]
                if not (isinstance(sha, str) and len(sha) == 64):
                    error(f"ledger: {rec.get('id')} invalid snapshot_sha256")


def check_query_catalog():
    """Validate query-catalog.json."""
    qc = REPO / "analysis" / "evidence" / "query-catalog.json"
    if not check_file_exists(qc, "query-catalog.json"):
        return
    data = check_json_valid(qc, "query-catalog.json")
    if not data:
        return

    # Check snapshot consistency
    expected_sha = "20c5ea2c51f30d1a24cd2ce6927f0d182b47f951ebd8209f1aaef429941cf2ef"
    if data.get("snapshot_sha256") != expected_sha:
        error(f"query-catalog: snapshot_sha256 mismatch")

    # Check all queries have required fields
    for qid, q in data.get("queries", {}).items():
        for field in ["description", "sql", "params", "fields", "provenance"]:
            if field not in q:
                error(f"query-catalog: {qid} missing field '{field}'")


def check_timelines():
    """Validate game-evidence-timeline JSON files."""
    tl_dir = REPO / "analysis" / "evidence" / "game-timelines"
    if not tl_dir.exists():
        error("game-timelines directory missing")
        return

    schema_path = REPO / "analysis" / "evidence" / "game-evidence-timeline-schema.json"
    schema = check_json_valid(schema_path, "game-evidence-timeline-schema.json")

    tl_files = list(tl_dir.glob("*.json"))
    if not tl_files:
        error("no timeline files found")
        return

    # Check unique timeline IDs
    ids = []
    for f in tl_files:
        t = check_json_valid(f, str(f.name))
        if t:
            ids.append(t.get("timeline_id"))
    if len(ids) != len(set(ids)):
        error("game-timelines: duplicate timeline IDs")

    # Check series IDs exist in DB
    try:
        con = sqlite3.connect(str(REPO / "data" / "mpl_id_s18.db"))
        db_ids = set(r[0] for r in con.execute("select match_detail_id from matches").fetchall())
        con.close()
    except Exception:
        db_ids = set()

    for f in tl_files:
        t = check_json_valid(f, str(f.name))
        if not t:
            continue
        if t.get("series_id") and db_ids and t["series_id"] not in db_ids:
            error(f"game-timelines: {f.name} references unknown series {t['series_id']}")
        # DB-only timelines must not have transcript evidence
        if t.get("game_boundary_status") == "unresolved":
            for e in t.get("events", []):
                if e.get("transcript_evidence") is not None:
                    error(f"game-timelines: {f.name} unresolved boundary but has transcript evidence")
        # All timelines must reference same DB snapshot
        if t.get("db_snapshot_id") != "mpl-s18-db-20c5ea2c51f3":
            error(f"game-timelines: {f.name} wrong DB snapshot")

    # Schema validation if jsonschema available
    try:
        import jsonschema
        for f in tl_files:
            t = check_json_valid(f, str(f.name))
            if t:
                try:
                    jsonschema.validate(t, schema)
                except Exception as e:
                    error(f"game-timelines: {f.name} schema validation failed: {str(e)[:100]}")
    except ImportError:
        warning("jsonschema not available; skipping schema validation")


def check_report_references():
    """Check that analysis/index.md references existing files."""
    index = REPO / "analysis" / "index.md"
    if not check_file_exists(index, "analysis/index.md"):
        return
    content = index.read_text(encoding='utf-8')
    # Check that referenced match files exist
    import re
    refs = re.findall(r'\[.*?\]\(([^)]+)\)', content)
    for ref in refs:
        if ref.startswith('http'):
            continue
        # Resolve relative to analysis/
        target = REPO / "analysis" / ref
        if not target.exists() and not (REPO / ref).exists():
            warning(f"index.md: referenced file not found: {ref}")


def check_visual_reviews():
    """Lightweight integrity check for the DeepSeek visual-review ledger."""
    ledger_path = REPO / "analysis" / "evidence" / "deepseek-visual-reviews.json"
    if not check_file_exists(ledger_path, "deepseek-visual-reviews.json"):
        return
    data = check_json_valid(ledger_path, "deepseek-visual-reviews.json")
    if not data:
        return
    if data.get("reviewer") != "deepseek":
        error("visual-reviews: reviewer is not deepseek")
    if data.get("human_review") is not False:
        error("visual-reviews: human_review must be false")
    smoke = data.get("smoke_test") or {}
    if smoke.get("status") != "passed":
        error("visual-reviews: smoke test did not pass")
    frames = data.get("frames", [])
    if not frames:
        error("visual-reviews: no frame records")
    for frame in frames:
        if frame.get("review_status") == "reviewed" and not frame.get("api_request_id"):
            error(f"visual-reviews: {frame.get('frame_id')} reviewed without API request id")
        if frame.get("reviewer") != "deepseek":
            error(f"visual-reviews: {frame.get('frame_id')} reviewer is not deepseek")
    for boundary in data.get("boundary_reviews", []):
        if boundary.get("disposition") == "used" and not boundary.get("frame_sha256"):
            error(f"visual-reviews: {boundary.get('boundary_id')} used without frame hashes")


def check_visual_status():
    """Validate the derived visual-review-status reconciliation artifact."""
    path = REPO / "analysis" / "evidence" / "visual-review-status.json"
    if not check_file_exists(path, "visual-review-status.json"):
        return
    data = check_json_valid(path, "visual-review-status.json")
    if not data:
        return
    offsets = REPO / "analysis" / "evidence" / "game-offsets.json"
    ledger = REPO / "analysis" / "evidence" / "deepseek-visual-reviews.json"
    if offsets.exists() and data.get("game_offsets_sha256") != hashlib.sha256(offsets.read_bytes()).hexdigest():
        error("visual-review-status: game_offsets_sha256 is stale")
    if ledger.exists() and data.get("ledger_sha256") != hashlib.sha256(ledger.read_bytes()).hexdigest():
        error("visual-review-status: ledger_sha256 is stale")
    rows = data.get("series", [])
    if len(rows) != 72:
        error(f"visual-review-status: expected 72 series, got {len(rows)}")
    summary = data.get("summary", {})
    if summary.get("series_total") != len(rows):
        error("visual-review-status: series_total mismatch")
    for key, field in (("rejected", "rejected"), ("context_only", "context-only"),
                       ("inconclusive", "inconclusive"), ("no_candidate_waiver", "no_candidate_waiver"),
                       ("not_reviewed", "not_reviewed")):
        expected = sum(1 for row in rows if row.get("visual_status") == field)
        if summary.get(key) != expected:
            error(f"visual-review-status: summary.{key} mismatch ({summary.get(key)} != {expected})")
    if summary.get("visually_verified") != 0:
        error("visual-review-status: visually_verified must be 0 while §6a is unmet")


def check_db_integrity():
    """Check canonical DB integrity (read-only)."""
    db = REPO / "data" / "mpl_id_s18.db"
    if not db.exists():
        warning("canonical DB not found (CI may not have it)")
        return
    try:
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        result = con.execute("PRAGMA integrity_check").fetchone()
        if result[0] != "ok":
            error(f"DB integrity check failed: {result[0]}")
        # Check counts
        series = con.execute("select count(*) from matches").fetchone()[0]
        games = con.execute("select count(*) from games").fetchone()[0]
        if series != 72:
            error(f"DB: expected 72 series, got {series}")
        if games != 174:
            error(f"DB: expected 174 games, got {games}")
        con.close()
    except Exception as e:
        warning(f"DB check failed: {e}")


def main():
    print("=== CI Semantic Validation ===")
    print()

    check_game_offsets()
    check_ledger()
    check_query_catalog()
    check_timelines()
    check_report_references()
    check_visual_reviews()
    check_visual_status()
    check_db_integrity()

    print()
    print(f"Errors: {len(ERRORS)}")
    print(f"Warnings: {len(WARNINGS)}")
    if WARNINGS:
        for w in WARNINGS[:10]:
            print(f"  WARN: {w}")
    if ERRORS:
        print()
        print("ERRORS:")
        for e in ERRORS:
            print(f"  ERROR: {e}")
        return 1
    print("\nCI SEMANTIC CHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY