# NAVI 0–2 AE — series 1037 (pilot)

**Scope:** one series, game 1 turning-point sequence and result. Source: `src-s18-w01d01`, W1D1, verified YouTube video `40fehk2f4_E`. Broadcast timestamps are derived from the one-to-one caption alignment.

**Result:** schedule row 1037 — NAVI 0–2 AE. Game 1: AE won in **22:42**, 21–16 kills; AE 72,200 gold vs NAVI 70,169 (+2,031); AE tower damage 20,158 vs NAVI 33,132. Game 2: AE won in 11:27. Source: `OBS-1037-G1-DB` (`Q-MATCH-RESULT`, `Q-MATCH-DETAIL`, `Q-GAMES`, `Q-TEAM-GAMES`).

> **Database orientation note:** in the repaired `matches` table this series is stored as AE/NAVI, 2-0, with `matches.winner = 'team_a'` (AE). The schedule row is NAVI/AE, 0-2, with `schedule_all.winner = 'team_b'` (also AE). Both tables agree on the named winner; side tokens differ because team order differs. See `OBS-LINEAGE-WINNER`.

<!-- db-evidence:start -->
## Game-level database context

Database snapshot `mpl-s18-db-20c5ea2c51f3` · SHA-256 `20c5ea2c51f30d1a24cd2ce6927f0d182b47f951ebd8209f1aaef429941cf2ef`. Queries: `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`, `Q-MATCH-PLAYER-LINES`, `Q-GAME-PICKS`, `Q-GAME-BANS` (see `analysis/evidence/query-catalog.json`). These are source-reported scoreboard values, not official tournament tables.

**Series MVP (Liquipedia):** Yazukee.

### Game 1 — AE win · 22:42 · Dangerous Grass

Sides: AE blue / NAVI red · [VOD](https://www.youtube.com/watch?v=CGCbVSueZ7c)

| Team | K | D | A | Gold | Hero damage | Tower damage |
|---|---:|---:|---:|---:|---:|---:|
| AE | 21 | 16 | 53 | 72,200 | 294,598 | 20,158 |
| NAVI | 16 | 21 | 48 | 70,169 | 297,169 | 33,132 |

| Team | Player | Lane | Hero | K/D/A | KDA | Gold | Hero damage | Tower damage |
|---|---|---|---|---:|---:|---:|---:|---:|
| AE | Nino | EXP | Esmeralda | 4/1/9 | 13.0 | 12,643 | 56,555 | 235 |
| AE | Arfy | GOLD | Moskov | 5/3/8 | 4.33 | 17,003 | 76,572 | 13,962 |
| AE | Yazukee | JUNGLE | Paquito | 8/5/8 | 3.2 | 16,514 | 70,062 | 1,700 |
| AE | Hijumee | MID | Kimmy | 3/2/13 | 8.0 | 14,492 | 77,300 | 4,261 |
| AE | alekk | ROAM | Atlas | 1/5/15 | 3.2 | 11,548 | 14,109 | 0 |
| NAVI | Karss | EXP | Barats | 1/5/10 | 2.2 | 10,227 | 33,071 | 366 |
| NAVI | Zeonn | GOLD | Claude | 7/3/5 | 4.0 | 17,250 | 83,591 | 29,129 |
| NAVI | Andoryuuu | JUNGLE | Hirara | 5/5/8 | 2.6 | 17,103 | 72,065 | 961 |
| NAVI | Jiizee | MID | Lylia | 2/4/14 | 4.0 | 13,837 | 82,448 | 1,080 |
| NAVI | Aprho | ROAM | Valentina | 1/4/11 | 3.0 | 11,752 | 25,994 | 1,596 |

**Picks**

- AE: Nino (EXP, Esmeralda), Yazukee (JUNGLE, Paquito), Hijumee (MID, Kimmy), Arfy (GOLD, Moskov), alekk (ROAM, Atlas)
- NAVI: Karss (EXP, Barats), Andoryuuu (JUNGLE, Hirara), Jiizee (MID, Lylia), Zeonn (GOLD, Claude), Aprho (ROAM, Valentina)

**Bans:** A — Phoveus, Marcel, Kaja, Belerick, Mathilda · B — Freya, Fanny, Melissa, Uranus, Alice

### Game 2 — AE win · 11:27 · Flying Cloud

Sides: NAVI blue / AE red · [VOD](https://www.youtube.com/watch?v=Ap4igKgFkwU)

| Team | K | D | A | Gold | Hero damage | Tower damage |
|---|---:|---:|---:|---:|---:|---:|
| NAVI | 3 | 11 | 6 | 30,952 | 94,065 | 10,237 |
| AE | 11 | 3 | 29 | 40,327 | 160,801 | 29,278 |

| Team | Player | Lane | Hero | K/D/A | KDA | Gold | Hero damage | Tower damage |
|---|---|---|---|---:|---:|---:|---:|---:|
| NAVI | Karss | EXP | Barats | 0/3/1 | 0.33 | 4,816 | 16,989 | 0 |
| NAVI | Zeonn | GOLD | Brody | 2/1/1 | 3.0 | 8,065 | 14,481 | 6,657 |
| NAVI | Andoryuuu | JUNGLE | Paquito | 1/3/1 | 0.67 | 7,411 | 15,454 | 3,580 |
| NAVI | Jiizee | MID | Eudora | 0/1/2 | 2.0 | 5,648 | 35,158 | 0 |
| NAVI | Aprho | ROAM | Chou | 0/3/1 | 0.33 | 5,012 | 11,983 | 0 |
| AE | Nino | EXP | Carmilla | 2/1/6 | 8.0 | 6,670 | 11,845 | 1,228 |
| AE | Arfy | GOLD | Melissa | 4/0/5 | 9.0 | 10,132 | 57,348 | 24,665 |
| AE | Yazukee | JUNGLE | Hirara | 3/1/2 | 5.0 | 9,356 | 28,380 | 0 |
| AE | Hijumee | MID | Cecilion | 0/0/9 | 9.0 | 6,988 | 48,271 | 2,544 |
| AE | alekk | ROAM | Belerick | 2/1/7 | 9.0 | 7,181 | 14,957 | 841 |

**Picks**

- NAVI: Karss (EXP, Barats), Andoryuuu (JUNGLE, Paquito), Jiizee (MID, Eudora), Zeonn (GOLD, Brody), Aprho (ROAM, Chou)
- AE: Nino (EXP, Carmilla), Yazukee (JUNGLE, Hirara), Hijumee (MID, Cecilion), Arfy (GOLD, Melissa), alekk (ROAM, Belerick)

**Bans:** A — Fanny, Marcel, Uranus, Alice, Sora · B — Freya, Atlas, Esmeralda, Mathilda, Rafaela

Draft labels A/B are source draft order; picks are lane-order, not pick order.

**Transcript coverage:** none. This series is database-only; no broadcast quote, timestamp, or caster claim is made.

**Database limits:** no per-game objective counts, gold/damage timelines, vision, communications, or intent.
<!-- db-evidence:end -->

## Timeline and evidence

| Broadcast | Evidence | What is directly supported |
|---|---|---|
| 03:30:35–03:30:39 | `OBS-1037-SOURCE-MAP`, `seg-src-s18-w01d01-L005073-L005074` | The caster introduces “match yang kedua hari ini between Navi dan juga Alter Ego”, mapping the second W1D1 match to series 1037. |
| 04:14:00 | `OBS-1037-CLUTCH`, `seg-src-s18-w01d01-L006451-L006452` | The caster labels an AE play “the clutch 1v3 situation”. This is commentary; the quote alone does not prove the full sequence. |
| 04:14:06 | `OBS-1037-VISUAL`, `VF-1037-base` | Visible frame: game clock **21:08**, AE 17–15 NAVI, AE gold **63.9K** vs NAVI **65.8K**, AE defending its base. |
| 04:13:51 | `OBS-1037-VISUAL`, `VF-1037-replay` | Instant Replay banner labels an AE play “AE AFFAN … HAS SLAIN”. The broadcast name is not joined to a database handle. |
| 04:16:40–04:17:05 | `OBS-1037-DEFENSE`, `seg-src-s18-w01d01-L006524-L006532` | The caster says NAVI had a very large advantage, “three menghadapi satu pemain”, and describes NAVI’s defensive Lord attempt failing. |
| 04:16:11 | `VF-1037-post` | Post-game player-camera shot. It confirms the game ended, but is not used to prove the fight sequence. |
| Game 1 end | `OBS-1037-G1-DB` | Database: 22:42, AE 21–16, AE +2,031 gold, AE lower tower damage than NAVI. |

> **Exact quote (source lines 6451–6452):** “oleh Alter Ego Avon with the clutch 1v3 / situation”
>
> **Working translation (not source):** “by Alter Ego, Avon with the clutch 1v3 situation.”
>
> **ASR caveat:** “Avon” is an auto-caption spelling and is not mapped to a database player.

> **Exact quote (source lines 6524–6532):** “karena Navi punya sebuah keuntungan yang / sangat besar. / tiga menghadapi satu pemain. Tapi ini / pakit loh ya memang secara damage ini / udah ambrol sih langsung dan ternyata / itu [musik] berlanjut enggak berhenti / sampai di sana tetap berjalan sampai / mereka dapetin lord defensif juga / ternyata gak bisa berjalan dengan baik”
>
> **Working translation (not source):** “because NAVI had a very large advantage. Three against one player. But this is Paquito — the damage had already collapsed immediately, and it continued without stopping until they also got a defensive Lord, which apparently could not run well.”

## Insight

**INS-1037-LATE-SWING — `partially-supported`, one game.**

AE’s game-1 win is better described as a **late defensive swing** than wire-to-wire map control. The transcript describes a 1v3 stand and a failed NAVI Lord conversion; the reviewed frame shows AE defending base at 21:08 with a ~1.9k gold deficit; the final database line is a 2.0k gold win with less tower damage than NAVI (20,158 vs 33,132). The specific “1v3 turning point” remains caster framing, not a fully verified causal event.

**Counterexamples (`OBS-1037-COUNTER`, `Q-CLOSE-GOLD-WINNERS`):** close-gold games where the winner had less tower damage are not unique to 1037; 1074 game 2 and 1078 game 2 also appear. This weakens any claim that AE has a distinctive comeback signature from this one game.

**Alternative explanations:** a later NAVI macro mistake, a bad Lord call, a draft/execution difference, or the broadcast selecting a replay angle rather than the full fight. The frame does not show communications, vision or intent.

**Coaching question:** when defending base with a small gold deficit, what triggers AE’s counter-initiation, and how should opponents avoid overcommitting to the Lord?

## Audit

The skeptical audit is recorded as `AUD-1037-01` and expanded in `analysis/reports/audit-INS-1037-LATE-SWING.md`. Verdict: **partially supported** — the late-swing/base-defense reading is supported by transcript + frame + database; the exact 1v3 causal story is not fully verified.

## References

- `seg-src-s18-w01d01-L005073-L005074` — https://youtu.be/40fehk2f4_E?t=12635 (03:30:35)
- `seg-src-s18-w01d01-L006451-L006452` — https://youtu.be/40fehk2f4_E?t=15240 (04:14:00)
- `seg-src-s18-w01d01-L006524-L006532` — https://youtu.be/40fehk2f4_E?t=15400 (04:16:40)
- Frames: `VF-1037-replay` (04:13:51.476), `VF-1037-base` (04:14:06.335), `VF-1037-post` (04:16:11.480); local ignored cache plus sidecars
- `OBS-1037-SOURCE-MAP`, `OBS-1037-CLUTCH`, `OBS-1037-DEFENSE`, `OBS-1037-G1-DB`, `OBS-1037-VISUAL`, `OBS-1037-COUNTER`
- `Q-MATCH-RESULT`, `Q-MATCH-DETAIL`, `Q-GAMES`, `Q-TEAM-GAMES`, `Q-CLOSE-GOLD-WINNERS`
- Database snapshot `mpl-s18-db-20c5ea2c51f3`

## Limits

- One game, one broadcast, one camera/replay selection; no full clip or communications.
- Auto-captions: ASR errors, no speaker labels, possible missing context.
- Broadcast overlay names do not match database handles; no player identity join was made.
- A single reviewed frame cannot prove the full 1v3 or the reason NAVI lost.
