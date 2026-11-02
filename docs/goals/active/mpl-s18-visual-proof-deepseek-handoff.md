# Goal: Complete Screenshot-Based Visual Verification with DeepSeek Vision

**Project:** Berliandro's Eye — MPL ID Season 18  
**Role in the wider goal:** Dedicated visual-proof workstream for the semantic coaching completion goal  
**Status:** Active handoff specification; execute in the second phase with a vision-capable DeepSeek model  
**Primary visual reviewer:** DeepSeek vision model, selected through configuration after capability verification  
**Human visual review:** None. This workflow must not create a human-review queue or require a person to inspect screenshots.

---

## 1. Mission

Build and run an auditable screenshot-capture and visual-review pipeline in which DeepSeek is the sole visual reviewer.

The project already has transcript alignment, a screenshot-capture utility, a small historical visual-review record, a SQLite data set, and a partial semantic-evidence system. Those components are not yet a full-season, game-level visual-proof system.

This goal owns every remaining task in the broader semantic-analysis goal that requires visual inspection of screenshots. It must:

1. Capture reproducible screenshots from the official MPL Indonesia Season 18 broadcasts and, where available, per-game VODs.
2. Submit those screenshots, alone or in temporally ordered groups, to a vision-capable DeepSeek model.
3. obtain structured, conservative, auditable judgments about exactly what is visible.
4. Attach accepted visual claims to immutable screenshot hashes, source IDs, video IDs, timestamps, and existing evidence records.
5. Reject, retry, or quarantine uncertain evidence automatically. Do not ask a human to inspect it.
6. Provide machine-checkable proof that a visual claim was accepted by the configured DeepSeek model and that the exact reviewed screenshot is the one referenced by the report.

The first-stage model that lacks vision must not pretend to have reviewed images, infer visual facts from filenames, or mark visual work complete. It may prepare candidate timestamps, repair non-visual code, reconcile database/transcript metadata, and build the integration scaffolding. The actual image interpretation belongs to the DeepSeek vision phase described here.

## 2. Non-negotiable operating rules

### 2.1 DeepSeek is the reviewer, not a human

- Use a DeepSeek model whose currently configured API/model combination accepts image inputs. Verify image-input capability with a small fixture before processing the corpus.
- Model name and API configuration must be explicit and configurable. Do not hardcode an assumed model ID or silently fall back to a text-only model.
- The reviewer is DeepSeek. Record provider, exact model ID, API mode/version where available, prompt version, and request identifier.
- No manual review, human visual approval, or human transcription step is permitted.
- An inconclusive result is a valid automated terminal state. It means the visual claim is not proven and must not be published as verified.
- Do not create statuses such as needs-human-review or awaiting-manual-approval. Use inconclusive, rejected, retryable, or quarantined.
- A person may launch the goal and configure credentials, but must not be required to inspect screenshots or adjudicate visual claims.

### 2.2 Fail closed

- A screenshot being captured successfully does not mean it proves anything.
- A screenshot being sent to DeepSeek does not mean the claim is verified.
- Do not treat a model's confident wording as sufficient proof. Require the requested visual elements to be legible and directly observable.
- Missing, blurry, cropped, obstructed, ambiguous, contradictory, or temporally insufficient evidence must be marked inconclusive or rejected.
- Do not infer hidden game state, player intent, comms, vision, causality, or a sequence of actions from one still image.
- Do not turn a commentary statement into a visual fact. Keep transcript evidence and screenshot evidence distinct, then link them when they independently support the same claim.
- If a claim cannot be proven from screenshots, retain it as commentary-only, database-only, or unverified and state the limitation.
- A model response is not proof unless its exact input-image hash, prompt version, model identity, structured response, and verdict are recorded.

### 2.3 Preserve source and project integrity

- Raw transcripts and screenshot images remain local and Git-ignored unless the repository's existing data policy explicitly changes.
- Never commit API keys, access tokens, private request headers, or credential-bearing logs.
- Do not modify the canonical SQLite database merely to make visual evidence fit a claim.
- Preserve existing evidence and audit history. New DeepSeek reviews must be append-only or versioned; do not overwrite legacy review decisions.
- Do not rewrite source offsets from visual guesses. A verified boundary must have a reproducible screenshot reference and explicit review record.
- Do not push, merge, publish, delete source media, or perform destructive migrations unless separately authorized.

---

## 3. Current repository baseline to revalidate

The following is a snapshot from the repository inspection on 2026-11-02, not a permanent truth. Recompute it from the live checkout before acting. The files currently disagree, so the structured artifacts must be reconciled rather than trusting one prose summary.

### 3.1 Relevant paths

- Screenshot capture: tools/video_frames.py
- Source metadata: analysis/sources/source-manifest.json
- Timed caption alignment: analysis/evidence/timed-alignment.json
- Series/game offset candidates: analysis/evidence/game-offsets.json
- Historical screenshot review: analysis/evidence/visual-review.json
- Evidence schema: analysis/evidence/evidence-schema.json
- Evidence ledger: analysis/evidence/pilot-ledger.jsonl
- Evidence query catalog: analysis/evidence/query-catalog.json
- Evidence audit log: analysis/evidence/audit-log.jsonl
- Coverage summary: analysis/reports/coverage-summary.md
- Offset exceptions: analysis/reports/unvalidated-sources.md
- Pilot quality report: analysis/reports/pilot-quality-report.md
- Analysis index: analysis/index.md
- Local screenshot cache: analysis/cache/video-frames/ (Git-ignored)

### 3.2 Offset and boundary state observed

A direct count of analysis/evidence/game-offsets.json at the time of this handoff found:

| Measure | Observed value |
|---|---:|
| Broadcast sources | 27 |
| Scheduled regular-season series | 72 |
| Series marked boundary_verified | 26 |
| Series marked detected_pending_review | 24 |
| Series marked pending_validation | 22 |
| Series with no start_seconds | 14 |
| Series with no end_seconds | 72 |
| Source-level validation_status still pending | 27 |

The fact that 26 child series rows say boundary_verified while all 27 source-level validation_status values say pending is a state-model inconsistency. Resolve it in the data model and validator. A caption-boundary status is not automatically visual proof.

The prose files disagree about the number of unresolved sources and series. For example, unvalidated-sources.md says four active unvalidated sources while the structured offsets contain substantially more pending/detected rows. Recompute all counts from the structured data and regenerate prose summaries from one canonical inventory.

The historical offset entries largely concern series starts and often have no end. They do not establish exact starts and ends for all individual games in all series. The scheduled 72 series comprise 174 games; build and validate game-level coverage separately.

### 3.3 Historical screenshot baseline

The existing analysis/evidence/visual-review.json contains eight frame attempts:

- Five gameplay frames previously marked used.
- One post-game context frame previously marked used-as-context-only.
- One promotional-overlay frame previously rejected.
- One capture failure.

The file records a historical reviewer label of OpenCode multimodal review. Do not silently change that reviewer identity or assume this current non-vision model can reproduce the old visual judgment. Preserve the legacy record and re-review the underlying screenshot files with DeepSeek. Add new records that explicitly identify DeepSeek as the reviewer. If a referenced screenshot is missing locally or its hash cannot be verified, mark it unavailable and recapture it; do not reuse the old verdict as current DeepSeek proof.

### 3.4 Existing capture behavior

tools/video_frames.py already captures timestamped YouTube screenshots using Playwright/Chromium and supports a local-video FFmpeg path. It writes sidecars containing requested/actual time and hash-related provenance. It can create contact sheets. Its documentation correctly separates capture success from visual review.

Extend this tool or build a small companion utility where needed. Do not replace a working capture path without evidence that the replacement is more reliable.

---

## 4. Required deliverables

The implementation must leave these durable outputs (adapt names only when a strong existing project convention requires it):

1. **Visual proof target manifest** — analysis/evidence/visual-proof-manifest.json  
   Machine-readable inventory of all review targets, capture plans, scope, statuses, and evidence references.

2. **Append-only DeepSeek visual review ledger** — analysis/evidence/deepseek-visual-review.jsonl  
   One structured record per DeepSeek review attempt, including model and screenshot provenance, exact claims assessed, verdict, confidence, limitations, and retry lineage.

3. **Screenshot sidecars** — next to local images under analysis/cache/video-frames/  
   Exact screenshot hash, video ID, timestamp, capture method, requested/actual time, capture status, and review linkage. The screenshot cache remains local-only.

4. **DeepSeek reviewer integration** — a reusable module or tool under tools/  
   Configuration-driven; validates image inputs and structured outputs; retries safely; caches by image hash plus model and prompt version; never exposes secrets.

5. **Prompt and output schema** — versioned and tested  
   The prompt must request observable facts and uncertainty, not hidden reasoning. Output must be parseable and schema-validated.

6. **Automated tests and validator** — tests for malformed model output, missing images, changed hashes, wrong timestamps, ambiguous visual states, promotional overlays, and fail-closed behavior.

7. **Reconciled documentation** — coverage reports distinguish captured, DeepSeek-reviewed, screenshot-verified, rejected, inconclusive, and quarantined evidence. Counts must be generated from the manifest/ledger rather than manually typed.

8. **Report integration** — match, game, team, player, draft, and coaching reports cite only verified visual claims and include stable evidence IDs plus timestamp links.

---

## 5. Build the screenshot-to-DeepSeek pipeline

### 5.1 Verify DeepSeek vision capability

Before scaling:

- Inspect the current DeepSeek API documentation and the available account/model configuration to identify a model that accepts image input.
- Verify the exact endpoint/request shape for image content and supported image formats, size limits, batching behavior, and response structure.
- Use a local fixture screenshot to verify that the endpoint receives the image, can read the visible game clock/team labels in a controlled test, and returns the expected structured response.
- Record the exact provider/model/API configuration used in the audit output, but never record secrets.
- Fail fast if the configured model is text-only or if an image is silently omitted from the request.
- Do not implement a silent provider fallback. A fallback to another vision model requires explicit configuration and must be recorded as a different reviewer.

### 5.2 Capture planning and reproducibility

Use the canonical source manifest and schedule/database joins to generate capture targets. Each target must include:

- target_id and evidence question;
- source_id, video_id, canonical video URL, and broadcast date;
- match_detail_id, team names, and game number when known;
- candidate timestamp and its source (caption cue, database VOD link, schedule heuristic, existing observation, or another named source);
- requested capture time and a contextual window;
- reason for capture and the specific claim it is expected to verify;
- expected visible UI or game-state element;
- whether the target is a boundary, scoreboard, draft, event, player, team, or general context check.

Record requested time and actual player time separately. Reject captures whose actual time is absent or outside the configured tolerance. Never use a timestamp link based only on the requested time when the player sought elsewhere.

For event review, capture temporally ordered screenshot sets rather than one isolated frame. The default should be a context sequence around the candidate timestamp (before, at, and after), with intervals configurable per event. Add denser samples for fast events. Avoid huge indiscriminate screenshot dumps; prioritize candidates derived from captions, existing reports, database anomalies, game-state changes, and stratified coverage requirements.

Store capture settings and tool versions. Hash every image. A changed image at the same path must be treated as a new input.

### 5.3 DeepSeek review request

Send original screenshots at sufficient resolution for the relevant UI. For a sequence, preserve chronological order and include each frame's exact timestamp in the request metadata. Do not rely only on a compressed contact sheet when small scoreboard text or hero identity must be read; use contact sheets for navigation and individual original frames for final judgments.

The prompt must require DeepSeek to:

- identify which requested question(s) can actually be answered from the supplied image(s);
- report only directly visible details;
- distinguish visible text from visual inference;
- transcribe game clock, team labels, kill score, gold, objective/event overlays, hero portraits, item icons, draft picks/bans, and other requested UI only when legible;
- identify obscured or unreadable values as unknown rather than guessing;
- note ads, loading screens, post-game screens, replay overlays, stream overlays, minimap occlusion, cropping, compression, or other visual contamination;
- identify whether a single screenshot or the complete ordered sequence supports the requested claim;
- provide concise evidence notes and uncertainty/limitations without exposing or requiring hidden chain-of-thought;
- choose a strict verdict from the approved enum.

Do not ask the model to infer intent, comms, player thought, hidden vision, exact input timing, or causality from static images.

### 5.4 Required review output

Use a versioned JSON schema with at least these fields:

- review_id
- target_id
- screenshot_ids (ordered)
- input_image_sha256 values
- source_id, video_id, match_detail_id, game_no
- requested_seconds and actual_seconds for each screenshot
- provider = deepseek
- exact model_id
- api_mode/version where available
- prompt_version and schema_version
- request_id where available
- review_timestamp
- image_quality: usable, limited, or unusable
- visible_context: gameplay, draft, loading, replay, post_game, promotional, other, or unknown
- observations: atomic statements, each linked to screenshot_id(s)
- requested_claims: each claim assessed separately
- verdict per claim: verified, rejected, inconclusive, or more_screenshots_required
- confidence per claim, with a documented scale
- limitations
- retry_of or supersedes_review_id when applicable
- response_hash or durable response provenance
- reviewer_notes containing concise evidence grounds, not hidden reasoning.

Reject malformed responses. Permit one bounded structured-output repair/retry if appropriate; if still invalid, mark the review failed/inconclusive and retain the response/error metadata without treating it as evidence.

### 5.5 Verdict semantics

- **verified:** every required visual element is directly legible and the image(s) support the exact bounded claim.
- **rejected:** the screenshot contradicts the claim, identifies the wrong match/game, shows an irrelevant screen, or clearly fails the requested proof.
- **inconclusive:** the evidence is insufficient, ambiguous, blurry, obscured, or conflicting.
- **more_screenshots_required:** the model identifies a specific additional temporal/context frame needed. The capture planner may automatically acquire it and resubmit.
- **capture_failed / review_failed:** operational states, not evidence verdicts.

A claim is visually verified only when its review record passes schema validation and its image hashes still match. For a group of claims, accept or reject each separately. Never let one clear item make all requested claims verified.

### 5.6 No-human uncertainty loop

The system must resolve uncertainty automatically where possible:

1. DeepSeek returns more_screenshots_required with the missing context specified.
2. The planner captures the requested surrounding frames, checks actual timestamps and hashes, then resubmits.
3. DeepSeek reviews the expanded set.
4. If it is still inconclusive or rejected, mark the target inconclusive/rejected and quarantine it from positive visual claims.
5. Continue processing other targets; do not block the entire season on one ambiguous clip.
6. Do not create any manual or human-review queue.

Retries must be bounded. Use configurable maximum attempts, backoff, per-target capture limits, request timeout, and a cost budget. A repeated ambiguous target must terminate as inconclusive, not loop forever.

---

## 6. The full visual-proof backlog

All items below require screenshot evidence reviewed by DeepSeek. A task is complete only when the relevant target manifest and DeepSeek ledger contain verifiable records. Merely generating screenshots or reports does not complete a visual-proof task.

### VP-01 — Re-review the historical pilot screenshots

Re-capture or verify the local source images for all eight entries in the legacy visual-review.json. Re-submit all available images to DeepSeek with the exact original target question and context. Include the prior accepted, rejected, context-only, and failed attempts in the audit.

Required outcome:

- DeepSeek independently reviews the six historically usable images.
- The promotional overlay is independently classified and rejected as gameplay evidence if still visible.
- The previously failed timestamp is retried or remains a capture failure.
- Legacy decisions remain preserved as historical data.
- New report claims refer to new DeepSeek review IDs, not merely the old OpenCode reviewer label.

### VP-02 — Broadcast identity and series-to-VOD association

For each of the 27 broadcast sources:

- Verify that captured frames belong to the expected MPL ID S18 broadcast and the intended week/day.
- Where visible, verify broadcast title/channel context and match scoreboard/team identity.
- For every scheduled series mapped to a broadcast, obtain screenshots that visibly tie the correct two teams to the actual in-video series.
- Detect cases where a schedule overview, caster mention, lineup announcement, replay, or unrelated team mention was mistaken for the beginning of a series.
- Ensure a broadcast association is not mistaken for an exact series start.

Do not use a screenshot of a YouTube title/thumbnail alone as proof of the in-game team matchup. Prefer in-video team labels, loading/draft screens, or scoreboard evidence.

### VP-03 — Series boundaries

Review all 72 regular-season series, not just the 26 rows currently marked boundary_verified.

For each series, capture a sequence around the candidate start and, where possible, the transition from the previous series:

- pre-boundary context;
- candidate boundary;
- first clear team/draft/loading/scoreboard state;
- post-boundary confirmation.

DeepSeek must identify the actual series and visible teams. It must distinguish pre-show, caster discussion, schedule overview, lineup announcement, draft, game play, replay, and post-game. A boundary should not be marked visually verified solely because casters mention a team.

Review or quarantine the current problem candidates, including the sources and match IDs listed by the live game-offset manifest. At the 2026-11-02 snapshot, known examples include:

- W1D1: 1036 has a detected candidate; 1037 has no start.
- W1D3: 1042 is pending review; 1043 has no start.
- W2D2: 1048 is pending review.
- W3D2: 1056 is pending review.
- W3D3: 1057 and 1058 are pending review.
- W4D1: 1061 has no start.
- W4D2: 1063 and 1064 have no start.
- W4D3: 1066 and 1067 are pending review.
- W5D2: 1072 is pending review.
- W6D1: all three candidate offsets are pending review and appear identical at 2425 seconds; this is a high-priority suspected mapping failure.
- W6D2: 1078 is pending review; 1079 has no start.
- W6D3: 1082 is pending review; 1083 has no start.
- W7D1: 1085 has no start.
- W7D2: 1086 and 1088 are pending review; 1087 has no start.
- W7D3: 1090 is pending review.
- W8D1: 1092 and 1093 have no start.
- W8D2: 1094, 1095, and 1096 are pending review.
- W8D3: 1097 is pending review; 1099 has no start.
- W9D1: 1101 has no start.
- W9D2: 1102 and 1103 are pending review; 1104 has no start.
- W9D3: 1105 has no start.

This list is a starting queue only. Regenerate it from the live checkout; do not assume this snapshot is still current.

### VP-04 — Individual game boundaries and game identity

The regular season contains 174 games. Verify game-level coverage independently from 72 series-level coverage.

For each game, use the most reliable available VOD source and capture enough context to prove:

- match_detail_id and game number;
- the two teams and side assignment where visible;
- the game has actually started (not merely a draft/loading screen);
- the game has ended or reached the post-game/settled scoreboard;
- the screenshot timestamps are inside the correct game, not a neighboring game, replay, ad, intermission, or next series.

The database snapshot previously showed 173/174 games with per-game VOD. Revalidate this. Use a series broadcast only when per-game VOD is missing or inadequate, and retain the source-selection reason.

Do not fill a missing game boundary by splitting series duration evenly or by assuming each game begins at a fixed offset. Use the visible game transition and corroborating transcript/database evidence. If a screenshot does not show enough to distinguish game numbers, use additional frames or leave the game identity unresolved.

### VP-05 — Draft and hero identity where claims need visual proof

For draft-related claims that are not sufficiently established by the canonical database or where the data conflicts:

- capture the relevant draft screen(s);
- verify visible team side, selected/banned hero identity, order, and phase only when legible;
- distinguish a hero portrait from a similar skin/icon or an overlay graphic;
- capture both sides or enough of the draft sequence to establish order;
- do not infer draft intention, respect, comfort, or strategy solely from a pick/ban screenshot.

The database remains the primary source for structured draft rows when its integrity is established. Visual screenshots are corroboration or discrepancy-resolution evidence, not a reason to duplicate or casually overwrite canonical data.

### VP-06 — Scoreboard and game-state claims

For reports that quote or interpret visual game state, capture and review the relevant scoreboard/HUD screenshot(s), including where visible:

- game clock;
- team kill score;
- team gold;
- player gold and KDA;
- hero levels;
- items/build;
- towers/structures or objective overlays;
- team identity and side;
- current game versus replay/post-game state.

Every numeric value must be legible. If DeepSeek cannot reliably read a value, store it as unknown and do not use it in a derived claim. Cross-check readable values against database records when equivalent fields exist; record discrepancies rather than forcing a match.

### VP-07 — Objective events and structure conversion

For any claim about Turtle, Lord, turret, inhibitor/base, or other objective events:

- capture a temporally ordered screenshot sequence around the event;
- include the event banner/announcement or other direct UI marker where available;
- include enough before/after context to identify the match/game and distinguish a live objective from an old overlay, milestone, replay, or historical statistic;
- verify which team receives the objective only when directly observable;
- distinguish objective secure, objective attempt, objective presence, and later structure conversion.

A single screenshot showing a Lord milestone overlay, Lord on the map, or a caster mentioning Lord is not by itself proof of a current Lord kill. Existing pilot evidence already contains an example of a season milestone overlay that must not be mistaken for a current objective event.

### VP-08 — Teamfight, rotation, macro/meso/micro and mechanical claims

Capture screenshot sequences for candidate moments from all teams and a stratified set of games, including:

- rotations and lane assignments;
- jungle pathing and contested camps;
- Turtle/Lord setup and zoning;
- teamfight start, engagement, disengagement, and aftermath;
- split push and cross-map pressure;
- pickoffs, dives, sieges, defensive holds, and base defense;
- target selection and visible focus fire;
- positioning, spacing, grouping, and formation;
- skill/ultimate effects where they are visibly distinguishable;
- item/level power spikes when the HUD makes them legible;
- possible mispositioning, missed engage, overextension, or isolated player;
- claimed outplays, saves, escapes, and turning points.

Use multiple frames with timestamps. A static still cannot prove a full sequence such as a 1v3, a successful Lord secure, a rotation path, a mechanical combo, or the cause of a teamfight win. DeepSeek may verify bounded visible states (for example, which heroes are visible near a base at a clock time); it must not promote those into a causal narrative unless the screenshot sequence directly supports the full event.

Where screenshots cannot establish movement or temporal causality, mark the claim inconclusive or keep it transcript-only. Do not pretend that a collection of unrelated stills is a video.

### VP-09 — Player-level visual moments

For player dossiers and individual coaching claims that require visual proof:

- verify player/hero identity from visible HUD/name/roster context;
- verify the relevant game and time;
- capture enough frames to show the actual visible action/state;
- avoid attributing an action to a player when the HUD/hero identity is not legible;
- distinguish a visible successful action from the commentator's evaluation of it;
- do not infer player intent, communication, confidence, reaction time, or hidden information.

A player's season KDA, pick rate, or MVP count is database evidence, not screenshot evidence. Do not force screenshots into claims that are already adequately supported by structured statistics.

### VP-10 — Promotional overlays, replay context, and visual contamination

DeepSeek must identify and record:

- advertisements and YouTube promotional overlays;
- loading and waiting screens;
- scoreboard and draft screens;
- instant replay and replay labels;
- post-game player/caster cameras;
- sponsor graphics, lower thirds, and broadcast overlays;
- transitions and black/frozen frames;
- low resolution, compression, crop, motion blur, or UI obstruction.

Use a contamination flag and explain whether it prevents the target claim from being assessed. Never silently treat a promotional or post-game frame as gameplay evidence.

### VP-11 — Screenshot coverage for the full-season semantic sample

The wider goal requires a stratified season analysis, not three pilot series. Build a screenshot target plan that samples all nine teams, all relevant game lengths/outcomes, different weeks/patch periods, game-number positions, winning and losing sides, and a range of strategic situations.

The sample must be driven by explicit strata and report denominators. Do not claim screenshot coverage because every report file exists. Track:
- games with a verified identity/boundary;
- games with at least one usable DeepSeek-reviewed gameplay screenshot;
- games with reviewed target-event sequences;
- distinct teams, players, heroes, roles, game lengths, and patches represented;
- claims visually verified versus inconclusive/rejected.

Do not invent a universal minimum frame count per game. Define a defensible sampling plan based on target questions and cost/benefit, then record the actual counts.

### VP-12 — Screenshot-only limitations register

Maintain a clear register of visual questions that screenshots cannot prove reliably. At minimum consider:

- exact movement path between two points without adequate intermediate frames;
- reaction time and frame-perfect mechanics;
- hidden vision, information available to a player, or fog-of-war knowledge;
- team voice comms, intent, mental state, and shot-calling;
- causality ("this pick caused the win") from outcome screenshots;
- objective attribution when the event overlay/HUD is not visible;
- exact skill usage when effects/UI are obscured;
- continuous teamfight chronology when only sparse stills exist.

These are not failures of the DeepSeek reviewer. They are evidence limitations. Record them as not provable from available screenshots and do not publish them as verified.

---

## 7. Game-specific priority queue from known evidence gaps

Use live files to regenerate this queue; these are starting priorities, not a substitute for a full manifest.

1. **W6D1 / matches 1075, 1076, 1077:** all three series currently point to 2425 seconds and are only detected_pending_review. This is a likely collision caused by the heuristic. Capture frames around candidate starts and the whole relevant broadcast transitions to identify the actual three series.
2. **W7D2 / match 1086:** candidate 31928 seconds was previously described as likely wrong. Verify against visible team/game state and broadcast context.
3. **W8D2 / matches 1094, 1095, 1096:** candidates cluster at 1585, 1882, and 1884 seconds. Verify that they correspond to the correct separate series; do not accept timestamps solely because they are chronologically increasing.
4. **W1D1 / match 1037:** no start offset in the structured offset manifest despite its known pilot VOD. Locate and verify the series boundary.
5. **All series with null start_seconds:** use the live-generated target inventory to capture, review, and resolve or quarantine.
6. **All 72 series with null end_seconds:** derive/verify end boundaries where needed for reliable game segmentation; do not synthesize end time from a following match without visual evidence.
7. **All 174 games:** construct the individual game identity and boundary table, accounting for the current 173/174 per-game VOD availability snapshot.
8. **Legacy pilot frames:** re-review with DeepSeek before counting those old visual judgments as current model-backed evidence.
9. **Claims about Lord/Turtle/turret, 1v3, rotations, and turning points:** audit every existing claim and either attach an adequate ordered screenshot set, downgrade its evidence class, or remove the unsupported visual interpretation.

---

## 8. Integration with the existing semantic goal

The first-stage, non-vision-capable model should continue work that does not require image interpretation:

- reconcile the canonical database and report counts;
- fix the source/series/game offset schema and deterministic validators;
- build the manifest and candidate capture queues;
- implement screenshot capture, hashing, sidecars, and DeepSeek API scaffolding;
- build evidence schemas, cache, rate limits, retry controls, and tests;
- extract transcript-based candidate events and exact caption-aligned timestamps;
- add tests and documentation;
- ensure reports do not overstate visual proof.

It must leave visual targets explicitly pending DeepSeek and must not mark them as reviewed.

The DeepSeek vision phase then executes all visual targets in this file and writes the model-backed proof ledger. The overall semantic goal may proceed with non-visual evidence and clearly labeled limitations while this second phase is pending, but it must not claim completion of visual acceptance criteria.

When the DeepSeek phase finishes, reconcile this handoff with the parent semantic completion goal. Do not archive this goal until every required visual acceptance criterion below is actually satisfied or explicitly excluded with a documented, evidence-based reason that does not pretend visual proof exists.

---

## 9. Tests and audit requirements

Add deterministic offline tests for at least:

- DeepSeek request construction includes the exact image bytes or supported image URL and image hash;
- no text-only model can pass the vision capability check;
- model and prompt versions are present in every successful review record;
- malformed JSON, missing required fields, wrong enum, and invalid confidence are rejected;
- changed image hash invalidates cached review;
- changed model ID or prompt version invalidates cached review;
- frame actual time missing or outside tolerance cannot verify a timestamp-sensitive claim;
- team mismatch rejects the target;
- an unreadable scoreboard value remains unknown;
- an ad/promo frame cannot verify gameplay;
- a post-game frame cannot prove a live teamfight;
- a single still cannot verify a claimed sequence;
- sequence order and screenshot timestamps are preserved;
- more_screenshots_required triggers a bounded recapture plan;
- repeated inconclusive reviews terminate without human escalation;
- API errors, rate limits, and timeouts do not mark a target as reviewed;
- secrets are redacted from logs and output artifacts;
- ledger and manifest reconcile one-to-one;
- all report references resolve to a ledger record and the exact image hash.

Live DeepSeek calls should be separated from deterministic tests. Provide an optional smoke command that uses a known fixture screenshot and reports the exact configured model, but never makes a live network call part of the ordinary unit test suite.

---

## 10. Definition of done

This visual-proof goal is complete only when all conditions are true:

- [ ] A DeepSeek model that accepts images has been verified by an automated fixture test.
- [ ] The reviewer and prompt/schema versions are configurable, recorded, and reproducible.
- [ ] The legacy screenshot decisions have been preserved and independently re-reviewed by DeepSeek where the image files are available.
- [ ] A canonical manifest covers all 27 broadcast sources and 72 series, with reconciled statuses and explicit quarantine.
- [ ] Every series has either a DeepSeek-verified in-video identity/boundary or a documented non-verified/quarantined state.
- [ ] All 174 games have an individual identity/boundary status; no missing boundary is invented.
- [ ] Individual game VOD availability and fallback source selection are reconciled against the live database.
- [ ] Screenshot evidence is captured for all visual claims published by the semantic reports.
- [ ] Objective, scoreboard, draft, teamfight, macro/meso/micro, and player-moment claims use appropriately scoped screenshots or ordered screenshot sequences.
- [ ] Single-frame limitations and screenshot-only non-provable claims are explicitly handled.
- [ ] Every verified claim references a valid DeepSeek review, exact input hash, source, video, timestamp, and screenshot ID.
- [ ] An inconclusive/rejected result is never published as verified.
- [ ] No human visual-review step or human-review queue exists.
- [ ] Automated tests prove fail-closed, cache, provenance, retry, and report-reference behavior.
- [ ] Coverage reports count actual DeepSeek-reviewed targets and do not equate screenshot capture with proof.
- [ ] Raw screenshots and credentials remain protected according to repository policy.
- [ ] Relevant project verification passes, and documentation accurately reflects the resulting coverage.

If any criterion is not met, keep the goal active and report the exact remaining target counts. A goal is not complete merely because the DeepSeek integration exists; the required screenshot targets must actually be captured and reviewed.

## 11. Suggested execution command

Run this goal in the second phase, using an OpenCode setup configured with the DeepSeek vision model:

    /goal @docs/goals/active/mpl-s18-visual-proof-deepseek-handoff.md

Before execution, inspect the live branch and worktree, read AGENTS.md and the parent semantic-analysis goal, and regenerate every count and target list from the current structured artifacts. Preserve unrelated local changes.
