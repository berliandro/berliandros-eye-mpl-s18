# Semantic coaching intelligence — analysis area

This directory contains the first **traceable, transcript-powered** coaching pilot for Berliandro’s Eye. It is deliberately separate from the app and the canonical match database.

**Status:** pilot complete (2 caption-aligned videos, 3 series, 18 observations, 3 insights, 1 audit). **Not** full-season semantic coverage. The canonical schedule provides one VOD candidate for each transcript date, but candidates remain unverified until official metadata and caption alignment pass.

## What is here

| Path | Purpose |
|---|---|
| `sources/source-manifest.json` | 27 local transcript sources, hashes, schedule-derived VOD candidates, broadcast-date/series mappings, and verification status |
| `sources/copy-verification.json` | byte/hash copy verification of the source corpus |
| `sources/raw-transcripts/` | **local-only, Git-ignored** copy of the original corpus |
| `reports/corpus-inventory.md` | corpus counts, timestamp/link coverage and parsing risks |
| `reports/database-inventory.md` | read-only DB coverage, lineage warnings and join guidance |
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
- The app database, CSVs, season metadata and dashboard were treated as read-only. No ETL/build was run by this project.
- Reports contain only short quotations needed to support a claim; the ledger preserves exact source line spans and hashes.

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

# 4. Search exact transcript text with line numbers and timestamps
python tools/transcript_evidence.py search --source-id src-s18-w01d01 `
  --pattern "turtle|lord|rotasi" --context 2

# 5. Rebuild and validate the pilot ledger
python tools/transcript_evidence.py build --selection analysis/pilot/selection.json
python tools/transcript_evidence.py validate

# 6. Regenerate inventories/reports
python tools/analysis_inventory.py

# 7. Deterministic tests
python tools/verify_analysis.py

# 8. Optional live YouTube frame smoke test (network)
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
- **Database record** is tied to snapshot `mpl-s18-db-1fb1768560e1`, SQL, parameters and returned rows.
- **Gameplay observation** is only used where frames were actually reviewed; frame paths and actual times are recorded.
- **AI inference** is an insight, labelled with alternatives, counterexamples, scope and confidence rationale.
- Verification states are separate from evidence types. A transcript-only claim is never upgraded to gameplay-verified.

## Important lineage warning

The existing `matches.winner` column is **not** reliable in `matches` team order: 21/72 rows disagree with the score because team order is flipped relative to `schedule_all`. Use `schedule_all.winner` or derive the winner from `score_a/score_b`. See `analysis/reports/database-inventory.md` and `OBS-LINEAGE-WINNER`.

## What this is not

- Not a full-season semantic analysis.
- Not a claim that the 25 unlinked days are uninformative.
- Not a replacement for watching full games or for the app’s structured database.
- Not a source of objective counts, hidden vision, communications or intent.

## Next milestone

Resolve and align the remaining 25 video sources, map each broadcast to all series/game start offsets, then re-run the pilot process on a stratified sample before scaling. Only after quotation fidelity, timestamp/link integrity and audit quality hold across that sample should all nine weeks be processed.
