#!/usr/bin/env python3
"""Safely repair matches.winner orientation and refresh dependent artifacts.

Default mode is read-only preview. Pass --apply to back up the affected files,
repair the database and CSV, refresh the semantic evidence snapshot, regenerate
the dashboard, and run the validation chain. Any failed stage triggers rollback.
Raw transcripts, caches and backups remain local-only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "mpl_id_s18.db"
MATCHES_CSV = ROOT / "data" / "csv" / "matches.csv"
HTML = ROOT / "mpl_id_s18_dark.html"
QUERY_CATALOG = ROOT / "analysis" / "evidence" / "query-catalog.json"
SNAPSHOT_MANIFEST = ROOT / "analysis" / "evidence" / "database-snapshot-manifest.json"
PILOT_LEDGER = ROOT / "analysis" / "evidence" / "pilot-ledger.jsonl"
AUDIT_LOG = ROOT / "analysis" / "evidence" / "audit-log.jsonl"
TIMED_SUMMARY = ROOT / "analysis" / "evidence" / "timed-alignment.json"
CORPUS_REPORT = ROOT / "analysis" / "reports" / "corpus-inventory.md"
DB_REPORT = ROOT / "analysis" / "reports" / "database-inventory.md"
PILOT_REPORT = ROOT / "analysis" / "reports" / "pilot-quality-report.md"
BACKUP_ROOT = ROOT / "analysis" / "cache" / "migration-backups"


class RepairError(RuntimeError):
    """Raised when repair preconditions or validation fail."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def winner_for_score(score_a: object, score_b: object) -> str:
    try:
        a, b = int(score_a), int(score_b)
    except (TypeError, ValueError) as exc:
        raise RepairError(f"non-numeric series score {score_a!r}-{score_b!r}") from exc
    if a == b:
        raise RepairError(f"tied/undecided series score {a}-{b}")
    return "team_a" if a > b else "team_b"


def inspect_database(db_path: Path = DB) -> tuple[list[dict], list[dict]]:
    """Return database rows and required winner changes without modifying anything."""
    con = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        columns = {row[1] for row in con.execute("PRAGMA table_info(matches)")}
        required = {"match_detail_id", "team_a", "team_b", "score_a", "score_b", "winner"}
        if not required.issubset(columns):
            raise RepairError(f"matches table missing columns: {sorted(required-columns)}")
        rows = [dict(r) for r in con.execute(
            "SELECT match_detail_id, team_a, team_b, score_a, score_b, winner FROM matches "
            "ORDER BY CAST(match_detail_id AS INTEGER)"
        )]
    finally:
        con.close()
    if not rows:
        raise RepairError("matches table is empty")
    ids = [str(r["match_detail_id"]) for r in rows]
    if len(ids) != len(set(ids)):
        raise RepairError("matches contains duplicate match_detail_id values")
    updates = []
    for row in rows:
        expected = winner_for_score(row["score_a"], row["score_b"])
        if row["winner"] != expected:
            updates.append({
                "match_detail_id": str(row["match_detail_id"]),
                "team_a": row["team_a"],
                "team_b": row["team_b"],
                "score_a": int(row["score_a"]),
                "score_b": int(row["score_b"]),
                "old_winner": row["winner"],
                "new_winner": expected,
            })
    return rows, updates


def rewrite_matches_csv(csv_path: Path, database_rows: list[dict]) -> tuple[str, int]:
    """Return corrected CSV bytes and update count; reject any DB/CSV scope mismatch."""
    expected = {str(r["match_detail_id"]): r for r in database_rows}
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "match_detail_id" not in reader.fieldnames or "winner" not in reader.fieldnames:
            raise RepairError("matches.csv lacks match_detail_id or winner column")
        rows = list(reader)
        fields = list(reader.fieldnames)
    actual_ids = [str(row.get("match_detail_id") or "") for row in rows]
    if len(actual_ids) != len(set(actual_ids)):
        raise RepairError("matches.csv contains duplicate match_detail_id values")
    if set(actual_ids) != set(expected):
        missing = sorted(set(expected) - set(actual_ids))
        extra = sorted(set(actual_ids) - set(expected))
        raise RepairError(f"database/CSV match IDs differ; missing={missing[:5]}, extra={extra[:5]}")
    updates = 0
    for row in rows:
        mid = str(row["match_detail_id"])
        dbrow = expected[mid]
        for field in ("team_a", "team_b", "score_a", "score_b"):
            if str(row.get(field, "")) != str(dbrow[field]):
                raise RepairError(f"matches.csv vs database mismatch for {mid} field {field}")
        winner = winner_for_score(dbrow["score_a"], dbrow["score_b"])
        if row["winner"] != winner:
            row["winner"] = winner
            updates += 1
    from io import StringIO
    out = StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue(), updates


def db_winner_counts(rows: list[dict]) -> dict:
    return {
        "match_count": len(rows),
        "winner_team_a": sum(r["winner"] == "team_a" for r in rows),
        "winner_team_b": sum(r["winner"] == "team_b" for r in rows),
    }


def run_step(label: str, command: list[str], timeout: int = 900) -> None:
    print(f"\n--- {label}: {' '.join(command)}")
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    output = (result.stdout + "\n" + result.stderr).strip()
    if output:
        print(output[-12000:])
    if result.returncode:
        raise RepairError(f"{label} failed with exit code {result.returncode}")


def backup_files(paths: list[Path]) -> tuple[Path, dict[str, bool]]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = BACKUP_ROOT / f"winner-orientation-{stamp}"
    backup_dir.mkdir(parents=True, exist_ok=False)
    existed: dict[str, bool] = {}
    for path in paths:
        rel = path.relative_to(ROOT)
        existed[str(rel)] = path.exists()
        if path.exists():
            target = backup_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    return backup_dir, existed


def restore_files(backup_dir: Path, existed: dict[str, bool]) -> None:
    for relative, was_present in existed.items():
        target = ROOT / relative
        saved = backup_dir / relative
        if was_present:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(saved, target)
        elif target.exists():
            target.unlink()


def update_catalog_for_snapshot(database_sha: str) -> None:
    catalog = json.loads(QUERY_CATALOG.read_text(encoding="utf-8"))
    catalog["snapshot_sha256"] = database_sha
    catalog["snapshot_id"] = f"mpl-s18-db-{database_sha[:12]}"
    catalog["generated_at"] = now()
    catalog["notes"] = (
        "Queries are read-only and parameterised. schedule_all.winner is expressed in schedule orientation; "
        "matches.winner is expressed relative to matches.team_a/team_b and is validated against the score in "
        "that same row. Do not compare winner side tokens across tables without mapping the named teams."
    )
    QUERY_CATALOG.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def apply_repair(database_rows: list[dict], updates: list[dict]) -> dict:
    if not updates:
        return {"status": "already_correct", "changed_rows": 0}

    paths = [
        DB, MATCHES_CSV, HTML, QUERY_CATALOG, SNAPSHOT_MANIFEST, PILOT_LEDGER,
        AUDIT_LOG, TIMED_SUMMARY, CORPUS_REPORT, DB_REPORT, PILOT_REPORT,
    ]
    backup_dir, existed = backup_files(paths)
    before_sha = sha256_file(DB)
    csv_text, csv_updates = rewrite_matches_csv(MATCHES_CSV, database_rows)
    if csv_updates != len(updates):
        raise RepairError(
            f"database requires {len(updates)} winner corrections but CSV requires {csv_updates}; "
            "refusing to apply a partial/mismatched migration"
        )

    try:
        con = sqlite3.connect(DB, timeout=30)
        try:
            con.execute("BEGIN IMMEDIATE")
            for item in updates:
                con.execute(
                    "UPDATE matches SET winner=? WHERE match_detail_id=?",
                    (item["new_winner"], item["match_detail_id"]),
                )
            wrong = con.execute("""
                SELECT COUNT(*) FROM matches
                WHERE CAST(score_a AS INTEGER)=CAST(score_b AS INTEGER)
                   OR winner <> CASE WHEN CAST(score_a AS INTEGER)>CAST(score_b AS INTEGER)
                                     THEN 'team_a' ELSE 'team_b' END
            """).fetchone()[0]
            if wrong:
                raise RepairError(f"post-update database winner integrity has {wrong} invalid rows")
            integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
            if integrity != "ok":
                raise RepairError(f"SQLite integrity_check returned {integrity!r}")
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

        temp_csv = MATCHES_CSV.with_suffix(".csv.repair-tmp")
        temp_csv.write_text(csv_text, encoding="utf-8", newline="")
        temp_csv.replace(MATCHES_CSV)
        after_sha = sha256_file(DB)
        update_catalog_for_snapshot(after_sha)

        py = sys.executable
        run_step("rebuild evidence ledger", [
            py, str(ROOT / "tools" / "transcript_evidence.py"), "build",
            "--selection", str(ROOT / "analysis" / "pilot" / "selection.json"),
            "--ledger", str(PILOT_LEDGER),
            "--queries", str(QUERY_CATALOG),
            "--db", str(DB),
            "--cache-dir", str(ROOT / "analysis" / "cache" / "timed"),
        ])
        run_step("validate evidence ledger", [
            py, str(ROOT / "tools" / "transcript_evidence.py"), "validate",
            "--ledger", str(PILOT_LEDGER),
            "--schema", str(ROOT / "analysis" / "evidence" / "evidence-schema.json"),
            "--queries", str(QUERY_CATALOG),
            "--db", str(DB),
            "--cache-dir", str(ROOT / "analysis" / "cache" / "timed"),
        ])
        run_step("regenerate dashboard", [py, str(ROOT / "tools" / "gen_dark.py")])
        run_step("regenerate inventories", [py, str(ROOT / "tools" / "analysis_inventory.py")])
        run_step("check semantic sources", [py, str(ROOT / "tools" / "check_analysis.py")])
        run_step("check data integrity", [py, str(ROOT / "tools" / "check.py")])
        run_step("check CSV/HTML parity", [py, str(ROOT / "tools" / "check_parity.py")])
        run_step("full regression suite", [py, str(ROOT / "tools" / "verify.py")])

        after_rows, remaining = inspect_database(DB)
        if remaining:
            raise RepairError(f"winner repair incomplete: {len(remaining)} mismatches remain")
        return {
            "status": "repaired_and_verified",
            "changed_rows": len(updates),
            "matches_csv_rows_changed": csv_updates,
            "database_sha256_before": before_sha,
            "database_sha256_after": after_sha,
            "backup_dir": str(backup_dir.relative_to(ROOT)),
            "database_winner_counts": db_winner_counts(after_rows),
            "updated_at": now(),
        }
    except Exception:
        restore_files(backup_dir, existed)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="perform migration; default is read-only preview")
    args = parser.parse_args(argv)
    try:
        rows, updates = inspect_database()
        print(json.dumps({
            "mode": "apply" if args.apply else "preview",
            "database": str(DB.relative_to(ROOT)),
            "database_sha256": sha256_file(DB),
            "counts": db_winner_counts(rows),
            "mismatch_count": len(updates),
            "mismatches": updates,
            "will_rebuild": [
                "data/csv/matches.csv", "analysis/evidence/query-catalog.json",
                "analysis/evidence/pilot-ledger.jsonl", "analysis/evidence/audit-log.jsonl",
                "analysis/evidence/timed-alignment.json", "mpl_id_s18_dark.html",
                "analysis/evidence/database-snapshot-manifest.json",
                "analysis/reports/corpus-inventory.md", "analysis/reports/database-inventory.md",
            ] if args.apply else [],
        }, indent=2, ensure_ascii=False))
        if not args.apply:
            print("\nRead-only preview. Re-run with --apply to back up, repair, rebuild and validate.")
            return 0
        result = apply_repair(rows, updates)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (RepairError, OSError, sqlite3.Error, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print("No partial migration is intended; restore from the timestamped backup if rollback itself was interrupted.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
