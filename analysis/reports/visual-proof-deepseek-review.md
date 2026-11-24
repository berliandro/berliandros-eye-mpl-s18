# DeepSeek visual proof review — MPL ID S18

**Date:** 2026-11-02  
**Reviewer:** DeepSeek only (no human visual inspection, manual approval, review queue, or escalation)  
**Goal status:** **ACTIVE — NOT COMPLETE.** Pass 3 was executed exhaustively across all 72 series; **0** boundaries are `visually_verified`. All 18 original null offsets are covered by reviewed candidates or documented waivers; 41 context-only, 1 inconclusive and 20 rejected reviews remain unpromoted. Only §6a box 1 is unchecked.  
**Ledger:** `analysis/evidence/deepseek-visual-reviews.json`  
**Plan:** `analysis/evidence/visual-review-plan.json`  
**Audit:** `analysis/evidence/visual-evidence-audit.json`  
**Handoff:** `docs/goals/active/mpl-s18-visual-proof-deepseek-handoff.md` (completion gate: §6a)

## Hy4 High re-review (2026-11-24)

The `opencode-go-session` backend now uses **OpenCode Go — Hy4 Flash Free: High** (`opencode-go/hy4-flash-free`, variant `high`); smoke test passed with `reviewer: hy4`. Three parallel subagents re-reviewed **128 disjoint frames** (37 / 42 / 49; 30 groups) covering 1062, 1048, 1084/1106/1107, 1042/1051/1078/1102, the null-offset candidates 1037/1085/1087/1088/1079/1083/1072/1101, and 1036/1105/1038–1041/1045/1047. All frames have API request IDs; dispositions 69 `used`, 17 `context-only`, 42 `inconclusive`, 0 `rejected`. **`visible_00_00` is false on every frame**: the only readable game clocks are 00:15–00:46 (e.g. 1083 `00:44`, 1102 `00:34`, 1051 paused `00:16`, 1062 `00:17`–`00:20`); other candidates are drafts, countdowns, sponsor bumpers or interviews. No promotion was made; the canonical DeepSeek ledger is unchanged. Evidence: `analysis/evidence/hy4-review-{a,b,c}.json`, `hy4-plan-{a,b,c}.json`. Full verification passed (29/29 suites, 24/24 integrity tests, 0 hash mismatches).

**Why no frame-step recovery is possible (user-confirmed):** the match starts before the camera cuts into the game (commentator shout, cinematic pan, heroes walking out); the first normal HUD is already ~5–20 s into the game. Stepping back with YouTube `,` or extracting an exact frame range with yt-dlp/ffmpeg cannot reveal a `00:00` HUD that was never broadcast. The gate needs a standard change or a genuine `00:00` source.

## Pass 3 progress (intermediate)

Pass 3 is in progress. Current ledger: **203 frames, 31 canonical boundary reviews, 65 API calls** — 104 `used`, 33 `context-only`, 64 `inconclusive`, 2 `rejected` at frame level; 18 `rejected`, 11 `context-only`, 2 `inconclusive`, **0 `used` / 0 `visually_verified`** at boundary level. The 18 null offsets remain.

Attempted so far:

- **P0 1062 @2443–2449s:** 2444.513 / 2447.543 / 2450.515s show a pre-match lineup comparison, no clock or `00:00`. No promotion.
- **P1 1048:** 23491.313 / 23494.321 / 23497.468s and a 4x crop show an M3 stage/scoreboard with unlabeled crests; ONIC/RRQ not legibly confirmed. No promotion.
- **P2a 1084/1106/1107:** first visible clocks are `00:19` (1084 at 3704.435s) and `01:37` (1106 at 14681.456s); 1107 shows no game clock in the sampled 24945–24970s range. No `00:00`, no promotion.

- **P2b 1042/1051/1078/1102:** first visible HUD clocks are `00:51` (1051) and `00:34` (1102); 1042/1078 show draft/player-cam segments without a game clock. A narrow 1051 probe shows a paused `00:16` HUD. No `00:00`, no promotion.

- **P3 first batch 1037/1085/1087/1088:** transcript cues found and captured. Pairings confirmed (NAVI/AE, DEWA/TLID, BTR/RRQ, GEEK/DEWA), but all four are draft/desk segments without `00:00`; no promotion. The 1086 31928s candidate was rejected as 1088 game 3 and nulled.

Validation: visual-review validator 0 errors / 4 warnings; 21/21 adversarial tests; CI semantic check pass; audit 190 PNGs, 178 official, 0 hash mismatches, 6 failed captures. Remaining: P2b, P3 null offsets, P4 reconciliation, P5 1036.

## 1. Scope and method

Pass 1 reviewed:

- all eight historical pilot targets in `analysis/evidence/visual-review.json`;
- the Alberttt draft frame;
- all captured frames for the four unvalidated sources (w06d01, w07d01, w07d02, w08d02);
- the w04d02 1:00:00 probes and the 1107 turret probe;
- newly captured frames for the priority boundaries: 1036 @1303s, 1105 @300s, 1106 @13093s, 1106 @24389s (stale handoff value), 1107 @23893s, 1062 @2460s, 1084 @2043s, 1094 @1585s;
- a 4x scoreboard crop for 1084 to read the small team marks.

Pass 2 reviewed the 20 non-null boundary candidates that pass 1 did not capture:

`1042, 1044, 1046, 1048, 1049, 1051, 1054, 1056, 1067, 1070, 1073, 1078, 1082, 1089, 1090, 1095, 1096, 1097, 1102, 1103`

Each candidate was captured as three ordered frames at roughly `t-5`, `t`, `t+5` seconds (60 new frames, all captures succeeded), then sent as one multi-image review group. This covers every non-null candidate in `game-offsets.json`; the 18 null offsets remain unreviewed because they have no capture target.

Each image was sent as the original PNG bytes (or, for the 1084 scoreboard, a documented 4x crop with its source hash and crop box) to a DeepSeek vision model. The review ledger records the screenshot SHA-256, sidecar SHA-256, source/video, requested/actual time, API request id, model, provider, timestamp, observation, visible text, confidence, limitations, and deterministic checks. A frame is not marked `reviewed` without a parsed API response.

### Models and smoke tests

| Stage | Model / transport | Smoke result | Notes |
|---|---|---|---|
| Direct DeepSeek API | `deepseek-flash` / `https://api.deepseek.com` | **passed** | Synthetic image text and bottom-right orange circle read correctly; then `HTTP 402 Insufficient Balance`. |
| OpenCode free | `deepseek-v4.1-flash-free` / local OpenCode session API | **passed** | First 7 frames reviewed; then free daily limit reached. |
| OpenCode Go (pass 1) | `deepseek-v4.1-flash` / local OpenCode session API | **passed** | Remaining 46 pass-1 frames reviewed. |
| OpenCode Go (pass 2) | `deepseek-v4.1-flash` / local OpenCode session API | **passed** | All 60 pass-2 frames reviewed; record in `deepseek-vision-smoke-opencode-go-pass2.json`. |

The ledger records 7 frames from `deepseek-v4.1-flash-free` and 106 frames from `deepseek-v4.1-flash` (opencode-go). Both are DeepSeek vision models. The smoke test used a synthetic image with the text `DEEPSEEK VISION`, `SMOKE TEST 4729`, and an orange circle at bottom-right; the model correctly ignored the misleading `TOP LEFT` label.

## 2. Frame inventory and audit

`python tools/audit_visual_evidence.py` produced `analysis/evidence/visual-evidence-audit.json`:

- 125 PNG frames in the local cache;
- 113 official plan frames, all present;
- 0 sidecar hash mismatches;
- 12 excluded frames: 8 scratch/smoke images, the `_crop-1037-top` helper, the live-smoke frame, and two adjacent Alberttt draft frames not individually reviewed;
- 4 failed captures: `VF-1037-041545` (timing drift, image is an unrelated ad) and three sidecar-only 30s timeouts (`live-smoke2` @15230s, turret-probe @25504s and @25507s).

The cache is Git-ignored. The audit JSON is the committed snapshot; the ledger records the same hashes for every reviewed frame.

## 3. Frame dispositions

**113 frames:** 53 `used`, 29 `context-only`, 29 `inconclusive`, 2 `rejected`.

| Stage | Frames | `used` | `context-only` | `inconclusive` | `rejected` |
|---|---:|---:|---:|---:|---:|
| Pass 1 | 53 | 19 | 18 | 14 | 2 |
| Pass 2 | 60 | 34 | 11 | 15 | 0 |
| **Total** | **113** | **53** | **29** | **29** | **2** |

`used` means the frame is usable evidence for its bounded group claim. It does not mean a boundary is verified. Pass 2 has no `rejected` frames because the frame-level rule only checks whether the claimed pairing is visible; contradictions such as a later game or a wrong pairing are recorded at boundary level.

### Historical pilot corrections

| Frame | Historical label | DeepSeek finding |
|---|---|---|
| VF-1037-replay | Instant Replay banner confirms "AE AFFAN ... HAS SLAIN" | Banner says `INSTANT REPLAY`; `AFFAN` is visible; neither `AE AFFAN` nor `HAS SLAIN` is visible. **context-only.** |
| VF-1037-base | AE defending its base | Clock `21:08`, score `AE 17 - NAVI 15`, gold `63.9K` / `65.8K` confirmed. The camera shows a lane/river teamfight with no base structures. Base defense is not visible. **context-only.** |
| VF-1037-post | Post-game player-camera shot | Stage/player-camera shot; no in-game fight. **context-only.** |
| VF-1037-041545 | Failed capture | Failed sidecar, null actual time; the image is a Scotch-Brite ad, not the requested broadcast instant. **rejected.** |
| VF-1107-early | Clock 5:08; TLID 14.0K vs ONIC 13.1K; top-lane fight | All values and the active fight confirmed. **used.** |
| VF-1107-item | Clock 5:27; TLID 15.3K vs ONIC 13.6K; "FIRST ITEM PRIORITY DRICHEL" | All values and overlay confirmed. **used.** |
| VF-1107-mid | Clock 12:58; TLID 40.6K vs ONIC 34.7K; season milestone | Clock, ONIC 34.7K, and the `SEASON 18 / 40 / LORD KILL / KEVIN` milestone confirmed. TLID reads **40.8K**, not 40.6K. **context-only.** |
| VF-1107-070620 | YouTube Premium overlay | Promotional card confirmed; not gameplay evidence. **rejected.** |
| Alberttt draft | EVOS top-3 identity draft | Produced `DRAFT IDENTITY` / `DRAFT DNA` analysis segment; Paquito/Eudora/Melissa confirmed; not a live draft or specific series/game. **context-only.** |

## 4. Boundary findings

Current offsets are taken from the current `analysis/evidence/game-offsets.json`. No boundary was promoted, and `game-offsets.json` was not edited.

**31 boundary reviews:** 18 `rejected`, 11 `context-only`, 2 `inconclusive`, **0 `used`**.

### 4.1 Pass 1

| Series | Current offset | Pairing | Series pairing | Game 1 start | Overall | Finding |
|---|---|---:|---|---|---|---|
| 1036 EVOS vs RRQ | 1303s `detected_pending_review` | EVOS/RRQ | inconclusive | inconclusive | **inconclusive** | Analyst desk and welcome banner; no legible team names, match label, draft, or clock. |
| 1105 EVOS vs AE | 300s `pending_validation` | EVOS/AE | context-only | rejected | **rejected** | Pre-show screen with a 27:45 countdown and the day's schedule; 300s is not the match start. |
| 1106 NAVI vs BTR | 13093s `boundary_verified` | NAVI/BTR | used | context-only | **context-only** | `M71 - GAME 1`, NAVI vs VITALITY, `DRAFT PICK IN 14:54`; series intro confirmed, game 1 not started. The handoff's old 24389s capture shows 1107 ONIC vs TLID. |
| 1107 ONIC vs TLID | 23893s `boundary_verified` | ONIC/TLID | used (related 24389s) | context-only | **context-only** | `M72 GAME 1`, `DRAFT PICK IN 16:02`; the 24389s frames explicitly name ONIC vs TLID. |
| 1062 DEWA vs ONIC | 2460s `boundary_verified` | DEWA/ONIC | used | context-only | **context-only** | 2460s is a logo animation; 2464s shows ONIC/DEWA with game clock `00:19`. Pairing confirmed, but the candidate is not game-clock zero. |
| 1084 GEEK vs BTR | 2043s `boundary_verified` | GEEK/BTR | used (crop) | context-only | **context-only** | `M49 - GAME 1`, GEEK vs VITALITY, `DRAFT PICK IN 15:51`; series intro confirmed, game 1 not started. |
| 1094 EVOS vs ONIC | 1585s `detected_pending_review` | EVOS/ONIC | used (related 1560s) | context-only | **context-only** | `M59 - GAME 1`, `DRAFT PICK IN 17:00`; the 1560s ticker names EVOS vs ONIC. |
| 1075 RRQ vs DEWA | 2425s `detected_pending_review` | RRQ/DEWA | context-only | rejected | **rejected** | Full-screen KLASEMEN standings table; no match start. |
| 1076 ONIC vs GEEK | 2425s `detected_pending_review` | ONIC/GEEK | context-only | rejected | **rejected** | KLASEMEN standings. A related 2400s frame shows `M41 - GAME 1` and the GEEK wordmark, but the full pairing and a start are not established. |
| 1077 DEWA vs EVOS | 2425s `detected_pending_review` | DEWA/EVOS | context-only | rejected | **rejected** | KLASEMEN standings table; no match start. |
| 1086 AE vs NAVI | 31928s `detected_pending_review` | AE/NAVI | rejected | rejected | **rejected** | `M53 - GAME 3`, GEEK 2-1 DEWA; this is series 1088's end, not AE vs NAVI. |

### 4.2 Pass 2 — all remaining non-null candidates

| Series | Offset | Pairing | Series pairing | Game 1 start | Overall | Finding |
|---|---:|---|---|---|---|---|
| 1042 BTR vs GEEK | 10608s | VITALITY/GEEK | used | context-only | **context-only** | Series intro; `DRAFT PICK IN 10:26`. No draft board or game clock. |
| 1044 TLID vs NAVI | 300s | — | inconclusive | rejected | **rejected** | Pre-show rundown; match 9 crests are logos (not legible as text); other cards name VITALITY/DEWA; countdown `09:27`. |
| 1046 TLID vs EVOS | 300s | — | inconclusive | rejected | **rejected** | Pre-show promo/countdown `09:27`; no series pairing or match UI. |
| 1048 ONIC vs RRQ | 23266s | — | inconclusive | context-only | **inconclusive** | `M3 - GAME 1` analyst desk; `DRAFT PICK IN 03:52`; crests are not legible as team names. |
| 1049 DEWA vs AE | 300s | DEWA/AE | used | rejected | **rejected** | Pre-show card lists DEWA vs AE; countdown `09:32`. Not a start. |
| 1051 GEEK vs EVOS | 22773s | GEEK/EVOS | used | context-only | **context-only** | Stage intro; GEEK 0-0 EVOS, `DRAFT PICK IN 13:16`. |
| 1054 TLID vs ONIC | 300s | partial | context-only | rejected | **rejected** | Pre-show schedule; MATCH 19 crests are logos; ONIC appears only in an audience comment; countdown `10:19`. |
| 1056 RRQ vs BTR | 15232s | RRQ/BTR | used | context-only | **context-only** | Analyst desk; ticker names RRQ vs BTR and `GAME 1`; no draft or game clock. |
| 1067 BTR vs AE | 22586s | BTR/AE | used | context-only | **context-only** | Player interview; lower third BTR vs AE, 0-0; no draft or game clock. |
| 1070 TLID vs BTR | 300s | partial | context-only | rejected | **rejected** | Pre-show countdown `12:34`; BTR appears only in a viewer comment; no TLID pairing. |
| 1073 GEEK vs TLID | 300s | GEEK/TLID | used | rejected | **rejected** | Pre-show card lists GEEK vs TLID; countdown `10:06`. Not a start. |
| 1078 GEEK vs NAVI | 1461s | NAVI only | context-only | context-only | **context-only** | Pre-match NAVI interview; `MATCH 3 - GAME 1`, countdown `14:58`; GEEK not visible. |
| 1082 BTR vs ONIC | 17077s | BTR/ONIC | used | rejected | **rejected** | `MATCH 47 - GAME 2`, clock `10:39`. Game 1 already happened; this cannot be the game-1 start. |
| 1089 AE vs TLID | 300s | AE/TLID | used | rejected | **rejected** | Pre-show card lists AE vs TLID; countdown `19:08`. Not a start. |
| 1090 RRQ vs EVOS | 12178s | partial | context-only | rejected | **rejected** | Crowd b-roll under a sponsor overlay; no match UI or pairing. |
| 1095 RRQ vs TLID | 1882s | — | context-only | rejected | **rejected** | Full-screen KLASEMEN standings; no pairing or start. |
| 1096 DEWA vs NAVI | 1884s | — | context-only | rejected | **rejected** | Full-screen KLASEMEN standings; no pairing or start. |
| 1097 EVOS vs GEEK | 2052s | — | context-only | rejected | **rejected** | Full-screen KLASEMEN standings; no pairing or start. |
| 1102 ONIC vs DEWA | 2354s | DEWA only | context-only | context-only | **context-only** | Analyst desk; `DRAFT IN 15:02`; ONIC not visible. |
| 1103 BTR vs EVOS | 2429s | — | context-only | rejected | **rejected** | Full-screen KLASEMEN standings; no pairing or start. |

### 4.3 Pass-2 conclusions

- **13 candidates rejected:** 1044, 1046, 1049, 1054, 1070, 1073, 1089 (300s pre-show countdown/promo, not a match start), 1082 (`GAME 2` already in progress), 1090 (crowd/ad), and 1095, 1096, 1097, 1103 (KLASEMEN standings).
- **6 candidates context-only:** 1042, 1051, 1056, 1067, 1078, 1102. These are series intros, desks, or interviews; none shows a draft board or a `00:00` game clock.
- **1 candidate inconclusive:** 1048; the frame is `M3 - GAME 1` at the analyst desk with `DRAFT PICK IN 03:52`, but the crests cannot be read as team names.
- **No game-1 start was proven.** The pass-2 frames contain no draft phase and no `00:00` game clock.
- **Systemic finding:** the non-null candidate offsets are series-intro or pre-show markers, typically 10–19 minutes before the draft, not game-1 starts. This matches the pass-1 pattern (1106, 1107, 1084, 1094).
- **Rule corrections:** (a) `GAME 2`–`GAME 9` now rejects a game-1 claim, not only `GAME 3`; (b) team names from *other* cards on a multi-match schedule can no longer produce a pairing contradiction; (c) a pre-show/desk segment at a 300s candidate offset is rejected as a game-1 start. Recompute changed 0 frame dispositions and 7 boundary reviews (1082, 1044, 1049, 1054, 1070, 1073, 1089); 1044/1054 also changed pairing from contradicted to unknown/partial.

### 4.4 Unverified draft-countdown leads

These are arithmetic leads computed from visible countdowns. They were **not captured or reviewed** and must not be cited as boundaries:

| Series | Candidate | Visible cue | Candidate + countdown |
|---|---:|---|---:|
| 1042 | 10608s | `DRAFT PICK IN 10:26` | ≈11234s |
| 1048 | 23266s | `DRAFT PICK IN 03:47` | ≈23493s |
| 1051 | 22773s | `DRAFT PICK IN 13:11` | ≈23564s |
| 1078 | 1461s | `DRAFT PICK IN 14:53` | ≈2354s |
| 1102 | 2354s | `DRAFT IN 14:52` | ≈3246s |

A draft screen would confirm the series and show that the candidate offset is early, but it still would not prove game-clock zero. A later capture would be needed to find the actual game-1 start.

## 5. What the frames prove and do not prove

The visual evidence is strong for **series pairing and pre-match state**:

- 1042: BTR (VITALITY) vs GEEK at 10608s, `DRAFT PICK IN 10:26`.
- 1048: `M3 - GAME 1` at 23266s; ONIC/RRQ pairing not legible.
- 1049/1073/1089: the 300s pre-show cards list the expected pairings but are not match starts; the offsets are rejected.
- 1051: GEEK vs EVOS at 22773s, `DRAFT PICK IN 13:16`.
- 1056: RRQ vs BTR analyst desk at 15232s.
- 1067: BTR vs AE interview at 22586s.
- 1078: NAVI pre-match interview at 1461s.
- 1082: BTR vs ONIC in `GAME 2` at 17077s, clock `10:39`.
- 1090: crowd b-roll with a sponsor overlay at 12178s.
- 1095/1096/1097/1103: KLASEMEN standings, not matches.
- Pass-1 confirmations (1084, 1094, 1106, 1107) remain series-intro-only.

It does **not** prove a game-1 start for any series. The frames show pre-match intros with draft countdowns, desks, standings, or in-progress gameplay. A pre-match countdown is not a game start; a still frame cannot prove the continuous transition from the desk to the draft to the game clock. No boundary was marked `visually_verified`.

The 1082 group also shows a capture-order limitation: the three frames read `10:39`, `10:35`, `10:40` despite increasing requested times, so the player did not return strictly monotonic content. This does not affect the `GAME 2` conclusion, but it is another reason not to infer temporal order from nominally ordered stills alone.

## 6. Unresolved items

- **18 null offsets** (no capture target): 1037, 1043, 1058, 1061, 1063, 1064, 1066, 1072, 1079, 1083, 1085, 1087, 1088, 1092, 1093, 1099, 1101, 1104.
- **6 pass-2 candidates remain `context-only`** (1042, 1051, 1056, 1067, 1078, 1102). Their pairings are partly or fully visible, but the offsets are pre-match, not game-1 starts.
- **1 pass-2 candidate remains `inconclusive`** (1048): the pairing cannot be read from the desk frame.
- **The 20 non-null candidates are now all reviewed**: 13 rejected, 6 context-only, 1 inconclusive. There is no remaining non-null capture backlog.
- **Four unvalidated sources** remain partially resolved: w06d01, w07d01, w07d02, w08d02. Some pairings are confirmed, but no full boundary is promoted.
- **No boundary is `visually_verified`.** The ledger's 31 boundary reviews are 18 rejected, 11 context-only, 2 inconclusive, 0 used.
- **`game-offsets.json` is unchanged.** Rejections are recorded in the ledger, not written back as status changes.
- **Historical `visual-review.json` labels** remain the historical "OpenCode multimodal review". They were not relabelled. DeepSeek records are linked by `historical_frame_id` and exact screenshot hash.

## 7. Validation and reproducibility

```text
python tools/validate_visual_reviews.py
python tools/test_visual_review_integrity.py
python tools/audit_visual_evidence.py
python tools/recompute_visual_reviews.py
python tools/validate_game_offsets.py
```

Results:

- Validator: **0 errors, 4 warnings** (1062, 1084, 1106, 1107 are transcript-verified offsets only partially confirmed visually; they remain `boundary_verified` from transcript evidence and were not promoted).
- Visual-review adversarial tests: **21/21 pass** (17 validator tests + 4 boundary-decision regressions).
- Boundary adversarial tests: **14/14 pass**.
- Transcript evidence tests: **18/18 pass**.
- Audit: **125 PNGs, 113 official, 0 hash mismatches, 4 failed captures** (including 3 sidecar-only timeouts).
- Game-offset validator: **0 errors** (27 `boundary_verified`, 26 `pending_validation`, 19 `detected_pending_review`).
- CI semantic check: **pass**.
- CI: `.github/workflows/semantic-check.yml` runs the validator, both adversarial suites, the offset validator, and the inventory check.

## 8. No-human-review attestation

The ledger records `human_review: false`, `reviewer: deepseek`, `review_mode: api-pixel-inspection-only`, and a non-empty API request id for every reviewed frame. No human screenshot inspection, manual visual approval, human-review queue, or human escalation was used. The historical `visual-review.json` reviewer label is preserved as history and is not a DeepSeek review.


## Pass 3 final status

- **P3:** all 18 original null offsets covered — 8 reviewed candidates and 10 documented no-candidate waivers. 1037/1085/1087/1088/1083/1101 are context-only; 1072/1079 were rejected (GAME 2 / schedule rundown); 1086's 31928s candidate was rejected as 1088 game 3 and nulled.
- **P4:** `analysis/evidence/visual-review-status.json` reconciles all 72 series: 20 rejected, 41 context-only, 1 inconclusive, 10 no-candidate waivers, 0 not reviewed, 0 visually verified. It is hash-linked and CI-checked.
- **P5:** 1036 wide probe confirms EVOS vs RRQ but first HUD is `03:08`; no `00:00`; context-only.
- **Remaining:** only §6a box 1 — a visible `00:00` with the correct pairing. No boundary was promoted.


All 23 remaining boundary-verified/unreviewed series were sampled in first-game-feed windows. None contained a same-frame `00:00` with the correct pairing; all are context-only. The derived status now has **0 not-reviewed** series.


**1051 one-second sweep:** 17 frames at 24028–24044s; draft/bumpers only, then paused `00:16` at 24045.6s with no team labels. No `00:00`; no promotion.


**1084 one-second sweep:** 21 frames at 3684-3704s; bumpers and HUD-less map until 3702.5s (`00:17`), then `00:19` with GEEK/BTR at 3704.5s. No `00:00`; no promotion. Token-bounded team matching and related-frame support-only rules were added with regression tests; the 1084 candidate is context-only.


**1083 one-second sweep:** 19 frames at 24398-24416s; player cams and a league-intro bumper until 24413s, then first HUD at 24414.5s with `00:12` and no team labels (`00:15` by 24417.5s). No `00:00`; no promotion. The clock started during the non-game segment.


**1068 one-second sweep:** 29 frames at 2940-2968s; draft HUD, player cams, bench/stage shots, draft comparison, sponsor bumpers, and trophy animation. No gameplay HUD, no game clock, no `00:00`; the first HUD at 3001.5s reads `00:58`. No promotion.


**1041 one-second sweep:** the requested 1152-1198s range is pre-show; the actual first HUD is 2220.5s (`00:17`), not `00:46`. Swept 2200-2251s: pre-match stats, bumpers, first HUD at `00:17` (TLID only), `00:18` with TLID/DEWA, split-screen replay, then `00:34`-`00:46`. No `00:00`; no promotion.


**1040 one-second sweep:** source `src-s18-w01d02`; first HUD 24076.5s (`00:17`), not 24067s or `01:01`. Swept 24055-24121s: draft/stat comparison, bumpers, map flyover, then `00:17` (EVOS prefix only), `00:20` with EVOS/NAVI, split-screen, and `00:33`-`01:02`. No `00:00`; no promotion.


**1038 one-second sweep:** source `src-s18-w01d02`; first clocked HUD 2701.5s (`01:36`), but first game HUD at 2621.4s (`00:17`). Swept 2600-2701s in 102 frames across four operational groups. Pre-game lineup/bumpers until 2620s, then `00:17` (GEEK only), `00:20` with TLID/GEEK, and a continuous count-up to `01:37`. No `00:00`; no promotion.


**1106 one-second sweep:** source `src-s18-w09d03`; first HUD 14600.5s (`00:17`), not the later `01:37` at 14681.5s. Swept 14580-14632s: season intro/bumpers, map showcase, then `00:17` (NAVI only), `00:18` with NAVI/BTR, and a count-up to `00:48`. No `00:00`; no promotion.


**1107 one-second sweep:** source `src-s18-w09d03`; pilot `05:08` at 25491s implied start ~25183s. Swept 25180-25210s: bumpers/cinematics, then first HUD 25200.5s (`00:17`) with ONIC/TLID, `00:18`-`00:22`, then split-screen replay. No `00:00`; no promotion.


**1102 one-second sweep:** source `src-s18-w09d02`; first HUD 3714.4s (`00:17`), not the later `00:34` at 3731.5s. Swept 3694-3732s: pre-match/player cams/bumpers/map, then `00:17` (DEWA only), `00:18` with DEWA/ONIC, `00:19`-`00:22`, split-screen, and `00:28`-`00:35`. No `00:00`; no promotion.


**1069 one-second sweep:** source `src-s18-w05d01`; first HUD 3137.5s (`00:17`), not the later `01:20` at 3201.4s. Swept 3118-3140s: pre-match lineup, hero/player cams, bumpers, map flyover, then `00:17` (GEEK only), `00:18` with GEEK/ONIC, `00:19`. No `00:00`; no promotion.


**1074 one-second sweep:** source `src-s18-w05d03`; first HUD 13443.4s (`00:17`), not the later `02:04` at 13551.1s. Swept 13424-13461s: player cams/sponsor/hero/trophy/map, then `00:17` with ONIC/AE, `00:18`-`00:23`, split-screen replay, and `00:32`-`00:34`. No `00:00`; no promotion.


**1062 one-second sweep:** source `src-s18-w04d02`; existing 2465.2s frame reads `00:19`; actual first HUD 2463.5s (`00:17`). Swept 2444-2466s: draft lineup, hero/player cams, bumpers, map flyover, then `00:17` (DEWA only), `00:18` with DEWA/ONIC, `00:19`-`00:20`. No `00:00`; no promotion.


**1052 one-second sweep:** source `src-s18-w03d01`; plan pairing BTR/NAVI (prompt label GEEK/EVOS was wrong). First HUD 2669.4s (`00:18`), inferred start ~2651.4s. Small groups because 23/24-frame requests stalled. Draft lead-in/bumpers, then `00:18` (NAVI only), `00:19` with BTR/NAVI, `00:20`-`00:23`. No `00:00`; no promotion.


**1098 one-second sweep:** source `src-s18-w08d03`; first HUD 18817.3s (`00:18`), inferred start ~18799.3s. Swept 18797-18820s in 6-frame groups: sponsor/character/trophy/logo bumpers, map views, then `00:18` (ONIC only), `00:19` with RRQ/ONIC, `00:20`-`00:22`. No `00:00`; no promotion.


**1081 one-second sweep:** source `src-s18-w06d03`; first HUD 2958.3s (`00:17`), inferred start ~2941.3s. Swept 2939-2962s in 6-frame groups: player cams, sponsor/mascot/trophy bumpers, then `00:17` with AE/DEWA, `00:18`-`00:21`, split-screen transition. No `00:00`; no promotion.


**1057 one-second sweep:** source `src-s18-w03d03`, pairing NAVI/ONIC. First HUD 2342.4s (`00:17`), inferred start ~2325.4s. Swept 2324-2347s in 6-frame groups: pregame lineup/stat, draft, player cams, bumpers, then `00:17` (NAVI only), `00:18` with NAVI/ONIC, `00:19`-`00:23`. No `00:00`; no promotion.


**1060 one-second sweep:** source `src-s18-w04d01`, pairing NAVI/DEWA. First HUD 2487.4s (`00:17`), inferred start ~2470.4s. Swept 2469-2492s in 6-frame groups: pre-game lineup, draft/bumpers, map transition, then `00:17` (NAVI only), `00:19` with NAVI/DEWA, `00:20`-`00:22`. No `00:00`; no promotion.
