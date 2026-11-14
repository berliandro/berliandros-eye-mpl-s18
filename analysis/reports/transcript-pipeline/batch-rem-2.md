# Transcript pipeline — batch 2 summary

**Date:** 2026-11-13
**Status:** complete; 1050 is partial coverage.

| Source | Match | Segments | Observations | Accepted | Needs review | Status |
|---|---|---:|---:|---:|---:|---|
| `src-s18-w02d03` | 1050 ONIC vs BTR | 45 | 10 | 5 | 5 | partial — intro/interview only |
| `src-s18-w03d01` | 1052 BTR vs NAVI | 100 | 12 | 5 | 7 | complete |
| `src-s18-w03d03` | 1057 NAVI vs ONIC | 99 | 12 | 5 | 7 | complete |
| **Total** | | **244** | **34** | **15** | **19** | |

All three ledgers pass `tools/validate_transcript_ledger.py` with 0 errors and 0 warnings.

## Consolidation

- `analysis/matches/1050-onic-vs-btr.md`
- `analysis/matches/1052-navi-vs-btr.md`
- `analysis/matches/1057-navi-vs-onic.md`

## Notes

- 1050’s window contains only intro/interview material and database facts; it is
  marked `partial`, not silently treated as full gameplay coverage.
- 1052 `TOBS-1052-G1-006` was narrowed to the free-Lord claim supported by the
  quote.
- Statistic records carry `database_refs`; context quotes are not treated as the
  source of the numbers.
- No raw transcript or database mutation; no visual claims promoted.
