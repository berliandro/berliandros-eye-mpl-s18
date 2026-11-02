# DEWA 0–2 BTR — series 1045 (stratified expansion sample)

**Scope:** one series, source-mapping and result context. Source: `src-s18-w02d01`, W2D1, verified YouTube video `O1vhySUmgj0`. Broadcast timestamps come from the one-to-one caption alignment.

**Result:** schedule row 1045 — DEWA 0–2 BTR. Game 1: BTR won in **11:49**, 9–3 kills. Game 2: BTR won in **23:30**, 14–16 kills (BTR). Source: `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`.

## Game-level database context

| Game | Winner | Duration | Map mode | Side (blue/red) | Series MVP |
|---:|---|---:|---|---|---|
| 1 | BTR | 11:49 | Flying Cloud | DEWA blue / BTR red | Shogun |
| 2 | BTR | 23:30 | Dangerous Grass | BTR blue / DEWA red | Shogun |

## Timeline and evidence

| Broadcast | Evidence | What is directly supported |
|---|---|---|
| 03:22:06 | `seg-src-s18-w02d01-L004853-L004854` | The caster introduces "match antara BTR dan juga Dewa United", mapping the second W2D1 match to series 1045. |
| Game 1 end | `Q-TEAM-GAMES` | Database: 11:49, BTR 9–3, 39,994 vs 0 tower damage (BTR). |
| Game 2 end | `Q-TEAM-GAMES` | Database: 23:30, BTR 14–16, 22,064 vs 48,383 tower damage (DEWA). |

> **Exact quote (source lines 4853–4854):** "ngelihat bagaimana match antara BTR dan / juga Deo United. Let's go."

## References

- `seg-src-s18-w02d01-L004853-L004854` — https://youtu.be/O1vhySUmgj0?t=12126 (03:22:06)
- `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`
- Database snapshot `mpl-s18-db-20c5ea2c51f3`

## Limits

- Source-mapping only; no tactical insight claimed.
- Auto-captions contain ASR errors and no speaker labels.
- Broadcast timestamps are derived from auto-caption alignment.
- Game offsets for this series are boundary-verified at 12126s (medium confidence).
