> **Post-completion audit (2026-11-13):** Non-match routing added after the first completion audit. 313/313 accepted observations are cross-filed to player, team, hero, and strategy pages (979 links, 60 pages, 0 routing errors). Coverage: analysis/reports/transcript-pipeline/coverage.md.

> **COMPLETED 2026-11-13.** 27/27 S18 source ledgers validated; 363 observations extracted; 155 accepted and consolidated; 208 needs_review; 3 partial sources. Coverage: analysis/reports/transcript-pipeline/coverage.md.

# Goal: MPL S18 Transcript Knowledge Pipeline

**Status:** ready to start. This is the active goal. The execution contract is
`docs/goals/active/revised_transcript_workflow.md`.

## Objective

Turn the existing 27 Indonesian S18 transcripts into validated, source-linked
observations and consolidate them into the existing player, team, match, hero,
and strategy Markdown. Work one match at a time; do not process the whole season
in one pass.

## Inputs

- 27/27 raw transcripts: `analysis/sources/raw-transcripts/` (immutable).
- 27/27 timed alignments: `analysis/cache/timed/src-s18-*.json`
  (`src-s18-w09d02` is partial; use `null` timestamps where unaligned).
- Read-only stats bridge: `tools/stats_query.py`.
- Staging schema: `analysis/evidence/transcript-observation-schema.json`.
- Validator: `tools/validate_transcript_ledger.py`.
- Spec: `docs/goals/active/revised_transcript_workflow.md`.

## Start sequence

1. Read the spec and the two READMEs under `analysis/evidence/transcript-*`.
2. Run the setup gates:

   ```text
   python tools/test_stats_query.py
   python tools/test_transcript_ledger.py
   ```

3. Pick one representative match from `src-s18-w01d01` or another dense
   tactical source.
4. Build its segment ledger in `analysis/evidence/transcript-segments/`.
5. Extract 20–50 observations into
   `analysis/evidence/transcript-observations/`.
6. Validate with `tools/validate_transcript_ledger.py`.
7. Spot-check 10 observations, consolidate accepted ones into at most two
   Markdown files, and write the run report.
8. Only after the prototype passes, process 3 varied sources, then the remaining
   24.

## Phases

- **Phase 0 — Setup gates:** tests and one-match prototype. (Tooling is already
  in place; the prototype is the first real run.)
- **Phase 1 — Prototype:** one match end-to-end with measured cost.
- **Phase 2 — Batch:** 27/27 source ledgers, tracked as `complete`, `partial`, or
  `blocked`.
- **Phase 3 — Consolidation and coverage:** accepted observations merged;
  unresolved queue and proposals reported; database bridge tests pass.

## Completion

- 27/27 source ledgers validated.
- Every accepted observation consolidated or explicitly deferred.
- Database bridge tests pass and published numbers are reproducible.
- Coverage report matches the ledgers.
- Visual-proof status unchanged.

## Non-goals

- Visual verification or screenshot review.
- Full-season coaching briefs.
- Complete 174-game timelines.
- Evidence-backed profiles for every entity in this pass.
- Editing raw transcripts or `data/mpl_id_s18.db`.

## First command

```text
python tools/stats_query.py --match 1037 --stat result
```

Then build the first segment ledger. Do not start by cleaning all 27 transcripts.
