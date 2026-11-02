# Pilot quality report

**Pilot:** `pilot-mpl-s18-semantic-v1`
**Status:** first working end-to-end pilot; **not full-season coverage**
**Pilot coverage:** 3 series across 2 verified broadcast days / 2 videos
**Source-resolution coverage:** 27/27 metadata-verified, 26/27 fully caption-aligned, 1/27 partial
**Evidence store:** `analysis/evidence/pilot-ledger.jsonl` (canonical JSONL, versioned schema)

## Scope and selection

| Series | Date | Source | Video | Selection reason |
|---|---|---|---|---|
| 1036 EVOS 2–0 RRQ | 2026-08-14 | `src-s18-w01d01` | `40fehk2f4_E` | first series of the season; explicit draft commentary |
| 1037 NAVI 0–2 AE | 2026-08-14 | `src-s18-w01d01` | `40fehk2f4_E` | same broadcast, contrasting close late game; visually reviewable |
| 1107 ONIC 0–2 TLID | 2026-10-18 | `src-s18-w09d03` | `hY0Upem95uo` | final series, title-deciding context; objective/map-control commentary |

The two pilot sources were selected because their exact transcript lines align one-to-one with the official YouTube timed captions, and their video identities were verified by title/week/day/channel metadata. The wider local resolution pass now verifies all 27 official videos; 26 sources have full-line caption timing, and one remains partial.

## Processing coverage

- Sources imported: **27**, **9,682,086 bytes**, **27/27** SHA-256 verified after copy, **0** conflicts.
- Native timestamp strings in raw transcripts: **0**.
- Verified video IDs: **27/27** (official MPL Indonesia channel, exact season/week/day title).
- Fully caption-aligned sources: **26/27**. The pilot videos alone cover **9,104** and **12,273** lines; W1D1 has **9,103 exact + 1 normalized** and W9D3 has **12,273 exact + 0**.
- Partial alignment: **1/27** (`src-s18-w09d02`, `b9SktblDNuc`): 14,259 raw lines vs 14,551 caption snippets, 13,759 exact + 463 token-matched, 37 short ad/transition lines without trustworthy timestamps. Excluded from timestamp citations.
- Pilot evidence: **8 segments**, **18 observations**, **3 insights**, **1 audit**.
- Quote validation: **8/8** stored segments match the source line span exactly after newline normalization; **0** quote mismatches.
- Database references: every observation’s query is re-executed by the validator; **0** reproducibility errors.
- Visual review: **6** used frames, **1** rejected promotional overlay, **1** failed frame; **3** series-level frames / **2** contact sheets.
- Live video smoke test: **PASS** at requested 04:14:05 on `40fehk2f4_E` (actual 04:14:06.521), frame 669,722 bytes.

## Evidence inventory

| Type | Count | Notes |
|---|---:|---|
| Transcript / commentary observations | 8 | exact short quotes, source line spans, generated `t=` links |
| Database observations | 5 | schedule/game/team/pick/lineage/coverage queries |
| Gameplay observations | 2 | 5 frames reviewed, actual timestamps recorded |
| Counterexample observations | 3 | DB queries and corpus search |
| Insights | 3 | one `cross-checked`, two `partially-supported` |
| Audits | 1 | `AUD-1037-01`, verdict `partially supported` |

## What is supported

1. **`INS-1036-EARLY-DRAFT` (`cross-checked`)** — the caster’s early-snowball framing is consistent with EVOS’s Paquito/Eudora/Melissa game-1 lineup and a 16:51 tower-heavy win. Same-core losses and a 24:40 win are recorded as counterexamples.
2. **`INS-1037-LATE-SWING` (`partially-supported`)** — transcript, a reviewed frame and the database all support a close late game and base defense; the specific 1v3 causal story is not fully verified. Audit verdict: partially supported.
3. **`INS-1107-EARLY-CONVERSION` (`partially-supported`)** — commentary, visible gold leads and the database support a fast structure-heavy win in one game; tower damage is an outcome, not a causal signature.

## What is not supported

- No claim that a draft “caused” a win, that a team has a repeatable season-long trait, or that a player communicated/intended anything.
- No objective counts: the database has no per-game Lord/Turtle/Tower counts. Transcript mentions are commentary.
- No reaction-time, hidden-vision or mechanical-execution claims.
- No full-season semantic analysis. Twenty-six sources are alignment-ready, but only 3/72 series have curated semantic insights.
- No claim that unprocessed series are uninformative. They are simply not analyzed semantically yet.
- No timestamp citations from the partial source `src-s18-w09d02`; its 37 unmatched short lines remain explicitly unaligned.

## Data lineage finding

The guarded winner-orientation migration changed **21/72** `matches.winner` values so each agrees with its own row's `score_a/score_b` and `team_a/team_b` order. Post-migration integrity is **0/72** row-score mismatches; SQLite `integrity_check` returned `ok`. The database SHA-256 changed from `1fb1768560e1ca5c2613761e5a9150f77aecb1941096b557e16e072f772125a2` to `20c5ea2c51f30d1a24cd2ce6927f0d182b47f951ebd8209f1aaef429941cf2ef`.

`schedule_all.winner` is still expressed in schedule row order. `matches` sometimes stores the same series with the teams reversed, so map the named teams before comparing side tokens. The backup is `analysis/cache/migration-backups/winner-orientation-20261031T011845Z`.

The database also has **153/174** games with map mode, **173/174** with per-game VOD, **174/174** with recorded sides, **72/72** with series VOD and **72/72** with a Liquipedia series MVP. It has no per-game objective counts. See `analysis/reports/database-inventory.md`.

## Validation and tests

Deterministic analysis suite (`python tools/verify_analysis.py`, local corpus required):

- `test_transcript_import.py`: **4/4**
- `test_transcript_evidence.py`: **10/10**
- `test_video_frames.py`: **7/7**
- ledger validation: **PASS** (8 segments / 18 observations / 3 insights / 1 audit)
- source/corpus boundary check: **PASS** (27/27 source paths, hashes; raw/cache ignored)
- inventory regeneration: **PASS**

Live-only smoke (network, separately marked):

- `RUN_LIVE_VIDEO_SMOKE=1 python tools/test_video_frames_live.py`: **PASS**

Existing app verification (`python tools/verify.py`) passed **24/24 suites** after the migration. The migration intentionally modified `data/mpl_id_s18.db`, `data/csv/matches.csv` and the generated dashboard; all changes are backed up and validated. Season metadata and raw transcripts were not edited.

## Known gaps and next steps before scaling

1. Resolve or explicitly quarantine the 37 unmatched short lines in `src-s18-w09d02`; do not use that source for timestamp citations until then.
2. Build a mapping from each verified broadcast to all series/games and game start offsets; do not use fuzzy names alone.
3. Process more than one game per claimed pattern; use matched comparisons and patch partitions.
4. Review full clips for turning-point claims; still frames cannot prove a 1v3 or a Lord sequence.
5. Add OCR-assisted scoreboard extraction only if it can be validated; do not read blurry values.
6. Keep raw transcripts and media local. Only short quotes and derived metadata/reports belong in Git.
