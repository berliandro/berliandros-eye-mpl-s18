# Corpus inventory

Generated: 2026-10-25T13:42:13+00:00

## Copy verification

- Source files: **27**
- Source bytes: **9,682,086**
- Copied / identical-skipped / conflicts: **27 / 0 / 0**
- SHA-256 verification after copy: **27/27**
- All verified: **True**
- Raw corpus location: `analysis/sources/raw-transcripts` (Git-ignored, local-only)

The source directory was copied byte-for-byte; no source file was edited, moved or deleted.

## Coverage

- Files: **27**, weeks **1–9**, days per week: W1: 3, W2: 3, W3: 3, W4: 3, W5: 3, W6: 3, W7: 3, W8: 3, W9: 3
- Encoding: UTF-8 without BOM; CRLF line endings in the raw files.
- Native timestamp strings in the raw files: **0**. The files are caption text only; filenames carry week/day but no video ID.
- Verified YouTube video IDs/URLs: **2/27** (pilot only).
- Timed caption alignments: **2/2** pilot videos, one-to-one with raw caption lines.
- Byte-identical duplicate files: **0**.

## Source table

| Source ID | Week/day | Bytes | Lines | Native timestamps | Video ID | Timed alignment |
|---|---:|---:|---:|---|---|---|
| `src-s18-w01d01` | W1D1 | 279,422 | 9104 | none | 40fehk2f4_E | yes |
| `src-s18-w01d02` | W1D2 | 428,822 | 14476 | none | unknown | no |
| `src-s18-w01d03` | W1D3 | 355,862 | 12402 | none | unknown | no |
| `src-s18-w02d01` | W2D1 | 261,503 | 8472 | none | unknown | no |
| `src-s18-w02d02` | W2D2 | 417,886 | 13021 | none | unknown | no |
| `src-s18-w02d03` | W2D3 | 378,939 | 12957 | none | unknown | no |
| `src-s18-w03d01` | W3D1 | 235,383 | 7945 | none | unknown | no |
| `src-s18-w03d02` | W3D2 | 435,336 | 14817 | none | unknown | no |
| `src-s18-w03d03` | W3D3 | 366,365 | 12016 | none | unknown | no |
| `src-s18-w04d01` | W4D1 | 245,518 | 7549 | none | unknown | no |
| `src-s18-w04d02` | W4D2 | 429,999 | 14283 | none | unknown | no |
| `src-s18-w04d03` | W4D3 | 331,164 | 11400 | none | unknown | no |
| `src-s18-w05d01` | W5D1 | 164,689 | 5402 | none | unknown | no |
| `src-s18-w05d02` | W5D2 | 363,316 | 12265 | none | unknown | no |
| `src-s18-w05d03` | W5D3 | 258,103 | 8133 | none | unknown | no |
| `src-s18-w06d01` | W6D1 | 425,004 | 14220 | none | unknown | no |
| `src-s18-w06d02` | W6D2 | 411,068 | 13138 | none | unknown | no |
| `src-s18-w06d03` | W6D3 | 419,344 | 14245 | none | unknown | no |
| `src-s18-w07d01` | W7D1 | 326,946 | 10453 | none | unknown | no |
| `src-s18-w07d02` | W7D2 | 485,334 | 16038 | none | unknown | no |
| `src-s18-w07d03` | W7D3 | 406,167 | 13840 | none | unknown | no |
| `src-s18-w08d01` | W8D1 | 404,055 | 13423 | none | unknown | no |
| `src-s18-w08d02` | W8D2 | 392,625 | 12607 | none | unknown | no |
| `src-s18-w08d03` | W8D3 | 393,493 | 12650 | none | unknown | no |
| `src-s18-w09d01` | W9D1 | 274,162 | 8817 | none | unknown | no |
| `src-s18-w09d02` | W9D2 | 433,140 | 14259 | none | unknown | no |
| `src-s18-w09d03` | W9D3 | 358,441 | 12273 | none | hY0Upem95uo | yes |

## Timestamp/link coverage

The pilot uses an explicit derived method: the raw caption lines are aligned one-to-one with the official YouTube auto-caption snippets, then timestamps and `t=` links are generated only for verified video IDs.

- `src-s18-w01d01` / `40fehk2f4_E`: 9,104 lines, 9,103 exact + 1 normalized caption matches.
- `src-s18-w09d03` / `hY0Upem95uo`: 12,273 lines, 12,273 exact + 0 normalized caption matches.

This alignment is not native transcript metadata and does not make timestamps frame-accurate; it is a reproducible cue-time mapping.

## Parsing risks and gaps

- Captions are Indonesian auto-generated ASR: names, hero names and punctuation can be wrong; there are no speaker labels.
- Some lines are music/noise tags (`[musik]`, `[berteriak]`, `[tertawa]`), not evidence of gameplay.
- Line breaks split sentences; quotes must preserve the source line span.
- 25/27 sources still have no verified video ID and therefore no timestamp links or visual verification.
- Week/day mapping comes from the filename. Series mapping is only claimed for the pilot sources in the manifest, with rationale recorded.
- The raw corpus is local-only. Committed reports contain only short pilot quotations; validators that need raw text are run in this local workspace and require the ignored corpus copy.

## Duplicate/suspicious files

No byte-identical duplicates were detected. The corpus is one file per broadcast day; this is consistent with the source naming, but it is not proof that every file is a complete broadcast.
