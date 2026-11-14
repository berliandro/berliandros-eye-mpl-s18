# Transcript pipeline — batch 3 summary

**Date:** 2026-11-13
**Status:** complete.

| Source | Match / game | Segments | Observations | Accepted | Needs review | Validation |
|---|---|---:|---:|---:|---:|---|
| `src-s18-w09d03` | 1107 ONIC vs TLID, game 1 | 116 | 24 | 10 | 14 | 0 errors / 0 warnings |
| `src-s18-w01d02` | 1039 DEWA vs RRQ, game 1 | 151 | 22 | 10 | 12 | 0 errors / 0 warnings |
| `src-s18-w03d02` | 1055 AE vs EVOS, game 1 | 121 | 21 | 10 | 11 | 0 errors / 0 warnings |
| **Total** | | **388** | **67** | **30** | **37** | **0 errors** |

## Coverage

- Three different broadcast days and commentary styles.
- Three different match reports updated:
  `1107-onic-vs-tlid.md`, `1039-dewa-vs-rrq.md`, `1055-ae-vs-evos.md`.
- Every accepted statistic has `database_refs` from `tools/stats_query.py` and
  snapshot `mpl-s18-db-20c5ea2c51f3`.
- Every accepted observation has an exact quote, quote hash, raw line range, cue
  range, source link, and claim-type label.
- No raw transcript or database mutation.
- No visual claims promoted.

## Issues found and fixed

- Cue timestamps initially pointed at segment starts; all observations were
  tightened to the exact quote lines.
- Four 1055 claims outran their quotes; they were narrowed before acceptance.
- 1039 `TOBS-1039-G1-020` mixed `Q-GAMES` and `Q-TEAM-GAMES` scopes; the claim was
  split and team statistics moved to `TOBS-1039-G1-022`.

## Cost

- Model: `opencode-go/beam-free#max`, free.
- Token usage not exposed by the subagent runtime.
- Wall time for the three source runs: roughly 20–30 minutes including
  consolidation and validation.
