# OpenCode Goal: Start Semantic Coaching Intelligence for Berliandro's Eye

## Mission

Build the first working version of a **traceable, transcript-powered MLBB coaching intelligence pipeline** in the existing `berliandros-eye-mpl-s18` repository. Import the user's local nine-week transcript corpus, inspect how source references and timestamps are represented, create a reusable YouTube video-frame capture tool, and run a small end-to-end pilot that produces auditable coaching observations.

This is an implementation goal, not a proposal-writing task. Complete the feasible work in this run: inspect and inventory sources, build the smallest reliable pipeline, visually inspect relevant footage when useful, process a carefully selected pilot of 2–3 series/games, audit at least one candidate insight, test the process, and report what is and is not established. Do **not** stop after writing an architecture plan. Do **not** pretend full-season semantic analysis is complete after the pilot.

## Local source paths

Transcript corpus to **copy** into this project:

`D:\! Coding\~ shit projects\get-youtube-transcript\mpl-s18-raw-transcripts`

Reference/helper script for retrieving or understanding transcript references when needed:

`D:\! Coding\~ shit projects\get-youtube-transcript\get_transcript.py`

The intended destination inside the current repository is:

`analysis\sources\raw-transcripts\`

Resolve the repository root from the current working directory. The Windows paths above are local user paths, not URLs. Handle spaces and the `!` character safely in shell commands.

## Non-negotiable data-safety rules

1. **Copy, never move or delete.** Do not modify, rename, normalize in place, or delete anything in the original transcript directory. Do not modify `get_transcript.py`; inspect/use it read-only.
2. If the destination already exists, compare paths, sizes, and hashes first. Skip identical files. Never silently overwrite a conflicting file. Report conflicts and choose a non-destructive resolution.
3. Preserve the raw transcripts exactly as copied. Normalization, parsing, segmentation, and metadata enrichment must create derived files or records elsewhere.
4. The raw transcripts are local source material and may contain copyrighted broadcast transcription. Copy them locally into the project as requested, but **do not stage, commit, or push the raw corpus by default**. Add a precise `.gitignore` rule for the raw corpus if needed. Do not hide unrelated files with broad ignore patterns. Generated reports must use only short quotations necessary to support an insight. Before commit/push, inspect the staged diff to ensure raw transcripts, private cookies, API keys, video downloads, frame caches, and other large/local-only source material are excluded.
5. Treat `data/mpl_id_s18.db`, its CSV exports, season metadata, and the existing dashboard as **read-only inputs** for this project. Do not rebuild, alter, or migrate them. Put semantic evidence and derived reports in a separate `analysis/` area and, if needed, a separate evidence database.
6. Do not expose API keys, browser cookies, local tokens, or environment secrets in logs, reports, fixtures, screenshots, or commits. Do not enable a paid provider or incur API costs without existing configuration/authorization. Prefer the project's already-configured provider/workflow; clearly report any unavailable capability.
7. Do not commit/push until tests pass and the diff has been reviewed. Preserve unrelated working-tree changes, especially the existing untracked `mpl-s18-analytics-data-consistency-goal.md` if it is present.

## Phase 0 — Inspect repository and import the source corpus

Before changing anything:

- Inspect the current branch, HEAD, `git status`, ignored/untracked files, and existing project conventions. Do not reset, clean, stash, or overwrite unrelated work.
- Confirm the source directory exists and inspect the helper script's CLI, output format, timestamp handling, video-ID/URL generation, and any existing reference logic. Do not assume arguments or run a bulk network operation blindly.
- Inventory existing transcript files: path, file type, byte size, encoding, line count, timestamp format/coverage, likely week, video ID/URL/title if present, match/game mapping where available, and SHA-256 checksum. Distinguish observed metadata from inferred mapping.
- Copy the contents of the source corpus into `analysis/sources/raw-transcripts/`, retaining directory structure and file bytes. Verify file count, total bytes, and hashes after copying. Produce a concise copy-verification result.
- Add a narrow ignore rule for the raw corpus and local frame/clip caches if needed, while keeping schemas, scripts, manifests, tests, and short curated reports trackable.
- Create `analysis/sources/source-manifest.json` from metadata that actually exists. Include a stable source ID; relative path; checksum; size; transcript timestamp coverage; known YouTube video ID, title, URL, and source provenance; week/series/game mapping and mapping confidence where supportable. Missing information stays `null`/`unknown`; never guess a video link or timestamp.
- Create `analysis/reports/corpus-inventory.md` with corpus counts, weeks/videos covered where confirmed, timestamp/link coverage, duplicate or suspicious files, parsing risks, and gaps.

Use `get_transcript.py` as a reference helper whenever useful to confirm how to get a timestamped YouTube link or source metadata for a known video. Prefer existing metadata to a second download. If the script needs to contact YouTube, invoke it only for the minimum sources needed and use its documented interface. Do not scrape all videos a second time merely to rebuild metadata already present.

## Phase 1 — Inspect the match database and define evidence provenance

Read the actual SQLite schema and relevant CSV/data dictionary in read-only mode. Do not assume the database contains a field just because it would be helpful.

Create `analysis/reports/database-inventory.md` and `analysis/evidence/database-snapshot-manifest.json` containing:

- Database path, SHA-256 fingerprint, schema/version if available, and inspected time.
- Tables and relationships relevant to matches, games, teams, players, picks, bans, objectives, items, maps, game stats, and source metadata, where present.
- Actual coverage and missingness for candidate fields.
- Explicit distinctions between source-reported facts, deterministic calculations, app heuristics, and unavailable values.
- How a transcript/source video is linked to a series/game, and the confidence/rationale for each mapping. Do not use fuzzy names alone as a definitive join.

Create a **separate** evidence store under `analysis/evidence/` (prefer a dedicated SQLite database if the repository's tools make it straightforward; otherwise use validated JSONL as the canonical store). Do not modify the app's canonical match database.

At minimum, represent:

- `sources`: source ID, original relative file path, checksum, source URL/video ID when known, title/week/series/game mapping, mapping confidence, metadata provenance.
- `transcript_segments`: stable ID, source ID, raw file location/line range or offset, exact transcript text, speaker if explicitly known, start/end timestamp when present and verified, and timestamp provenance.
- `observations`: stable observation ID, category, concise claim, evidence type, linked source/segment/database rows, sample scope, status, uncertainty, and extraction/schema/prompt version.
- `insights`: stable insight ID/version, claim, supporting and contradicting evidence IDs, alternative explanations, scope, confidence rationale, and practical coaching question or follow-up.
- `audit_results`: audit ID, insight version, sources actually inspected, quotation/URL/timestamp validation results, counterexamples searched, verdict, limitations, and timestamp.

Use stable deterministic IDs where feasible so rerunning a batch does not duplicate records. Validate outputs against a versioned schema. Exact quoted text must be retrievable from the copied raw transcript, with only explicitly documented normalization used for matching. Preserve original text and offsets/line numbers.

Evidence type and verification status are separate concepts. Suggested evidence types: transcript statement, commentator interpretation, database-record evidence, derived-stat evidence, gameplay observation, analytical inference. Suggested verification states: unverified, transcript-verified, gameplay-verified, cross-checked, partially supported, contradicted, inconclusive.

A transcript quotation establishes what the speaker said, not that the speaker's interpretation is correct. Do not label an insight `gameplay-verified` unless footage was actually reviewed and the visual observation was recorded. Do not call two items independent corroboration if they derive from the same underlying source/feed.

## Phase 2 — Build a reusable YouTube video-frame capture tool

Create a tested, documented tool, preferably `tools/video_frames.py` unless existing repository conventions indicate a better location. Its purpose is to extract a small number of **full-frame screenshots at specified game timestamps** to help inspect gameplay context behind a transcript event. It must be reusable by future audits, not a one-off script.

### Required interface and behavior

- Accept a registered `source_id` from the source manifest or an explicit video URL/ID, plus one or more timestamps. Resolve a known video URL from the manifest when possible.
- Support extracting a single timestamp and multiple timestamps, plus a configurable before/after window for event review. Provide an optional contact sheet for reviewing a sequence together.
- Suggested CLI shape (adjust to fit existing conventions):

  ```powershell
  python tools/video_frames.py --source-id <source-id> --timestamps 00:12:34,00:12:38,00:12:44 --around-seconds 4 --contact-sheet
  python tools/video_frames.py --url "https://www.youtube.com/watch?v=<video-id>" --timestamp 00:12:34
  ```

- Store screenshots and temporary clips under an ignored local cache/output directory, e.g. `analysis/cache/video-frames/`. Do not put binary screenshots or full videos into the Git repository by default.
- For every frame, write sidecar metadata containing source/video ID, canonical YouTube URL and timestamp link, requested timestamp, actual extraction time/frame metadata when available, extraction method, output path, tool versions, and errors/warnings. A timestamp in a file name alone is not sufficient provenance.
- Create timestamped links in the form supported by the source format (for example, a YouTube `t=` link), but only when the video identity and time base are known. Do not invent timestamps or assume every transcript's timestamp is video-relative without verification.
- Check locally available `yt-dlp`, FFmpeg/ffprobe, Python packages, and runtime capabilities before choosing an implementation. Prefer the current official `yt-dlp` workflow and FFmpeg frame extraction over adding unnecessary dependencies. Modern YouTube extraction may require yt-dlp's supported JavaScript runtime/EJS components; diagnose missing prerequisites clearly rather than silently claiming the video is unavailable.
- Prefer targeted timestamp/short-section retrieval instead of downloading entire livestreams. Full video download must not be the default. Reuse an already-cached permitted local video file if available. Temporary media must have size/time limits and reliable cleanup. Do not bypass private-video, paywall, or access restrictions. Browser cookies may only be used through an explicit opt-in setting, never by default; do not log or copy cookies.
- If a source is unavailable, age-restricted, blocked, removed, or cannot be sought accurately, report the exact limitation and preserve the transcript-only evidence state. Do not create a dummy image or claim visual verification.
- Keep the original extracted full frame untouched. A resized/contact-sheet derivative is fine, but its relationship to source frame(s) must be recorded. Avoid cropping away the minimap or HUD in the primary capture. Optional crops may be added as separate clearly-labelled derivatives.
- Tool errors must return nonzero status for failed requested frames and report which frames succeeded. One inaccessible timestamp should not silently turn into a successful complete capture.

Use the installed official documentation as the implementation reference and confirm behavior against the locally installed tool version: [yt-dlp documentation](https://github.com/yt-dlp/yt-dlp/blob/master/README.md) and [FFmpeg documentation](https://www.ffmpeg.org/ffmpeg.html). Do not assume an option behaves exactly the same across installed versions; check `--help`/version and test it.

### How to use screenshots for MLBB analysis

Use frames when a transcript passage raises a gameplay question that visual context can help answer, such as:

- **Player positioning and spacing:** where heroes are relative to one another, frontline/backline separation, flank angles, choke points, retreat routes, and whether a player is isolated in the reviewed frames.
- **Rotation and numbers advantage:** visible hero movements, grouping, lane assignments, map-side commitments, gank setup, invasion entry/exit, or a fight starting before teammates arrive.
- **Objective context:** Lord/Turtle spawn or contest setup, visible objective health/state when shown, which heroes are nearby, who has lane priority, whether a team trades an objective for a tower or another map resource, and the post-objective conversion.
- **Turrets and waves:** turret health/destruction where visible, siege setup, minion-wave position, side-lane pressure, high-ground entry/defense, and whether a team converts a win into structures.
- **Economy and scaling:** scoreboard gold difference, kills, levels, items, equipment spikes, and game time, but only read values that are actually visible and legible. Record values as uncertain/unreadable when not clear; do not infer exact gold or items from a blurry frame.
- **Teamfight execution:** initiation, target selection, follow-up/peel, counter-engage, disengage, cooldown/ultimate indicators if visible, death timers, buyback/respawn context if the game UI exposes them, and the sequence/outcome across multiple frames.
- **Draft and role evidence:** draft/ban screens, role or lane assignments where shown, hero composition, or visible item/skill choices.
- **Outcome and turning-point review:** compare a before/during/after sequence to see what materially changed, rather than assuming a single screenshot proves a whole fight.

The screenshot tool must help gather context, not invent hidden information. A few still frames cannot prove communication intent, information available outside the visible UI, mechanical reaction time, enemy vision, or why a player chose an action. Use a short frame sequence and, when the claim depends on timing, inspect a short clip if feasible. Record what is directly visible separately from interpretation. Never infer hidden vision or intention just because a hero is absent from the visible minimap.

### Test the video tool

- Add deterministic tests for timestamp parsing, URL/video-ID handling, `t=` link creation, cache path safety, filename collisions, metadata sidecars, invalid timestamps, and failed extraction handling.
- Where FFmpeg is available, create a tiny local synthetic video fixture and verify that requested frames can be extracted and metadata is written. Do not use a real broadcast download as the only unit test.
- Add a small live/integration smoke test only if network access and the chosen video are available. Mark that test separately from deterministic tests.
- Manually run the tool against at least one real transcript-linked video timestamp during the pilot, if access permits, then visually inspect the screenshot(s) with the available multimodal capability. If the agent/runtime cannot inspect images, report that limitation instead of claiming gameplay verification.

## Phase 3 — Implement the first transcript-to-evidence pipeline

Build a resumable local pipeline that is small but end-to-end:

1. Parse or segment transcript files while preserving line/offset references and any original timestamp strings. Do not discard uncued text or silently reinterpret timestamps.
2. Link segments to sources, series, and games only when metadata provides reliable evidence. Store unknown/ambiguous mappings explicitly.
3. Extract a limited initial taxonomy: objectives and map state, draft/pick-ban interpretation, teamfight/turning-point events, micro/meso/macro tactical observations, and explicit commentator interpretations. Add categories only where useful.
4. Require each transcript-derived observation to point to the exact source segment and quote. Validate the quote against the raw file. If a model paraphrases or quotes text that does not appear, reject/quarantine that record.
5. Attach database evidence by stable IDs and reproducible query/calculation when useful. Include the database fingerprint, fields, filters, sample size, and whether values are source-reported, derived, heuristic, or inferred. If the database lacks a useful field, say so.
6. Use visual review only when it can materially verify or contextualize a claim. Use the video-frame tool at relevant moments; capture multiple frames where sequence matters. Save only small local screenshot artifacts and sidecar provenance. Do not use screenshot presence as proof unless the frames were actually visually reviewed.
7. Keep every processing step resumable and idempotent, log validation failures and source gaps, and make model/provider/schema/prompt versions explicit. Do not spend tokens reprocessing successful batches without cause.
8. Search for disconfirming passages or counterexample games for each high-value pattern. Do not search only for confirming support.
9. Generate concise Markdown reports from validated records, with inline stable evidence IDs and a references section linking timestamped video, exact transcript passage, and/or database query result. Reports must distinguish direct quotations, caster interpretations, structured statistics, visual observations, and AI hypotheses.

Use the current OpenCode model/capabilities for a small pilot when available, or an already-configured project provider. Do not add a new paid dependency or invent an LLM response to make the pipeline look complete. If model access is unavailable, complete deterministic segmentation, source linking, frame tooling, schemas, validators, and tests; generate only the evidence-backed outputs that can honestly be produced, then state what blocks semantic synthesis.

## Phase 4 — Pilot on 2–3 representative series/games and audit the results

Select **2–3 actual series/games** after inventory, prioritizing clear transcript/source linkage and varied useful content (e.g. a draft discussion, an objective sequence, and a teamfight or turning point). Explain why the pilot was selected. Do not choose a source purely because its transcript is easy if the source cannot be mapped to real footage/data.

For the pilot:

- Build timestamped game timelines from exact segments.
- Extract candidate observations in the supported taxonomy.
- Query relevant structured match data where it genuinely supports or challenges a claim.
- Use the video-frame tool on at least one material gameplay question if a linked video is accessible. Capture before/during/after context where required and record whether the frame sequence was actually visually inspected.
- Generate at least one concise pilot report, plus team/draft/objective notes only where evidence supports them.
- Create several high-quality, evidence-backed insights if the sources support them; **do not force a target count or fabricate insight density**. Each material insight needs source evidence, verification state, alternatives/limitations, and at least one counterexample search where the claim is a pattern.
- Audit at least one insight skeptically, choosing a potentially weak or ambiguous claim if possible. The audit must retrieve the original transcript context, validate quote/timestamp/link, check relevant structured data, search for counterexamples, and review footage when relevant. The verdict must be `supported`, `partially supported`, `contradicted`, or `inconclusive`.
- If video access fails, continue with transcript/database analysis but retain `transcript-verified` or a lower status; report the precise visual limitation. Do not claim gameplay verification.

## Deliverables

Create only useful files; no large directory of empty reports. At minimum, aim for:

```text
analysis/
  README.md
  index.md
  sources/
    source-manifest.json
    raw-transcripts/            # local copy; gitignored by default
  reports/
    corpus-inventory.md
    database-inventory.md
    pilot-quality-report.md
  evidence/
    evidence-schema.json
    database-snapshot-manifest.json
    ...                         # separate SQLite or validated JSONL store
    audit-log.jsonl             # or an equivalent append-only audit table
  matches/                      # only selected pilot reports
  games/                        # only selected pilot reports
  coaching/
    pilot-coaching-brief.md
  cache/
    video-frames/               # local ignored screenshots, clips, contact sheets
```

Plus the tested tool (e.g. `tools/video_frames.py`), pipeline scripts, fixtures, tests, and narrow documentation updates.

`analysis/index.md` and `analysis/README.md` must explain the status and coverage: raw corpus import verified or not, number of sources and timestamps linked, pilot scope, visual-review coverage, and known limitations. Do not describe the pilot as full-season coverage.

## Required quality gates

- Original transcript source hashes are unchanged; copied file hashes match the source.
- Every source-manifest path exists; raw source paths are relative and portable inside the repository.
- Every quoted segment resolves to an exact source span under documented normalization.
- Missing/ambiguous video timestamps, video IDs, and game mappings remain explicit.
- Video screenshot metadata records the source URL, requested timestamp, output, method, and actual success/failure. The tool never labels a frame `verified` just because the download completed.
- Every database claim identifies the snapshot, row/table/fields or reproducible query/formula, filters, and scope.
- No field absent from the database is fabricated; heuristics stay labelled as heuristics.
- Insight types and verification states are not conflated. Transcript verification alone never upgrades a gameplay claim to gameplay-verified.
- Material claims cite stable evidence IDs. Counterevidence, alternatives, sample size, and coverage limitations are included where relevant.
- Rerunning the same batch is idempotent and does not duplicate evidence or overwrite original sources.
- Failed extraction or audits are logged and resumable.
- Tests cover malformed model output, non-existent source IDs, quote mismatch, invalid timestamp, ambiguous transcript-to-game mapping, source/database disagreement, and rejected unsupported claims.
- Existing app tests continue to pass; the canonical SQLite database, CSVs, season metadata, and generated dashboard have no unintended modifications.
- `git diff --check` or the repository's equivalent passes. Inspect the final staged/untracked diff before any commit.

## Out of scope for this goal

- Processing every transcript across all nine weeks to completion. The first deliverable is the infrastructure plus a validated 2–3-series pilot; all-week batching is a subsequent goal after pilot quality is demonstrated.
- Integrating semantic insight UI into the existing single-file dashboard.
- Rebuilding or modifying the existing match ETL/database.
- Unrelated visual redesign, broad refactors, speculative claims about player intent/communication, or an always-running agent service.

## Final report requirements

At the end, report concrete results rather than aspirations:

1. Original/copy path, file count, byte count, checksum verification, and any copy conflicts.
2. Corpus inventory: confirmed sources/weeks/video IDs/URL/timestamp coverage and important gaps.
3. Database snapshot fingerprint and what its real schema/coverage supports.
4. The frame-capture tool's interface, dependencies/versions, real video smoke-test result, screenshots/sidecars produced, and any unavailable capabilities.
5. Pilot source IDs and series/games selected, exact processing coverage, generated reports, and a few representative insight IDs.
6. One audit's verdict with evidence checked, counterexamples searched, and whether footage was actually visually inspected.
7. Test commands and actual pass/fail counts; separate deterministic tests from live network smoke tests.
8. Remaining limitations and what is required before scaling across all nine weeks.
9. Files changed, final working-tree status, commit SHA and push status if safely completed. Explicitly confirm that the raw corpus and local media/cookies were not committed or pushed.

Do not report full semantic analysis, full-season coverage, or gameplay verification unless the corresponding work actually happened and passed its evidence checks.
