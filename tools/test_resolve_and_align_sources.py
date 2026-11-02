#!/usr/bin/env python3
"""Offline tests for schedule VOD candidates and metadata verification."""
import csv,json,sys,tempfile,unittest
from pathlib import Path
TOOLS=Path(__file__).resolve().parent;REPO=TOOLS.parent;sys.path.insert(0,str(TOOLS))
from resolve_and_align_sources import build_schedule_candidates,metadata_errors,regular_schedule_rows,cache_alignment_is_current,derive_source_status
MANIFEST=REPO/"analysis/sources/source-manifest.json";SCHEDULE=REPO/"data/csv/schedule_all.csv"


class ResolverRegressionTests(unittest.TestCase):
    def test_partial_alignment_not_citation_ready(self):
        from resolve_and_align_sources import cache_alignment_is_current
        manifest = {"sources": [{"source_id": "s1", "sha256": "x", "video_id": "abc"}]}
        alignment = {"video_id": "abc", "raw_sha256": "x", "alignment_status": "partial", "mismatch_count": 1}
        self.assertFalse(cache_alignment_is_current(manifest["sources"][0], "abc", alignment))

    def test_quarantined_source_not_treated_as_verified(self):
        import json
        m = json.loads((Path(__file__).resolve().parent.parent / "analysis" / "sources" / "source-manifest.json").read_text())
        for s in m["sources"]:
            if s["source_id"] == "src-s18-w09d02":
                self.assertEqual(s.get("citation_policy"), "quarantined")
                break
        import json
        m = json.loads((Path(__file__).resolve().parent.parent / "analysis" / "sources" / "source-manifest.json").read_text())
        for s in m["sources"]:
            if s["source_id"] == "src-s18-w09d02":
                self.assertEqual(s.get("citation_policy"), "quarantined")
                break


    def test_partial_alignment_not_citation_ready(self):
        from resolve_and_align_sources import cache_alignment_is_current
        manifest = {"sources": [{"source_id": "s1", "sha256": "x", "video_id": "abc"}]}
        alignment = {"video_id": "abc", "raw_sha256": "x", "alignment_status": "partial", "mismatch_count": 1}
        self.assertFalse(cache_alignment_is_current(manifest["sources"][0], "abc", alignment))

    def test_quarantined_source_not_treated_as_verified(self):
        import json
        m = json.loads((Path(__file__).resolve().parent.parent / "analysis" / "sources" / "source-manifest.json").read_text())
        for s in m["sources"]:
            if s["source_id"] == "src-s18-w09d02":
                self.assertEqual(s.get("citation_policy"), "quarantined")
                break


class ResolverTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.manifest=json.loads(MANIFEST.read_text(encoding="utf-8"));cls.candidates,cls.failures=build_schedule_candidates(cls.manifest,SCHEDULE)
 def test_27_unique_candidates(self):
  self.assertEqual(len(self.candidates),27);self.assertEqual(self.failures,[]);self.assertTrue(all(x["candidate_video_id"] for x in self.candidates.values()));self.assertEqual(len({x["candidate_video_id"] for x in self.candidates.values()}),27)
 def test_all_72_series_map_once(self):
  ids=[mid for x in self.candidates.values() for mid in x["schedule_match_ids"]];expected=[str(r["match_detail_id"]) for r in regular_schedule_rows(SCHEDULE) if r.get("match_detail_id")]
  self.assertEqual(len(ids),72);self.assertEqual(len(set(ids)),72);self.assertCountEqual(ids,expected)
 def test_known_dates_and_ids(self):
  a=self.candidates["src-s18-w01d01"];b=self.candidates["src-s18-w09d03"]
  self.assertEqual((a["broadcast_date"],a["candidate_video_id"]),("2026-08-14","40fehk2f4_E"));self.assertEqual([x["match_detail_id"] for x in a["series_mapping"]],["1036","1037"]);self.assertEqual(b["candidate_video_id"],"hY0Upem95uo")
 def test_ambiguous_vods_rejected(self):
  rows=list(csv.DictReader(SCHEDULE.open("r",encoding="utf-8-sig",newline="")));target=next(r for r in rows if r["iso_date"]=="2026-08-14" and r["status"]=="completed");target["vod_url"]="https://www.youtube.com/watch?v=AAAAAAAAAAA"
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/"schedule.csv"
   with p.open("w",encoding="utf-8",newline="") as f:w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
   candidates,errors=build_schedule_candidates(self.manifest,p)
  self.assertIsNone(candidates["src-s18-w01d01"]["candidate_video_id"]);self.assertTrue(any("one distinct VOD ID" in e for e in errors))
 def test_alignment_requires_same_candidate_and_current_raw_hash(self):
  source={"source_id":"src-s18-w02d01","video_id":"O1vhySUmgj0","video_metadata_provenance":"yt-dlp verified","sha256":"raw-hash"}
  alignment={"source_id":"src-s18-w02d01","video_id":"O1vhySUmgj0","raw_sha256":"raw-hash","alignment_status":"verified","mismatch_count":0,"raw_line_count":12,"timed_snippet_count":12,"exact_matches":12,"normalized_matches":0,"timestamp_provenance":"test"}
  self.assertTrue(cache_alignment_is_current(source,"O1vhySUmgj0",alignment))
  self.assertEqual(derive_source_status(source,{"candidate_video_id":"O1vhySUmgj0"},alignment),"caption_alignment_verified")
  self.assertFalse(cache_alignment_is_current({**source,"sha256":"changed"},"O1vhySUmgj0",alignment))
  self.assertEqual(derive_source_status({**source,"sha256":"changed"},{"candidate_video_id":"O1vhySUmgj0"},alignment),"metadata_verified")

 def test_alignment_rejects_candidate_mismatch_or_bad_counts(self):
  source={"source_id":"src-s18-w02d01","video_id":"O1vhySUmgj0","video_metadata_provenance":"yt-dlp verified","sha256":"raw-hash"}
  alignment={"source_id":"src-s18-w02d01","video_id":"O1vhySUmgj0","raw_sha256":"raw-hash","alignment_status":"verified","mismatch_count":0,"raw_line_count":12,"timed_snippet_count":11,"exact_matches":11,"normalized_matches":0,"timestamp_provenance":"test"}
  self.assertFalse(cache_alignment_is_current(source,"otherVideoID",alignment))
  self.assertFalse(cache_alignment_is_current(source,"O1vhySUmgj0",alignment))
  self.assertEqual(derive_source_status(source,{"candidate_video_id":None},alignment),"candidate_resolution_failed")
  self.assertEqual(derive_source_status(source,{"candidate_video_id":"different123"},alignment),"schedule_candidate_pending_verification")

 def test_metadata_gates_channel_season_day(self):
  s={"week":2,"day":1};good={"title":"LIVE | MPL ID S18 | Minggu 2 Hari 1 | Bahasa Indonesia","channel":"MPL Indonesia"}
  self.assertEqual(metadata_errors(s,"O1vhySUmgj0",good),[]);self.assertTrue(metadata_errors(s,"O1vhySUmgj0",{**good,"channel":"fan archive"}));self.assertTrue(metadata_errors(s,"O1vhySUmgj0",{**good,"title":"MPL ID S18 | Minggu 2 Hari 2"}));self.assertTrue(metadata_errors(s,"O1vhySUmgj0",{**good,"title":"Minggu 2 Hari 1"}))
if __name__=="__main__":unittest.main(verbosity=2)
