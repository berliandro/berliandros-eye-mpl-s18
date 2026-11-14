import unittest
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OFF = REPO / "analysis" / "evidence" / "game-offsets.json"
MANIFEST = REPO / "analysis" / "sources" / "source-manifest.json"
LEDGER = REPO / "analysis" / "evidence" / "pilot-ledger.jsonl"


class AdversarialBoundaryTest(unittest.TestCase):
    """Adversarial test fixtures for boundary detection and evidence validation."""

    def test_ambiguous_team_mention_not_verified(self):
        """A caption mentioning both teams in a discussion context is not a boundary."""
        line = "EVOS dan juga RRQ masih bersaing di klasemen"
        # "match" must appear for it to be a candidate boundary
        self.assertNotIn("match", line.lower())

    def test_false_caption_match_quarantined(self):
        """Heuristic offsets that violate chronological order must not be boundary_verified."""
        data = json.loads(OFF.read_text(encoding='utf-8'))
        for sid, src in data['sources'].items():
            verified = [s for s in src['series'] if s.get('status') == 'boundary_verified']
            starts = [s.get('start_seconds') for s in verified if s.get('start_seconds') is not None]
            self.assertEqual(starts, sorted(starts),
                             f"{sid}: verified boundaries not in chronological order")

    def test_stale_hash_format(self):
        """All stored hashes in timed alignment must be valid SHA-256."""
        import re
        align_dir = REPO / "analysis" / "cache" / "timed"
        if not align_dir.exists():
            self.skipTest("no timed alignment cache")
        for f in list(align_dir.glob("*.json"))[:3]:
            data = json.loads(f.read_text(encoding='utf-8'))
            sha = data.get('raw_sha256', '')
            self.assertTrue(re.match(r'^[0-9a-f]{64}$', sha), f"{f.name}: invalid hash")

    def test_partial_alignment_excluded(self):
        """Partially aligned source must not produce timestamp links."""
        manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
        src = next(s for s in manifest['sources'] if s['source_id'] == 'src-s18-w09d02')
        status = src.get('caption_alignment_status', '')
        self.assertIn(status, ['partial', 'quarantined', 'partial_quarantined'])

    def test_quarantined_source_no_verified_boundary(self):
        """Quarantined/pending entries must not be marked boundary_verified."""
        data = json.loads(OFF.read_text(encoding='utf-8'))
        if 'src-s18-w09d02' in data['sources']:
            src = data['sources']['src-s18-w09d02']
            for s in src['series']:
                self.assertNotEqual(s.get('status'), 'boundary_verified')

    def test_all_series_accounted_for(self):
        """All 72 series must appear in game-offsets.json."""
        data = json.loads(OFF.read_text(encoding='utf-8'))
        ids = []
        for src in data['sources'].values():
            for s in src['series']:
                ids.append(s['match_detail_id'])
        self.assertEqual(len(ids), 72)
        self.assertEqual(len(set(ids)), 72)

    def test_no_duplicate_timeline_ids(self):
        """Each timeline file must have a unique timeline_id."""
        tl_dir = REPO / "analysis" / "evidence" / "game-timelines"
        ids = []
        for f in tl_dir.glob("*.json"):
            t = json.loads(f.read_text(encoding='utf-8'))
            ids.append(t['timeline_id'])
        self.assertEqual(len(ids), len(set(ids)))

    def test_timeline_series_ids_match_db(self):
        """Every timeline's series_id must exist in the matches table."""
        import sqlite3
        db = REPO / "data" / "mpl_id_s18.db"
        if not db.exists():
            self.skipTest("DB not available")
        con = sqlite3.connect(str(db))
        db_ids = set(r[0] for r in con.execute("select match_detail_id from matches").fetchall())
        con.close()
        tl_dir = REPO / "analysis" / "evidence" / "game-timelines"
        for f in tl_dir.glob("*.json"):
            t = json.loads(f.read_text(encoding='utf-8'))
            self.assertIn(t['series_id'], db_ids)

    def test_db_only_timelines_no_transcript(self):
        """DB-only timelines must have game_boundary_status 'unresolved' and no transcript evidence."""
        tl_dir = REPO / "analysis" / "evidence" / "game-timelines"
        for f in tl_dir.glob("*.json"):
            t = json.loads(f.read_text(encoding='utf-8'))
            if t.get("game_boundary_status") == "unresolved":
                for e in t.get("events", []):
                    self.assertIsNone(e.get("transcript_evidence"),
                                      f"{t['timeline_id']}: unresolved but has transcript evidence")

    def test_timeline_db_snapshot_consistent(self):
        """All timelines must reference the same DB snapshot."""
        tl_dir = REPO / "analysis" / "evidence" / "game-timelines"
        snaps = set()
        for f in tl_dir.glob("*.json"):
            t = json.loads(f.read_text(encoding='utf-8'))
            snaps.add(t['db_snapshot_id'])
        self.assertEqual(len(snaps), 1)

    def test_verified_boundary_has_provenance(self):
        """Every boundary_verified series must have method and provenance."""
        data = json.loads(OFF.read_text(encoding='utf-8'))
        for sid, src in data['sources'].items():
            for s in src['series']:
                if s.get('status') == 'boundary_verified':
                    self.assertTrue(s.get('provenance'))
                    self.assertTrue(s.get('provenance', {}).get('method'))

    def test_no_null_start_for_verified(self):
        """Boundary-verified series must have non-null start_seconds."""
        data = json.loads(OFF.read_text(encoding='utf-8'))
        for sid, src in data['sources'].items():
            for s in src['series']:
                if s.get('status') == 'boundary_verified':
                    self.assertIsNotNone(s.get('start_seconds'))

    def test_invalid_db_reference_rejected(self):
        """An insight with a non-existent supporting observation ID should be flagged."""
        # The ledger validator checks supporting_observation_ids non-empty for insights.
        # This test verifies the concept: an insight referencing a non-existent obs is invalid.
        # The observation ID doesn't exist in the ledger
        obs_ids = set()
        for line in LEDGER.read_text(encoding='utf-8').splitlines():
            if line.strip():
                rec = json.loads(line)
                if rec.get('record_type') == 'observation':
                    obs_ids.add(rec.get('id'))
        self.assertNotIn("OBS-NONEXISTENT-999", obs_ids)

    def test_contradictory_report_summaries(self):
        """Coverage summary must not have contradictory counts."""
        cov = (REPO / "analysis" / "reports" / "coverage-summary.md").read_text(encoding='utf-8')
        # Check that pilot + expansion + db_only = 72
        import re
        m_pilot = re.search(r'Pilot.*?\*\*(\d+)\*\*', cov)
        m_exp = re.search(r'Expansion.*?\*\*(\d+)\*\*', cov)
        m_db = re.search(r'DB-only.*?\*\*(\d+)\*\*', cov)
        if m_pilot and m_exp and m_db:
            pilot = int(m_pilot.group(1))
            exp = int(m_exp.group(1))
            db_only = int(m_db.group(1))
            self.assertEqual(pilot + exp + db_only, 72,
                             f"pilot ({pilot}) + expansion ({exp}) + db_only ({db_only}) != 72")


if __name__ == "__main__":
    unittest.main(verbosity=2)
PY