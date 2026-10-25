#!/usr/bin/env python3
"""Run the deterministic semantic-coaching suite (no live network).

The raw transcript corpus and local frame cache are Git-ignored local inputs.
This runner therefore fails clearly if they are missing rather than pretending
the evidence validation ran.

Usage: python tools/verify_analysis.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPO = BASE.parent

STEPS = [
    ("transcript import safety", [sys.executable, str(BASE / "test_transcript_import.py")], None),
    ("evidence pipeline", [sys.executable, str(BASE / "test_transcript_evidence.py")], None),
    ("video frame units", [sys.executable, str(BASE / "test_video_frames.py")], None),
    ("pilot ledger validation", [sys.executable, str(BASE / "transcript_evidence.py"), "validate"], None),
    ("source/corpus boundary check", [sys.executable, str(BASE / "check_analysis.py")], None),
    ("inventory regeneration", [sys.executable, str(BASE / "analysis_inventory.py")], None),
]


def main() -> int:
    failures = 0
    for name, cmd, _ in STEPS:
        print(f"--- {name}")
        result = subprocess.run(cmd, cwd=REPO)
        print(f"    (exit {result.returncode})")
        if result.returncode != 0:
            failures += 1
    if failures:
        print(f"ANALYSIS VERIFY FAIL ({failures}/{len(STEPS)} suites failed)")
        return 1
    print(f"ANALYSIS VERIFY PASS ({len(STEPS)}/{len(STEPS)} suites)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
