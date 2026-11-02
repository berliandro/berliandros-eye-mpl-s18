# Semantic coaching intelligence — analysis area

This directory contains the first **traceable, transcript-powered** coaching pilot for Berliandro’s Eye. It is deliberately separate from the app and the canonical match database.

**Status:** source resolution complete locally — **27/27** official videos metadata-verified, **26/27** fully caption-aligned, **1/27** partial and explicitly not citation-ready. The curated pilot covers 3 series with 18 observations, 3 insights and 1 audit. **Not** full-season semantic coverage.

## What is here

| Path | Purpose |
|---|---|
| `sources/source-manifest.json` | 27 local transcript sources, hashes, schedule-derived VOD candidates, broadcast-date/series mappings, and verification status |
| `sources/copy-verification.json` | byte/hash copy verification of the source corpus |
| `sources/raw-transcripts/` | **local-only, Git-ignored** copy of the original corpus |
| `reports/corpus-inventory.md` | corpus counts, timestamp/link coverage and parsing risks |
| `reports/video-source-resolution.md` | 27-source metadata/alignment status, status semantics and failure reasons |
| `reports/database-inventory.md` | DB coverage, post-migration lineage and join guidance |
| `reports/pilot-quality-report.md` | pilot scope, coverage, validation results and gaps |
| `reports/audit-INS-1037-LATE-SWING.md` | skeptical audit of the main ambiguous insight |
| `matches/` | one report for each pilot series |
| `coaching/pilot-coaching-brief.md` | practical prep questions/drills with evidence |
| `evidence/evidence-schema.json` | versioned JSON Schema for ledger records |
| `evidence/pilot-ledger.jsonl` | canonical pilot evidence (short excerpts only) |
| `evidence/query-catalog.json` | reproducible read-only SQL for every database reference |
| `evidence/database-snapshot-manifest.json` | DB fingerprint, tables, coverage, lineage |
| `evidence/audit-log.jsonl` | append-only audit record export |
| `evidence/visual-review.json` | which frames were reviewed, used, rejected or failed |
| `evidence/timed-alignment.json` | derived caption alignment coverage |
| `pilot/selection.json` | curated pilot claims/quotes; input to the deterministic builder |
| `cache/` | **local-only, Git-ignored** timed captions, screenshots, contact sheets |

## Data safety

- The original transcript directory was **copied, not moved or edited**. Its 27 files and 9,682,086 bytes match the copies by SHA-256; no conflicts occurred.
- `analysis/sources/raw-transcripts/` and `analysis/cache/` are Git-ignored. Raw transcripts, full videos, cookies and screenshots are not committed.
- The app database and CSVs were read-only until the explicit, backed-up winner-orientation migration. That migration changed only `matches.winner` values that disagreed with their own row score, then regenerated `matches.csv`, the dashboard and snapshot-bound evidence through the supported pipeline.
- Season metadata and all source transcripts were not edited. Reports contain only short quotations needed to support a claim; the ledger preserves exact source line spans and hashes.

## How to reproduce (local machine with the corpus)

```powershell
# 1. Copy and verify the corpus (safe/idempotent; never overwrites a conflict)
python tools/import_transcripts.py `
  --source "D:\! Coding\~ shit projects\get-youtube-transcript\mpl-s18-raw-transcripts"

# 2. Verify schedule-derived VOD candidates against official metadata and align
#    every local transcript line to official timed captions. This is resumable.
python tools/resolve_and_align_sources.py

# Optional metadata-only pass:
python tools/resolve_and_align_sources.py --no-align

# Retry an individual source after network/transcript failures:
python tools/resolve_and_align_sources.py --source-id src-s18-w02d01

# 3. Search exact transcript text with line numbers and timestamps
python tools/transcript_evidence.py search --source-id src-s18-w01d01 `
  --pattern "turtle|lord|rotasi" --context 2

# 4. Rebuild and validate the pilot ledger
python tools/transcript_evidence.py build --selection analysis/pilot/selection.json
python tools/transcript_evidence.py validate

# 5. Regenerate inventories/reports
python tools/analysis_inventory.py

# 6. Deterministic tests
python tools/verify_analysis.py

# 7. Optional live YouTube frame smoke test (network)
$env:RUN_LIVE_VIDEO_SMOKE="1"
python tools/test_video_frames_live.py
Remove-Item Env:RUN_LIVE_VIDEO_SMOKE
```

## Video frames

`tools/video_frames.py` captures full-frame screenshots at requested broadcast timestamps. It resolves a registered source, writes a sidecar per frame (canonical URL, timestamp link, requested/actual time, method, versions, output hash, errors) and can build a contact sheet.

```powershell
python tools/video_frames.py --source-id src-s18-w01d01 `
  --timestamps 04:13:50,04:14:05 --around-seconds 2 --contact-sheet
```

On this machine, yt-dlp/FFmpeg section downloads from the long VODs stalled; the YouTube path uses the installed Playwright Chromium player, while FFmpeg is used for local files and is covered by a synthetic-video unit test. The tool never downloads a full broadcast, never bypasses access restrictions, and never marks a frame “verified” merely because capture succeeded.

## Evidence rules

- **Transcript quotation** proves what the speaker said, not that the interpretation is correct.
- **Database record** is tied to snapshot `mpl-s18-db-20c5ea2c51f3`, SQL, parameters and returned rows.
- **Gameplay observation** is only used where frames were actually reviewed; frame paths and actual times are recorded.
- **AI inference** is an insight, labelled with alternatives, counterexamples, scope and confidence rationale.
- Verification states are separate from evidence types. A transcript-only claim is never upgraded to gameplay-verified.

## Database winner-orientation repair

The guarded local migration has been executed and verified.

- Preview: **21/72** `matches` rows had a `winner` that disagreed with the score in that row's own `team_a/team_b` order.
- Apply: **21 rows changed** in SQLite and **21 rows changed** in `data/csv/matches.csv`; the dashboard and snapshot-bound evidence were regenerated.
- Database SHA-256: `1fb1768560e1ca5c2613761e5a9150f77aecb1941096b557e16e072f772125a2` → `20c5ea2c51f30d1a24cd2ce6927f0d182b47f951ebd8209f1aaef429941cf2ef`.
- Post-migration gate: **0/72** row-score winner mismatches; SQLite `integrity_check` = `ok`; full regression **24/24**.
- Backup: `analysis/cache/migration-backups/winner-orientation-20261031T011845Z` (Git-ignored; contains the pre-migration DB, CSV, HTML and evidence/report files).

The command is idempotent: a second preview reports zero changes. To reproduce the preview/apply workflow:

```bash
python tools/repair_match_winner_orientation.py
python tools/repair_match_winner_orientation.py --apply
```

The apply command backs up the affected files, repairs `matches.winner` relative to that row's score/team order, rebuilds snapshot-bound evidence references and generated artifacts, then runs the evidence, integrity, parity and full regression validators. A failed stage triggers rollback. It does not edit raw transcript files.

## Important lineage note

`matches.winner` is now correct **relative to `matches.team_a/team_b`**. `schedule_all.winner` remains relative to schedule row order. The two tables sometimes store the same series with the teams in the opposite order, so map the named teams before comparing side tokens. See `analysis/reports/database-inventory.md` and `OBS-LINEAGE-WINNER`.

## What this is not

- Not a full-season semantic analysis: 26 sources are alignment-ready, but only 3 series have curated insights.
- Not a claim that the partially aligned source is uninformative; it is simply not citation-ready until its remaining short lines are resolved.
- Not a replacement for watching full games or for the app’s structured database.
- Not a source of objective counts, hidden vision, communications or intent.

## Next milestone

Map each verified broadcast to series/game start offsets, expand the curated evidence sample beyond the three pilot series, and resolve or explicitly quarantine the 37 unmapped short lines in `src-s18-w09d02`. Only after quotation fidelity, timestamp/link integrity and audit quality hold across a stratified sample should all nine weeks be processed semantically.

## Final regular-season standings (source-reported, cross-checked)

| Rank | Team | Match W-L | Game W-L |
|---:|---|---:|---:|
| 1 | TEAM LIQUID ID | 12-4 | 26-11 |
| 2 | NAVI | 12-4 | 25-12 |
| 3 | ALTER EGO ESPORTS | 10-6 | 23-13 |
| 4 | BIGETRON BY VIT | 10-6 | 21-18 |
| 5 | EVOS | 8-8 | 19-21 |
| 6 | ONIC | 7-9 | 19-21 |
| 7 | DEWA UNITED | 5-11 | 14-25 |
| 8 | RRQ HOSHI | 4-12 | 14-27 |
| 9 | GEEK FAM | 4-12 | 13-26 |

Cross-checked against the official MPL Indonesia Season 18 standings (id-mpl.com / Liquipedia) and the canonical database snapshot `mpl-s18-db-20c5ea2c51f3`.

## How to add a series (workflow)
Follow this checklist to add a new series with full provenance:

1. **Resolve source**: Ensure the broadcast day is in `source-manifest.json` with verified `video_id` and `caption_alignment_status: verified` (non-quarantined). `src-s18-w09d02` is quarantined - do not cite.
2. **Confirm citation-ready**: Check alignment coverage is full-line (no unmapped lines). Run `python tools/transcript_evidence.py build` to validate.
3. **Map offsets**: Update `analysis/evidence/game-offsets.json` for the series with `start_seconds`, `confidence`, `method`, `provenance`. Run `python tools/validate_game_offsets.py`.
4. **Detect boundaries**: Use `python tools/refine_game_offsets.py` or manual boundary detection with audit trail (caster transitions/scoreboard/series changes). Mark low confidence items for review.
5. **Extract quotes**: Use `transcript_evidence.py` to find exact spans with `line_hint`. Only use fully aligned sources.
6. **Add frames**: Use `tools/video_frames.py` with purpose, verdict (used/rejected), and rejection reason. Tie frames to observations/segments.
7. **Cross-ref DB**: Link to `matches`, `games`, `team_games`, `schedule_all` with query provenance from `analysis/evidence/query-catalog.json`.
8. **Audit**: For turning points, require supporting evidence (quote + context + DB state where possible). Follow existing audit structure.
9. **Build & validate**: Run `python tools/transcript_evidence.py build --selection ...` and `python tools/transcript_evidence.py validate`. Run `python tools/verify_analysis.py`. No citations from quarantined/partial sources allowed.
