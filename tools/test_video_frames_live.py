#!/usr/bin/env python3
"""Live-only video frame smoke test. Not part of the deterministic suite.

Set RUN_LIVE_VIDEO_SMOKE=1 and run:
    python tools/test_video_frames_live.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def main() -> int:
    if os.environ.get("RUN_LIVE_VIDEO_SMOKE") != "1":
        print("SKIP live video smoke (set RUN_LIVE_VIDEO_SMOKE=1)")
        return 0
    out = REPO / "analysis" / "cache" / "video-frames" / "live-smoke"
    cmd = [
        sys.executable,
        str(REPO / "tools" / "video_frames.py"),
        "--source-id", "src-s18-w01d01",
        "--timestamps", "04:14:05",
        "--out-dir", str(out),
        "--no-reuse",
    ]
    result = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=300)
    print(result.stdout[-3000:])
    if result.returncode != 0:
        print(result.stderr[-3000:], file=sys.stderr)
        return result.returncode
    index_path = out / "src-s18-w01d01-capture-index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    if index["success_count"] != 1 or index["failure_count"] != 0:
        print(f"FAIL unexpected capture counts: {index['success_count']}/{index['failure_count']}")
        return 1
    frame = index["frames"][0]
    if not frame.get("timestamp_link", "").startswith("https://www.youtube.com/watch?v=40fehk2f4_E&t="):
        print("FAIL missing canonical timestamp link")
        return 1
    path = REPO / frame["output_path"]
    if not path.exists() or path.stat().st_size < 20000:
        print("FAIL frame missing or implausibly small")
        return 1
    print(f"PASS live frame {frame['actual_seconds']}s -> {frame['output_path']} ({path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
