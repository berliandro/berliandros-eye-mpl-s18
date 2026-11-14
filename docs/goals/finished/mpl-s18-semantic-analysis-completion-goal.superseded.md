> **Status: SUPERSEDED — NOT COMPLETED (2026-11-07).**
>
> The transcript-analysis scope is replaced by
> `docs/goals/active/revised_transcript_workflow.md` and
> `docs/goals/active/mpl-s18-transcript-knowledge-goal.md`.
> Visual proof remains in `docs/goals/active/mpl-s18-visual-proof-deepseek-handoff.md`.
> Do not execute Phases 3–5 from this file as the active plan; keep it as a
> historical baseline only.

# Goal: Complete Berliandro's Eye MPL ID S18 Semantic Coaching Intelligence

## Mission

Turn the existing semantic-analysis pilot in `berliandro/berliandros-eye-mpl-s18` into a reliable, auditable, full-season coaching-intelligence system for MPL Indonesia Season 18.

The finished system must do more than create a Markdown file for every series. It must connect the immutable broadcast transcript corpus, verified YouTube VODs and timestamps, the canonical MPL statistics database, and reviewed gameplay footage to produce traceable game-level observations and defensible cross-game insights. It must be able to explain what happened, why a tactical interpretation is plausible, what contradicts it, and how confident the evidence allows us to be.

Work autonomously through the phases below. Inspect the actual local repository and current worktree first; GitHub state may have changed since this goal was written. Do not stop after an audit or plan. Implement, test, generate, validate, document, and continue until the acceptance criteria are met or a genuine external blocker prevents further progress. Persist progress in the goal/work log so interrupted work can resume safely.

---

## 1. Project context and intended end state

This project is an analytical extension of Berliandro's Eye, the existing MPL ID S18 statistics application. The established SQLite database and its CSV exports are the canonical structured match-data foundation. Semantic analysis should remain a separate research/evidence layer and must not destabilize the existing app or mutate the canonical database as an incidental side effect.

The intended end-state experience is:

1. A coach opens a team, player, hero, draft, match, or game report.
2. Every material analytical claim links to evidence: an exact transcript source span with a verified YouTube timestamp, a reproducible database query/result, a DeepSeek-reviewed screenshot or ordered screenshot sequence, or a clearly labelled combination.
3. The coach can ask the system to audit an insight. The audit retrieves the original source context, verifies citations, checks the relevant database rows, looks for confirming and contradicting examples elsewhere in the season, and inspects footage when useful.
4. The result is classified as **supported**, **partially supported**, **contradicted**, or **inconclusive**, with the strongest counterargument and limitations made explicit.
5. Reports distinguish direct facts from commentator statements, observed gameplay, computed statistics, heuristics, and AI hypotheses. The system never presents commentary as proof of an in-game event or correlation as causation.

The target coverage is the completed regular season: **72 series and 174 games**, across **27 broadcast days / 9 weeks**, with reports and evidence coverage reflecting the real depth of analysis. The goal is full-season intelligence where evidence supports it, not fabricated certainty or superficial 100% report coverage.

---

## 2. Baseline: what already exists (verify before changing)

The previous repository audit observed the following state on 2026-11-02:

- `main` was at `2b179abcdf65f16a2f2760fbcd726e633ad1dc9b` (`Merge pull request #2 ... Add semantic analysis expansion, player dossiers, and goal workflow`). Both earlier semantic PRs were merged.
- The GitHub Actions regression run for that exact `main` commit succeeded: run `41420053693`.
- The repository contained the existing dashboard, canonical SQLite DB and CSVs, 72 match report files, and 66 player dossiers.
- The transcript corpus contained 27 files / 9,682,086 bytes, copied byte-for-byte and SHA-256 verified 27/27. Raw files are intended to remain unmodified and Git-ignored under `analysis/sources/raw-transcripts/`.
- All 27 schedule-derived VOD candidates had official MPL Indonesia channel / S18 week-day metadata verification in the local resolution report. 26/27 transcript sources were fully aligned to official timed captions; `src-s18-w09d02` was partial and excluded from timestamp citations because 37 short lines did not receive trustworthy timestamps.
- Raw transcripts have no native timestamp strings. Timestamp citations are derived from monotonic alignment to the YouTube caption track. This is a cue-time mapping, not frame-accurate transcript metadata.
- The evidence framework already had a schema, `pilot-ledger.jsonl`, query catalogue, database snapshot manifest, audit log, timed-alignment summary, game-offset data, and visual-review log.
- The ledger had 40 records: 8 segments, 24 observations, 6 insights, and 2 audits. It contained three series-level pilot insights and three player-level insights.
- The screenshot implementation existed in `tools/video_frames.py`, using Playwright/Chromium for YouTube and FFmpeg for local video. It records sidecars, capture timestamps, hashes and review status. The pilot visual log had 8 attempts: 5 gameplay frames used, 1 post-game context frame used, 1 promo rejected, and 1 failed capture.
- The three substantive series pilots were 1036 EVOS vs RRQ, 1037 NAVI vs AE, and 1107 ONIC vs TLID. The current coaching brief is explicitly only a three-series pilot.
- The winner-orientation migration had repaired 21/72 `matches.winner` rows and checked the database integrity. Do not rerun or reverse it without first inspecting the current database and migration provenance.
- `tools/verify.py` was documented as the standard app regression suite (24 suites at the time of the audit). `tools/verify_analysis.py` was a separate local semantic suite requiring the ignored corpus/cache; it was not part of GitHub CI.

Treat this section as a historical checkpoint, not unquestionable live truth. First inspect `git status`, current branch and HEAD, `AGENTS.md`, all goal-workflow instructions, current reports, database fingerprint, source manifest, ignored local folders, and latest CI. Recompute all counts from actual current files. Never overwrite user work or trust stale generated reports over underlying records.

### Important existing paths

- `analysis/README.md`, `analysis/index.md`
- `analysis/sources/source-manifest.json`
- `analysis/sources/copy-verification.json`
- `analysis/sources/raw-transcripts/` (local-only, Git-ignored)
- `analysis/cache/` (local-only, Git-ignored; timed captions and video frames)
- `analysis/evidence/evidence-schema.json`
- `analysis/evidence/pilot-ledger.jsonl`
- `analysis/evidence/query-catalog.json`
- `analysis/evidence/database-snapshot-manifest.json`
- `analysis/evidence/timed-alignment.json`
- `analysis/evidence/game-offsets.json`
- `analysis/evidence/visual-review.json`
- `analysis/evidence/audit-log.jsonl`
- `analysis/pilot/selection.json`
- `analysis/matches/` (72 series Markdown files)
- `analysis/players/` (66 player Markdown files)
- `analysis/reports/`
- `analysis/coaching/pilot-coaching-brief.md`
- `tools/import_transcripts.py`
- `tools/link_video_source.py`
- `tools/resolve_and_align_sources.py`
- `tools/transcript_evidence.py`
- `tools/video_frames.py`
- `tools/build_game_offsets.py`
- `tools/refine_game_offsets.py`
- `tools/validate_game_offsets.py`
- `tools/analysis_inventory.py`
- `tools/check_analysis.py`
- `tools/verify_analysis.py`
- `tools/verify.py`

---

## 3. Non-negotiable evidence and safety rules

1. **Immutable source material.** Never edit, normalize in place, rename, move, or delete original transcript files. Store derived normalization, caption alignments, extracted observations, screenshots, contact sheets, and other media in separate generated/local cache locations.
2. **No public raw-corpus upload.** Keep full raw transcripts, full videos, screenshots, browser cookies, authentication tokens, and browser databases out of Git. Preserve the existing ignore rules. Only publish short necessary quotations, metadata, hashes, and derived reports after reviewing copyright/privacy implications.
3. **No invented evidence.** Never fabricate quotations, timestamps, video IDs, match/game IDs, player identities, objective counts, game events, score values, screenshots, visual observations, or database rows. Missing data remains missing and is surfaced as a gap.
4. **Timestamp discipline.** A raw transcript line receives a timestamp only when a reproducible alignment maps it to a timed caption from the verified video. Do not use fuzzy or partial matches as timestamp-ready citations. Preserve alignment algorithm/version, source hash, candidate video ID, cue start/end, confidence, and any normalization. Never describe cue-time alignment as frame-accurate.
5. **Boundary discipline.** A broadcast-day-to-series schedule association is not proof of the exact in-video series boundary. A series boundary is not a game boundary. Heuristic offsets are never citation-ready. A game-specific claim requires a validated series and game mapping, with uncertainty explicitly recorded.
6. **Source lineage.** Record whether a value is source-reported, derived from source-reported rows, heuristic, DeepSeek screenshot-reviewed, or AI-inferred. Do not call two records independent corroboration if they derive from the same underlying data feed.
7. **Visual evidence discipline.** A captured frame is not a reviewed frame. A reviewed still image can support only what is visibly present at that instant. It cannot prove a sequence, causality, intention, communication, reaction speed, a complete fight, or objective capture by itself. Use a timestamped, chronologically ordered screenshot sequence for temporal claims. Sparse stills do not establish continuity; keep the claim inconclusive when the sequence cannot prove it. Record rejected frames and failed captures; never silently omit them.
8. **Commentary is not gameplay fact.** Distinguish “the caster said X” from “X happened.” Indonesian auto-caption ASR may mistranscribe player/hero names and does not provide speaker labels. Record exact source spelling and any database-supported interpretation separately.
9. **No causal inflation.** Do not claim a draft, item, rotation, player, objective, or strategic identity caused a win based only on one match or an aggregate outcome. Use “consistent with”, “associated with”, or “hypothesis” until comparative evidence and alternative explanations justify stronger language.
10. **Counterexamples are mandatory.** For recurring tendencies, search the full available season evidence for contradictory examples, matched situations, losses with the same draft/core, wins without the supposed pattern, and patch/context differences.
11. **Database stays canonical and protected.** Treat `data/mpl_id_s18.db` and its CSVs as read-only analytical inputs. A necessary data repair must be a separately justified, backed-up, reversible migration with explicit validation, never an incidental analysis side effect.
12. **Auditable generation.** Store stable IDs, evidence schema version, extraction/model/prompt version, query/formula version, database snapshot ID/hash, source hashes, processing time, and job status. Make processing deterministic where possible, idempotent, resumable, and safe to rerun.
13. **No false completion.** Do not mark a goal, source, report, audit, or phase complete just because files exist. Completion is determined by explicit acceptance tests and evidence coverage.

---

## 3A. Vision capability constraint and DeepSeek visual-proof handoff

**The model executing the first stage of this goal does not have visual-inspection capability. The goal must continue; do not stop non-visual work because of this limitation.** Continue tasks that can be completed from repository code, text, JSON, transcript sources, timestamps, hashes, SQL/database records, deterministic tooling, tests, and report generation.

All work requiring pixel-level interpretation must be consolidated in this single project file:

- `docs/goals/active/mpl-s18-visual-proof-deepseek-handoff.md`

This is the sole dedicated visual-proof backlog and second-stage handoff. It contains the complete screenshot target scope, relevant sources/games/timestamps, capture instructions, DeepSeek review contract, uncertainty rules, evidence schema, unresolved claims, and visual acceptance criteria. Do not scatter separate visual-review TODO lists across other Markdown files; ordinary reports may link to this one canonical handoff/queue.

### Mandatory rules for the first-stage non-vision executor

1. Do not claim to have inspected image pixels. Reading a sidecar, OCR output, filename, annotation, hash, model response, or old review log is not visual inspection.
2. Do not newly set `review_status: reviewed`, `visually_reviewed`, or equivalent statuses. Do not approve/reject a visual claim from metadata or transcript text alone.
3. Preserve historical visual annotations and provenance. Historical reviewer labels are not DeepSeek reviews and must not be relabelled as such. The DeepSeek stage must independently review the underlying screenshots and append fresh records.
4. Continue building screenshot-capture tooling, boundary candidates, timestamp mappings, ordered frame sequences/contact sheets, validators, schemas, DeepSeek request scaffolding, and deterministic reports. A successful capture is `captured`, not `visually_verified`.
5. For every visual dependency encountered, add/update the corresponding target in `docs/goals/active/mpl-s18-visual-proof-deepseek-handoff.md`, including source/game/timestamp/image information and the exact unresolved visual question.
6. Keep visual-dependent claims pending, quarantined, or explicitly limited until a schema-valid DeepSeek vision review verifies the exact screenshot hash(es). Never use unreviewed images as proof of player position, objective state, score/UI values, game identity, rotations, teamfights, mechanics, intent, or causality.
7. DeepSeek is the sole visual reviewer in the second stage. **No human screenshot inspection, manual visual approval, human-review queue, or human escalation is permitted.** If automated retries and additional screenshots do not resolve a question, mark it inconclusive/rejected/quarantined and continue with other targets.
8. The visual proof method is screenshot-based. For temporal claims, use timestamped, chronologically ordered screenshot sequences with enough context; do not switch to a human watching a video or treating a sparse set of stills as continuous footage.
9. Do not commit raw videos, screenshots, contact sheets, browser profiles, cookies, credentials, or other local-only media.

### Main-goal execution policy

- Continue all non-visual phases and acceptance checks to the maximum supportable extent.
- Build and maintain the single actionable DeepSeek screenshot-proof handoff rather than repeatedly attempting pixel-level verification with a non-vision model.
- Keep visual-dependent acceptance criteria open until the DeepSeek stage has completed the required screenshot reviews and its ledger/manifest checks pass.
- Do not mark this goal finished or move it to `docs/goals/finished/` while required visual-proof items remain open or unresolved.
- Ensure the handoff covers historical pilot frames/contact sheets, uncertain and claim-critical series/game boundaries, all relevant game identity/boundary work, pilot temporal claims, full-season gameplay claims used in reports, scoreboard/draft/objective/player/team tactical claims, and visual/OCR quality checks.

Second-stage assignment command:

    /goal @docs/goals/active/mpl-s18-visual-proof-deepseek-handoff.md

See that file for the full inventory, DeepSeek-only review protocol, and definition of done.

---

## 4. Phase 0 — Re-entry, inventory and baseline verification

### Tasks

- Inspect current Git branch, HEAD, worktree, remotes and recent history. Preserve unrelated user changes. Establish a dedicated working branch if appropriate and follow repository `AGENTS.md` goal conventions.
- Inspect `docs/goals/active/` and existing goal files to avoid duplicating or overwriting an active task.
- Verify the raw transcript corpus exists locally. If not, locate it using the established path, without guessing. The previously used original source was:
  `D:\! Coding\~ shit projects\get-youtube-transcript\mpl-s18-raw-transcripts`
- The previous transcript helper was:
  `D:\! Coding\~ shit projects\get-youtube-transcript\get_transcript.py`
  Inspect it before use; use it for source references only where needed. Do not assume the paths still exist.
- Re-run corpus inventory, hashes and copy verification. Confirm 27 files / nine weeks / 3 days per week or report the actual current inventory.
- Inspect the SQLite schema and database snapshot read-only. Recompute table coverage, 72-series / 174-game coverage, missing map modes, per-game VOD coverage, both-side coverage, objective-data availability, and winner consistency. Record database provenance and all missing fields.
- Re-run source-resolution and caption-alignment checks safely. Reuse only cache entries tied to the current raw-source SHA-256 and candidate video ID. Retry failed/partial sources locally with available legitimate access; do not copy cookies or credentials into the repository.
- Recompute coverage statistics from the underlying manifest, offsets, ledger, visual review, match reports and player dossiers. Identify stale/conflicting documentation and record the exact source of truth for every count. Update the single visual-proof handoff with all items that require actual image/video inspection; do not count historical review labels as a new visual inspection.

### Deliverables

- Updated machine-readable inventory and concise gap report.
- A single reconciled coverage definition separating source metadata verification, caption alignment, series-boundary verification, game-boundary verification, transcript analysis, database-only reports, visual review, and audited insights.
- No mutation of the canonical database or raw transcripts.

### Acceptance

- Every source file is accounted for and checksum-verified, or listed as a specific unresolved blocker.
- All reported counts are computed from underlying records and agree across generated reports.
- Git worktree changes that predate this task are preserved.

---

## 5. Phase 1 — Repair and strengthen source, series and game mapping

This is a critical dependency. Do not scale semantic extraction on top of untrusted offsets.

### Existing weakness to investigate

The previous audit found `analysis/evidence/game-offsets.json` contained 72 schedule-associated series entries, but reported statuses were inconsistent with the coverage reports. At that checkpoint, individual entries included 26 `boundary_verified`, 24 `detected_pending_review`, and 22 `pending_validation`; all 27 top-level `validation_status` fields remained `pending`. There were 58 non-null starts and no end times. Other reports claimed different counts. The old `tools/validate_game_offsets.py` checked source membership, schedule order and presence of provenance, but did not independently prove timestamp correctness. `tools/refine_game_offsets.py` searched captions for both team names and could select weak or misleading matches. These implementations must be reviewed and replaced/hardened, not trusted as proof.

### Tasks

- Define versioned schemas for broadcast, series, game, and offset boundaries. Use stable IDs and explicit relations: one broadcast can contain several series; each series contains one or more games.
- Keep separate statuses for `schedule_associated`, `candidate_detected`, `boundary_verified`, `game_boundary_verified`, `visually_reviewed`, `quarantined`, and `unresolved` (or a similarly precise enum). Avoid a generic status that conflates different evidence levels.
- Identify candidate series boundaries using more than the first appearance of team-name strings. Use combinations of team names, ordered schedule, caster introductions, game loading/scoreboard transitions, timed captions, and DeepSeek-reviewed screenshot sequences. Preserve the candidate text and exact cue interval used.
- Never mark a boundary verified merely because the two team names appear somewhere near a timestamp or because the schedule order predicts it.
- Add a screenshot-review workflow that captures timestamped frames around candidate boundaries (including before and after), displays enough broadcast UI to identify series/game state, and records the DeepSeek disposition and concise evidence rationale. The first-stage non-vision executor may implement capture/review infrastructure and populate the handoff queue, but must not visually approve a boundary; route all pixel-level judgments to `docs/goals/active/mpl-s18-visual-proof-deepseek-handoff.md` for the second-stage DeepSeek reviewer.
- Establish series start/end intervals and then game start/end intervals wherever evidence permits. Do not infer game timestamps directly from match database duration alone unless the VOD clock and timing relationship are independently verified.
- Correctly handle multi-series broadcast dates, pauses, desk segments, replays, promos/ads, delays, and nonstandard broadcast structure.
- Quarantine unresolved/ambiguous boundaries. Ensure no downstream timestamp citation or visual event is attached to the wrong series/game.
- Make the validator independently check invariants: schedule completeness, unique IDs, chronological ordering, interval non-overlap where appropriate, timestamp bounds against VOD duration, valid source/video/hash references, and status-specific required evidence. Add fixtures for ambiguous team mentions, misleading schedule intros, promotions, repeated replays, reordered teams, missing lines, and boundary drift.
- Regenerate all offset reports and reconcile the current documentation. A previously resolved source retained as struck-through/pending must not remain contradictory in final status summaries.

### Deliverables

- Reliable series and game boundary data with provenance and status per interval.
- Boundary detection/refinement tool, automated DeepSeek screenshot-review integration and target queue, and genuinely independent deterministic validator.
- Machine-generated unresolved-target report with timestamped links, screenshot capture instructions, and automatic quarantine/inconclusive status; no human-review queue.

### Acceptance

- Every boundary claimed as caption-verified or visually verified has the corresponding distinct evidence, reproducible provenance, and verification record. Visual verification specifically requires a valid DeepSeek review record tied to exact screenshot hash(es).
- Heuristic or missing boundaries remain clearly quarantined and cannot generate game-specific citations.
- No false-positive verification in adversarial regression fixtures.
- All 72 series and 174 games are accounted for, even if some remain explicitly unresolved.

---

## 6. Phase 2 — Build complete game-level evidence timelines

### Tasks

- Create a canonical game-level evidence representation linking:
  - season / series / game IDs and team/player/hero entities;
  - broadcast source, transcript source span, exact raw lines, source hash and caption cue timestamps;
  - verified VOD ID and timestamp URL;
  - database snapshot, table/row references, query ID, parameters, formula and values;
  - screenshot IDs, requested/actual frame timestamps, image hashes, DeepSeek review status and concise reviewer notes;
  - event category, evidence type, confidence, uncertainty and counterevidence.
- Design a usable taxonomy for gameplay observations. At minimum cover:
  - draft/pick/ban and composition hypotheses;
  - lane matchups, early lane pressure and resource allocation;
  - rotations, ganks, counter-ganks and cross-map trades;
  - jungle pathing and buff/resource contests where observable;
  - Turtle/Lord setup, objective contest, secure/deny, trade and post-objective conversion;
  - turret/structure pressure, wave management, lane assignments and map pressure;
  - vision/brush control only when directly observable in footage or source;
  - teamfight initiation, target selection, peel, spacing, disengage, flank and follow-up;
  - player positioning, mechanical execution, mistakes, outplays and survivability, only when evidence actually supports the interpretation;
  - gold/experience/item/level power spikes where scoreboard evidence exists;
  - base defense, siege, comeback, throw, closing and failure to convert;
  - macro (map-wide strategic decisions), meso (rotations, objective setups and team-level execution), and micro (individual mechanics/positioning/ability usage).
- Extract atomic events rather than immediately writing long narrative conclusions. An event should be one falsifiable observation with a bounded time interval and clear subject/action/context.
- Build chronological timelines for all games whose source boundaries can be validated. For unresolved games, create a database-only timeline or report and label it accurately; never manufacture broadcast timestamps.
- Use SQL and reproducible deterministic calculations for database facts. Never ask an LLM to calculate basic totals from transcript text when the database contains the fields.
- Add validation of line spans, quoted text, timestamps, database result reproducibility, canonical IDs, source hashes, visual sidecar integrity, and interval/game mapping.

### Visual evidence improvements

- Review `tools/video_frames.py` and its tests. Preserve the current safe frame-capture behavior and sidecar provenance.
- Add practical workflows for capturing a sequence/contact sheet around an event, not just one isolated frame. Support repeated frames at useful intervals and exact frame links. Use screenshot sequences only for visual review. Capture enough ordered frames to answer the bounded question; if still images cannot prove the claimed continuous event, mark it inconclusive rather than switching to human video review.
- Capture useful visible context when available: minimap/player positioning, lane formations, objective HP/state/timers, turret state, scoreboard kills/deaths, gold difference, levels, item builds, death timers, wave positions, teamfight spacing, target selection, and game clock. Only record values/positions actually legible in the reviewed footage.
- Record OCR/CV output as machine-extracted and unverified until DeepSeek checks it against the original screenshot. Add confidence and review provenance; do not turn blurred or ambiguous UI into hard facts.
- Keep all screenshots, contact sheets and media caches local and Git-ignored.

### Deliverables

- Canonical game-level event/evidence schema and deterministic validator.
- Reproducible timeline generation and review tools.
- Game timelines for verified portions of the season, with unresolved coverage reported honestly.

### Acceptance

- Every evidence event resolves to its exact underlying source span/query/frame and verified series/game association.
- No timestamp-backed event can point to an unverified game boundary.
- A visual capture is never automatically treated as a verified gameplay fact. DeepSeek visual review pass 1 is complete (53 frames, 11 boundaries; 0 promotions), but 20 non-null boundary candidates and 18 null offsets remain pending. Visual-dependent claims remain pending/quarantined and are listed in `docs/goals/active/mpl-s18-visual-proof-deepseek-handoff.md` §8.4. No human reviewer is part of this workflow.
- Re-running ingestion/build does not duplicate evidence or alter raw sources.

---

## 7. Phase 3 — Build a resumable AI-assisted extraction and audit engine

### Extraction pipeline

- Implement a configurable model/provider adapter so the pipeline is not locked to one LLM vendor. Keep model configuration, prompts, schemas and validation separate from provider transport. Do not hardcode API keys or secrets.
- Process transcripts in bounded chunks using source IDs, line ranges and timed caption cues; never feed the entire season corpus into one prompt or depend on one enormous context window.
- Extract structured candidate observations into a strict schema. Require exact source line spans for transcript claims, explicit event time ranges, known entity IDs or a quarantined unknown entity, category, evidence type, confidence, uncertainty, and alternative interpretation.
- Do not let the LLM invent timestamps. The deterministic alignment layer supplies verified cues; the model only selects source spans and proposes interpretations.
- Reject malformed model output, unknown or guessed identifiers, invalid categories, text not found in the source, impossible timestamps, unsupported DB fields, and missing provenance. Quarantine rather than silently repair ambiguous output.
- Persist job state by source/chunk. Make retries idempotent, record model/prompt/schema versions, and allow resuming only failed or changed chunks.
- Store extraction errors and quality metrics, including quote fidelity, entity resolution rate, timestamp validity, duplicate rate, unsupported-claim rate and reviewer rejection rate.

### Corpus search and synthesis

- Add searchable corpus retrieval across all 27 transcript files, returning exact spans, surrounding context, source IDs and aligned timestamps only when valid.
- Add structured DB query retrieval using the existing query catalogue and versioned SQL/formulas.
- Create a candidate-insight workflow that aggregates atomic events across games, teams, players, heroes, drafts and patches.
- Require a minimum evidence/sample threshold for longitudinal tendencies; expose denominator, sample size, match context and patch partitions. Do not infer a season-long pattern from one play or one series.
- Search for counterexamples and matched comparisons before promoting a candidate insight. Include games where the pattern did not occur, teams that achieved the same outcome differently, similar drafts that lost, and opposing conditions.
- Preserve the distinction between commentator narrative, source-reported database facts, derived statistics, visually observed gameplay, and model inference.

### Audit engine

Implement an auditable command/workflow conceptually equivalent to:

`Audit insight <INSIGHT_ID>`

It must:

1. Retrieve the exact insight and all referenced evidence records.
2. Load the original immutable transcript passages and context before/after each span.
3. Recheck quote fidelity, source hash, source ID, timestamp mapping and VOD identity.
4. Search the entire available transcript corpus for related passages and counterexamples.
5. Re-run each database query/calculation against the recorded snapshot and compare the result.
6. Check whether sources are genuinely independent or share the same origin.
7. Retrieve relevant DeepSeek-reviewed screenshots or ordered screenshot sequences where available. State clearly whether screenshots were reviewed by DeepSeek, merely captured, linked, or unavailable.
8. Separate direct facts, commentator interpretations, database records, derived statistics, observed gameplay and AI hypotheses.
9. Give a verdict: `supported`, `partially supported`, `contradicted`, or `inconclusive`.
10. Show strongest evidence, strongest counterargument, alternative explanations, missing evidence, confidence and limits.
11. Append an audit record without silently overwriting the original insight. Corrections must be versioned and preserve history.

### Acceptance

- A candidate insight can be generated from source material, validated, counter-searched, and audited end to end.
- An audit can reproduce every referenced database fact and verify transcript quotations.
- Provider failure, rate limits, malformed model output, and interrupted processing do not corrupt completed work.
- The same inputs/configuration create stable IDs and reproducible deterministic outputs wherever intended.

---

## 8. Phase 4 — Stratified full-season semantic analysis

Do not simply generate 72 reports from database rows and label them semantic analysis. Build a representative analysis plan and track genuine evidence coverage.

### Sampling and scaling

- Use the full 72-series / 174-game schedule and database as the population frame.
- Create a stratified analysis plan that covers all nine weeks, all nine teams, different standings positions, match outcomes, 2-0 and 2-1 series, game lengths, map modes, patch/meta periods, draft types, and different strategic situations.
- Include high-value events (turning points, objective contests, base defenses, failed sieges, comeback situations) and ordinary games as controls to reduce highlight-selection bias.
- Start with a representative batch large enough to test the complete pipeline, then scale in resumable batches. The target is the whole season where source and boundary quality permit.
- Prioritize games with fully verified source alignment and game boundaries. Continue to document and expose unresolved cases rather than silently excluding them from coverage.
- Distinguish these report states: database-only, source-mapped, transcript-verified, boundary-verified, visual-reviewed, cross-checked, and fully audited.

### Analytical outputs

Generate and maintain:

1. **Series reports:** outcome, game-by-game context, drafts, timelines, turning points, objectives, evidence links, counterexamples, and unresolved questions.
2. **Game reports:** detailed chronological event timelines; game state changes; early/mid/late game; draft-to-execution links; objective and structure conversion; teamfights; mistakes/outplays; win conditions and failure points.
3. **Team dossiers:** strategic identity hypotheses, draft tendencies, side preferences, early/mid/late-game patterns, tempo, rotations, objective setup/control, teamfight patterns, closing ability, adaptability, patch changes, strengths, weaknesses and counter-strategies. Each tendency must cite multiple examples and counterexamples.
4. **Player dossiers:** statistical baseline plus evidence-backed role behavior, positioning, mechanics, hero comfort/flex, decision quality, rotations, teamfight contributions, repeated mistakes/successes, situational performance, matchup and patch context. Avoid judging a player from a single match or KDA alone.
5. **Hero dossiers:** pick/ban context, lane/role, composition synergies, matchup/counter context, win/loss contexts, item/talent choices where data exists, and examples of actual execution. Separate popularity and win rate from strategic effectiveness.
6. **Draft and composition analysis:** pick/ban order when actually known, respect-ban hypotheses with supporting evidence, flexible picks, power spikes, initiation/front-to-back/dive/pick-off/siege/defensive composition hypotheses, and how the composition was executed. Never label a ban a proven respect ban without evidence.
7. **Macro / meso / micro reports:** map-wide resource allocation and trades; rotations and objective setups; individual mechanics, positioning, target selection and ability use. Include only observable or supported claims.
8. **Objective and map-control analysis:** Turtle/Lord setup, secure/deny/trade, lanes, turrets, waves, vision and pressure. If no reliable data exists, state that. Do not infer objective counts from commentary alone.
9. **Patch/meta trends:** version/patch-aware changes in picks, bans, compositions, roles and gameplay patterns. Avoid cross-patch comparisons without explicit caveats.
10. **Opponent scouting and head-coach briefs:** actionable preparation points, opponent tendencies, likely options only when supported, punishable patterns, responses to test, timestamped VOD links and screenshot evidence, drills, counterexamples, confidence and limitations.

### Acceptance

- Every series and game has a coverage state; every meaningful report links to underlying evidence or explicitly labels itself database-only/unresolved.
- Season-level claims draw on multiple relevant games and include counterexamples and patch/context limitations.
- All teams, eligible players and heroes have evidence-backed profiles to the extent supported by source coverage; no empty template counts as an analysis.
- The coverage report differentiates report-file existence from semantic evidence coverage and visual/audit coverage.

---

## 9. Phase 5 — Coaching usefulness and quality review

- Run automated adversarial review on a stratified sample of generated reports, including cases likely to be wrong or ambiguous; retain exact reviewer/model provenance and unresolved limitations.
- Ask whether a coach could use the report to answer: what does this opponent do, under what conditions, what can be punished, what should we prepare, and what evidence supports this recommendation?
- Create targeted coaching questions and drills only where evidence supports them.
- Identify the strongest opposing explanation for each important insight.
- Track unsupported statements, hallucinated/incorrect entities, false timestamp links, wrong game joins, weak sample sizes, patch confounding and visual misreads.
- Measure usefulness separately from extraction accuracy. A perfectly cited but strategically trivial observation is not sufficient.
- Keep confidence conservative. Insights that fail review remain partial, contradicted, or inconclusive; do not upgrade them to make progress look better.

### Acceptance

- At least one useful, fully audited coaching brief per team and an overall head-coach brief, with evidence depth and confidence visible.
- The reports include concrete review links, counterexamples and practical preparation questions/drills.
- A skeptical reader can challenge each major recommendation by following its references.

---

## 10. Phase 6 — Documentation, CI, reproducibility and project hygiene

### Documentation reconciliation

At the previous audit, reporting inconsistencies included:

- `corpus-inventory.md` reporting 27/27 metadata verification while a stale parsing-risk sentence still said 0/27 candidates needed verification.
- `coverage-summary.md` reporting 3 pilot + 25 expansion + 44 DB-only (=72), while its known-gaps section said 45 DB-only.
- Different boundary-verified / unvalidated counts across `coverage-summary.md`, `unvalidated-sources.md` and `game-offsets.json`.
- A resolved boundary retained as struck-through/pending in `unvalidated-sources.md` while its summary still counted it as unresolved.
- `pilot-quality-report.md` retaining 18 observations / 3 insights / 1 audit while the expanded ledger had 24 / 6 / 2.
- Top-level source offset statuses staying `pending` even where child entries said `boundary_verified`.

Recompute everything from underlying records. Fix status derivation and generate reports from one source of truth. No manually maintained contradictory totals.

### Test/CI improvements

- Keep `python tools/verify.py` and existing application tests passing.
- Add semantic validation to CI for committed artifacts that do not require local-only raw media. This should validate schema, IDs, coverage counts, DB query references where feasible, ledger links, status consistency, report references, offsets, and generated report parity.
- Keep a separate local-only gate for raw transcript SHA checks, cached caption alignment, local frames and visual-review assets. It must fail clearly when prerequisites are missing, not claim it passed.
- Add synthetic fixtures so core logic is testable in CI without shipping copyrighted raw transcripts or private media.
- Include adversarial tests: ambiguous boundaries, stale hashes, partial alignment, false caption matches, video drift, ads/promos, missing VODs, duplicate chunks, incorrect team orientation, invalid DB references, and contradictory report summaries.
- Ensure CI reports clearly distinguish application regression from semantic evidence validation.
- Update `analysis/README.md`, `analysis/index.md`, top-level README semantic status, `docs/ROADMAP.md`, and relevant schemas/commands so instructions match the actual implementation.

### Project hygiene

- Keep all active goals in `docs/goals/active/` and move this goal to `docs/goals/finished/` only after every acceptance criterion is met, following `AGENTS.md`.
- Preserve relative structure when archiving goal-related snapshots.
- Avoid committing generated local-only data or media.
- Avoid unnecessary duplication of old reports. Keep historical evidence and audit history intact.
- Ensure all scripts have clear CLI help, deterministic output where possible, actionable error messages, type/format validation, reasonable timeout/retry handling, and tests.

### Acceptance

- The documented local and CI test commands reflect the true coverage and pass.
- All published count/status summaries agree with their machine-readable sources.
- A clean clone can run CI without the local transcript corpus, while a configured local workstation can run the full evidence gate.

---

## 11. Required reporting structure and definitions

Maintain a machine-generated coverage report with at least these dimensions:

- Transcript sources: present / checksum-verified / missing / changed.
- VODs: schedule candidate / metadata verified / mismatch / unresolved.
- Timed captions: fully aligned / partially aligned / failed / not attempted.
- Series boundaries: verified / heuristic / unresolved / quarantined.
- Game boundaries: verified / heuristic / unresolved / quarantined.
- Series and games: total / database-only / source-mapped / transcript-verified / visual-reviewed / cross-checked / audited.
- Evidence records: segments / observations / events / insights / counterexamples / audits / rejected candidates.
- Visual evidence: captured / reviewed / used / context-only / rejected / failed.
- Teams / players / heroes: profile completeness and evidence depth, not just file count.
- Extraction jobs: completed / failed / quarantined / pending, with model and prompt version.
- Quality indicators: quote fidelity, timestamp validity, source mapping accuracy, DB reproducibility, visual review accuracy, duplicate rate, unsupported claim rate, and audit outcomes.

Every metric must define its denominator. For example, “26/27 caption-aligned sources” is not “26/27 semantically analyzed broadcasts”; “72/72 Markdown files” is not “72/72 transcript-backed analyses.”

---

## 12. Execution rules for the agent

- Begin with a fresh repo/worktree audit and a concise execution plan saved in the goal progress log.
- Read repository `AGENTS.md`, applicable skills/instructions, and existing goal files before modifying code.
- Execute phases in dependency order. Do not scale analysis while series/game source mapping is unreliable.
- Continue autonomously through implementation and testing. Do not ask for confirmation for routine reversible coding, report generation or test execution.
- For destructive operations, database migrations, raw-source replacement, history rewrites, or publication of local/copyrighted assets: do not proceed without explicit authorization. Prefer read-only and backed-up workflows.
- If a local path is unavailable, search the local workspace and configured environment before declaring a blocker. Do not claim access to another machine or user path unless it is actually available.
- If YouTube blocks automated access, use the user's already-authenticated local environment only through supported tools; never harvest or expose browser credentials. Fall back to an explicitly pending/quarantined status and a repeatable automated DeepSeek screenshot-target queue rather than inventing metadata or requesting human visual review.
- If an API/model provider is unavailable, finish deterministic tooling, fixtures, schema, reports, and local processing that can run without it. Do not mark LLM extraction complete.
- Make reasonable engineering decisions without waiting for user input. When a choice materially changes architecture, protect the current working implementation, document the trade-off, and choose the smallest reversible option.
- Run focused tests after each meaningful change, then the full app regression and semantic suites. Inspect generated diffs and report accuracy before committing.
- Do not merge or publish a branch merely because tests pass. Follow repository workflow and user authorization for push/merge. Never force-push or rewrite history as a convenience.
- Update this goal file's progress/checklist as work advances. If interrupted, leave exact next commands, known blockers, and current test results.
- At the end, provide a factual completion report: what changed, actual coverage, tests run and their results, unresolved blockers, artifacts generated, current Git branch/commit, and whether anything was pushed or merged.

---

## 13. Final definition of done

This goal is complete only when all of the following are true:

1. The 27-source corpus and VOD metadata/timed-caption states are verified or explicitly quarantined, with no false source-ready claims.
2. All 72 series and 174 games are mapped to broadcast sources and have series/game boundary statuses backed by real evidence; unresolved cases remain quarantined and are not used for game-level claims.
3. The evidence model supports atomic game events with immutable transcript spans, timestamp provenance, reproducible DB references, reviewed visual evidence, clear labels and counterevidence.
4. The LLM-assisted extraction and insight-generation pipeline is configurable, resumable, validated and auditable; deterministic steps remain provider-independent.
5. The audit workflow can retrieve and independently check claims, search counterexamples, inspect available footage and issue one of four defensible verdicts without overwriting history.
6. The season is semantically analyzed at game level to the maximum supportable coverage, with team/player/hero/draft/macro/meso/micro/objective/coaching reports grounded in evidence. Coverage gaps are prominent and honest.
7. Important longitudinal claims are supported by multiple games, relevant comparisons and counterexamples; one-game observations are labelled as such.
8. The screenshot workflow supports ordered reviewable sequences with DeepSeek as the sole visual reviewer and records the limitations of still images; any OCR/CV output is checked against the original screenshots before being treated as fact.
9. Reports, ledgers, source statuses, offset statuses and coverage counts agree because they are generated/validated from canonical underlying records.
10. Application regression, committed semantic checks, local corpus/evidence checks, and adversarial fixtures pass. No unrelated user changes are lost and no raw transcripts/media/credentials are committed.
11. Documentation reflects the actual system and provides reproducible commands for a new local run.
12. This goal is moved from `docs/goals/active/` to `docs/goals/finished/` only after all applicable completion gates have passed. If an external dependency prevents full completion, leave the goal active and report a precise, evidence-backed blocker rather than marking it finished.

**The central quality bar:** Build a trustworthy coaching analyst, not a report-count generator. Evidence quality, correct game mapping, falsifiability, counter-analysis and usefulness take priority over superficial coverage.
