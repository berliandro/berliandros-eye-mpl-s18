# Video source resolution

The canonical completed regular-season schedule provides one VOD candidate for each of the 27 transcript broadcast dates and associates all 72 completed series with those dates. Candidate IDs and series mappings are stored in [`analysis/sources/source-manifest.json`](../sources/source-manifest.json).

**A schedule URL is not a verified source identity by itself.** The local resolver confirms that the YouTube title identifies the expected MPL ID S18 week/day, that the channel is MPL Indonesia, and then aligns the official timed captions against the immutable raw transcript lines before enabling timestamp links.

## Current local result

- **Metadata-verified official videos: 27/27.**
- **Fully caption-aligned sources: 26/27.** Every raw line has a verified caption timestamp.
- **Partially aligned: 1/27** — `src-s18-w09d02` (`b9SktblDNuc`). The raw file has 14,259 lines; the current YouTube caption track has 14,551 snippets. The monotonic token alignment matched 13,759 lines exactly and 463 lines by token span, leaving 37 short ad/transition/interjection lines without a trustworthy timestamp. The source is recorded as `caption_alignment_partial` and is **not** used for timestamp citations.
- **Hard failures: 0/27.**

The local run succeeded where the GitHub-hosted runner was blocked by YouTube's “Sign in to confirm you’re not a bot” response. The local machine used the installed `yt-dlp` with an explicit Deno JavaScript runtime for metadata and the official `youtube-transcript-api` track for timing. No cookies, tokens, browser databases or credentials are written to the repository or reports.

## Status semantics

| Status | Meaning |
|---|---|
| `schedule_candidate_pending_verification` | A schedule-derived candidate exists, but official metadata or alignment has not been confirmed for the current run. |
| `metadata_verified` | Official channel, season and exact week/day title match. No timestamp citation is enabled yet. |
| `caption_alignment_verified` | Every raw transcript line is mapped monotonically to a timed caption interval. Timestamp links are enabled. |
| `caption_alignment_partial` | Some raw lines have no trustworthy timestamp. The source is explicitly not citation-ready. |
| `metadata_mismatch` | The candidate's observed title/channel does not match the expected week/day. |
| `candidate_resolution_failed` | No unambiguous schedule candidate could be derived. |

A previous verification is reused only when the current source SHA-256, candidate video ID and cached alignment all match. A fresh metadata failure does not erase valid prior evidence, but the failure is recorded in `last_resolution_status` / `last_resolution_error` and in `analysis/cache/video-resolution-report.json`.

## Reproduce locally

```powershell
python tools/resolve_and_align_sources.py
```

The run is resumable. It writes a full report to the Git-ignored `analysis/cache/video-resolution-report.json`, updates the manifest and regenerates the corpus inventory. Use `--no-align` for a metadata-only pass, `--source-id` to retry one source, or `--refresh-metadata` to re-check already verified sources.

Broadcast-date mapping does not establish the exact start time of each series or game within a multi-hour VOD. Series/game offsets remain a separate evidence step.
