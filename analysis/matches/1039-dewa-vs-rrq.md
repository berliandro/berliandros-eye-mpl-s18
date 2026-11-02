# DEWA 1–2 RRQ — series 1039 (stratified expansion sample)

**Scope:** one series, source-mapping and result context. Source: `src-s18-w01d02`, W1D2, verified YouTube video `tpgvzhEO1Qc`. Broadcast timestamps come from the one-to-one caption alignment (`youtube-auto-caption-alignment-v1`).

**Result:** schedule row 1039 — DEWA 1–2 RRQ. Game 1: RRQ won in **14:02**, 10–1 kills. Game 2: DEWA won in **19:43**, 25–14 kills. Game 3: RRQ won in **22:31**, 15–19 kills (RRQ). Source: `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`.

## Game-level database context

| Game | Winner | Duration | Map mode | Side (blue/red) | Per-game VOD | Series MVP |
|---:|---|---:|---|---|---|---|
| 1 | RRQ | 14:02 | Broken Walls | DEWA blue / RRQ red | https://www.youtube.com/watch?v=... (per-game VOD recorded) | Sutsujin |
| 2 | DEWA | 19:43 | Expanding Rivers | DEWA blue / RRQ red | (per-game VOD recorded) | Sutsujin |
| 3 | RRQ | 22:31 | Broken Walls | DEWA blue / RRQ red | (per-game VOD recorded) | Sutsujin |

Exact per-game VOD URLs are in `games.vod_url` for this series; see `Q-GAMES`.

## Timeline and evidence

| Broadcast | Evidence | What is directly supported |
|---|---|---|
| 03:19:06 | `seg-src-s18-w01d02-L005192-L005193` | The caster introduces "match kedua kita antara Dewa dan juga RRQ", mapping the second W1D2 match to series 1039. |
| Game 1 end | `Q-TEAM-GAMES` | Database: 14:02, RRQ 10–1, 43,506 vs 2,907 tower damage (RRQ). |
| Game 2 end | `Q-TEAM-GAMES` | Database: 19:43, DEWA 25–14, 32,565 vs 10,087 tower damage (DEWA). |
| Game 3 end | `Q-TEAM-GAMES` | Database: 22:31, RRQ 15–19 kills, 23,455 vs 21,673 tower damage (RRQ). |

> **Exact quote (source lines 5192–5193):** "Yeay. Ini dia match kedua kita antara / Dewa dan juga RRQ. Yehe. Menyambut"
>
> **Working translation (not source):** "Yay. Here is our second match between Dewa and also RRQ."

## References

- `seg-src-s18-w01d02-L005192-L005193` — https://youtu.be/tpgvzhEO1Qc?t=11946 (03:19:06)
- `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES` in `analysis/evidence/query-catalog.json`
- Database snapshot `mpl-s18-db-20c5ea2c51f3`

## Limits

- Source-mapping only; no tactical insight is claimed from this series.
- Auto-captions contain ASR errors and no speaker labels.
- Broadcast timestamps are derived from auto-caption alignment, not native transcript timestamps.
- Game offsets for this series are boundary-verified at 11946s (medium confidence); per-game start times within the series are not yet mapped.
