# MPL S18 hero meta — evidence report

**Scope:** all 174 games in the canonical snapshot. Pick, ban and win counts come from `Q-ALL-PICKS`, `Q-ALL-BANS` and `Q-ALL-HERO-STATS` (`mpl-s18-db-20c5ea2c51f3`). The database has no pick order and no patch/version field, so this is a descriptive season report, not a draft theory.

## What the season says

- **93 heroes appear in the pick/ban pool; 91 were actually picked.** 1,740 picks and 1,738 bans were recorded. The ban set is more concentrated than the pick set.
- **Freya (129 bans, 98.3% contest), Hirara (80 bans, 94.3%), Atlas (120 bans, 93.7%) and Paquito (58 bans, 83.3%)** are the four must-answer names. Freya and Atlas are primarily ban-pressure; Hirara and Paquito are pick-or-ban.
- **Paquito is the volume trap.** 87 picks at 44.8% is the highest pick count in the league, but the team split is extreme: TLID 14 picks at 71.4%, AE 9 at 100%, RRQ 17 at 23.5%, ONIC 7 at 14.3%, GEEK 7 at 14.3%. The hero is not uniformly strong; the team and matchup decide.
- **Selena is the second volume trap.** 46 picks at 41.3%, with BTR 13 at 30.8% and NAVI 4 at 100%. Volume without a team-specific plan is not priority.
- **Obsidia is the quiet overperformer.** 43 picks at 62.8%, only 28 bans, and a 40.8% contest rate. The hero is available and wins more than the headline picks.
- **Belerick is the volume stabilizer.** 68 picks at exactly 50%, but the team split runs from TLID 77.8% and NAVI 70% to DEWA 36.4%, GEEK 40% and RRQ 25%. It is a structure check, not a solo carry.
- **Uranus has the widest team-context swing of any high-volume hero:** BTR 8 picks at 87.5%, NAVI 6 at 83.3%, AE 6 at 83.3%, against GEEK 6 at 0%, EVOS 6 at 16.7%, ONIC 5 at 20% and RRQ 7 at 28.6%.
- **Marcel is the best low-volume return:** 29 picks at 65.5% with 84 bans (64.9% contest), and NAVI/BTR combine for 14 of the 29 picks at 14–0.

## Priority table (top 20 by contest rate)

| Hero | Picks | Win rate | Bans | Contest rate | Read |
|---|---:|---:|---:|---:|---|
| Freya | 42 | 52.4% | 129 | 98.3% | Permaban pressure; the pick is ordinary, the ban is not |
| Hirara | 84 | 53.6% | 80 | 94.3% | Pick-or-ban jungle flex |
| Atlas | 43 | 55.8% | 120 | 93.7% | Roam ban priority; NAVI 5–1 with it |
| Paquito | 87 | 44.8% | 58 | 83.3% | System pick; elite teams win, others lose |
| Marcel | 29 | 65.5% | 84 | 64.9% | High-return ban target; NAVI/BTR perfect |
| Uranus | 49 | 46.9% | 53 | 58.6% | Team-context hero with a huge split |
| Nolan | 54 | 59.3% | 45 | 56.9% | Best high-volume jungle return |
| Selena | 46 | 41.3% | 48 | 54.0% | Volume trap outside NAVI |
| Zhuxin | 47 | 51.1% | 43 | 51.7% | TLID 87.5%, GEEK 28.6% |
| Belerick | 68 | 50.0% | 20 | 50.6% | Structure check; team split decides |
| Melissa | 34 | 52.9% | 53 | 50.0% | Gold-lane priority with a wide team split |
| Barats | 39 | 46.2% | 43 | 47.1% | TLID/AE win, RRQ/BTR lose |
| Rafaela | 37 | 54.1% | 44 | 46.6% | RRQ volume (11) at 45.5% |
| Eudora | 49 | 55.1% | 30 | 45.4% | AE 7–1; ONIC 7–3 |
| Aulus | 51 | 56.9% | 19 | 40.2% | DEWA volume (11) at 45.5%; BTR/NAVI 80% |
| Claude | 60 | 51.7% | 10 | 40.2% | Highest-pick gold lane; rarely banned |
| Obsidia | 43 | 62.8% | 28 | 40.8% | Available and efficient |
| Minotaur | 43 | 41.9% | 28 | 40.8% | Volume without return |
| Carmilla | 39 | 56.4% | 64 | 59.2% | Support ban priority |
| Valentina | 42 | 35.7% | 24 | 37.9% | Worst high-volume return |

## Team-context warnings

- A hero's season win rate mixes strong and weak teams. The Paquito, Selena, Uranus and Belerick splits show the effect clearly. Never convert a season rate into a matchup rule without the team split.
- Bans are not picks. Freya's 129 bans do not mean Freya is a high-value pick at 52.4%; they mean teams prefer to remove her.
- The database does not record pick order, so "first pick" and "counter pick" claims are unsupported. The transcript occasionally names draft order, but only for specific games.

## How to use this

1. For opponent prep, start with the ban-pressure list (Freya, Atlas, Hirara, Paquito, Marcel) and then the opponent's personal volume picks, not the league average.
2. For your own draft, prefer heroes with a team-specific winning record over league-average volume.
3. Check `analysis/strategy/draft.md` for the coaching version, and the individual hero pages for transcript evidence and per-team splits.

## Limits

- Descriptive only; no causal identification.
- No patch/version partition, so cross-month comparisons are not patch comparisons.
- Small per-team samples; a 7–0 split is not a rule.
- Hero pages now exist for all 94 pool heroes (including Lilia, transcript-only); this report remains the cross-hero view.
