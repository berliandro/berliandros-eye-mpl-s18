# Resume prompt — MPL ID S18 visual proof (pass 3)

You are resuming the **active MPL ID S18 semantic-analysis goal** in the implementer session. DeepSeek visual-review passes 1–2 are finished, but the visual-proof goal is **NOT complete**: 0 boundaries are `visually_verified`, 18 null offsets remain, and 11 context-only + 2 inconclusive reviews are unpromoted. Pass 3 is the next unit of work. This is an execution order, not a new backlog: the canonical backlog remains `docs/goals/finished/mpl-s18-visual-proof-deepseek-handoff.md` (completion gate §6a).

## Read first, in order

1. `docs/goals/active/mpl-s18-semantic-analysis-completion-goal.md`
2. `docs/goals/finished/mpl-s18-visual-proof-deepseek-handoff.md` — §3.3, §6, §8.3–§8.5
3. `analysis/reports/visual-proof-deepseek-review.md`
4. `analysis/evidence/deepseek-visual-reviews.json` — `summary`, `unresolved`, `backlog`
5. `analysis/evidence/game-offsets.json`

## Baseline to preserve

- **113 frames reviewed; 31 boundary reviews:** 18 `rejected`, 11 `context-only`, 2 `inconclusive`, **0 `used`; 0 `visually_verified`.**
- **18 null offsets:** `1037, 1043, 1058, 1061, 1063, 1064, 1066, 1072, 1079, 1083, 1085, 1087, 1088, 1092, 1093, 1099, 1101, 1104`.
- **6 pass-2 context-only:** 1042, 1051, 1056, 1067, 1078, 1102. **1 pass-2 inconclusive:** 1048. The other inconclusive is 1036.
- **4 `boundary_verified` offsets are only context-only visually:** 1062, 1084, 1106, 1107 — these are the 4 validator warnings.
- `game-offsets.json` still has **27 `boundary_verified` / 26 `pending_validation` / 19 `detected_pending_review`**. The 18 rejections are ledger-only.
- **Reviewer is DeepSeek only. You do not inspect or approve screenshots yourself. No human review.** Use the API pipeline.
- The direct DeepSeek API is out of balance (`HTTP 402`). Use **`opencode-go-session` / `deepseek-v4.1-flash`** at `http://127.0.0.1:28894`.

## Mission

Execute the frozen priority order. Stop and report at each gate. **Do not promote from a countdown or a draft screen. Only a visible `00:00` game clock with the correct pairing counts as a game-1 start.**

### P0 — 1062 (first promotion attempt)

- Source from `game-offsets.json` (1062, `src-s18-w04d02`).
- The 2465s capture shows game clock **`00:19`**; expected `00:00` is approximately **2446s**.
- Capture **2443–2449s** (3–5 frames), review as one group.
- If `00:00` is visible: set the offset to the frame's `actual_seconds` (~2446s), promote, and retire the old 2460s boundary claim.
- If not: record `context-only`; do not promote.

### P1 — 1048 pairing cleanup

- Capture ~**23490–23496s** (draft-pick expiry `03:47` from 23266s), or 4x-crop the M3 crests.
- Goal: confirm ONIC vs RRQ. No promotion from this item.

### P2a — 1084, 1106, 1107

- Already `boundary_verified`, only context-only visually. Countdowns: **15:51, 14:54, 16:02**.
- Capture draft expiry; read the draft; sample forward **5–12 minutes** for `00:00`.
- Promote only on `00:00`; otherwise context-only.

### P2b — 1042, 1051, 1078, 1102

- Same method. Countdowns: **10:26, 13:16, 14:53, 14:52**.
- Same gate.

### P3 — 18 null offsets

- Detect transcript cues first; **no blind captures**.
- Start with **1085, 1087, 1088** (remaining nulls in unvalidated sources), then **1037**, then the rest.
- Add a candidate only when a cue is found; capture 3–5 frames; review.
- Do not invent offsets.

### P4 — reconciliation

- Decide how the 18 rejections and 13 non-promotions become visible in `game-offsets.json` or a derived `visual-review-status.json`.
- Prefer a derived file unless you also update schema, validator, and tests. Do not silently change statuses.

### P5 — 1036

- Capture wider around 1303s (+5/+10/+15 min) to find the EVOS/RRQ match intro. Low priority.

## Hard rules

- Original PNG bytes + sidecars; record SHA-256, `actual_seconds`, API request id, model, provider.
- Run the smoke test before any review run.
- One group per candidate; 3–5 ordered frames.
- **Do not modify an existing group's frame list.** Adding frames forces a full re-review and orphans the old call. Add a new group instead.
- After `run --resume`, the tool rewrites the ledger and **drops the manual `backlog` object**. Patch the tool to preserve it, or re-add it immediately. Do not validate or report without it.
- Plan edits change `plan_sha256`: re-run `run --resume` after plan edits; do not hand-edit the ledger hash.
- Promotion mechanics: the validator requires `candidate_start_seconds == series.start_seconds`. Retire the old boundary claim at the old offset, add a new claim at the verified offset, and keep the old frame group as historical evidence.
- No human review; no manual image approval.
- Keep `game-offsets.json` unchanged for rejections until P4 is explicitly approved.

## Commands

```text
python tools/video_frames.py --source-id <id> --timestamps 2446 --around-seconds 3
python tools/deepseek_visual_review.py smoke --backend opencode-go-session --out analysis/evidence/deepseek-vision-smoke-opencode-go-pass3.json
python tools/deepseek_visual_review.py run --backend opencode-go-session --plan analysis/evidence/visual-review-plan.json --smoke analysis/evidence/deepseek-vision-smoke-opencode-go-pass3.json --out analysis/evidence/deepseek-visual-reviews.json --resume
python tools/recompute_visual_reviews.py --plan analysis/evidence/visual-review-plan.json --ledger analysis/evidence/deepseek-visual-reviews.json
python tools/validate_visual_reviews.py
python tools/test_visual_review_integrity.py
python tools/audit_visual_evidence.py
python tools/validate_game_offsets.py
python tools/ci_semantic_check.py
```

- Use `tools/build_pass2_groups.py` as the template for adding pass-3 groups; generalize it rather than copying its hardcoded match list.
- If a promotion changes an offset, update the report, handoff §8.3–§8.4, coverage summary, and index.

## Definition of done for this pass

- P0, P1, and P2a attempted; results recorded.
- Any promotion has a `used` boundary review with a `00:00` frame, exact hash, API id, and updated offset.
- All new frames are `reviewed`; the audit shows 0 hash mismatches.
- Ledger `summary`, `unresolved`, and `backlog` are consistent; `plan_sha256` matches.
- Validators: 0 errors; tests pass; CI semantic check passes.
- Handoff/report/coverage updated; no human review used.
- If no `00:00` is found, do not promote. Report the negative result and continue to P3/P4.

## Report back after each priority

1. What was captured/reviewed (ids, actual seconds).
2. Promotion result (offset, frame hash, API id) or why not.
3. Updated counts (frames, boundaries, rejections, context-only, inconclusive, `visually_verified`).
4. Remaining backlog (null offsets, unpromoted).
5. Validator/test output.
6. Any blocker (API, capture, schema).

This prompt covers the visual-proof phase only. After it, return to the parent goal's remaining phases; do not move the parent goal to `finished` until its own criteria are met.
