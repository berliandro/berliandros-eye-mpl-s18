#!/usr/bin/env python3
r"""Safely copy the local MPL ID S18 transcript corpus into this repository.

The source corpus is immutable user material. This tool only copies bytes,
compares SHA-256 checksums before any overwrite decision, and writes a
machine-readable manifest plus a copy-verification report. It never deletes
or edits the source directory.

Usage (PowerShell; quote the path containing spaces and !):
    python tools/import_transcripts.py `
      --source "D:\! Coding\~ shit projects\get-youtube-transcript\mpl-s18-raw-transcripts"

The destination defaults to analysis/sources/raw-transcripts/ and is ignored by
Git. Manifest/verification files are intentionally trackable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_DEST = REPO / "analysis" / "sources" / "raw-transcripts"
DEFAULT_MANIFEST = REPO / "analysis" / "sources" / "source-manifest.json"
DEFAULT_VERIFICATION = REPO / "analysis" / "sources" / "copy-verification.json"
NAME_RE = re.compile(
    r"^LIVE _ MPL ID S18 _ Minggu (?P<week>\d+) Hari (?P<day>\d+) "
    r"_ Bahasa Indonesia - MPL Indonesia\.txt$"
)
LANG_RE = re.compile(r"Bahasa Indonesia - (?P<channel>[^.]+)$")


def sha256_file(path: Path, chunk_size: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_source_name(name: str) -> dict:
    match = NAME_RE.match(name)
    if not match:
        return {
            "week": None,
            "day": None,
            "channel": None,
            "parse_status": "unrecognized_filename",
        }
    week = int(match.group("week"))
    day = int(match.group("day"))
    return {
        "source_id": f"src-s18-w{week:02d}d{day:02d}",
        "week": week,
        "day": day,
        "title": f"LIVE | MPL ID S18 | Minggu {week} Hari {day} | Bahasa Indonesia",
        "channel": "MPL Indonesia",
        "parse_status": "filename_week_day",
    }


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def import_corpus(
    source_dir: Path,
    dest_dir: Path,
    manifest_path: Path,
    verification_path: Path,
) -> dict:
    source_dir = source_dir.resolve()
    if not source_dir.is_dir():
        raise SystemExit(f"source directory not found: {source_dir}")
    dest_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(
        (p for p in source_dir.rglob("*") if p.is_file()),
        key=lambda p: p.relative_to(source_dir).as_posix(),
    )
    if not files:
        raise SystemExit(f"source directory is empty: {source_dir}")

    previous = _load_json(manifest_path)
    previous_by_path = {
        item.get("original_relative_path"): item
        for item in previous.get("sources", [])
        if item.get("original_relative_path")
    }

    entries: list[dict] = []
    sources: list[dict] = []
    copied = identical = conflicts = 0
    total_bytes = 0

    for src in files:
        rel = src.relative_to(source_dir).as_posix()
        dst = dest_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        src_hash = sha256_file(src)
        src_size = src.stat().st_size
        total_bytes += src_size

        status = "copied"
        if dst.exists():
            dst_hash = sha256_file(dst)
            if dst_hash == src_hash and dst.stat().st_size == src_size:
                status = "identical"
                identical += 1
            else:
                status = "conflict"
                conflicts += 1
        if status == "copied":
            shutil.copyfile(src, dst)
            copied += 1

        entry = {
            "source_relative_path": rel,
            "destination_relative_path": dst.relative_to(REPO).as_posix(),
            "sha256": src_hash,
            "bytes": src_size,
            "status": status,
        }
        entries.append(entry)

        meta = parse_source_name(src.name)
        source_id = meta.get("source_id") or f"src-s18-{src.stem.lower().replace(' ', '-')}"
        prior = previous_by_path.get(rel, {})
        record = {
            "source_id": source_id,
            "path": dst.relative_to(REPO).as_posix(),
            "original_relative_path": rel,
            "sha256": src_hash,
            "bytes": src_size,
            "encoding": "utf-8",
            "line_count": line_count(src),
            "week": meta.get("week", prior.get("week")),
            "day": meta.get("day", prior.get("day")),
            "title": meta.get("title", prior.get("title")),
            "channel": meta.get("channel", prior.get("channel")),
            "timestamp_coverage": {
                "present": False,
                "format": None,
                "note": "Raw file contains caption text only; no timestamp strings.",
            },
            "video_id": prior.get("video_id"),
            "video_url": prior.get("video_url"),
            "video_title": prior.get("video_title"),
            "video_channel": prior.get("video_channel"),
            "video_duration_seconds": prior.get("video_duration_seconds"),
            "video_metadata_provenance": prior.get("video_metadata_provenance"),
            "mapping_confidence": prior.get("mapping_confidence", "week_day_from_filename"),
            "series_mapping": prior.get("series_mapping", []),
            "local_only": True,
            "metadata_provenance": "filename; no embedded metadata/timestamps",
        }
        sources.append(record)

    # Detect byte-identical files without deleting anything.
    by_hash: dict[str, list[str]] = {}
    for record in sources:
        by_hash.setdefault(record["sha256"], []).append(record["source_id"])
    for record in sources:
        peers = [sid for sid in by_hash[record["sha256"]] if sid != record["source_id"]]
        record["duplicate_of"] = peers or None

    # Re-verify the copied bytes; conflicts are reported, never hidden.
    verification_entries = []
    verified = 0
    for entry in entries:
        dst = REPO / entry["destination_relative_path"]
        if not dst.exists():
            entry["after_hash_match"] = False
            verification_entries.append(entry)
            continue
        after_hash = sha256_file(dst)
        entry["after_hash_match"] = (
            after_hash == entry["sha256"] and dst.stat().st_size == entry["bytes"]
        )
        if entry["after_hash_match"]:
            verified += 1
        verification_entries.append(entry)

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    manifest = {
        "schema_version": 1,
        "generated_at": now,
        "corpus_root": dest_dir.relative_to(REPO).as_posix(),
        "local_only": True,
        "source_file_count": len(sources),
        "source_total_bytes": total_bytes,
        "sources": sorted(sources, key=lambda s: s["source_id"]),
    }
    verification = {
        "schema_version": 1,
        "generated_at": now,
        "source_root": str(source_dir),
        "destination_root": dest_dir.relative_to(REPO).as_posix(),
        "source_file_count": len(files),
        "source_total_bytes": total_bytes,
        "copied": copied,
        "identical_skipped": identical,
        "conflicts": conflicts,
        "verified_hash_matches": verified,
        "all_verified": verified == len(entries) and conflicts == 0,
        "entries": verification_entries,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    verification_path.write_text(
        json.dumps(verification, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return verification


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="local source corpus directory")
    parser.add_argument("--dest", default=str(DEFAULT_DEST), help="destination directory")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--verification", default=str(DEFAULT_VERIFICATION))
    args = parser.parse_args(argv)

    verification = import_corpus(
        Path(args.source),
        Path(args.dest),
        Path(args.manifest),
        Path(args.verification),
    )
    print(
        "files={source_file_count} bytes={source_total_bytes} copied={copied} "
        "identical={identical_skipped} conflicts={conflicts} verified={verified_hash_matches}".format(
            **verification
        )
    )
    if not verification["all_verified"]:
        print("COPY VERIFICATION FAILED", file=sys.stderr)
        return 1
    print("COPY VERIFICATION PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
