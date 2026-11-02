# TLID 2–0 BTR — series 1080 (stratified expansion sample)

**Scope:** one series, source-mapping and result context. Source: `src-s18-w06d02`, W6D2, verified YouTube video `5tOPeDiETK0`. Broadcast timestamps come from the one-to-one caption alignment.

**Result:** schedule row 1080 — TLID 2–0 BTR. Game 1: TLID won in **12:30**, 19–1 kills. Game 2: TLID won in **10:03**, 17–2 kills. Source: `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`.

## Game-level database context

| Game | Winner | Duration | Map mode | Side (blue/red) | Series MVP |
|---:|---|---:|---|---|---|
| 1 | TLID | 12:30 | (not recorded) | TLID blue / BTR red | JOOOOO |
| 2 | TLID | 10:03 | (not recorded) | TLID blue / BTR red | JOOOOO |

## Timeline and evidence

| Broadcast | Evidence | What is directly supported |
|---|---|---|
| 06:35:17 | `seg-src-s18-w06d02-L010394-L010395` | The caster introduces "match terakhir untuk hari ini antara Bigetron dan juga tim Liquid ID", mapping the match to series 1080. |
| Game 1 end | `Q-TEAM-GAMES` | Database: 12:30, TLID 19–1 kills. |
| Game 2 end | `Q-TEAM-GAMES` | Database: 10:03, TLID 17–2 kills. |

> **Exact quote (source lines 10394–10395):** "match terakhir untuk hari ini antara / Bigetron dan juga tim Liquid ID. Karena"

## References

- `seg-src-s18-w06d02-L010394-L010395` — https://youtu.be/5tOPeDiETK0?t=23717 (06:35:17)
- `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`
- Database snapshot `mpl-s18-db-20c5ea2c51f3`

## Limits

- Source-mapping only; no tactical insight claimed.
- Auto-captions contain ASR errors and no speaker labels.
- Broadcast timestamps are derived from auto-caption alignment.
- Game offsets for this series are boundary-verified at 23717s (medium confidence).
- Map mode is not recorded for either game in the database (21/174 games lack map mode).
- Game 2's 10:03 duration is very short.
