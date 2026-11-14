---
name: mpls18-coaching-analyst
description: Working guide for Berliandro's Eye / MPL ID S18. Use for substantial analysis, database, transcript, evidence-ledger, visual-proof, coaching, documentation, or validation work; also use when a command fails, the user corrects an approach, or a durable project decision emerges. Covers canonical data rules, timed-transcript provenance, observation routing, DeepSeek-only visual review, goal workflow, and verification gates.
---

# MPL S18 Coaching Analyst

This project builds a trustworthy MPL ID S18 coaching-intelligence layer on top of a canonical match database and 27 broadcast transcripts. Read this body before substantial work; load only the reference that matches the task.

## First moves

1. Read `AGENTS.md` and the active files under `docs/goals/active/`.
2. Read `analysis/index.md` and `analysis/reports/transcript-pipeline/coverage.md` for current state.
3. Check `git status` before editing. The worktree may contain unrelated user changes; preserve them.
4. Identify the lane: canonical data, transcript extraction, visual proof, coaching synthesis, or validation/docs. Load the matching reference.
5. State the evidence you will use and the validation command you will run.

## Non-negotiables

- Never modify raw transcripts in `analysis/sources/raw-transcripts/` or `data/mpl_id_s18.db`.
- Transcript timestamps come only from `analysis/cache/timed/<source_id>.json`; raw `.txt` files have no timestamps or speaker labels.
- Never hand-copy numbers into Markdown. Use `tools/stats_query.py` and cite `query_id` plus the snapshot hash.
- Visual claims are DeepSeek-reviewed only. No human review, no self-approval, no promotion from draft screens, countdowns, paused HUDs, or `00:01+` clocks.
- Promote a visual boundary only for a same-frame literal `00:00` with the correct pairing.
- Do not mark a goal complete until its acceptance gate and validators pass. Do not reopen a closed goal without an explicit user instruction.
- Do not record secrets, credentials, tokens, or personal data.

## Fast map

| Need | Start here |
|---|---|
| Current state | `analysis/index.md`, `analysis/reports/transcript-pipeline/coverage.md` |
| Canonical stats | `tools/stats_query.py`, `analysis/evidence/query-catalog.json` |
| Transcript extraction | `references/transcript-pipeline.md` |
| Visual proof | `references/visual-proof.md` |
| Coaching synthesis | `references/coaching-synthesis.md` |
| Validation/tooling | `references/data-and-tools.md` |
| Visual contract | `docs/goals/active/mpl-s18-visual-proof-deepseek-handoff.md` |
| Completed transcript goal | `docs/goals/finished/mpl-s18-transcript-knowledge-goal.md` |

## Gotchas

**PowerShell + `python -c` quoting.** Complex JSON, backticks, `$defs`, or nested quotes fail with `SyntaxError` or empty variable expansion. Write a temp `.py` file with the `write` tool and run it. This happened repeatedly; do not debug shell quoting for more than one attempt.

**`ruff` is not on PATH.** Use `python -m ruff check ...`. `python tools/verify.py` runs a narrow lint gate (`F401,F841,E722,E9`); fix those before claiming the suite passes.

**Timed alignment is not raw metadata.** `src-s18-w09d02` is partial. Use `cue_start/cue_end/timestamp_link = null` and `timestamp_provenance: "none"` where no trustworthy cue exists. Never invent a timestamp or speaker.

**Segment range is not quote range.** Build the segment ledger in bounded line groups, then tighten each observation's `raw_line_start/end` and cue range to the exact quoted lines. A validator that passes the quote can still pass an overreaching claim; spot-check the claim against the quote.

**Statistic scope can silently mix tables.** `Q-GAMES`, `Q-TEAM-GAMES`, and `Q-MATCH-RESULT` have different scopes and orientations. Put only fields from the cited query into the claim. `matches.winner` and `schedule_all.winner` use different team order; map named teams before comparing side tokens.

**Subagent/visual groups stall.** Large visual-review batches (>~26 images) and oversized prompts retry indefinitely. Split into small groups (6–20 visual frames; up to 3 text sources per subagent), then verify the output files exist and run the validator before trusting a summary.

**Accepted observations need two homes.** The match report is the primary destination; `cross_destinations` must include the player/team/hero/strategy pages. Run `tools/route_transcript_observations.py`, then `tools/transcript_coverage.py`; require 0 unrouted and 0 missing IDs.

**Goal tools cannot edit closed goals.** `get_goal` may return `complete` or `null`. Files under `docs/goals/` are the durable record. Move finished goals to `docs/goals/finished/` per `AGENTS.md`; keep active work in `docs/goals/active/`.

**The `ALL MPL TRANSCRIPT` set is not a replacement.** The Indonesian S18 set has three vertical-only days, and the extracted text is lossy (about one-third of lines removed). Use the existing 27 raw + timed sources; do not treat the extracted text as source of truth.

**Visual proof is structurally blocked in the current broadcasts.** Feeds consistently cut in after the clock advanced (`00:12`–`03:08`). Do not force a promotion; report the blocker and leave §6a unchecked until the user changes the standard or supplies a source with `00:00`.

## Playbooks

### Data or statistics question

1. Use `tools/stats_query.py` with `--match`, `--player`, `--team`, `--hero`, or `--query`.
2. Capture the `query_id`, `snapshot_sha256`, `rows`, and `row_count`.
3. Put the result in the report with query provenance; do not calculate a new total from transcript text.
4. Read `references/data-and-tools.md` for the bridge and orientation rules.

### Transcript observation work

1. Build a bounded segment ledger with `tools/build_transcript_segments.py`.
2. Extract observations with exact quotes and tightened line/cue ranges.
3. Validate with `tools/validate_transcript_ledger.py`.
4. Spot-check 5–10 claims against their full segments; accept only supported claims, reject overreach, check ASR names against the player/hero lists.
5. Add accepted observations to the match report, run `tools/route_transcript_observations.py`, then `tools/transcript_coverage.py`.
6. Read `references/transcript-pipeline.md` for commands, schema fields, and routing rules.

### Visual proof

1. Read `docs/goals/active/mpl-s18-visual-proof-deepseek-handoff.md` §6a and the current status.
2. Capture a bounded window with `tools/video_frames.py`.
3. Review through `tools/deepseek_visual_review.py --backend opencode-go-session`; split groups to avoid stalls.
4. Preserve screenshot hashes, sidecars, API request IDs, and failed captures.
5. Promote only a same-frame `00:00` with the correct pairing; otherwise leave `context-only`/`inconclusive`.
6. Read `references/visual-proof.md`.

### Coaching synthesis

1. Start from accepted observations and the relevant page; do not re-read the whole corpus by default.
2. Reproduce the DB facts through `tools/stats_query.py`.
3. Search confirming and contradicting cases; keep one-game claims one-game.
4. Write a scoped claim with evidence, counterexample, verdict, and limits.
5. Read `references/coaching-synthesis.md`.

### Finish and validate

Run the smallest sufficient set:

```text
python tools/verify.py
python tools/ci_semantic_check.py
python tools/validate_game_offsets.py
python tools/validate_transcript_ledger.py --ledger <ledger> --segments <segments>
python tools/transcript_coverage.py
```

For transcript changes, require 0 ledger errors, 0 routing errors, 0 missing match-report IDs, and coverage counts that match the JSON. For visual changes, require 0 hash mismatches and the handoff gate still honest. Report exact command output, not just “passed.”

## Models and subagents

- Text-only subagent: `opencode-go/beam-free#max` (Beam Free, max effort).
- Image/vision subagent: `opencode/deepseek-v4.1-flash-free#max`; fallback `opencode-go/longcat-2.5-free`.
- Visual-review pipeline: `tools/deepseek_visual_review.py --backend opencode-go-session` (opencode-go `deepseek-v4.1-flash`).
- Do not use the direct DeepSeek API or a human reviewer. A direct key previously failed with HTTP 402; the OpenCode session backend is the working path.

## Maintenance

Update this skill when the user corrects you, a failure/retry loop recurs, a recorded instruction becomes wrong, a better method is verified, or a manual operation repeats.

Project skills live in `.agents/skills/`; `.opencode/` is Git-ignored in this repo, so a skill placed there is not tracked.

1. Find the root cause and ask whether the skill caused or failed to prevent it.
2. Verify a better approach.
3. Apply the admission test: changes behavior, non-obvious, likely to recur, verified or user-stated.
4. Edit in place; merge into existing entries, don't append duplicates. Delete obsolete/contradicted text.
5. Re-check size; move detail to the right reference file.
6. Never record one-offs, guesses, task progress, or secrets. Current user instructions outrank this skill.

## References

- `references/transcript-pipeline.md` — read when building, reviewing, routing, or validating transcript observations.
- `references/visual-proof.md` — read when capturing frames, running DeepSeek review, or touching the visual gate.
- `references/coaching-synthesis.md` — read when writing insights, team/player/hero analyses, or coaching briefs.
- `references/data-and-tools.md` — read for database queries, source/timed alignment, PowerShell/tooling issues, and validation conventions.
