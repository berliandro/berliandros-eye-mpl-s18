---
name: mpls18-coaching-analyst
description: Working guide for Berliandro's Eye / MPL ID S18. Use for substantial analysis, database, broadcast or game-VOD transcript, evidence-ledger, browser-capture, visual-proof, coaching, documentation, or validation work; also use when a command fails, the user corrects an approach, or a durable project decision emerges. Covers canonical data rules, transcript provenance, the game-observation layer, free-model review policy, goal workflow, and verification gates.
---

# MPL S18 Coaching Analyst

This project builds a trustworthy MPL ID S18 coaching-intelligence layer on top of a canonical match database, 27 broadcast transcripts, and 107 official per-game VOD transcripts. Read this body before substantial work; load only the reference that matches the task.

## First moves

1. Read `AGENTS.md` and the active files under `docs/goals/active/`.
2. Read `analysis/index.md`, `analysis/reports/coverage-matrix.md`, and `analysis/evidence/game-transcript-manifest.json` for current state.
3. Check `git status` before editing. The worktree may contain unrelated user changes; preserve them.
4. Identify the lane: canonical data, broadcast transcript, game-VOD transcript, visual/browser capture, coaching synthesis, or validation/docs. Load the matching reference.
5. State the evidence you will use and the validation command you will run. If the task is visual, run `browse status`; if it is `paired-offline`, use the Playwright MCP browser, not the `browse` extension (see `references/browser-capture.md`).

## Non-negotiables

- Never modify raw transcripts in `analysis/sources/raw-transcripts/`, game-transcript cache files, or `data/mpl_id_s18.db`.
- Broadcast timestamps come only from `analysis/cache/timed/<source_id>.json`; raw `.txt` files have no timestamps or speaker labels. Game-VOD quotes come only from `analysis/cache/game-transcripts/<video_id>.json`. Never mix the two layers or invent a timestamp.
- Game-VOD observations use `GOBS-*` IDs and `src-game-<video_id>` sources, live in `analysis/evidence/game-observations/`, and must pass `tools/validate_game_observations.py`. They are separate from the 27-source `TOBS-*` ledger.
- Never hand-copy numbers into Markdown. Use `tools/stats_query.py` and cite `query_id` plus the snapshot hash.
- Visual claims are DeepSeek-reviewed only. Use DeepSeek V4.1 Flash Free as the baseline; LongCat 2.5 Free is a cross-check, never the sole gate. No human review, no self-approval, no promotion from draft screens, countdowns, paused HUDs, or `00:01+` clocks.
- Promote a visual boundary only for a same-frame literal `00:00` with the correct pairing.
- Do not mark a goal complete until its acceptance gate and validators pass. Do not reopen a closed goal without an explicit user instruction.
- Do not record secrets, credentials, tokens, or personal data.

## Fast map

| Need | Start here |
|---|---|
| Current state | `analysis/index.md`, `analysis/reports/coverage-matrix.md` |
| Canonical stats | `tools/stats_query.py`, `analysis/evidence/query-catalog.json` |
| Broadcast transcript | `references/transcript-pipeline.md` |
| Game-VOD transcripts | `analysis/evidence/game-transcript-manifest.json`, `references/game-vod-transcripts.md` |
| Browser capture | `references/browser-capture.md` |
| Visual proof | `references/visual-proof.md` |
| Coaching synthesis | `references/coaching-synthesis.md` |
| Validation/tooling | `references/data-and-tools.md` |
| Visual contract | `docs/goals/active/mpl-s18-visual-proof-deepseek-handoff.md` |
| Completed transcript goal | `docs/goals/finished/mpl-s18-transcript-knowledge-goal.md` |

## Gotchas

**PowerShell + `python -c` quoting.** Complex JSON, backticks, `$defs`, or nested quotes fail with `SyntaxError` or empty variable expansion. Write a temp `.py` file with the `write` tool and run it. This happened repeatedly; do not debug shell quoting for more than one attempt.

**`ruff` is not on PATH.** Use `python -m ruff check ...`. `python tools/verify.py` runs a narrow lint gate (`F401,F841,E722,E9`); fix those before claiming the suite passes.

**`browse` is not Playwright MCP.** `browse status` may report `paired-offline` because Chrome is running headless with `--disable-extensions`; do not retry the extension. Use `tools.playwright.*` (`browser_navigate`, `browser_evaluate`, `browser_take_screenshot`). YouTube navigation can exceed 60s; the page often loads anyway—check `video.readyState` before retrying.

**Timed alignment is not raw metadata.** `src-s18-w09d02` is partial. Use `cue_start/cue_end/timestamp_link = null` and `timestamp_provenance: "none"` where no trustworthy cue exists. Never invent a timestamp or speaker.

**YouTube blocks transcript IPs.** `IpBlocked`/HTTP 429 after a batch is expected. Use the `get-youtube-transcript` project's Invidious fallback with language `id`: `fetch_from_invidious(video_id, "id", True)`. Do not accept the English default for quote provenance; mark the language if you must use it.

**Segment range is not quote range.** Build the segment ledger in bounded line groups, then tighten each observation's `raw_line_start/end` and cue range to the exact quoted lines. A validator that passes the quote can still pass an overreaching claim; spot-check the claim against the quote.

**Game-VOD quotes are snippet-bound.** A game observation quote must be an exact substring of the joined transcript snippets; `snippet_start/end` and `start_s/end_s` must cover it. Run `tools/validate_game_observations.py`; do not reuse `TOBS-*` routing/validator assumptions.

**Statistic scope can silently mix tables.** `Q-GAMES`, `Q-TEAM-GAMES`, and `Q-MATCH-RESULT` have different scopes and orientations. Put only fields from the cited query into the claim. `matches.winner` and `schedule_all.winner` use different team order; map named teams before comparing side tokens.

**Subagent/visual groups stall.** Large visual-review batches (>~26 images) and oversized prompts retry indefinitely. Split into small groups (6–20 visual frames; up to 3 text sources per subagent), then verify the output files exist and run the validator before trusting a summary.

**Free models only; no new chat sessions.** Use DeepSeek V4.1 Flash Free (`opencode/deepseek-v4.1-flash-free#max`) as primary and LongCat 2.5 Free (`opencode-go/longcat-2.5-free`) only as fallback/cross-check. Do not use paid `opencode-go/deepseek-v4.1-flash` or create API sessions for image review; use subagents.

**Accepted observations need two homes.** The match report is the primary destination; `cross_destinations` must include the player/team/hero/strategy pages. Run `tools/route_transcript_observations.py`, then `tools/transcript_coverage.py`; require 0 unrouted and 0 missing IDs.

**Goal tools cannot edit closed goals.** `get_goal` may return `complete` or `null`. Files under `docs/goals/` are the durable record. Move finished goals to `docs/goals/finished/` per `AGENTS.md`; keep active work in `docs/goals/active/`.

**The `ALL MPL TRANSCRIPT` set is still not source of truth.** Its extracted text is lossy and three days are vertical-only. The 107 official game-VOD transcripts in `analysis/cache/game-transcripts/` are the new source; use `analysis/evidence/game-transcript-manifest.json`.

**Visual proof is blocked at frame level.** First visible HUD is `00:21` (1036 G1) and `00:42` (1036 G2); 1036 G1 frames `413.0–415.0s` are trophy/sponsor intro with no HUD. Do not force a promotion; report the blocker and leave §6a unchecked.

## Playbooks

### Data or statistics question

1. Use `tools/stats_query.py` with `--match`, `--player`, `--team`, `--hero`, or `--query`.
2. Capture the `query_id`, `snapshot_sha256`, `rows`, and `row_count`.
3. Put the result in the report with query provenance; do not calculate a new total from transcript text.
4. Read `references/data-and-tools.md` for the bridge and orientation rules.

### Broadcast transcript observation work

1. Build a bounded segment ledger with `tools/build_transcript_segments.py`.
2. Extract observations with exact quotes and tightened line/cue ranges.
3. Validate with `tools/validate_transcript_ledger.py`.
4. Spot-check 5–10 claims against their full segments; accept only supported claims, reject overreach, check ASR names against the player/hero lists.
5. Add accepted observations to the match report, run `tools/route_transcript_observations.py`, then `tools/transcript_coverage.py`.
6. Read `references/transcript-pipeline.md` for commands, schema fields, and routing rules.

### Game-VOD transcript observation

1. Read `analysis/evidence/game-transcript-manifest.json`; use a row with `status: ok` and its cache path.
2. Quote exact snippets; write `GOBS-*` records to `analysis/evidence/game-observations/<match>.jsonl`, with `snippet_start/end` and `start_s/end_s`.
3. Run `python tools/validate_game_observations.py --observations <ledger>`; require 0 errors, then spot-check 2–3 claims against the surrounding transcript.
4. Add the accepted records to the match report under `## Game transcript evidence`; do not route them as `TOBS-*`. Re-run `tools/build_match_evidence.py --check` and the coverage matrix.
5. Read `references/game-vod-transcripts.md`.

### Visual proof

1. Read `docs/goals/active/mpl-s18-visual-proof-deepseek-handoff.md` §6a and the current status.
2. For a known timestamp, use the Playwright MCP browser to pause/seek and screenshot the `video` element; for bulk windows use `tools/video_frames.py`. Read `references/browser-capture.md`.
3. Review with DeepSeek V4.1 Flash Free first; use LongCat 2.5 Free only as a cross-check. Preserve model, timestamp, screenshot hash, and failed captures.
4. Promote only a same-frame literal `00:00` with the correct pairing; otherwise leave `context-only`/`inconclusive`.
5. Read `references/visual-proof.md`.

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
python tools/validate_game_observations.py
python tools/build_match_evidence.py --check
python tools/build_coverage_matrix.py
python tools/transcript_coverage.py
```

`tools/verify.py` currently runs 28 suites, including the game-observation validator. For broadcast transcript changes, require 0 ledger errors, 0 routing errors, 0 missing match-report IDs, and coverage counts that match the JSON. For game-VOD changes, require 0 observation errors and a refreshed coverage matrix. For visual changes, require 0 hash mismatches and the handoff gate still honest. Report exact command output, not just “passed.”

## Models and subagents

- Text-only subagent: `opencode-go/beam-free#max` (Beam Free, max effort).
- Image/vision subagent: `opencode/deepseek-v4.1-flash-free#max` primary; `opencode-go/longcat-2.5-free` fallback/cross-check.
- Do not use paid `opencode-go/deepseek-v4.1-flash` or start new API chat sessions for image review; use subagents. Canonical visual review, if the tool is used, runs `--backend opencode-session` (DeepSeek Free).
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

- `references/transcript-pipeline.md` — read when building, reviewing, routing, or validating broadcast transcript observations.
- `references/game-vod-transcripts.md` — read when fetching, extracting, validating, or consolidating official per-game VOD transcripts and `GOBS-*` observations.
- `references/browser-capture.md` — read when using a browser to seek, capture, or screenshot a broadcast frame, or when the `browse` extension is offline.
- `references/visual-proof.md` — read when reviewing frames, running DeepSeek/LongCat checks, or touching the visual gate.
- `references/coaching-synthesis.md` — read when writing insights, team/player/hero analyses, or coaching briefs.
- `references/data-and-tools.md` — read for database queries, coverage tooling, PowerShell issues, and validation conventions.
