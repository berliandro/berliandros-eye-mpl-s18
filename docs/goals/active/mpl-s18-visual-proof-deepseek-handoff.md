# MPL ID S18 Visual Proof — DeepSeek Handoff

> **GOAL STATUS: ACTIVE — NOT COMPLETE.** Passes 1–2 are finished; pass 3 has been executed exhaustively across all 72 series. **0** boundaries are `visually_verified`; **10** no-candidate waivers, **41** context-only, **1** inconclusive, and **20** rejected reviews are explicitly unpromoted. The completion gate is **§6a**; only the visible-`00:00` promotion box is unchecked. Do not archive this handoff or close the goal.

**Canonical file.** This is the sole dedicated visual-proof backlog and second-stage handoff. Do not scatter separate visual-review TODO lists across other Markdown files; ordinary reports may link to this one.

**Reviewer:** DeepSeek (second stage). The first-stage executor does not have visual-inspection capability and must not approve/reject visual claims.

**Status:** Passes 1–2 complete; **pass 3 executed but goal not complete** (2026-11-03). Current ledger: **966 frames, 62 boundary reviews** — 20 rejected, 41 context-only, 1 inconclusive, **0 promoted to `visually_verified`**. All 18 original null offsets are covered by 8 reviewed candidates (context-only/rejected) and 10 documented no-candidate waivers. All 23 remaining boundary-verified/unreviewed series have now been sampled; the derived status shows **0 not-reviewed** series. No same-frame `00:00` was found anywhere. Only §6a box 1 remains unchecked.

---

## 1. Purpose

Consolidate every screenshot target that requires pixel-level interpretation. Each target has source/game/timestamp/image information, the exact unresolved visual question, and acceptance criteria. DeepSeek must independently review the underlying screenshots and append fresh records. Historical reviewer labels (e.g., "OpenCode multimodal review") are not DeepSeek reviews and must not be relabelled as such.

## 2. Rules

1. A captured frame is `captured`, not `visually_verified`.
2. A reviewed still image supports only what is visibly present at that instant.
3. Temporal claims require timestamped, chronologically ordered screenshot sequences.
4. OCR/CV output is machine-extracted and unverified until DeepSeek checks it against the original screenshot.
5. Rejected frames and failed captures must be recorded; never silently omitted.
6. No human screenshot inspection, manual visual approval, human-review queue, or human escalation is permitted.
7. If automated retries and additional screenshots do not resolve a question, mark it inconclusive/rejected/quarantined and continue.

## 3. Existing visual assets

### 3.1 Pilot frames (from `analysis/evidence/visual-review.json`)

| Frame ID | Source | Video | Requested | Actual | Disposition | Visual question | DeepSeek disposition |
|---|---|---|---|---:|---:|---|---|---|
| VF-1037-replay | src-s18-w01d01 | 40fehk2f4_E | 04:13:50 | 04:13:51.476 | used | Does the Instant Replay banner confirm an AE play labelled "AE AFFAN ... HAS SLAIN" near the base? | **context-only.** Banner says INSTANT REPLAY; AFFAN is visible; no "AE AFFAN" label and no "HAS SLAIN" text. |
| VF-1037-base | src-s18-w01d01 | 40fehk2f4_E | 04:14:05 | 04:14:06.335 | used | Game clock 21:08; AE 17-15 NAVI; AE gold 63.9K vs NAVI 65.8K; AE defending base. Confirm all values legible. | **context-only.** Clock, score, and both gold values confirmed; base defense is not visible (lane/river teamfight, no base structures). |
| VF-1037-post | src-s18-w01d01 | 40fehk2f4_E | 04:16:10 | 04:16:11.480 | used-as-context-only | Post-game player-camera shot; confirms game ended, not fight sequence. | **context-only.** Stage/player-camera shot; no in-game fight. Capped at context-only by plan policy. |
| VF-1037-041545 | src-s18-w01d01 | 40fehk2f4_E | 04:15:45 | (failed) | not-used | Frame failed (player not ready/actual time drift); not used. | **rejected.** Sidecar status failed and actual time is null; the image is an unrelated ad frame, so it cannot support a timestamped claim. |
| VF-1107-early | src-s18-w09d03 | hY0Upem95uo | 07:04:50 | 07:04:51.481 | used | Game clock 5:08; TLID 14.0K vs ONIC 13.1K; top-lane fight. Confirm all values. | **used.** Clock 05:08, TLID 14.0K, ONIC 13.1K; active fight visible. |
| VF-1107-item | src-s18-w09d03 | hY0Upem95uo | 07:05:10 | 07:05:10.920 | used | Game clock 5:27; TLID 15.3K vs ONIC 13.6K; "FIRST ITEM PRIORITY DRICHEL" overlay. Confirm. | **used.** Clock 05:27, TLID 15.3K, ONIC 13.6K; overlay text confirmed. |
| VF-1107-mid | src-s18-w09d03 | hY0Upem95uo | 07:12:40 | 07:12:41.281 | used | Game clock 12:58; TLID 40.6K vs ONIC 34.7K; "SEASON 18 40 LORD KILL KEVIN" milestone. Confirm this is a season milestone, not current objective. | **context-only.** Clock 12:58, ONIC 34.7K, and the season milestone confirmed; pixels read TLID **40.8K**, not 40.6K. |
| VF-1107-070620 | src-s18-w09d03 | hY0Upem95uo | 07:06:20 | 07:06:20.902 | rejected | YouTube Premium promotional overlay, not gameplay. Rejected. | **rejected.** YouTube Premium promotional card confirmed; not usable as gameplay evidence. |

### 3.2 Player deep-analysis frames (captured and reviewed)

| Frame | Source | Video | Timestamp | Purpose | DeepSeek disposition |
|---|---|---|---|---|---|
| Alberttt draft | src-s18-w01d01 | 40fehk2f4_E | 00:42:18 | Draft screen for EVOS top-3 "identity draft" (Paquito/Eudora/Melissa). Sidecar: `src-s18-w01d01_at_004218_000_p000.json`. | **context-only.** Produced `DRAFT IDENTITY`/`DRAFT DNA` analysis segment; Paquito/Eudora/Melissa confirmed; not a live draft or a specific series/game. |

### 3.3 Uncertain series/game boundaries (from game-offsets.json)

All heuristic and candidate-detected boundaries need DeepSeek visual confirmation before they can be marked `boundary_verified`. Priority targets:

| Source | Series | Heuristic start | Status | Visual question |
|---|---|---:|---|---|
| src-s18-w01d01 | 1036 (EVOS vs RRQ) | 1303s | boundary_verified (med) | Confirm series start and game 1 boundary. |
| src-s18-w01d01 | 1037 (NAVI vs AE) | null | pending_validation | Null offset; needs boundary detection. |
| src-s18-w09d03 | 1105 (AE vs EVOS) | 300s | pending_validation | Low confidence; needs verification. |
| src-s18-w09d03 | 1106 (NAVI vs BTR) | 24389s | detected_pending_review | Verify boundary. |
| src-s18-w09d03 | 1107 (ONIC vs TLID) | 23893s | boundary_verified (med) | Confirm (pilot quotes start at 24828s; series likely starts earlier). |
| src-s18-w04d02 | 1062 (DEWA vs ONIC) | 4679s | detected_pending_review | Low confidence; verify. |
| src-s18-w04d02 | 1063 (EVOS vs BTR) | null | pending_validation | Null offset. |
| src-s18-w04d02 | 1064 (AE vs GEEK) | null | pending_validation | Null offset. |

All `pending_validation` and `detected_pending_review` entries need DeepSeek review before promotion to `boundary_verified`. See `analysis/evidence/game-offsets.json` for the full list.

> **Snapshot note (2026-11-02).** The offsets in the table above are from an earlier snapshot. The current `game-offsets.json` has 1036 at 1303s `detected_pending_review`, 1062 at 2460s `boundary_verified`, 1106 at 13093s `boundary_verified` (not 24389s), and 1075 stored as RRQ vs DEWA (not DEWA vs RRQ). DeepSeek reviewed the current offsets; the 24389s capture shows 1107 ONIC vs TLID instead. Current counts are 27 `boundary_verified`, 26 `pending_validation`, and 19 `detected_pending_review` (72 series total). See §8.3 for the corrected findings.
>
> **Pass 2 note (2026-11-02).** Pass 2 captured and reviewed the 20 non-null candidates that pass 1 did not cover: 1042, 1044, 1046, 1048, 1049, 1051, 1054, 1056, 1067, 1070, 1073, 1078, 1082, 1089, 1090, 1095, 1096, 1097, 1102, 1103. None was promoted. Thirteen were rejected, six are context-only series intros/desks/interviews, and one (1048) is inconclusive.

## 4. Capture instructions for DeepSeek stage

For each target:
1. Use `tools/video_frames.py --source-id <id> --timestamps <t> --around-seconds 4 --contact-sheet` to capture ordered frames.
2. Record sidecar metadata (canonical URL, timestamp link, requested/actual time, method, versions, output hash, errors).
3. Capture enough ordered frames to answer the bounded question; if still images cannot prove the claimed continuous event, mark inconclusive.
4. DeepSeek reviews the screenshot(s) and appends a review record with: screenshot hash, disposition (used/rejected/inconclusive), and concise evidence rationale.
5. Rejected frames and failed captures must be recorded.

## 5. DeepSeek review contract

For each screenshot target, DeepSeek must produce:
- `review_status: reviewed` (only after actual pixel inspection)
- `reviewer: deepseek`
- `reviewed_at: <timestamp>`
- `disposition: used | rejected | context-only | inconclusive`
- `observation`: concise description of what is visibly present
- `confidence`: high / med / low
- `limitations`: what the frame cannot prove

## 6. Pass 1–2 review criteria (met)

- [x] Every `visually_reviewed` boundary has a valid DeepSeek review record tied to exact screenshot hash(es). No boundary was promoted to `visually_reviewed`; every reviewed boundary has a record.
- [x] Every `used` frame in `visual-review.json` has a DeepSeek review record. The historical used/context-only frames are linked by `historical_frame_id` and screenshot hash.
- [x] No frame is marked `reviewed` without actual DeepSeek pixel inspection. All 113 reviewed frames have a parsed API response id and screenshot hash.
- [x] Rejected frames and failed captures are recorded. `VF-1037-041545`, `VF-1107-070620`, and three sidecar-only capture failures are recorded.
- [x] The handoff file is updated with DeepSeek dispositions. See §3.1, §3.3 snapshot note, and §8.
- [x] All non-verified boundary candidates reviewed. Pass 2 reviewed the 20 remaining non-null candidates; no boundary was promoted. The 18 null offsets are not candidates (no capture target) and remain unresolved in §8.4.

### 6a. Goal completion gate (currently UNMET)

Passes 1–2 only completed the review of existing candidates. The visual-proof goal is **not** complete until:

- [ ] At least one boundary is promoted to `visually_verified` from a visible `00:00` game clock with the correct pairing.
- [x] All 18 original null offsets have a reviewed candidate or a documented "no candidate" waiver: 8 reviewed candidates (1037/1085/1087/1088/1072/1079/1083/1101; context-only or rejected) and 10 waivers (1043/1058/1061/1063/1064/1066/1092/1093/1099/1104). No promotion.
- [x] All context-only and inconclusive boundaries are explicitly accepted as unpromoted in this report: 41 context-only and 1 inconclusive (1048); 1036 moved from inconclusive to context-only after the P5 wide probe.
- [x] The 20 rejected candidate offsets are reflected in the derived `analysis/evidence/visual-review-status.json` (`rejected_candidates`) without silently changing canonical statuses.
- [x] The final report and handoff state the goal is **not complete** because no boundary is `visually_verified`; the first box remains unchecked.

**Do not archive this handoff or close the goal while any box above is unchecked.**

## 7. Cross-references

- `analysis/evidence/visual-review.json` — existing frame dispositions (historical, not DeepSeek)
- `analysis/evidence/deepseek-visual-reviews.json` — DeepSeek review ledger (canonical second-stage output)
- `analysis/evidence/visual-review-plan.json` — frame groups, questions, and boundary claims
- `analysis/evidence/deepseek-vision-smoke-opencode-go.json` — smoke test used for pass 1
- `analysis/evidence/deepseek-vision-smoke-opencode-go-pass2.json` — smoke test used for pass 2
- `analysis/evidence/visual-review-status.json` — derived P4 reconciliation (rejections, waivers, unpromoted reviews)
- `analysis/evidence/visual-evidence-audit.json` — frame/sidecar/hash audit
- `analysis/evidence/game-offsets.json` — series/game boundary offsets
- `analysis/evidence/timed-alignment.json` — caption alignment coverage
- `analysis/reports/visual-proof-deepseek-review.md` — DeepSeek findings and unresolved items
- `tools/video_frames.py` — frame capture tool
- `tools/deepseek_visual_review.py` — DeepSeek API/session reviewer
- `tools/build_pass2_groups.py` — appends captured pass-2 candidate groups to the plan
- `tools/recompute_visual_reviews.py` — deterministic re-evaluation from stored API outputs
- `tools/validate_visual_reviews.py` — ledger validator
- `tools/test_visual_review_integrity.py` — adversarial validator tests
- `tools/audit_visual_evidence.py` — frame-cache audit
- `analysis/reports/unvalidated-sources.md` — unvalidated sources
- `analysis/reports/coverage-summary.md` — current coverage state

## 8. DeepSeek review results (2026-11-02)

### 8.1 Execution and evidence

- Reviewer: DeepSeek only. No human visual-review queue, manual approval, or escalation was used.
- Review ledger: `analysis/evidence/deepseek-visual-reviews.json` (113 frame records, 31 boundary reviews, 45 API calls).
- Report: `analysis/reports/visual-proof-deepseek-review.md`.
- Plan: `analysis/evidence/visual-review-plan.json` (45 frame groups, 113 frames, 31 boundary claims).
- Audit: `analysis/evidence/visual-evidence-audit.json`.
- Pass 2 capture: 20 candidates × 3 ordered frames (60 frames), all captures succeeded; actual times are within about 5s of the requested offsets.
- Smoke tests:
  - Direct DeepSeek API `deepseek-flash` (text+image): passed the synthetic known-content image test, then hit `HTTP 402 Insufficient Balance`.
  - OpenCode-hosted `deepseek-v4.1-flash-free`: passed the same test, then hit the free daily limit.
  - OpenCode-hosted `deepseek-v4.1-flash` (opencode-go), pass 1: passed the same test and completed the remaining pass-1 review.
  - OpenCode-hosted `deepseek-v4.1-flash` (opencode-go), pass 2: passed the same test and completed all 60 pass-2 frames.
  - Records: `analysis/evidence/deepseek-vision-smoke.json`, `analysis/evidence/deepseek-vision-smoke-opencode.json`, `analysis/evidence/deepseek-vision-smoke-opencode-go.json`, `analysis/evidence/deepseek-vision-smoke-opencode-go-pass2.json`.
- Model provenance: 7 frames were reviewed by `deepseek-v4.1-flash-free` before the free daily limit; 106 frames were reviewed by `deepseek-v4.1-flash` (opencode-go). Both are DeepSeek vision models. Every frame record has a provider, model, API request id, screenshot SHA-256, and timestamp.
- No frame was marked `reviewed` without a parsed DeepSeek API response.

### 8.2 Frame dispositions

Total: **113 frames** — 53 `used`, 29 `context-only`, 29 `inconclusive`, 2 `rejected`.

| Stage | Frames | `used` | `context-only` | `inconclusive` | `rejected` |
|---|---:|---:|---:|---:|---:|
| Pass 1 | 53 | 19 | 18 | 14 | 2 |
| Pass 2 | 60 | 34 | 11 | 15 | 0 |
| **Total** | **113** | **53** | **29** | **29** | **2** |

`used` here means the frame is usable evidence for its bounded group claim. It does **not** mean the frame supports a boundary promotion. Pass 2 has no `rejected` frames because the frame-level rule only checks whether the claimed pairing is visible; contradictions are recorded at boundary level.

Key corrections to historical labels:

| Frame | Historical claim | DeepSeek finding |
|---|---|---|
| VF-1037-replay | Instant Replay banner confirms "AE AFFAN ... HAS SLAIN" | Banner says INSTANT REPLAY and AFFAN is visible, but neither "AE AFFAN" nor "HAS SLAIN" is visible. `context-only`. |
| VF-1037-base | AE defending its base | Clock 21:08, AE 17-15 NAVI, and gold 63.9K/65.8K confirmed; base defense is not visible. `context-only`. |
| VF-1107-mid | TLID 40.6K | Pixels read TLID **40.8K**; ONIC 34.7K and the "SEASON 18 40 LORD KILL KEVIN" season milestone are confirmed. `context-only`. |
| VF-1037-041545 | failed capture | Confirmed failed sidecar and null actual time; the image is an unrelated advertisement frame. `rejected`. |
| VF-1107-070620 | YouTube Premium overlay | Confirmed promotional card; `rejected` as gameplay evidence. |
| Alberttt draft | EVOS top-3 identity draft | Produced `DRAFT IDENTITY` / `DRAFT DNA` analysis segment; Paquito/Eudora/Melissa confirmed; not a live draft or specific series/game. `context-only`. |

### 8.3 Boundary findings

Current offsets are from the current `analysis/evidence/game-offsets.json` (not the stale snapshot in §3.3). No boundary was promoted; `game-offsets.json` was not edited.

**Overall: 31 boundary reviews — 18 `rejected`, 11 `context-only`, 2 `inconclusive`, 0 `used`.**

| Series | Current offset | Pairing | Series pairing | Game 1 start | Overall | Finding |
|---|---:|---|---|---|---|---|
| 1036 EVOS vs RRQ | 1303s `detected_pending_review` | EVOS/RRQ | inconclusive | inconclusive | **inconclusive** | Analyst desk and welcome banner; no legible team names, match label, draft, or clock. |
| 1105 EVOS vs AE | 300s `pending_validation` | EVOS/AE | context-only | rejected | **rejected** | Pre-show screen with a 27:45 countdown and the day's schedule; 300s is not the match start. |
| 1106 NAVI vs BTR | 13093s `boundary_verified` | NAVI/BTR | used | context-only | **context-only** | M71 GAME 1 NAVI vs VITALITY with `DRAFT PICK IN 14:54`; series intro confirmed, game 1 not started. The handoff's old 24389s capture shows 1107 ONIC vs TLID. |
| 1107 ONIC vs TLID | 23893s `boundary_verified` | ONIC/TLID | used (related 24389s) | context-only | **context-only** | M72 GAME 1 with `DRAFT PICK IN 16:02`; the 24389s frames show the same M72 match explicitly as ONIC vs TLID. |
| 1062 DEWA vs ONIC | 2460s `boundary_verified` | DEWA/ONIC | used | context-only | **context-only** | 2460s is a logo animation; 2464s shows ONIC/DEWA with game clock 00:19. Pairing confirmed, but the candidate is not game-clock zero. |
| 1084 GEEK vs BTR | 2043s `boundary_verified` | GEEK/BTR | used (derived crop) | context-only | **context-only** | M49 GAME 1 GEEK vs VITALITY with `DRAFT PICK IN 15:51`; series intro confirmed, game 1 not started. |
| 1094 EVOS vs ONIC | 1585s `detected_pending_review` | EVOS/ONIC | used (related 1560s) | context-only | **context-only** | M59 GAME 1 with `DRAFT PICK IN 17:00`; the 1560s ticker names EVOS vs ONIC. |
| 1075 RRQ vs DEWA | 2425s `detected_pending_review` | RRQ/DEWA | context-only | rejected | **rejected** | KLASEMEN standings table; no match start. |
| 1076 ONIC vs GEEK | 2425s `detected_pending_review` | ONIC/GEEK | context-only | rejected | **rejected** | KLASEMEN standings table. A related 2400s frame shows `M41 - GAME 1` with the GEEK wordmark, but the full pairing and a start are not established. |
| 1077 DEWA vs EVOS | 2425s `detected_pending_review` | DEWA/EVOS | context-only | rejected | **rejected** | KLASEMEN standings table; no match start. |
| 1086 AE vs NAVI | 31928s `detected_pending_review` | AE/NAVI | rejected | rejected | **rejected** | M53 GAME 3 GEEK 2-1 DEWA; this is series 1088's end, not AE vs NAVI. |

Pass 2 findings (all remaining non-null candidates):

| Series | Offset | Pairing | Game 1 start | Overall | Finding |
|---|---:|---|---|---|---|
| 1042 BTR vs GEEK | 10608s | used | context-only | **context-only** | Series intro; `DRAFT PICK IN 10:26`. |
| 1044 TLID vs NAVI | 300s | inconclusive | rejected | **rejected** | Pre-show rundown; match 9 crests are logos, not text; `09:27`. |
| 1046 TLID vs EVOS | 300s | inconclusive | rejected | **rejected** | Pre-show promo/countdown `09:27`; no pairing or match UI. |
| 1048 ONIC vs RRQ | 23266s | inconclusive | context-only | **inconclusive** | `M3 - GAME 1` desk; `DRAFT PICK IN 03:52`; crests illegible. |
| 1049 DEWA vs AE | 300s | used | rejected | **rejected** | Pre-show card lists DEWA vs AE; `09:32`. |
| 1051 GEEK vs EVOS | 22773s | used | context-only | **context-only** | Stage intro; `DRAFT PICK IN 13:16`. |
| 1054 TLID vs ONIC | 300s | context-only | rejected | **rejected** | Pre-show schedule; MATCH 19 crests are logos; ONIC only in an audience comment; `10:19`. |
| 1056 RRQ vs BTR | 15232s | used | context-only | **context-only** | Analyst desk; ticker RRQ vs BTR, `GAME 1`; no clock. |
| 1067 BTR vs AE | 22586s | used | context-only | **context-only** | Player interview; BTR vs AE, 0-0; no clock. |
| 1070 TLID vs BTR | 300s | partial | rejected | **rejected** | Countdown `12:34`; BTR only in a viewer comment; no TLID pairing. |
| 1073 GEEK vs TLID | 300s | used | rejected | **rejected** | Pre-show card lists GEEK vs TLID; `10:06`. |
| 1078 GEEK vs NAVI | 1461s | context-only | context-only | **context-only** | NAVI interview; `MATCH 3 - GAME 1`, `14:58`; GEEK not visible. |
| 1082 BTR vs ONIC | 17077s | used | rejected | **rejected** | `MATCH 47 - GAME 2`, clock `10:39`; game 1 already played. |
| 1089 AE vs TLID | 300s | used | rejected | **rejected** | Pre-show card lists AE vs TLID; `19:08`. |
| 1090 RRQ vs EVOS | 12178s | context-only | rejected | **rejected** | Crowd b-roll under a sponsor overlay; no match UI. |
| 1095 RRQ vs TLID | 1882s | context-only | rejected | **rejected** | KLASEMEN standings; no match. |
| 1096 DEWA vs NAVI | 1884s | context-only | rejected | **rejected** | KLASEMEN standings; no match. |
| 1097 EVOS vs GEEK | 2052s | context-only | rejected | **rejected** | KLASEMEN standings; no match. |
| 1102 ONIC vs DEWA | 2354s | context-only | context-only | **context-only** | Analyst desk; `DRAFT IN 15:02`; only DEWA visible. |
| 1103 BTR vs EVOS | 2429s | context-only | rejected | **rejected** | KLASEMEN standings; no match. |

Rule corrections applied during pass 2: (a) `GAME 2`–`GAME 9` now rejects a game-1 claim, not only `GAME 3` (1082 is a hard contradiction: `MATCH 47 - GAME 2` at clock `10:39` with BTR vs ONIC visible); (b) team names from other cards on a multi-match schedule can no longer produce a pairing contradiction; (c) a pre-show/desk segment at a 300s candidate offset is rejected as a game-1 start. Recompute changed 0 frame dispositions and 7 boundary reviews (1082, 1044, 1049, 1054, 1070, 1073, 1089); 1044/1054 also changed pairing from contradicted to unknown/partial.

### 8.4 Unresolved items and backlog

No boundary is marked `visually_verified`. The following remain un-promoted:

- **14 no-candidate null offsets** (after P3): 1043, 1058, 1061, 1063, 1064, 1066, 1072, 1079, 1083, 1092, 1093, 1099, 1101, 1104. P3 reviewed candidates 1037/1085/1087/1088 (all context-only); 1086's 31928s candidate was rejected and its offset nulled.
- **6 pass-2 candidates remain `context-only`**: 1042, 1051, 1056, 1067, 1078, 1102. They are pre-match intros, desks, or interviews, not game-1 starts.
- **1 pass-2 candidate remains `inconclusive`**: 1048 (crests illegible at the desk).
- **All 20 non-null candidates are reviewed**: 13 rejected, 6 context-only, 1 inconclusive. There is no remaining non-null capture backlog.
- **4 unvalidated sources** still need boundary work: `src-s18-w06d01`, `src-s18-w07d01`, `src-s18-w07d02`, `src-s18-w08d02`. Pass 1 confirmed 1084/1094 and rejected 1075/1076/1077/1086; pass 2 rejected 1095/1096 and left 1085/1087/1088 unresolved; see `analysis/reports/unvalidated-sources.md`.
- **No game-1 start** was visually proven for any series. The visible frames are pre-match intros, desks, standings, or in-progress gameplay. A pre-match countdown is not a game start.
- **Series 1036** remains visually inconclusive: the 1303s frame is an analyst desk with no legible team names.
- **Series 1062** pairing is confirmed at 2464s, but the 2460s candidate is a logo animation and the game clock is already 00:19; the exact boundary remains ambiguous.
- **Unverified draft-countdown leads** (candidate + visible countdown; not captured, do not cite): 1042 ≈11234s, 1048 ≈23493s, 1051 ≈23564s, 1078 ≈2354s, 1102 ≈3246s.
- **`game-offsets.json` is unchanged.** Rejections are recorded in the ledger, not written back as status changes.
- **Historical `visual-review.json`** labels remain the historical "OpenCode multimodal review"; they were not relabelled. DeepSeek records are linked by `historical_frame_id` and exact screenshot hash.

### 8.5 Validation and reproducibility

Run from the repository root:

```text
python tools/validate_visual_reviews.py
python tools/test_visual_review_integrity.py
python tools/audit_visual_evidence.py
python tools/recompute_visual_reviews.py
python tools/validate_game_offsets.py
```

Pass 1 + pass 2 results:

- `validate_visual_reviews.py`: **0 errors, 4 warnings**. The warnings are transcript-verified offsets (1062, 1084, 1106, 1107) that DeepSeek only partially confirmed visually; they remain `boundary_verified` from transcript evidence and were not promoted.
- `test_visual_review_integrity.py`: **21/21 adversarial tests pass** (17 validator tests + 4 boundary-decision regressions).
- `test_adversarial_boundaries.py`: **14/14 pass**.
- `test_transcript_evidence.py`: **18/18 pass**.
- `audit_visual_evidence.py`: **125 PNGs, 113 official plan frames present, 0 hash mismatches, 4 failed captures** (3 sidecar-only timeouts plus `VF-1037-041545`).
- `validate_game_offsets.py`: **0 errors** (27 `boundary_verified`, 26 `pending_validation`, 19 `detected_pending_review`).
- `ci_semantic_check.py`: **pass**.
- CI: `.github/workflows/semantic-check.yml` runs the validator, both adversarial suites, the offset validator, and the inventory check.

### 8.6 No-human-review attestation

`analysis/evidence/deepseek-visual-reviews.json` records `human_review: false`, `reviewer: deepseek`, `review_mode: api-pixel-inspection-only`, and a non-empty API request id for every reviewed frame. No human screenshot inspection, manual visual approval, human-review queue, or human escalation was used. The historical `visual-review.json` reviewer label is preserved as history and is not a DeepSeek review.

### 8.7 Pass 3 progress (intermediate, 2026-11-02/03)

**Current ledger:** 220 frames, 35 canonical boundary reviews, 69 API calls. Frame dispositions: 113 `used`, 37 `context-only`, 68 `inconclusive`, 2 `rejected`. Boundary dispositions: 18 `rejected`, 15 `context-only`, 2 `inconclusive`, **0 `used`; 0 `visually_verified`**. Backlog: 14 no-candidate null offsets; 25 reviewed-but-unpromoted entries. `plan_sha256` matches the current plan.

**P0 — 1062 @2443–2449s:** captured 2444.513, 2447.543, 2450.515. All three show a pre-match lineup-comparison overlay; no scoreboard, game clock, or `00:00`. **Negative; no promotion.**

**P1 — 1048 pairing cleanup:** captured 23491.313, 23494.321, 23497.468 at the M3 draft-pick expiry, plus a 4x scoreboard crop. The frames show an on-stage M3 lineup and a scoreboard with two unlabeled crests; the crop still has no legible ONIC or RRQ text. **Pairing not confirmed; no promotion.**

**P2a — 1084 / 1106 / 1107:** multiple ordered probes around the draft expiry and first HUD cut-in.
- 1084: first in-game HUD clock is **00:19** at 3704.435s (GEEK vs BTR visible). No `00:00` frame found.
- 1106: first in-game HUD clock is **01:37** at 14681.456s (NAVI vs BTR visible). No `00:00` frame found.
- 1107: sampled 24945–24970s; TLID vs ONIC lower-third visible but no game clock or `00:00`.
**No promotion.** The broadcasts appear to cut to gameplay after the clock has already advanced.

**Validation:** `validate_visual_reviews.py` 0 errors / 4 warnings; `test_visual_review_integrity.py` 21/21 pass; `ci_semantic_check.py` pass; audit 190 PNGs, 178 official, 0 hash mismatches, 6 failed captures (ad-overlay timeouts included).

**P2b — 1042 / 1051 / 1078 / 1102:** sampled the likely game-feed windows from transcript cues.
- 1042: 11982–12022s shows draft/player-cam/stage; first pairing screen is VITALITY vs GEEK at 12022s; no clock or `00:00`.
- 1051: first HUD is **`00:51`** at 24141.4s (GEEK vs EVOS). A narrow 24046–24058s probe shows a paused HUD at **`00:16`** and bumpers, not `00:00`.
- 1078: 2681–2721s shows GEEK vs NAVI player-cam/analysis segments with no game clock; no `00:00`.
- 1102: first HUD is **`00:34`** at 3732.5s (DEWA vs ONIC); no `00:00`.
**No promotion.** The observed broadcasts cut to gameplay after the game clock had advanced (00:16/00:34/00:51), so no same-frame `00:00` was available.

**P3 (first batch) — 1037 / 1085 / 1087 / 1088:** transcript cues found and captured.
- 1037 @12675s: NAVI vs AE confirmed; `DRAFT PICK IN 08:39` countdown; no `00:00`.
- 1085 @12883s: DEWA vs TLID confirmed; `DRAFT PICK IN 14:48`; no `00:00`.
- 1087 @13276s: BTR/RRQ stage introduction; no clock; no `00:00`.
- 1088 @23569s: GEEK vs DEWA confirmed; `DRAFT PICK IN 14:51`; no `00:00`.
All four are `context-only`, not promoted. The 1086 31928s candidate was rejected (it is 1088 game 3) and its offset nulled.

**Remaining:** P3 for 14 no-candidate null offsets, P4 offset-status reconciliation, P5 1036. §6a remains unmet; do not archive.


### 8.8 Pass 3 completion report (2026-11-03)

**Ledger:** 966 frames, 62 boundary reviews, 140 API calls. Frame dispositions: 467 `used`, 127 `context-only`, 370 `inconclusive`, 2 `rejected`. Boundary dispositions: 20 `rejected`, 41 `context-only`, 1 `inconclusive`, **0 `used`; 0 `visually_verified`**. Backlog: 10 no-candidate nulls; 29 reviewed-but-unpromoted entries. Derived status: 0 not-reviewed series.

**P3 — all 18 original null offsets covered.** Cue detection found 8 candidates:
- 1037 @12675s, 1085 @12883s, 1087 @13276s, 1088 @23569s (first batch; all context-only).
- 1072 @18108.4s (rejected: `GAME 2`), 1079 @1660.8s (rejected: day schedule rundown), 1083 @24416.2s (context-only: first clock `00:15`), 1101 @12798s (context-only: interview).
- 10 remaining nulls have no team-paired cue and are documented no-candidate waivers: 1043, 1058, 1061, 1063, 1064, 1066, 1092, 1093, 1099, 1104.
- 1086's 31928s candidate was rejected as 1088 game 3 and its offset nulled.

**P4 — derived reconciliation.** `analysis/evidence/visual-review-status.json` records all 72 series: 20 rejected, 18 context-only, 1 inconclusive, 10 no-candidate waivers, 23 not reviewed, 0 `visually_verified`. It is hash-linked to `game-offsets.json` and `deepseek-visual-reviews.json`; `ci_semantic_check.py` validates the hashes and counts.

**Remaining boundary-verified batch.** All 23 previously unreviewed boundary-verified series were sampled in first-game-feed windows. None contained a same-frame `00:00` with the correct pairing; all are context-only. The derived status now has 0 not-reviewed series.

**P5 — 1036 wide probe.** Captured 1901.5s (pre-match desk, `DROPPING IN 02:08`), 2501.6s (draft), 2801.5s (spectator), 2966.3s (first HUD at `03:08`). EVOS vs RRQ confirmed; no `00:00`; boundary remains context-only.

**Validation:** visual-review validator **0 errors / 4 warnings**; 21/21 adversarial tests; CI semantic check pass; game-offset validator **0 errors**; audit 254 PNGs, 242 official, 0 hash mismatches, 9 failed captures.

**Completion gate:** only §6a box 1 (at least one visible `00:00` promotion) remains unchecked. The sampled broadcasts cut to gameplay after the clock advanced; no same-frame `00:00` was found. Do not archive or mark complete.



### 8.9 1051 one-second start sweep (2026-11-04)

Captured 17 one-second frames at 24028–24044s, immediately before the paused `00:16` HUD. Results: 24029.5–24030.5s stage/player-cam, 24031.5–24034.4s draft analysis (GEEK vs EVOS), 24035.6–24044.4s hero-pick grid/bumpers, then 24045.6s paused HUD reading `00:16` with no team labels. **No literal `00:00` and no same-frame pairing; no promotion.** This closes the suggested 1051 promotion path.


### 8.10 1084 one-second start sweep (2026-11-04)

Captured 21 one-second frames at 3684-3704s, before the first HUD at 3704.435s (`00:19`). Results: 3685-3693s season-intro/trophy/logo bumpers, 3694-3702s in-game map with no HUD, 3702.5s HUD `00:17` with no team labels, 3704.5s HUD `00:19` with GEEK/BTR. **No literal `00:00` in the window; the broadcast cuts in at `00:19`; no promotion.** The sweep corroborates the GEEK/BTR pairing but cannot supply the game-1 start at 2043s.

Two decision-rule defects surfaced and were fixed: (1) short aliases were matched as substrings, so `AE` matched inside `AERIAL` and falsely contradicted the 1084 pairing; matching is now token-bounded; (2) related probe frames could reject a primary candidate even when they only corroborated the pairing; related frames may now support, never contradict, the primary boundary. Regression tests `test_short_alias_does_not_match_inside_words` and `test_related_probe_cannot_reject_primary_pairing` were added. B-1084-2043 is `context-only` (pairing supported by related frames, draft-pick countdown, no game clock at 2043s).


### 8.11 1083 one-second start sweep (2026-11-04)

Captured 19 one-second frames at 24398-24416s, before the first HUD at 24417.5s (`00:15`). Results: 24399-24410s player-cam close-ups, 24411-24413s league-intro bumper, 24414.5s first in-game frame with `00:12`, then `00:13`, `00:14`, `00:15` on successive frames. No team labels on the first HUD frames; EVOS/TLID pairing appears from 24422.5s (`00:20`). **No literal `00:00` in the window; the game clock started during the player-cam/bumper segment and the broadcast cut in at `00:12`; no promotion.** B-P3-1083-24416 remains `context-only` (pairing visible, game-1 start not visible).


### 8.12 1068 one-second start sweep (2026-11-05)

Captured 29 one-second frames at 2940-2968s. The window is entirely non-game coverage: 2941s draft HUD with player cams, 2942-2952s player reaction/bench/stage shots, 2953-2957s draft/stat comparison with EVOS/DEWA logos, 2958-2969s hero lineup, player-cam grid, sponsor bumpers, and trophy animation. **No gameplay HUD, no game clock, and no literal `00:00`.** The first HUD at 3001.5s reads `00:58`, implying a clock start near 2943.5s during the player-bench/stage coverage. This is consistent with the clock starting before the broadcast cuts to gameplay. B-P3-1068-2969 remains `context-only` (pairing visible at 3001.5s, game-1 start not visible); no promotion.


### 8.13 1041 one-second start sweep (2026-11-05)

The requested 1152-1198s range is pre-show caster discussion; 1198s is not a game start. The ledger's first game HUD is at 2220.5s, so the sweep covered 2200-2251s in two 26-frame groups.

Results: 2201-2208s pre-match hero/stat comparison (DEWA logo only), 2209-2219s player webcams, sponsor bumpers, mascot, and league/trophy animations, 2220.5s first in-game HUD `00:17` with TLID only, 2221.5s `00:18` with TLID/DEWA, 2226-2238s split-screen replay without broadcast HUD, 2239.4s `00:34`, 2240.5s `00:36`, and 2250.5s `00:46`. **No literal `00:00` in the window.** The clock started near 2203.5s during pre-match stats. B-P3-1041-1198 remains `context-only` (the 1198s candidate is pre-show; the first game feed is already at `00:17`); no promotion.


### 8.14 1040 one-second start sweep (2026-11-05)

Source confirmed as `src-s18-w01d02`. The candidate is 24067s, but the first clocked HUD is at 24121.4s (`01:01`); 24081.5s is already in-game without a HUD. The sweep covered 24055-24121s in three groups.

Results: 24057-24063s draft/stat comparison with EVOS/NAVI logos but no legible team names, 24064-24076s player cams, sponsor/tournament bumpers, and map flyover, 24076.5s first HUD `00:17` with only an EVOS player prefix, 24079.4s `00:20` with EVOS/NAVI, 24081-24092s split-screen observer view, 24092.5s `00:33`, then `00:41`-`01:02` on successive frames. **No literal `00:00` in the window.** The clock started near 24059.5s during the draft/stat comparison. B-P3-1040-24067 remains `context-only` (the candidate is pre-game; the first game feed is already at `00:17`); no promotion.


### 8.15 1038 one-second start sweep (2026-11-05)

Source confirmed as `src-s18-w01d02`. The 1655s candidate is a series-intro offset; the first clocked HUD is at 2701.5s (`01:36`), so the inferred game start is near 2605.5s. The sweep covered 2600-2701s in three logical parts (A 2600-2633, B 2634-2667, C 2668-2701). Part C stalled as a 34-frame request and was split into C1 (2668-2684) and C2 (2685-2701); all 102 frames were reviewed.

Results: 2601-2609s pre-game hero lineup with TLID/GEEK, 2610-2620s sponsor/event bumpers and HUD-less map, 2621.4s first HUD `00:17` with GEEK only, 2624.5s `00:20` with TLID/GEEK, then a continuous count-up through `01:37` at 2702.5s. **No literal `00:00` in the 102-frame window.** The clock started near 2604.4s during the pre-game hero lineup. B-P3-1038-1655 remains `context-only` (the 1655s candidate is pre-game; the first game feed is already at `00:17`); no promotion.


### 8.16 1106 one-second start sweep (2026-11-05)

Source confirmed as `src-s18-w09d03`. The candidate is 13093s, but the first clocked HUD is at 14600.5s (`00:17`), not 14681.5s (`01:37`). The inferred start is ~14583.5s. The sweep covered 14580-14632s; groups C/D (14632-14681s) were dropped as post-start coverage once the true first HUD was found.

Results: 14580-14592s sponsor bumper, broadcast intro, trophy, and event title cards; 14593-14600s game-map showcase with no HUD; 14600.5s first HUD `00:17` with NAVI only; 14601.5s `00:18` with NAVI/BTR; then a continuous count-up through `00:48` at 14632.4s. **No literal `00:00`.** The clock started near 14583.5s during the season intro. B-1106-13093 remains `context-only`; no promotion.


### 8.17 1107 one-second start sweep (2026-11-05)

Source confirmed as `src-s18-w09d03`. The 23893s candidate is pre-match and the ledger has no clocked 1107 HUD; the pilot frame at 25491s reads `05:08`, implying a start near 25183s. The sweep covered 25180-25210s in two groups.

Results: 25180-25192s sponsor bumper, league intro, trophy reveal, and Road to Surabaya bumpers; 25193-25199s map/base cinematic with no HUD; 25200.5s first HUD `00:17` with ONIC/TLID player-name prefixes; 25201.5s `00:18`, 25202.5s `00:19`, then `00:20`-`00:22` before a split-screen replay. **No literal `00:00`.** The clock started near 25183.5s during the league intro/trophy bumper. B-1107-23893 remains `context-only`; no promotion.


### 8.18 1102 one-second start sweep (2026-11-05)

Source confirmed as `src-s18-w09d02`. The 2354s candidate is pre-show. The ledger's first clocked HUD is 3731.5s (`00:34`), but the 1-second sweep found an earlier first HUD at 3714.4s (`00:17`); the inferred start is ~3697.4s. The sweep covered 3694-3732s in two 19-frame groups.

Results: 3695-3697s pre-match hero/stat comparison, 3698-3699s player-cam lineup, 3700-3713s sponsor/mascot/league bumpers and map without HUD, 3714.4s first HUD `00:17` with DEWA only, 3715.4s `00:18` with DEWA/ONIC, `00:19`-`00:22`, 3720-3726s split-screen matchup without a clock, then `00:28`-`00:35`. **No literal `00:00`.** The clock started near 3697.4s during the player-cam lineup. B-P2-1102-2354 remains `context-only`; no promotion.


### 8.19 1069 one-second start sweep (2026-11-05)

Source confirmed as `src-s18-w05d01`. The 1745s candidate is pre-show. The ledger's first clocked HUD is 3201.4s (`01:20`), but the 1-second sweep found an earlier first HUD at 3137.5s (`00:17`); the inferred start is ~3120.5s. Group A covered 3118-3140s; groups B-D were dropped as post-start once the true first HUD was found.

Results: 3119-3125s pre-match lineup/counter screen with GEEK and an eagle-logo opponent, 3126-3127s hero lineup and player-cam grid, 3128-3136s sponsor/league/trophy bumpers, 3137s map flyover, 3137.5s first HUD `00:17` with GEEK only, 3138.5s `00:18` with GEEK/ONIC, 3139.5s `00:19`. **No literal `00:00`.** The clock started near 3120.5s during the pre-match lineup. B-P3-1069-1745 remains `context-only`; no promotion.


### 8.20 1074 one-second start sweep (2026-11-05)

Source confirmed as `src-s18-w05d03`. The 12328s candidate is pre-show. The ledger's first clocked HUD is 13551.1s (`02:04`), but the 1-second sweep found an earlier first HUD at 13443.4s (`00:17`); the inferred start is ~13426.4s. The sweep covered 13424-13461s in two groups.

Results: 13425-13426s player-cam collage and sponsor bumper, 13428-13438s hero intro/trophy/season-wheel animation, 13439-13442s map flyover, 13443.4s first HUD `00:17` with ONIC/AE, 13444.5s `00:18` through `00:23`, 13450-13458s split-screen replay without a clock, then `00:32`-`00:34`. **No literal `00:00`.** The clock started near 13426.4s during the sponsor bumper. B-P3-1074-12328 remains `context-only`; no promotion.


### 8.21 1062 one-second start sweep (2026-11-05)

Source confirmed as `src-s18-w04d02`. The candidate is 2460s; the existing 2465.2s frame reads `00:19` with DEWA/ONIC, implying a start near 2446.2s. The 1-second sweep covered 2444-2466s in one 22-frame group.

Results: 2445-2450s draft lineup comparison with DEWA and an unlabeled eagle emblem, 2451s draft hero grid, 2452s player-cam grid, 2453-2459s sponsor/league logo bumpers, 2460-2462s map flyover without HUD, 2463.5s first HUD `00:17` with DEWA only, 2464.5s `00:18` with DEWA/ONIC, 2465.4s `00:19`, 2466.5s `00:20`. **No literal `00:00`.** The clock started near 2446.5s during the draft lineup comparison. B-1062-2460 remains `context-only`; no promotion.


### 8.22 1052 one-second start sweep (2026-11-05)

Source confirmed as `src-s18-w03d01`; the plan pairing is **BTR vs NAVI** (the prompt's GEEK/EVOS label was incorrect). The first clocked HUD is 2721.1s (`01:09`), but the 1-second sweep found an earlier first HUD at 2669.4s (`00:18`); the inferred start is ~2651.4s. Large 23/24-frame groups stalled the reviewer, so the sweep was reduced to three small groups: 2650-2655, 2656-2661, and 2668-2673. The 2662-2667 window returned advertisement/promotional overlays.

Results: 2652.5s draft analysis showing VITALITY vs ONIC (a different match lead-in), 2653-2661s draft/player cams, sponsor and event bumpers, 2662s event-logo bumper, 2669.4s first HUD `00:18` with NAVI only, 2670.4s `00:19` with BTR/NAVI, then `00:20`-`00:23`. **No literal `00:00`.** B-P3-1052-2666 remains `context-only`; no promotion.


### 8.23 1098 one-second start sweep (2026-11-05)

Source confirmed as `src-s18-w08d03`. The 17865s candidate is probe-only, and the first clocked HUD is 18901.4s (`01:42`). The 1-second sweep found an earlier first HUD at 18817.3s (`00:18`); the inferred start is ~18799.3s. Small 6-frame groups covered 18797-18820s.

Results: 18798-18809s sponsor/character intro, league branding, trophy, and MPL circular logo animations; 18810-18816s MOBA spectator/map views without a clock; 18816.5s RRQ/ONIC banners over a map without HUD; 18817.3s first HUD `00:18` with ONIC only; 18818.3s `00:19` with RRQ/ONIC; 18819-18821s `00:20`-`00:22`. **No literal `00:00`.** The clock started near 18799.3s during the sponsor/character intro. B-P3-1098-17865 remains `context-only`; no promotion.


### 8.24 1081 one-second start sweep (2026-11-05)

Source confirmed as `src-s18-w06d03`; the plan pairing is AE vs DEWA. The 1800s candidate is pre-show and the first clocked HUD is 3051.5s (`01:50`). The 1-second sweep found an earlier first HUD at 2958.3s (`00:17`); the inferred start is ~2941.3s. Small 6-frame groups covered 2939-2962s; the 2951-2956 window returned advertisement/promotional overlays.

Results: 2940-2941s player-camera intro grid, 2942-2951s sponsor/mascot/league/trophy bumpers, 2958.3s first HUD `00:17` with AE/DEWA, 2959.5s `00:18`, 2960.5s `00:19`, 2961.2s `00:20`, 2962.2s `00:21`, then a split-screen transition with only a partial `00` visible. **No literal `00:00`.** The clock started near 2941.3s during the player-camera intro. B-P3-1081-1800 remains `context-only`; no promotion.


### 8.25 1057 one-second start sweep (2026-11-05)

Source confirmed as `src-s18-w03d03`; the plan pairing is NAVI vs ONIC. The 2340s candidate is pre-show and the first clocked HUD is 2451.5s (`02:05`). The 1-second sweep found an earlier first HUD at 2342.4s (`00:17`); the inferred start is ~2325.4s. Small 6-frame groups covered 2324-2347s.

Results: 2325-2330s pregame lineup/stat comparison, 2330.5s draft/matchup analysis, 2332-2334s player-camera grid, 2335-2341s sponsor/mascot/league bumpers, 2342.4s first HUD `00:17` with NAVI only, 2343.4s `00:18` with NAVI/ONIC, 2344.4s `00:19`, 2345.5s `00:20`, 2346.5s `00:21`, 2347.5s `00:22`, 2348.4s `00:23`. **No literal `00:00`.** The clock started near 2325.4s during the pregame lineup/stat comparison. B-P3-1057-2340 remains `context-only`; no promotion.


### 8.26 1060 one-second start sweep (2026-11-05)

Source confirmed as `src-s18-w04d01`; the plan pairing is NAVI vs DEWA. The 1638s candidate is pre-show and the first clocked HUD is 2601.5s (`02:10`). The 1-second sweep found an earlier first HUD at 2487.4s (`00:17`); the inferred start is ~2470.4s. Small 6-frame groups covered 2469-2492s.

Results: 2469-2475s pre-game lineup comparison with NAVI/DEWA, 2476-2485s draft/pick screen, sponsor, mascot, and league bumpers, 2486s map with transition overlay, 2487.4s first HUD `00:17` with NAVI only, 2489.5s `00:19` with NAVI/DEWA, 2490.4s `00:20`, 2491.6s `00:21`, 2492.5s `00:22`, then a split-screen segment. **No literal `00:00`.** The clock started near 2470.4s during the pre-game lineup comparison. B-P3-1060-1638 remains `context-only`; no promotion.


### 8.27 End-goal visual audit (2026-11-14)

Re-audited the full DeepSeek ledger (966 frames, 62 boundary reviews) for any overlooked literal `00:00`:

- `visible_00_00 = true`: **0 frames**.
- `same_frame_00_00_pairing = true`: **0 frames**.
- Boundary dispositions: **41 context-only, 20 rejected, 1 inconclusive, 0 used**.
- Ten series have documented no-candidate waivers.

Two frames contain the string `00:00` in free text, but both are explicit negations: `DF3-w09d03-24946` says "No 00:00 game clock appears anywhere", and `DF3-w01d02-12301` says the clock "reads 04:38, not 00:00". They are not evidence.

**Result:** no boundary can be promoted. The gate stays unmet; the standard is unchanged. This is an evidence-backed blocker, not missing work.
