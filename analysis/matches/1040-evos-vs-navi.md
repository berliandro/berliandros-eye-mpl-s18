# EVOS 1–2 NAVI — series 1040 (stratified expansion sample)

**Scope:** one series, source-mapping and result context. Source: `src-s18-w01d02`, W1D2, verified YouTube video `tpgvzhEO1Qc`. Broadcast timestamps come from the one-to-one caption alignment.

**Result:** schedule row 1040 — EVOS 1–2 NAVI. Game 1: NAVI won in **10:56**, 7–2 kills. Game 2: EVOS won in **13:50**, 12–3 kills. Game 3: NAVI won in **20:53**, 14–5 kills. Source: `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`.

## Game-level database context

| Game | Winner | Duration | Map mode | Side (blue/red) | Series MVP |
|---:|---|---:|---|---|---|
| 1 | NAVI | 10:56 | Broken Walls | EVOS blue / NAVI red | Karss |
| 2 | EVOS | 13:50 | Dangerous Grass | EVOS blue / NAVI red | Karss |
| 3 | NAVI | 20:53 | Dangerous Grass | EVOS blue / NAVI red | Karss |

## Timeline and evidence

| Broadcast | Evidence | What is directly supported |
|---|---|---|
| 06:41:07 | `seg-src-s18-w01d02-L010853-L010854` | The caster announces "Navi. Navi Nation ready. EVOS ready.", mapping the match to series 1040. |
| Game 1 end | `Q-TEAM-GAMES` | Database: 10:56, NAVI 7–2 kills. |
| Game 2 end | `Q-TEAM-GAMES` | Database: 13:50, EVOS 12–3 kills. |
| Game 3 end | `Q-TEAM-GAMES` | Database: 20:53, NAVI 14–5 kills. |

> **Exact quote (source lines 10853–10854):** "melakukan drafik antara EVOS dan juga / Navi. Navi Nation ready. EVOS ready."

## References

- `seg-src-s18-w01d02-L010853-L010854` — https://youtu.be/tpgvzhEO1Qc?t=24067 (06:41:07)
- `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`
- Database snapshot `mpl-s18-db-20c5ea2c51f3`

## Limits

- Source-mapping only; no tactical insight claimed.
- Auto-captions contain ASR errors and no speaker labels.
- Broadcast timestamps are derived from auto-caption alignment.
- Game offsets for this series are boundary-verified at 24067s (medium confidence).
- The quote is a draft announcement, not a full series introduction; the series start may be earlier.
- Series 1040 is an EVOS 1–2 loss and appears in no existing insight; added for coverage.
- Game 2 (13:50) appears in the INS-1036 counterexample set (EVOS Paquito win in 1040 game 2? Actually EVOS used Paquito in 1040 game 2 per the counterexample query).
