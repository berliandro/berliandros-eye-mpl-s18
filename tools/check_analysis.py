#!/usr/bin/env python3
"""Quality gates for the local transcript corpus and pilot evidence boundaries.

Checks that every source manifest path exists and matches its recorded hash,
that source IDs/video IDs are well formed, that series mappings reference real
database matches, and that the raw/media directories are ignored. This is a
local check because the raw corpus is intentionally not committed.

Usage: python tools/check_analysis.py
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "analysis" / "sources" / "source-manifest.json"
LEDGER = REPO / "analysis" / "evidence" / "pilot-ledger.jsonl"
VIDEO_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    fails = []
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    sources = manifest.get("sources", [])
    con = sqlite3.connect(f"file:{REPO / 'data' / 'mpl_id_s18.db'}?mode=ro", uri=True)
    db_matches = {row[0] for row in con.execute("select match_detail_id from schedule_all")}
    con.close()
    if len(sources) != 27:
        fails.append(f"expected 27 sources, found {len(sources)}")
    ids = [s.get("source_id") for s in sources]
    if len(set(ids)) != len(ids):
        fails.append("duplicate source IDs")
    for source in sources:
        path = REPO / source["path"]
        if not path.exists():
            fails.append(f"{source['source_id']}: missing raw path")
            continue
        if sha256(path) != source["sha256"]:
            fails.append(f"{source['source_id']}: raw hash mismatch")
        if path.stat().st_size != source["bytes"]:
            fails.append(f"{source['source_id']}: raw size mismatch")
        if source.get("video_id") and not VIDEO_RE.match(source["video_id"]):
            fails.append(f"{source['source_id']}: malformed video ID")
        for mapping in source.get("series_mapping", []):
            if not mapping.get("match_detail_id"):
                fails.append(f"{source['source_id']}: empty series mapping")
            elif mapping["match_detail_id"] not in db_matches:
                fails.append(f"{source['source_id']}: unknown series {mapping['match_detail_id']}")
    if not LEDGER.exists():
        fails.append("pilot ledger missing")
    else:
        records = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]
        known = set(ids)
        for record in records:
            for sid in record.get("source_ids", []):
                if sid not in known:
                    fails.append(f"ledger references unknown source {sid}")
        if not any(r.get("record_type") == "insight" for r in records):
            fails.append("ledger has no insights")
        if not any(r.get("record_type") == "audit" for r in records):
            fails.append("ledger has no audits")
    for ignored in ("analysis/sources/raw-transcripts", "analysis/cache"):
        # git check-ignore exits 0 when the path is ignored
        import subprocess

        result = subprocess.run(
            ["git", "check-ignore", "-q", ignored], cwd=REPO
        )
        if result.returncode != 0:
            fails.append(f"{ignored} is not Git-ignored")
    if fails:
        print("ANALYSIS CHECK FAIL")
        for fail in fails:
            print("FAIL " + fail)
        return 1
    print(f"PASS sources={len(sources)} ledger_records={len(records) if LEDGER.exists() else 0}")
    print("PASS raw corpus and media caches are Git-ignored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
