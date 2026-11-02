# TLID 2–1 AE — series 1059 (stratified expansion sample)

**Scope:** one series, source-mapping and result context. Source: `src-s18-w03d03`, W3D3, verified YouTube video `3bAUu2t3FGI`. Broadcast timestamps come from the one-to-one caption alignment.

**Result:** schedule row 1059 — TLID 2–1 AE. Game 1: AE won in **13:27**, 14–5 kills. Game 2: TLID won in **13:07**, 10–4 kills. Game 3: TLID won in **11:54**, 17–3 kills. Source: `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`.

## Game-level database context

| Game | Winner | Duration | Map mode | Side (blue/red) | Series MVP |
|---:|---|---:|---|---|---|
| 1 | AE | 13:27 | Flying Cloud | TLID blue / AE red | JOOOOO |
| 2 | TLID | 13:07 | Dangerous Grass | AE blue / TLID red | JOOOOO |
| 3 | TLID | 11:54 | Broken Walls | AE blue / TLID red | JOOOOO |

## Timeline and evidence

| Broadcast | Evidence | What is directly supported |
|---|---|---|
| 06:15:02 | `seg-src-s18-w03d03-L007749-L007750` | The caster introduces "match penutupan antara Alter Ego melawan Team Liquid Indonesia", mapping the match to series 1059. |
| Game 1 end | `Q-TEAM-GAMES` | Database: 13:27, AE 14–5 kills. |
| Game 2 end | `Q-TEAM-GAMES` | Database: 13:07, TLID 10–4 kills. |
| Game 3 end | `Q-TEAM-GAMES` | Database: 11:54, TLID 17–3 kills. |

> **Exact quote (source lines 7749–7750):** "akan lihat di match penutupan antara / Alter Ego melawan Team Liquid Indonesia."

## References

- `seg-src-s18-w03d03-L007749-L007750` — https://youtu.be/3bAUu2t3FGI?t=22502 (06:15:02)
- `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`
- Database snapshot `mpl-s18-db-20c5ea2c51f3`

## Limits

- Source-mapping only; no tactical insight claimed.
- Auto-captions contain ASR errors and no speaker labels.
- Broadcast timestamps are derived from auto-caption alignment.
- Game offsets for this series are boundary-verified at 22502s (medium confidence).
- Game 3's 11:54 duration is short; map mode recorded as Broken Walls.
