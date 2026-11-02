# Analysis index

## Status

- Corpus imported: **27 files / 9,682,086 bytes**, SHA-256 verified **27/27**, conflicts **0**.
- Native transcript timestamps: **0**.
- Unique schedule VOD candidates: **27/27 broadcast dates**, derived from the canonical completed schedule.
- Metadata-verified official videos: **27/27** (official MPL Indonesia channel, exact season/week/day title).
- Fully caption-aligned sources: **26/27**; one partial source (`src-s18-w09d02`) is explicitly not citation-ready.
- Database winner orientation: repaired **21/72** rows; **0/72** row-score mismatches remain.
- Pilot series: **3** — 1036, 1037, 1107.
- Evidence: **8 segments / 18 observations / 3 insights / 1 audit**.
- Visual review: **6 used frames** (5 gameplay + 1 post-game context), **1 rejected promo**, **1 failed frame**.
- Full-season coverage: **no**.

## Start here

1. [`README.md`](README.md) — scope, safety, reproduction commands.
2. [`reports/corpus-inventory.md`](reports/corpus-inventory.md) — what was imported, timestamp/video coverage, parsing risks.
3. [`reports/database-inventory.md`](reports/database-inventory.md) — DB coverage, joins, and the post-migration `matches.winner` semantics.
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
- [`evidence/timed-alignment.json`](evidence/timed-alignment.json) — caption alignment coverage for 26 verified sources.
- [`sources/source-manifest.json`](sources/source-manifest.json) — source hashes, verified video IDs, status semantics and series mapping.
- [`pilot/selection.json`](pilot/selection.json) — curated claims/quotes used to build the ledger.

## Video source resolution

- [Video source resolution report](reports/video-source-resolution.md) lists every source, status, failure reason and status transition.
- Local result: **27/27 metadata-verified**, **26/27 fully aligned**, **1/27 partial** (`src-s18-w09d02`; 37 short lines without trustworthy timestamps).
- Run `python tools/resolve_and_align_sources.py` on the local machine with the ignored raw corpus to re-check metadata and alignment.
- Broadcast-date mapping does not establish exact in-video start times for individual series or games.

## Coverage warning

Only 3 series have curated semantic insights. Twenty-six sources are alignment-ready, but alignment readiness is not semantic analysis. The remaining source days are **unprocessed**, not “empty” or “irrelevant”. Do not read this pilot as a season-level finding.
