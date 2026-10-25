"""Deterministic tests for quote validation, evidence schema and idempotent ledger builds."""

import hashlib
import json
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
from transcript_evidence import (
    EvidenceError,
    align_captions,
    build_ledger,
    find_quote,
    validate_ledger,
)

REPO = BASE.parent
CACHE = REPO / "analysis" / "cache"
SCHEMA = REPO / "analysis" / "evidence" / "evidence-schema.json"
MANIFEST = REPO / "analysis" / "sources" / "source-manifest.json"


class EvidenceFixture:
    def __init__(self):
        CACHE.mkdir(parents=True, exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix="test-evidence-", dir=CACHE))
        self.raw = self.root / "raw.txt"
        self.raw.write_bytes("alpha beta\r\ngamma delta\r\nalpha beta\r\n".encode("utf-8"))
        self.sha = hashlib.sha256(self.raw.read_bytes()).hexdigest()
        self.manifest = self.root / "manifest.json"
        self.manifest.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "sources": [
                        {
                            "source_id": "src-test",
                            "path": self.raw.relative_to(REPO).as_posix(),
                            "sha256": self.sha,
                            "video_id": "abcdefghijk",
                            "video_url": "https://www.youtube.com/watch?v=abcdefghijk",
                            "line_count": 3,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.cache = self.root / "timed"
        self.cache.mkdir()
        snippets = [
            {"start": 1.0, "duration": 1.0, "text": "alpha beta"},
            {"start": 2.5, "duration": 1.0, "text": "gamma delta"},
            {"start": 4.0, "duration": 1.0, "text": "alpha beta"},
        ]
        aligned = align_captions(
            {
                "source_id": "src-test",
                "path": self.raw.relative_to(REPO).as_posix(),
                "sha256": self.sha,
                "video_id": "abcdefghijk",
                "video_url": "https://www.youtube.com/watch?v=abcdefghijk",
            },
            snippets,
        )
        (self.cache / "src-test.json").write_text(json.dumps(aligned), encoding="utf-8")
        self.db = self.root / "test.db"
        con = sqlite3.connect(self.db)
        con.execute("create table demo(id integer primary key, value text)")
        con.execute("insert into demo values(1, 'row-value')")
        con.commit()
        con.close()
        self.db_sha = hashlib.sha256(self.db.read_bytes()).hexdigest()
        self.queries = self.root / "queries.json"
        self.queries.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "snapshot_id": "test-snapshot",
                    "snapshot_sha256": self.db_sha,
                    "queries": {
                        "Q-TEST": {
                            "description": "one row",
                            "sql": "select id, value from demo where id = :id",
                            "params": {"id": 1},
                            "fields": ["id", "value"],
                            "provenance": "test source row",
                        }
                    },
                }
            ),
            encoding="utf-8",
        )
        self.selection = self.root / "selection.json"
        self.ledger = self.root / "ledger.jsonl"
        self._write_selection(
            quote="gamma delta",
            line_hint=2,
            insight_state="cross-checked",
        )

    def _write_selection(self, quote: str, line_hint: int, insight_state: str):
        self.selection.write_text(
            json.dumps(
                {
                    "pilot_id": "test-pilot",
                    "extraction_version": "test-v1",
                    "observations": [
                        {
                            "id": "OBS-T-1",
                            "source_id": "src-test",
                            "quote": quote,
                            "line_hint": line_hint,
                            "category": "test",
                            "claim": "a transcript claim",
                            "evidence_type": "transcript_statement",
                            "verification_state": "transcript-verified",
                            "scope": "one line",
                            "uncertainty": "test",
                            "database_refs": [],
                        },
                        {
                            "id": "OBS-D-1",
                            "category": "test",
                            "claim": "a database claim",
                            "evidence_type": "database_record",
                            "verification_state": "cross-checked",
                            "scope": "one row",
                            "uncertainty": "test",
                            "database_refs": [{"query_id": "Q-TEST"}],
                        },
                    ],
                    "insights": [
                        {
                            "id": "INS-T-1",
                            "claim": "test insight",
                            "supporting_observation_ids": ["OBS-T-1", "OBS-D-1"],
                            "contradicting_observation_ids": [],
                            "alternative_explanations": ["test alternative"],
                            "scope": "test",
                            "confidence_rationale": "test",
                            "coaching_question": "test?",
                            "verification_state": insight_state,
                        }
                    ],
                    "audits": [
                        {
                            "id": "AUD-T-1",
                            "insight_id": "INS-T-1",
                            "sources_inspected": ["src-test"],
                            "quote_checks": [],
                            "database_checks": [],
                            "counterexamples_searched": [],
                            "visual_review": [],
                            "verdict": "inconclusive",
                            "limitations": ["test"],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

    def build(self):
        return build_ledger(
            self.selection,
            manifest_path=self.manifest,
            ledger_path=self.ledger,
            queries_path=self.queries,
            db_path=self.db,
            cache_dir=self.cache,
            fetch=False,
        )

    def validate(self):
        return validate_ledger(
            self.ledger,
            SCHEMA,
            self.manifest,
            self.queries,
            self.db,
            self.cache,
        )

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


class EvidenceTest(unittest.TestCase):
    def setUp(self):
        self.f = EvidenceFixture()

    def tearDown(self):
        self.f.cleanup()

    def test_quote_must_match_exact_span(self):
        lines = self.f.raw.read_text(encoding="utf-8").replace("\r\n", "\n").split("\n")
        self.assertEqual(find_quote(lines, "gamma delta"), (1, 1))
        with self.assertRaises(EvidenceError):
            find_quote(lines, "gamma  delta")
        with self.assertRaises(EvidenceError):
            find_quote(lines, "absent")

    def test_ambiguous_quote_requires_hint(self):
        lines = ["same", "same"]
        with self.assertRaises(EvidenceError):
            find_quote(lines, "same")
        self.assertEqual(find_quote(lines, "same", 2), (1, 1))

    def test_alignment_count_mismatch_rejected(self):
        with self.assertRaises(EvidenceError):
            align_captions(
                {
                    "source_id": "src-test",
                    "path": self.f.raw.relative_to(REPO).as_posix(),
                    "sha256": self.f.sha,
                    "video_id": "abcdefghijk",
                },
                [{"start": 0, "duration": 1, "text": "alpha beta"}],
            )

    def test_build_and_validate(self):
        result = self.f.build()
        self.assertEqual(result["observations"], 2)
        self.assertEqual(result["insights"], 1)
        self.assertEqual(result["audits"], 1)
        check = self.f.validate()
        self.assertTrue(check["ok"], check["errors"])
        records = [json.loads(line) for line in self.f.ledger.read_text(encoding="utf-8").splitlines()]
        segment = next(r for r in records if r["record_type"] == "segment")
        self.assertEqual(segment["text"], "gamma delta")
        self.assertEqual(segment["timestamp_start"], 2.5)
        self.assertEqual(segment["timestamp_link"], "https://youtu.be/abcdefghijk?t=2")

    def test_build_is_idempotent(self):
        self.f.build()
        first = self.f.ledger.read_bytes()
        self.f.build()
        self.assertEqual(first, self.f.ledger.read_bytes())

    def test_bad_quote_rejected(self):
        self.f._write_selection(quote="not in source", line_hint=2, insight_state="cross-checked")
        with self.assertRaises(EvidenceError):
            self.f.build()

    def test_unknown_source_rejected(self):
        data = json.loads(self.f.selection.read_text(encoding="utf-8"))
        data["observations"][0]["source_id"] = "missing"
        self.f.selection.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(EvidenceError):
            self.f.build()

    def test_gameplay_verified_requires_visual(self):
        self.f._write_selection(quote="gamma delta", line_hint=2, insight_state="gameplay-verified")
        with self.assertRaises(EvidenceError):
            self.f.build()

    def test_database_result_is_reproducible(self):
        self.f.build()
        self.assertTrue(self.f.validate()["ok"])
        con = sqlite3.connect(self.f.db)
        con.execute("update demo set value='changed' where id=1")
        con.commit()
        con.close()
        check = self.f.validate()
        self.assertFalse(check["ok"])
        self.assertTrue(any("snapshot mismatch" in e or "not reproducible" in e for e in check["errors"]))

    def test_validate_rejects_malformed_record(self):
        self.f.build()
        records = [json.loads(line) for line in self.f.ledger.read_text(encoding="utf-8").splitlines()]
        obs = next(r for r in records if r["record_type"] == "observation")
        obs["evidence_type"] = "made_up"
        self.f.ledger.write_text(
            "".join(json.dumps(r) + "\n" for r in records), encoding="utf-8"
        )
        check = self.f.validate()
        self.assertFalse(check["ok"])
        self.assertTrue(any("schema" in e or "evidence_type" in e for e in check["errors"]), check["errors"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
