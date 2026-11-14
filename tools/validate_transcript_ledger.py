#!/usr/bin/env python3
"""Validate a transcript observation ledger against the staging schema.

Checks schema shape, quote hashes, quote/line/cue provenance, duplicate keys,
statistic database references, proposals, unresolved records, and run counts.

Examples:
    python tools/validate_transcript_ledger.py \
      --ledger analysis/evidence/transcript-observations/src-s18-w01d01.jsonl \
      --segments analysis/evidence/transcript-segments/src-s18-w01d01.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jsonschema

REPO = Path(__file__).resolve().parent.parent
DEFAULT_SCHEMA = REPO / "analysis" / "evidence" / "transcript-observation-schema.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class Issue:
    level: str
    code: str
    message: str
    record_id: str | None = None
    line_no: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "record_id": self.record_id,
            "line_no": self.line_no,
        }


def _read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[Issue]]:
    records: list[dict[str, Any]] = []
    issues: list[Issue] = []
    if not path.is_file():
        return [], [Issue("error", "file-missing", f"file not found: {path}")]
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            issues.append(Issue("error", "json-invalid", f"invalid JSON: {exc}", line_no=line_no))
            continue
        if not isinstance(obj, dict):
            issues.append(Issue("error", "json-not-object", "record is not a JSON object", line_no=line_no))
            continue
        records.append(obj)
    return records, issues


def _record_id(record: dict[str, Any]) -> str | None:
    for key in ("observation_id", "proposal_id", "unresolved_id", "run_id"):
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _norm_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _get_segments(path: Path | None) -> tuple[dict[str, dict[str, Any]], list[Issue]]:
    if path is None:
        return {}, []
    records, issues = _read_jsonl(path)
    segments: dict[str, dict[str, Any]] = {}
    for record in records:
        segment_id = record.get("segment_id")
        if not isinstance(segment_id, str) or not segment_id:
            issues.append(Issue("error", "segment-id-missing", "segment record has no segment_id"))
            continue
        if segment_id in segments:
            issues.append(Issue("error", "segment-duplicate", f"duplicate segment_id {segment_id}", segment_id))
        segments[segment_id] = record
    return segments, issues


def validate_records(
    records: Iterable[dict[str, Any]],
    *,
    segments: dict[str, dict[str, Any]] | None = None,
    schema: dict[str, Any] | None = None,
) -> list[Issue]:
    segments = segments or {}
    issues: list[Issue] = []
    validator = jsonschema.Draft202012Validator(schema) if schema else None

    records = list(records)
    seen_ids: dict[str, str] = {}
    by_type: dict[str, list[dict[str, Any]]] = {
        "observation": [],
        "proposal": [],
        "unresolved": [],
        "run": [],
    }
    observation_ids: set[str] = set()

    for record in records:
        record_type = record.get("record_type")
        rid = _record_id(record)
        if record_type in by_type:
            by_type[record_type].append(record)
        if rid:
            if rid in seen_ids:
                issues.append(Issue("error", "id-duplicate", f"duplicate record id {rid}", rid))
            seen_ids[rid] = str(record_type)
        if record_type == "observation" and record.get("observation_id"):
            observation_ids.add(str(record["observation_id"]))

        if validator:
            for error in validator.iter_errors(record):
                path = "/".join(str(part) for part in error.absolute_path) or "<root>"
                issues.append(
                    Issue(
                        "error",
                        "schema",
                        f"{path}: {error.message}",
                        rid,
                    )
                )

    dup_keys: dict[tuple[str, str, str, str, str], str] = {}
    for obs in by_type["observation"]:
        rid = str(obs.get("observation_id", "<unknown>"))
        quote = obs.get("quote")
        if isinstance(quote, str):
            expected = _sha256(quote)
            if obs.get("quote_sha256") != expected:
                issues.append(Issue("error", "quote-hash", "quote_sha256 does not match quote", rid))
        else:
            issues.append(Issue("error", "quote-missing", "observation has no quote", rid))

        start = obs.get("raw_line_start")
        end = obs.get("raw_line_end")
        if isinstance(start, int) and isinstance(end, int) and end < start:
            issues.append(Issue("error", "line-range", "raw_line_end is before raw_line_start", rid))

        cue_start = obs.get("cue_start")
        cue_end = obs.get("cue_end")
        if isinstance(cue_start, (int, float)) and isinstance(cue_end, (int, float)) and cue_end < cue_start:
            issues.append(Issue("error", "cue-range", "cue_end is before cue_start", rid))

        provenance = obs.get("timestamp_provenance")
        if provenance == "none":
            if cue_start is not None or cue_end is not None or obs.get("timestamp_link") is not None:
                issues.append(Issue("error", "timestamp-none", "timestamp_provenance=none requires null cue/link fields", rid))
        elif provenance == "youtube-auto-caption-alignment-v1":
            if cue_start is None or cue_end is None:
                issues.append(Issue("error", "timestamp-missing", "aligned observation needs cue_start and cue_end", rid))
            if not obs.get("timestamp_link"):
                issues.append(Issue("error", "timestamp-link", "aligned observation needs timestamp_link", rid))

        if obs.get("speaker_basis") == "unavailable" and obs.get("speaker") is not None:
            issues.append(Issue("warning", "speaker-mismatch", "speaker is set while speaker_basis=unavailable", rid))

        if obs.get("claim_type") == "statistic" and not obs.get("database_refs"):
            issues.append(Issue("error", "stat-no-db", "statistic observation requires database_refs", rid))

        for ref in obs.get("database_refs", []):
            if not isinstance(ref, dict):
                continue
            rows = ref.get("rows")
            row_count = ref.get("row_count")
            if isinstance(rows, list) and isinstance(row_count, int) and row_count != len(rows):
                issues.append(Issue("error", "db-row-count", "database_ref row_count != len(rows)", rid))
            snapshot_sha = ref.get("snapshot_sha256")
            if isinstance(snapshot_sha, str) and not HEX64.match(snapshot_sha):
                issues.append(Issue("error", "db-snapshot-hash", "database_ref snapshot_sha256 is not 64 hex chars", rid))

        if obs.get("status") == "duplicate" and not obs.get("duplicate_of"):
            issues.append(Issue("error", "duplicate-target", "duplicate observation requires duplicate_of", rid))

        key = (
            str(obs.get("source_id", "")),
            str(obs.get("segment_id", "")),
            str(obs.get("quote_sha256", "")),
            str(obs.get("claim_type", "")),
            str(obs.get("topic", "")),
        )
        if key in dup_keys:
            issues.append(Issue("warning", "observation-duplicate", f"possible duplicate of {dup_keys[key]}", rid))
        else:
            dup_keys[key] = rid

        segment = segments.get(str(obs.get("segment_id", "")))
        if segments and segment is None:
            issues.append(Issue("error", "segment-missing", f"segment not found: {obs.get('segment_id')}", rid))
        elif segment:
            seg_start = segment.get("raw_line_start")
            seg_end = segment.get("raw_line_end")
            if isinstance(start, int) and isinstance(seg_start, int) and start < seg_start:
                issues.append(Issue("error", "line-outside", "raw_line_start is before segment start", rid))
            if isinstance(end, int) and isinstance(seg_end, int) and end > seg_end:
                issues.append(Issue("error", "line-outside", "raw_line_end is after segment end", rid))

            seg_text = str(segment.get("text", ""))
            if isinstance(quote, str) and quote:
                if quote in seg_text:
                    pass
                elif _norm_ws(quote) in _norm_ws(seg_text):
                    issues.append(Issue("warning", "quote-whitespace", "quote matches only after whitespace normalization", rid))
                else:
                    issues.append(Issue("error", "quote-not-found", "quote is not present in segment text", rid))

            seg_cue_start = segment.get("cue_start")
            seg_cue_end = segment.get("cue_end")
            if isinstance(cue_start, (int, float)) and isinstance(seg_cue_start, (int, float)) and cue_start < seg_cue_start - 1:
                issues.append(Issue("error", "cue-outside", "cue_start is before segment cue range", rid))
            if isinstance(cue_end, (int, float)) and isinstance(seg_cue_end, (int, float)) and cue_end > seg_cue_end + 1:
                issues.append(Issue("error", "cue-outside", "cue_end is after segment cue range", rid))

    for proposal in by_type["proposal"]:
        rid = str(proposal.get("proposal_id", "<unknown>"))
        for oid in proposal.get("example_observation_ids", []):
            if oid not in observation_ids:
                issues.append(Issue("error", "proposal-observation", f"unknown observation id {oid}", rid))

    for unresolved in by_type["unresolved"]:
        rid = str(unresolved.get("unresolved_id", "<unknown>"))
        if segments and unresolved.get("segment_id") not in segments:
            issues.append(Issue("error", "unresolved-segment", f"segment not found: {unresolved.get('segment_id')}", rid))
        if unresolved.get("status") == "resolved" and not unresolved.get("resolution"):
            issues.append(Issue("error", "unresolved-resolution", "resolved record requires resolution", rid))

    obs_count = len(by_type["observation"])
    prop_count = len(by_type["proposal"])
    unres_count = len(by_type["unresolved"])
    for run in by_type["run"]:
        rid = str(run.get("run_id", "<unknown>"))
        counts = run.get("counts") or {}
        expected = {
            "observations": obs_count,
            "proposals": prop_count,
            "unresolved": unres_count,
            "errors": len([i for i in issues if i.level == "error"]),
        }
        for key, value in expected.items():
            if counts.get(key) != value:
                issues.append(Issue("error", "run-count", f"run count {key}={counts.get(key)} expected {value}", rid))
        if counts.get("errors") != len(run.get("errors", [])):
            issues.append(Issue("error", "run-errors", "run errors count does not match errors list", rid))

    return issues


def validate_file(
    ledger_path: Path,
    *,
    segments_path: Path | None = None,
    schema_path: Path = DEFAULT_SCHEMA,
) -> list[Issue]:
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
    except (OSError, json.JSONDecodeError, jsonschema.exceptions.SchemaError) as exc:
        return [Issue("error", "schema-invalid", f"cannot load schema: {exc}")]
    records, issues = _read_jsonl(ledger_path)
    segments, segment_issues = _get_segments(segments_path)
    issues.extend(segment_issues)
    issues.extend(validate_records(records, segments=segments, schema=schema))
    return issues


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--segments", type=Path)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--json", action="store_true", help="emit machine-readable results")
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = _build_parser().parse_args(argv)
    issues = validate_file(args.ledger, segments_path=args.segments, schema_path=args.schema)
    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]

    if args.json:
        print(json.dumps({"errors": [i.to_dict() for i in errors], "warnings": [i.to_dict() for i in warnings]}, indent=2, ensure_ascii=False))
    else:
        print(f"ledger: {args.ledger}")
        print(f"errors: {len(errors)}")
        print(f"warnings: {len(warnings)}")
        for issue in errors + warnings:
            prefix = "ERROR" if issue.level == "error" else "WARN"
            where = f" {issue.record_id}" if issue.record_id else ""
            print(f"  {prefix}:{where} [{issue.code}] {issue.message}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
