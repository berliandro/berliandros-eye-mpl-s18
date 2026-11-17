# Evidence store reconciliation

**Decision:** the 27-source transcript observation ledgers are the canonical store for broadcast evidence. The older `analysis/evidence/pilot-ledger.jsonl` is a frozen claim-level pilot store, not a duplicate.

## Canonical stores

| Store | Rows | Status | Scope |
|---|---:|---|---|
| `analysis/snapshots/mpl_id_s18_regular.db` | 174 games | canonical | source-reported regular-season schedule and scoreboard snapshot |
| `analysis/evidence/transcript-observations/` | 368 | canonical | 27 sources; atomic quote-level observations (313 accepted) |
| `analysis/evidence/transcript-segments/` | 3010 | canonical | 27 bounded segment ledgers |
| `analysis/evidence/pilot-ledger.jsonl` | 234 | frozen legacy | 3 pilot series; claim-level observations, insights and audits |
| `analysis/evidence/deepseek-visual-reviews.json` | see ledger | canonical for visual claims | DeepSeek reviews; 0 visually verified |

## Why the pilot ledger is not merged

- Pilot records are claim-level (`OBS-1036-DRAFT`, `INS-*`, `AUD-*`); staging records are quote-level (`TOBS-*`). A one-to-one alias would be false precision.
- Series 1037 has **no transcript source**. Its pilot observations are the only semantic evidence for that series, so the store cannot be discarded.
- The pilot ledger also holds the 8 pilot segments and the visual/database references used by the pilot audits.
- No record IDs are shared between the two stores.

## Rules for future work

1. New transcript observations go to `analysis/evidence/transcript-observations/` and must pass `tools/validate_transcript_ledger.py`.
2. Never append new records to `pilot-ledger.jsonl`.
3. Cite transcript records by `TOBS-*` id and pilot records as pilot-store records; keep the store qualifier.
4. Statistics always come from `tools/stats_query.py` with `query_id` and snapshot hash.
5. Visual claims come only from the DeepSeek visual ledger and require a same-frame literal `00:00`.

## Known ID variant

- 21 observation records (17 accepted) from `src-s18-w03d02` use `TOBS-src-s18-w03d02-1055-g1-<seq>` instead of `TOBS-<match>-G<game>-<seq>`.
- They are schema-valid (`TOBS-` prefix) and referenced from Markdown. Do not rename them; use the canonical form for new records.

## Evidence

- Machine-readable manifest: `analysis/evidence/canonical-store.json`
- Coverage matrix: `analysis/reports/coverage-matrix.md`
- Validator: `tools/validate_transcript_ledger.py`
