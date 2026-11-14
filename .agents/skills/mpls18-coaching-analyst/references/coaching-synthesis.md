# Coaching synthesis reference

Read when turning accepted observations into insights, team/player/hero analyses, match-prep notes, or coaching briefs.

## Current state

Verify counts before quoting. As of 2026-11-14:

- 72 match reports exist; 27 have transcript observations, 45 are DB-only.
- 174 game timelines exist; 29 are boundary-verified, 145 DB-only.
- 66 player dossiers; 24 carry the new transcript cross-files, about 28 have any transcript evidence.
- 73 insights (70 player-level, 3 series-level) and 68 audits (67 player-level, 1 series-level).
- Team/hero/strategy pages exist but are mostly cross-file indexes, not synthesized analyses.
- One 3-series pilot coaching brief; no per-team briefs and no overall head-coach brief.
- Visual proof: 0 boundaries `visually_verified`.

The big goal is **not complete** even though the transcript pipeline is. Do not confuse “313 accepted observations” with “full-season coaching intelligence.”

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
- Do not claim full-season coverage while 45 matches remain DB-only.
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
