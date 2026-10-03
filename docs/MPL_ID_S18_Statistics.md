# MPL Indonesia Season 18 — Statistics
Sources:
- https://liquipedia.net/mobilelegends/MPL/Indonesia/Season_18/Statistics (wrapper: Overall + tabs Hero/Game, sections Hero Stats, DurationStats, Country Representation, Player Appearances)
- https://liquipedia.net/mobilelegends/MPL/Indonesia/Season_18/Statistics/Regular_Season (HeroStats tournament=MPL/Indonesia/Season_18/Regular Season, DurationStats limit=12)
- https://liquipedia.net/mobilelegends/MPL/Indonesia/Season_18/Statistics/Playoffs (exists, TBD – no games at fetch)
Method: `api.php?action=parse&prop=text` – Regular_Season stats HTML 1,088,734 chars, 88 hero rows + 2 duration tables. Overall page HeroStats queries Regular + Playoffs.

## Hero Statistics – Regular Season (121 games at fetch: 51 series × ~2.37 games; %T = pick/ban rate out of 121 games)
Hero table columns: ∑ picks, W, L, WR, %T | Blue ∑/W/L/WR | Red ∑/W/L/WR | Bans ∑, %T | P+B ∑, %T + Details popup (Played By Teams, Played With, Played Against).

Most Picked (Top 10):
1. Hirara – 75P (40W-35L, 53.33%, 61.98%) – Blue 44 (26-18, 59.09%), Red 31 (14-17, 45.16%) – Bans 40 (33.06%), P+B 115 (95.04%)
2. Belerick – 64P (31-33, 48.44%, 52.89%) – Bans 19, P+B 83 (68.60%)
3. Paquito – 63P (31-32, 49.21%, 52.07%) – Bans 52 (42.98%), P+B 115 (95.04%)
4. Claude – 52P (27-25, 51.92%, 42.98%) – Bans 10, P+B 62
5. Uranus – 45P (22-23, 48.89%, 37.19%) – Bans 43, P+B 88
6. Eudora – 43P (26-17, 60.47%) – Bans 20, P+B 63
7. Selena – 41P (17-24, 41.46%) – Bans 41, P+B 82
8. Barats – 36P (16-20, 44.44%) – Bans 38, P+B 74
9. Minotaur – 35P (17-18, 48.57%) – Bans 20, P+B 55
10. Melissa – 34P (18-16, 52.94%) – Bans 53, P+B 87

Next 20 (rank 11-30):
11. Rafaela 32P 19-13 59.38%, B36 P+B68
12. Obsidia 29P 18-11 62.07%, B13 P+B42
13. Moskov 29P 16-13 55.17%, B13 P+B42
14. Carmilla 28P 18-10 64.29%, B24 P+B52
15. Brody 28P 8-20 28.57%, B12 P+B40
16. Gloo 27P 16-11 59.26%, B29 P+B56
17. Nolan 26P 15-11 57.69%, B24 P+B50
18. Miya 25P 16-9 64.00%, B15 P+B40
19. Atlas 25P 14-11 56.00%, B88 (72.73%) P+B113 (93.39%)
20. Valentina 24P 10-14 41.67%, B13 P+B37
21. Lylia 23P 10-13 43.48%, B21 P+B44
22. Esmeralda 20P 10-10 50.00%, B26 P+B46
23. Zhuxin 20P 10-10 50.00%, B22 P+B42
24. Novaria 19P 10-9 52.63%, B38 P+B57
25. Harley 18P 6-12 33.33%, B12 P+B30
26. Mathilda 17P 10-7 58.82%, B44 P+B61
27. Gatotkaca 17P 8-9 47.06%, B6 P+B23
28. Alice 16P 8-8 50.00%, B9 P+B25
29. Fanny 15P 8-7 53.33%, B70 (57.85%) P+B85 (70.25%)
30. Marcel 14P 7-7 50.00%, B73 (60.33%) P+B87 (71.90%)

Most Banned (Top 15):
1. Freya – 107B + 13P (5W 38.46%) P+B120 (99.17% – near-perma-ban)
2. Atlas – 88B + 25P P+B113
3. Marcel – 73B + 14P P+B87
4. Fanny – 70B + 15P P+B85
5. Melissa – 53B + 34P P+B87
6. Paquito – 52B + 63P P+B115
7. Mathilda – 44B + 17P P+B61
8. Uranus – 43B + 45P P+B88
9. Selena – 41B + 41P P+B82
10. Hirara – 40B + 75P P+B115
11. Barats – 38B + 36P P+B74
12. Novaria – 38B + 19P P+B57
13. Rafaela – 36B + 32P P+B68
14. Gloo – 29B + 27P P+B56
15. Esmeralda – 26B + 20P P+B46

Highest P+B presence: Freya 120, Paquito/Hirara 115, Atlas 113, Uranus 88, Marcel/Melissa 87, Fanny 85, Belerick 83, Selena 82, etc.
Total heroes tracked: 88 (includes low/0-pick heroes – full list in HTML; e.g. Aulus/Cecilion high WR small sample per mirrors, Masha disabled Week 6).

Details popup example – Hirara:
- Played By: NAVI 12 (8-4 66.67%), AE 10 (8-2 80%), RRQ 10 (3-7 30%), TLID 9 (8-1 88.89%), BTR 8 (4-4 50%) …
- Played With: Belerick 27 (16-11), Claude 21 (11-10), Selena 16, Uranus 15, Moskov 14 (10-4 71.43%)
- Played Against: Paquito 35, Melissa 19, Eudora 19, Belerick 17, Uranus 17
(Same popups exist for every hero – query Game_history via Special:RunQuery links in Picks/Bans columns.)

Side split note: Hirara strong Blue (59.09%) vs Red (45.16%); Belerick Blue 62.50% (15-9) vs Red 40.00% (16-24); Paquito Blue 60.00% vs Red 42.11% – Blue-side edge for top meta picks.

## Game Statistics – Regular Season (DurationStats limit=12)
Shortest Games (12):
- 10:03 – 2026-09-19 Week 6 G2 – TLID beat BTR
- 10:12 – 2026-10-02 Week 7 G1 – TLID beat DEWA (DEWA-TLID series, DEWA won 2-1)
- 10:32 – 2026-08-29 Week 3 G2 – RRQ beat BTR (BTR won series 2-1)
- 10:38 – 2026-08-28 Week 3 G2 – DEWA beat GEEK
- 10:40 – 2026-08-23 Week 2 G1 – AE beat DEWA
- 10:45 – 2026-08-15 Week 1 G2 – TLID beat GEEK
- 10:50 – 2026-08-15 Week 1 G1 – GEEK beat TLID
- 10:53 – 2026-08-29 Week 3 G1 – BTR beat RRQ
- 10:55 – 2026-09-06 Week 4 G2 – AE beat BTR
- 10:56 – 2026-08-15 Week 1 G1 – NAVI beat EVOS
- 11:03 – 2026-08-16 Week 1 G3 – BTR beat GEEK
- 11:03 – 2026-09-18 Week 6 G1 – GEEK beat ONIC

Longest Games (12):
- 31:05 – 2026-09-05 Week 4 G2 – EVOS beat BTR (longest of season)
- 30:00 – 2026-08-22 Week 2 G2 – ONIC beat RRQ
- 27:33 – 2026-08-30 Week 3 G2 – RRQ beat GEEK
- 27:06 – 2026-09-13 Week 5 G2 – AE beat ONIC
- 26:35 – 2026-08-29 Week 3 G1 – AE beat EVOS
- 25:32 – 2026-08-21 Week 2 G1 – NAVI beat TLID
- 24:54 – 2026-09-19 Week 6 G2 – NAVI beat GEEK
- 24:50 – 2026-09-06 Week 4 G1 – ONIC beat EVOS
- 24:40 – 2026-08-14 Week 1 G2 – EVOS beat RRQ
- 24:12 – 2026-08-30 Week 3 G1 – NAVI beat ONIC
- 24:11 – 2026-09-05 Week 4 G2 – AE beat GEEK
- 23:30 – 2026-08-21 Week 2 G2 – BTR beat DEWA

## Other Statistics Sections (from wrapper page)
- Country Representation (`{{Country representation|staff=true}}`): rendered in HTML – use Overall page HTML for per-country player/staff counts (ID/PH/etc.).
- Players Appearances / Team/Player tables: Liquipedia `{{Player tournament appearances}}` + official https://id-mpl.com/statistics supplements (mirrors previously scraped):
  - Team totals (K/D/A/Gold/Damage/Lord/Turtle/Tower): BTR 315/313/885, EVOS 247/259/621, RRQ 190/333/468, ONIC 270/276/729, AE 373/287/923, GEEK 278/373/726, DEWA 266/290/658, TLID 337/250/850, NAVI 298/194/794
  - Kill leaders: NNAEL 145, KEVIN 133, ARFY 122, YAZUKEE 114, KAIRI 97; Assist leaders: LYONI 242, HIJUMEE 233, FINN 231, ALEKK 230, SHOGUN 205
  - MVP pts (MLBBHub): KEVIN 119, Dingarai 81, NNAEL 59, KAIRI 54, Nino 53, MORENOO 51 …
- Playoffs Statistics page: exists but empty at fetch (no playoff games yet) – HeroStats tournament2 + DurationStats tournament2 will populate after Oct 18.
- Per-game drafts/VODs: in Regular Season Match blocks (Map template: vod, side, length, winner, bans/picks, comment map name) – 121 games with full drafts.
