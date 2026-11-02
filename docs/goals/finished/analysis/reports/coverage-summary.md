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
- Observations: **18**
- Insights: **3** (1 `cross-checked`, 2 `partially-supported`)
- Audits: **1** (`AUD-1037-01`, verdict `partially supported`)

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
