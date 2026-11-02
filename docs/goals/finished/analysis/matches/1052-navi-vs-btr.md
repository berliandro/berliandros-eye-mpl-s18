# NAVI 0–2 BTR — series 1052 (stratified expansion sample)

**Scope:** one series, source-mapping and result context. Source: `src-s18-w03d01`, W3D1, verified YouTube video `9c2wPhSYTGA`. Broadcast timestamps come from the one-to-one caption alignment.

**Result:** schedule row 1052 — NAVI 0–2 BTR. Game 1: BTR won in **17:06**, 8–1 kills. Game 2: BTR won in **13:21**, 11–5 kills. Source: `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`.

## Game-level database context

| Game | Winner | Duration | Map mode | Side (blue/red) | Series MVP |
|---:|---|---:|---|---|---|
| 1 | BTR | 17:06 | Dangerous Grass | NAVI blue / BTR red | Moreno |
| 2 | BTR | 13:21 | Flying Cloud | NAVI blue / BTR red | Moreno |

## Timeline and evidence

| Broadcast | Evidence | What is directly supported |
|---|---|---|
| 00:44:26 | `seg-src-s18-w03d01-L001122-L001123` | The caster introduces "match pertama kita di minggu yang ketiga... Jumat Navi Nation dan Biget Troopers", mapping the match to series 1052. |
| Game 1 end | `Q-TEAM-GAMES` | Database: 17:06, BTR 8–1 kills. |
| Game 2 end | `Q-TEAM-GAMES` | Database: 13:21, BTR 11–5 kills. |

> **Exact quote (source lines 1122–1123):** "pertama untuk match pertama kita / di minggu yang ketiga. Tapi sebelum itu"

## References

- `seg-src-s18-w03d01-L001122-L001123` — https://youtu.be/9c2wPhSYTGA?t=2666 (00:44:26)
- `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`
- Database snapshot `mpl-s18-db-20c5ea2c51f3`

## Limits

- Source-mapping only; no tactical insight claimed.
- Auto-captions contain ASR errors and no speaker labels.
- Broadcast timestamps are derived from auto-caption alignment.
- Game offsets for this series are boundary-verified at 2666s (medium confidence).
