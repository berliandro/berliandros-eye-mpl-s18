# Transcript pipeline reference

Read when building, reviewing, routing, or validating **broadcast** transcript observations. For official per-game VOD transcripts and `GOBS-*` records, read `references/game-vod-transcripts.md` instead.

## Inputs

- 27 raw transcripts: `analysis/sources/raw-transcripts/`
- 27 timed alignments: `analysis/cache/timed/<source_id>.json`
- Source manifest: `analysis/sources/source-manifest.json`
- One match per source is planned in `analysis/evidence/transcript-pipeline-plan.json`.

Raw `.txt` files have no native timestamps or speaker labels. Timestamps are a one-to-one caption alignment (`youtube-auto-caption-alignment-v1`), not frame-accurate metadata. `src-s18-w09d02` is partial; unaligned lines must use null cues and `timestamp_provenance: "none"`.

The separate `ALL MPL TRANSCRIPT` download is not a complete replacement: 26 Indonesian S18 files with three vertical-only days, and its extracted text is lossy. Do not use it as source of truth.

The 107 official game-VOD transcripts in `analysis/cache/game-transcripts/` are a separate, higher-fidelity source for the 45 missing matches. They do not enter this 27-source `TOBS-*` ledger; use `references/game-vod-transcripts.md`.

## Artifacts

```text
analysis/evidence/transcript-segments/<source_id>-<match_id>-g1.jsonl
analysis/evidence/transcript-observations/<source_id>-<match_id>-g1.jsonl
analysis/evidence/transcript-pipeline-plan.json
analysis/evidence/transcript-pipeline-coverage.json
analysis/evidence/transcript-routing.json
analysis/evidence/transcript-review-decisions.jsonl
analysis/reports/transcript-pipeline/
```

Schema: `analysis/evidence/transcript-observation-schema.json`.

## Build a segment ledger

Use a bounded match/game window, not a whole VOD:

```text
python tools/build_transcript_segments.py \
  --source-id src-s18-w01d01 \
  --start-line 350 --end-line 4600 --max-lines 10 \
  --out analysis/evidence/transcript-segments/src-s18-w01d01-1036-g1.jsonl
```

A segment has `segment_id`, `source_id`, raw line range, `cue_start/end`, `timestamp_link`, `segment_type`, `include`, `exclude_reason`, `text`, `text_sha256`. Verify raw and timed line counts match before building.

## Observation ledger

Accepted staging records use:

- `observation_id` (`TOBS-...`), `source_id`, `segment_id`
- exact `quote`, `quote_sha256`
- `raw_line_start/end` and `cue_start/end` tightened to the quote, not the whole segment
- `timestamp_provenance`, `timestamp_link`
- `speaker` normally null, `speaker_basis: "unavailable"`
- `segment_type`, `claim`, `claim_type`, `topic`
- `entities` (`players`, `teams`, `heroes`, `maps`, `matches`)
- `destination` = match report; `cross_destinations` = non-match pages
- `status` (`accepted`, `needs_review`, `rejected`, `duplicate`), `confidence`, `notes`
- `database_refs` for statistics; `visual_refs` normally empty
- `extraction` model/provider/prompt/run metadata

Keep exact quotes short. Do not paraphrase the source text; paraphrase only the claim.

## Validate

```text
python tools/validate_transcript_ledger.py \
  --ledger analysis/evidence/transcript-observations/<ledger>.jsonl \
  --segments analysis/evidence/transcript-segments/<ledger>.jsonl
```

The validator checks schema, quote hash, quote presence, line/cue bounds, duplicate keys, statistic DB refs, unresolved records, and run counts. It cannot judge whether a claim overreaches the quote; the main agent must spot-check that.

## Review rules

Accept only when:

- the exact quote supports the claim as written;
- `claim_type` is correct (`commentary` is not fact);
- no player/team/hero/number is invented;
- game-1 material is not game 2/3 evidence;
- the claim is not a mere lead-in for a statistic unless `database_refs` carry the numbers.

Reject overreach, vague fragments, wrong-game material, and unresolvable ASR references. For ambiguous names, check `player_season_stats` and `hero_stats` before deciding; do not guess.

Batch review pattern that worked:

1. A text-only Beam Max subagent triages all `needs_review` records into `accept|reject|merge|needs_human`.
2. Main agent samples accepted/rejected records against full segments.
3. Apply decisions, then add newly accepted records to match reports.
4. Re-route and recompute coverage.

## Route and cover

```text
python tools/route_transcript_observations.py
python tools/transcript_coverage.py
```

Routing keeps the match report as primary destination and adds player/team/hero/strategy cross-files. Coverage must show:

- 0 validation errors
- 0 routing errors
- 0 accepted IDs missing from match reports
- all accepted observations with at least one non-match destination

Current broadcast state: 27 source ledgers validated. Verify exact counts with `python tools/transcript_coverage.py` and `analysis/reports/transcript-pipeline/coverage.md`; do not quote stale numbers. Game-VOD coverage is separate in `analysis/evidence/game-transcript-manifest.json`.

Partial sources: `src-s18-w02d03` (1050 intro/interview), `src-s18-w07d03` (1091 desk/draft), `src-s18-w08d02` (1094 desk/commentary). Retry with a different game window or explicitly keep partial.

## Common failure fixes

- Quote not found: the quote spans lines differently than the segment text; copy the exact substring or choose a containing segment.
- Segment missing: the observation points at a boundary group or a line range outside the built segment ledger; rebuild with the correct window.
- Cue mismatch: cue points at segment start, not quote start; recompute from the quote's first/last line using the timed JSON.
- Statistic claim rejected: the quote is only a lead-in; either move the numbers into `database_refs` or reject the record.
- Routing overreach: use claim-mentioned players/heroes first, entity lists only as fallback.
- Duplicate sections in player dossiers: update between `transcript-routing:start/end`, do not append again.
