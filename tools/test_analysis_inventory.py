#!/usr/bin/env python3
"""Regression tests ensuring database inventory reports match the current snapshot state."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_inventory import winner_integrity_section


class WinnerIntegrityReportTests(unittest.TestCase):
    def test_active_mismatch_warning_uses_measured_count(self):
        snapshot = {
            "coverage": {"matches": 72},
            "warnings": [{
                "table": "matches",
                "field": "winner",
                "status": "orientation_mismatch",
                "mismatch_count": 21,
                "detail": "21/72 rows conflict with row-oriented score.",
                "example_match_ids": ["1037", "1107"],
            }],
        }
        lines = winner_integrity_section(snapshot)
        report = "\n".join(lines)
        self.assertIn("21/72", report)
        self.assertIn("1037, 1107", report)
        self.assertIn("conflicts with row scores", report)

    def test_repaired_snapshot_does_not_keep_stale_21_row_claim(self):
        snapshot = {"coverage": {"matches": 72}, "warnings": []}
        report = "\n".join(winner_integrity_section(snapshot))
        self.assertIn("No row in the current snapshot", report)
        self.assertNotIn("21/72", report)
        self.assertNotIn("series 1107", report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
