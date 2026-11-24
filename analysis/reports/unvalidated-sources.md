# Unvalidated game-offset sources — DeepSeek visual review status

Four of 27 sources could not be boundary-validated automatically because their captions contain no clean single-series introduction line (no "match antara X dan Y" / "pertandingan antara X melawan Y" cue). Their offsets remain heuristic and must not be used for timestamp citations until visually verified. No human review is used; DeepSeek is the sole visual reviewer.

| Source | Broadcast date | Series in DB | Heuristic offset(s) | Why not validated |
|---|---|---|---|---|
| `src-s18-w06d01` | 2026-09-18 | 1075 RRQ vs DEWA, 1076 ONIC vs GEEK, 1077 DEWA vs EVOS | all @ 2425s | Only schedule overview at 2486s ("Onic Geek, Dewa EVOS dan RRQ Dewa"); no single-series intro. |
| `src-s18-w07d01` | 2026-10-02 | 1084 GEEK vs BTR (validated @ 2043s), 1085 DEWA vs TLID | 1084 @ 2043s, 1085 @ 12883s candidate | 1084 series intro visually confirmed; 1085 candidate from the 12883s Team Liquid player-room cue (DEWA/TLID countdown `14:48`), context-only, not promoted. |
| `src-s18-w07d02` | 2026-10-03 | 1086 AE vs NAVI, 1087 BTR vs RRQ, 1088 GEEK vs DEWA | 1086 @ null (31928s rejected), 1087 @ 13276s candidate, 1088 @ 23569s candidate | 1087/1088 candidates from explicit `match kedua`/`match ketiga` cues; both pairings confirmed, context-only, not promoted. 1086's 31928s candidate was 1088 game 3 and was rejected/nulled. |
| `src-s18-w08d02` | 2026-10-09 | 1094 EVOS vs ONIC, 1095 RRQ vs TLID, 1096 DEWA vs NAVI | 1094 @ 1585s | Only schedule overview at 1939s ("EVOS versus ONIC untuk match pembuka"); no single-series intro. |

## Status (updated 2026-11-03, DeepSeek pass 3)

Automated transcript-level boundary review was attempted for all 4 sources using multiple strategies (team-name pairing, series-result announcements, "match pertama/kedua/ketiga" with team names, schedule overviews, lineup announcements, and frame capture). None yielded a clean single-series boundary introduction for every unvalidated series. DeepSeek then reviewed the captured frames directly. The visual findings are below. These 4 sources remain `pending_validation` / `detected_pending_review` for the unresolved series; their unconfirmed offsets must not be used for timestamp citations. Across the other sources, 22 of 27 have at least one `boundary_verified` series; `src-s18-w01d01` remains `candidate_detected` and `src-s18-w09d02` is quarantined.

### DeepSeek visual findings

| Source | Frames reviewed | Finding | Effect |
|---|---|---|---|
| w06d01 | 6 frames at 00:40:00 and 00:40:25 | The 00:40:25 frames are the full-screen **KLASEMEN** standings table, not a match start. The 00:40:00 frames show `M41 - GAME 1` with a GEEK wordmark on the right; the left crest is not legible as a team name, so the full ONIC vs GEEK pairing is not established. | Candidates 1075/1076/1077 @2425s **rejected**. No promotion. |
| w07d01 | 3 frames at 00:34:00 + crop; 5 frames at 12878-12943 | 1084 reads `M49 - GAME 1`, GEEK vs VITALITY, `DRAFT PICK IN 15:51`. 1085 reads DEWA vs TLID with `DRAFT PICK IN 14:48`. | 1084 and 1085 pairings **confirmed (context-only)**; no `00:00`; neither promoted. |
| w07d02 | 3 at 08:52:00, 3 at 00:33:19, 4 at 13272-13337, 4 at 23564-23629 | 1087 shows the BTR/RRQ stage introduction; 1088 shows GEEK vs DEWA with `DRAFT PICK IN 14:51`. The 08:52 frames are 1088 game 3, not 1086. | 1086 @31928s **rejected/nulled**; 1087/1088 pairings **confirmed (context-only)**; no `00:00`, no promotion. |
| w08d02 | 9 frames: 00:26:00, 00:26:25 (pass 1) and 00:31:22, 00:31:24 (pass 2) | The 00:26:00 ticker names `Match 1: EVOS vs ONIC`; the 00:26:25 frames show `M59 - GAME 1`, `DRAFT PICK IN 17:00`. The pass-2 00:31:22/00:31:24 frames are a full-screen **KLASEMEN** standings table, with all nine teams listed as separate rows. | 1094 series pairing **confirmed (context-only)**; 1095 @1882s and 1096 @1884s **rejected** (standings, not match starts). |

### Attempted resolution summary

| Source | Strategy attempted | Result |
|---|---|---|
| w06d01 | Team-name pairing (DEWA+RRQ, ONIC+GEEK, DEWA+EVOS), "match pertama/pembuka" with team names, schedule overview, frame capture | Only schedule overview at 2486s; 6 frames reviewed. 2425s is standings, not a start. |
| w07d01 | Team-name pairing (GEEK+BTR, DEWA+TLID), "match pertama" with team names, lineup announcements, frame capture | Series intro at 2043s for 1084 (GEEK vs BTR, visually confirmed). No clean intro for 1085. |
| w07d02 | Team-name pairing (AE+NAVI, BTR+RRQ, GEEK+DEWA), "match pertama/pembuka" with team names, frame capture | 31928s is GEEK vs DEWA game 3 (1088), not 1086. No team-paired intro for 1087/1088. |
| w08d02 | Team-name pairing (EVOS+ONIC), "match" with team names, schedule overview, frame capture | 1094 pairing confirmed from the ticker; 1095/1096 captured in pass 2 and rejected as KLASEMEN standings. |

### DeepSeek frame capture status

Frame capture was attempted for all 4 remaining unvalidated sources (27 frames total: 21 in pass 1 plus 6 pass-2 frames for 1095/1096, with sidecars). DeepSeek reviewed the relevant frames in passes 1–2; the full results are in `analysis/evidence/deepseek-visual-reviews.json`. All captured frames remain `captured`/`reviewed`, not `visually_verified`. Frame sidecars are in `analysis/cache/video-frames/`. All targets are documented in `docs/goals/finished/mpl-s18-visual-proof-deepseek-handoff.md`.

**Status: partially resolved.** The visual review confirmed 1084/1085/1087/1088 pairings and rejected 1086/1095/1096 as non-match frames. The 1085/1087/1088 candidates are context-only and unpromoted; no same-frame `00:00` was found. The remaining null series must not be cited with timestamps until a later DeepSeek pass finds a start cue. No human review is permitted.

### Final automated attempt summary (2026-11-02)

| Source | Strategies tried | Result |
|---|---|---|
| w06d01 | Team-name pairing (DEWA+RRQ, ONIC+GEEK, DEWA+EVOS), "match pertama/pembuka" with team names, schedule overview, frame capture @ 00:40:00 | No clean single-series intro. 2425s is KLASEMEN standings. |
| w07d01 | Team-name pairing (GEEK+BTR, DEWA+TLID), "match pertama" with team names, lineup announcements, frame capture @ 00:34:00 | Series intro at 2043s for 1084 (GEEK vs BTR, visually confirmed). No clean intro for 1085. |
| w07d02 | Team-name pairing (AE+NAVI, BTR+RRQ, GEEK+DEWA), "match pertama/pembuka" with team names, frame capture @ 08:52:00 | 31928s is GEEK vs DEWA game 3 (1088), not 1086. |
| w08d02 | Team-name pairing (EVOS+ONIC), "match" with team names, schedule overview, frame capture @ 00:26:00 and 00:31:22/00:31:24 | 1094 pairing confirmed from ticker; 1095/1096 rejected as KLASEMEN standings. |

### Frame capture inventory

| Source | Timestamps captured | Sidecar files | Status |
|---|---|---|---|
| w06d01 | 00:40:00, 00:40:25 (×2 around) | 6 sidecars | DeepSeek reviewed; 2425s rejected |
| w07d01 | 00:34:00, 03:34:38-03:35:43 | 3 + 5 sidecars + scoreboard crop | DeepSeek reviewed; 1084/1085 pairings confirmed (context-only) |
| w07d02 | 08:52:00, 00:33:19, 03:41:12-03:42:17, 06:32:44-06:33:49 | 14 sidecars | DeepSeek reviewed; 1086 rejected, 1087/1088 confirmed (context-only) |
| w08d02 | 00:26:00, 00:26:25, 00:31:22, 00:31:24 | 12 sidecars | DeepSeek reviewed; 1094 pairing confirmed; 1095/1096 rejected |

All sidecars are in `analysis/cache/video-frames/` (Git-ignored). DeepSeek records are in `analysis/evidence/deepseek-visual-reviews.json`; the review report is `analysis/reports/visual-proof-deepseek-review.md`.
