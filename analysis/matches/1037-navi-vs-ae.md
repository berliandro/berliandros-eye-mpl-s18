# NAVI 0–2 AE — series 1037 (pilot)

**Scope:** one series, game 1 turning-point sequence and result. Source: `src-s18-w01d01`, W1D1, verified YouTube video `40fehk2f4_E`. Broadcast timestamps are derived from the one-to-one caption alignment.

**Result:** schedule row 1037 — NAVI 0–2 AE. Game 1: AE won in **22:42**, 21–16 kills; AE 72,200 gold vs NAVI 70,169 (+2,031); AE tower damage 20,158 vs NAVI 33,132. Game 2: AE won in 11:27. Source: `OBS-1037-G1-DB` (`Q-MATCH-RESULT`, `Q-MATCH-DETAIL`, `Q-GAMES`, `Q-TEAM-GAMES`).

> **Database orientation warning:** in the `matches` table this series is stored as AE/NAVI, 2–0, but `matches.winner = 'team_b'` — that is schedule orientation (NAVI/AE, 0–2, winner `team_b` = AE), not a statement that NAVI won. This report uses `schedule_all` and the score. See `OBS-LINEAGE-WINNER`.

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
- Database snapshot `mpl-s18-db-1fb1768560e1`

## Limits

- One game, one broadcast, one camera/replay selection; no full clip or communications.
- Auto-captions: ASR errors, no speaker labels, possible missing context.
- Broadcast overlay names do not match database handles; no player identity join was made.
- A single reviewed frame cannot prove the full 1v3 or the reason NAVI lost.
