# Berliandro's Eye — Transcript-Powered Coaching Intelligence

## Project brief for a future continuation

**Project:** Berliandro's Eye — MPL Indonesia Season 18  
**Repository:** https://github.com/berliandro/berliandros-eye-mpl-s18  
**Current source material:** Transcripts from all nine weeks of YouTube live broadcasts, already fetched using the user's app; approximately **9.23 MB of text**.  
**Status:** Idea and architecture brief only. This document does not claim that the analysis pipeline, schema, reports, or audit tooling have been implemented.

---

## 1. Vision

Turn Berliandro's Eye from a statistics dashboard into an **auditable, transcript-powered esports coaching intelligence system**.

The system should go beyond describing what happened in MPL Indonesia Season 18. It should help a coach investigate why a team may have won or lost, identify repeated tactical patterns, study player and team tendencies, evaluate draft decisions, and generate hypotheses worth testing in scrims.

The defining principle is:

> **Every meaningful AI-generated insight must be traceable to source evidence, and a user must be able to challenge that insight and ask the agent to show its proof.**

The AI must not ask the coach to trust polished prose. It should expose the exact transcript quotations, corresponding broadcast moments, related gameplay evidence where available, supporting statistics, counterexamples, reasoning, and uncertainty.

This is intended as a project to return to in the future, possibly after a long pause. Start with the smallest reliable foundation and expand only after its evidence quality has been demonstrated.

## 2. Core idea: raw sources, existing data, evidence, and insights

Keep four distinct layers so that original material and observed facts are never silently overwritten by interpretation. Transcript evidence and the app's existing structured match database are complementary sources: the transcript can capture what commentators noticed or said, while the database can answer structured questions about recorded matches, players, heroes, scoreboards, and other fields it actually contains.

### Layer A — Immutable raw transcripts and source metadata

Preserve the original transcripts as fetched. Do not rewrite, normalize in place, or replace them with summaries. Store metadata describing each source video and its relationship to week, series, and game where known.

The corpus should remain searchable even after the AI-generated reports are created. If a report becomes questionable, the agent must be able to retrieve the original transcript and the passages around the citation.

If timestamps are included in the transcripts, preserve them. If they are absent or unreliable, record that limitation and derive or verify timestamps only using an explicit, reproducible method. **Never invent a timestamp or fabricate a direct quotation.**

### Layer B — Existing structured match database

Treat the data already fetched for Berliandro's Eye as a first-class evidence source, not merely as background context. Before designing new storage, inspect the current SQLite schema, CSV exports, data provenance, identifiers, and the fields that are genuinely available. Reuse those records rather than re-fetching or re-extracting information the project already has.

The structured data can help answer questions such as:

- Which heroes were picked or banned, in what match/game, and by which team, if those fields are present?
- What were the recorded game results, player/hero lineups, kills, deaths, assists, gold, duration, or other available scoreboard fields?
- How do a team's objective or match outcomes compare across its games, where reliable data exists?
- Does a commentator's statement match the recorded result, pick/ban, player, or other structured value?
- Is an apparent transcript pattern consistent with a wider sample of games, and are there counterexamples?

Do not assume a field exists just because it would be useful. Inspect actual schemas and coverage first. Distinguish authoritative/source-reported values from app-derived or heuristic values. For example, the existing README documents game MVP as a highest-KDA-on-the-winning-team heuristic because the API does not supply game MVP; MANIAC/SAVAGE are unavailable rather than fabricated. Such fields must not be presented as official measurements.

Every database-derived citation should be reproducible and traceable. Retain, where applicable:

- Database/snapshot identifier or fingerprint and its version/date.
- Table or view, stable match/game/player identifiers, and the exact fields used.
- The query or a versioned query template, including parameters needed to reproduce it.
- Returned values, units, sample size, filters, and any excluded/missing rows.
- Data lineage/provenance: source-reported, computed, heuristic, or AI-inferred.
- Known coverage gaps, stale-data caveats, and schema version.

If a metric is computed from database rows, save its formula or calculation version. A report should be able to show not just “the database says so,” but which records and calculation produced the number. Avoid copying large query results into every Markdown file; store the evidence record and a concise reproducible reference instead.

### Layer C — Structured evidence records

Create a common machine-readable evidence layer that can reference both transcript passages and database facts. Each record should retain:

- A stable evidence ID.
- Evidence source type: transcript, database query/result, gameplay review, external source, or a combination.
- Source video ID/title/YouTube URL, week, series, game, and verified timestamp/range where relevant.
- Exact transcript quotation and source segment/file location when transcript-derived.
- Database snapshot, table/view, row identifiers, field names, query/calculation version, values, and provenance when database-derived.
- Speaker/caster identity if known, not guessed.
- Event/topic categories and linked teams, players, heroes, and objectives where supported.
- Verification state, uncertainty, sample scope, and known limitations.
- Extraction model/prompt/schema versions when relevant for reproducibility.

Structured records are the common source of truth for reports and audits. Do not rely on prose files as the only storage for evidence. Preserve the distinction between evidence sources: two claims are not necessarily independent corroboration if both originate from the same underlying feed or data provider.

### Layer D — Insights and reports

Generate individual-game timelines, team/player/hero/draft reports, meta summaries, and coaching briefs from the validated evidence layer. Use transcripts and the match database together when relevant, while being explicit about what each source can and cannot establish.

Every important claim in these reports should cite one or more stable evidence IDs. The Markdown presentation may use locally numbered references such as `[1]`, `[2]`, but those numbers must map back to stable source/evidence IDs so that regenerated files remain traceable even if numbering changes. A reference may link to a timestamped broadcast, an exact transcript span, a reproducible database query/result, or multiple complementary sources.

---

## 3. The reference style the user wants

An insight should be readable like a scouting note, with numbered citations inline and a reference section at the end.

### Illustrative example only — not a factual claim about a real player

> A player appeared to react late to a flank in this engagement. The commentator described the player as being caught off guard, but the transcript alone cannot establish whether this was slow mechanical reaction, poor positioning, or a lack of information. [1][2]

**References**

[1] YouTube broadcast link at the relevant verified timestamp. Include the exact commentator quotation, week, series, game, and transcript location.  
[2] Corresponding gameplay evidence, with a timestamp or clip where the threat becomes observable, the player's response, and the outcome can be reviewed. State whether the video was actually visually inspected.  
[3] Database-backed comparison, if relevant: identify the dataset snapshot, match/game IDs, fields or query, filters, sample size, and whether the values are directly sourced or derived. Do not imply that ordinary scoreboard fields prove a mechanical reaction-time claim if they cannot measure reaction time.

For cross-season or repeated-pattern claims, include additional references to comparable earlier games and explain the comparison method.

A cited transcript proves that the commentator said something. It does **not**, by itself, prove the commentator's interpretation was correct. Footage or independent game data may be needed to verify gameplay events. A claim such as “reaction time declined from the previous season” requires comparable footage or reliable observations from both periods, similar criteria, and an explicit sample size; one memorable event is insufficient.

## 4. Evidence and confidence rules

Keep these two questions separate:

1. **What kind of evidence is this?**
2. **How far has the evidence been verified?**

Suggested evidence types:

- **Transcript statement:** A direct statement in the source, quoted accurately.
- **Commentator interpretation:** An opinion or explanation expressed by a caster. Attribute it to the caster; do not automatically turn it into fact.
- **Database-record evidence:** A value directly present in an identified database row/field, with dataset version and provenance retained.
- **Derived-stat evidence:** A reproducible calculation from identified database rows, with formula, filters, and sample size recorded. Mark heuristics as heuristics rather than official statistics.
- **Gameplay observation:** An observation made by reviewing the corresponding video.
- **Analytical inference:** A conclusion synthesized from multiple observations. Label the reasoning and alternatives explicitly.

Suggested verification states:

- **Unverified:** Extracted but not checked against source context.
- **Transcript-verified:** The quotation exists in the source and the citation points to the right passage.
- **Gameplay-verified:** The relevant visual event has been reviewed in the footage.
- **Cross-checked:** Supporting structured data or independent comparable evidence has been examined.
- **Partially supported:** Some elements are supported, but the full claim goes further than the evidence.
- **Contradicted:** Evidence materially conflicts with the claim.
- **Inconclusive:** Available material cannot determine whether the claim is right.

These labels are not interchangeable. For example, a line may be transcript-verified while the commentator's interpretation remains unverified.

For important inferences, include:

- Evidence supporting the claim.
- Evidence that challenges it or plausible counterexamples.
- Alternative explanations.
- Sample size and scope (one moment vs. repeated matches).
- What evidence would confirm or refute the hypothesis.
- A practical coaching question or action, where useful.

Avoid false precision. Do not invent numeric confidence percentages unless a calibrated, tested methodology exists. A qualitative label with transparent reasoning is preferable.

## 5. What to extract from the transcripts

The taxonomy should be fixed and documented so that different model runs use consistent categories.

### Objectives and map state

- Turtle and Lord mentions, attempts, contests, secure/steal outcomes, trades, setup, post-objective conversion, and failed attempts.
- Lane pressure, rotations, river control, invasions, siege, high-ground defense, map trades, tempo, and wave management when the source supports it.
- Distinguish a secured objective from a spawn, threat, setup, contest, attempted steal, or hypothetical discussion. A transcript mention alone is not a complete or authoritative objective count.

### Draft and composition

- Pick/ban sequence and order, heroes, role/flex possibilities, comfort picks, possible counterpicks, composition archetypes, synergies, and likely win conditions.
- **Respect-ban hypotheses:** Explore whether a ban may reflect a particular player's demonstrated proficiency, an opposing team's strategy, a composition matchup, or another plausible reason. A ban alone cannot prove the coach's intention.
- Compare draft intent as a hypothesis with observed execution. Label inferred intent as inference unless supported by explicit commentary or other reliable evidence.

### Micro — moment-to-moment execution

- Mechanical outplays, combos, dodges, target selection, initiation, peel, counter-engage, disengage, survival, and clutch moments.
- “Fast hands” or reaction-time claims require video review or comparable evidence; energetic commentary is not enough to establish mechanical speed.

### Meso — local tactical coordination

- Rotations, ganks, jungle invasions, lane pressure, grouping, timing, setup before objectives, skirmishes, and local numbers advantages.
- Possible coordination gaps, isolated players, missing follow-up, or conflicting movements. Call these **possible coordination breakdowns**, not proven miscommunication, unless direct evidence establishes communication intent or content.

### Macro — whole-map and strategic decisions

- Trading objectives, tempo, side-lane pressure, resource allocation, scaling, siege, map control, playing from behind, recovery, closing games, and high-ground defense.
- Risk/reward tradeoffs, overextension, questionable calls, throw/blunder hypotheses, and failure to convert an advantage.

### Key and notable moments

- Fight or game turning points, decisive mistakes, comeback opportunities, objective flips, clutch plays, epic moments, and notable individual contributions.
- Distinguish “the commentator called this a key moment” from “the system judges this to be a key moment.” Explain system-generated rankings using observed consequences rather than hype words alone.

### Team, player, hero, patch, and meta trends

- Repeated team tendencies and apparent win conditions.
- Player tendencies when supported by multiple comparable observations.
- Hero-specific strengths, weaknesses, composition relationships, pick/ban context, and observed game patterns.
- Patch-specific patterns, with findings partitioned by patch/version where possible. Do not combine games from materially different patches without noting the limitation.
- Cross-week changes and cross-season comparisons only when the relevant comparable sources exist.

---

## 6. Suggested output structure

These are generated reports, not all hand-written source files. Start with a manageable subset, then expand based on real usefulness.

```text
analysis/
├── README.md
├── index.md
├── sources/
│   └── source-manifest.json
├── evidence/
│   ├── evidence-schema.json
│   ├── evidence-ledger.jsonl   # or canonical SQLite evidence database
│   ├── database-snapshot-manifest.json
│   ├── query-catalog/           # versioned, reusable analysis queries (if needed)
│   └── audit-log.jsonl
├── matches/
│   └── <series-id>.md
├── games/
│   └── <series-id>-game-<n>.md
├── teams/
│   └── <team-id>.md
├── players/
│   └── <player-id>.md
├── heroes/
│   └── <hero-id>.md
├── drafts/
│   ├── <series-id>.md
│   └── team-draft-meta.md
├── systems/
│   ├── micro.md
│   ├── meso.md
│   ├── macro.md
│   ├── objective-control.md
│   └── teamfights.md
├── patches/
│   └── <patch-id>.md
├── meta/
│   └── season-trends.md
└── coaching/
    ├── head-coach-brief.md
    ├── opponent-scouting.md
    └── recurring-patterns.md
```

Use canonical IDs and metadata in the structured layer; readable names can be used in Markdown. Do not create a huge set of empty or low-value reports just because they fit this tree. `analysis/index.md` should navigate to reports and state their coverage/last-generated version.

### Match/game reports

Create a timestamped chronological event timeline, relevant quotations, notable plays and objectives, draft context, evidence references, and unresolved questions.

### Team/player reports

Summarize patterns across multiple games; link every material tendency to examples and identify counterexamples. Avoid judging a player from one isolated clip.

### Hero/draft/meta reports

Track draft order, pick/ban patterns, hero combinations, composition hypotheses, patch context, and source-backed reasons. Keep explicit statistics separate from interpretations.

### Coaching briefs

Summarize high-value, evidence-backed preparation points: what to watch for, possible punishable patterns, promising responses to test, supporting examples, counterexamples, confidence/limitations, and recommended follow-up review.

---

## 7. How the audit feature should work

A user should be able to select an insight or ask the agent in natural language, for example:

> **“Audit insight INS-TEAM-A-0042. Show me the proof.”**

The audit workflow should:

1. Retrieve the exact insight and every evidence record it cites.
2. Load the immutable original transcript segments, including context before and after each quoted passage.
3. Check that quoted text matches the source and that its citation metadata is internally consistent.
4. Verify the YouTube link and timestamp if available; report missing or unreliable timestamps rather than guessing.
5. Search the raw transcript corpus for related passages and potential counterexamples.
6. Query the existing match database when relevant. Trace every database-derived value to a reproducible query/calculation and the underlying match/game/player rows; check whether the field is source-reported, computed, heuristic, or inferred.
7. Compare transcript statements with the database where the two sources overlap. Report agreement, discrepancy, missing coverage, and whether the sources are genuinely independent.
8. Open the corresponding video/clip for visual review when the environment supports it. Clearly distinguish actually inspected footage from a link that was merely generated or opened.
9. Separate direct source facts, commentator opinions, database facts, derived statistics, gameplay observations, and AI inferences.
10. Return one of: **supported, partially supported, contradicted, or inconclusive**.
11. Show the exact evidence, reasoning, alternative explanations, query/filter details, and limitations behind the verdict.
12. Log the audit result and which sources were examined without modifying the original transcript, source database, or silently overwriting the original insight.

An audit can produce a suggested correction or a new insight version, but it should preserve the historical record of what was previously claimed and why it changed.

### Example audit prompt

```text
Audit insight <INSIGHT_ID>.

- Retrieve every cited evidence record and the original transcript context.
- Verify quotations, source IDs, timestamps, and video links.
- Search the raw corpus for corroborating passages and counterexamples.
- Query the existing match database when relevant; show the exact rows/fields or reproducible query/calculation, filters, sample size, and data provenance.
- Compare transcript statements with database values where they overlap. Flag discrepancies and do not pretend sources are independent if they share the same underlying data feed.
- Inspect relevant footage when available, and state explicitly whether it was visually reviewed or merely linked.
- Separate commentator statements, database-recorded facts, computed/heuristic metrics, gameplay observations, and AI inferences.
- Decide whether the insight is supported, partially supported, contradicted, or inconclusive.
- Show the evidence and reasoning, including the strongest counterargument and any data or coverage limitations.
- Do not invent evidence, timestamps, quotes, rows, metrics, or missing context.
- Do not edit source transcripts or the existing match database. Suggest any correction as a separate versioned change.
```

---

## 8. Processing transcripts and existing database data efficiently and reproducibly

Do **not** feed all transcripts to one agent prompt and ask for every report at once. Do not make the agent keep the entire corpus in working context. The existing MPL database is a major advantage: use it for structured queries, cross-checks, and repeatable calculations instead of asking an LLM to infer numeric facts from commentary.

Build a repeatable local processing pipeline:

1. **Inventory transcripts:** List every transcript file, size, week, video URL/ID, existing timestamps, match/game mapping, encoding, and missing metadata. Record checksums so source changes can be detected.
2. **Inventory the existing database:** Inspect SQLite schemas, CSV exports, stable IDs, row coverage, update dates, source lineage, calculations/heuristics, and relationships to teams, series, games, players, heroes, bans, items, and other fields actually present. Do not assume a field exists before checking.
3. **Preserve sources:** Keep raw transcripts read-only and separate from generated outputs. Treat the current database and CSV exports as read-only inputs unless a separate, explicitly approved migration is designed. Do not overwrite or rebuild them as a side effect of analysis.
4. **Normalize as derived copies:** Standardize transcript line endings/whitespace and metadata without replacing raw files. Preserve offsets or source-line references where possible. Normalize database identifiers through explicit, tested mappings rather than fuzzy guesses.
5. **Segment and link:** Split transcripts by match/game boundaries or natural transcript sections. Link segments to database series/game IDs only when source metadata or deterministic matching supports the relationship; otherwise mark the mapping as uncertain.
6. **Extract atomic records:** Process transcript chunks into structured events that conform to a fixed schema. Require an exact source span for transcript-derived claims. For database-derived claims, retain the source rows/fields and query or formula that produced the result.
7. **Validate:** Reject malformed model outputs, unknown IDs, missing provenance, quotations not found in source, impossible timestamps, invalid categories, invalid joins, and values that cannot be traced to known rows or calculations. Record failed jobs for retry.
8. **Query and cross-check:** Use deterministic queries for questions such as team pick/ban patterns, player or hero performance, game outcomes, and recurring statistics, but only where the actual database fields support the calculation. Store filters, sample size, missing-data handling, and formula/query version. Compare with transcript statements when the two sources overlap.
9. **Search for counterexamples:** Use both corpus search and structured database queries to find games or observations that challenge a proposed pattern. Avoid cherry-picking only the games that support the initial hypothesis.
10. **Deduplicate and reconcile:** Use source segment, event/topic, entity IDs, time window, and explicit deterministic rules. Preserve distinct events. When the transcript and database disagree, flag the discrepancy and inspect data lineage instead of silently choosing the version that agrees with the AI.
11. **Synthesize:** Build cross-game insights from validated evidence records. Separate descriptive database results from commentary interpretation and AI inference. Do not turn correlation into causation or a small sample into a reliable trend.
12. **Render Markdown:** Generate reports and numbered references from structured records. A reference should resolve to an exact transcript span, timestamped video, reproducible database query/result, or a combination of those sources.
13. **Resume safely:** Persist progress per chunk/batch, use idempotent jobs, record model/prompt/schema/query versions, and avoid reprocessing successful material unnecessarily.
14. **Audit samples:** Review representative events and database-backed claims manually before scaling. Measure quote fidelity, source-row traceability, query reproducibility, transcript-to-game mapping accuracy, reference integrity, duplicate rate, and whether inferences are appropriately labeled.

### Choosing the evidence store

SQLite is a strong fit if the system needs joins between evidence, matches, players, teams, heroes, and audit history. JSONL is easy to inspect and diff and can work well for append-oriented evidence exports. The existing match database can remain the authoritative source for the app's collected match data, while a **separate evidence database or evidence schema** stores transcript segments, citations, extracted events, insight records, and audit logs. Do not casually modify the production/app database or create multiple competing sources of truth.

The model/API provider should be configurable so extraction can use an affordable model and harder cross-match synthesis can use a stronger model if the pilot demonstrates value. Keep extraction schemas, database queries, and validation independent of any one provider.

---

## 9. Recommended implementation phases

### Phase 0 — Re-entry and corpus audit

- Inspect the current repository, branch, worktree, and build pipeline before changing anything.
- Find where the 9.23 MB transcripts currently live; do not assume a path.
- Inventory files, source links, timestamps, match boundaries, week coverage, and metadata quality.
- Identify what the current match database already knows and what the transcripts could add.
- Verify the lineage and reliability of important fields, including whether values are direct source data, calculations, or heuristics.
- Avoid changing the existing app, source database, or ETL pipeline during initial research.

**Deliverable:** Transcript inventory, database/schema inventory, source-lineage notes, and a short gap report.

### Phase 1 — Schema and source manifest

- Define versioned schemas for sources, transcript segments, database snapshots/records, observations, insights, references, and audit results.
- Establish stable source/evidence IDs, database row/query provenance, deterministic cross-source links, and quotation fidelity rules.
- Define data-lineage labels for source-reported, computed, heuristic, and AI-inferred values.
- Create validators and a small test fixture corpus, including mismatched transcript/database cases.
- Decide whether SQLite or JSONL is the canonical evidence store; avoid maintaining competing sources of truth.

**Deliverable:** Validated schema, source manifest, and deterministic tests.

### Phase 2 — Pilot on two or three representative series

- Choose matches with clear objective sequences, draft discussion, teamfights, and varied commentary.
- Extract a limited taxonomy first: objectives, draft, teamfight events, and explicit commentary interpretations.
- Generate concise match/game Markdown with exact citations.
- Ask the agent to audit several insights, including at least one weak or misleading claim.
- Manually inspect evidence quality, links, timestamps, duplicates, and unsupported inferences.

**Gate:** Do not scale to all nine weeks until the pilot is sufficiently traceable and useful.

### Phase 3 — Audit workflow

- Implement the “audit this insight” operation using stable IDs.
- Retrieve source context and counterexamples from the raw corpus.
- Compare claims with available match data and video when possible.
- Produce a verdict, evidence trail, alternatives, and limitations without silently altering the report.

**Deliverable:** Repeatable audit prompt/command with regression cases.

### Phase 4 — Batch extraction across all nine weeks

- Run resumable, deterministic batches.
- Track coverage and failures by source and game.
- Validate every output before marking it complete.
- Reconcile transcript-derived observations with structured match/game metadata.

**Deliverable:** Full evidence corpus with a coverage and quality report.

### Phase 5 — Generated scouting and coaching reports

Generate, where coverage supports them:

- Individual series/game reports.
- Team and player scouting reports.
- Hero and draft reports.
- Micro, meso, macro, teamfight, and objective-control summaries.
- Patch/meta trends.
- Recurring patterns, opponent scouting, and a head-coach brief.

Every material claim should cite evidence. Include counterexamples and distinguish one-off moments from recurring patterns.

### Phase 6 — Optional integration with the web app

Only after the pipeline proves useful and trustworthy, consider integrating evidence links into Berliandro's Eye. Possible features include clickable insight citations, source/game jump links, an audit panel, and filters by team/player/hero/patch. Keep transcript processing/report generation separate from the existing single-file app at first so a research pipeline cannot accidentally destabilize the working dashboard.

---

## 10. Quality gates and tests

At minimum, test that:

- Every report claim requiring evidence has one or more valid stable references.
- Every quoted passage exactly matches the raw source after only documented normalization.
- Every source ID maps to an existing source and every transcript segment maps to a real file/range.
- Every database reference resolves to the expected snapshot, table/view, rows/fields, and reproducible query or formula.
- Derived metrics reproduce from the documented filters and sample; heuristic/app-generated fields are never mislabeled as official source data.
- Transcript-to-match/game joins use validated identifiers and visibly flag ambiguous or unsupported mappings.
- A timestamp is marked verified only if a reproducible check supports it.
- Missing timestamps remain missing; no invented YouTube links are accepted.
- An insight's status never upgrades from transcript-verified to gameplay-verified without visual inspection evidence.
- The same source and configuration produce deterministic IDs and stable outputs where intended.
- Re-running a batch does not duplicate evidence or corrupt prior results.
- Unknown entities/categories and malformed model responses are rejected or quarantined.
- Reports separate direct observations, commentary interpretations, structured facts, and AI hypotheses.
- Counterexamples and patch/sample-size limitations are represented where relevant.
- Auditing an insight retrieves the correct source records and reports missing evidence honestly.
- Failed extraction/audit jobs are logged and can resume without rebuilding successful work.

Track coverage explicitly. A report should say whether it is based on all nine weeks, a subset of games, only transcript references, or visually verified footage. “Not mentioned in transcript” must not be treated as “did not happen in the game.”

---

## 11. Practical constraints and guardrails

- Keep raw transcripts unchanged. Generated artifacts belong in a separate directory.
- Do not overwrite the existing MPL dashboard, SQLite database, or CSV exports as a side effect of the new analysis pipeline. Treat current app data as a read-only input unless a separate, explicitly approved migration is designed.
- Do not assume transcript extraction is complete or free from speech-recognition errors.
- Do not treat database fields as ground truth without checking data lineage, freshness, completeness, and whether the values are official, computed, or heuristic.
- Do not call transcript and database records independent corroboration if they derive from the same original feed; document shared lineage where known.
- Do not derive definitive objective counts, precise reaction speed, unseen team communications, player intention, or mechanical execution from commentator language alone.
- Do not label a ban as a proven “respect ban” without supporting evidence; report plausible explanations.
- Do not infer a longitudinal trend from a single event or compare players across patches without noting differences.
- Do not have a model invent quotes, source links, timestamps, events, match IDs, or statistics. Missing data must remain missing and be reported.
- Preserve the distinction between “the commentator said X” and “X happened.”
- Keep an audit trail for model and prompt versions; regenerate reports when extraction logic changes.
- Do not add all raw transcripts or copyrighted source content to a public repository without consciously reviewing whether publication is appropriate.

---

## 12. The end-state experience

A coach reads a report and sees a statement with a citation. The coach can click the source link or ask the agent to audit the insight. The agent retrieves the raw transcript and its context, validates the quotation, searches other weeks for supporting and contradicting examples, checks relevant match data, and opens footage for review where available. It then explains whether the insight is supported, partially supported, contradicted, or inconclusive, showing the proof and limitations.

The agent can draw on both the raw transcript corpus and the existing Berliandro's Eye match database. It can find what commentators said, query recorded match/game/player data, compute repeatable statistics, cross-check overlapping facts, and surface contradictions or counterexamples. Database-backed claims include traceable rows and calculations; transcript-backed claims include the original passage and timestamp where verified.

The system does not simply return an answer. It returns an answer with an evidence trail the coach can inspect and challenge.

## 13. First action when returning to this project

Do not begin by asking an agent to produce every Markdown report.

Start with **Phase 0: inventory the raw transcript corpus and inspect the current repository**. Then design the schema and pilot the extraction/audit loop on two or three series. Only scale up after quotations, references, category labels, and audits pass real inspection.

The first milestone is successful when the system can generate one useful claim, link it to exact raw-source evidence, and survive a skeptical audit without inventing or overstating anything.
