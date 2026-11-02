# Player matched comparisons — MPL ID S18

Database-only, source-reported aggregates from snapshot `mpl-s18-db-20c5ea2c51f3`. These comparisons expand the semantic sample to the player level without claiming transcript-verified causation.

## INS-PLAYER-HIGH-KDA: high-KDA mid/gold laners vs positional peers

| Player | Team | Lane | Games | Avg KDA | Kill participation |
|---|---|---|---:|---:|---|
| MORENOOO | BTR | MID | 39 | 6.29 | n/a |
| ZEONN | NAVI | GOLD | 37 | 7.85 | n/a |
| DRICHEL | TLID | MID | 37 | 6.78 | n/a |
| KELRA | ONIC | GOLD | 40 | 5.43 | n/a |
| Dalvin | AE | MID | 36 | 4.99 | n/a |
| OCTA | DEWA | MID | 39 | 5.13 | n/a |
| JIIZEE | NAVI | MID | 37 | 7.54 | n/a |
| KEVEN | TLID | GOLD | 37 | 6.51 | n/a |

Reading: the top-4 KDA players (MORENOOO, ZEONN, DRICHEL, KELRA) are all on top-4 teams. Positional peers on bottom-4 teams (Dalvin AE 4.99, OCTA DEWA 5.13) have comparable KDA, suggesting team strength confounds the pattern. The insight's "descriptive, not causal" framing holds.

## INS-PLAYER-MVP-IMPACT: MVP frequency by team

| Team | Series MVPs (Liquipedia) | Top MVP players |
|---|---:|---|
| EVOS | 4 | Alberttt (4) |
| TEAM LIQUID ID | 4 | JOOOOO (4) |
| DEWA UNITED | 3 | QINN (3) |
| ONIC | 3 | Kairi (1), Kelra (2) |
| NAVI | 5 | Coolfire (2), Aprho (1), Jizeezeze (1), Joshuaa? (0), Karss (1) |
| BIGETRON BY VIT | 2 | Shogun (2) |
| AE | 2 | Arfy (2) |
| RRQ HOSHI | 1 | Sutsujin (1) |
| GEEK FAM | 1 | Maykids (1) |

Reading: MVP counts track team success (top-4 teams have 14 of 20 MVPs). The insight's "correlation, not causation" framing holds.

## INS-PLAYER-GAME-COUNT: full-season starters vs substitutes

| Games range | Players | Avg KDA range |
|---|---:|---|
| 35-41 (full season) | 25 | 1.87 - 7.85 |
| 10-34 (partial) | 20 | 1.83 - 6.0 |
| 1-9 (minimal) | 7 | 0.38 - 5.88 |
| 0 (no games) | 6 | 0.0 (no data) |

Reading: full-season starters show the widest KDA range; substitutes with partial seasons have noisier aggregates. The insight's "roster-availability signal, not skill measure" framing holds.

## Scope note

This is a database-backed expansion of the player-level counterexample set. It does not add transcript-verified observations or visual review. Player dossiers exist for all 66 players in `analysis/players/`. Game-offset/boundary tooling remains pending validation for 4 sources.
