# Matched comparisons — pilot insights vs counterexample series

Database-only, source-reported aggregates from snapshot `mpl-s18-db-20c5ea2c51f3`. These comparisons expand the semantic sample beyond the three pilot series without claiming transcript-verified causation. No new transcript claims are made here; the counterexample series are referenced only through their structured game aggregates.

## INS-1036-EARLY-DRAFT: does Paquito/Eudora guarantee a fast tower-heavy win?

| Series (game) | EVOS Paquito/Eudora? | Result | Duration | EVOS tower damage |
|---|---|---|---:|---:|
| 1036 (g1) | yes | W | 16:51 | 22,472 |
| 1036 (g2) | yes | W | 24:40 | 28,036 |
| 1055 (g2) | Paquito | L | 17:22 | 0 |
| 1063 (g1) | Eudora | L | 16:42 | 1,357 |
| 1066 (g2) | Paquito | L | 13:44 | 904 |
| 1072 (g1) | Paquito | L | 23:25 | 10,635 |
| 1077 (g1) | Paquito+Eudora | W | 13:52 | 25,877 |
| 1083 (g3) | neither (Paquito absent) | W | 13:48 | 29,413 |

Reading: the same core produces both fast tower-heavy wins and fast/long losses; tower damage varies with opponent and game flow. The pilot insight's "consistent with" framing holds; "caused by" remains unsupported.

## INS-1037-LATE-SWING: is a close-gold win with less tower damage AE-specific?

| Series (game) | Winner | Gold diff | Winner tower damage | Loser tower damage |
|---|---|---:|---:|---:|
| 1037 (g1) | AE | +2,031 | 20,158 | 33,132 |
| 1074 (g2) | AE | +15,359 | 11,093 | 14,652 |
| 1078 (g2) | NAVI | +2,021 | 29,758 | 20,683 |

Reading: close-gold wins with lower tower damage occur for multiple teams, so the pattern is not an AE signature. The audit verdict `partially supported` stands.

## INS-1107-EARLY-CONVERSION: is tower damage a TLID signature?

| Series (game) | TLID result | Duration | TLID tower damage | Opponent tower damage |
|---|---|---:|---:|---:|
| 1107 (g1) | W | 14:47 | 32,659 | 1,902 |
| 1107 (g2) | W | 12:25 | 45,031 | 6,534 |
| 1044 (g1) | L | 25:32 | 15,436 | 19,411 |
| 1044 (g2) | L | 22:38 | 33,466 | 15,652 |
| 1093 (g1-g2) | W | 13:58/21:20 | 27,523/13,364 | 2,198/25,114 |
| 1095 (g1-g2) | W | 14:22/13:56 | 38,784/23,296 | 2,838/12,086 |
| 1083 (g1-g3) | L/W/L | 21:06/22:03/13:48 | 4,724/32,820/29,413 | 33,351/24,909/0 |

Reading: TLID wins with both high and modest tower damage, and loses games with substantial tower damage. Tower damage is an outcome, not a signature, consistent with the pilot insight's stated limits.

## Scope note

This is a database-backed expansion of the counterexample set. It does not add transcript-verified observations, visual review, or new insights, and it does not claim full-season coverage. Game-offset/boundary tooling remains pending validation (see `analysis/evidence/game-offsets.json`).
