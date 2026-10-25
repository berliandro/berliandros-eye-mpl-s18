# ONIC 0–2 TLID — series 1107 (pilot)

**Scope:** one series, game 1 early map pressure/objective context and result. Source: `src-s18-w09d03`, W9D3, verified YouTube video `hY0Upem95uo`. Broadcast timestamps are derived from the one-to-one caption alignment.

**Result:** schedule row 1107 — ONIC 0–2 TLID. Game 1: TLID won in **14:47**, 14–3 kills, 49,124 vs 39,093 gold (+10,031), 32,659 vs 1,902 tower damage. Game 2: TLID won in **12:25**, 11–7 kills, 45,031 vs 6,534 tower damage. Source: `OBS-1107-G1-DB` (`Q-MATCH-RESULT`, `Q-MATCH-DETAIL`, `Q-GAMES`, `Q-TEAM-GAMES`, `Q-GAME-PICKS`).

> **Database orientation warning:** `matches` stores TLID/ONIC 2–0 but `matches.winner = 'team_b'`; that is schedule orientation (ONIC/TLID, 0–2, winner `team_b` = TLID), not a statement that ONIC won. This report uses `schedule_all` and the score. See `OBS-LINEAGE-WINNER`.

## Timeline and evidence

| Broadcast | Evidence | What is directly supported |
|---|---|---|
| 06:53:48–06:54:10 | `OBS-1107-ROTATION`, `seg-src-s18-w09d03-L009584-L009589` | The caster highlights early rotations toward Aran to limit ONIC’s map control, naming Drichel among TLID’s counterplay pieces. |
| 07:06:00–07:06:10 | `OBS-1107-TURTLE`, `seg-src-s18-w09d03-L009941-L009946` | The caster links TLID’s Rapid Boots rotations to contesting the healing Turtle and shutting down ONIC’s snowball. |
| 07:04:51 | `OBS-1107-VISUAL`, `VF-1107-early` | Visible: game clock **5:08**, TLID **14.0K** vs ONIC **13.1K** gold, top-lane fight. |
| 07:05:10 | `OBS-1107-VISUAL`, `VF-1107-item` | Visible: game clock **5:27**, TLID **15.3K** vs ONIC **13.6K**, “FIRST ITEM PRIORITY DRICHEL” overlay. |
| 07:12:41 | `OBS-1107-VISUAL`, `VF-1107-mid` | Visible: game clock **12:58**, TLID **40.6K** vs ONIC **34.7K**, “SEASON 18 40 LORD KILL KEVIN” milestone overlay. The milestone is **not** evidence of a current Lord. |
| 07:46:42 | `OBS-1107-SOURCE-MAP`, `seg-src-s18-w09d03-L011191-L011193` | The caster calls Team Liquid regular-season champion after a “2-0 yang solid” over Onic. |
| Game 1/2 end | `OBS-1107-G1-DB` | Database: 14:47 and 12:25 wins; large tower-damage gaps. |

> **Exact quote (source lines 9584–9589):** “early rotasi ke arah Aran. Wah, kembali / lagi ya poin pentingnya ada di Aran / untuk batasi map control. / Yap, memaksimalkan unico, Lione dan juga / Drichel untuk meng-counter gameplay ONIC / nih. Siapa yang lebih agresif berarti”
>
> **Working translation (not source):** “early rotation toward Aran. The important point is again Aran, to limit map control. Maximize Unico, Lione and also Drichel to counter ONIC’s gameplay. Whoever is more aggressive…”

> **Exact quote (source lines 9941–9946):** “Iya ya, rotasi cepat ya, empat agility / Rapid Boots. / Iya. Ngincer healing turtle menangin / dulu earlynya menangin healing / turtle-nya. Jadi power snowball dari / nolanya bisa dikatakan mati.”
>
> **Working translation (not source):** “yes, fast rotation, four agility Rapid Boots. Going for the healing Turtle, winning the early healing Turtle; so Nolan’s snowball power can be said to be dead.”

## Insight

**INS-1107-EARLY-CONVERSION — `partially-supported`, one game.**

TLID’s game-1 win was **fast and structure-heavy**. The commentary describes early rotations/Rapid Boots and Turtle pressure; the reviewed frames show TLID with a 1.5–1.7k gold lead at 5:27 and a 5.9k lead at 12:58; the database records 32.7k vs 1.9k tower damage in a 14:47 win. This supports a descriptive early-pressure-to-structures reading for this game. It does not prove that the rotations caused the structures, and it is not a season-long rule.

**Counterexamples (`OBS-1107-COUNTER`, `Q-TLID-TOWER-GAMES`):** TLID also lost games with substantial tower damage (1044 games 1–2, 1083 game 2, 1093 game 2) and won games with lower tower damage (for example 1095 game 2). Tower damage is an outcome, not a signature that guarantees a win.

**Alternative explanations:** ONIC draft/execution errors, TLID’s draft matchup, or a snowball after one fight. The “40 LORD KILL” banner is a season milestone, not a current objective. The 07:06:20 capture was a YouTube Premium promotional overlay and was rejected; it is not used.

**Coaching question:** which early rotation/Turtle setups consistently create outer-turret damage before six minutes, and how can opponents punish the Rapid Boots investment?

## References

- `seg-src-s18-w09d03-L009584-L009589` — https://youtu.be/hY0Upem95uo?t=24828 (06:53:48)
- `seg-src-s18-w09d03-L009941-L009946` — https://youtu.be/hY0Upem95uo?t=25560 (07:06:00)
- `seg-src-s18-w09d03-L011191-L011193` — https://youtu.be/hY0Upem95uo?t=28002 (07:46:42)
- Frames: `VF-1107-early` (07:04:51.481), `VF-1107-item` (07:05:10.920), `VF-1107-mid` (07:12:41.281); local ignored cache plus sidecars
- `OBS-1107-SOURCE-MAP`, `OBS-1107-ROTATION`, `OBS-1107-TURTLE`, `OBS-1107-G1-DB`, `OBS-1107-VISUAL`, `OBS-1107-COUNTER`
- `Q-MATCH-RESULT`, `Q-MATCH-DETAIL`, `Q-GAMES`, `Q-TEAM-GAMES`, `Q-GAME-PICKS`, `Q-TLID-TOWER-GAMES`
- Database snapshot `mpl-s18-db-1fb1768560e1`

## Limits

- One game, one broadcast, selected frames; no full clip, communications, vision or intent.
- Broadcast timestamps are derived from auto-caption cue alignment, not native transcript timestamps.
- The database has no per-game objective counts; “Turtle” and “Lord” in the transcript are commentary.
- “40 LORD KILL” is a season milestone overlay, not a current-objective indicator.
- Tower damage is a derived team aggregate and an outcome, not a causal measure.
