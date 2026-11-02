# Goal: Achieve Full In-Depth Player-Level Semantic Analysis (MPL ID S18)

## Objective

Take the existing 66 database-backed player dossiers (`analysis/players/`) from "data-complete" to "analysis-complete": every player must have transcript-verified observations, visual evidence where material, per-player insights with counterexamples, at least one skeptical audit, and matched comparisons against positional peers. The result should be a fully traceable, transcript-powered coaching intelligence layer at the player level.

## Prerequisites (Already Complete)

- [x] All 66 player dossiers generated from `player_season_stats`, `game_players`, `game_picks`, `matches.liq_mvp`
- [x] 4 Q-PLAYER-* queries in `query-catalog.json` (season, games, picks, MVP series)
- [x] 6 OBS-PLAYER observations, 3 insights, 1 audit in the evidence ledger
- [x] Player matched-comparisons report (database-backed)
- [x] 22 of 27 broadcast sources boundary-verified (medium confidence)
- [x] 72 of 72 series have curated reports
- [x] `verify_analysis.py` passes (6/6 suites)
- [x] Canonical DB snapshot `mpl-s18-db-20c5ea2c51f3` (read-only)
- [x] Phase 0 scan & fix complete: all 66 dossiers validated, 11 zero-game players fixed (missing Draft history and Items sections, inaccurate Limits line)

## Phase 0 — Scan & Fix (COMPLETE)

All 66 dossiers were scanned and fixed. Validation confirmed:
- All 66 files exist and contain DB snapshot ID `mpl-s18-db-20c5ea2c51f3`
- All have per-game breakdown or "no per-game data" note
- All have draft history section and items & talents section
- File count matches `player_season_stats` (66 players, 66 files, 0 extras)
- `verify_analysis.py` → PASS (6/6); `git diff --check` → clean

## Phase 1 — Add All Missing Useful Information (NEXT)

For each player, add information currently absent:

- [ ] **Transcript evidence:** Search the verified transcript corpus for mentions of each player (by display name and in-game name). Use `tools/transcript_evidence.py search --source-id <id> --pattern "<player>"`. Record exact quote, source line span, and timestamp link (only from fully aligned, non-quarantined sources).
- [ ] **Player-level observations:** Create `OBS-PLAYER-<NAME>-*` observations for notable patterns. Each must cite DB refs and/or transcript segments.
- [ ] **Full per-game items/talents:** Replace the single-sample items/talents with a per-game breakdown (or a "top items by frequency" summary) for players with 10+ games.
- [ ] **Trend analysis:** Add early-season (weeks 1-4) vs late-season (weeks 7-9) KDA/game splits where the data supports it.
- [ ] **Opponent context:** For each player, note their record against top-4 vs bottom-5 teams.
- [ ] **Role-specific metrics:** For junglers, add first-blood/first-turtle involvement if derivable; for gold laners, add tower-damage share; for roamers, add assist participation.
- [ ] **Cross-references to series reports:** Link each player dossier to the series reports where they appeared (bidirectional links).
- [ ] Update `analysis/index.md` and `analysis/players/` README with coverage counts.

## Phase 2 — Improve Quality of Analysis

- [ ] **Confidence language:** Ensure every claim uses "consistent with" / "partially supported" / "not established".
- [ ] **Matched comparisons:** For each player insight, compare against positional peers on the same team and on other teams.
- [ ] **Sample size honesty:** Mark players with < 10 games as "small sample" and exclude from pattern claims.
- [ ] **Outlier handling:** For players with extreme KDA (e.g., ZEONN 7.85 on 37 games), check if a single outlier game inflates the average. Report median KDA alongside mean.
- [ ] **Missing data honesty:** For players with 0 games, state explicitly that no per-game data exists.
- [ ] **Visual verification:** Where a transcript passage raises a gameplay question about a specific player, use `tools/video_frames.py` to capture frames and record whether they were visually reviewed.
- [ ] Run `python tools/verify_analysis.py` and `git diff --check` after every batch.

## Phase 3 — Counter Your Own Analysis (Antithesis)

- [ ] For each player-level insight, write an antithesis: what would weaken or overturn it?
- [ ] Search for counterexample players (e.g., a high-KDA player on a losing team, or a low-KDA player on a winning team).
- [ ] Document alternative explanations (role effects, team strength, small sample, ASR errors).
- [ ] Create a `counter-analysis-players.md` report following the structure of `counter-analysis-pilot.md`.
- [ ] Improve the previous analysis based on the antithesis findings.

## Phase 4 — Recheck All Previous Steps

- [ ] Re-run all validation scripts and DB cross-checks.
- [ ] Re-read all 66 dossiers for factual errors introduced during expansion.
- [ ] Re-run `verify_analysis.py` (6/6 suites) and `git diff --check`.
- [ ] Update `coverage-summary.md` with final player-level counts.
- [ ] Confirm no raw transcripts, cookies, or media caches are staged.

## Phase 5 — Polish Everything

- [ ] Search online for any additional context needed (e.g., MPL ID S18 player rosters, role assignments, patch notes).
- [ ] Ensure consistent formatting across all 66 dossiers.
- [ ] Add a player index to `analysis/index.md` linking all 66 dossiers.
- [ ] Final diff review: inspect for generated data churn or accidental local artifacts.
- [ ] Commit and push only when safe and permitted; never force-push.

## Data safety (non-negotiable)

- Treat `data/mpl_id_s18.db`, CSVs, season metadata, and the dashboard as read-only inputs.
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
- Do not claim full-season player coverage until at least 10 dossiers have transcript-verified observations.

## Completion rule

When this goal is finished, move this file from `docs/goals/active/` to `docs/goals/finished/`.

## Final report requirements

1. Files changed, final working-tree status, commit SHA and push status.
2. Player count, coverage by team/lane, and representative player IDs.
3. Queries added, tests run and results.
4. Remaining limitations and what is required before scaling to full player coverage.
5. Explicitly confirm that raw corpus and local media/cookies were not committed or pushed.
