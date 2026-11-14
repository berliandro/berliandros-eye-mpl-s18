# Transcript pipeline — remaining batch 5 summary

**Date:** 2026-11-13
**Status:** complete.

| Source | Match | Segments | Observations | Accepted | Needs review |
|---|---|---:|---:|---:|---:|
| `src-s18-w06d01` | 1076 ONIC vs GEEK | 100 | 12 | 5 | 7 |
| `src-s18-w06d02` | 1080 BTR vs TLID | 91 | 12 | 5 | 7 |
| `src-s18-w06d03` | 1081 AE vs DEWA | 99 | 12 | 5 | 7 |
| **Total** | | **290** | **36** | **15** | **21** |

All ledgers pass `tools/validate_transcript_ledger.py` with 0 errors / 0 warnings.

## Consolidation

- `analysis/matches/1076-onic-vs-geek.md`
- `analysis/matches/1080-tlid-vs-btr.md`
- `analysis/matches/1081-dewa-vs-ae.md`

## Notes

- Two weak context-quote/statistic records in 1076 were left `needs_review`; the
  accepted set uses stronger draft and vision records instead.
- 1080 and 1081 accepted five tactical records each plus one database record.
- No raw transcript or database mutation; no visual claims promoted.
