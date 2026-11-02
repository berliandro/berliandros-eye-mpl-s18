#!/usr/bin/env python3
"""Resolve and record a verified YouTube video for one imported transcript source.

This is intentionally a separate, explicit step: a filename is not enough to
claim a video identity. The tool asks yt-dlp for metadata, checks that the
source week/day words and channel match, and only then writes the video ID/URL
into analysis/sources/source-manifest.json. The raw transcript is untouched.

Usage:
    python tools/link_video_source.py --source-id src-s18-w01d01 `
      --video-id 40fehk2f4_E --series 1036,1037 --confidence high `
      --rationale "W1D1 broadcast; transcript names NAVI vs Alter Ego for match 2"
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "analysis" / "sources" / "source-manifest.json"


def video_id_from(value: str) -> str:
    value = value.strip()
    match = re.search(
        r"(?:v=|/v/|/embed/|/shorts/|/live/|youtu\.be/)([A-Za-z0-9_-]{11})", value
    )
    if match:
        return match.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", value):
        return value
    raise ValueError(f"not a YouTube video ID or URL: {value!r}")


def ytdlp_command(video_id: str, which=shutil.which) -> list[str]:
    """Build a metadata command with an explicit JavaScript runtime for YouTube extraction.

    Prefer Deno when installed; otherwise opt into Node, which this repository
    already uses for its JavaScript build and regression workflow.
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    cmd = ["yt-dlp", "--no-playlist", "--skip-download", "--dump-single-json"]
    deno = which("deno")
    node = which("node")
    if deno:
        cmd.extend(["--js-runtimes", f"deno:{deno}"])
    elif node:
        cmd.extend(["--js-runtimes", f"node:{node}"])
    cmd.append(url)
    return cmd


def ytdlp_metadata(video_id: str) -> dict:
    cmd = ytdlp_command(video_id)
    try:
        raw = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=120)
    except FileNotFoundError as exc:
        raise SystemExit("yt-dlp is not installed") from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"yt-dlp failed: {exc.output.decode('utf-8', 'replace')[:500]}") from exc
    return json.loads(raw.decode("utf-8", "replace"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--video-id", required=True)
    parser.add_argument("--series", default="", help="comma-separated match_detail_id values")
    parser.add_argument("--confidence", default="high", choices=("high", "medium", "low"))
    parser.add_argument("--rationale", required=True)
    parser.add_argument("--manifest", default=str(MANIFEST))
    args = parser.parse_args(argv)

    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source = next((s for s in manifest.get("sources", []) if s["source_id"] == args.source_id), None)
    if source is None:
        raise SystemExit(f"unknown source_id {args.source_id!r}")

    vid = video_id_from(args.video_id)
    meta = ytdlp_metadata(vid)
    title = meta.get("title") or ""
    channel = meta.get("channel") or meta.get("uploader") or ""
    if not channel.lower().startswith("mpl indonesia"):
        raise SystemExit(f"channel mismatch: {channel!r}")
    week, day = source.get("week"), source.get("day")
    needle = f"Minggu {week} Hari {day}"
    if needle.lower() not in title.lower():
        raise SystemExit(f"title mismatch: expected {needle!r} in {title!r}")

    source.update(
        {
            "video_id": vid,
            "video_url": f"https://www.youtube.com/watch?v={vid}",
            "video_title": title,
            "video_channel": channel,
            "video_duration_seconds": meta.get("duration"),
            "video_metadata_provenance": (
                "yt-dlp metadata lookup; title week/day and MPL Indonesia channel matched"
            ),
            "mapping_confidence": f"{args.confidence}_video_metadata",
            "series_mapping": [
                {
                    "match_detail_id": sid.strip(),
                    "confidence": args.confidence,
                    "method": "broadcast_day_schedule_order_and_transcript_context",
                    "rationale": args.rationale,
                }
                for sid in args.series.split(",")
                if sid.strip()
            ],
            "resolved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
    )
    manifest["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(ascii(f"linked {args.source_id} -> {vid} ({meta.get('duration')}s) {title}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
