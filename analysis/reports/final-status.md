# MPL S18 — final status

**Date:** 2026-11-14
**Database snapshot:** `mpl-s18-db-20c5ea2c51f3` (`20c5ea2c51f30d1a24cd2ce6927f0d182b47f951ebd8209f1aaef429941cf2ef`)
**Canonical coverage:** [`coverage-matrix.md`](coverage-matrix.md)

## Delivered

| Deliverable | Evidence |
|---|---|
| 72/72 match reports with database evidence | Every report has one `<!-- db-evidence:start -->` block with game result, team totals, player lines, picks, bans and transcript status. `tools/build_match_evidence.py --check` reports 0 changes. |
| Honest no-transcript status | 45 reports say `Transcript coverage: none`; 27 carry transcript sections (24 complete, 3 partial). |
| Game transcript availability | 107/107 game VODs fetched in Indonesian; 45/45 missing matches have full game-transcript coverage. |
| Canonical evidence store | `analysis/evidence/canonical-store.json` + [`evidence-store.md`](evidence-store.md): transcript ledgers canonical, pilot ledger frozen, 0 duplicate IDs. |
| League synthesis | [`league-meta.md`](league-meta.md) + [`league-data.md`](league-data.md) + `analysis/evidence/league-aggregates.json`. |
| Team synthesis | 9/9 team pages contain `## Evidence-backed profile` with season splits, transcript evidence, counterexamples and limits. |
| Hero synthesis | 94 hero pages contain `## Evidence-backed profile`; [`hero-meta.md`](hero-meta.md) covers the full 93-hero pool. |
| Strategy synthesis | 6/6 strategy pages contain `## Evidence-backed analysis` (draft, objectives, macro-map, micro, patch-meta, index). |
| Coaching product | 9 team briefs in `analysis/coaching/teams/` plus [`head-coach-brief.md`](../coaching/head-coach-brief.md). |
| Visual proof resolved honestly | 966 frames and 62 boundary reviews audited: 0 `visible_00_00`, 0 same-frame pairing. Gate stays unmet; blocker recorded in the handoff §8.27. |
| Docs reconciled | `analysis/index.md`, `README.md`, `analysis/reports/coverage-summary.md` no longer report the old 3/72 pilot state. |

## Coverage numbers

- 72 series, 174 games, 9 teams, 66 players, 1,740 picks, 1,738 bans.
- 27 transcript sources: 24 complete, 3 partial (`src-s18-w02d03`, `src-s18-w07d03`, `src-s18-w08d02`).
- 368 transcript rows: 313 accepted, 50 rejected, 5 resolved.
- 107 game transcripts fetched from 107 game VODs (all Indonesian); the 7 IP-blocked games were recovered through the Invidious fallback.
- Game-VOD pilot: 1037 has 6 accepted observations (G1: 4, G2: 2), validator 0 errors/0 warnings.
- 173/174 games have a VOD link; 153/174 have a map mode.
- 0 visual boundaries verified: 41 context-only, 20 rejected, 1 inconclusive, 10 waived.

## Validation commands

```text
python tools/verify.py
python tools/ci_semantic_check.py
python tools/validate_game_offsets.py
python tools/build_match_evidence.py --check
python tools/build_coverage_matrix.py
python tools/build_canonical_store.py
python -m unittest tools/test_stats_query.py
```

## Still blocked (honest limits)

- **Visual proof:** no same-frame literal `00:00` exists in the reviewed broadcasts; per-game VODs also cut in after zero (first HUD `00:21` in 1036 G1, `00:42` in 1036 G2). Do not promote; the standard is unchanged.
- **Objectives:** the database has no Lord/Turtle/tower-event counts. Objective analysis is transcript-attributed or a review protocol.
- **Patch meta:** no patch/version field. Calendar splits are not patch splits.
- **Transcript coverage:** 1037 is the pilot with 6 accepted game-VOD observations. The other 44 matches are fetched but not extracted yet. No match is blocked. The 27-source observation ledger is unchanged.
- **Intent/vision/comms:** unavailable. Coaching claims stay hypotheses.
