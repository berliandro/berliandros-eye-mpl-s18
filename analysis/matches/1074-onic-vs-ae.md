# ONIC 0–2 AE — series 1074 (stratified expansion sample)

**Scope:** one series, source-mapping and result context. Source: `src-s18-w05d03`, W5D3, verified YouTube video `YPbOKyQltIo`. Broadcast timestamps come from the one-to-one caption alignment.

**Result:** schedule row 1074 — ONIC 0–2 AE. Game 1: AE won in **16:17**, 12–6 kills. Game 2: AE won in **27:06**, 28–26 kills. Source: `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`.

## Game-level database context

| Game | Winner | Duration | Map mode | Side (blue/red) | Series MVP |
|---:|---|---:|---|---|---|
| 1 | AE | 16:17 | Broken Walls | ONIC blue / AE red | Hijumee |
| 2 | AE | 27:06 | Expanding Rivers | AE blue / ONIC red | Hijumee |

## Timeline and evidence

| Broadcast | Evidence | What is directly supported |
|---|---|---|
| 03:25:28 | `seg-src-s18-w05d03-L004370-L004371` | The caster introduces "match berikut ini melawan Onik", mapping the match to series 1074. |
| Game 1 end | `Q-TEAM-GAMES` | Database: 16:17, AE 12–6 kills. |
| Game 2 end | `Q-TEAM-GAMES` | Database: 27:06, AE 28–26 kills. |

> **Exact quote (source lines 4370–4371):** "ya untuk match berikut ini melawan Onik. / Thank you guys for this interview. Good"

## References

- `seg-src-s18-w05d03-L004370-L004371` — https://youtu.be/YPbOKyQltIo?t=12328 (03:25:28)
- `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`
- Database snapshot `mpl-s18-db-20c5ea2c51f3`

## Limits

- Source-mapping only; no tactical insight claimed.
- Auto-captions contain ASR errors and no speaker labels.
- Broadcast timestamps are derived from auto-caption alignment.
- Game offsets for this series are boundary-verified at 12328s (medium confidence).
- The 27:06 game 2 is a close game and appears in the INS-1037 counterexample set (close-gold winner with less tower damage).
