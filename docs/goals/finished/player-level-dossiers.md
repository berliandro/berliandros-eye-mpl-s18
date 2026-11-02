# Goal: Build Player-Level Semantic Dossiers (MPL ID S18)

## Objective

Build traceable, database-backed player-level dossiers for all 66 MPL ID S18 players, using the existing canonical SQLite database (`data/mpl_id_s18.db`, snapshot `mpl-s18-db-20c5ea2c51f3`), the verified transcript corpus, and the established evidence ledger (`analysis/evidence/pilot-ledger.jsonl`). Each dossier must cite reproducible SQL queries, exact game references, and transcript evidence where available, and must distinguish source-reported facts, derived stats, and commentary.

## Scope & deliverables

1. `analysis/players/` directory with one Markdown dossier per player (66 files), following the same provenance discipline as `analysis/matches/`.
2. Each dossier includes: identity (team, lane, role), season aggregates (games, kills, deaths, assists, KDA, gold, kill participation), per-game breakdown (duration, map mode, side, kills/deaths/assists, gold, hero damage, tower damage, items, talents), draft history (heroes picked/banned per game), and MVP/award references.
3. Database cross-references via `query-catalog.json` entries (new `Q-PLAYER-*` queries) with snapshot SHA-256 and reproducible SQL.
4. Evidence ledger observations (`OBS-PLAYER-*`) for notable per-player patterns, with verification states (`transcript-verified`, `database-record`, etc.).
5. At least 3 player-level insights with counterexamples and at least 1 skeptical audit, following the pilot insight/audit structure.
6. Matched comparisons: for each insight, compare the player against positional peers (same lane/team) using DB aggregates.
7. Update `analysis/index.md`, `analysis/README.md`, and `coverage-summary.md` to reflect player-level coverage.

## Data safety (non-negotiable)

- Treat `data/mpl_id_s18.db`, CSVs, season metadata, and the dashboard as read-only inputs. Do not rebuild or alter them.
- Put all player evidence and derived reports in `analysis/players/` and `analysis/evidence/`.
- Do not fabricate player stats, items, or performance claims. Missing fields stay `null`/`unknown`.
- Preserve raw transcripts; only short quotations in reports.
- Do not commit raw transcripts, cookies, or media caches.

## Quality gates

- Every DB claim identifies snapshot, table/fields, SQL, parameters, and scope.
- Every quoted transcript span resolves to an exact source line under documented normalization.
- `python tools/verify_analysis.py` passes (6/6 suites) after changes.
- `git diff --check` passes.
- No weakened or deleted tests.

## Out of scope

- Modifying the canonical database, CSVs, or dashboard.
- Processing every transcript for player mentions (use DB facts + targeted transcript search).
- Integrating player UI into the dashboard.
- Claiming full-season player coverage until dossiers exist for all 66 players and pass validation.

## Final report

List files changed, player count, queries added, tests run and results, commit SHA and push status.

## Completion rule

When this goal is finished, move this file from `docs/goals/active/` to `docs/goals/finished/`.
