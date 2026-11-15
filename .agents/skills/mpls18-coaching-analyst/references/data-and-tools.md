# Data and tooling reference

Read for database queries, source/timed alignment, PowerShell/tooling issues, goal workflow, and validation conventions.

## Canonical database

- Path: `data/mpl_id_s18.db`
- Query catalogue: `analysis/evidence/query-catalog.json`
- Snapshot: `mpl-s18-db-20c5ea2c51f3` and hash `20c5ea2c51f30d1a24cd2ce6927f0d182b47f951ebd8209f1aaef429941cf2ef` (verify before quoting; the DB must not change).
- Read-only bridge: `tools/stats_query.py`
- Expected scale: 72 series, 174 games, 66 players, 9 teams. Verify from the database, not memory.

Commands:

```text
python tools/stats_query.py --match 1037 --stat result
python tools/stats_query.py --match 1037 --stat games
python tools/stats_query.py --match 1037 --stat teams
python tools/stats_query.py --player MORENOOO --stat season
python tools/stats_query.py --team "BIGETRON BY VIT" --stat season
python tools/stats_query.py --hero LING --stat season
python tools/stats_query.py --match 1037 --game 1 --stat players
```

Every result includes `query_id`, SQL, params, fields, provenance, `snapshot_id`, `snapshot_sha256`, rows, and row count. Cite these in Markdown. Do not hand-copy numbers.

### Orientation trap

`matches.winner` is relative to `matches.team_a/team_b`; `schedule_all.winner` is relative to schedule row order. Do not compare side tokens across tables without mapping the named teams. Use the query catalogue provenance or derive the result from the score in the same row.

## Sources and timed alignment

- Manifest: `analysis/sources/source-manifest.json`
- Raw transcripts: `analysis/sources/raw-transcripts/` (immutable)
- Timed captions: `analysis/cache/timed/<source_id>.json`
- 27 metadata-verified sources; 26 fully aligned; `src-s18-w09d02` partial.

Raw text has no timestamps or speaker labels. The timed JSON is a derived caption alignment; never describe it as frame-accurate. For unaligned lines use null cues and `timestamp_provenance: "none"`.

The `ALL MPL TRANSCRIPT` download is not a replacement: 26 Indonesian S18 files with three vertical-only days, and the extracted text is lossy. Use the existing 27 raw + timed sources or the 107 official game-VOD transcripts.

## Game-VOD layer

- Manifest: `analysis/evidence/game-transcript-manifest.json`
- Cache: `analysis/cache/game-transcripts/<video_id>.json`
- Schema: `analysis/evidence/game-observation-schema.json`
- Ledger: `analysis/evidence/game-observations/<match>.jsonl`
- Validator: `tools/validate_game_observations.py`
- Coverage: `tools/build_coverage_matrix.py` reports game-transcript availability, `GOBS-*` matches, and combined transcript evidence.

The game-VOD layer is separate from the 27-source `TOBS-*` ledger. See `references/game-vod-transcripts.md`.

## Validation

```text
python tools/verify.py
python tools/ci_semantic_check.py
python tools/validate_game_offsets.py
python tools/transcript_coverage.py
python tools/validate_transcript_ledger.py --ledger <ledger> --segments <segments>
python tools/validate_game_observations.py
python tools/build_match_evidence.py --check
python tools/build_coverage_matrix.py
```

`tools/verify.py` runs 28 suites (2026-11-15): application regression, lint, transcript ledger, game observations, and goal artifacts. If lint fails, run:

```text
python -m ruff check tools --select F401,F841,E722,E9 --line-length 200
```

`ruff` is not on PATH in this environment; use `python -m ruff`.

## PowerShell and temp scripts

Complex `python -c` commands fail in PowerShell when they contain JSON, backticks, `$defs`, or nested quotes. Write a temporary `.py` file outside the repo with the `write` tool and run it. Do not burn turns escaping shell strings.

Examples of failures seen:

- `python -c` with a JSON dictionary and `\"` → `SyntaxError` or empty variable expansion.
- `$defs` in a JSON Schema access → PowerShell expands it to empty.
- Multi-line Python inside double quotes → unterminated string.

Default: write `C:\Users\nberl\AppData\Local\Temp\opencode\<task>.py`, run it, delete it when done if sensitive.

## Goal workflow

- Active goals: `docs/goals/active/`
- Finished goals: `docs/goals/finished/`
- When a goal is finished, move its Markdown file from active to finished per `AGENTS.md`.
- Do not reopen a closed goal without an explicit user instruction; the goal tool rejects plan edits on closed goals.
- The transcript goal is finished at `docs/goals/finished/mpl-s18-transcript-knowledge-goal.md`.
- The visual-proof handoff remains active and incomplete at `docs/goals/active/mpl-s18-visual-proof-deepseek-handoff.md`.

## Documentation sources of truth

- Current project state: `analysis/index.md`
- Canonical coverage: `analysis/reports/coverage-matrix.md` and `analysis/evidence/coverage-matrix.json`
- Broadcast transcript coverage: `analysis/reports/transcript-pipeline/coverage.md` and `analysis/evidence/transcript-pipeline-coverage.json`
- Game-VOD transcript availability: `analysis/evidence/game-transcript-manifest.json`
- Visual status: `analysis/evidence/visual-review-status.json` and the visual handoff
- `analysis/reports/coverage-summary.md` is historical; do not cite it for current coverage.

## Git and safety

- The worktree may contain unrelated user changes; inspect `git status` before edits.
- Do not commit raw transcripts, media, browser profiles, credentials, or local-only caches.
- Do not install packages or commit unless asked.
- Do not modify `data/mpl_id_s18.db` or raw transcripts as part of analysis or validation.
