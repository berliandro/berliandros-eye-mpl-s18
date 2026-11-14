#!/usr/bin/env python3
"""Build a bounded transcript segment ledger from raw lines + timed cues.

Raw transcripts are immutable. This tool only reads them and writes a derived
JSONL segment ledger with exact line ranges and aligned caption cues.

Example:
    python tools/build_transcript_segments.py \
      --source-id src-s18-w01d01 \
      --start-line 350 --end-line 4600 \
      --out analysis/evidence/transcript-segments/src-s18-w01d01-1036-g1.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "analysis" / "sources" / "source-manifest.json"
TIMED_DIR = REPO / "analysis" / "cache" / "timed"


def classify(text: str) -> tuple[str, bool, str | None]:
    lower = text.lower()
    ad_terms = ("sponsor", "promo", "tiket", "merchandise", "voting", "kuis")
    if any(term in lower for term in ad_terms):
        return "ad", False, "advertisement/sponsor term"
    if any(term in lower for term in ("draft", "pick", "ban", "hero", "lineup", "roster")):
        return "draft", True, None
    if any(term in lower for term in ("turtle", "lord", "tower", "turret", "gold", "team fight", "teamfight", "kill", "objective")):
        return "gameplay", True, None
    if any(term in lower for term in ("game 2", "game kedua", "series", "match point", "post-game", "post game")):
        return "post_match", True, None
    if any(term in lower for term in ("welcome", "opening", "intro", "pertandingan", "match pertama")):
        return "pre_match", True, None
    if any(term in lower for term in ("coach", "analyst", "analisis", "prediksi")):
        return "analysis", True, None
    return "unknown", True, None


def load_source(source_id: str) -> dict:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for source in data["sources"]:
        if source["source_id"] == source_id:
            return source
    raise SystemExit(f"source not found in manifest: {source_id}")


def build(source_id: str, start_line: int, end_line: int, max_lines: int, out_path: Path) -> dict:
    source = load_source(source_id)
    raw_path = REPO / source["path"]
    timed_path = TIMED_DIR / f"{source_id}.json"
    raw_lines = raw_path.read_text(encoding="utf-8").splitlines()
    timed = json.loads(timed_path.read_text(encoding="utf-8"))["timed_captions"]

    if len(raw_lines) != len(timed):
        raise SystemExit(f"line mismatch: raw={len(raw_lines)} timed={len(timed)}")
    if not (1 <= start_line <= end_line <= len(raw_lines)):
        raise SystemExit(f"invalid line range {start_line}-{end_line} for {len(raw_lines)} lines")

    records = []
    for first in range(start_line, end_line + 1, max_lines):
        last = min(first + max_lines - 1, end_line)
        text = "\n".join(raw_lines[first - 1:last])
        cue_start = timed[first - 1]["start"]
        cue_end = timed[last - 1]["end"]
        segment_type, include, reason = classify(text)
        segment_id = f"seg-{source_id}-L{first:06d}-L{last:06d}"
        records.append(
            {
                "segment_id": segment_id,
                "source_id": source_id,
                "raw_line_start": first,
                "raw_line_end": last,
                "cue_start": cue_start,
                "cue_end": cue_end,
                "timestamp_link": f"https://youtu.be/{source['video_id']}?t={int(cue_start)}",
                "segment_type": segment_type,
                "include": include,
                "exclude_reason": reason,
                "text": text,
                "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            }
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")
    counts = {}
    for record in records:
        counts[record["segment_type"]] = counts.get(record["segment_type"], 0) + 1
    return {"source_id": source_id, "start_line": start_line, "end_line": end_line, "segments": len(records), "types": counts, "out": str(out_path)}


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--start-line", type=int, required=True)
    parser.add_argument("--end-line", type=int, required=True)
    parser.add_argument("--max-lines", type=int, default=10)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    print(json.dumps(build(args.source_id, args.start_line, args.end_line, args.max_lines, args.out), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
