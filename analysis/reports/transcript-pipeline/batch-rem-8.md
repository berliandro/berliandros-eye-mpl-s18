# Transcript pipeline — remaining batch 8 summary

**Date:** 2026-11-13
**Status:** complete.

| Source | Match | Segments | Observations | Accepted | Needs review |
|---|---|---:|---:|---:|---:|
| `src-s18-w09d01` | 1100 NAVI vs RRQ | 96 | 12 | 5 | 7 |
| `src-s18-w09d02` | 1102 ONIC vs DEWA | 102 | 12 | 5 | 7 |
| **Total** | | **198** | **24** | **10** | **14** |

Both ledgers pass `tools/validate_transcript_ledger.py` with 0 errors / 0 warnings.

## Fixes during batch

- 1100 `TOBS-1100-G1-06` had an unsupported quote and was removed.
- 1100 `TOBS-1100-G1-07` was corrected to the exact multi-line quote.
- 1102 `TOBS-1102-G1-12` pointed at a nonexistent segment; it was repointed to
  the real segment and quote.
- Two overbroad claims were narrowed before acceptance.

## Consolidation

- `analysis/matches/1100-rrq-vs-navi.md`
- `analysis/matches/1102-dewa-vs-onic.md`

No raw transcript or database mutation; no visual claims promoted.
