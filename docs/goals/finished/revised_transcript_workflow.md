# MPL S18 Transcript Knowledge Pipeline — Execution Spec

**Status:** completed 2026-11-13. The non-goals below applied to this pipeline only; the coaching layer is delivered separately in `analysis/coaching/`. Visual proof remains separate and incomplete. Superseded as a working spec by the delivered coaching product.

**Objective:** turn the 27 existing Indonesian S18 transcripts into validated,
source-linked observations and consolidate them into the existing Markdown at low
token cost.

**Non-goals:** re-downloading transcripts, editing raw files or the canonical
database, proving visual claims, full-season coaching briefs, or complete
profiles for every entity in one pass.

## Inputs

- 27/27 Indonesian S18 raw transcripts in `analysis/sources/raw-transcripts/`
  (local-only, immutable).
- 27/27 timed alignments in `analysis/cache/timed/src-s18-*.json`.
  `src-s18-w09d02` is partial: its unaligned lines get `timestamp: null`.
- `data/mpl_id_s18.db` via `analysis/evidence/query-catalog.json` (read-only).
- Existing Markdown `analysis/players/`, `analysis/matches/`; canonical schema
  `analysis/evidence/evidence-schema.json`.

`ALL MPL TRANSCRIPT` is optional: it has 26 Indonesian S18 files, with three days
vertical-only, so it does not replace the 27 existing transcripts. Raw `.txt`
files have no timestamps or speaker labels; timestamps come only from the timed
alignment layer.

## Artifacts

```text
analysis/evidence/transcript-segments/<source_id>.jsonl
analysis/evidence/transcript-observations/<source_id>.jsonl
analysis/reports/transcript-pipeline/<source_id>.md
```

The **segment ledger** records include/exclude, type, raw line range, cue range,
exact text, and exclusion reason. The **observation ledger** records one atomic
observation with quote, provenance, entities, destination, confidence, status.
Staging ledgers are not canonical; only validated records are consolidated.

## Pipeline

1. **Verify source.** Check manifest, raw SHA-256, alignment status, video ID,
   duration. Stop on mismatch.
2. **Build segment ledger.** Join raw lines to cues. Classify `pre_match`,
   `draft`, `gameplay`, `post_match`, `interview`, `analysis`, `ad`, `intro`,
   `outro`, `unknown`. Keep interviews tagged; do not delete them.
3. **Chunk by match.** One match or bounded cue window per run, not a whole VOD.
   Load only the central index, relevant registries, and the window.
4. **Extract.** Use the 1M-context model with a strict schema. Require quote,
   line range, cue range when available, entity IDs, claim type, topic,
   destination, confidence. Ambiguous names become unresolved records.
5. **Validate.** Quote substring/hash must match; line/cue ranges must fit;
   canonical IDs must exist; duplicates detected; destinations exist. No record
   reaches Markdown if validation fails.
6. **Consolidate.** Main agent merges accepted observations by match or team,
   with dry-run/diff, idempotent writes, no silent overwrites.
7. **Report.** Write the run report and coverage index.

## Database bridge

No hand-copied numbers. Use the read-only bridge `tools/stats_query.py`:

```text
get_player_stat(player, stat, hero=None, period=None)
get_team_stat(team, stat, map=None, period=None)
get_match_stat(match_id, stat)
get_game_stat(match_id, game_no, stat)
```

Each result carries `query_id`, SQL, params, snapshot ID/hash, rows, row count,
and provenance. New queries go in `analysis/evidence/query-catalog.json`. Open
SQLite read-only. Verify patch/map period before comparisons. Only expose fields
that exist in the database; item-level data may not be available.

## Quality gates

- 100% exact quote + `quote_sha256`; 100% raw line range.
- Cue range present or explicitly `null`.
- 0 invented player/team/hero/map IDs.
- Duplicate rate below 5% per source.
- Every unresolved reference and proposed category recorded.
- 10 observations per source spot-checked.
- Time and token usage reported per source.
- No unvalidated observation written to Markdown.
- Validator: `tools/validate_transcript_ledger.py`.

## Prototype and batches

Prototype one match chunk end-to-end: segment ledger, 20–50 observations,
validator pass, 10-record spot-check, consolidation into at most two Markdown
files, run report with cost and unresolved items. Use the 1M model, but still
chunk by match.

Then batch 3 varied sources, then the remaining 24. Track `pending`,
`in_progress`, `complete`, `partial`, `blocked` per source — not percentages.

## Completion

27/27 source ledgers validated; accepted observations consolidated or explicitly
deferred; database bridge tests pass; coverage report matches the ledgers;
visual-proof status unchanged.

## Goal split

1. **Transcript knowledge pipeline** — this spec; active.
2. **Database bridge** — read-only stats API and query catalog; active.
3. **Visual proof** — existing handoff; separate and incomplete.

Retire from the old goal: full-season per-team coaching briefs, complete 174-game
timelines, evidence-backed profiles for every entity, and visual verification as
a prerequisite. Partial coverage is acceptable.

## Forbidden

- Editing raw transcripts or the canonical database.
- Inventing timestamps, quotes, speaker labels, IDs, or statistics.
- Assigning ambiguous names without an unresolved record.
- Treating the LLM-cleaned `ALL MPL TRANSCRIPT` output as source of truth.
- Using screenshots/video by default.
- Marking visual claims verified from this workflow.

**Schema:** `analysis/evidence/transcript-observation-schema.json`.
