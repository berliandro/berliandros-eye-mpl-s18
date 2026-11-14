# MPL S18 transcript pipeline — coverage

**Date:** 2026-11-13
**Status:** 27/27 source ledgers validated; 313 accepted observations consolidated into match reports and 60 non-match pages; 0 remain for review, 50 rejected.

## Summary

| Metric | Count |
|---|---:|
| Sources processed | 27 |
| Sources complete | 24 |
| Sources partial | 3 |
| Source ledgers validated | 27 |
| Validation errors | 0 |
| Observations extracted | 363 |
| Accepted observations | 313 |
| Needs review | 0 |
| Rejected observations | 50 |
| Resolved unresolved references | 5 |
| Match reports updated | 27 |
| Accepted observations cross-filed outside match reports | 313 / 313 |
| Non-match cross-destination links | 979 |
| Non-match pages | 60 |
| Routing errors | 0 |
| Accepted IDs missing from match reports | 0 |

Partial sources are `src-s18-w02d03` (1050, intro/interview window), `src-s18-w07d03` (1091, desk/draft-heavy), and `src-s18-w08d02` (1094, desk/commentary-heavy). These are marked partial rather than counted as full gameplay coverage.

## Non-match routing

Every accepted observation has at least one cross-destination outside its match report. The match report remains the primary destination and retains the full quote/provenance.

| Category | Pages | Links |
|---|---:|---:|
| Players | 24 | 83 |
| Teams | 9 | 508 |
| Heroes | 21 | 75 |
| Strategy | 6 | 313 |
| **Total** | **60** | **979** |

## Per-source status

| Source | Match | Status | Observations | Accepted | Routed | Needs review | Rejected | Validation |
|---|---|---:|---:|---:|---:|---:|---:|---|
| src-s18-w01d01 | 1036 | complete | 29 | 19 | 19 | 0 | 10 | 0 |
| src-s18-w01d02 | 1039 | complete | 22 | 21 | 21 | 0 | 1 | 0 |
| src-s18-w01d03 | 1041 | complete | 12 | 9 | 9 | 0 | 3 | 0 |
| src-s18-w02d01 | 1045 | complete | 12 | 11 | 11 | 0 | 1 | 0 |
| src-s18-w02d02 | 1047 | complete | 12 | 9 | 9 | 0 | 3 | 0 |
| src-s18-w02d03 | 1050 | partial | 10 | 9 | 9 | 0 | 1 | 0 |
| src-s18-w03d01 | 1052 | complete | 12 | 10 | 10 | 0 | 2 | 0 |
| src-s18-w03d02 | 1055 | complete | 21 | 17 | 17 | 0 | 4 | 0 |
| src-s18-w03d03 | 1057 | complete | 12 | 12 | 12 | 0 | 0 | 0 |
| src-s18-w04d01 | 1060 | complete | 11 | 7 | 7 | 0 | 4 | 0 |
| src-s18-w04d02 | 1062 | complete | 11 | 11 | 11 | 0 | 0 | 0 |
| src-s18-w04d03 | 1065 | complete | 11 | 9 | 9 | 0 | 2 | 0 |
| src-s18-w05d01 | 1069 | complete | 12 | 12 | 12 | 0 | 0 | 0 |
| src-s18-w05d02 | 1071 | complete | 11 | 11 | 11 | 0 | 0 | 0 |
| src-s18-w05d03 | 1074 | complete | 11 | 11 | 11 | 0 | 0 | 0 |
| src-s18-w06d01 | 1076 | complete | 12 | 12 | 12 | 0 | 0 | 0 |
| src-s18-w06d02 | 1080 | complete | 12 | 10 | 10 | 0 | 2 | 0 |
| src-s18-w06d03 | 1081 | complete | 12 | 9 | 9 | 0 | 3 | 0 |
| src-s18-w07d01 | 1084 | complete | 12 | 10 | 10 | 0 | 2 | 0 |
| src-s18-w07d02 | 1087 | complete | 12 | 12 | 12 | 0 | 0 | 0 |
| src-s18-w07d03 | 1091 | partial | 10 | 10 | 10 | 0 | 0 | 0 |
| src-s18-w08d01 | 1068 | complete | 12 | 11 | 11 | 0 | 1 | 0 |
| src-s18-w08d02 | 1094 | partial | 12 | 11 | 11 | 0 | 1 | 0 |
| src-s18-w08d03 | 1098 | complete | 12 | 12 | 12 | 0 | 0 | 0 |
| src-s18-w09d01 | 1100 | complete | 12 | 8 | 8 | 0 | 4 | 0 |
| src-s18-w09d02 | 1102 | complete | 12 | 6 | 6 | 0 | 6 | 0 |
| src-s18-w09d03 | 1107 | complete | 24 | 24 | 24 | 0 | 0 | 0 |

## Artifacts

- Segment ledgers: `analysis/evidence/transcript-segments/`
- Observation ledgers: `analysis/evidence/transcript-observations/`
- Routing manifest: `analysis/evidence/transcript-routing.json`
- Review decisions: `analysis/evidence/transcript-review-decisions.jsonl`
- Job plan: `analysis/evidence/transcript-pipeline-plan.json`
- Run reports: `analysis/reports/transcript-pipeline/`

## Rules preserved

- Raw transcripts and `data/mpl_id_s18.db` were not modified.
- Every accepted observation has an exact quote, quote hash, raw line range, cue range or explicit null, source link, and claim type.
- Statistics use `tools/stats_query.py` provenance.
- Visual proof status is unchanged; no screenshots or visual claims were promoted.
