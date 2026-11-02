# NAVI 0–2 BTR — series 1106 (stratified expansion sample)

**Scope:** one series, source-mapping and result context. Source: `src-s18-w09d03`, W9D3, verified YouTube video `hY0Upem95uo`. Broadcast timestamps come from the one-to-one caption alignment.

**Result:** schedule row 1106 — NAVI 0–2 BTR. Game 1: BTR won in **11:26**, 18–5 kills. Game 2: BTR won in **23:00**, 16–11 kills. Source: `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`.

## Game-level database context

| Game | Winner | Duration | Map mode | Side (blue/red) | Series MVP |
|---:|---|---:|---|---|---|
| 1 | BTR | 11:26 | Revealing Wisps | NAVI blue / BTR red | Shogun |
| 2 | BTR | 23:00 | Flying Cloud | BTR blue / NAVI red | Shogun |

## Timeline and evidence

| Broadcast | Evidence | What is directly supported |
|---|---|---|
| 03:38:13 | `seg-src-s18-w09d03-L005070-L005071` | The caster introduces "match antara Navi melawan Bron", mapping the match to series 1106. |
| Game 1 end | `Q-TEAM-GAMES` | Database: 11:26, BTR 18–5 kills. |
| Game 2 end | `Q-TEAM-GAMES` | Database: 23:00, BTR 16–11 kills. |

> **Exact quote (source lines 5070–5071):** "match antara Navi melawan Bron. Silakan / ker."

## References

- `seg-src-s18-w09d03-L005070-L005071` — https://youtu.be/hY0Upem95uo?t=13093 (03:38:13)
- `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`
- Database snapshot `mpl-s18-db-20c5ea2c51f3`

## Limits

- Source-mapping only; no tactical insight claimed.
- Auto-captions contain ASR errors and no speaker labels.
- Broadcast timestamps are derived from auto-caption alignment.
- Game offsets for this series are boundary-verified at 13093s (medium confidence).
- "Bron" is an ASR spelling of BTR and is not joined to a database handle.
- Series 1106 is a BTR 2–0 win and appears in no existing insight; it is added for coverage.
