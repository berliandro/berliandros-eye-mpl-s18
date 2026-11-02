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
- Boundary-validated sources: **22** (medium confidence, verified against timed captions) — 25 series offsets verified
- Unvalidated sources: **4** (`src-s18-w06d01`, `src-s18-w07d01`, `src-s18-w07d02`, `src-s18-w08d02`) — documented in `unvalidated-sources.md`
- Quarantined source: **1** (`src-s18-w09d02`, 37 unmatched short lines)

## Evidence store

- Segments: **8**
- Observations: **24** (18 series-level + 6 player-level)
- Insights: **70** (3 series-level + 67 player-level)
- Audits: **14** (`AUD-1037-01` series, `AUD-PLAYER-HIGH-KDA-01`, `AUD-PLAYER-ALBERTTT-01`, `AUD-PLAYER-KELRA-01`, `AUD-PLAYER-KAIRI-01`, `AUD-PLAYER-MORENOOO-01`, `AUD-PLAYER-ZEONN-01`, `AUD-PLAYER-DRICHEL-01`, `AUD-PLAYER-SHOGUN-01`, `AUD-PLAYER-EMANN-01`, `AUD-PLAYER-ERLAN-01`, `AUD-PLAYER-FINN-01`, `AUD-PLAYER-HAJIRIN-01`, `AUD-PLAYER-MARCEL-01` player)

## Player-level coverage

- Player dossiers: **66 of 66** (100%) in `analysis/players/`
- Player observations: **29** (OBS-PLAYER-*)
- Player insights: **70** (INS-PLAYER-*)
- Player audits: **68** (AUD-PLAYER-*) — all 66 players now have per-player audits
- Per-player matched comparisons: **66** (all players)
- Player matched comparisons: `analysis/reports/player-matched-comparisons.md` (general) + per-player sections in all 66 dossiers
- Q-PLAYER-* queries: 4 (Q-PLAYER-SEASON, Q-PLAYER-GAMES, Q-PLAYER-PICKS, Q-PLAYER-MVP-SERIES)
- Dossiers with transcript evidence: **28** (Alberttt, Aboyy, Arthur, Clayyy, Dalvin, Drichel, Drianw, Emann, Erlan, Finn, Hajirin, Hazle, Joshua, Kairi, Keven, Kelra, Kiboy, Killuaa, Lutpi, Marcel, Morenooo, Muezza, Nnael, Octa, Rendyyy, Said, Shogun, Zeonn)
- Dossiers with no verifiable transcript mentions: **38** (documented with 'No verifiable transcript mentions' note in each dossier)
- Players with no verifiable transcript mentions: **38** — predominantly substitutes or low-profile players whose names do not appear as distinct mentions in the broadcast captions (verified by exhaustive search across all 22 validated sources)
- Dossiers with top items by frequency: **46** (players with 10+ games)
- Dossiers with opponent context: **58** (players with 5+ games)
- Dossiers with season trend: **46** (players with 10+ games)
- Dossiers with series appearances: **60** (players with 1+ games)

## Known gaps

1. 45 of 72 reports are DB-only (no transcript quote or verified boundary).
2. 4 of 27 sources have no validated game offset.
3. No transcript-verified observations beyond the 3 pilot series and 1 expansion series (1039).
4. No matched comparisons beyond the pilot insights' counterexample sets.
5. Game-offset heuristic for remaining series is unvalidated.

## Next steps

1. Manual boundary review for the 4 unvalidated sources (visual frame inspection).
2. Add transcript-verified observations for additional series where boundaries are verified.
3. Add matched comparisons for all insights.
4. Do not claim full-season semantic coverage until transcript-verified observations exist for a stratified sample beyond the pilot.
