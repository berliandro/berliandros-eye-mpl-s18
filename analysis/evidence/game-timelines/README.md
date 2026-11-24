# Game-level evidence timelines

This directory contains canonical game-level evidence timelines following `analysis/evidence/game-evidence-timeline-schema.json`.

## Files

- `TL-<SERIES>-G<GAME>.json` — one timeline per game per series.

## Current coverage

- 174 timelines (one per game across all 72 series): 29 boundary-verified timelines and 145 DB-only timelines. See `analysis/reports/coverage-summary.md` for the current reconciliation.
- The pilot timelines (1036, 1037, 1107) carry the richest event evidence; the rest are DB-only or boundary-only where noted in each file.

## Status definitions

- `verified`: independently confirmed series+game boundary (not yet achieved for any game; all current timelines are `heuristic`)
- `heuristic`: candidate boundary from transcript detection or schedule order; not independently verified
- `unresolved`: not yet determined
- `quarantined`: explicitly excluded from citations

## Visual evidence

Timeline frames remain `review_status: not-reviewed` unless their exact screenshot is recorded in the DeepSeek review ledger. DeepSeek visual review pass 1 (2026-11-02) reviewed 53 frames and 11 boundary candidates: 5 candidate offsets were rejected, 5 were context-only, 1 was inconclusive, and 0 boundaries were promoted to `visually_verified`. See `analysis/evidence/deepseek-visual-reviews.json`, `analysis/reports/visual-proof-deepseek-review.md`, and `docs/goals/finished/mpl-s18-visual-proof-deepseek-handoff.md` §8.

## Validation

Run `python tools/validate_visual_reviews.py` for the visual-review ledger and `python tools/ci_semantic_check.py` for timelines, offsets, IDs, and report references. The GitHub workflow is `.github/workflows/semantic-check.yml`.
