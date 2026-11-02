# NAVI 2–1 GEEK — series 1047 (stratified expansion sample)

**Scope:** one series, source-mapping and result context. Source: `src-s18-w02d02`, W2D2, verified YouTube video `QsOUpAE-Jd8`. Broadcast timestamps come from the one-to-one caption alignment.

**Result:** schedule row 1047 — NAVI 2–1 GEEK. Game 1: NAVI won in **23:23**, 16–10 kills. Game 2: GEEK won in **20:40**, 13–8 kills. Game 3: NAVI won in **18:17**, 11–6 kills. Source: `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`.

## Game-level database context

| Game | Winner | Duration | Map mode | Side (blue/red) | Series MVP |
|---:|---|---:|---|---|---|
| 1 | NAVI | 23:23 | Flying Cloud | NAVI blue / GEEK red | Aprho |
| 2 | GEEK | 20:40 | Dangerous Grass | GEEK blue / NAVI red | Aprho |
| 3 | NAVI | 18:17 | Broken Walls | NAVI blue / GEEK red | Aprho |

## Timeline and evidence

| Broadcast | Evidence | What is directly supported |
|---|---|---|
| 03:18:06 | `seg-src-s18-w02d02-L004431-L004432` | The caster introduces "antara Navi dan juga GeekF", mapping the match to series 1047. |
| Game 1 end | `Q-TEAM-GAMES` | Database: 23:23, NAVI 16–10 kills. |
| Game 2 end | `Q-TEAM-GAMES` | Database: 20:40, GEEK 13–8 kills. |
| Game 3 end | `Q-TEAM-GAMES` | Database: 18:17, NAVI 11–6 kills. |

> **Exact quote (source lines 4431–4432):** "kedua yang akan segera berlangsung / antara Navi dan juga GeekF."

## References

- `seg-src-s18-w02d02-L004431-L004432` — https://youtu.be/QsOUpAE-Jd8?t=11886 (03:18:06)
- `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`
- Database snapshot `mpl-s18-db-20c5ea2c51f3`

## Limits

- Source-mapping only; no tactical insight claimed.
- Auto-captions contain ASR errors and no speaker labels.
- Broadcast timestamps are derived from auto-caption alignment.
- Game offsets for this series are boundary-verified at 11886s (medium confidence).
- "GeekF" is an ASR spelling of Geek Fam and is not joined to a database handle.
