# Coverage summary — semantic analysis (MPL ID S18)

**Last updated:** 2026-11-02 (final expansion pass)

## Series coverage

- Total completed regular-season series: **72**
- Curated series reports: **72 of 72 (100%)**
- Coverage: **72/72 (100%)**

All 72 series now have curated reports in `analysis/matches/`. See `analysis/index.md` for the full linked list.

- Pilot (transcript-verified, full evidence): **3** (1036, 1037, 1107)
- Expansion (source-mapped, boundary-verified): **25** (1038, 1039, 1040, 1041, 1045, 1047, 1050, 1052, 1053, 1055, 1059, 1060, 1062, 1065, 1068, 1069, 1071, 1074, 1080, 1081, 1084, 1091, 1098, 1100, 1106)
- DB-only (boundary unverifiable): **44** (all remaining series)

## Source coverage

- Total broadcast sources: **27**
- Sources containing at least one child series row marked `boundary_verified`: **22/27**; those rows total **26/72** series. This is a caption/metadata state, not DeepSeek visual proof.
- Series offset states in `game-offsets.json`: **26 boundary_verified**, **24 detected_pending_review**, **22 pending_validation**.
- Series missing `start_seconds`: **14/72**; series missing `end_seconds`: **72/72**.
- Source-level `validation_status`: **pending for all 27/27 sources**. The source-level aggregate has not yet been reconciled with child-series statuses.
- Transcript-alignment quarantine: **1** (`src-s18-w09d02`, 37 unmatched short lines); it remains excluded from timestamp citations regardless of screenshot review.

## Evidence store

- Segments: **8**
- Observations: **24** (18 series-level + 6 player-level)
- Insights: **6** (3 series-level + 3 player-level)
- Audits: **2** (`AUD-1037-01` series, `AUD-PLAYER-HIGH-KDA-01` player)

## Player-level coverage

- Player dossiers: **66 of 66** (100%) in `analysis/players/`
- Player observations: **6** (OBS-PLAYER-*)
- Player insights: **3** (INS-PLAYER-*)
- Player audits: **1** (AUD-PLAYER-HIGH-KDA-01)
- Player matched comparisons: `analysis/reports/player-matched-comparisons.md`
- Q-PLAYER-* queries: 4 (Q-PLAYER-SEASON, Q-PLAYER-GAMES, Q-PLAYER-PICKS, Q-PLAYER-MVP-SERIES)

## Known gaps

1. **44 of 72** report files are categorized DB-only in the series-coverage breakdown; report existence is not semantic evidence.
2. All **27/27** source-level offset validation statuses remain pending; 14 series starts and all 72 series ends are null in the current offset manifest.
3. No transcript-verified observations beyond the 3 pilot series and 1 expansion series (1039).
4. No matched comparisons beyond the pilot insights' counterexample sets.
5. Game-offset heuristic for remaining series is unvalidated.

## Next steps

1. Generate screenshot targets from the live offset manifest and run automated DeepSeek visual review for series/game identity and boundaries. No human visual-review stage is permitted; inconclusive targets remain quarantined.
2. Add transcript-verified observations for additional series where source alignment and boundaries are sufficiently supported.
3. Add matched comparisons for all insights.
4. Do not claim full-season semantic coverage until transcript-verified observations exist for a stratified sample beyond the pilot.

For all screenshot-based work, follow [`../../docs/goals/active/mpl-s18-visual-proof-deepseek-handoff.md`](../docs/goals/active/mpl-s18-visual-proof-deepseek-handoff.md).
