# Transcript pipeline — batch 1 summary

**Date:** 2026-11-13
**Status:** complete.

| Source | Match | Segments | Observations | Accepted | Needs review | Validation |
|---|---|---:|---:|---:|---:|---|
| `src-s18-w01d03` | 1041 TLID vs DEWA | 100 | 12 | 5 | 7 | 0 errors / 0 warnings |
| `src-s18-w02d01` | 1045 BTR vs DEWA | 95 | 12 | 5 | 7 | 0 errors / 0 warnings |
| `src-s18-w02d02` | 1047 NAVI vs GEEK | 95 | 12 | 5 | 7 | 0 errors / 0 warnings |
| **Total** | | **290** | **36** | **15** | **21** | **0 errors** |

## Consolidation

- `analysis/matches/1041-tlid-vs-dewa.md`
- `analysis/matches/1045-dewa-vs-btr.md`
- `analysis/matches/1047-navi-vs-geek.md`

Each accepted observation has an exact quote, quote hash, raw line range, cue
range, source link, claim type and confidence. Statistic records carry
`database_refs` from `tools/stats_query.py` and snapshot
`mpl-s18-db-20c5ea2c51f3`.

## Notes

- 1041 `TOBS-1041-G1-008` was narrowed from “game closing out” to the
  turtle-specific claim supported by the quote.
- ASR name variants remain commentary/context; no player IDs were invented.
- No raw transcript or database mutation; no visual claims promoted.
