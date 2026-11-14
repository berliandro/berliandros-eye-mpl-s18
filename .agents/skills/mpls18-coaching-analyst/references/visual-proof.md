# Visual proof reference

Read when capturing frames, running DeepSeek review, or touching the visual gate.

## Contract

- The current contract is `docs/goals/active/mpl-s18-visual-proof-deepseek-handoff.md`, especially §6a.
- Visual reviewer: DeepSeek only. No human review, no self-approval.
- Working backend: `python tools/deepseek_visual_review.py --backend opencode-go-session` (`opencode-go/deepseek-v4.1-flash`). Do not use the direct DeepSeek API; the direct key previously failed with HTTP 402.
- Promotion requires a **literal same-frame `00:00`** with the correct team pairing.
- Draft screens, countdowns, paused HUDs, replay screens, and any `00:01+` clock are confirmation only, never promotions.
- Preserve screenshot SHA-256, sidecar hashes, requested/actual timestamps, API request IDs, failed captures, and review dispositions.
- Do not modify the canonical database or raw transcripts.

## Current status

As of 2026-11-14: 0 boundaries are `visually_verified`; §6a box 1 is unchecked. `analysis/evidence/visual-review-status.json` is the derived status. Multiple 1-second sweeps found the broadcast cutting in after the clock advanced (`00:12`–`03:08`), so the strict `00:00` gate is blocked by the available broadcasts. Read the handoff for the current counts; do not quote stale counts.

## Capture

```text
python tools/video_frames.py \
  --source-id src-s18-w01d01 \
  --timestamps 1303,1310,1320 \
  --out-dir analysis/cache/video-frames/pass3/<label>
```

A failed capture is not a reviewed frame. Keep the sidecar and failure reason.

## Add a review group

```text
python tools/add_visual_group.py \
  --group-id G-P3-<match>-<label> \
  --boundary-id B-P3-<match>-<candidate> \
  --match-id <match_id> \
  --source-id <source_id> \
  --candidate-seconds <seconds> \
  --team-a <TEAM> --team-b <TEAM> \
  --capture-dir <capture_dir> \
  --promotion-requires-same-frame \
  --claim "<claim>" \
  --question "<exact visual question>"
```

Use `--no-boundary --related-to-boundary <id>` for probe-only sweeps. Do not let a probe at a different timestamp contradict the primary pairing; related frames may support, never reject, the candidate.

## Review

```text
python tools/deepseek_visual_review.py run \
  --backend opencode-go-session \
  --plan analysis/evidence/visual-review-plan.json \
  --smoke analysis/evidence/deepseek-vision-smoke-opencode-go-pass3.json \
  --out analysis/evidence/deepseek-visual-reviews.json \
  --resume
```

Then:

```text
python tools/recompute_visual_reviews.py
python tools/validate_visual_reviews.py
python tools/audit_visual_evidence.py
python tools/validate_game_offsets.py
```

Large groups stall. Prefer 6–20 frames per group; 21–26 can work but may stall; 34-frame groups repeatedly hung. If a group stalls, split it, remove the oversized group from the plan, delete the superseded capture directory, and retry. Do not add an oversized group and wait indefinitely.

After `run --resume`, verify `ledger.backlog` still exists. If the run dropped it, restore it from the prior ledger/plan before claiming completion. Do not lose the no-candidate null list or reviewed-but-unpromoted list.

## Promotion discipline

Before any promotion, answer:

1. Is the clock literally `00:00` in this frame?
2. Are the claimed teams legible in the same frame?
3. Is the timestamp backed by the exact screenshot hash and sidecar?
4. Is the visual reviewer DeepSeek, with a valid request ID?
5. Does the handoff still have §6a box 1 unchecked?

If any answer is no, leave the boundary `context-only` or `inconclusive`. Never promote from a draft screen, countdown, paused HUD, or a later clock.

## Goal status

The visual goal remains separate from the transcript goal and is **not complete** until §6a is fully checked. Do not archive or mark it complete because the transcript pipeline finished. If the strict gate cannot be met from available sources, report the evidence-backed blocker and ask the user to change the standard or provide a source; do not force a promotion.
