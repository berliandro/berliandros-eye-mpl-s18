# Transcript segment ledgers

One JSONL file per source: `<source_id>.jsonl`.

Each record describes an exact raw line range and its aligned caption cue:

```json
{"segment_id":"seg-src-s18-w01d01-L001016-L001020","source_id":"src-s18-w01d01","raw_line_start":1016,"raw_line_end":1020,"cue_start":2538.319,"cue_end":2550.52,"segment_type":"gameplay","include":true,"exclude_reason":null,"text":"..."}
```

Rules:

- Raw transcripts stay unchanged.
- `text` must be the exact raw text for the line range.
- Timestamps come only from `analysis/cache/timed/<source_id>.json`.
- If alignment is unavailable, set `cue_start`, `cue_end`, and `timestamp_link` to `null`.
- Keep interviews tagged; do not delete them.
- Ads, intros, outros, and pure noise may be excluded with a reason.

Validate observations against these files with:

```text
python tools/validate_transcript_ledger.py --ledger <ledger> --segments <segments>
```
