#!/usr/bin/env python3
"""Regression tests for yt-dlp's JavaScript runtime selection."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from link_video_source import ytdlp_command


class YtDlpCommandTests(unittest.TestCase):
    def test_prefers_deno_when_present(self):
        def which(name):
            return {"deno": "/usr/bin/deno", "node": "/usr/bin/node"}.get(name)
        cmd = ytdlp_command("abcDEF_1234", which)
        self.assertEqual(cmd[0], "yt-dlp")
        self.assertIn("--js-runtimes", cmd)
        self.assertEqual(cmd[cmd.index("--js-runtimes") + 1], "deno:/usr/bin/deno")
        self.assertEqual(cmd[-1], "https://www.youtube.com/watch?v=abcDEF_1234")

    def test_uses_node_when_deno_is_unavailable(self):
        def which(name):
            return "/opt/node/bin/node" if name == "node" else None
        cmd = ytdlp_command("abcDEF_1234", which)
        self.assertEqual(cmd[cmd.index("--js-runtimes") + 1], "node:/opt/node/bin/node")

    def test_leaves_runtime_unset_if_neither_is_installed(self):
        cmd = ytdlp_command("abcDEF_1234", lambda _name: None)
        self.assertNotIn("--js-runtimes", cmd)
        self.assertEqual(cmd[-1], "https://www.youtube.com/watch?v=abcDEF_1234")


if __name__ == "__main__":
    unittest.main(verbosity=2)
