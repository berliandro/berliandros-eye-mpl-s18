# EVOS 2–0 RRQ — series 1036 (pilot)

**Scope:** one series, game 1 draft/objective sequence and result. Source: `src-s18-w01d01`, W1D1, verified YouTube video `40fehk2f4_E`. Broadcast timestamps below are derived from the one-to-one caption alignment (`youtube-auto-caption-alignment-v1`).

**Result:** schedule row 1036 — EVOS 2–0 RRQ. Game 1: EVOS won in **16:51**, 11–7 kills, 22,472 vs 1,252 tower damage. Game 2: EVOS won in **24:40**. Source: `OBS-1036-G1-DB` (`Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`, `Q-GAME-PICKS`).

## Game-level database context

| Game | Winner | Duration | Map mode | Side (blue/red) | Per-game VOD | Series MVP |
|---:|---|---:|---|---|---|---|
| 1 | EVOS | 16:51 | Broken Walls | EVOS blue / RRQ red | https://www.youtube.com/watch?v=SuqcHmHNTos | Alberttt |
| 2 | EVOS | 24:40 | Flying Cloud | RRQ blue / EVOS red | https://www.youtube.com/watch?v=7D7HZLDDKew | Alberttt |

## Timeline and evidence

| Broadcast | Evidence | What is directly supported |
|---|---|---|
| 00:39:29 | — | The caster enters the draft. |
| 00:42:18–00:42:33 | `OBS-1036-DRAFT`, `seg-src-s18-w01d01-L001016-L001020` | The caster calls the top-three draft an “identity draft” for early snowball and names Paquito/Eudora/Melissa as pressure pieces. This is commentary, not proof of intent. |
| 00:58:09–00:58:13 | `OBS-1036-LORD`, `seg-src-s18-w01d01-L001533-L001534` | The caster says EVOS has the Lord (“Lord ada di tangan”). This is a commentary claim, not an official objective count. |
| Game 1 end | `OBS-1036-G1-DB` | Database: 16:51, EVOS 11–7, 22,472 vs 1,252 tower damage. |
| Game 2 end | `OBS-1036-G1-DB` | Database: 24:40, EVOS win. |

> **Exact quote (source lines 1016–1020):** “identity draft yang sama-sama early / snowball. Pakito dan Yudora udah pasti / siap banget untuk membantai di early / game pengin menutup poin cepat apalagi / ada pemukul turetnya itu adalah Melisa”
>
> **Working translation (not source):** “an identity draft that is early snowball on both sides. Paquito and Eudora are surely ready to punish in the early game and want to close points quickly; the turret hitter is Melissa.”
>
> **ASR caveat:** “Pakito”/“Yudora” are auto-caption spellings; the database lineup contains **Paquito** (Alberttt) and **Eudora** (DrianW), plus Melissa (Erlan). The quotation is exact; the hero-name interpretation is cross-checked, not independently audio-verified.

## Insight

**INS-1036-EARLY-DRAFT — `cross-checked`, one-game execution observation.**

The caster’s early-snowball framing is **consistent with** the recorded composition and the fast, tower-heavy win: EVOS picked Paquito and Eudora, won game 1 in 16:51, and recorded 22,472 tower damage to RRQ’s 1,252. This is not evidence that the draft caused the win, and it is not a repeatable draft rule.

**Counterexamples (`OBS-1036-COUNTER`, `Q-EVOS-PAQUITO-EUDORA`):** EVOS used Paquito or Eudora in losses in 1055 game 2, 1066 game 2, 1077 game 1 and 1103 game 1; they also won game 2 of this series with the same core but took 24:40. Opponent, draft context and execution vary.

**Alternative explanations:** RRQ errors, matchup effects, early skirmish variance, or a general EVOS identity rather than a specific draft plan. The database tower-damage figure is a derived team aggregate, not an official objective count.

**Coaching question:** when EVOS draft Paquito/Eudora, which early objective and outer-turret timings actually convert the intended snowball, and which opposing drafts punish it?

## References

- `seg-src-s18-w01d01-L001016-L001020` — https://youtu.be/40fehk2f4_E?t=2538 (00:42:18)
- `seg-src-s18-w01d01-L001533-L001534` — https://youtu.be/40fehk2f4_E?t=3489 (00:58:09)
- `OBS-1036-DRAFT`, `OBS-1036-LORD`, `OBS-1036-G1-DB`, `OBS-1036-COUNTER`
- `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`, `Q-GAME-PICKS`, `Q-EVOS-PAQUITO-EUDORA` in `analysis/evidence/query-catalog.json`
- Database snapshot `mpl-s18-db-20c5ea2c51f3`

## Limits

- One game and one caster passage; no visual draft review and no full-game tactical review.
- Auto-captions contain ASR errors and no speaker labels.
- “Lord ada di tangan” is commentary; the database does not track objective counts.
- The transcript establishes what was said, not why the draft succeeded.
