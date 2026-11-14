# Transcript pipeline — remaining batch 4 summary

**Date:** 2026-11-13
**Status:** complete.

| Source | Match | Segments | Observations | Accepted | Needs review |
|---|---|---:|---:|---:|---:|
| `src-s18-w05d01` | 1069 GEEK vs ONIC | 98 | 12 | 5 | 7 |
| `src-s18-w05d02` | 1071 AE vs RRQ | 96 | 11 | 5 | 6 |
| `src-s18-w05d03` | 1074 ONIC vs AE | 93 | 11 | 5 | 6 |
| **Total** | | **287** | **34** | **15** | **19** |

All ledgers pass `tools/validate_transcript_ledger.py` with 0 errors / 0 warnings.

## Consolidation

- `analysis/matches/1069-geek-vs-onic.md`
- `analysis/matches/1071-ae-vs-rrq.md`
- `analysis/matches/1074-onic-vs-ae.md`

## Notes

- Player/hero ASR variants were kept in commentary text rather than forced into entity IDs.
- Statistic records carry database provenance; context quotes are not treated as the source of numbers.
- No raw transcript or database mutation; no visual claims promoted.
