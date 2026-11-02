# GEEK 2–1 ONIC — series 1069 (stratified expansion sample)

**Scope:** one series, source-mapping and result context. Source: `src-s18-w05d01`, W5D1, verified YouTube video `TeegcSSZJbI`. Broadcast timestamps come from the one-to-one caption alignment.

**Result:** schedule row 1069 — GEEK 2–1 ONIC. Game 1: GEEK won in **13:40**, 9–4 kills. Game 2: ONIC won in **16:43**, 17–3 kills. Game 3: GEEK won in **14:03**, 17–2 kills. Source: `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`.

## Game-level database context

| Game | Winner | Duration | Map mode | Side (blue/red) | Series MVP |
|---:|---|---:|---|---|---|
| 1 | GEEK | 13:40 | Dangerous Grass | GEEK blue / ONIC red | Maykids |
| 2 | ONIC | 16:43 | Broken Walls | ONIC blue / GEEK red | Maykids |
| 3 | GEEK | 14:03 | Broken Walls | GEEK blue / ONIC red | Maykids |

## Timeline and evidence

| Broadcast | Evidence | What is directly supported |
|---|---|---|
| 00:29:05 | `seg-src-s18-w05d01-L000248-L000249` | The caster introduces "pertandingan antara Onic Esports melawan GeekFCs", mapping the match to series 1069. |
| Game 1 end | `Q-TEAM-GAMES` | Database: 13:40, GEEK 9–4, 22,653 vs 11,748 tower damage (GEEK). |
| Game 2 end | `Q-TEAM-GAMES` | Database: 16:43, ONIC 17–3, 42,234 vs 3,276 tower damage (ONIC). |
| Game 3 end | `Q-TEAM-GAMES` | Database: 14:03, GEEK 17–2, 32,043 vs 2,675 tower damage (GEEK). |

> **Exact quote (source lines 248–249):** "pertandingan antara Onic Esports melawan / GeekFCs. Silakan."

## References

- `seg-src-s18-w05d01-L000248-L000249` — https://youtu.be/TeegcSSZJbI?t=1745 (00:29:05)
- `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`
- Database snapshot `mpl-s18-db-20c5ea2c51f3`

## Limits

- Source-mapping only; no tactical insight claimed.
- Auto-captions contain ASR errors and no speaker labels.
- Broadcast timestamps are derived from auto-caption alignment.
- Game offsets for this series are boundary-verified at 1745s (medium confidence).
