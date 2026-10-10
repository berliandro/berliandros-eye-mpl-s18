# MPL ID Season 18 — Engineering Quality Improvements

Use the `@ui-craft` skill whenever a UI change is necessary, but prioritize correctness, data integrity, test coverage, and maintainability.

**Repository:** `berliandro/berliandros-eye-mpl-s18`

## Overall objective

Audit and improve six areas of the existing MPL Indonesia Season 18 application:

1. Prevent overconfident probability predictions when sample sizes are small.
2. Prevent partially failed live refreshes from destroying complete statistics.
3. Fix the Liquipedia ETL parser so it includes the final match block.
4. Integrate the probability tests into the normal regression suite and add GitHub Actions CI.
5. Version local cache data and prevent stale or incompatible snapshots from overriding newer data.
6. Centralize season-specific assumptions to make future season transitions safer.

This is a targeted engineering improvement, not a rewrite.

**Important constraints:**
- Inspect the existing implementation before changing it.
- Preserve all working functionality and the current visual design.
- Keep MPL Season 18 as the active season.
- Do not invent MPL Season 19 rules, teams, schedules, or data.
- Do not change the probability model merely to make its outputs look more plausible.
- Do not remove existing tests or weaken their assertions to make the suite pass.
- Use the smallest maintainable changes that solve the identified problems.
- Do not declare completion just because the code compiles.

Required workflow:

`INSPECT → PLAN → IMPLEMENT → TEST → REVIEW → REGRESSION CHECKS → REPORT`

---

## 1. Probability model: statistical smoothing

Inspect the existing probability engine in `tools/templates/app.js`, especially `calcChances`, `winRate`, `qWin`, and the sweep-probability calculation.

The current matchup calculation derives each team's win rate directly from its observed match record and then calculates matchup probability using a ratio of those win rates. This can produce a 100% predicted win probability for an undefeated team playing a team with zero wins.

The sweep probability also comes directly from observed sweep results. If the only observed series ends 2-0, the model can assign a 100% sweep probability to future matches.

These are unacceptable small-sample behaviors.

### 1.1 Smooth team-strength estimates

Introduce a documented statistical prior or equivalent smoothing method for team win rates.

Requirements:
- Shrink early-season estimates toward a neutral 50% baseline.
- Use a symmetric prior with a documented strength, such as a Beta(2, 2) prior, unless tests or a defensible calibration analysis support a different choice.
- Calculate smoothed estimates using actual series wins and losses.
- Convert the smoothed estimates into future matchup probabilities using a clearly documented method.
- Preserve the existing model's general purpose and avoid unnecessary changes to the calculation pipeline.
- Do not hardcode team-specific ratings or probabilities.
- Do not use upcoming matches as historical results.
- Ensure finite historical records do not automatically produce exactly 0% or 100% probability for an ordinary future match solely because one team has no wins or another is undefeated.

If the implementation continues to use the existing win-rate ratio as a Bradley-Terry-style heuristic, document that accurately. Do not claim to have implemented a formally fitted Bradley-Terry model unless that is actually what the code does.

### 1.2 Smooth sweep probability

Apply a documented prior to the probability of a series ending in a 2-0 sweep rather than relying exclusively on the observed sweep proportion.

For example, a Beta(2, 2) prior would give:

`smoothedSweepProbability = (observedSweeps + 2) / (decidedSeries + 4)`

Treat this as a candidate implementation, not an excuse to skip verification.

Requirements:
- With zero observed series, use a neutral 50% sweep baseline.
- One observed sweep must not imply that every future series will be a sweep.
- One observed non-sweep must not imply that future sweeps are impossible.
- As more results accumulate, the estimate should increasingly reflect observed data.
- Keep completed-series detection and sweep classification consistent with existing fixture-normalization rules.

### 1.3 Keep the model internally consistent

Preserve:
- Deterministic simulation using the configured random seed.
- The existing qualification calculation and mathematically justified certainty checks.
- Upper Bracket Chance never exceeding Playoff Chance.
- Aggregate probability invariants before display rounding.
- Wilson confidence intervals and trial-count tooltips for simulation-based estimates.
- Correct handling of completed, live-decisive, and upcoming fixtures.

Do not confuse a probability estimate with a mathematically guaranteed outcome.

### 1.4 Add tests for early-season behavior

Add automated tests covering:
- No completed series.
- Exactly one completed series ending 2-0.
- Exactly one completed series ending 2-1.
- An undefeated team against a team with zero wins.
- A team with zero wins but several losses.
- Teams with one or two completed series.
- Several teams with identical records.
- Increasing historical sample sizes.
- No future matchup probability becoming exactly 0% or 100% solely because of finite-sample win-rate extremes.
- Deterministic results for the same input and seed.
- Valid aggregate probability totals and Upper Bracket Chance ≤ Playoff Chance.

Use manually verifiable scenarios where practical. Do not merely assert that outputs fall within plausible-looking ranges. Verify the expected direction and properties of the smoothing itself.

---

## 2. Live refresh: preserve data when individual requests fail

Inspect `refreshDB()` and its supporting functions in `tools/templates/app.js`.

The existing implementation fetches match details concurrently. If some individual requests fail, successful responses can replace the entire games and player-stat datasets, and that incomplete result can be written to `localStorage`. This can permanently discard records from a previously complete snapshot.

### 2.1 Merge successful updates instead of replacing everything

For each refresh:
- Identify which match-detail requests succeeded.
- Identify which requests failed.
- Replace old records only for successfully retrieved match IDs.
- Preserve existing records for match IDs whose refresh requests failed.
- Do not discard valid records from the embedded snapshot or last good cached snapshot.
- Deduplicate merged results.

Use stable composite keys appropriate to each collection, such as match detail ID plus game number, player identity, or ban side.

For successfully refreshed match IDs, remove their old records before inserting newly retrieved records. This prevents duplicate data. For failed match IDs, keep the previously available records.

Pay particular attention to the current `DATA.bans` merge logic. Verify its matching keys rather than assuming the current filter deduplicates records correctly.

### 2.2 Validate data before committing a refresh

Before replacing shared application data or saving the cache:
- Validate the structure of required API responses.
- Reject unexpected empty or malformed responses when the application requires nonempty data.
- Verify that identifiers are consistent.
- Record failed match IDs.
- Check whether the refresh is complete or partial.

A partially successful refresh may still provide useful updates, but it must not be presented as a fully successful refresh.

The UI may retain its existing visual style, but its existing status message must clearly distinguish a complete refresh from a partial refresh.

### 2.3 Preserve the last known-good state

If required top-level requests fail:
- Keep the existing in-memory data.
- Keep the last known-good cache.
- Continue displaying usable data when possible.
- Report the refresh failure without implying that the data has been updated.

If individual match-detail requests fail:
- Merge successful updates with retained records for failed match IDs.
- Do not overwrite complete collections with incomplete collections.
- Store the merged snapshot only after validation.

Handle `localStorage` quota failures safely. Do not let a failed cache write cause the UI to report that a successful network refresh failed when the in-memory refresh actually succeeded.

### 2.4 Automated refresh-failure tests

Test scenarios where:
- Every request succeeds.
- One match-detail request fails.
- Several match-detail requests fail.
- A match that previously failed is successfully retrieved on the next refresh.
- A response is malformed.
- A required API endpoint fails.
- The local cache write fails.
- Repeated refreshes do not duplicate games, player records, bans, or matches.

Use mocked API responses. Tests must not depend on the real live API being available.

Verify failed match IDs retain their previous records and successfully retrieved match IDs receive updated records.

---

## 3. Liquipedia ETL: parse the final match block

Inspect `tools/build_s18_db.py`, especially the match-block parsing around the current Liquipedia regex.

The current parser ends a match block only when it encounters the next match marker. This risks omitting the final match block because no subsequent marker exists.

### 3.1 Correct the parser boundary

Update the parser so a match block ends at either:
- The next Liquipedia match marker.
- The end of the input.

A possible regex boundary is:

`(?=\|M\d+=\{\{Match|\Z)`

Use an appropriate capture group and confirm the exact behavior with representative input. Prefer a small, named parsing helper over burying complex parsing logic in `main()`.

### 3.2 Add regression tests

Create automated parser tests covering:
- One match block.
- Two consecutive match blocks.
- The final block at end-of-input.
- Input with a trailing newline.
- Input without a trailing newline.
- A block with a missing optional MVP field.
- Empty or malformed input.
- Preservation of opponent names, series winners, scores, dates, and MVP metadata.

The tests must prove the final block is captured and preceding blocks are not merged or truncated.

### 3.3 Protect existing database output

The ETL currently removes the existing SQLite database before the entire rebuild has completed. Improve the publication process so a failed build does not replace a known-good database with an incomplete one.

Requirements:
- Build into a temporary database and staging output directory where practical.
- Run required integrity checks before publishing generated files.
- Detect failed match-detail requests and do not silently publish a dataset with missing expected records.
- Retain the last known-good database and CSV exports if validation fails.
- Publish the validated results atomically where supported.
- Keep the existing database schema and output format compatible unless a schema change is necessary.

Do not force the ETL to succeed by ignoring failed validations. Do not require live network access for unit tests.

---

## 4. Regression tests and GitHub Actions CI

The repository contains `tools/test_chances.js`, but the normal Python regression command currently does not execute this dedicated probability suite. This means the documented regression command can pass without running the probability-engine tests.

### 4.1 Create one reliable standard verification workflow

Integrate the existing JavaScript probability tests and new regression tests into the standard test process.

The documented normal verification procedure should exercise:
- Probability-engine unit tests.
- Liquipedia parser tests.
- Application JavaScript syntax validation.
- Existing data-integrity checks.
- Existing strict asset-coverage checks.
- Generated HTML consistency.
- Cache/refresh merge tests.
- Season configuration validation.

Do not duplicate test execution unnecessarily, but ensure the standard workflow cannot silently skip critical suites. If Node.js or another required test runtime is absent, fail clearly when that runtime is required rather than incorrectly reporting full success.

### 4.2 Add GitHub Actions

Add a GitHub Actions workflow that runs on:
- Pushes to relevant branches.
- Pull requests targeting `main`.

Use supported versions of Python and Node.js, pinning major versions or versions as appropriate.

The workflow should:
1. Check out the repository.
2. Set up Python and Node.js.
3. Build the application from the committed source templates and data.
4. Run the standard regression suite.
5. Run the probability-engine tests.
6. Run applicable parser and refresh tests.
7. Run the generated-output parity check.
8. Fail the workflow if any required check fails.

Keep CI independent of external API availability. Do not run the network ETL as a required CI step. Do not require Playwright or screenshot dependencies for every CI run unless the existing project already supports those tests reliably. If browser smoke tests can run consistently, they may be added as a separate job.

### 4.3 Update documentation

Update README commands to match the actual standard regression procedure. Document:
- The local test command.
- The application build command.
- The parity-check command.
- The purpose of the GitHub Actions workflow.

Do not claim that a test runs automatically unless the workflow actually runs it.

---

## 5. Local cache versioning and freshness

Inspect the current cache logic using the `s18db` localStorage key.

The app currently restores cached data without checking whether it belongs to the current season/schema or whether its underlying source data is older than the embedded snapshot. Maintain offline-first behavior while preventing stale or incompatible data from overriding newer bundled data.

### 5.1 Add cache metadata

Introduce explicit metadata for:
- `seasonId`
- `schemaVersion`
- `snapshotVersion` or a stable source-data fingerprint
- `sourceSnapshotAt`, when available
- `refreshedAt`, for the last successful live refresh
- Refresh completeness/status

Use a deterministic snapshot identifier or fingerprint derived from actual data. Do not use an unchanging identifier for snapshots that differ, and do not introduce nondeterministic build timestamps that break the parity gate.

Use a versioned, season-specific cache namespace, such as:

`mpl-board:<seasonId>:v<schemaVersion>`

The exact format may differ if there is a good reason, but compatibility must be explicit.

### 5.2 Validate cache before loading it

At startup:
- Reject cache entries belonging to another season.
- Reject unsupported schema versions.
- Validate essential data structures before applying cached data.
- Do not let malformed cache content corrupt application state.
- Do not blindly prefer localStorage over the embedded snapshot.

When source-data freshness can be compared reliably, use the newer valid snapshot. If source timestamps are unavailable, do not infer freshness from unrelated timestamps. Use a documented fallback that preserves offline usability and makes data age clear.

### 5.3 Handle stale data honestly

Offline-first operation remains a requirement. A stale but valid snapshot may still be useful when the network is unavailable. Do not automatically delete useful data solely because it is old.

Instead:
- Preserve the last valid snapshot.
- Display its age or last successful refresh time.
- Clearly distinguish cached/stale data from a successful live update.
- Avoid showing a misleading "updated" status when the update did not complete.

Ensure a failed partial refresh cannot overwrite a more complete valid cache.

### 5.4 Cache migration tests

Test:
- A valid cache for the current season and schema.
- A cache from an older schema.
- A cache from another season.
- A malformed cache.
- A cache older than the embedded snapshot.
- A cache newer than the embedded snapshot.
- An offline startup with a valid stale cache.
- A complete refresh followed by reload.
- A partial refresh followed by reload.
- An unsuccessful refresh that must preserve the last known-good data.

---

## 6. Season configuration and future-season safety

The project is currently a Season 18-specific application. It is acceptable for the active season to remain explicitly Season 18, but season-specific assumptions should no longer be scattered unnecessarily throughout the code.

The future objective is to make the application safer to reuse for another MPL Indonesia season without assuming that the competition format or data source will remain unchanged.

**Do not switch the active dataset to Season 19 or invent unconfirmed 2027 details.**

### 6.1 Centralize season configuration

Introduce or extend a season configuration structure containing the applicable settings, such as:
- Season ID and display name.
- Team list and aliases.
- Total number of teams.
- Regular-season match format.
- Expected matches per team and total regular-season fixtures.
- Playoff qualification slots.
- Upper-bracket qualification slots.
- Tiebreaker configuration.
- Data-source endpoints.
- Liquipedia page or season identifier.
- Database/export locations or logical dataset identifiers.
- Cache namespace and schema version.
- Probability-model defaults and documented prior settings.

Keep the Season 18 configuration populated with the project's existing verified rules and data. Configuration should contain rules and identifiers, not fabricated results or team-strength assumptions.

### 6.2 Remove avoidable duplicated assumptions

Inspect the application, ETL, generator, regression tests, and README for duplicated season-specific constants. Where practical, derive those values from configuration rather than independently hardcoding them in multiple files.

Examples include:
- `TOTAL_SERIES`
- `PLAYOFF_SLOTS`
- `UPPER_BRACKET_SLOTS`
- Team lists.
- Season-specific Liquipedia paths.
- Database and cache identifiers.
- Expected fixture counts in data-integrity checks.

Preserve explicit tests of Season 18's known invariants. Those tests must not become meaningless merely because values are configurable.

Keep configuration validation strict so an incomplete or inconsistent configuration fails clearly instead of silently generating bad probabilities.

### 6.3 Support future format changes without inventing them

The calculation and ETL should be able to read a different season configuration when a verified configuration becomes available.

However:
- Do not hardcode a hypothetical Season 19 schedule.
- Do not assume the number of teams or playoff slots remains the same.
- Do not automatically treat an unknown tiebreaking rule as official.
- Do not reuse Season 18 statistics as Season 19 performance data without an explicitly documented preseason model.
- Do not let Season 18 browser caches contaminate another season.
- Do not compromise the existing Season 18 build to make the abstraction appear more generic.

The immediate deliverable is a well-tested, configurable Season 18 implementation, not a speculative Season 19 release.

### 6.4 Configuration tests

Verify:
- The current Season 18 configuration reproduces the current expected output.
- Invalid team counts, duplicate teams, invalid slot counts, and missing required fields fail clearly.
- Fixture-count validation derives expectations from the configured format where appropriate.
- Cache IDs follow the configured season/schema.
- A second synthetic configuration can be loaded in isolated tests without changing Season 18's committed data or output.

---

## 7. End-to-end regression and compatibility

After all changes, verify that the application still behaves correctly across its existing sections.

Preserve:
- Overview and player statistics.
- Player identity and alias normalization.
- Match lists and scoreboards.
- Hero and item drill-downs.
- Series MVP mapping.
- Standings and qualification probabilities.
- Playoff bracket layout and hover interactions.
- Offline startup and manual refresh.
- Existing artwork/asset coverage.
- The self-contained HTML build.
- README screenshots and their specification.

Do not redesign the bracket or introduce unrelated visual changes.

If a tooltip/status message needs minor clarification for cache freshness or partial refresh, keep the change minimal and consistent with the existing UI. Use @ui-craft to review any such visible change.

Run the build and regression suite after source changes. Do not assume passing unit tests proves the generated HTML contains the changes: verify the final built application includes the correct templates and data.

---

## 8. Required testing approach

Use a combination of:
- Deterministic unit tests.
- Manually verifiable calculation scenarios.
- Mocked API responses.
- Parser fixtures.
- Cache migration tests.
- Existing data-integrity tests.
- Generated HTML parity checks.
- Browser checks when supported by the project's tooling.

Do not make tests depend on the live MPL API or Liquipedia being available. Keep the simulation's random seed deterministic in tests.

When testing approximate probability results, test both expected properties and meaningful numerical tolerances rather than relying on exact Monte Carlo percentages unless the scenario is deterministic.

Check the full console/output for errors, warnings, missing assets, dropped fixtures, and failed tests.

---

## 9. Required implementation workflow

### Phase 1: Audit
- Inspect relevant source files, current constants, tests, generated HTML, and cache shape.
- Identify how each planned change fits the existing architecture.
- Record current test results before modifying code.

### Phase 2: Implement
- Implement statistical smoothing and early-season tests.
- Fix partial refresh handling and deduplication.
- Fix and test the final Liquipedia match-block parser.
- Protect ETL publication from incomplete builds.
- Integrate the test suite and add GitHub Actions CI.
- Add cache versioning/freshness validation.
- Centralize season-specific configuration and migrate existing code carefully.

### Phase 3: Verify
- Run all relevant unit tests.
- Run the standard regression suite.
- Rebuild the single-file application.
- Run the parity check.
- Inspect generated artifacts and data-integrity results.
- Test mocked refresh failures and cache scenarios.
- Verify that the current Season 18 UI remains intact.

### Phase 4: Self-review
Review the implementation for:
- Unnecessary abstraction.
- Duplicate configuration.
- Stale cache edge cases.
- Partial-data loss.
- Probability-model edge cases.
- Tests that accidentally pass without exercising the relevant path.
- Network dependencies in CI.
- Changes that could break the next season transition.
- Regressions to the existing visual design.

Fix problems discovered during this review and rerun the affected tests. Do not stop after the first successful build.

---

## 10. Final acceptance criteria

- [ ] Future match probabilities are smoothed and do not become 0%/100% solely because of finite-sample win-rate extremes.
- [ ] Sweep probabilities use a documented prior and handle zero or very small samples sensibly.
- [ ] The probability model remains deterministic for a fixed input and seed.
- [ ] Qualification guarantees, confidence intervals, aggregate invariants, and tiebreaker tests still pass.
- [ ] A partially failed match-detail refresh preserves old records for failed IDs.
- [ ] Successful match refreshes replace stale records without duplicating rows.
- [ ] Partial refreshes are clearly identified and do not overwrite the last known-good snapshot with incomplete data.
- [ ] The final Liquipedia match block is captured when the input ends.
- [ ] Parser regression tests cover end-of-input and normal consecutive blocks.
- [ ] ETL failures cannot destroy or replace the existing valid database with an incomplete build.
- [ ] The normal regression workflow executes the probability-engine tests.
- [ ] GitHub Actions runs the required build and tests for pushes and pull requests to `main`.
- [ ] Cache entries are checked for season, schema, integrity, and freshness.
- [ ] Valid stale cache remains available offline without being misrepresented as fresh.
- [ ] Season-specific configuration is centralized where practical.
- [ ] The current Season 18 application remains the active, validated build.
- [ ] No speculative Season 19 rules or results have been introduced.
- [ ] Existing UI, bracket interactions, player stats, MVP data, assets, and offline behavior have no unrelated regressions.
- [ ] All required checks pass.

---

## 11. Completion report and Git

When finished, provide a concise but specific report covering:
1. The root cause and fix for each of the six areas.
2. The statistical prior selected and why.
3. How partial refreshes and cache freshness now work.
4. How the ETL parser and database publication were made safer.
5. Which tests and CI jobs were run and their actual results.
6. Any known limitations or deferred work.
7. Files changed and why.
8. The final commit SHA, if committed.

Commit changes using a descriptive message after all relevant checks pass. Push to `origin/main` only if the repository workflow permits it and the branch can be updated safely with a normal fast-forward push. Never force-push or discard unrelated local changes.

Do not claim success for any test or CI job that was not actually executed.

The task is complete only when the six improvements are implemented, verified, and the existing Season 18 application remains stable.
