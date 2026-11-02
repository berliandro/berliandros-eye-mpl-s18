# DEWA 2–0 AE — series 1081 (stratified expansion sample)

**Scope:** one series, source-mapping and result context. Source: `src-s18-w06d03`, W6D3, verified YouTube video `K30JsmMhQ4Q`. Broadcast timestamps come from the one-to-one caption alignment.

**Result:** schedule row 1081 — DEWA 2–0 AE. Game 1: DEWA won in **18:07**, 19–12 kills. Game 2: DEWA won in **14:28**, 17–12 kills. Source: `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`.

## Game-level database context

| Game | Winner | Duration | Map mode | Side (blue/red) | Series MVP |
|---:|---|---:|---|---|---|
| 1 | DEWA | 18:07 | (not recorded) | DEWA blue / AE red | QINN |
| 2 | DEWA | 14:28 | (not recorded) | AE blue / DEWA red | QINN |

## Timeline and evidence

| Broadcast | Evidence | What is directly supported |
|---|---|---|
| 00:30:00 | `seg-src-s18-w06d03-L000530-L000532` | The caster introduces "hello untuk Alterigo dan juga Dewa United... match pertama kita di hari Minggu ini", mapping the match to series 1081. |
| Game 1 end | `Q-TEAM-GAMES` | Database: 18:07, DEWA 19–12 kills. |
| Game 2 end | `Q-TEAM-GAMES` | Database: 14:28, DEWA 17–12 kills. |

> **Exact quote (source lines 530–532):** "hello untuk Alterigo dan juga Dewa / United ya yang akan membuka match / pertama kita di hari Minggu ini. Lalu"

## References

- `seg-src-s18-w06d03-L000530-L000532` — https://youtu.be/K30JsmMhQ4Q?t=1800 (00:30:00)
- `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`
- Database snapshot `mpl-s18-db-20c5ea2c51f3`

## Limits

- Source-mapping only; no tactical insight claimed.
- Auto-captions contain ASR errors and no speaker labels.
- Broadcast timestamps are derived from auto-caption alignment.
- Game offsets for this series are boundary-verified at 1800s (medium confidence).
- Map mode is not recorded for either game (21/174 games lack map mode).
- "Alterigo" is an ASR spelling of Alter Ego and is not joined to a database handle.
