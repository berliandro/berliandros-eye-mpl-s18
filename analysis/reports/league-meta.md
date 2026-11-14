# MPL S18 league meta — evidence brief

**Snapshot:** `mpl-s18-db-20c5ea2c51f3` (`20c5ea2c51f3…`). 72 series, 174 games, 9 teams, 66 players. Full tables: `analysis/reports/league-data.md`. Raw aggregates: `analysis/evidence/league-aggregates.json`.

## The season in one paragraph

TLID and NAVI tied at 12–4, but they got there differently: TLID won 26 games and finished series early (15:14 average, 9 sweeps, only one close game), while NAVI played 17:17 on average, went to five deciders and owned the best close-game record (4–3). AE (10–6) had the best sweep rate alongside TLID (9 sweeps). BTR (10–6) was the weakest 10-win team by game differential (+3). ONIC (7–9) had the league's most extreme side split (15–6 blue, 4–15 red). RRQ (4–12) reached nine deciders and lost most of them. DEWA and GEEK combined for 15 sweep losses.

## Tiers, by evidence

| Tier | Teams | Why |
|---|---|---|
| Contenders | TLID, NAVI, AE | 10+ series wins, positive game differential, multiple sweep wins. TLID is the finisher; NAVI is the close-game team; AE is the clean-sweep team. |
| Playoff fringe | BTR | 10–6 but +3 games, five 0–2 losses, 5–6 in blowouts. The record is better than the control. |
| Middle | EVOS, ONIC | Both 8–8 or 7–9 with extreme variance. EVOS is .500 in every split; ONIC's red side is the league's biggest anomaly. |
| Rebuild | DEWA, GEEK, RRQ | 4–5 series wins each, negative game differentials, 6–7 sweep losses. RRQ's nine deciders are the only argument that they are closer than the record. |

This is a descriptive tier list, not a power ranking. It uses series record, game differential, sweep count, close-game record and blowout record from the snapshot.

## What separates the top

- **Finishing.** TLID had 12 blowout wins and a 15:14 average; NAVI had 11 blowout wins but a 17:17 average and five deciders. TLID converts leads faster.
- **Close-game execution.** NAVI 4–3, AE 3–1, EVOS 3–3, BTR 2–3, ONIC 2–4, RRQ 2–1 (small samples). NAVI's record is the best among contenders.
- **Sweep avoidance.** DEWA (7 lost), GEEK (7) and RRQ (6) gave away 0–2 series. TLID lost two, NAVI three, AE three.
- **Draft efficiency.** Top teams get winning returns from high-volume picks; RRQ (Paquito 17 at 23.5%) and BTR (Selena 13 at 30.8%) do not.

## Side and map

- Blue won 101/174 games (58.0%). The league average is real but confounded: side interacts with draft order, opponent and map.
- Team splits are more actionable than the league average: ONIC 15–6 blue / 4–15 red, TLID 15–3 / 11–8, AE 14–5 / 9–8, RRQ 10–14 / 4–13, GEEK 6–9 / 7–17.
- Map samples are 12–38 games. Healing Turtle (72.7% blue, 22 games) and Expanding Rivers (70.6%, 17) look blue-friendly; Revealing Wisps (43.8%, 16) looks red-friendly. Do not treat any as proven; 21 games have no map mode.
- Average game is 16:28 (median 15:23). Golden Turret is the shortest map (14:37); Dangerous Grass the longest (17:39).

## Hero meta

- Ban pressure: Freya 129 bans (98.3% contest), Atlas 120, Hirara 80, Paquito 58, Marcel 84.
- Pick volume: Paquito 87 (44.8%), Hirara 84 (53.6%), Belerick 68 (50.0%), Claude 60 (51.7%), Nolan 54 (59.3%).
- Best high-volume returns: Nolan 59.3%, Obsidia 62.8%, Aulus 56.9%, Eudora 55.1%, Atlas 55.8%.
- Worst high-volume returns: Valentina 35.7%, Selena 41.3%, Paquito 44.8%, Barats 46.2%, Uranus 46.9%.
- The team split is the story for Paquito, Selena, Uranus and Belerick. Full report: `analysis/reports/hero-meta.md`.

## Player production

- KDA leaders (minimum 10 games): Zeonn 7.85, Jiizee 7.54 (both NAVI), Drichel 6.78, Keven 6.51 (both TLID), Morenooo 6.29 (BTR).
- Role baselines matter: MID average KDA 4.85, GOLD 4.52, JUNGLE 3.65, EXP 3.03, ROAM 2.77. Never compare across roles without the baseline.
- Gold lane converts to tower damage: average 12,379 per game, versus 3,627 for jungle, 1,768 for exp, 1,594 for mid and 593 for roam.

## Evidence limits

- No patch/version field, so calendar splits are not patch splits.
- No objective counts, gold timelines, vision, communications or intent. Objective analysis is transcript-attributed or blocked.
- 45 series have no transcript; their reports are database-only.
- 0 visual boundaries are verified. No claim in this report depends on a screenshot.
- Hero and player rates are descriptive; none of this identifies causality.

## What this means for the head coach

1. The gap between TLID/NAVI/AE and the field is conversion and sweep avoidance, not draft novelty.
2. The cheapest matchup edge in the league is forcing ONIC or RRQ to red and preparing for their red-side draft.
3. The biggest draft trap is Paquito volume outside TLID/AE; the biggest comfort trap is BTR's Selena.
4. RRQ's nine deciders are a closing problem, not an access problem. DEWA's 14 blowout losses are a collapse problem.
5. Any objective KPI needs a video-review dataset first; the database cannot support one.
