# Pilot quality report

**Pilot:** `pilot-mpl-s18-semantic-v1`
**Status:** first working end-to-end pilot; **not full-season coverage**
**Coverage:** 3 series across 2 verified broadcast days / 2 videos
**Evidence store:** `analysis/evidence/pilot-ledger.jsonl` (canonical JSONL, versioned schema)

## Scope and selection

| Series | Date | Source | Video | Selection reason |
|---|---|---|---|---|
| 1036 EVOS 2–0 RRQ | 2026-08-14 | `src-s18-w01d01` | `40fehk2f4_E` | first series of the season; explicit draft commentary |
| 1037 NAVI 0–2 AE | 2026-08-14 | `src-s18-w01d01` | `40fehk2f4_E` | same broadcast, contrasting close late game; visually reviewable |
| 1107 ONIC 0–2 TLID | 2026-10-18 | `src-s18-w09d03` | `hY0Upem95uo` | final series, title-deciding context; objective/map-control commentary |

The two sources were selected because their exact transcript lines align one-to-one with the official YouTube timed captions, and their video identities were verified by title/week/day/channel metadata. The other 25 days remain unmapped to a video ID.

## Processing coverage

- Sources imported: **27**, **9,682,086 bytes**, **27/27** SHA-256 verified after copy, **0** conflicts.
- Native timestamp strings in raw transcripts: **0**.
- Verified video IDs: **2/27**.
- Timed alignments: **2/2** verified videos; **9,104** and **12,273** lines; **9,103 + 1** exact/whitespace-normalized match on W1D1 and **12,273 + 0** on W9D3.
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
- No full-season semantic analysis. Only 2/27 sources and 3/72 series have been processed.
- No claim that the other 25 transcript days are unusable; they are simply not linked to a verified video or analyzed.

## Data lineage finding

`matches.winner` disagrees with the score in **21/72** rows because `matches.team_a/team_b` is flipped relative to `schedule_all` while `winner` keeps schedule orientation. This report and ledger use `schedule_all` or the score, never `matches.winner`. This is a read-only finding; the app database was not modified.

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

Existing app verification (`python tools/verify.py`) passed **20/20 suites** after this work. The semantic work did not modify the app database, CSVs, season metadata or dashboard.

## Known gaps and next steps before scaling

1. Resolve video IDs for the remaining 25 transcript days (exact title/week/day/channel match + timed alignment), then align timestamps.
2. Build a mapping from a broadcast day to all series/games and game start offsets; do not use fuzzy names alone.
3. Process more than one game per claimed pattern; use matched comparisons and patch partitions.
4. Review full clips for turning-point claims; still frames cannot prove a 1v3 or a Lord sequence.
5. Add OCR-assisted scoreboard extraction only if it can be validated; do not read blurry values.
6. Keep raw transcripts and media local. Only short quotes and derived metadata/reports belong in Git.
