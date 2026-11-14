#!/usr/bin/env python3
"""Regression tests for tools/validate_transcript_ledger.py."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import validate_transcript_ledger as v

SEGMENT = {
    "segment_id": "seg-test-0001",
    "source_id": "src-s18-w01d01",
    "raw_line_start": 1,
    "raw_line_end": 3,
    "cue_start": 10.0,
    "cue_end": 20.0,
    "text": "alpha beta\ngamma delta",
}


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def observation(**overrides):
    record = {
        "record_type": "observation",
        "schema_version": 1,
        "observation_id": "TOBS-src-s18-w01d01-0001",
        "source_id": "src-s18-w01d01",
        "segment_id": "seg-test-0001",
        "raw_line_start": 1,
        "raw_line_end": 2,
        "cue_start": 10.5,
        "cue_end": 12.0,
        "timestamp_provenance": "youtube-auto-caption-alignment-v1",
        "timestamp_link": "https://youtu.be/40fehk2f4_E?t=10",
        "speaker": None,
        "speaker_basis": "unavailable",
        "segment_type": "gameplay",
        "quote": "alpha beta",
        "quote_sha256": sha("alpha beta"),
        "claim": "A test claim.",
        "claim_type": "commentary",
        "topic": "other",
        "entities": {"players": [], "teams": [], "heroes": [], "maps": [], "matches": []},
        "destination": "analysis/matches/1036-evoss-vs-rrq.md",
        "status": "needs_review",
        "confidence": "low",
        "database_refs": [],
        "visual_refs": [],
        "notes": "test",
        "extraction": {
            "run_id": "test-run",
            "model": "test-model",
            "provider": "test-provider",
            "prompt_version": "test-v1",
            "extracted_at": "2026-11-07T00:00:00Z",
        },
        "created_at": "2026-11-07T00:00:00Z",
    }
    record.update(overrides)
    return record


class TranscriptLedgerValidatorTest(unittest.TestCase):
    def run_case(self, observation_record, segment=SEGMENT):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = root / "ledger.jsonl"
            segments = root / "segments.jsonl"
            ledger.write_text(json.dumps(observation_record) + "\n", encoding="utf-8")
            segments.write_text(json.dumps(segment) + "\n", encoding="utf-8")
            return v.validate_file(ledger, segments_path=segments)

    def test_valid_record_passes(self):
        issues = self.run_case(observation())
        self.assertEqual([i for i in issues if i.level == "error"], [])

    def test_bad_quote_hash_is_rejected(self):
        issues = self.run_case(observation(quote_sha256="0" * 64))
        self.assertTrue(any(i.code == "quote-hash" for i in issues))

    def test_quote_not_in_segment_is_rejected(self):
        issues = self.run_case(observation(quote="not in segment", quote_sha256=sha("not in segment")))
        self.assertTrue(any(i.code == "quote-not-found" for i in issues))

    def test_statistic_without_database_ref_is_rejected(self):
        issues = self.run_case(observation(claim_type="statistic"))
        self.assertTrue(any(i.code == "stat-no-db" for i in issues))

    def test_aligned_record_needs_cue(self):
        issues = self.run_case(observation(cue_start=None, cue_end=None))
        self.assertTrue(any(i.code == "timestamp-missing" for i in issues))

    def test_none_provenance_rejects_cue(self):
        issues = self.run_case(
            observation(timestamp_provenance="none", timestamp_link=None)
        )
        self.assertTrue(any(i.code == "timestamp-none" for i in issues))

    def test_duplicate_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = root / "ledger.jsonl"
            segments = root / "segments.jsonl"
            ledger.write_text(json.dumps(observation()) + "\n" + json.dumps(observation()) + "\n", encoding="utf-8")
            segments.write_text(json.dumps(SEGMENT) + "\n", encoding="utf-8")
            issues = v.validate_file(ledger, segments_path=segments)
        self.assertTrue(any(i.code == "id-duplicate" for i in issues))


if __name__ == "__main__":
    unittest.main(verbosity=2)
