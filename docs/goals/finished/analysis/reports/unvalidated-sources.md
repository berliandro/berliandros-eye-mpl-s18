# Unvalidated game-offset sources — manual review required

Four of 27 sources could not be boundary-validated automatically because their captions contain no clean single-series introduction line (no "match antara X dan Y" / "pertandingan antara X melawan Y" cue). Their offsets remain heuristic and must not be used for timestamp citations until manually verified.

| Source | Broadcast date | Series in DB | Heuristic offset(s) | Why not validated |
|---|---|---|---|---|
| ~~`src-s18-w04d02`~~ | 2026-09-05 | 1062 DEWA vs ONIC (validated @ 2460s), 1063 EVOS vs BTR, 1064 AE vs GEEK | — | Validated: boundary at 2460s ("match pertama ya. Dewa United versus ONIC"). |
| `src-s18-w06d01` | 2026-09-18 | 1075 DEWA vs RRQ, 1076 ONIC vs GEEK, 1077 DEWA vs EVOS | all @ 2425s | Only schedule overview at 2486s ("Onic Geek, Dewa EVOS dan RRQ Dewa"); no single-series intro. |
| `src-s18-w07d01` | 2026-10-02 | 1084 GEEK vs BTR, 1085 DEWA vs TLID | 1084 @ 8849s | Lineup announcement at 2686s for BTR; no clean series intro for 1085. |
| `src-s18-w07d02` | 2026-10-03 | 1086 AE vs NAVI, 1087 BTR vs RRQ, 1088 GEEK vs DEWA | 1086 @ 31928s (likely wrong) | Only "match pembukaan" cues at 1999s/3694s; no team-paired intro. |
| `src-s18-w08d02` | 2026-10-09 | 1094 EVOS vs ONIC, 1095 RRQ vs TLID, 1096 DEWA vs NAVI | 1094 @ 1585s | Only schedule overview at 1939s ("EVOS versus ONIC untuk match pembuka"); no single-series intro. |

## What is needed to resolve

1. Manual review of the broadcast around each heuristic offset to find the actual series start (loading screen, caster intro, scoreboard).
2. Optional: use `tools/video_frames.py` to capture frames around candidate timestamps for visual confirmation of team names/scoreboard.
3. Update `game-offsets.json` with verified offsets and set `verified_by` once confirmed.

## Status

These 5 sources remain `pending_validation` / `detected_pending_review`. Their offsets must not be used for timestamp citations. The other 22 of 27 sources are `boundary_verified`.
