#!/usr/bin/env python3
"""Adversarial tests for the DeepSeek visual-review validator.

Run with:
    python -m pytest tools/test_visual_review_integrity.py -v
or:
    python tools/test_visual_review_integrity.py
"""
from __future__ import annotations

import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_visual_reviews as v  # noqa: E402
import deepseek_visual_review as dvr  # noqa: E402

HASH = hashlib.sha256(b"frame-bytes").hexdigest()
SMOKE_HASH = hashlib.sha256(b"smoke-bytes").hexdigest()


def fixture() -> tuple[dict, dict, dict, dict]:
    frame = {
        "frame_id": "F1",
        "group_id": "G1",
        "path": "frame.png",
        "sidecar_path": "frame.json",
        "screenshot_sha256": HASH,
        "review_status": "reviewed",
        "reviewer": "deepseek",
        "model": "deepseek-v4.1-flash",
        "provider": "opencode-go",
        "transport": "opencode-session",
        "reviewed_at": "2026-11-02T12:00:00+00:00",
        "api_request_id": "msg_1",
        "disposition": "used",
        "confidence": "high",
        "observation": "A clearly visible scoreboard reads M71 GAME 1.",
        "limitations": "Still image only.",
        "capture_status": "succeeded",
    }
    boundary = {
        "boundary_id": "B1",
        "match_detail_id": "1",
        "source_id": "S1",
        "team_a": "A",
        "team_b": "B",
        "candidate_start_seconds": 10,
        "frame_group": "G1",
        "frame_ids": ["F1"],
        "frame_sha256": [HASH],
        "related_frame_ids": [],
        "related_frame_sha256": [],
        "series_pairing": {"disposition": "used", "evidence": "A and B visible", "confidence": "high"},
        "game1_start": {"disposition": "used", "evidence": "draft visible", "confidence": "high"},
        "disposition": "used",
        "status_effect": "visual_confirmation",
        "observation": "A and B are visible in the draft.",
        "limitations": "Still image only.",
    }
    ledger = {
        "schema_version": 1,
        "generated_at": "2026-11-02T12:00:00+00:00",
        "reviewer": "deepseek",
        "model": "deepseek-v4.1-flash",
        "provider": "opencode-go",
        "transport": "opencode-session",
        "review_mode": "api-pixel-inspection-only",
        "human_review": False,
        "smoke_test": {
            "status": "passed",
            "reviewer": "deepseek",
            "model": "deepseek-v4.1-flash",
            "image_sha256": SMOKE_HASH,
            "api_request_id": "msg_smoke",
            "checks": {
                "text_deepseek_vision": True,
                "text_smoke_test_4729": True,
                "shape_orange": True,
                "shape_bottom_right": True,
            },
        },
        "frames": [frame],
        "boundary_reviews": [boundary],
        "summary": {
            "frames_reviewed": 1,
            "frame_dispositions": {"used": 1, "rejected": 0, "context-only": 0, "inconclusive": 0},
            "boundary_reviews": 1,
            "boundary_dispositions": {"used": 1, "rejected": 0, "context-only": 0, "inconclusive": 0},
            "candidate_rejections": 0,
            "visual_confirmations": 1,
        },
    }
    plan = {
        "groups": [{
            "group_id": "G1",
            "frames": [{"frame_id": "F1", "path": "frame.png"}],
        }],
        "boundary_claims": [{
            "boundary_id": "B1",
            "match_detail_id": "1",
            "source_id": "S1",
            "team_a": "A",
            "team_b": "B",
            "candidate_start_seconds": 10,
            "frame_group": "G1",
        }],
    }
    offsets = {
        "sources": {
            "S1": {
                "series": [{
                    "match_detail_id": "1",
                    "team_a": "A",
                    "team_b": "B",
                    "start_seconds": 10,
                    "status": "detected_pending_review",
                }]
            }
        }
    }
    return ledger, plan, offsets, {}


class VisualReviewIntegrityTest(unittest.TestCase):
    def assert_valid(self, ledger, plan, offsets, visual=None, frame_root=None):
        errors, _ = v.validate_ledger(ledger, visual or {}, offsets, plan, frame_root=frame_root)
        self.assertEqual(errors, [], msg="\n".join(errors))

    def assert_invalid(self, ledger, plan, offsets, needle, visual=None, frame_root=None):
        errors, _ = v.validate_ledger(ledger, visual or {}, offsets, plan, frame_root=frame_root)
        self.assertTrue(any(needle.lower() in e.lower() for e in errors),
                        msg=f"expected error containing {needle!r}, got {errors}")

    def test_valid_fixture_passes(self):
        ledger, plan, offsets, _ = fixture()
        self.assert_valid(ledger, plan, offsets)

    def test_human_reviewer_rejected(self):
        ledger, plan, offsets, _ = fixture()
        bad = copy.deepcopy(ledger)
        bad["frames"][0]["reviewer"] = "human"
        self.assert_invalid(bad, plan, offsets, "reviewer is not 'deepseek'")

    def test_missing_api_request_id_rejected(self):
        ledger, plan, offsets, _ = fixture()
        bad = copy.deepcopy(ledger)
        bad["frames"][0]["api_request_id"] = ""
        self.assert_invalid(bad, plan, offsets, "missing api_request_id")

    def test_empty_observation_rejected(self):
        ledger, plan, offsets, _ = fixture()
        bad = copy.deepcopy(ledger)
        bad["frames"][0]["observation"] = ""
        self.assert_invalid(bad, plan, offsets, "observation is empty")

    def test_invalid_hash_rejected(self):
        ledger, plan, offsets, _ = fixture()
        bad = copy.deepcopy(ledger)
        bad["frames"][0]["screenshot_sha256"] = "not-a-hash"
        self.assert_invalid(bad, plan, offsets, "screenshot_sha256")

    def test_invalid_confidence_rejected(self):
        ledger, plan, offsets, _ = fixture()
        bad = copy.deepcopy(ledger)
        bad["frames"][0]["confidence"] = "certain"
        self.assert_invalid(bad, plan, offsets, "invalid confidence")

    def test_invalid_timestamp_rejected(self):
        ledger, plan, offsets, _ = fixture()
        bad = copy.deepcopy(ledger)
        bad["frames"][0]["reviewed_at"] = "yesterday"
        self.assert_invalid(bad, plan, offsets, "reviewed_at")

    def test_failed_capture_not_rejected(self):
        ledger, plan, offsets, _ = fixture()
        bad = copy.deepcopy(ledger)
        bad["frames"][0]["capture_status"] = "failed"
        bad["frames"][0]["disposition"] = "used"
        self.assert_invalid(bad, plan, offsets, "failed capture must be disposition=rejected")

    def test_used_boundary_without_game1_start_rejected(self):
        ledger, plan, offsets, _ = fixture()
        bad = copy.deepcopy(ledger)
        bad["boundary_reviews"][0]["game1_start"]["disposition"] = "context-only"
        self.assert_invalid(bad, plan, offsets, "used boundary without used game-1 start")

    def test_candidate_rejection_against_verified_boundary_rejected(self):
        ledger, plan, offsets, _ = fixture()
        bad = copy.deepcopy(ledger)
        bad["boundary_reviews"][0]["disposition"] = "rejected"
        bad["boundary_reviews"][0]["status_effect"] = "candidate_rejected"
        bad["boundary_reviews"][0]["series_pairing"]["disposition"] = "rejected"
        bad["boundary_reviews"][0]["game1_start"]["disposition"] = "rejected"
        bad["summary"]["boundary_dispositions"] = {"used": 0, "rejected": 1, "context-only": 0, "inconclusive": 0}
        bad["summary"]["candidate_rejections"] = 1
        bad["summary"]["visual_confirmations"] = 0
        offsets2 = copy.deepcopy(offsets)
        offsets2["sources"]["S1"]["series"][0]["status"] = "boundary_verified"
        self.assert_invalid(bad, plan, offsets2, "visual review rejects a candidate")

    def test_summary_mismatch_rejected(self):
        ledger, plan, offsets, _ = fixture()
        bad = copy.deepcopy(ledger)
        bad["summary"]["frames_reviewed"] = 2
        self.assert_invalid(bad, plan, offsets, "summary.frames_reviewed")

    def test_plan_missing_frame_rejected(self):
        ledger, plan, offsets, _ = fixture()
        bad_plan = copy.deepcopy(plan)
        bad_plan["groups"][0]["frames"].append({"frame_id": "F2", "path": "frame2.png"})
        self.assert_invalid(ledger, bad_plan, offsets, "plan frames missing")

    def test_historical_used_frame_missing_rejected(self):
        ledger, plan, offsets, _ = fixture()
        visual = {"frames": [{
            "frame_id": "H1",
            "review_status": "reviewed",
            "disposition": "used",
            "output_sha256": HASH,
        }]}
        self.assert_invalid(ledger, plan, offsets, "no DeepSeek review record", visual=visual)

    def test_local_hash_mismatch_rejected(self):
        ledger, plan, offsets, _ = fixture()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "frame.png").write_bytes(b"different-bytes")
            self.assert_invalid(ledger, plan, offsets, "local screenshot hash mismatch", frame_root=root)

    def test_derived_frame_requires_provenance(self):
        ledger, plan, offsets, _ = fixture()
        bad = copy.deepcopy(ledger)
        bad["frames"][0]["derived_from_path"] = "original.png"
        self.assert_invalid(bad, plan, offsets, "derived_from_sha256")

    def test_smoke_failure_rejected(self):
        ledger, plan, offsets, _ = fixture()
        bad = copy.deepcopy(ledger)
        bad["smoke_test"]["checks"]["shape_bottom_right"] = False
        self.assert_invalid(bad, plan, offsets, "shape_bottom_right")

    def test_human_review_mode_rejected(self):
        ledger, plan, offsets, _ = fixture()
        bad = copy.deepcopy(ledger)
        bad["human_review"] = True
        self.assert_invalid(bad, plan, offsets, "human_review must be false")


class VisualReviewDecisionTest(unittest.TestCase):
    """Regression tests for deterministic boundary decisions."""

    @staticmethod
    def decide(answer: dict, candidate: int, team_a="TLID", team_b="NAVI") -> dict:
        boundary = {
            "boundary_id": "B1",
            "match_detail_id": "1",
            "source_id": "S1",
            "team_a": team_a,
            "team_b": team_b,
            "candidate_start_seconds": candidate,
            "claim": "game 1 boundary",
            "frame_group": "G1",
        }
        output = {
            "observation": answer.get("observation", ""),
            "visible_text": answer.get("visible_text", []),
            "answers": answer,
            "model_disposition": "context-only",
            "confidence": "high",
        }
        records = [{"frame_id": "F1", "screenshot_sha256": "h"}]
        return dvr.decide_boundary(boundary, [output], [], records, [])

    def test_later_game_rejects_game1(self):
        result = self.decide({
            "scene_type": "gameplay",
            "teams": "BTR vs ONIC",
            "match_label": "MATCH 47 - GAME 2",
            "clock_or_countdown": "10:39",
            "observation": "Live gameplay in game 2.",
        }, candidate=17077, team_a="BTR", team_b="ONIC")
        self.assertEqual(result["game1_start"]["disposition"], "rejected")
        self.assertIn("GAME 2", result["game1_start"]["evidence"])
        self.assertEqual(result["disposition"], "rejected")

    def test_multi_match_schedule_is_not_a_contradiction(self):
        result = self.decide({
            "scene_type": "pre-match",
            "teams": "VITALITY vs DEWA UNITED (match 10); match 9 crests illegible",
            "match_label": "MATCH 9 | BO3 and MATCH 10 | BO3",
            "clock_or_countdown": "09:27",
            "observation": "Pre-show schedule with two match cards.",
        }, candidate=300)
        self.assertNotEqual(result["series_pairing"]["disposition"], "rejected")
        self.assertEqual(result["game1_start"]["disposition"], "rejected")
        self.assertEqual(result["disposition"], "rejected")

    def test_300s_pre_show_rejects_game1(self):
        result = self.decide({
            "scene_type": "pre-match",
            "teams": "DEWA vs AE",
            "match_label": "MATCH 14",
            "clock_or_countdown": "09:32",
            "observation": "Pre-show countdown over a feature clip.",
        }, candidate=300, team_a="DEWA", team_b="AE")
        self.assertEqual(result["game1_start"]["disposition"], "rejected")
        self.assertEqual(result["disposition"], "rejected")

    def test_series_intro_with_draft_countdown_stays_context_only(self):
        result = self.decide({
            "scene_type": "pre-match",
            "teams": "VITALITY vs GEEK",
            "match_label": "GAME 1",
            "clock_or_countdown": "DRAFT PICK IN 10:26",
            "observation": "Series intro with a draft-pick countdown.",
        }, candidate=10608, team_a="BTR", team_b="GEEK")
        self.assertNotEqual(result["game1_start"]["disposition"], "rejected")
        self.assertEqual(result["disposition"], "context-only")

    def test_draft_screen_is_not_promotion(self):
        result = self.decide({
            "scene_type": "draft",
            "teams": "DEWA vs GEEK",
            "match_label": "MATCH 1 - GAME 1",
            "clock_or_countdown": "none visible",
            "visible_00_00": False,
            "observation": "Draft/player-cam screen with both team names; no game clock.",
        }, candidate=12043, team_a="DEWA", team_b="GEEK")
        self.assertEqual(result["game1_start"]["disposition"], "context-only")
        self.assertEqual(result["disposition"], "context-only")
        self.assertIn("confirmation only", result["game1_start"]["evidence"])

    def test_short_alias_does_not_match_inside_words(self):
        self.assertEqual(dvr.find_teams("Aerial in-game map with an AEGIS banner"), set())
        self.assertEqual(dvr.find_teams("AE vs BTR"), {"AE", "BTR"})

    def test_related_probe_cannot_reject_primary_pairing(self):
        boundary = {
            "boundary_id": "B1",
            "match_detail_id": "1084",
            "source_id": "S1",
            "team_a": "GEEK",
            "team_b": "BTR",
            "candidate_start_seconds": 2043,
            "claim": "game 1 boundary",
            "frame_group": "G1",
        }
        primary = {
            "observation": "Pre-match stage with a DRAFT PICK IN countdown.",
            "answers": {
                "scene_type": "pre-match",
                "teams": "none",
                "match_label": "GAME 1",
                "clock_or_countdown": "DRAFT PICK IN 15:56",
            },
        }
        related = {
            "observation": "Live gameplay at 00:19 with GEEK vs BTR.",
            "answers": {
                "scene_type": "gameplay",
                "teams": "GEEK vs BTR",
                "match_label": "GAME 1",
                "clock_or_countdown": "00:19",
            },
        }
        result = dvr.decide_boundary(boundary, [primary], [related],
                                     [{"frame_id": "F1", "screenshot_sha256": "h"}], [])
        self.assertNotEqual(result["series_pairing"]["disposition"], "rejected")
        self.assertEqual(result["disposition"], "context-only")
        self.assertNotEqual(result["game1_start"]["disposition"], "used")


if __name__ == "__main__":
    unittest.main(verbosity=2)
