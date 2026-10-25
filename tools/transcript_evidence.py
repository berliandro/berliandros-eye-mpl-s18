#!/usr/bin/env python3
"""Deterministic transcript ingestion, alignment, quote verification and evidence building.

The raw transcript files have no timestamps. For pilot sources with a verified
YouTube video ID, this tool fetches the official timed auto-caption track and
aligns it one-to-one with the raw caption lines. Raw text is never modified;
derived timed data lives under the ignored analysis/cache/ directory.

Commands:
    align    --source-id SRC [--languages id]
    search   --source-id SRC --pattern TEXT [--context 2]
    build    --selection analysis/pilot/selection.json --ledger ...
    validate --ledger ... [--schema ...]

Only explicitly documented normalization is used for matching: CRLF/CR
newlines become LF, and caption alignment ignores leading/trailing whitespace.
Quotes stored in the evidence ledger must match the source byte-for-byte after
newline normalization.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO / "analysis" / "sources" / "source-manifest.json"
DEFAULT_CACHE = REPO / "analysis" / "cache" / "timed"
DEFAULT_LEDGER = REPO / "analysis" / "evidence" / "pilot-ledger.jsonl"
DEFAULT_SCHEMA = REPO / "analysis" / "evidence" / "evidence-schema.json"
DEFAULT_QUERIES = REPO / "analysis" / "evidence" / "query-catalog.json"
DEFAULT_DB = REPO / "data" / "mpl_id_s18.db"

EVIDENCE_TYPES = {
    "transcript_statement",
    "commentator_interpretation",
    "database_record",
    "derived_stat",
    "gameplay_observation",
    "analytical_inference",
}
VERIFICATION_STATES = {
    "unverified",
    "transcript-verified",
    "gameplay-verified",
    "cross-checked",
    "partially-supported",
    "contradicted",
    "inconclusive",
}
VERDICTS = {"supported", "partially supported", "contradicted", "inconclusive"}


class EvidenceError(ValueError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def caption_key(text: str) -> str:
    """Whitespace-insensitive key used only for one-to-one caption alignment."""
    return re.sub(r"\s+", " ", text).strip()


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def source_by_id(manifest: dict, source_id: str) -> dict:
    for source in manifest.get("sources", []):
        if source.get("source_id") == source_id:
            return source
    raise EvidenceError(f"unknown source_id {source_id!r}")


def load_source_text(source: dict, repo: Path = REPO) -> str:
    path = repo / source["path"]
    if not path.exists():
        raise EvidenceError(f"raw source missing: {source['path']}")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != source["sha256"]:
        raise EvidenceError(
            f"raw source checksum changed for {source['source_id']}: {digest} != {source['sha256']}"
        )
    return normalize_newlines(raw.decode("utf-8"))


def fetch_timed(video_id: str, languages: tuple[str, ...] = ("id",)) -> list[dict]:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except Exception as exc:  # pragma: no cover - dependency error path
        raise EvidenceError("youtube_transcript_api is not installed") from exc
    api = YouTubeTranscriptApi()
    fetched = api.fetch(video_id, languages=list(languages))
    return [
        {"start": float(s.start), "duration": float(s.duration), "text": s.text}
        for s in fetched.snippets
    ]


def align_captions(source: dict, snippets: list[dict], manifest_path: Path = DEFAULT_MANIFEST) -> dict:
    text = load_source_text(source)
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    if len(lines) != len(snippets):
        raise EvidenceError(
            f"alignment count mismatch for {source['source_id']}: "
            f"{len(lines)} raw lines vs {len(snippets)} timed snippets"
        )
    mismatches = []
    exact = 0
    normalized = 0
    for index, (line, snippet) in enumerate(zip(lines, snippets)):
        if line == snippet["text"]:
            exact += 1
        elif caption_key(line) == caption_key(snippet["text"]):
            normalized += 1
        else:
            mismatches.append(
                {"line_no": index + 1, "raw": line, "timed": snippet["text"]}
            )
            if len(mismatches) >= 10:
                break
    if mismatches:
        raise EvidenceError(
            f"caption alignment failed for {source['source_id']}: {len(mismatches)} mismatches "
            f"(first: {mismatches[0]})"
        )
    mapping = []
    for index, (line, snippet) in enumerate(zip(lines, snippets), start=1):
        start = snippet["start"]
        end = start + snippet["duration"]
        mapping.append(
            {
                "line_no": index,
                "text": line,
                "start": round(start, 3),
                "duration": round(snippet["duration"], 3),
                "end": round(end, 3),
            }
        )
    return {
        "schema_version": 1,
        "source_id": source["source_id"],
        "video_id": source["video_id"],
        "video_url": source.get("video_url"),
        "raw_sha256": source["sha256"],
        "raw_line_count": len(lines),
        "timed_snippet_count": len(snippets),
        "exact_matches": exact,
        "normalized_matches": normalized,
        "mismatch_count": 0,
        "normalization": "CRLF/CR->LF; caption alignment strips leading/trailing whitespace",
        "timestamp_provenance": "youtube-auto-caption-alignment-v1",
        "aligned_at": now(),
        "alignment_status": "verified",
        "timed_captions": mapping,
    }


def load_alignment(source_id: str, cache_dir: Path = DEFAULT_CACHE) -> dict | None:
    path = cache_dir / f"{source_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def alignment_for(source: dict, cache_dir: Path = DEFAULT_CACHE, fetch: bool = False) -> dict:
    cached = load_alignment(source["source_id"], cache_dir)
    if cached:
        if cached.get("raw_sha256") != source.get("sha256"):
            raise EvidenceError("cached alignment belongs to a different raw source checksum")
        return cached
    if not source.get("video_id"):
        raise EvidenceError(f"source {source['source_id']} has no verified video_id")
    if not fetch:
        raise EvidenceError(
            f"no cached timed alignment for {source['source_id']}; run: "
            f"python tools/transcript_evidence.py align --source-id {source['source_id']}"
        )
    snippets = fetch_timed(source["video_id"])
    aligned = align_captions(source, snippets)
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / f"{source['source_id']}.json").write_text(
        json.dumps(aligned, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return aligned


def find_quote(lines: list[str], quote: str, line_hint: int | None = None) -> tuple[int, int]:
    if not quote:
        raise EvidenceError("empty quote")
    text = "\n".join(lines)
    positions = [m.start() for m in re.finditer(re.escape(quote), text)]
    if not positions:
        raise EvidenceError("quote not found in source after newline normalization")
    spans = []
    for pos in positions:
        before = text[:pos]
        line_start = before.count("\n")
        line_end = line_start + quote.count("\n")
        spans.append((line_start, line_end))
    if line_hint is not None:
        matches = [(s, e) for s, e in spans if s <= line_hint - 1 <= e]
        if not matches:
            raise EvidenceError(f"quote does not cover line_hint {line_hint}")
        if len(matches) > 1:
            raise EvidenceError("line_hint still ambiguous for quote")
        return matches[0]
    if len(spans) > 1:
        raise EvidenceError(
            f"quote occurs {len(spans)} times; provide line_hint to disambiguate"
        )
    return spans[0]


def segment_id(source_id: str, line_start: int, line_end: int) -> str:
    return f"seg-{source_id}-L{line_start:06d}-L{line_end:06d}"


def build_segment(
    source: dict, lines: list[str], quote: str, line_hint: int | None, alignment: dict
) -> dict:
    line_start, line_end = find_quote(lines, quote, line_hint)
    mapping = {row["line_no"]: row for row in alignment["timed_captions"]}
    first = mapping[line_start + 1]
    last = mapping[line_end + 1]
    video_id = source["video_id"]
    link = f"https://youtu.be/{video_id}?t={int(first['start'])}"
    return {
        "record_type": "segment",
        "schema_version": 1,
        "id": segment_id(source["source_id"], line_start + 1, line_end + 1),
        "source_id": source["source_id"],
        "path": source["path"],
        "line_start": line_start + 1,
        "line_end": line_end + 1,
        "text": quote,
        "text_sha256": sha256_text(quote),
        "timestamp_start": first["start"],
        "timestamp_end": last["end"],
        "timestamp_link": link,
        "timestamp_provenance": alignment["timestamp_provenance"],
        "video_id": video_id,
    }


def run_query(db_path: Path, query: dict) -> dict:
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        rows = [dict(row) for row in con.execute(query["sql"], query.get("params", {}))]
    finally:
        con.close()
    max_rows = query.get("max_rows")
    truncated = False
    if max_rows is not None and len(rows) > max_rows:
        rows = rows[:max_rows]
        truncated = True
    return {"rows": rows, "row_count": len(rows), "truncated": truncated}


def database_refs(
    refs: list[dict], queries: dict, db_path: Path, snapshot_id: str, snapshot_sha: str
) -> list[dict]:
    result = []
    for ref in refs:
        qid = ref["query_id"]
        if qid not in queries.get("queries", {}):
            raise EvidenceError(f"unknown database query_id {qid!r}")
        query = queries["queries"][qid]
        params = dict(query.get("params") or {})
        params.update(ref.get("params") or {})
        executed = run_query(db_path, {**query, "params": params})
        result.append(
            {
                "query_id": qid,
                "description": query["description"],
                "sql": query["sql"],
                "params": params,
                "fields": query.get("fields", []),
                "provenance": query["provenance"],
                "snapshot_id": snapshot_id,
                "snapshot_sha256": snapshot_sha,
                "rows": executed["rows"],
                "row_count": executed["row_count"],
                "truncated": executed["truncated"],
                "note": ref.get("note"),
            }
        )
    return result


def build_ledger(
    selection_path: Path,
    manifest_path: Path = DEFAULT_MANIFEST,
    ledger_path: Path = DEFAULT_LEDGER,
    queries_path: Path = DEFAULT_QUERIES,
    db_path: Path = DEFAULT_DB,
    cache_dir: Path = DEFAULT_CACHE,
    fetch: bool = False,
) -> dict:
    manifest = load_manifest(manifest_path)
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    queries = json.loads(queries_path.read_text(encoding="utf-8"))
    db_path = db_path.resolve()
    snapshot_sha = sha256_file(db_path)
    if snapshot_sha != queries.get("snapshot_sha256"):
        raise EvidenceError(
            "database snapshot checksum does not match query catalog: "
            f"{snapshot_sha} != {queries.get('snapshot_sha256')}"
        )
    snapshot_id = queries["snapshot_id"]

    segments: dict[str, dict] = {}
    observations: list[dict] = []
    for item in selection.get("observations", []):
        segment = None
        source_ids = []
        if item.get("quote"):
            if not item.get("source_id"):
                raise EvidenceError(f"observation {item['id']} has a quote but no source_id")
            source = source_by_id(manifest, item["source_id"])
            alignment = alignment_for(source, cache_dir, fetch=fetch)
            text = load_source_text(source)
            lines = normalize_newlines(text).split("\n")
            if lines and lines[-1] == "":
                lines = lines[:-1]
            segment = build_segment(source, lines, item["quote"], item.get("line_hint"), alignment)
            segments[segment["id"]] = segment
            source_ids = [item["source_id"]]
        observation = {
            "record_type": "observation",
            "schema_version": 1,
            "id": item["id"],
            "version": item.get("version", 1),
            "pilot_id": selection["pilot_id"],
            "category": item["category"],
            "claim": item["claim"],
            "evidence_type": item["evidence_type"],
            "verification_state": item["verification_state"],
            "segment_ids": [segment["id"]] if segment else [],
            "source_ids": source_ids,
            "database_refs": database_refs(
                item.get("database_refs", []), queries, db_path, snapshot_id, snapshot_sha
            ),
            "visual_refs": item.get("visual_refs", []),
            "scope": item["scope"],
            "uncertainty": item["uncertainty"],
            "notes": item.get("notes", ""),
            "extraction_version": selection.get("extraction_version", "manual-pilot-v1"),
        }
        if observation["evidence_type"] in {"database_record", "derived_stat"} and not observation["database_refs"]:
            raise EvidenceError(f"{observation['id']}: database evidence without database_refs")
        if observation["evidence_type"] in {"transcript_statement", "commentator_interpretation"} and not segment:
            raise EvidenceError(f"{observation['id']}: transcript evidence without a quote")
        observations.append(observation)
    obs_by_id = {o["id"]: o for o in observations}
    if len(obs_by_id) != len(observations):
        raise EvidenceError("duplicate observation id")

    insights: list[dict] = []
    for item in selection.get("insights", []):
        support = item.get("supporting_observation_ids", [])
        contradict = item.get("contradicting_observation_ids", [])
        for oid in support + contradict:
            if oid not in obs_by_id:
                raise EvidenceError(f"insight {item['id']} references unknown observation {oid}")
        state = item.get("verification_state")
        if state not in VERIFICATION_STATES:
            raise EvidenceError(f"invalid insight verification_state {state!r}")
        if state == "gameplay-verified":
            visual = [
                obs_by_id[oid]
                for oid in support
                if obs_by_id[oid]["evidence_type"] == "gameplay_observation"
                and obs_by_id[oid]["verification_state"] == "gameplay-verified"
            ]
            if not visual:
                raise EvidenceError(
                    f"insight {item['id']} cannot be gameplay-verified without a "
                    "gameplay-verified observation"
                )
        insights.append(
            {
                "record_type": "insight",
                "schema_version": 1,
                "id": item["id"],
                "version": item.get("version", 1),
                "pilot_id": selection["pilot_id"],
                "claim": item["claim"],
                "supporting_observation_ids": support,
                "contradicting_observation_ids": contradict,
                "alternative_explanations": item.get("alternative_explanations", []),
                "scope": item["scope"],
                "confidence_rationale": item["confidence_rationale"],
                "coaching_question": item.get("coaching_question", ""),
                "verification_state": state,
                "extraction_version": selection.get("extraction_version", "manual-pilot-v1"),
            }
        )
    insight_by_id = {i["id"]: i for i in insights}

    audits: list[dict] = []
    for item in selection.get("audits", []):
        insight = insight_by_id.get(item["insight_id"])
        if not insight:
            raise EvidenceError(f"audit references unknown insight {item['insight_id']}")
        if item["verdict"] not in VERDICTS:
            raise EvidenceError(f"invalid audit verdict {item['verdict']!r}")
        audits.append(
            {
                "record_type": "audit",
                "schema_version": 1,
                "id": item["id"],
                "insight_id": item["insight_id"],
                "insight_version": insight["version"],
                "sources_inspected": item["sources_inspected"],
                "quote_checks": item["quote_checks"],
                "database_checks": item["database_checks"],
                "counterexamples_searched": item["counterexamples_searched"],
                "visual_review": item.get("visual_review", []),
                "verdict": item["verdict"],
                "limitations": item["limitations"],
                "created_at": item.get("created_at", now()),
            }
        )

    records = (
        [segments[key] for key in sorted(segments)]
        + sorted(observations, key=lambda r: r["id"])
        + sorted(insights, key=lambda r: r["id"])
        + sorted(audits, key=lambda r: r["id"])
    )
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )
    audit_log = ledger_path.parent / "audit-log.jsonl"
    audit_log.write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in audits),
        encoding="utf-8",
    )
    timed_summary = {
        "schema_version": 1,
        "generated_at": now(),
        "sources": [
            {
                "source_id": sid,
                "video_id": source_by_id(manifest, sid)["video_id"],
                "raw_sha256": source_by_id(manifest, sid)["sha256"],
                "raw_lines": alignment_for(source_by_id(manifest, sid), cache_dir)["raw_line_count"],
                "exact_matches": alignment_for(source_by_id(manifest, sid), cache_dir)["exact_matches"],
                "normalized_matches": alignment_for(source_by_id(manifest, sid), cache_dir)["normalized_matches"],
                "timestamp_provenance": "youtube-auto-caption-alignment-v1",
            }
            for sid in sorted({o["source_ids"][0] for o in observations if o["source_ids"]})
            if source_by_id(manifest, sid).get("video_id")
        ],
    }
    (ledger_path.parent / "timed-alignment.json").write_text(
        json.dumps(timed_summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return {
        "segments": len(segments),
        "observations": len(observations),
        "insights": len(insights),
        "audits": len(audits),
        "ledger": str(ledger_path),
    }


def validate_ledger(
    ledger_path: Path = DEFAULT_LEDGER,
    schema_path: Path = DEFAULT_SCHEMA,
    manifest_path: Path = DEFAULT_MANIFEST,
    queries_path: Path = DEFAULT_QUERIES,
    db_path: Path = DEFAULT_DB,
    cache_dir: Path = DEFAULT_CACHE,
) -> dict:
    try:
        import jsonschema
    except Exception as exc:  # pragma: no cover
        raise EvidenceError("jsonschema is required for ledger validation") from exc
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    manifest = load_manifest(manifest_path)
    queries = json.loads(queries_path.read_text(encoding="utf-8"))
    db_path = db_path.resolve()
    snapshot_sha = sha256_file(db_path)
    text_cache: dict[str, str] = {}
    records = []
    errors = []
    for line_no, line in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            jsonschema.validate(record, schema)
        except Exception as exc:
            errors.append(f"line {line_no}: schema/invalid JSON: {exc}")
            continue
        records.append(record)
    by_id = {r["id"]: r for r in records if "id" in r}
    if len(by_id) != len([r for r in records if "id" in r]):
        errors.append("duplicate stable IDs")
    segments = {r["id"]: r for r in records if r["record_type"] == "segment"}
    observations = {r["id"]: r for r in records if r["record_type"] == "observation"}
    insights = {r["id"]: r for r in records if r["record_type"] == "insight"}
    audits = {r["id"]: r for r in records if r["record_type"] == "audit"}
    for seg in segments.values():
        source = source_by_id(manifest, seg["source_id"])
        if seg["source_id"] not in text_cache:
            text_cache[seg["source_id"]] = load_source_text(source)
        lines = text_cache[seg["source_id"]].split("\n")
        expected = "\n".join(lines[seg["line_start"] - 1 : seg["line_end"]])
        if seg["text"] != expected:
            errors.append(f"{seg['id']}: quote does not match source line span")
        if sha256_text(seg["text"]) != seg["text_sha256"]:
            errors.append(f"{seg['id']}: text hash mismatch")
        alignment = load_alignment(seg["source_id"], cache_dir)
        if alignment:
            row = next(
                (r for r in alignment["timed_captions"] if r["line_no"] == seg["line_start"]),
                None,
            )
            if row and abs(row["start"] - seg["timestamp_start"]) > 0.01:
                errors.append(f"{seg['id']}: timestamp_start does not match cached alignment")
    for obs in observations.values():
        if obs["evidence_type"] not in EVIDENCE_TYPES:
            errors.append(f"{obs['id']}: invalid evidence_type")
        if obs["verification_state"] not in VERIFICATION_STATES:
            errors.append(f"{obs['id']}: invalid verification_state")
        if obs["evidence_type"] == "gameplay_observation" and obs["verification_state"] == "gameplay-verified":
            reviewed = [v for v in obs.get("visual_refs", []) if v.get("reviewed") is True]
            if not reviewed:
                errors.append(f"{obs['id']}: gameplay-verified without a reviewed visual_ref")
        for sid in obs["segment_ids"]:
            if sid not in segments:
                errors.append(f"{obs['id']}: missing segment {sid}")
        for ref in obs["database_refs"]:
            if ref["snapshot_sha256"] != snapshot_sha:
                errors.append(f"{obs['id']}: database snapshot mismatch")
            qid = ref["query_id"]
            if qid not in queries.get("queries", {}):
                errors.append(f"{obs['id']}: unknown query {qid}")
                continue
            try:
                again = run_query(
                    db_path,
                    {
                        **queries["queries"][qid],
                        "params": ref.get("params", queries["queries"][qid].get("params", {})),
                    },
                )
            except Exception as exc:
                errors.append(f"{obs['id']}: query {qid} failed: {exc}")
                continue
            if again["rows"] != ref["rows"]:
                errors.append(f"{obs['id']}: query {qid} result is not reproducible")
    for ins in insights.values():
        for oid in ins["supporting_observation_ids"] + ins["contradicting_observation_ids"]:
            if oid not in observations:
                errors.append(f"{ins['id']}: missing observation {oid}")
        if ins["verification_state"] == "gameplay-verified":
            has_visual = any(
                observations.get(oid, {}).get("evidence_type") == "gameplay_observation"
                and observations.get(oid, {}).get("verification_state") == "gameplay-verified"
                for oid in ins["supporting_observation_ids"]
            )
            if not has_visual:
                errors.append(f"{ins['id']}: gameplay-verified without visual observation")
    for audit in audits.values():
        if audit["insight_id"] not in insights:
            errors.append(f"{audit['id']}: missing insight {audit['insight_id']}")
        if audit["verdict"] not in VERDICTS:
            errors.append(f"{audit['id']}: invalid verdict")
    return {
        "ok": not errors,
        "errors": errors,
        "counts": {
            "segments": len(segments),
            "observations": len(observations),
            "insights": len(insights),
            "audits": len(audits),
        },
    }


def search_source(source: dict, pattern: str, context: int = 2) -> list[dict]:
    alignment = load_alignment(source["source_id"])
    text = load_source_text(source)
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    try:
        rx = re.compile(pattern, re.IGNORECASE)
    except re.error as exc:
        raise EvidenceError(f"bad regex: {exc}") from exc
    hits = []
    for index, line in enumerate(lines):
        if rx.search(line):
            start = max(0, index - context)
            end = min(len(lines), index + context + 1)
            elapsed = None
            if alignment:
                row = alignment["timed_captions"][index]
                elapsed = row["start"]
            hits.append(
                {
                    "line_no": index + 1,
                    "timestamp": elapsed,
                    "context": lines[start:end],
                }
            )
    return hits


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    sub = parser.add_subparsers(dest="command", required=True)

    align = sub.add_parser("align")
    align.add_argument("--source-id", required=True)
    align.add_argument("--languages", default="id")
    align.add_argument("--cache-dir", default=str(DEFAULT_CACHE))

    search = sub.add_parser("search")
    search.add_argument("--source-id", required=True)
    search.add_argument("--pattern", required=True)
    search.add_argument("--context", type=int, default=2)

    build = sub.add_parser("build")
    build.add_argument("--selection", required=True)
    build.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    build.add_argument("--queries", default=str(DEFAULT_QUERIES))
    build.add_argument("--db", default=str(DEFAULT_DB))
    build.add_argument("--cache-dir", default=str(DEFAULT_CACHE))
    build.add_argument("--fetch", action="store_true")

    validate = sub.add_parser("validate")
    validate.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    validate.add_argument("--schema", default=str(DEFAULT_SCHEMA))
    validate.add_argument("--queries", default=str(DEFAULT_QUERIES))
    validate.add_argument("--db", default=str(DEFAULT_DB))
    validate.add_argument("--cache-dir", default=str(DEFAULT_CACHE))

    args = parser.parse_args(argv)
    manifest = load_manifest(Path(args.manifest))
    try:
        if args.command == "align":
            source = source_by_id(manifest, args.source_id)
            if not source.get("video_id"):
                raise EvidenceError("source has no verified video_id")
            snippets = fetch_timed(source["video_id"], tuple(args.languages.split(",")))
            aligned = align_captions(source, snippets)
            cache_dir = Path(args.cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
            (cache_dir / f"{source['source_id']}.json").write_text(
                json.dumps(aligned, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            print(
                f"aligned {source['source_id']}: {aligned['raw_line_count']} lines, "
                f"{aligned['exact_matches']} exact, {aligned['normalized_matches']} normalized"
            )
            return 0
        if args.command == "search":
            source = source_by_id(manifest, args.source_id)
            for hit in search_source(source, args.pattern, args.context):
                stamp = hit["timestamp"]
                stamp_text = (
                    f"{int(stamp // 3600):02d}:{int(stamp % 3600 // 60):02d}:{int(stamp % 60):02d}"
                    if stamp is not None
                    else "no-timestamp"
                )
                print(f"L{hit['line_no']:05d} {stamp_text} " + " | ".join(hit["context"]))
            return 0
        if args.command == "build":
            result = build_ledger(
                Path(args.selection),
                manifest_path=Path(args.manifest),
                ledger_path=Path(args.ledger),
                queries_path=Path(args.queries),
                db_path=Path(args.db),
                cache_dir=Path(args.cache_dir),
                fetch=args.fetch,
            )
            print(json.dumps(result, indent=2))
            return 0
        if args.command == "validate":
            result = validate_ledger(
                Path(args.ledger),
                Path(args.schema),
                Path(args.manifest),
                Path(args.queries),
                Path(args.db),
                Path(args.cache_dir),
            )
            print(json.dumps(result, indent=2))
            return 0 if result["ok"] else 1
    except EvidenceError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
