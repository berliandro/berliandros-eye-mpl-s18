# Phase 0 mistake audit — semantic analysis

**Scope:** active files under `analysis/` (excluding `analysis/cache/migration-backups/` and raw transcripts).

## Mistakes found

1. **Stale database snapshot references after the 2026-10-31 winner-orientation migration.**
   - **Where:** `analysis/matches/*.md`, `analysis/reports/audit-INS-1037-LATE-SWING.md`, `analysis/evidence/audit-log.jsonl`, `analysis/evidence/pilot-ledger.jsonl`, `analysis/pilot/selection.json`.
   - **What was wrong:** these files still cited the pre-migration snapshot `mpl-s18-db-1fb1768560e1` (SHA-256 `1fb17685…`), while the canonical post-migration snapshot is `mpl-s18-db-20c5ea2c51f3` (SHA-256 `20c5ea2c…`). The pilot ledger's `database_refs` already used the post-migration snapshot, so the human-readable `scope`/`sources_inspected` strings contradicted the embedded database references.
   - **Why it is a mistake:** the canonical database fingerprint changed on 2026-10-31; any current claim must reference the current snapshot. Mixing two snapshot IDs in one record breaks provenance and makes re-execution ambiguous.
   - **Fix:** replaced the stale snapshot ID/SHA in all active files. `README.md` line 100 and `pilot-quality-report.md` line 60 were intentionally kept as the documented pre→post transition.
   - **Proof:** `tools/verify_analysis.py` still passes (6/6 suites, 8 segments / 18 observations / 3 insights / 1 audit); edited JSON/JSONL files parse cleanly; an active-file scan now finds stale references only in the two intentionally transitional files.

2. **No other factual mismatches found in pilot numbers.**
   - Series results, durations, kills, gold, tower damage, picks, map modes, sides, VODs and MVPs were re-queried from `data/mpl_id_s18.db` and match the reports and ledger (see Phase 1 additions).
   - Visual-review counts (6 used, 1 rejected promo, 1 failed) match `visual-review.json`.
   - Alignment counts (W1D1 9,103 exact + 1 normalized; W9D3 12,273 exact) match `timed-alignment.json`.

## Files changed in Phase 0

- `analysis/matches/1036-evoss-vs-rrq.md`
- `analysis/matches/1037-navi-vs-ae.md`
- `analysis/matches/1107-onic-vs-tlid.md`
- `analysis/reports/audit-INS-1037-LATE-SWING.md`
- `analysis/evidence/audit-log.jsonl`
- `analysis/evidence/pilot-ledger.jsonl`
- `analysis/pilot/selection.json`
