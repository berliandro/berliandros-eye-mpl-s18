# Coaching synthesis reference

Read when turning accepted observations into insights, team/player/hero analyses, match-prep notes, or coaching briefs.

## Current state

Verify current counts in `analysis/reports/coverage-matrix.md`; do not quote stale numbers.

- Match evidence is complete; broadcast transcript coverage is 27 sources; game-VOD coverage is tracked separately in the manifest and matrix.
- Team, hero, strategy, and coaching pages exist; check the page before calling a topic analyzed.
- Visual proof is separate and not verified.

Do not confuse accepted observations with full-season coaching intelligence, and do not claim transcript depth for a match whose `GOBS-*` or `TOBS-*` ledger is empty.

## Evidence rules

- A quotation proves what the caster said, not that the event happened.
- Separate `commentary`, `observation`, `statistic`, and `inference`. Never promote commentary into a fact.
- Statistics must come from `tools/stats_query.py` with `query_id` and snapshot hash. Do not calculate totals from transcript text.
- One-game observations stay one-game. Longitudinal claims need multiple games, a denominator, and relevant comparisons.
- Search for counterexamples before promoting a tendency. State the strongest alternative explanation.
- Respect patch and map periods; do not compare across a patch/map change without labelling it.
- Keep unresolved identities and missing facts explicit. Do not invent player/team/hero joins.

## Insight workflow

1. Start from accepted observations in the relevant match/player/team/hero page; do not re-read the whole corpus by default.
2. Pull the supporting DB rows with the stats bridge.
3. Search for confirming and contradicting cases in other matches.
4. Classify the claim:
   - `supported`
   - `partially supported`
   - `contradicted`
   - `inconclusive`
5. Write the claim with scope, sample, evidence links, counterexample, confidence, and limitations.
6. Put it in the narrowest useful page: player dossier for player claims, team page for team claims, hero page for hero claims, strategy page for tactical patterns, match report for game-specific claims.
7. Add coaching usefulness only when the evidence supports it: prep question, punishable pattern, drill, or decision rule. Label hypotheses as hypotheses.

## Output discipline

- Do not duplicate an existing insight or audit; update/version it instead.
- Do not upgrade a verdict to make coverage look better.
- Do not present a team/hero cross-file index as a finished analysis.
- Do not claim full-season transcript depth while matches lack extracted transcript observations.
- Keep the coverage report honest about partial sources and visual gaps.

## Where to write

- Match-specific: `analysis/matches/<match>.md`
- Player: `analysis/players/<player>.md`
- Team: `analysis/teams/<team>.md`
- Hero: `analysis/heroes/<hero>.md`
- Strategy: `analysis/strategy/<topic>.md`
- Coaching briefs: `analysis/coaching/`
- Cross-cutting reports: `analysis/reports/`

## Before calling an insight done

- The claim is falsifiable and scoped.
- The evidence links resolve.
- The DB numbers reproduce through the bridge.
- Counterexamples are included.
- The verdict matches the evidence.
- The limitation is visible.
- The coaching recommendation does not exceed the evidence.
