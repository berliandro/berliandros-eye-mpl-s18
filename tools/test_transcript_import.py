"""Deterministic tests for the transcript import/copy safety tool."""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
from import_transcripts import import_corpus, sha256_file

REPO = BASE.parent
CACHE = REPO / "analysis" / "cache"


def write_transcript(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ImportTest(unittest.TestCase):
    def setUp(self):
        CACHE.mkdir(parents=True, exist_ok=True)
        self.tmp = Path(tempfile.mkdtemp(prefix="test-import-", dir=CACHE))
        self.source = self.tmp / "source"
        self.dest = self.tmp / "dest"
        self.manifest = self.tmp / "manifest.json"
        self.verification = self.tmp / "verification.json"
        write_transcript(
            self.source / "LIVE _ MPL ID S18 _ Minggu 1 Hari 1 _ Bahasa Indonesia - MPL Indonesia.txt",
            "alpha\nbeta\n",
        )
        write_transcript(
            self.source / "LIVE _ MPL ID S18 _ Minggu 2 Hari 3 _ Bahasa Indonesia - MPL Indonesia.txt",
            "gamma\n",
        )

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_import(self):
        return import_corpus(self.source, self.dest, self.manifest, self.verification)

    def test_copy_manifest_and_checksums(self):
        result = self.run_import()
        self.assertTrue(result["all_verified"])
        self.assertEqual(result["copied"], 2)
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        self.assertEqual(manifest["source_file_count"], 2)
        first = next(s for s in manifest["sources"] if s["source_id"] == "src-s18-w01d01")
        self.assertEqual(first["line_count"], 2)
        self.assertEqual(first["sha256"], sha256_file(self.source / "LIVE _ MPL ID S18 _ Minggu 1 Hari 1 _ Bahasa Indonesia - MPL Indonesia.txt"))

    def test_repeat_is_identical_and_idempotent(self):
        self.run_import()
        second = self.run_import()
        self.assertTrue(second["all_verified"])
        self.assertEqual(second["copied"], 0)
        self.assertEqual(second["identical_skipped"], 2)

    def test_conflict_is_not_overwritten(self):
        self.run_import()
        target = self.dest / "LIVE _ MPL ID S18 _ Minggu 1 Hari 1 _ Bahasa Indonesia - MPL Indonesia.txt"
        target.write_text("user changed this\n", encoding="utf-8")
        result = self.run_import()
        self.assertFalse(result["all_verified"])
        self.assertEqual(result["conflicts"], 1)
        self.assertEqual(target.read_text(encoding="utf-8"), "user changed this\n")

    def test_duplicate_hash_detected(self):
        write_transcript(
            self.source / "LIVE _ MPL ID S18 _ Minggu 3 Hari 1 _ Bahasa Indonesia - MPL Indonesia.txt",
            "alpha\nbeta\n",
        )
        self.run_import()
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        source = next(s for s in manifest["sources"] if s["source_id"] == "src-s18-w03d01")
        self.assertTrue(source["duplicate_of"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
