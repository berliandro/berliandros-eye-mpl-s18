# Series offset verification queue — DeepSeek screenshot review required

**Generated from:** `analysis/evidence/game-offsets.json`  
**Manifest generated_at:** 2026-11-02T06:50:04.350835Z  
**Purpose:** Identify series candidates that need screenshot-based visual verification by DeepSeek. This is an automated-review queue, not a human-review queue.

## Current structured state

| Measure | Count |
|---|---:|
| Broadcast sources | 27 |
| Scheduled series | 72 |
| Child series rows marked `boundary_verified` | 26 |
| Child series rows marked `detected_pending_review` | 24 |
| Child series rows marked `pending_validation` | 22 |
| Series rows with null `start_seconds` | 14 |
| Series rows with null `end_seconds` | 72 |
| Source-level `validation_status = pending` | 27/27 |

**Important:** A row marked `boundary_verified` currently means the child row passed the existing caption/metadata boundary process. It does not mean that a screenshot has been reviewed by DeepSeek. All source-level aggregate statuses remain pending, so the parent/child state model requires reconciliation.

## Complete per-source queue

The three middle status columns list the match IDs in that source for each current child-row status. The final column lists match IDs whose candidate start is null.

| Source ID | Video ID | Child rows marked boundary_verified | Child rows detected_pending_review | Child rows pending_validation | Missing start |
|---|---|---|---|---|---|
| src-s18-w01d01 | 40fehk2f4_E | — | 1036 | 1037 | 1037 |
| src-s18-w01d02 | tpgvzhEO1Qc | 1038, 1039, 1040 | — | — | — |
| src-s18-w01d03 | X1yGjaXTbww | 1041 | 1042 | 1043 | 1043 |
| src-s18-w02d01 | O1vhySUmgj0 | 1045 | — | 1044 | — |
| src-s18-w02d02 | QsOUpAE-Jd8 | 1047 | 1048 | 1046 | — |
| src-s18-w02d03 | C-H_iCLxtL8 | 1050 | 1051 | 1049 | — |
| src-s18-w03d01 | 9c2wPhSYTGA | 1052, 1053 | — | — | — |
| src-s18-w03d02 | FDioYoG4ads | 1055 | 1056 | 1054 | — |
| src-s18-w03d03 | 3bAUu2t3FGI | 1059 | 1057, 1058 | — | — |
| src-s18-w04d01 | W-LSKxUkUi4 | 1060 | — | 1061 | 1061 |
| src-s18-w04d02 | -M1_bwTRlHk | 1062 | — | 1063, 1064 | 1063, 1064 |
| src-s18-w04d03 | nu3RfzQdsec | 1065 | 1066, 1067 | — | — |
| src-s18-w05d01 | TeegcSSZJbI | 1069 | — | — | — |
| src-s18-w05d02 | ykgecDVRvlI | 1071 | 1072 | 1070 | — |
| src-s18-w05d03 | YPbOKyQltIo | 1074 | — | 1073 | — |
| src-s18-w06d01 | wRRWT8fO_h0 | — | 1076, 1077, 1075 | — | — |
| src-s18-w06d02 | 5tOPeDiETK0 | 1080 | 1078 | 1079 | 1079 |
| src-s18-w06d03 | K30JsmMhQ4Q | 1081 | 1082 | 1083 | 1083 |
| src-s18-w07d01 | Nd_s3qCnRPY | 1084 | — | 1085 | 1085 |
| src-s18-w07d02 | px_HftyZBxo | — | 1086, 1088 | 1087 | 1087 |
| src-s18-w07d03 | S7ugRA3UMjo | 1091 | 1090 | 1089 | — |
| src-s18-w08d01 | 7Fk2t0Kc9-Q | 1068 | — | 1092, 1093 | 1092, 1093 |
| src-s18-w08d02 | VWScHYPW7Qc | — | 1094, 1095, 1096 | — | — |
| src-s18-w08d03 | jz3rH4xDoak | 1098 | 1097 | 1099 | 1099 |
| src-s18-w09d01 | -QC1gIugHrM | 1100 | — | 1101 | 1101 |
| src-s18-w09d02 | b9SktblDNuc | — | 1102, 1103 | 1104 | 1104 |
| src-s18-w09d03 | hY0Upem95uo | 1106, 1107 | — | 1105 | — |

## Required automated DeepSeek workflow

1. Regenerate this table from the live manifest whenever offsets change. Never maintain it manually.
2. For each series row, prepare a candidate screenshot sequence around the proposed boundary and around the transition from the previous series.
3. Capture with `tools/video_frames.py` or its validated successor. Record requested time, actual time, video ID, image path, and SHA-256.
4. Submit original screenshots to the configured image-capable DeepSeek model. Ask it to identify the visible broadcast/game context and both teams. Do not ask for hidden reasoning.
5. Persist the structured DeepSeek verdict and exact screenshot hashes in `analysis/evidence/deepseek-visual-review.jsonl`; update the target manifest.
6. A target may become visually verified only when the required elements are legible and the model returns a schema-valid `verified` verdict. Capture success or caption matching alone is insufficient.
7. If more context is needed, automatically capture more frames and retry within a bounded budget. If still unclear, mark inconclusive/quarantined. **Do not create a manual-review or human-approval state.**

## Important limitations

- This queue verifies series identity and boundaries. It does not establish individual game start/end boundaries for all 174 games; those require a separate game-level manifest and screenshot targets.
- A screenshot cannot repair the 37 unmatched transcript lines in `src-s18-w09d02`. That source remains excluded from timestamp citations until caption alignment itself is resolved.
- A series boundary screenshot does not prove a later tactical event. Objective, scoreboard, teamfight, player, draft, and macro/meso/micro claims need their own appropriately timed screenshot(s) and DeepSeek review.
- Do not use heuristic offsets for timestamp citations until the relevant boundary target is accepted by the required evidence rules.

See [the full DeepSeek visual-proof goal](../docs/goals/active/mpl-s18-visual-proof-deepseek-handoff.md) for the screenshot capture/review contract, all visual target classes, automated retry policy, tests, and definition of done.
