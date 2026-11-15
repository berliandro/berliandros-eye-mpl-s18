#!/usr/bin/env python3
"""Regression tests for the end-goal artifacts (coverage, synthesis, briefs)."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MATCHES = REPO / "analysis" / "matches"
TEAMS = REPO / "analysis" / "teams"
HEROES = REPO / "analysis" / "heroes"
STRATEGY = REPO / "analysis" / "strategy"
COACHING = REPO / "analysis" / "coaching"


class GoalArtifactsTest(unittest.TestCase):
    def test_all_72_match_reports_have_one_database_block(self):
        reports = sorted(MATCHES.glob("*.md"))
        self.assertEqual(len(reports), 72)
        for report in reports:
            text = report.read_text(encoding="utf-8")
            self.assertEqual(text.count("<!-- db-evidence:start -->"), 1, report.name)
            self.assertEqual(text.count("<!-- db-evidence:end -->"), 1, report.name)
            self.assertIn("Database snapshot `mpl-s18-db-20c5ea2c51f3`", text, report.name)

    def test_transcript_split_is_27_and_45(self):
        reports = sorted(MATCHES.glob("*.md"))
        with_transcript = [p for p in reports if "## Validated transcript observations" in p.read_text(encoding="utf-8")]
        without = [p for p in reports if "**Transcript coverage:** none." in p.read_text(encoding="utf-8")]
        self.assertEqual(len(with_transcript), 27)
        self.assertEqual(len(without), 45)

    def test_team_profiles_and_briefs(self):
        self.assertEqual(len(sorted(TEAMS.glob("*.md"))), 9)
        for page in TEAMS.glob("*.md"):
            self.assertIn("## Evidence-backed profile", page.read_text(encoding="utf-8"), page.name)
        briefs = sorted((COACHING / "teams").glob("*.md"))
        self.assertEqual(len(briefs), 9)
        self.assertTrue((COACHING / "head-coach-brief.md").is_file())

    def test_hero_profiles_and_strategy_analyses(self):
        hero_pages = sorted(HEROES.glob("*.md"))
        self.assertEqual(len(hero_pages), 94)
        for page in hero_pages:
            self.assertIn("## Evidence-backed profile", page.read_text(encoding="utf-8"), page.name)
        strategy_pages = sorted(STRATEGY.glob("*.md"))
        self.assertEqual(len(strategy_pages), 6)
        for page in strategy_pages:
            self.assertIn("## Evidence-backed analysis", page.read_text(encoding="utf-8"), page.name)

    def test_canonical_store_counts(self):
        store = json.loads((REPO / "analysis/evidence/canonical-store.json").read_text(encoding="utf-8"))
        summary = store["summary"]
        self.assertEqual(summary["transcript_rows"], 368)
        self.assertEqual(summary["transcript_statuses"]["accepted"], 313)
        self.assertEqual(summary["pilot_rows"], 234)
        self.assertEqual(store["reconciliation"]["duplicate_record_ids"], [])
        self.assertEqual(store["authority"], "transcript-observations")

    def test_coverage_matrix_is_complete(self):
        matrix = json.loads((REPO / "analysis/evidence/coverage-matrix.json").read_text(encoding="utf-8"))
        summary = matrix["summary"]
        self.assertEqual(summary["matches_total"], 72)
        self.assertEqual(summary["reports_present"], 72)
        self.assertEqual(summary["db_evidence_blocks"], 72)
        self.assertEqual(summary["evidence_incomplete"], 0)
        self.assertEqual(summary["transcript_matches"], 27)
        self.assertEqual(summary["db_only_matches"], 45)
        self.assertEqual(summary["visual_verified"], 0)
        self.assertEqual(summary["teams_with_synthesis"], 9)
        self.assertEqual(summary["heroes_with_synthesis"], 94)
        self.assertEqual(summary["strategy_with_synthesis"], 6)
        self.assertEqual(summary["team_briefs"], 9)
        self.assertTrue(summary["head_coach_brief"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
