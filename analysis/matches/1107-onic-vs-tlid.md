# ONIC 0–2 TLID — series 1107 (pilot)

**Scope:** one series, game 1 early map pressure/objective context and result. Source: `src-s18-w09d03`, W9D3, verified YouTube video `hY0Upem95uo`. Broadcast timestamps are derived from the one-to-one caption alignment.

**Result:** schedule row 1107 — ONIC 0–2 TLID. Game 1: TLID won in **14:47**, 14–3 kills, 49,124 vs 39,093 gold (+10,031), 32,659 vs 1,902 tower damage. Game 2: TLID won in **12:25**, 11–7 kills, 45,031 vs 6,534 tower damage. Source: `OBS-1107-G1-DB` (`Q-MATCH-RESULT`, `Q-MATCH-DETAIL`, `Q-GAMES`, `Q-TEAM-GAMES`, `Q-GAME-PICKS`).

> **Database orientation note:** the repaired `matches` table stores TLID/ONIC 2-0 with `matches.winner = 'team_a'` (TLID). The schedule row is ONIC/TLID, 0-2, with `schedule_all.winner = 'team_b'` (also TLID). Both tables agree on the named winner; side tokens differ because team order differs. See `OBS-LINEAGE-WINNER`.

<!-- db-evidence:start -->
## Game-level database context

Database snapshot `mpl-s18-db-20c5ea2c51f3` · SHA-256 `20c5ea2c51f30d1a24cd2ce6927f0d182b47f951ebd8209f1aaef429941cf2ef`. Queries: `Q-MATCH-RESULT`, `Q-GAMES`, `Q-TEAM-GAMES`, `Q-MATCH-PLAYER-LINES`, `Q-GAME-PICKS`, `Q-GAME-BANS` (see `analysis/evidence/query-catalog.json`). These are source-reported scoreboard values, not official tournament tables.

**Series MVP (Liquipedia):** Lyoni.

### Game 1 — TLID win · 14:47 · Healing Turtle

Sides: TLID blue / ONIC red · [VOD](https://www.youtube.com/watch?v=paUEKUP6Fo8)

| Team | K | D | A | Gold | Hero damage | Tower damage |
|---|---:|---:|---:|---:|---:|---:|
| TLID | 14 | 3 | 39 | 49,124 | 143,224 | 32,659 |
| ONIC | 3 | 14 | 10 | 39,093 | 167,218 | 1,902 |

| Team | Player | Lane | Hero | K/D/A | KDA | Gold | Hero damage | Tower damage |
|---|---|---|---|---:|---:|---:|---:|---:|
| TLID | Aran | EXP | Atlas | 0/1/9 | 9.0 | 7,244 | 14,987 | 1,955 |
| TLID | Keven | GOLD | Cici | 4/0/8 | 12.0 | 11,263 | 32,104 | 15,465 |
| TLID | Kevinn | JUNGLE | Aulus | 4/1/5 | 9.0 | 12,352 | 38,334 | 8,122 |
| TLID | Drichel | MID | Zhuxin | 3/0/9 | 12.0 | 9,095 | 32,635 | 5,286 |
| TLID | Lyoni | ROAM | Gloo | 3/1/8 | 11.0 | 9,170 | 25,164 | 1,831 |
| ONIC | Lutpi | EXP | Terizla | 1/4/2 | 0.75 | 6,551 | 40,368 | 0 |
| ONIC | Kelra | GOLD | Paquito | 0/2/3 | 1.5 | 8,953 | 17,387 | 1,902 |
| ONIC | Kairi | JUNGLE | Nolan | 1/3/1 | 0.67 | 9,705 | 35,296 | 0 |
| ONIC | Killuaa | MID | Zetian | 1/3/1 | 0.67 | 6,740 | 44,230 | 0 |
| ONIC | Kiboy | ROAM | Marcel | 0/2/3 | 1.5 | 7,144 | 29,937 | 0 |

**Picks**

- TLID: Aran (EXP, Atlas), Kevinn (JUNGLE, Aulus), Drichel (MID, Zhuxin), Keven (GOLD, Cici), Lyoni (ROAM, Gloo)
- ONIC: Lutpi (EXP, Terizla), Kairi (JUNGLE, Nolan), Killuaa (MID, Zetian), Kelra (GOLD, Paquito), Kiboy (ROAM, Marcel)

**Bans:** A — Fanny, Esmeralda, Carmilla, Alice, Kimmy · B — Masha, Hirara, Freya, Obsidia, Barats

### Game 2 — TLID win · 12:25 · Healing Turtle

Sides: TLID blue / ONIC red · VOD not recorded

| Team | K | D | A | Gold | Hero damage | Tower damage |
|---|---:|---:|---:|---:|---:|---:|
| TLID | 11 | 7 | 29 | 41,381 | 195,995 | 45,031 |
| ONIC | 7 | 11 | 18 | 34,018 | 117,820 | 6,534 |

| Team | Player | Lane | Hero | K/D/A | KDA | Gold | Hero damage | Tower damage |
|---|---|---|---|---:|---:|---:|---:|---:|
| TLID | Aran | EXP | Freya | 1/1/3 | 4.0 | 8,111 | 35,568 | 8,968 |
| TLID | Keven | GOLD | Bruno | 2/0/5 | 7.0 | 9,433 | 43,575 | 25,903 |
| TLID | Kevinn | JUNGLE | Aulus | 6/3/4 | 3.33 | 9,218 | 40,821 | 5,321 |
| TLID | Drichel | MID | Zhuxin | 1/1/10 | 11.0 | 7,348 | 43,360 | 2,737 |
| TLID | Lyoni | ROAM | Marcel | 1/2/7 | 4.0 | 7,271 | 32,671 | 2,102 |
| ONIC | Lutpi | EXP | Cici | 0/1/5 | 5.0 | 5,681 | 32,812 | 1,202 |
| ONIC | Kelra | GOLD | Paquito | 1/1/2 | 3.0 | 7,751 | 20,954 | 1,332 |
| ONIC | Kairi | JUNGLE | Hirara | 3/2/2 | 2.5 | 8,328 | 22,502 | 0 |
| ONIC | Killuaa | MID | Kimmy | 3/2/4 | 3.5 | 6,548 | 28,523 | 2,000 |
| ONIC | Kiboy | ROAM | Carmilla | 0/5/5 | 1.0 | 5,710 | 13,029 | 2,000 |

**Picks**

- TLID: Aran (EXP, Freya), Kevinn (JUNGLE, Aulus), Drichel (MID, Zhuxin), Keven (GOLD, Bruno), Lyoni (ROAM, Marcel)
- ONIC: Lutpi (EXP, Cici), Kairi (JUNGLE, Hirara), Killuaa (MID, Kimmy), Kelra (GOLD, Paquito), Kiboy (ROAM, Carmilla)

**Bans:** A — Fanny, Esmeralda, Nolan, Cecilion, Alice · B — Masha, Atlas, Valentina, Selena, Eudora

Draft labels A/B are source draft order; picks are lane-order, not pick order.

**Transcript coverage:** `src-s18-w09d03` (complete); 24 accepted observations are carried in this report. Caster statements are commentary or observation, not database facts.

**Database limits:** no per-game objective counts, gold/damage timelines, vision, communications, or intent.
<!-- db-evidence:end -->

## Timeline and evidence

| Broadcast | Evidence | What is directly supported |
|---|---|---|
| 06:53:48–06:54:10 | `OBS-1107-ROTATION`, `seg-src-s18-w09d03-L009584-L009589` | The caster highlights early rotations toward Aran to limit ONIC’s map control, naming Drichel among TLID’s counterplay pieces. |
| 07:06:00–07:06:10 | `OBS-1107-TURTLE`, `seg-src-s18-w09d03-L009941-L009946` | The caster links TLID’s Rapid Boots rotations to contesting the healing Turtle and shutting down ONIC’s snowball. |
| 07:04:51 | `OBS-1107-VISUAL`, `VF-1107-early` | Visible: game clock **5:08**, TLID **14.0K** vs ONIC **13.1K** gold, top-lane fight. |
| 07:05:10 | `OBS-1107-VISUAL`, `VF-1107-item` | Visible: game clock **5:27**, TLID **15.3K** vs ONIC **13.6K**, “FIRST ITEM PRIORITY DRICHEL” overlay. |
| 07:12:41 | `OBS-1107-VISUAL`, `VF-1107-mid` | Visible: game clock **12:58**, TLID **40.8K** (DeepSeek re-read; historical `OBS-1107-VISUAL` recorded 40.6K) vs ONIC **34.7K**, “SEASON 18 40 LORD KILL KEVIN” milestone overlay. The milestone is **not** evidence of a current Lord. |
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

## Validated transcript observations (batch 3, 2026-11-13)

These 10 observations passed schema, quote, line-range, cue-range and duplicate checks and were spot-checked by the main agent. The other 14 staged observations remain `needs_review`. Caster statements are commentary, not proof of an in-game event.

### TOBS-1107-G1-01 — 06:53:45
[seg-src-s18-w09d03-L009580-L009589](https://youtu.be/hY0Upem95uo?t=24825) · analysis · commentary · confidence medium

> Maksimalkan
> early rotasi ke arah Aran. Wah, kembali
> lagi ya poin pentingnya ada di Aran
> untuk batasi map control.
> Yap, memaksimalkan unico, Lione dan juga
> Drichel untuk meng-counter gameplay ONIC

**Supported reading:** Caster says TLID should maximize early rotations toward Aran to limit ONIC's map control, naming Unico, Lyoni and Drichel as counterplay pieces.
**Notes:** Caster commentary about planned early rotations; not verified in-game movement. Spot-checked by main agent on 2026-11-13.

### TOBS-1107-G1-02 — 07:01:14
[seg-src-s18-w09d03-L009800-L009809](https://youtu.be/hY0Upem95uo?t=25274) · gameplay · observation · confidence medium

> Iya. Tapi lihat tuh ada empat agility
> tadi.
> Pelari culture
> pelari loh semuanya buat tim liquid id

**Supported reading:** Caster observes TLID's lineup has four agility/Rapid Boots users, enabling fast rotations.
**Notes:** Counts agility users as commentary; not a verified item build. Spot-checked by main agent on 2026-11-13.

### TOBS-1107-G1-04 — 06:58:28
[seg-src-s18-w09d03-L009720-L009729](https://youtu.be/hY0Upem95uo?t=25108) · draft · commentary · confidence medium

> Geser. Pakito di exp dan dia pakai badan
> satu.
> Eh sor pakai e
> boleh boleh. Aku lebih sepakat kayak
> gitu sih karena mereka ngandelin
> frontline di Marcel doang

**Supported reading:** Casters discuss moving Pakito to exp lane and relying on Marcel as sole frontline, agreeing it is heavy for TLID.
**Notes:** Draft/lane assignment commentary; not confirmed deployment. Spot-checked by main agent on 2026-11-13.

### TOBS-1107-G1-05 — 07:06:00
[seg-src-s18-w09d03-L009940-L009949](https://youtu.be/hY0Upem95uo?t=25560) · gameplay · commentary · confidence high

> Iya ya, rotasi cepat ya, empat agility
> Rapid Boots.
> Iya. Ngincer healing turtle menangin
> dulu earlynya menangin healing
> turtle-nya. Jadi power snowball dari
> nolanya bisa dikatakan mati.

**Supported reading:** Caster links TLID's fast Rapid Boots rotations to contesting the healing Turtle early and shutting down ONIC's snowball.
**Notes:** Turtle is a game objective; 'snowball dead' is caster evaluation. Spot-checked by main agent on 2026-11-13.

### TOBS-1107-G1-06 — 07:07:23
[seg-src-s18-w09d03-L009980-L009989](https://youtu.be/hY0Upem95uo?t=25643) · gameplay · commentary · confidence medium

> Leoni hampir saja tertake down. Coba
> dizoning sama Del. Jadi dengan tiga
> pemain mereka bisa menutup berapa pemain
> tuh? Lima di atas itu rugi rotasi.

**Supported reading:** Caster says TLID's three-player zone can lock down ONIC's five in the top area, wasting ONIC's rotation.
**Notes:** Positioning commentary; not a verified teamfight result. Spot-checked by main agent on 2026-11-13.

### TOBS-1107-G1-07 — 07:08:13
[seg-src-s18-w09d03-L010000-L010009](https://youtu.be/hY0Upem95uo?t=25693) · gameplay · observation · confidence medium

> wah dan bahkan di menit ke-el satu buah
> pasif base turet tengah sudah berhasil
> ditrigger melalui turtle yang ketiga,
> Om.

**Supported reading:** Caster reports that by about minute eleven the mid base turret passive was triggered via the third Turtle.
**Notes:** Minute and turret trigger are caster commentary; database has no per-game objective counts. Spot-checked by main agent on 2026-11-13.

### TOBS-1107-G1-12 — 07:14:05
[seg-src-s18-w09d03-L010180-L010189](https://youtu.be/hY0Upem95uo?t=26045) · gameplay · observation · confidence medium

> sebagai padat one by one situation Kevin
> dan juga K juga pun gagal untuk
> mendapatkan poin atas sosok dari Kevin
> karena terlalu tebal 3 versus 5

**Supported reading:** Caster describes a 3v5 situation where ONIC fails to secure a kill on Kevin because he is too tanky.
**Notes:** Teamfight description from commentary; not verified kill counts. Spot-checked by main agent on 2026-11-13.

### TOBS-1107-G1-14 — 07:14:29
[seg-src-s18-w09d03-L010190-L010199](https://youtu.be/hY0Upem95uo?t=26069) · post_match · commentary · confidence medium

> di game yang pertama. Sebuah dominasi
> yang begitu mengerikan tim Liquid ID.
> Mereka menendang dengan cukup
> mengerikan.

**Supported reading:** Caster calls game one total domination by TLID.
**Notes:** Evaluative; supported in aggregate by DB result but not proof of cause. Spot-checked by main agent on 2026-11-13.

### TOBS-1107-G1-22 — 07:16:39
[seg-src-s18-w09d03-L010240-L010249](https://youtu.be/hY0Upem95uo?t=26199) · post_match · statistic · confidence high

> 14 menit bos
> 14 menit

**Supported reading:** Database records game 1 duration 887 seconds (14:47) and TLID win; caster's '14 minutes' aligns.
**Database provenance:** Q-GAMES (snapshot mpl-s18-db-20c5ea2c51f3).
**Notes:** DB-backed duration; caster's rounded minute is commentary. Spot-checked by main agent on 2026-11-13.

### TOBS-1107-G1-24 — 07:14:55
[seg-src-s18-w09d03-L010200-L010209](https://youtu.be/hY0Upem95uo?t=26095) · post_match · statistic · confidence high

> semuanya. Ternyata Tim Liquid mereka
> sangat memegang jalannya permainan dari
> awal tadi.

**Supported reading:** Database records game 1 team stats: TLID 14 kills/3 deaths, 49124 gold, 32659 tower damage vs ONIC 3 kills/14 deaths, 39093 gold, 1902 tower damage.
**Database provenance:** Q-TEAM-GAMES (snapshot mpl-s18-db-20c5ea2c51f3).
**Notes:** DB-backed game 1 aggregates; commentary about control is separate. Spot-checked by main agent on 2026-11-13.

## Additional accepted observations (review pass, 2026-11-13)

<!-- review-pass-start -->
These 13 observations were accepted in the Beam Max review pass. Caster statements remain commentary, not proof of an in-game event.

### TOBS-1107-G1-03 — 07:03:11
[seg-src-s18-w09d03-L009860-L009869](https://youtu.be/hY0Upem95uo?t=25391) · draft · commentary · confidence medium

> juga. Gold-nya masih tarik-tarikan masih
> cukup seimbang. Tidak ada yang terlalu
> dominan. Tapi tetap aja yang jadi cukup
> berbahaya adalah kalau farmingnya
> dibiarkan terus-menerus nih.

**Supported reading:** Caster says early gold is still balanced with no dominant side, but unchecked farming would become dangerous.
**Notes:** Gold balance claim is caster observation, not database-backed. Beam Max triage 2026-11-13: accept — Quote supports balanced gold and farming danger.

### TOBS-1107-G1-08 — 07:09:54
[seg-src-s18-w09d03-L010050-L010059](https://youtu.be/hY0Upem95uo?t=25794) · gameplay · observation · confidence medium

> Oke, lordnya marching tanpa adanya Holy
> Defense
> tanpa ada Hense jadi gak bisa ditahan
> pakai Golden Hour.

**Supported reading:** Caster notes the Lord is marching without Holy Defense, so Golden Hour cannot hold it.
**Notes:** Lord state described by caster; not database-backed. Beam Max triage 2026-11-13: accept — Quote supports Lord marching without Holy Defense.

### TOBS-1107-G1-09 — 07:19:06
[seg-src-s18-w09d03-L010330-L010339](https://youtu.be/hY0Upem95uo?t=26346) · gameplay · commentary · confidence medium

> healing turtle yang sangat-sangat
> maksimal ya. Mentok maksimal mentok deh
> buat Liquid. Perfect semua.
> Tiga stacknya juga dipecahin [musik]
> terus ya kan.

**Supported reading:** Caster says TLID maximized healing Turtle usage to the limit, calling it perfect.
**Notes:** Evaluative caster commentary. Beam Max triage 2026-11-13: accept — Quote supports TLID maximizing healing Turtle.

### TOBS-1107-G1-10 — 07:04:59
[seg-src-s18-w09d03-L009910-L009919](https://youtu.be/hY0Upem95uo?t=25499) · gameplay · observation · confidence medium

> outer middle turetnya dihancurkan.
> Sementara pertukaran yang coba dilakukan
> sama Kelra masih belum berhasila. Wah,
> udah
> malah atasnya juga bolong nih.

**Supported reading:** Caster reports the outer middle turret is destroyed while Kelra's attempted trade fails and top lane is also open.
**Notes:** Tower destruction claim from commentary; database records aggregate tower damage. Beam Max triage 2026-11-13: accept — Quote supports outer middle turret destroyed and Kelra trade fail.

### TOBS-1107-G1-11 — 07:10:13
[seg-src-s18-w09d03-L010060-L010069](https://youtu.be/hY0Upem95uo?t=25813) · gameplay · observation · confidence medium

> Defense. Mau enggak mau Hly Defense
> karena juga sekarang sudah menit ke-10
> tapi yang paling mahal di antara semua
> adalah mid-nya base turetnya bolong
> bolong

**Supported reading:** Caster says by minute ten the most costly damage is the mid base turret being opened.
**Notes:** Minute and turret state are caster commentary. Beam Max triage 2026-11-13: accept — Quote supports minute-ten mid base turret damage.

### TOBS-1107-G1-13 — 07:16:11
[seg-src-s18-w09d03-L010230-L010239](https://youtu.be/hY0Upem95uo?t=26171) · gameplay · commentary · confidence medium

> iya jadi menurutku kayak tim Liquid
> sangat-sangat terstruktur ya dari segi
> emblem yang mereka bawakan build-nya
> juga mau gimana dan kayak plan yang
> sudah mereka siapkan ini tereksekusi

**Supported reading:** Caster evaluates TLID as highly structured, with emblem, build and prepared plan well executed.
**Notes:** Evaluative commentary, not a measured fact. Beam Max triage 2026-11-13: accept — Quote supports TLID structured emblem/build/plan.

### TOBS-1107-G1-16 — 06:55:03
[seg-src-s18-w09d03-L009620-L009629](https://youtu.be/hY0Upem95uo?t=24903) · draft · commentary · confidence medium

> itu bisa selamat atau lebih susah
> ditangkap sama hero-hero kayak ber kayak
> Atlas dibanding Pakito ataupun Aulus.

**Supported reading:** Caster compares catchability, saying Lunox is harder to catch by heroes like Atlas than Pakito or Aulus.
**Notes:** Draft matchup commentary; 'Nolan' in prior lines refers to Lunox. Beam Max triage 2026-11-13: accept — Quote supports Lunox catchability comparison.

### TOBS-1107-G1-17 — 06:55:40
[seg-src-s18-w09d03-L009630-L009639](https://youtu.be/hY0Upem95uo?t=24940) · draft · commentary · confidence medium

> win rate yang cukup tinggi ya 67% dari
> 27 kali pick
> dan rata-rata memang Marcel ini kayaknya

**Supported reading:** Caster cites Marcel's 67% win rate over 27 picks as a high win rate.
**Notes:** Statistic is caster-reported, not database-backed; marked commentary. Beam Max triage 2026-11-13: accept — Quote supports Marcel 67% over 27 picks as caster stat.

### TOBS-1107-G1-18 — 06:59:05
[seg-src-s18-w09d03-L009740-L009749](https://youtu.be/hY0Upem95uo?t=25145) · draft · commentary · confidence medium

> Uh nih hardpck ya sebenarnya ya.
> Ini fify-F enggak sih Om? kayak mereka
> punya power sendiri-sendiri.
> Iya. Tapi kalau kita bicara soal Onik,
> kalau sampai terhenti di early-nya nih

**Supported reading:** Casters evaluate the draft as hardpick with each side having its own power, and warn ONIC could struggle if stopped early.
**Notes:** Draft evaluation commentary. Beam Max triage 2026-11-13: accept — Quote supports hardpick evaluation and ONIC early risk.

### TOBS-1107-G1-19 — 07:03:53
[seg-src-s18-w09d03-L009880-L009889](https://youtu.be/hY0Upem95uo?t=25433) · gameplay · observation · confidence medium

> adalah di mana kalau misalnya Kyoynya
> Golden Hour for defensive dan Kevin
> hampir saja terkick down
> berani sekali dia tetap bertahan

**Supported reading:** Caster says Kyoy used Golden Hour defensively while Kevin nearly got kicked down but stayed brave.
**Notes:** Teamfight detail from commentary; names resolved by context. Beam Max triage 2026-11-13: accept — Quote supports Kyoy Golden Hour and Kevin bravery.

### TOBS-1107-G1-20 — 07:04:34
[seg-src-s18-w09d03-L009900-L009909](https://youtu.be/hY0Upem95uo?t=25474) · gameplay · observation · confidence medium

> fight kembali. Kakas membuat lupi gak
> ada jalan untuk pulang tapi damagen-nya
> terlalu sakit ters Kevin dan akhirnya
> Rel yang menyelamatkan Kevin.

**Supported reading:** Caster reports a re-engaged fight where Lutfi has no way home, Kevin's damage is too high, and Lyoni saves Kevin.
**Notes:** Names resolved by context; fight outcome is caster narration. Beam Max triage 2026-11-13: accept — Quote supports re-engaged fight and Lyoni saving Kevin.

### TOBS-1107-G1-21 — 07:10:58
[seg-src-s18-w09d03-L010080-L010089](https://youtu.be/hY0Upem95uo?t=25858) · draft · commentary · confidence medium

> Sempat harusnya
> sempat harusnya ya. Oke. Tapi ini cukup
> dalam tadi masuknya dari tim Liquid ID
> cuman mereka strong banget untuk
> bertahan di dalam satu buah B turet.

**Supported reading:** Caster says ONIC almost had a chance, but TLID's deep entry was strong enough to hold in one base turret.
**Notes:** Evaluative commentary. Beam Max triage 2026-11-13: accept — Quote supports TLID holding in base turret.

### TOBS-1107-G1-23 — 07:16:30
[seg-src-s18-w09d03-L010240-L010249](https://youtu.be/hY0Upem95uo?t=26190) · unknown · statistic · confidence high

> mereka berani lepas ke arah Nolan
> berarti tandanya mereka udah tahu oh
> early-nya kita cekek beneran dicekek
> enggak ada nafas sama sekali

**Supported reading:** Database records series 1107 result ONIC 0-2 TLID (schedule row id-w9-7).
**Database provenance:** Q-MATCH-RESULT (snapshot mpl-s18-db-20c5ea2c51f3).
**Notes:** DB-backed series result; caster's 'no breath' is commentary. Beam Max triage 2026-11-13: accept — Statistic matches database schedule row.

<!-- review-pass-end -->
## Ambiguity resolutions (2026-11-13)

<!-- ambiguity-resolution-start -->
These records were resolved by checking the canonical player/hero lists.

### TOBS-1107-G1-15 — 06:53:01
[seg-src-s18-w09d03-L009560-L009569](https://youtu.be/hY0Upem95uo?t=24781) · draft · commentary · confidence medium

> Hm. XP ya tetap menjadi prioritas juga
> apalagi kebetulan ya lawannya Lutfi
> bukan lawan yang mudah. Aran.

**Supported reading:** Caster says XP remains a priority, especially since the opponent Lutfi is not an easy opponent, naming Aran.
**Notes:** Name resolution uncertain; 'Aran' may be player or hero. Beam Max triage 2026-11-13: needs_human — Aran identity ambiguous (player vs hero) from quote. List-resolution 2026-11-13: Aran resolved as TLID EXP player in player_season_stats; no hero named Aran exists.

<!-- ambiguity-resolution-end -->
## References

- `seg-src-s18-w09d03-L009584-L009589` — https://youtu.be/hY0Upem95uo?t=24828 (06:53:48)
- `seg-src-s18-w09d03-L009941-L009946` — https://youtu.be/hY0Upem95uo?t=25560 (07:06:00)
- `seg-src-s18-w09d03-L011191-L011193` — https://youtu.be/hY0Upem95uo?t=28002 (07:46:42)
- Frames: `VF-1107-early` (07:04:51.481), `VF-1107-item` (07:05:10.920), `VF-1107-mid` (07:12:41.281); local ignored cache plus sidecars
- `OBS-1107-SOURCE-MAP`, `OBS-1107-ROTATION`, `OBS-1107-TURTLE`, `OBS-1107-G1-DB`, `OBS-1107-VISUAL`, `OBS-1107-COUNTER`
- `Q-MATCH-RESULT`, `Q-MATCH-DETAIL`, `Q-GAMES`, `Q-TEAM-GAMES`, `Q-GAME-PICKS`, `Q-TLID-TOWER-GAMES`
- Database snapshot `mpl-s18-db-20c5ea2c51f3`

## Limits

- One game, one broadcast, selected frames; no full clip, communications, vision or intent.
- Broadcast timestamps are derived from auto-caption cue alignment, not native transcript timestamps.
- The database has no per-game objective counts; “Turtle” and “Lord” in the transcript are commentary.
- "40 LORD KILL" is a season milestone overlay, not a current-objective indicator.
- DeepSeek pass 1 re-read the visual frames: TLID gold at 12:58 is **40.8K**, not the historical 40.6K.
- Tower damage is a derived team aggregate and an outcome, not a causal measure.
