# MPL S18 Analytics — Data Consistency and Correctness Goal

## Goal

Make every statistic in Berliandro's Eye MPL S18 reproducible from one coherent, explicitly identified data snapshot. Resolve discrepancies between **Analytics → Teams**, **Coach Prep**, **Matches → Regular Season → Standings**, and other database-driven views. Fix confirmed analytics calculation defects in scope and add cross-view regression gates so inconsistent statistics cannot silently ship again.

**Do not begin semantic transcript analytics.** That is a separate future project. Do not redesign unrelated UI or refactor the app broadly.

Repository: `berliandro/berliandros-eye-mpl-s18`

## Important baseline findings to independently re-check

The latest state inspected during the initial review was commit `9e9d01b6f1b1b0f74a0e60f92028fc5b63bdd2af`. Never assume the repository is still at that commit; start by inspecting current HEAD and the working tree.

The checked-in CSV snapshot at review time contained 9 standings rows, 69 completed series, 167 games, and 334 `team_games` rows. When game results were recalculated from `data/csv/games.csv`, game W–L reconciled with the official `standings.csv` **Game W–L** for all nine teams. This means the reported mismatch may be caused by a different comparison (match W–L vs game W–L), mismatched snapshot versions after refresh/cache selection, stale derived aggregates, or a data/phase scope mismatch. Reproduce the actual issue; do not assume which cause is responsible.

Specific code risks identified during review and to verify against current source:

1. `buildTeamMetrics()` consumes both sides of `team_games`; `anBT()` updates both teams from each row. Consequently each game may be counted twice in Bradley–Terry fitting. The bootstrap also samples individual team rows instead of paired game results.
2. Player `deathShare` in `buildPlayerMetrics()` appears to divide player deaths by team kills rather than team deaths, affecting the player-impact model.
3. Coach Prep's weak/strong-map selection filters on `n >= 5` but appears to allow the `Unknown` map category. Unknown map records must not be reported as actual maps.
4. `buildBanRanking()` appears to combine the team's picks and bans into one presence value and multiply it by the team's pick win rate. This may conflate the opponent's played-hero threat with bans that the same opponent chooses. Define the intent and separate measures.
5. Draft meta movement groups games into fixed seven-day intervals from the first date and compares the last two non-empty intervals. Confirm that these periods are not mislabeled as consecutive official competition weeks or mixed across regular season/playoffs.
6. Draft pair tables are sorted by observation count, so their displayed “top” rows mean most observed, not necessarily strongest synergy/counter effect. Label this accurately or separate frequency and effect rankings.

These are audit targets, not permission to assume all are unchanged or to alter code without verifying the current implementation.

## Phase 0 — Inspect and reproduce before editing

1. Inspect current branch, HEAD, working tree, latest commits, remote relationship, and any ongoing/uncommitted changes. Preserve unrelated work.
2. Read `README.md`, `docs/DATA_DICTIONARY.md`, `data/season.json` and any relevant season metadata, `tools/verify.py`, the ETL/build code, CSV generation code, and all analytics implementations/tests.
3. Inspect the actual SQLite database schema and determine the authoritative source for every displayed statistic. Establish which CSVs, embedded JavaScript data objects, caches, and aggregates are derived from it.
4. Trace the data lifecycle end to end:
   - SQLite and ETL outputs;
   - CSV exports;
   - HTML generation/embedded `DATA`;
   - runtime live refresh;
   - localStorage cache selection/migration;
   - derived datasets such as `team_games`, `team_season`, picks/bans, and team/player analytics.
5. Reproduce the reported mismatch using the current built HTML and current source where possible. Record team, view, metric, compared values, source snapshot, and refresh/cache state. Identify whether the mismatch is caused by wrong calculations, different metric definitions, phase filters, team aliases, stale cache/data, or another defect.
6. Record baseline test results before changing code.

Do not claim the bug is reproduced if it could not be. If local-browser state is unavailable, use reproducible tests and explain which part could not be directly observed.

## Phase 1 — Define the source of truth and metric contracts

Use the existing SQLite database as the canonical persisted data source for the generated season snapshot. Keep the current single-file/offline app architecture where practical: SQLite remains the source of truth during build/ETL, and all embedded arrays/CSVs must be generated from the same validated snapshot.

Create or document explicit metric contracts:

- **Series/match W–L:** number of completed regular-season series won/lost by the team.
- **Game W–L:** number of completed regular-season games won/lost by the team.
- **GP:** label whether this means game appearances or series played. In Analytics → Teams, the current aggregation uses team-game rows, so it is game-level unless deliberately changed.
- **Playoffs:** must be included or excluded deliberately and consistently. Never compare an all-phase analytics calculation to regular-season-only standings without clearly labelling that scope.
- **Official standings:** preserve the source-published match and game records as official values. Treat them as a reconciliation target, not as an interchangeable table with derived calculations.
- **Derived calculations:** record source row set, filters, aggregation formulas, and as-of snapshot/version.

Where official standings and derived values ought to match, define strict expected reconciliation. If discrepancies are explained by phase, incomplete matches, or source timing, report those reasons explicitly instead of silently forcing values to match.

Normalize team identities through the existing canonical alias/config system. Do not maintain another independent mapping.

## Phase 2 — Eliminate mixed-snapshot analytics

Investigate and fix the likely stale-aggregate path rather than merely changing display labels.

Current implementation reviewed at baseline has a potential inconsistency: runtime refresh updates top-level `schedule`/`standings` and raw `games`/`players`/`bans`, but the Analytics calculations consume precomputed `DATA.team_games`, `DATA.team_season`, `DATA.picks`, and `DATA.bans`/other data that may not be recomputed or versioned as one unit. The cache schema also needs to be checked for whether it stores every required analytics input and derived aggregate consistently.

Requirements:

1. All analytics inputs used by a calculation must come from one coherent snapshot/version. Do not mix refreshed standings with stale team aggregates or picks.
2. Choose one minimal safe approach:
   - recompute derived analytics inputs from the validated current raw snapshot after a successful refresh; or
   - keep analytics bound to the embedded/database snapshot until all dependent inputs can be refreshed consistently, clearly labelling the data state.
3. If an aggregate is derived, calculate it from canonical raw rows using one shared helper/pipeline rather than duplicating logic across ETL, UI, and tests.
4. Keep stable primary/composite keys and consistent filters for season, phase, match, game, and team.
5. Cache metadata should identify snapshot version/fingerprint, completion/partial-refresh status, and relevant source progress. Never present mismatched or partial aggregates as fully updated.
6. Preserve offline operation and the last-known-good snapshot. A failed/partial refresh must not leave some views on new data and other views silently using stale aggregates without an explicit consistent policy.
7. Avoid network-dependent tests. Use deterministic mocked refreshes and committed source snapshots.

## Phase 3 — Cross-view reconciliation gates

Add automated integrity checks using the committed SQLite database and/or its canonically generated CSV exports. Reconciliation must be based on the same set of completed regular-season series/games, with phase and status filters explicit.

Required checks:

- For each team, calculated regular-season game W–L from completed game results equals `standings.game_win` / `standings.game_lose` where both sources cover the same snapshot.
- For each team, series W–L aggregated from completed regular-season match results equals `standings.match_win` / `standings.match_lose` where coverage is complete.
- Calculated game counts, wins, losses, and game differential reconcile with the published standings fields.
- The total of team game appearances is exactly twice the number of included completed games; every game contributes one and only one win and one loss across its two teams.
- Each completed game maps to valid teams and exactly one winning team; invalid/missing winners are reported, not silently counted as losses.
- Team identities reconcile through canonical aliases; no duplicate team rows arise from alternate spellings.
- Analytics → Teams and Coach Prep use the same documented scope, snapshot, and base counts when showing the same metric.
- Official standings remain distinct from series/game counts and are not accidentally substituted for each other.
- Any intentional exceptions (incomplete source, absent map mode, unplayed fixture) are explicit and tested.

When reconciliation fails, the command should print an actionable per-team/per-metric diff containing official value, derived value, included row count, missing/excluded row IDs, phase/status filters, and snapshot identifier.

Integrate these checks into `python tools/verify.py` or the repository's current standard verification workflow. Do not make passing tests easier by weakening existing assertions.

## Phase 4 — Correct the analytics methodology defects that are confirmed

Audit the following areas. Make each code change only after confirming the current code still has the issue. Add tests for the mathematical meaning, not merely consistency with the same implementation.

### A. Team ratings and bootstrap

- Ensure the Bradley–Terry model consumes each game result exactly once. Do not feed both team-perspective rows to a function that already updates both sides symmetrically.
- Bootstrap at the game/matchup unit so the two opposing results remain paired. Document the chosen resampling unit and interval interpretation.
- Test that duplicating perspective rows does not inadvertently double the modeled sample, that a game is counted once, the model is deterministic under a fixed seed, intervals are ordered, and empty/small inputs behave honestly.
- Confirm `form5`, series form, H2H, series count, SOS, tempo, clutch, and map records use explicit scopes and a stable chronological order.

### B. Player death share and impact

- Calculate death share from player deaths / that team's total deaths for the same game, not team kills.
- Handle zero team deaths explicitly and document the chosen behavior.
- Ensure player and team source rows join on the correct match/game/team keys.
- Add real semantic tests: for teams with nonzero deaths, player death shares should sum to approximately 1; verify zero-death games; verify impact changes in the intended direction when deaths change.

### C. Unknown/missing map categories

- Exclude `Unknown`, null, empty, and unresolved map labels from rankings called “weak maps” or “strong maps.”
- Surface missing-map counts as a data-quality note; don't discard those games from unrelated overall team record metrics.
- Test that unknown maps can never be selected as actual strong/weak maps even if `n >= 5`.

### D. Ban threat ranking

- Separate opponent's observed pick frequency/win rate from that team's own ban choices.
- Give each score a clear, defensible definition. If a heuristic uses presence × win rate, define whether presence means picks, combined pick/ban contest rate, or another explicitly named statistic.
- Do not describe a statistical proxy as confirmed draft intent or a guaranteed best ban.
- Add tests for ban-only heroes, pick-only heroes, zero picks, zero bans, small samples, and exact expected scores.

### E. Draft meta periods and pair tables

- Compare official adjacent weeks when official week identifiers exist. Otherwise use explicit date ranges and do not label non-adjacent periods as consecutive weeks.
- Handle gaps and regular-season/playoff phase changes explicitly.
- Make the pair table labels match their sort rule. Either label them “Most observed” (frequency order) or separately show most frequent pairs and highest/lowest estimated effects with sample size/uncertainty. Avoid causal wording.
- Test missing dates, interval gaps, phase transitions, low sample sizes, ties, and no-data states.

## Phase 5 — UI consistency and language

- Make Analytics → Teams labels unambiguous: use “Games GP” / “Game W–L” for per-game counts and display series W–L separately if useful.
- In Matches → Regular Season → Standings, preserve explicit Match W–L and Game W–L columns.
- Add concise source/scope notes when values have different definitions or include different phases.
- If the snapshot is partially updated or analytics are held to the embedded snapshot, show that state honestly and consistently across views.
- Do not redesign unrelated UI. Maintain existing dark visual style, responsive behavior, keyboard accessibility, and all existing interactions.
- Use `@ui-craft` only for targeted presentation changes, not a full restyle.

## Phase 6 — Validate against committed real data and runtime scenarios

Add deterministic regression fixtures and integration checks that cover:

1. Current committed snapshot: derive team game W–L from canonical game rows and reconcile all teams against official standings.
2. Series W–L from match-level rows and its distinctness from game W–L.
3. Normal refresh: all raw and derived data update coherently, and cross-view totals still reconcile.
4. Partial refresh: failed match IDs retain last-good detail and do not create mismatched aggregate counts; the state is labelled partial.
5. Cache load/reload: raw data, derived aggregates, standings, and analytics all use the same snapshot version.
6. Legacy cache migration: no mixed schemas or stale aggregates masquerade as complete.
7. Alias variation: equivalent team names reconcile to one canonical identity.
8. Unknown map data: no false map ranking.
9. Team-rating model: one observation per game and paired bootstrap.
10. Player death share: correct denominator and impact semantics.
11. Ban recommendation and meta-period semantics.
12. Empty/malformed/missing data and deterministic outputs.

Use the existing test infrastructure where possible. Add focused tests and integrate them into the standard verify command; avoid unnecessary frameworks or dependencies.

## Phase 7 — Final verification and delivery

Run the full standard suite, including `python tools/verify.py` if still supported, all focused new tests, generated-output parity, and build checks. Rebuild the HTML from canonical data and verify that generated outputs are consistent. Inspect the final diff for generated data churn, unrelated modifications, or accidental inclusion of local cache/raw files.

Commit and push only when safe and permitted by the repository workflow. Never force-push or discard user changes.

The final report must include:

- Root cause of the reported cross-view discrepancy, with a reproducible example.
- Explicit statement about whether the checked-in snapshot originally reconciled and whether the problem appeared only under refresh/cache or different metric semantics.
- The chosen canonical source-of-truth and snapshot policy.
- Reconciliation results for all nine teams, including Match W–L and Game W–L separately.
- Every analytics formula/label fixed and why.
- Tests actually run and results; CI status if available.
- Files changed, limitations, final commit SHA, and remote push status.

Do not claim completion if the team-level reconciliations fail or if different views can still silently calculate from different snapshot versions.

## Out of scope

- Transcript/semantic AI analysis, semantic search, embeddings, evidence ledgers, and coaching insight generation.
- New analytics that require sources the database does not contain (such as Lord/Turtle timelines or gold-at-15) unless separately requested.
- Broad architecture rewrites or visual redesigns.
