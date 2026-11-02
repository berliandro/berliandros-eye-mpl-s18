# NAVI 2–0 DEWA — series 1060 (stratified expansion sample)

**Scope:** one series, source-mapping and result context. Source: `src-s18-w04d01`, W4D1, verified YouTube video `W-LSKxUkUi4`. Broadcast timestamps come from the one-to-one caption alignment.

**Result:** schedule row 1060 — NAVI 2–0 DEWA. Game 1: NAVI won in **14:23**, 10–3 kills. Game 2: NAVI won in **15:17**, 14–4 kills. Source: `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`.

## Game-level database context

| Game | Winner | Duration | Map mode | Side (blue/red) | Series MVP |
|---:|---|---:|---|---|---|
| 1 | NAVI | 14:23 | Dangerous Grass | NAVI blue / DEWA red | Coolfire |
| 2 | NAVI | 15:17 | Flying Cloud | NAVI blue / DEWA red | Coolfire |

## Timeline and evidence

| Broadcast | Evidence | What is directly supported |
|---|---|---|
| 00:27:18 | `seg-src-s18-w04d01-L000412-L000413` | The caster introduces "match pertama pembuka di minggu yang keempat... Dewa akan menurunkan kin pasti dengan Hazel", mapping the match to series 1060. |
| Game 1 end | `Q-TEAM-GAMES` | Database: 14:23, NAVI 10–3 kills. |
| Game 2 end | `Q-TEAM-GAMES` | Database: 15:17, NAVI 14–4 kills. |

> **Exact quote (source lines 412–413):** "diturunkan untuk match pertama pembuka / di minggu yang keempat. Bagi teman-teman"

## References

- `seg-src-s18-w04d01-L000412-L000413` — https://youtu.be/W-LSKxUkUi4?t=1638 (00:27:18)
- `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`
- Database snapshot `mpl-s18-db-20c5ea2c51f3`

## Limits

- Source-mapping only; no tactical insight claimed.
- Auto-captions contain ASR errors and no speaker labels.
- Broadcast timestamps are derived from auto-caption alignment.
- Game offsets for this series are boundary-verified at 1638s (medium confidence).
