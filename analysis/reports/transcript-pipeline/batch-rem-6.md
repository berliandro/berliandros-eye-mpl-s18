# Transcript pipeline — remaining batch 6 summary

**Date:** 2026-11-13
**Status:** complete.

| Source | Match | Segments | Observations | Accepted | Needs review |
|---|---|---:|---:|---:|---:|
| `src-s18-w07d01` | 1084 GEEK vs BTR | 96 | 12 | 5 | 7 |
| `src-s18-w07d02` | 1087 BTR vs RRQ | 102 | 12 | 5 | 7 |
| `src-s18-w07d03` | 1091 ONIC vs NAVI | 92 | 10 | 5 | 5 |
| **Total** | | **290** | **34** | **15** | **19** |

All ledgers pass `tools/validate_transcript_ledger.py` with 0 errors / 0 warnings.

## Consolidation

- `analysis/matches/1084-geek-vs-btr.md`
- `analysis/matches/1087-btr-vs-rrq.md`
- `analysis/matches/1091-onic-vs-navi.md`

## Notes

- 1084 `TOBS-1084-G1-010` was excluded from acceptance because the quote’s kill
  direction was ambiguous; stronger map/objective/draft records were used.
- 1091 is mostly desk/draft commentary; accepted records are marked analysis or
  post-match, not gameplay fact.
- No raw transcript or database mutation; no visual claims promoted.
