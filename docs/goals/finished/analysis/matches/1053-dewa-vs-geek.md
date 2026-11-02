# DEWA 2–0 GEEK — series 1053 (stratified expansion sample)

**Scope:** one series, source-mapping and result context. Source: `src-s18-w03d01`, W3D1, verified YouTube video `9c2wPhSYTGA`. Broadcast timestamps come from the one-to-one caption alignment.

**Result:** schedule row 1053 — DEWA 2–0 GEEK. Game 1: DEWA won in **13:19**, 13–12 kills. Game 2: DEWA won in **10:38**, 18–1 kills. Source: `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`.

## Game-level database context

| Game | Winner | Duration | Map mode | Side (blue/red) | Series MVP |
|---:|---|---:|---|---|---|
| 1 | DEWA | 13:19 | Dangerous Grass | DEWA blue / GEEK red | Hazle |
| 2 | DEWA | 10:38 | Broken Walls | GEEK blue / DEWA red | Hazle |

## Timeline and evidence

| Broadcast | Evidence | What is directly supported |
|---|---|---|
| 03:20:43 | `seg-src-s18-w03d01-L004622-L004623` | The caster introduces "Match kedua akan ada Dewa United versus GeekF", mapping the match to series 1053. |
| Game 1 end | `Q-TEAM-GAMES` | Database: 13:19, DEWA 13–12 kills. |
| Game 2 end | `Q-TEAM-GAMES` | Database: 10:38, DEWA 18–1 kills. |

> **Exact quote (source lines 4622–4623):** "sampai situ saja ya. Oke. Oke. Match / kedua akan ada Dewa United versus GeekF."

## References

- `seg-src-s18-w03d01-L004622-L004623` — https://youtu.be/9c2wPhSYTGA?t=12043 (03:20:43)
- `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`
- Database snapshot `mpl-s18-db-20c5ea2c51f3`

## Limits

- Source-mapping only; no tactical insight claimed.
- Auto-captions contain ASR errors and no speaker labels.
- Broadcast timestamps are derived from auto-caption alignment.
- Game offsets for this series are boundary-verified at 12043s (medium confidence).
- "GeekF" is an ASR spelling of Geek Fam and is not joined to a database handle.
- Series 1053 is a DEWA 2–0 win and appears in no existing insight; added for coverage.
- Game 2's 10:38 duration is very short for an 18–1 game.
