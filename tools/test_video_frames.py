"""Deterministic tests for tools/video_frames.py (synthetic media, no network)."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
import video_frames as vf

REPO = BASE.parent
CACHE = REPO / "analysis" / "cache"


class TimestampTest(unittest.TestCase):
    def test_parse_formats(self):
        self.assertEqual(vf.parse_timestamp("00:12:34"), 754)
        self.assertEqual(vf.parse_timestamp("12:34"), 754)
        self.assertEqual(vf.parse_timestamp("754"), 754)
        self.assertAlmostEqual(vf.parse_timestamp("1.5"), 1.5)

    def test_reject_invalid(self):
        for value in ("", "-1", "abc", "1:2:3:4", "12:xx"):
            with self.assertRaises(vf.FrameError):
                vf.parse_timestamp(value)

    def test_video_id_and_links(self):
        for value in (
            "https://www.youtube.com/watch?v=40fehk2f4_E",
            "https://youtu.be/40fehk2f4_E?t=12",
            "40fehk2f4_E",
        ):
            self.assertEqual(vf.extract_video_id(value), "40fehk2f4_E")
        self.assertEqual(vf.timestamp_link("40fehk2f4_E", 754.9), "https://www.youtube.com/watch?v=40fehk2f4_E&t=754s")
        with self.assertRaises(vf.FrameError):
            vf.extract_video_id("not a video")

    def test_path_safety_and_plan(self):
        self.assertEqual(vf.safe_component("../../evil"), "evil")
        self.assertEqual(vf.safe_component(".."), "video")
        plan = vf.build_plan([10.0], 2)
        self.assertEqual([row["capture_seconds"] for row in plan], [8.0, 10.0, 12.0])
        plan = vf.build_plan([10.0, 10.0], 0)
        self.assertEqual(len(plan), 1)
        with self.assertRaises(vf.FrameError):
            vf.build_plan([10.0], -1)


class LocalCaptureTest(unittest.TestCase):
    def setUp(self):
        CACHE.mkdir(parents=True, exist_ok=True)
        self.tmp = Path(tempfile.mkdtemp(prefix="test-frames-", dir=CACHE))
        self.video = self.tmp / "fixture.mp4"
        subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
                "-i", "testsrc=size=320x180:rate=10", "-t", "3", "-pix_fmt",
                "yuv420p", "-y", str(self.video),
            ],
            check=True,
            timeout=60,
        )

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_extract_frame_sidecar_and_contact_sheet(self):
        out_dir = self.tmp / "out"
        frames = vf.capture_local(
            self.video,
            vf.build_plan([0.5, 2.0]),
            out_dir,
            source_id="src-test",
            reuse=False,
        )
        self.assertEqual([f["status"] for f in frames], ["succeeded", "succeeded"])
        for frame in frames:
            path = REPO / frame["output_path"]
            self.assertTrue(path.exists())
            self.assertGreater(path.stat().st_size, 100)
            sidecar = json.loads(Path(frame["output_path"]).with_suffix(".json").read_text(encoding="utf-8"))
            self.assertEqual(sidecar["status"], "succeeded")
            self.assertEqual(sidecar["method"], "ffmpeg-local-frame")
            self.assertIn("output_sha256", sidecar)
        sheet = vf.make_contact_sheet(frames, out_dir / "sheet.jpg", "test")
        self.assertTrue((REPO / sheet["path"]).exists())
        self.assertEqual(len(sheet["frames"]), 2)

    def test_reuse_and_beyond_duration(self):
        out_dir = self.tmp / "out"
        vf.capture_local(self.video, vf.build_plan([0.5]), out_dir, source_id="src-test", reuse=False)
        reused = vf.capture_local(self.video, vf.build_plan([0.5]), out_dir, source_id="src-test", reuse=True)
        self.assertTrue(reused[0].get("reused"))
        failed = vf.capture_local(self.video, vf.build_plan([99]), out_dir, source_id="src-test", reuse=False)
        self.assertEqual(failed[0]["status"], "failed")
        self.assertIn("beyond duration", failed[0]["error"])

    def test_missing_local_video(self):
        with self.assertRaises(vf.FrameError):
            vf.capture_local(self.tmp / "missing.mp4", vf.build_plan([1]), self.tmp / "out")


if __name__ == "__main__":
    unittest.main(verbosity=2)
