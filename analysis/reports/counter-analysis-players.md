# Counter-analysis (antithesis) — player-level insights

This document challenges the three per-player insights and records what would weaken or overturn them. It is an audit-style counterweight, not a replacement.

## INS-PLAYER-ALBERTTT (`cross-checked`)

**Thesis:** Alberttt (EVOS jungle) has the highest series MVP count (4) and a 4.70 avg KDA across 35 games; his Paquito/Eudora early-snowball compositions are consistent with fast, tower-heavy wins.

**Antithesis:**
- MVP count may be a team-success proxy: EVOS is 8-8 (mid-table), not a losing team, but not dominant either. Alberttt's 4 MVPs are concentrated in EVOS wins.
- The same Paquito/Eudora core appeared in losses (1055 g2, 1066 g2, 1077 g1, 1103 g1), so the draft does not guarantee the outcome.
- Tower damage (22,472 vs 1,252 in 1036 g1) is an outcome aggregate; a fast win against a collapsed opponent inflates it.
- Auto-captions may misidentify player names; "Albert" in transcripts is not independently audio-verified.
- No matched comparison against other junglers on top-4 vs bottom-5 teams exists.

**What would be needed to upgrade:** matched comparisons across EVOS wins/losses with the same core against similar opposing drafts, plus first-turret/first-Turtle timings. Until then the insight stays "consistent with," not "caused by."

## INS-PLAYER-MORENOOO (`cross-checked`)

**Thesis:** MORENOOO (BTR mid) has the highest avg KDA (6.29) among players with 30+ games.

**Antithesis:**
- BTR is a top-4 team (10-6); team strength may inflate KDA. Mid lane has naturally lower death exposure.
- No kill participation parsing; high KDA with low kill participation would indicate a different (less impactful) playstyle.
- Sample size (39 games) is large but a few outlier games can inflate averages. Median KDA was not computed.
- Transcript mentions (405 hits) are frequent but not systematically curated for individual performance.

**What would be needed to upgrade:** matched comparison against mid laners on bottom-4 teams (Dalvin AE 4.99, OCTA DEWA 5.13) with the same game count. Median KDA computation. Kill participation parsing.

## INS-PLAYER-KELRA (`cross-checked`)

**Thesis:** Kelra (ONIC gold) has the highest avg KDA among gold laners with 40 games (5.43) and was MVP for 1066 and 1107.

**Antithesis:**
- ONIC is 6th place (7-9); Kelra's KDA may reflect gold-lane role (lower death exposure) rather than individual skill.
- Kelra was completely shut down in 1066 game 2 (1-11 loss), showing vulnerability.
- MVP awards (2) may reflect team success in those series, not individual dominance.
- Transcript mentions (288 hits) are caster references, not systematic performance analysis.

**What would be needed to upgrade:** What shuts down Kelra in losses (1066 g2: 1-11)? Which opposing drafts or jungle pressure neutralize his gold-lane impact? Matched comparison against gold laners on top-4 teams.

## Shared antithesis (all three)

- All three insights rest on season aggregates only; no game-level causal estimate exists.
- No matched comparisons against positional peers on weaker teams.
- No visual verification of any player's gameplay.
- No transcript-verified observations for individual player performance (transcript mentions exist but are not systematically curated).
- Kill participation is stored as text and was not parsed.
- "Cross-checked" is a verification state about evidence quality, not proof of a player trait.

## Improvements applied after this counter-analysis

- Added transcript evidence to 28 player dossiers (verified quotes with line spans and timestamp links).
- Added top-items-by-frequency to 46 dossiers.
- Added opponent context (vs top-4/bottom-5) to 58 dossiers.
- Added season trend (early vs late KDA) to 46 dossiers.
- Added series appearances (cross-refs) to 60 dossiers.
- Created 3 per-player insights with counterexamples and 1 skeptical audit.
- Created player-matched-comparisons.md report.
- All dossiers validated (66 files, snapshot ID, consistent structure).
