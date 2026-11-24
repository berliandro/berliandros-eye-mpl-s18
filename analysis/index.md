# Analysis index

## Status

- Corpus imported: **27 files / 9,682,086 bytes**, SHA-256 verified **27/27**, conflicts **0**.
- Native transcript timestamps: **0**.
- Unique schedule VOD candidates: **27/27 broadcast dates**, derived from the canonical completed schedule.
- Metadata-verified official videos: **27/27** (official MPL Indonesia channel, exact season/week/day title).
- Fully caption-aligned sources: **26/27**; one partial source (`src-s18-w09d02`) is explicitly not citation-ready.
- Database winner orientation: repaired **21/72** rows; **0/72** row-score mismatches remain.
- Pilot series: **3** — 1036, 1037, 1107.
- Transcript store: **27 segment ledgers / 368 observation records** (313 accepted, 50 rejected, 5 resolved), canonical.
- Legacy pilot store: **234 frozen records** (85 observations, 73 insights, 68 audits, 8 segments); see `reports/evidence-store.md`.
- Match evidence: **72/72** reports carry a database block; **27** have transcript coverage (24 complete, 3 partial), **45** are DB-only.
- Synthesis: **9/9** team profiles, **94** hero pages, **6/6** strategy pages, plus the season hero and league meta reports.
- Coaching: **9** team briefs and **1** head-coach brief in `coaching/`.
- Visual review: **1 boundary visually verified** (match 1062, DEWA vs ONIC; anchor DF3-w04d02-2465); 966 frame reviews and 62 boundary reviews (1 used, 40 context-only, 20 rejected, 1 inconclusive, 10 waived). Goal complete 2026-11-24 under the revised first-visible-HUD standard.
- Semantic coverage: **27/72 broadcast-source transcript-backed**; game transcripts are now available for **all 45 DB-only matches** (107/107 games, all Indonesian); the **1037 pilot** has 6 accepted game-VOD observations, bringing combined transcript evidence to **28/72**.
- Game transcript availability: **107/107 games fetched** (45/45 matches full, all Indonesian); source availability, not accepted observations (except the 1037 pilot). Manifest: [`evidence/game-transcript-manifest.json`](evidence/game-transcript-manifest.json).

## Transcript knowledge pipeline

- Status: **27/27 source ledgers validated**; 363 observations extracted, 313 accepted and consolidated, 0 left for review, 50 rejected, 3 sources marked partial.
- Coverage: [`reports/transcript-pipeline/coverage.md`](reports/transcript-pipeline/coverage.md)
- Team notes: [`teams/`](teams/)
- Hero notes: [`heroes/`](heroes/)
- Strategy notes: [`strategy/`](strategy/)
- Spec: `../docs/goals/active/revised_transcript_workflow.md`
- Completed goal: `../docs/goals/finished/mpl-s18-transcript-knowledge-goal.md`
- Canonical store manifest: [`evidence/canonical-store.json`](evidence/canonical-store.json)
- Store reconciliation: [`reports/evidence-store.md`](reports/evidence-store.md)
- Coverage matrix: [`reports/coverage-matrix.md`](reports/coverage-matrix.md)
- Staging schema: [`evidence/transcript-observation-schema.json`](evidence/transcript-observation-schema.json)
- Validator: [`../tools/validate_transcript_ledger.py`](../tools/validate_transcript_ledger.py)
- Read-only stats bridge: [`../tools/stats_query.py`](../tools/stats_query.py)
- Segment ledgers: `evidence/transcript-segments/`
- Observation ledgers: `evidence/transcript-observations/`
- Run reports: `reports/transcript-pipeline/`

## Start here

1. [`reports/coverage-matrix.md`](reports/coverage-matrix.md) — canonical coverage: 72/72 match evidence, transcript split, visual status, page inventory.
2. [`reports/league-meta.md`](reports/league-meta.md) — season interpretation: tiers, side/map, hero meta, player production, limits.
3. [`coaching/head-coach-brief.md`](coaching/head-coach-brief.md) — the overall coaching product; team briefs live in [`coaching/teams/`](coaching/teams/).
4. [`README.md`](README.md) — scope, safety, reproduction commands.
5. [`reports/corpus-inventory.md`](reports/corpus-inventory.md) — what was imported, timestamp/video coverage, parsing risks.
6. [`reports/database-inventory.md`](reports/database-inventory.md) — DB coverage, joins, and the post-migration `matches.winner` semantics.
7. [`reports/evidence-store.md`](reports/evidence-store.md) — canonical vs frozen stores and the rules for new evidence.

## Pilot series

- [`matches/1036-evoss-vs-rrq.md`](matches/1036-evoss-vs-rrq.md) — EVOS 2–0 RRQ; early-snowball draft consistency check.
- [`matches/1037-navi-vs-ae.md`](matches/1037-navi-vs-ae.md) — NAVI 0–2 AE; late base defense/turning-point review.
- [`matches/1107-onic-vs-tlid.md`](matches/1107-onic-vs-tlid.md) — ONIC 0–2 TLID; early rotations to structure damage.
- [`matches/1039-dewa-vs-rrq.md`](matches/1039-dewa-vs-rrq.md) — DEWA 1–2 RRQ; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1038-geek-vs-tlid.md`](matches/1038-geek-vs-tlid.md) — GEEK 1–2 TLID; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1040-evos-vs-navi.md`](matches/1040-evos-vs-navi.md) — EVOS 1–2 NAVI; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1045-dewa-vs-btr.md`](matches/1045-dewa-vs-btr.md) — DEWA 0–2 BTR; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1069-geek-vs-onic.md`](matches/1069-geek-vs-onic.md) — GEEK 2–1 ONIC; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1052-navi-vs-btr.md`](matches/1052-navi-vs-btr.md) — NAVI 0–2 BTR; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1053-dewa-vs-geek.md`](matches/1053-dewa-vs-geek.md) — DEWA 2–0 GEEK; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1060-navi-vs-dewa.md`](matches/1060-navi-vs-dewa.md) — NAVI 2–0 DEWA; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1068-evos-vs-dewa.md`](matches/1068-evos-vs-dewa.md) — EVOS 2–1 DEWA; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1100-rrq-vs-navi.md`](matches/1100-rrq-vs-navi.md) — RRQ 1–2 NAVI; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1041-tlid-vs-dewa.md`](matches/1041-tlid-vs-dewa.md) — TLID 2–0 DEWA; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1042-btr-vs-geek.md`](matches/1042-btr-vs-geek.md) — BTR 2–1 GEEK; stratified expansion (DB-only, boundary unverified).
- [`matches/1043-onic-vs-ae.md`](matches/1043-onic-vs-ae.md) — ONIC 2–0 AE; stratified expansion (DB-only, boundary unverified).
- [`matches/1044-tlid-vs-navi.md`](matches/1044-tlid-vs-navi.md) — TLID 0–2 NAVI; stratified expansion (DB-only, boundary unverified).
- [`matches/1046-evos-vs-tlid.md`](matches/1046-evos-vs-tlid.md) — EVOS 0–2 TLID; stratified expansion (DB-only, boundary unverified).
- [`matches/1055-ae-vs-evos.md`](matches/1055-ae-vs-evos.md) — AE 2–0 EVOS; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1048-onic-vs-rrq.md`](matches/1048-onic-vs-rrq.md) — ONIC 2–0 RRQ; stratified expansion (DB-only, boundary unverified).
- [`matches/1049-dewa-vs-ae.md`](matches/1049-dewa-vs-ae.md) — DEWA 0–2 AE; stratified expansion (DB-only, boundary unverified).
- [`matches/1051-geek-vs-evos.md`](matches/1051-geek-vs-evos.md) — GEEK 0–2 EVOS; stratified expansion (DB-only, boundary unverified).
- [`matches/1054-tlid-vs-onic.md`](matches/1054-tlid-vs-onic.md) — TLID 2–1 ONIC; stratified expansion (DB-only, boundary unverified).
- [`matches/1056-rrq-vs-btr.md`](matches/1056-rrq-vs-btr.md) — RRQ 1–2 BTR; stratified expansion (DB-only, boundary unverified).
- [`matches/1065-rrq-vs-navi.md`](matches/1065-rrq-vs-navi.md) — RRQ 0–2 NAVI; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1061-tlid-vs-rrq.md`](matches/1061-tlid-vs-rrq.md) — TLID 2–0 RRQ; stratified expansion (DB-only, boundary unverified).
- [`matches/1063-btr-vs-evos.md`](matches/1063-btr-vs-evos.md) — BTR 1–2 EVOS; stratified expansion (DB-only, boundary unverified).
- [`matches/1064-ae-vs-geek.md`](matches/1064-ae-vs-geek.md) — AE 2–0 GEEK; stratified expansion (DB-only, boundary unverified).
- [`matches/1066-onic-vs-evos.md`](matches/1066-onic-vs-evos.md) — ONIC 2–0 EVOS; stratified expansion (DB-only, boundary unverified).
- [`matches/1067-ae-vs-btr.md`](matches/1067-ae-vs-btr.md) — AE 2–0 BTR; stratified expansion (DB-only, boundary unverified).
- [`matches/1074-onic-vs-ae.md`](matches/1074-onic-vs-ae.md) — ONIC 0–2 AE; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1075-dewa-vs-rrq.md`](matches/1075-dewa-vs-rrq.md) — DEWA 2–1 RRQ; stratified expansion (DB-only, boundary unverified).
- [`matches/1076-onic-vs-geek.md`](matches/1076-onic-vs-geek.md) — ONIC 0–2 GEEK; stratified expansion (DB-only, boundary unverified).
- [`matches/1077-dewa-vs-evos.md`](matches/1077-dewa-vs-evos.md) — DEWA 0–2 EVOS; stratified expansion (DB-only, boundary unverified).
- [`matches/1078-geek-vs-navi.md`](matches/1078-geek-vs-navi.md) — GEEK 0–2 NAVI; stratified expansion (DB-only, boundary unverified).
- [`matches/1079-rrq-vs-ae.md`](matches/1079-rrq-vs-ae.md) — RRQ 1–2 AE; stratified expansion (DB-only, boundary unverified).
- [`matches/1071-ae-vs-rrq.md`](matches/1071-ae-vs-rrq.md) — AE 2–0 RRQ; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1091-onic-vs-navi.md`](matches/1091-onic-vs-navi.md) — ONIC 2–1 NAVI; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1070-tlid-vs-btr.md`](matches/1070-tlid-vs-btr.md) — TLID 2–0 BTR; stratified expansion (DB-only, boundary unverified).
- [`matches/1072-navi-vs-evos.md`](matches/1072-navi-vs-evos.md) — NAVI 2–0 EVOS; stratified expansion (DB-only, boundary unverified).
- [`matches/1073-geek-vs-tlid.md`](matches/1073-geek-vs-tlid.md) — GEEK 0–2 TLID; stratified expansion (DB-only, boundary unverified).
- [`matches/1092-ae-vs-btr.md`](matches/1092-ae-vs-btr.md) — AE 2–0 BTR; stratified expansion (DB-only, boundary unverified).
- [`matches/1093-navi-vs-tlid.md`](matches/1093-navi-vs-tlid.md) — NAVI 2–0 TLID; stratified expansion (DB-only, boundary unverified).
- [`matches/1059-tlid-vs-ae.md`](matches/1059-tlid-vs-ae.md) — TLID 2–1 AE; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1080-tlid-vs-btr.md`](matches/1080-tlid-vs-btr.md) — TLID 2–0 BTR; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1106-navi-vs-btr.md`](matches/1106-navi-vs-btr.md) — NAVI 0–2 BTR; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1094-evos-vs-onic.md`](matches/1094-evos-vs-onic.md) — EVOS 2–1 ONIC; stratified expansion (DB-only, boundary unverified).
- [`matches/1095-rrq-vs-tlid.md`](matches/1095-rrq-vs-tlid.md) — RRQ 0–2 TLID; stratified expansion (DB-only, boundary unverified).
- [`matches/1096-dewa-vs-navi.md`](matches/1096-dewa-vs-navi.md) — DEWA 0–2 NAVI; stratified expansion (DB-only, boundary unverified).
- [`matches/1097-evos-vs-geek.md`](matches/1097-evos-vs-geek.md) — EVOS 0–2 GEEK; stratified expansion (DB-only, boundary unverified).
- [`matches/1099-btr-vs-dewa.md`](matches/1099-btr-vs-dewa.md) — BTR 2–0 DEWA; stratified expansion (DB-only, boundary unverified).
- [`matches/1101-geek-vs-ae.md`](matches/1101-geek-vs-ae.md) — GEEK 0–2 AE; stratified expansion (DB-only, boundary unverified).
- [`matches/1102-dewa-vs-onic.md`](matches/1102-dewa-vs-onic.md) — DEWA 1–2 ONIC; stratified expansion (DB-only, boundary unverified).
- [`matches/1103-evos-vs-btr.md`](matches/1103-evos-vs-btr.md) — EVOS 1–2 BTR; stratified expansion (DB-only, boundary unverified).
- [`matches/1104-rrq-vs-geek.md`](matches/1104-rrq-vs-geek.md) — RRQ 2–1 GEEK; stratified expansion (DB-only, boundary unverified).
- [`matches/1105-ae-vs-evos.md`](matches/1105-ae-vs-evos.md) — AE 1–2 EVOS; stratified expansion (DB-only, boundary unverified).
- [`matches/1098-rrq-vs-onic.md`](matches/1098-rrq-vs-onic.md) — RRQ 1–2 ONIC; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1081-dewa-vs-ae.md`](matches/1081-dewa-vs-ae.md) — DEWA 2–0 AE; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1084-geek-vs-btr.md`](matches/1084-geek-vs-btr.md) — GEEK 1–2 BTR; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1082-onic-vs-btr.md`](matches/1082-onic-vs-btr.md) — ONIC 2–0 BTR; stratified expansion (DB-only, boundary unverified).
- [`matches/1083-evos-vs-tlid.md`](matches/1083-evos-vs-tlid.md) — EVOS 2–1 TLID; stratified expansion (DB-only, boundary unverified).
- [`matches/1085-dewa-vs-tlid.md`](matches/1085-dewa-vs-tlid.md) — DEWA 2–1 TLID; stratified expansion (DB-only, boundary unverified).
- [`matches/1086-ae-vs-navi.md`](matches/1086-ae-vs-navi.md) — AE 1–2 NAVI; stratified expansion (DB-only, boundary unverified).
- [`matches/1087-btr-vs-rrq.md`](matches/1087-btr-vs-rrq.md) — BTR 2–1 RRQ; stratified expansion (DB-only, boundary unverified).
- [`matches/1050-onic-vs-btr.md`](matches/1050-onic-vs-btr.md) — ONIC 1–2 BTR; stratified expansion sample (source-mapped, boundary-verified).
- [`matches/1057-navi-vs-onic.md`](matches/1057-navi-vs-onic.md) — NAVI 2–0 ONIC; stratified expansion (DB-only, boundary unverified).
- [`matches/1058-rrq-vs-geek.md`](matches/1058-rrq-vs-geek.md) — RRQ 2–0 GEEK; stratified expansion (DB-only, boundary unverified).
- [`matches/1088-dewa-vs-geek.md`](matches/1088-dewa-vs-geek.md) — DEWA 1–2 GEEK; stratified expansion (DB-only, boundary unverified).
- [`matches/1089-tlid-vs-ae.md`](matches/1089-tlid-vs-ae.md) — TLID 2–0 AE; stratified expansion (DB-only, boundary unverified).
- [`matches/1090-rrq-vs-evos.md`](matches/1090-rrq-vs-evos.md) — RRQ 2–1 EVOS; stratified expansion (DB-only, boundary unverified).
- [`matches/1047-navi-vs-geek.md`](matches/1047-navi-vs-geek.md) — NAVI 2–1 GEEK; stratified expansion sample (source-mapped, boundary-verified).

## Audit

- [`reports/audit-INS-1037-LATE-SWING.md`](reports/audit-INS-1037-LATE-SWING.md) — verdict **partially supported**. Quote/timestamp validation, DB checks, counterexamples, actual frame review and limitations.
- [`reports/phase0-mistake-audit.md`](reports/phase0-mistake-audit.md) — Phase 0 mistake audit and fixes.
- [`reports/unvalidated-sources.md`](reports/unvalidated-sources.md) — 4 sources that could not be auto-validated; DeepSeek visual review status.
- [`reports/visual-proof-deepseek-review.md`](reports/visual-proof-deepseek-review.md) - DeepSeek visual review passes 1–2: 113 frames, 31 boundaries, 18 rejected candidates, 0 promoted.
- [`reports/coverage-summary.md`](reports/coverage-summary.md) — historical pre-transcript coverage; superseded by the canonical matrix.
- [`reports/player-matched-comparisons.md`](reports/player-matched-comparisons.md) — database-backed matched comparisons for player-level insights.
- [`players/`](players/) — 66 player dossiers (one per player). See `analysis/players/` for the full list.
- [`reports/counter-analysis-pilot.md`](reports/counter-analysis-pilot.md) — antithesis/counter-analysis of the three pilot insights.
- [`reports/matched-comparisons.md`](reports/matched-comparisons.md) — database-backed matched comparisons expanding the counterexample set beyond the pilot.

## Evidence and reproducibility

- [`evidence/pilot-ledger.jsonl`](evidence/pilot-ledger.jsonl) — frozen pilot claim store (85 observations, 73 insights, 68 audits); not canonical for new observations.
- [`evidence/canonical-store.json`](evidence/canonical-store.json) — canonical store manifest with hashes, counts and rules.
- [`evidence/evidence-schema.json`](evidence/evidence-schema.json) — versioned JSON Schema.
- [`evidence/query-catalog.json`](evidence/query-catalog.json) — every SQL query, parameters and provenance.
- [`evidence/database-snapshot-manifest.json`](evidence/database-snapshot-manifest.json) — DB fingerprint, coverage and lineage.
- [`evidence/audit-log.jsonl`](evidence/audit-log.jsonl) — audit export.
- [`evidence/visual-review.json`](evidence/visual-review.json) — frame dispositions.
- [`evidence/timed-alignment.json`](evidence/timed-alignment.json) — caption alignment coverage for 26 verified sources.
- [`sources/source-manifest.json`](sources/source-manifest.json) — source hashes, verified video IDs, status semantics and series mapping.
- [`pilot/selection.json`](pilot/selection.json) — curated claims/quotes used to build the ledger.

## Video source resolution

- [Video source resolution report](reports/video-source-resolution.md) lists every source, status, failure reason and status transition.
- Local result: **27/27 metadata-verified**, **26/27 fully aligned**, **1/27 partial** (`src-s18-w09d02`; 37 short lines without trustworthy timestamps).
- Run `python tools/resolve_and_align_sources.py` on the local machine with the ignored raw corpus to re-check metadata and alignment.
- Broadcast-date mapping does not establish exact in-video start times for individual series or games.

## Coverage warning

All 72 series have database evidence. Only 27 have transcript coverage; 45 are DB-only and cannot support quote or timestamp claims. Alignment readiness is not semantic analysis. Do not read the 27-series transcript layer as a season-level conclusion without checking the counterexamples and limits on each synthesis page.

## Player index

| Player | Team | Lane | Dossier |
|---|---|---|---|
| Nino | ALTER EGO ESPORTS | EXP | [dossier](players/nino.md) |
| Dingarai | ALTER EGO ESPORTS | GOLD | [dossier](players/dingarai.md) |
| Affan | ALTER EGO ESPORTS | JUNGLE | [dossier](players/affan.md) |
| Reyy | ALTER EGO ESPORTS | JUNGLE | [dossier](players/reyy.md) |
| Dalvin | ALTER EGO ESPORTS | MID | [dossier](players/dalvin.md) |
| Halim | ALTER EGO ESPORTS | MID | [dossier](players/halim.md) |
| Alexander | ALTER EGO ESPORTS | ROAM | [dossier](players/alexander.md) |
| SHOGUN | BIGETRON BY VIT | EXP | [dossier](players/shogun.md) |
| EMANN | BIGETRON BY VIT | GOLD | [dossier](players/emann.md) |
| NNAEL | BIGETRON BY VIT | JUNGLE | [dossier](players/nnael.md) |
| MIGUEL | BIGETRON BY VIT | MID | [dossier](players/miguel.md) |
| MORENOOO | BIGETRON BY VIT | MID | [dossier](players/morenooo.md) |
| FINN | BIGETRON BY VIT | ROAM | [dossier](players/finn.md) |
| QINN | DEWA UNITED | EXP | [dossier](players/qinn.md) |
| MAYBEEE | DEWA UNITED | GOLD | [dossier](players/maybeee.md) |
| Hazle | DEWA UNITED | JUNGLE | [dossier](players/hazle.md) |
| KAYN | DEWA UNITED | JUNGLE | [dossier](players/kayn.md) |
| OCTA | DEWA UNITED | MID | [dossier](players/octa.md) |
| RUL GOOD | DEWA UNITED | MID | [dossier](players/rul-good.md) |
| ITOSHI KESU | DEWA UNITED | ROAM | [dossier](players/itoshi-kesu.md) |
| SHANEE | DEWA UNITED | ROAM | [dossier](players/shanee.md) |
| RENDYYY | EVOS | EXP | [dossier](players/rendyyy.md) |
| VELL | EVOS | EXP | [dossier](players/vell.md) |
| ERLAN | EVOS | GOLD | [dossier](players/erlan.md) |
| ALBERTTT | EVOS | JUNGLE | [dossier](players/alberttt.md) |
| DRIANW | EVOS | MID | [dossier](players/drianw.md) |
| Ryzaa | EVOS | MID | [dossier](players/ryzaa.md) |
| EgaTzy | EVOS | ROAM | [dossier](players/egatzy.md) |
| MUEZZA | EVOS | ROAM | [dossier](players/muezza.md) |
| FEBRIII | GEEK FAM | EXP | [dossier](players/febriii.md) |
| MARCEL | GEEK FAM | EXP | [dossier](players/marcel.md) |
| KENNZYYSKIE | GEEK FAM | GOLD | [dossier](players/kennzyyskie.md) |
| MAYKIDSS | GEEK FAM | JUNGLE | [dossier](players/maykidss.md) |
| NAZARA | GEEK FAM | JUNGLE | [dossier](players/nazara.md) |
| ABOYY | GEEK FAM | MID | [dossier](players/aboyy.md) |
| AUDYTZY | GEEK FAM | ROAM | [dossier](players/audytzy.md) |
| Frenzyy | GEEK FAM | ROAM | [dossier](players/frenzyy.md) |
| FEBBB | NAVI | EXP | [dossier](players/febbb.md) |
| KARSS | NAVI | EXP | [dossier](players/karss.md) |
| ZEONN | NAVI | GOLD | [dossier](players/zeonn.md) |
| ANDORYUUU | NAVI | JUNGLE | [dossier](players/andoryuuu.md) |
| Joshuaa | NAVI | JUNGLE | [dossier](players/joshuaa.md) |
| JIIZEE | NAVI | MID | [dossier](players/jiizee.md) |
| APRHO | NAVI | ROAM | [dossier](players/aprho.md) |
| LUTPI | ONIC | EXP | [dossier](players/lutpi.md) |
| KELRA | ONIC | GOLD | [dossier](players/kelra.md) |
| KAIRI | ONIC | JUNGLE | [dossier](players/kairi.md) |
| Killuaa | ONIC | MID | [dossier](players/killuaa.md) |
| SANZ | ONIC | MID | [dossier](players/sanz.md) |
| KIBOY | ONIC | ROAM | [dossier](players/kiboy.md) |
| SSAMUEL | ONIC | ROAM | [dossier](players/ssamuel.md) |
| JOSHUA | RRQ HOSHI | EXP | [dossier](players/joshua.md) |
| ARTHUR | RRQ HOSHI | GOLD | [dossier](players/arthur.md) |
| HABIL | RRQ HOSHI | GOLD | [dossier](players/habil.md) |
| DEMONKITE | RRQ HOSHI | JUNGLE | [dossier](players/demonkite.md) |
| Faviannn | RRQ HOSHI | JUNGLE | [dossier](players/faviannn.md) |
| CLAYYY | RRQ HOSHI | MID | [dossier](players/clayyy.md) |
| HAJIRIN | RRQ HOSHI | MID | [dossier](players/hajirin.md) |
| Excellent99 | RRQ HOSHI | ROAM | [dossier](players/excellent99.md) |
| SAID | RRQ HOSHI | ROAM | [dossier](players/said.md) |
| ARAN | TEAM LIQUID ID | EXP | [dossier](players/aran.md) |
| KEVEN | TEAM LIQUID ID | GOLD | [dossier](players/keven.md) |
| KEVIN | TEAM LIQUID ID | JUNGLE | [dossier](players/kevin.md) |
| ANAVER | TEAM LIQUID ID | MID | [dossier](players/anaver.md) |
| DRICHEL | TEAM LIQUID ID | MID | [dossier](players/drichel.md) |
| LYONI | TEAM LIQUID ID | ROAM | [dossier](players/lyoni.md) |
