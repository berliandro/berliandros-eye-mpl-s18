# RRQ 0–2 NAVI — series 1065 (stratified expansion sample)

**Scope:** one series, source-mapping and result context. Source: `src-s18-w04d03`, W4D3, verified YouTube video `nu3RfzQdsec`. Broadcast timestamps come from the one-to-one caption alignment.

**Result:** schedule row 1065 — RRQ 0–2 NAVI. Game 1: NAVI won in **13:54**, 13–1 kills. Game 2: NAVI won in **22:19**, 14–8 kills. Source: `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`.

## Game-level database context

| Game | Winner | Duration | Map mode | Side (blue/red) | Series MVP |
|---:|---|---:|---|---|---|
| 1 | NAVI | 13:54 | Expanding Rivers | RRQ blue / NAVI red | Coolfire |
| 2 | NAVI | 22:19 | Dangerous Grass | RRQ blue / NAVI red | Coolfire |

## Timeline and evidence

| Broadcast | Evidence | What is directly supported |
|---|---|---|
| 07:16:15 | `seg-src-s18-w04d03-L009983-L009984` | The caster introduces "match yang pertama ya antara Navi dan juga Arar", mapping the match to series 1065. |
| Game 1 end | `Q-TEAM-GAMES` | Database: 13:54, NAVI 13–1 kills. |
| Game 2 end | `Q-TEAM-GAMES` | Database: 22:19, NAVI 14–8 kills. |

> **Exact quote (source lines 9983–9984):** "dari match yang pertama ya antara Navi / dan juga Arar tadi ya kan ada match up"

## References

- `seg-src-s18-w04d03-L009983-L009984` — https://youtu.be/nu3RfzQdsec?t=26175 (07:16:15)
- `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`
- Database snapshot `mpl-s18-db-20c5ea2c51f3`

## Limits

- Source-mapping only; no tactical insight claimed.
- Auto-captions contain ASR errors and no speaker labels.
- Broadcast timestamps are derived from auto-caption alignment.
- Game offsets for this series are boundary-verified at 26175s (medium confidence).
- "Arar" is an ASR spelling of RRQ and is not joined to a database handle.
