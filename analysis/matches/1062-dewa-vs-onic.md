# DEWA 2–1 ONIC — series 1062 (stratified expansion sample)

**Scope:** one series, source-mapping and result context. Source: `src-s18-w04d02`, W4D2, verified YouTube video `-M1_bwTRlHk`. Broadcast timestamps come from the one-to-one caption alignment.

**Result:** schedule row 1062 — DEWA 2–1 ONIC. Game 1: DEWA won in **13:45**, 13–0 kills. Game 2: ONIC won in **18:34**, 21–6 kills. Game 3: DEWA won in **13:05**, 11–1 kills. Source: `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`.

## Game-level database context

| Game | Winner | Duration | Map mode | Side (blue/red) | Series MVP |
|---:|---|---:|---|---|---|
| 1 | DEWA | 13:45 | Broken Walls | DEWA blue / ONIC red | Hazle |
| 2 | ONIC | 18:34 | Broken Walls | ONIC blue / DEWA red | Hazle |
| 3 | DEWA | 13:05 | Dangerous Grass | DEWA blue / ONIC red | Hazle |

## Timeline and evidence

| Broadcast | Evidence | What is directly supported |
|---|---|---|
| 00:41:00 | `seg-src-s18-w04d02-L000908-L000909` | The caster introduces "match pertama ya. Dewa United versus ONIC Shane", mapping the match to series 1062. |
| Game 1 end | `Q-TEAM-GAMES` | Database: 13:45, DEWA 13–0 kills. |
| Game 2 end | `Q-TEAM-GAMES` | Database: 18:34, ONIC 21–6 kills. |
| Game 3 end | `Q-TEAM-GAMES` | Database: 13:05, DEWA 11–1 kills. |

> **Exact quote (source lines 908–909):** "match pertama ya. Dewa United versus / ONIC Shane ini debute berarti ya untuk"

## References

- `seg-src-s18-w04d02-L000908-L000909` — https://youtu.be/-M1_bwTRlHk?t=2460 (00:41:00)
- `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`
- Database snapshot `mpl-s18-db-20c5ea2c51f3`

## Limits

- Source-mapping only; no tactical insight claimed.
- Auto-captions contain ASR errors and no speaker labels.
- Broadcast timestamps are derived from auto-caption alignment.
- Game offsets for this series are boundary-verified at 2460s (medium confidence).
- "Shane" is an ASR spelling and is not joined to a database handle.
- Series 1062 is a DEWA 2–1 win and appears in no existing insight; added for coverage.
