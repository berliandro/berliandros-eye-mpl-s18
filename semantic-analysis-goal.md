# Goal: Achieve Full Traceable, Transcript-Powered Semantic Coaching Intelligence

This goal is to take the MPL ID S18 semantic analysis from "infrastructure complete" to a fully traceable, transcript-powered coaching intelligence system where every claim can be traced back to verified sources with exact timestamps and database cross-references.

## Objective
Transform the pilot semantic analysis into a scalable, auditable coaching brief engine covering the full season while maintaining strict citation discipline and provenance for all claims.

## Prerequisites (Already Complete)
- [x] All 27 broadcast sources mapped to verified official MPL Indonesia VODs (27/27 metadata verified)
- [x] Caption alignment complete for 26/27 sources (1 partial quarantined)
- [x] Winner orientation migration applied and verified (21/72 rows fixed, 0/72 mismatches)
- [x] Pilot evidence ledger established (3 series, 18 observations, 3 insights, 1 audit)
- [x] Robust alignment tooling with monotonic matching
- [x] Basic citation gating in build_segment

## Phase 1: Citation Discipline & Policy (Tighten The Guardrails)
Enforce the "only cite what is verifiably timestampable" rule.

- [ ] **Enforce gate everywhere**: Apply citation gate checks to any code path that generates `timestamp_link` (e.g., search, CLI helpers, ledger builders). Prevent quarantined sources from ever producing a `t=` link.
- [ ] **Formalize `src-s18-w09d02` policy**: Enforce quarantined status in all tooling with explicit rejection messages. Keep permanently quarantined unless a clear, verifiable path appears that can make it full-line aligned without guessing.
- [ ] **Add tests for citation gating**: Add unit tests to `tools/test_transcript_evidence.py` asserting quarantined/partial sources are rejected when attempting to build timestamped segments.

## Phase 2: Game-Level Mapping (Biggest Blocker)
Map broadcasts to individual series and games within multi-hour VODs.

- [ ] **Create schema for game offsets**: Create `analysis/evidence/game-offsets.json` with fields: `source_id`, `series_id`, `match_detail_id`, `game_no`, `start_seconds`, `end_seconds`, `confidence` (high/med/low), `provenance`, `method` (schedule/caster/scoreboard/frames/manual), and `verified_by`.
- [ ] **Infer offsets from data**: Leverage `schedule_all`, `matches`, `games`, `team_games` and raw transcript to infer start points. Look for caster intros, team name pairings, "Game X", draft/ban mentions, scoreboard callouts, and series transitions.
- [ ] **Integrate with `tools/video_frames.py`**: For ambiguous boundaries, pull frames around candidate timestamps to validate (loading screens, scoreboard, draft, hero select). Only use frames to confirm, never guess blindly. Reject promo frames as proof.
- [ ] **Build a validator**: Create validation ensuring offsets don't overlap invalidly, align to known series for that broadcast date, every offset has provenance, and cross-reference against DB.
- [ ] **Flag uncertain series for approval**: Anything with low confidence tagged for review with evidence shortlist for user approval before use in ledger.

## Phase 3: Boundary Detection & Series Segmentation
Turn broadcast-level alignment into game-level citations.

- [ ] **Heuristic boundary detection**: Implement detection based on caster transitions, series name calls, "next game/series", map changes, scoreboard resets, and gaps in relevant discussion.
- [ ] **Correlate with DB**: Use `schedule_all` to know expected order of series per broadcast date. Expected sequence is strongest constraint for multi-series days.
- [ ] **Create audit trail**: Every detected boundary needs a reason with provenance. If heuristic-only, must be marked low confidence.
- [ ] **Regression coverage**: Add tests to prevent breaking known series (1036/1037 on W1D1, 1107 on W9D3).

## Phase 4: Expand The Evidence Ledger (Scale Past Pilot)
Expand while maintaining rigor.

- [ ] **Stratified expansion plan**: Pick diverse sample (different teams, regular season/playoffs, stomp vs close games, comebacks) to validate fidelity before full season.
- [ ] **Systematize visual evidence**: Tightly integrate `tools/video_frames.py` into ledger. Every frame needs purpose, verdict (used/rejected), rejection reason. Tie to observation/segment.
- [ ] **Generate observations with full provenance**: For each new series, create segments with exact quote spans, timestamps (only from verified+fully aligned sources), DB cross-references, visual evidence where applicable.
- [ ] **Build audits for turning points**: For "turning point" claims, require supporting evidence (quote + context + DB state where possible). Enforce same audit structure as pilot.
- [ ] **Ledger validation**: Run `build` and `validate` after every batch, ensuring schema compliance and no citations from quarantined/partial sources.

## Phase 5: Tooling, Tests, Docs & Finalization
Polish and make reproducible.

- [ ] **Resolver regression tests**: Add tests for stale manifests, partial failures, conflicting candidates, already-verified metadata, and report/manifest reconciliation.
- [ ] **Harden `tools/analysis_inventory.py`**: Ensure correct reporting of partial vs fully aligned counts and surfaces citation policy.
- [ ] **Codify "how to add a series" workflow**: Add concrete checklist to `analysis/README.md` (resolve source → confirm citation-ready → map offsets → detect boundaries → extract quotes → add frames → cross-ref DB → audit → build+validate).
- [ ] **Update remaining docs**: Sweep for stale phrasing.
- [ ] **Commit and push**: Commit all changes and push to origin.
- [ ] **Update PR #1 description**: Update PR to reflect migration, source resolution, alignment, policy, and next steps.

## Execution Order
1. Lock down citations (Phase 1)
2. Build offset infrastructure (Phase 2)
3. Detect boundaries (Phase 3)
4. Validate pilot against new system (ensure 3 pilot series still validate)
5. Expand selectively in stratified batches
6. Finalize (Phase 5)

## Constraints & Guardrails
- **Citation discipline**: Only fully aligned, non-quarantined sources may produce timestamp links
- **Provenance required**: Every offset, boundary, claim must have method/provenance
- **No guessing**: Ambiguous cases flagged for approval, not guessed
- **Local-only artifacts**: Raw transcripts, media, cookies, caches remain Git-ignored
- **Evidence-first**: Claims need supporting quotes/frames/DB evidence
- **Distinguish fact from heuristic**: Be explicit about confidence levels
