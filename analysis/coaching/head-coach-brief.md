# MPL S18 — head-coach brief

**Evidence base:** 72 series, 174 games, snapshot `mpl-s18-db-20c5ea2c51f3`. League interpretation: `analysis/reports/league-meta.md`; full tables: `analysis/reports/league-data.md`; coverage: `analysis/reports/coverage-matrix.md`. Team briefs: `analysis/coaching/teams/`.

## The league in five points

1. **TLID and NAVI tied at 12–4, with different identities.** TLID finish fast (15:14 average, 12 blowout wins, 9 sweeps); NAVI absorb and win close games (17:17 average, 4–3 close, 5 deciders).
2. **AE are the cleanest third team.** 10–6, 9 sweeps, 12 blowout wins, 15:41 average. Their early-snowball draft converts when the first skirmish goes their way.
3. **BTR's 10–6 is fragile.** +3 game differential, five 0–2 losses, 5–6 in blowouts, and a Selena volume pick at 30.8%.
4. **ONIC's red side is the league's biggest matchup lever.** 15–6 blue, 4–15 red. Force them to red.
5. **The bottom three collapse differently.** DEWA lose by blowout (4–14), GEEK lose the red side (7–17) and 5v5, RRQ lose deciders (9 played, 4 won).

## Cross-team priorities

- **First Turtle is the first conversion checkpoint.** The transcript repeats it across 1055, 1080, 1094 and 1107. But it is not destiny: 1087, 1102 and 1057 are counterexamples where the first objective did not decide the game. Coach the sequence, not the statistic.
- **Draft volume is not priority.** Paquito is the highest-volume pick at 44.8%; Selena is 41.3%; Uranus is 46.9%. The team split decides. Build opponent-specific ban lists from their volume, not the league average.
- **Side is a scouting question.** League blue win rate is 58.0%, but team splits range from ONIC 15–6 to RRQ 4–13. Use side to force a draft, not as an excuse.
- **Close games are a small sample.** NAVI 4–3, AE 3–1, EVOS 3–3, BTR 2–3, ONIC 2–4. Do not build a "clutch" identity on seven games.
- **Patch claims are blocked.** The database has no patch field. The healing Turtle rework and gold changes are transcript-only. Do not present a patch tier list until a dated patch map exists.

## Matchup sheet

| Opponent | Force them to | Deny | Test |
|---|---|---|---|
| TLID | low-economy, messy game | first Turtle rotation and three-player zone | their one close-game sample |
| NAVI | fast first-Turtle game | engage/frontline, Belerick/Hirara | the 4–3 close record |
| AE | red side, contested first Turtle | Paquito/Nolan/Hirara clean enablers | the 3–1 close record |
| BTR | 5v5 front-to-back | Selena comfort and first Turtle | whether 10–6 is real |
| EVOS | 30-minute game | first Turtle and Obsidia/Carmilla | their 10k collapse |
| ONIC | red side | Hirara/Nolan and first selection | the 1102 comeback |
| DEWA | structured mid-game | early Turtle conversion | the 1102 turtle lead |
| GEEK | standard 5v5 | Kimmy and river chaos | the ONIC-only strength |
| RRQ | game three, front-to-back | Paquito conversion and Joshua pressure | the 9-decider record |

## Review queue (highest value first)

1. **1107 ONIC vs TLID** — the three-player zone and Turtle-to-tower conversion.
2. **1080 TLID vs BTR** — forcing the mid out and converting Turtle into Lord.
3. **1055 AE vs EVOS** — early snowball vs 10,000-gold collapse.
4. **1062 DEWA vs ONIC** — early Turtle fight into a 15-minute close.
5. **1102 DEWA vs ONIC** — first two Turtles lost the series; the counterexample.
6. **1076 GEEK vs ONIC** — the 13–3 / 20–2 outlier.
7. **1091 ONIC vs NAVI** — first selection and the Joshua pressure.
8. **1087 BTR vs RRQ** — Turtle won, four players lost.

## Operating rhythm

- **Weekly:** one opponent-specific ban list from their volume picks; one first-Turtle sequence review; one close-game endgame block.
- **Per series:** record the first Turtle winner, conversion, first Lord, and whether the first-Turtle team won. That is the only way to build an objective dataset.
- **Per patch:** add a dated patch map before making patch claims; re-run `tools/build_league_aggregates.py` and the coverage matrix.
- **Per update:** if a claim depends on a screenshot, it needs a same-frame literal `00:00`; 0 visual boundaries are verified.

## Unknowns that matter

- No objective counts, gold timelines, vision, communications or intent.
- 45 of 72 series have no transcript; their reports are database-only.
- 3 transcript sources are partial; 21 games lack map mode.
- No patch/version field.
- 0 visual boundaries verified; the strict `00:00` gate is unmet.

## Bottom line

The league is not separated by draft novelty. It is separated by conversion, sweep avoidance and side-specific draft execution. TLID and NAVI are the benchmarks; AE is close; BTR's record is ahead of its control; ONIC's red side and RRQ's deciders are the cheapest matchup edges; DEWA and GEEK need structural fixes before new picks matter.
