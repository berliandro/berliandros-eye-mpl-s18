# Analysis index

## Status

- Corpus imported: **27 files / 9,682,086 bytes**, SHA-256 verified **27/27**, conflicts **0**.
- Native transcript timestamps: **0**.
- Verified pilot videos: **2/27** (`src-s18-w01d01`, `src-s18-w09d03`).
- Timed alignments: **2/2** at 9,104 and 12,273 caption lines.
- Pilot series: **3** — 1036, 1037, 1107.
- Evidence: **8 segments / 18 observations / 3 insights / 1 audit**.
- Visual review: **6 used frames** (5 gameplay + 1 post-game context), **1 rejected promo**, **1 failed frame**.
- Full-season coverage: **no**.

## Start here

1. [`README.md`](README.md) — scope, safety, reproduction commands.
2. [`reports/corpus-inventory.md`](reports/corpus-inventory.md) — what was imported, timestamp/video coverage, parsing risks.
3. [`reports/database-inventory.md`](reports/database-inventory.md) — DB coverage, joins, and the `matches.winner` orientation warning.
4. [`reports/pilot-quality-report.md`](reports/pilot-quality-report.md) — pilot coverage, validation results, gaps.
5. [`coaching/pilot-coaching-brief.md`](coaching/pilot-coaching-brief.md) — the three practical prep points.

## Pilot series

- [`matches/1036-evoss-vs-rrq.md`](matches/1036-evoss-vs-rrq.md) — EVOS 2–0 RRQ; early-snowball draft consistency check.
- [`matches/1037-navi-vs-ae.md`](matches/1037-navi-vs-ae.md) — NAVI 0–2 AE; late base defense/turning-point review.
- [`matches/1107-onic-vs-tlid.md`](matches/1107-onic-vs-tlid.md) — ONIC 0–2 TLID; early rotations to structure damage.

## Audit

- [`reports/audit-INS-1037-LATE-SWING.md`](reports/audit-INS-1037-LATE-SWING.md) — verdict **partially supported**. Quote/timestamp validation, DB checks, counterexamples, actual frame review and limitations.

## Evidence and reproducibility

- [`evidence/pilot-ledger.jsonl`](evidence/pilot-ledger.jsonl) — canonical short-excerpt evidence.
- [`evidence/evidence-schema.json`](evidence/evidence-schema.json) — versioned JSON Schema.
- [`evidence/query-catalog.json`](evidence/query-catalog.json) — every SQL query, parameters and provenance.
- [`evidence/database-snapshot-manifest.json`](evidence/database-snapshot-manifest.json) — DB fingerprint, coverage and lineage.
- [`evidence/audit-log.jsonl`](evidence/audit-log.jsonl) — audit export.
- [`evidence/visual-review.json`](evidence/visual-review.json) — frame dispositions.
- [`evidence/timed-alignment.json`](evidence/timed-alignment.json) — caption alignment coverage.
- [`sources/source-manifest.json`](sources/source-manifest.json) — source hashes, verified video IDs and series mapping.
- [`pilot/selection.json`](pilot/selection.json) — curated claims/quotes used to build the ledger.

## Coverage warning

Only 2/27 broadcast days have verified video IDs and timestamp links. The remaining 25 days are **unprocessed**, not “empty” or “irrelevant”. Do not read this pilot as a season-level finding.
