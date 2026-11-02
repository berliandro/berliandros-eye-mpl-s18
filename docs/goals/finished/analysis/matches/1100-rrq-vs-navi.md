# RRQ 1–2 NAVI — series 1100 (stratified expansion sample)

**Scope:** one series, source-mapping and result context. Source: `src-s18-w09d01`, W9D1, verified YouTube video `-QC1gIugHrM`. Broadcast timestamps come from the one-to-one caption alignment.

**Result:** schedule row 1100 — RRQ 1–2 NAVI. Game 1: RRQ won in **13:48**, 15–5 kills. Game 2: NAVI won in **11:53**, 19–1 kills. Game 3: NAVI won in **19:19**, 13–6 kills. Source: `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`.

## Game-level database context

| Game | Winner | Duration | Map mode | Side (blue/red) | Series MVP |
|---:|---|---:|---|---|---|
| 1 | RRQ | 13:48 | Flying Cloud | RRQ blue / NAVI red | Aprho |
| 2 | NAVI | 11:53 | Flying Cloud | RRQ blue / NAVI red | Aprho |
| 3 | NAVI | 19:19 | Revealing Wisps | NAVI blue / RRQ red | Aprho |

## Timeline and evidence

| Broadcast | Evidence | What is directly supported |
|---|---|---|
| 00:44:10 | `seg-src-s18-w09d01-L000688-L000689` | The caster introduces "Match pertama kita, ya antara Navi dan juga RRQ", mapping the match to series 1100. |
| Game 1 end | `Q-TEAM-GAMES` | Database: 13:48, RRQ 15–5 kills. |
| Game 2 end | `Q-TEAM-GAMES` | Database: 11:53, NAVI 19–1 kills. |
| Game 3 end | `Q-TEAM-GAMES` | Database: 19:19, NAVI 13–6 kills. |

> **Exact quote (source lines 688–689):** "Match pertama kita, ya antara Navi dan / juga RRQ. Ada player siapa yang akan"

## References

- `seg-src-s18-w09d01-L000688-L000689` — https://youtu.be/-QC1gIugHrM?t=2650 (00:44:10)
- `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`
- Database snapshot `mpl-s18-db-20c5ea2c51f3`

## Limits

- Source-mapping only; no tactical insight claimed.
- Auto-captions contain ASR errors and no speaker labels.
- Broadcast timestamps are derived from auto-caption alignment.
- Game offsets for this series are boundary-verified at 2650s (medium confidence).
