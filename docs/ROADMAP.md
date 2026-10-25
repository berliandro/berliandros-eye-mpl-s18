# Berliandro's Eye — Masterplan

> **Vision.** Be the deepest public source of MPL Indonesia knowledge: not just
> "who won", but *why* — draft patterns, player edges, team tendencies, and
> matchup weaknesses a head coach can act on. Reusable every season, not rebuilt
> each season.
>
> **Status of this document.** Living plan of record. Phases 0–3 are implemented
> (2026-10-22); Phase 4 is ongoing/future work. Effort estimates assume one
> focused maintainer.

---

## 1. Success criteria

The project is "complete" when all five are true:

| # | Criterion | Test |
|---|---|---|
| 1 | **Season-proof** | Onboarding Season 19 is config + data only; no application-code fork. |
| 2 | **Trustworthy** | Every displayed rate carries a sample size and a confidence band; nothing is fabricated. |
| 3 | **Coach-useful** | A coach can produce a series prep sheet for an opponent in under 10 minutes. |
| 4 | **Deeper than alternatives** | At least six analytics that Liquipedia / id-mpl / mlbbhub do not publish. |
| 5 | **Durable** | One command rebuilds any season from committed sources; CI proves it. |

---

## 2. Where the project stands

### 2.1 What exists today

A single-file, offline-first dark web app for **MPL ID Season 18**, built from
committed SQLite/CSV, with live refresh from the mlbbhub API.

```
mlbbhub API ──┐
              ├─► tools/build_s18_db.py ─► data/mpl_id_s18.db + data/csv/
Liquipedia ───┘                                   │
                                                  ▼
assets/manifest.json ────────────────► tools/gen_dark.py ─► mpl_id_s18_dark.html
data/season.json ────────────────────┘        ▲
                                              │
                    tools/templates/{doc.html, app.js, style.css}
```

**Verified current inventory** (from `data/mpl_id_s18.db`):

| Table | Rows | Notes |
|---|---:|---|
| `matches` | 72 | completed series |
| `games` | 174 | per-game result, duration, sides, VOD |
| `game_players` | 1,740 | 174 × 10; K/D/A, gold, GPM, damage, tanked, tower dmg, emblem, 6 items, 3 talents |
| `game_bans` | 1,738 | 10 ordered bans per game, except two 9-ban games (duplicate/blank source rows) listed in `quality.json` |
| `game_picks` | 1,740 | 5 picks per side with lane + lane source |
| `hero_stats` | 133 | pick / ban / win / WR |
| `player_season_stats` | 66 | season totals + primary lane |
| `team_games` | 348 | per-game team aggregates derived from the five player rows |
| `team_season_stats` | 9 | team season aggregates; wins/losses reconcile with standings 9/9 |
| `standings` | 9 | match points, game diff |
| `schedule_all` | 80 | 72 regular + 8 playoff |

Distinct: **61 players with completed game rows** (66 season-stat rows),
**93 heroes picked or banned**, **114 item identifiers**.
Built HTML ≈ **1.55 MB**, fully self-contained.

**Application surface:** Overview (player deep dive), Players, Matches (list/grid,
regular/playoffs, bracket preview), Stats (MVP race + hero dashboard), **Analytics**
(players, teams, draft) and **Prep** (opponent scouting report). Plus drill-down
dialogs for hero / item / emblem / talent / opponent / game (with map mode and VOD),
a Bradley-Terry playoff-chance simulator, a `Ctrl/⌘K` search palette, URL
permalinks for views/analytics/prep, offline cache, and live refresh.

**Engineering:** 18 verification suites (`tools/verify.py`), generated-output
parity gate, XSS sink tests, ETL staging + atomic publish, season-config
validation, ruff, GitHub Actions CI.

### 2.2 What is genuinely strong

- **Data is already relational and rich.** Per-player damage, gold, tanked and
  tower damage at game level is more than most public MPL dashboards expose.
- **Provenance discipline.** Staged ETL, parity gate, "never fabricate" rule for
  MANIAC/SAVAGE — unusual rigor for a fan project.
- **Season config already exists** (`data/season.json`) and is validated and
  embedded. The seed of reusability is there.
- **Single-file offline artifact** is a real distribution advantage.

### 2.3 Structural debt (resolved in Phases 0–1)

| Debt | Resolution |
|---|---|
| Season baked into filenames | `data/registry.json` + `--season` wrappers; S18 keeps `layout:"legacy"` without a physical move |
| Player aliases / lanes hardcoded in JS | `data/global/aliases.json`, embedded as `window.ALIASES` |
| Branding / cache key / single output path | season config and `--season` output; root artifact retained for link compatibility |
| No provenance record | `data/seasons/s18/meta.json` (schema, sources, row counts); a SQLite `meta` table remains optional |
| Hero metadata absent | `data/global/hero_classes.json` covers all 133 heroes (damage type derived and labelled) |
| Per-game lane `NULL` | 1,740/1,740 player rows carry `lane` + `lane_source=liq_slot` |
| Draft data under-used | 1,740 picks, 1,738 ordered bans, 153/174 map modes, 174/174 VOD links, team aggregates |

### 2.4 Data ceilings (verified, not assumed)

These are *source* limits. The roadmap must design around them, not pretend
they don't exist.

| Missing | Evidence | Consequence |
|---|---|---|
| Per-game Lord / Turtle / Tower **counts** | mlbbhub `/match` has no objective fields; `id-mpl.com/match-detail/<id>` exposes only KDA/damage/tower-damage/gold | No objective-control analytics per game. Team **season totals** do exist on `id-mpl.com/statistics`. |
| Gold / damage **timelines** | no per-minute endpoint anywhere public | No gold-diff-at-15, no comeback curves, no power-spike timing |
| Draft **pick order** | `/drafts` returns `bans_a` / `bans_b` arrays only; Liquipedia `t1h1..h5` is **lane order** (verified below), not pick order | No "first-pick win rate" by hero; ban order may still be recoverable |
| MANIAC / SAVAGE | no source | stays `–` |
| Damage type split (physical/magic/true) | not exposed | composition analysis uses hero roles as a proxy, labelled as such |
| Per-game lane from API | `lane: null` on every player row | **Recoverable** from Liquipedia — see 2.5 |

### 2.5 Verified unlock: per-game lane is recoverable

Liquipedia's `Map` template carries both teams' five heroes as
`t1h1…t1h5` / `t2h1…t2h5`, always in the order
**EXP → JUNGLE → MID → GOLD → ROAM**.

Validated against Season 18 data:

- **89.5%** agreement with each player's declared season lane (340/380 slots).
- **13 of 14** players occupy a ≥80% stable slot; modal slots map exactly to the
  lane order (e.g. Kelra 100% slot 4 = GOLD; Killuaa 96% slot 3 = MID).
- Residual mismatches look like **genuine flexes** (Kiboy 6 games at EXP, Ryzaa 2
  at ROAM), which is itself coach-relevant signal.

The same template also carries **map mode** (`Broken Walls`, `Flying Cloud`,
`Dangerous Grass`, `Expanding Rivers`), per-game **VOD**, duration, sides and
**full 5-man picks + 5 bans** — all currently unused.

**This single ingestion change unlocks lane matchups, role-normalised metrics,
map analytics, and full draft analysis.** It is the highest-leverage item in
the plan.

---

## 3. Product principles

1. **Never fabricate.** A missing number renders as `–`, with the reason on hover.
2. **Sample size is part of the number.** Every rate ships with `n`; rates below
   a threshold are visually de-emphasised, not hidden.
3. **Adjusted beats raw.** A tank's KDA is not compared to a marksman's. Role,
   opponent and hero context are normalised before ranking.
4. **Explain the metric.** Every derived stat has a one-line definition and
   formula in-product (a `?` affordance), not just in code comments.
5. **Coach-first, fan-friendly.** Default views stay readable; depth is one
   click away.
6. **Season-agnostic core.** Season differences live in data, never in branches.
7. **Provenance always.** Every build records sources, timestamps, row counts and
   a content hash.

---

## 4. Workstream A — Season-proofing (reusability)

### 4.1 Target repository layout

```
data/
  registry.json                  # [{id, displayName, status, dir}] — drives all builds
  global/
    aliases.json                 # player + team aliases, roster history
    hero_classes.json            # role, lanes, damage type, scaling
    item_classes.json            # existing
    assets/manifest.json         # existing (additive across seasons)
  seasons/
    s18/
      season.json                # rules, endpoints, model priors
      mpl_id_s18.db
      csv/*.csv
      playoffs.json
      meta.json                  # provenance + schema_version + row counts
    s19/ …
dist/
  index.html                     # season landing page
  mpl_id_s18.html
  mpl_id_s19.html
```

### 4.2 Generic tooling

| Today | Target |
|---|---|
| `build_s18_db.py` | `tools/etl.py --season s18` |
| `gen_dark.py` | `tools/build.py --season s18 [--all]` |
| `check_parity.py` | parity per season, driven by `registry.json` |
| `verify.py` | `--season s18|all` |
| hardcoded outputs | `dist/mpl_id_<season>.html` |

**Compatibility:** keep `mpl_id_s18_dark.html` at the repo root as a pointer
stub for one release (or update README/CI in the same commit), so external
links don't break.

### 4.3 Extract code-resident data

Move out of `app.js` into `data/global/aliases.json`:

- `PLAYER_ALIAS` (MVP spelling → canonical)
- `SALIAS`, `GALIAS` (roster vs season-stat spelling)
- `LIQLANES` (per-player primary lane)
- `ROSTER_SPELLING`

Shape:

```json
{
  "players": {
    "coolfire": { "canonical": "Joshuaa", "seasons": ["s18"] },
    "lutpiii":  { "canonical": "Lutpi",   "seasons": ["s18"] }
  },
  "teams": { "bigetronbyvitality": "BTR" },
  "rosters": {
    "s18": { "TLID": ["Aran","Kevin","Drichel","Lyoni","Keven"] }
  },
  "lanes": { "nino": "EXP", "affan": "JUNGLE" }
}
```

Aliases are global + season-scoped so a player who changes IGN in S19 does not
rewrite S18 history.

### 4.4 Provenance and schema versioning

`data/seasons/s18/meta.json` is implemented with `schema_version`, `season_id`,
`layout`, `sources`, `row_counts` and `build_commit`. A SQLite `meta` table remains
optional/deferred; the JSON file is the provenance record used by the build and
the docs. The UI footer can surface the same counts when a season index is added.

### 4.5 Build & distribution ops

- **GitHub Pages** publishes `dist/` on tag; per-season archive stays online.
- **Scheduled data refresh** (daily during season, weekly otherwise) opens a
  **pull request** with rebuilt DB/CSV — never auto-pushes to `main`. Humans
  review data before publish.
- **Failure alerting:** ETL failure leaves last-known-good untouched (already
  true) and opens an issue.
- **Performance budget** per build: HTML < 1.5 MB, first render < 1.5 s on a
  mid-range phone.

### 4.6 Season onboarding checklist (the reusability test)

A new season is "supported" when this checklist needs **no code edits**:

1. Add `data/seasons/s19/season.json` (teams, aliases, slots, endpoints, priors).
2. Add roster / IGN aliases to `data/global/aliases.json`.
3. Run `python tools/etl.py --season s19`.
4. Run `python tools/build.py --season s19`.
5. Run `python tools/verify.py --season s19`.
6. Add the season to `data/registry.json`.

---

## 5. Workstream B — Data completeness

### 5.1 Ingestion backlog

| # | Data | Source | Effort | Value |
|---|---|---|---|---|
| B1 | Full draft: 5 picks + 5 bans per side, per game | Liquipedia `Map` template | 2 d | High |
| B2 | Per-game lane (EXP/JUNGLE/MID/GOLD/ROAM) | Liquipedia slot order + hero prior fallback | 2 d | **Very high** |
| B3 | Map mode per game | Liquipedia `mapmode` | 0.5 d | Medium |
| B4 | Ban order (`b1…b5`) + first ban by side | Liquipedia | 1 d | High |
| B5 | Hero metadata: role(s), lanes, damage type, scaling | mlbb.io / community lists, transcribed once into `hero_classes.json` | 2 d | **Very high** |
| B6 | Team per-game aggregates (gold, damage, tower dmg, kills diff) | derived from `game_players` | 1 d | High |
| B7 | Playoffs bracket + seeding (live) | mlbbhub `/playoffs` + Liquipedia | 1 d | Medium |
| B8 | Patch per week | Liquipedia / docs | 0.5 d | Medium |
| B9 | Season team objective totals (Lord/Turtle/Tower) | `id-mpl.com/statistics` scrape | 1 d | Low–Medium (season level only) |
| B10 | VOD deep links per game | Liquipedia + API | 0.5 d | Medium |
| B11 | Historical backfill S1–S17 (results + drafts where present) | Liquipedia | 5–8 d | High (era comparisons) |

**B2 detail — lane resolution order:**
1. Liquipedia slot lane (source = `liq_slot`).
2. If a hero was played by that player in ≥80% of games in one lane, use it
   (`inferred_player`).
3. Else hero's modal lane in the dataset (`inferred_hero`).
4. Else player's season lane (`inferred_season`).
5. Store `lane_source` on every row so the UI can label inferred values.

**Do not** store a lane without a source tag.

### 5.2 Data quality gates to add

- Draft coverage: every completed game has 10 picks + 10 bans, or is explicitly
  listed as uncovered.
- Lane coverage: 100% of player-rows have a lane **and** a `lane_source`.
- Cross-source agreement: API bans vs Liquipedia bans; mismatches reported, not
  silently overwritten.
- Aggregate reconciliation: team gold = sum of player gold, ±rounding.
- Orphan check: every `game_players` row joins a `games` row and a `matches` row.

### 5.3 Source strategy

| Source | Role | Freshness | Risk |
|---|---|---|---|
| mlbbhub API | authoritative per-player stats, schedule, standings | live | unofficial; ToS unverified |
| Liquipedia API | drafts, lanes, map, MVP, durations | near-live | robots.txt disallows generic crawling; use `api.php` with identifying UA, low rate |
| id-mpl.com | season objective totals, official player stats | season | HTML scraping, fragile |
| scoregg / id-mpl CDN | artwork | static | signed URLs expire — mirror locally (already done) |

**Rule:** every source adapter is isolated behind a module with a fixture-based
parser test, so a source change breaks one test, not the app.

---

## 6. Workstream C — Analytics engine (the differentiator)

### 6.1 Statistical foundations (build once, use everywhere)

| Mechanism | Why | Rule |
|---|---|---|
| **Role normalisation** | A tank's KDA is not comparable to a marksman's | Rank only within lane; show role percentile |
| **Shrinkage (empirical Bayes)** | 3-game samples produce fake 100% rates | Shrink toward role mean; weight by games played |
| **Wilson intervals** | Honest uncertainty on win rates | Show `n` and 95% CI; de-emphasise `n < 5` |
| **Opponent adjustment** | Beating weak teams inflates stats | Regress on opponent rating; report residual |
| **Hero adjustment** | A hero's strength inflates its players | Compare player to that hero's average performance |
| **Deterministic tie-breaks** | Reproducible tables | Count desc, then id asc (existing pattern) |

**Display rule:** any rate with `n < 5` renders muted with a tooltip
("small sample — treat as indicative"). Never hide it; never headline it.

### 6.2 Player metrics

**Volume / output**
- Games, K/D/A, KDA, GPM, gold share, damage share, damage-taken share,
  tower-damage share, kill participation.
- **Damage per gold** (efficiency), **gold per minute** (resource), **tower
  damage per game** (objective pressure).

**Quality / context**
- **Role percentile** for each metric (within lane, shrinkage applied).
- **Hero-adjusted residual**: player's damage share minus the same hero's
  average damage share across the league.
- **Opponent-adjusted residual**: performance vs expected given opponent rating.
- **Consistency**: interquartile range of per-game KDA / GPM / damage share;
  plus **floor** (p10) and **ceiling** (p90) — "how bad is his bad game?"
- **Form**: rolling last-5 games vs season baseline (delta, not absolute).
- **Close-game record**: win rate in games with final kill diff ≤ 5
  (proxy for composure — labelled as proxy, because no timeline exists).

**Pool**
- Unique heroes, effective pool (≥2 games and ≥50% WR), **comfort index**
  (usage × win rate), **flex score** (heroes played in ≥2 lanes).
- **Off-role penalty**: performance delta when playing outside primary lane.

**Impact composite** (documented weights, not a black box)
- `impact = w1·role_pct(damage share) + w2·role_pct(KP) + w3·role_pct(gold share)
  + w4·role_pct(tower dmg) − w5·role_pct(death share)`, weights shown in the UI
  and pinned by a test.

### 6.3 Team metrics

- **Rating** (Bradley-Terry on games, prior + bootstrap CI) and **strength of
  schedule** (mean opponent rating).
- **Form**: rolling 5-series and 5-game win rate, and rating delta.
- **Side profile**: blue/red win rate, side preference, and side-specific hero
  pool.
- **Tempo profile**: win duration vs loss duration; share of wins under 15 min
  and over 22 min; "fast-win" vs "late-win" identity.
- **Dominance**: mean gold differential, damage differential, tower-damage
  differential, kill differential; blowout rate (|kill diff| ≥ 10).
- **Clutch**: game-3 record, series-deciding-game record.
- **Draft identity**: unique heroes, hero-pool overlap between players, ban
  targets, first-ban tendency by side.
- **Head-to-head matrix** with per-game and per-series records.

All team aggregates are derivable by summing the five player rows — no new
source needed (B6).

### 6.4 Draft & meta analytics

Enabled by B1–B5.

- **Hero**: pick, ban, P+B, WR, WR by side, WR by patch, WR by map.
- **Flex rate**: share of a hero's games played in each lane.
- **Synergy**: hero pairs on the same team — games, WR, delta vs expectation.
- **Counter**: hero pairs on opposing teams — games, WR, delta vs expectation.
- **Player–hero fit**: player WR on hero vs league WR on that hero.
- **Team draft fingerprint**: most-picked, most-banned, first-ban by side,
  comfort-pick concentration (HHI), pocket picks (low league usage, high team
  usage).
- **Composition archetypes** (from `hero_classes.json`): frontline count, damage
  type balance, engage/CC count → win rate by archetype.
- **Meta movement**: week-over-week pick/ban deltas; "rising" and "falling"
  heroes.
- **Map meta**: pick/ban/WR by map mode.

> Explicitly out of scope: pick-order analysis (not in any source) and
> "counter-pick success" in the draft sense. Report only what the data shows.

### 6.5 Coach workflows (the reason to build all of the above)

| Workflow | What the coach gets | Data used |
|---|---|---|
| **Scouting report** | One page per opponent: likely picks/bans, side preference, tempo, comfort players, weak heroes, recent form | team + draft + player metrics |
| **Ban recommender** | Ranked bans by expected swing = opponent proficiency × your vulnerability; shows assumptions and sample sizes | hero pools, matchup WR |
| **Weakness finder** | Metrics where a player/team sits below role/league median, with `n` and CI; hero-specific and matchup-specific drops | player metrics |
| **Strength finder** | Above-median metrics, high-leverage players, best hero combos, best side/map | player + draft |
| **Matchup explorer** | Player-vs-player, hero-vs-hero, team-vs-team with sample size and CI | all |
| **Prep export** | Print/PDF one-pager + CSV of the underlying rows | all |

Every workflow must state **what it does not know** (e.g. "no objective data").

---

## 7. Workstream D — Product, UX and distribution

| # | Item | Detail |
|---|---|---|
| U1 | **Permalinks** | Encode view/season/hero/player/filters in the URL hash; every drill-down shareable |
| U2 | **Global search + command palette** | `Ctrl/⌘K`: players, teams, heroes, matches, metrics |
| U3 | **Metric explainers** | `?` on every derived stat → definition, formula, sample caveat |
| U4 | **Mobile tables** | Sticky first column, horizontal scroll affordance, 44 px tap targets |
| U5 | **Season switcher** | Header control; only when `registry.json` has >1 season |
| U6 | **Share cards** | Generated OG image per player/team/hero (static at build time) |
| U7 | **Export** | CSV per table; print stylesheet for prep sheets |
| U8 | **Accessibility** | Keyboard traps fixed, focus visible, contrast ≥ 4.5:1, `aria-live` on refresh status |
| U9 | **Freshness banner** | "Data as of … · last ETL … · build …" with a changelog link |
| U10 | **PWA / offline** | Single-file already works offline; add service worker only for multi-file builds |

---

## 8. Phased roadmap

### Phase 0 — Season-proof the core · ~8–10 days

**Goal:** Season 19 becomes configuration, not a fork.

- A1 `data/registry.json` + per-season directory layout
- A2 `tools/etl.py --season` and `tools/build.py --season` wrappers
- A3 Extract aliases/lanes to `data/global/aliases.json`
- A4 `meta` table + `meta.json` provenance
- A5 Move output to `dist/`; update CI, parity, README
- A6 Season onboarding checklist documented

**Status (2026-10-21):** A1–A3 and A6 landed. A4 landed as
`data/seasons/s18/meta.json`; the SQLite `meta` table is deferred. A5 landed as
`--season` output while keeping the root artifact for link compatibility; a
`dist/` season index is Phase 4. S18 deliberately keeps `layout:"legacy"` rather
than moving files. Verify is 18/18.

**Exit:** S18 output is byte-identical after the refactor; `verify.py` green;
adding a stub `s19` config produces a build with no code edits.

### Phase 1 — Complete the dataset · ~10–12 days

**Goal:** Every game has draft, lane, map and team aggregates.

- B1 Liquipedia draft parser (picks, bans, order, VOD)
- B2 Per-game lane with source tags + fallback chain
- B3 Map mode
- B5 `hero_classes.json`
- B6 Team game aggregates
- Added data-quality gates

**Status (2026-10-24):** B1-B6 landed. 174/174 completed games have 10 picks;
172/174 have 10 unique bans (one source duplicate and one blank placeholder
removed; exceptions listed in `data/seasons/s18/quality.json`). 1,740/1,740
player rows are tagged `liq_slot`. 153/174 games have a map mode; the 21
missing are the Week 9 source gap.
`hero_classes.json` covers all 133 heroes (damage type derived and labelled).
`team_games` (348 rows) and `team_season_stats` (9 teams) reconcile with
standings on wins/losses. The data is surfaced in the game dialog (map mode,
ordered bans, lane-ordered picks), the hero table (role/lane/damage) and the team
profiles under Standings.

**Exit:** 100% of completed games have 10 picks and every player row has a
lane + `lane_source`; the two 9-ban source gaps are listed; cross-source ban
mismatches are listed; `verify.py` gains draft/lane/aggregate suites and passes.

### Phase 2 — Analytics engine · ~15–20 days

**Goal:** The numbers other sites don't have, with honest uncertainty.

- C1 Statistical primitives (shrinkage, Wilson CI, role percentile)
- C2 Player metric library + tests
- C3 Team ratings + strength of schedule
- C4 Consistency / form / close-game profile
- C5 Draft analytics (flex, synergy, counter, fingerprint)
- C6 Composition archetypes
- C7 New "Analytics" view with metric explainers

**Status (2026-10-22): complete.** C1–C7 landed.
C1/C2: Wilson CI, shrinkage, lane percentiles, the pinned impact composite,
per-player KDA/GPM/damage/KP/death shares, p10–p90/IQR consistency, form delta,
off-lane delta, hero-adjusted damage, effective pool, comfort/flex, damage per
gold, close-game record, opponent split and hero-fit vs league. C3/C4: Bradley-
Terry ratings with bootstrap CIs, SOS, form (games and series), side splits,
tempo, dominance, game-3/series-close records, map records and a head-to-head
matrix. C5/C6: hero flex/side/map splits, synergy, counters, team fingerprints,
meta movement and composition archetypes. C7: Players/Teams/Draft Analytics
sub-tabs with method text, sample sizes and proxy labels. `tools/test_analytics.js`
has 160 deterministic assertions; `verify.py` is green.

**Exit:** satisfied. Every metric has a unit test on a deterministic fixture and
a definition in-product; rates are not shown without `n`; `verify.py` is 18/18.

### Phase 3 — Coach workspace · ~12–18 days

**Goal:** A coach can prep a series in under 10 minutes.

- D1 Scouting report generator
- D2 Ban recommender with visible assumptions
- D3 Weakness / strength finder
- D4 Matchup explorer
- D5 Prep export (print + CSV)
- D6 Saved/shareable reports (permalink)

**Status (2026-10-22): complete.** The **Prep** view takes an opponent and an
optional "our team" and produces: rating/form/side/tempo tiles, likely picks and
bans, a ban ranking (presence × opponent WR, with the proxy and sample sizes
shown), player weaknesses/strengths by lane percentile, weak/strong maps, H2H and
lane matchups, and print/PDF + CSV export. The URL records view/opponent/team so
the report is shareable; `Ctrl/⌘K` searches players, teams, heroes and matches.
No player-vs-player head-to-head exists in the source, and the report says so.

**Exit:** satisfied for the available data. Every claim is derived from the DB;
the report explicitly states what it does not know (no objectives, timelines or
pick order).

### Phase 4 — Scale & polish · ongoing

- E1 Multi-season comparison / career views
- E2 Historical backfill (S1–S17 results + drafts where available)
- E3 Additional regions (MPL PH / MY) if the pipeline holds
- E4 Public launch: Pages, docs, screenshots, changelog
- E5 Accessibility and performance hardening

**Status (2026-10-22):** E5 baseline landed: visible focus, skip link, synced
`aria-selected` tabs, dialog focus trap, sticky first column and 34 px controls
on mobile, and a print stylesheet. E1–E3 remain future/data-limited: only S18 is
loaded, no historical source is committed, and no other region pipeline is
configured. E4 needs deployment credentials and is not performed from this repo.

**Total to Phase 3:** roughly **45–60 focused days** (~3 months part-time).

---

## 9. Backlog (actionable)

| ID | Item | Phase | Effort | Depends on | Done when |
|---|---|---|---|---|---|
| A1 | Season registry + directory layout | 0 | 2 d | — | `registry.json` drives every tool |
| A2 | `etl.py` / `build.py --season` | 0 | 2 d | A1 | `--season s18` reproduces current output |
| A3 | Extract aliases/lanes to JSON | 0 | 1.5 d | A1 | No alias/lane literals in `app.js` |
| A4 | `meta` provenance table | 0 | 1 d | A1 | Build records sources, counts, commit |
| A5 | `dist/` output + CI/README update | 0 | 1.5 d | A1 | Parity gate passes on new path |
| A6 | Season onboarding checklist | 0 | 0.5 d | A1–A5 | Checklist executed for a stub season |
| B1 | Liquipedia full draft parser | 1 | 2 d | A2 | 10 picks + 10 bans per game stored |
| B2 | Per-game lane + source tag | 1 | 2 d | B1 | 100% lane coverage, source recorded |
| B3 | Map mode ingestion | 1 | 0.5 d | B1 | `games.map_mode` populated |
| B4 | Ban order + first ban | 1 | 1 d | B1 | `game_bans.ban_order` populated |
| B5 | `hero_classes.json` | 1 | 2 d | — | Every picked hero has role/lanes/damage |
| B6 | Team game aggregates | 1 | 1 d | — | Gold/damage/tower diffs per game |
| B7 | Playoffs bracket live | 1 | 1 d | A2 | Bracket + seeding from data |
| B8 | Patch per week | 1 | 0.5 d | A2 | Patch stored per game |
| B9 | Season objective totals | 1 | 1 d | — | Team Lord/Turtle/Tower totals stored |
| B10 | VOD deep links | 1 | 0.5 d | B1 | Every game links to its VOD |
| B11 | Historical backfill | 4 | 5–8 d | A2 | ≥3 prior seasons browsable |
| C1 | Statistical primitives | 2 | 3 d | B2, B5 | Shrinkage/CI/percentile unit-tested |
| C2 | Player metrics | 2 | 4 d | C1 | All metrics defined + tested |
| C3 | Team ratings + SoS | 2 | 3 d | C1 | Rating with CI, reproducible |
| C4 | Consistency/form/clutch | 2 | 2 d | C2 | Form deltas visible per player |
| C5 | Draft analytics | 2 | 4 d | B1, B4 | Flex/synergy/counter/fingerprint |
| C6 | Composition archetypes | 2 | 2 d | B5 | WR by archetype with `n` |
| C7 | Analytics view + explainers | 2 | 3 d | C2–C6 | Definitions in-product |
| D1 | Scouting report | 3 | 4 d | C2–C5 | One-page opponent report |
| D2 | Ban recommender | 3 | 3 d | C5 | Ranked bans with assumptions shown |
| D3 | Weakness/strength finder | 3 | 3 d | C2 | Below/above-median lists with CI |
| D4 | Matchup explorer | 3 | 3 d | C2, C5 | Player/hero/team matchups |
| D5 | Prep export | 3 | 2 d | D1 | Print + CSV verified |
| D6 | Shareable reports | 3 | 2 d | D1 | Permalink reproduces the report |
| U1 | Permalinks | 2–3 | 2 d | A1 | Every view restores from URL |
| U2 | Search + palette | 3 | 2 d | — | `Ctrl/⌘K` finds any entity |
| U3 | Metric explainers | 2 | 1 d | C2 | `?` on every derived stat |
| U4 | Mobile tables | 2 | 2 d | — | Usable at 360 px |
| U8 | Accessibility pass | 4 | 3 d | — | Automated + manual checks pass |
| E4 | Public launch | 4 | 3 d | Phase 3 | Pages live, docs current |

**Backlog status (2026-10-22):** A1–A6, B1–B6, B10, C1–C7, D1–D6, U2 and
view-level U1 permalinks have landed. U3 explainers are in-product method text;
U4/U8 have the baseline described above. B7 is a static bracket preview; B8
(patch), B9 (season objective totals) and B11 (historical backfill) need sources
that are not committed. E4 needs deployment credentials.

---

## 10. Idea bank (bigger bets, not committed)

> The full idea layer — global time filtering, patch pins, A/B comparison, and
> ~40 derived insights with data dependencies and effort — lives in
> [`docs/INSIGHT_CATALOGUE.md`](INSIGHT_CATALOGUE.md). This section is the short
> list of bigger bets.

These are worth exploring once the core is solid. Each is explicitly *not* in
the committed roadmap.

- **Draft simulator with win probability** — expose the model, not just the
  number.
- **"What-if" roster analysis** — replace player X with the league-median at that
  role and re-estimate team rating.
- **Automated objective capture via broadcast OCR** — the only credible path to
  per-game Lord/Turtle data. High effort, high moat.
- **Highlight timestamps** — derive from VOD + kill events if a timeline source
  ever appears.
- **Public JSON API** — let analysts build on the cleaned dataset.
- **Era comparisons** — "is this the strongest MPL ID team ever?" using
  cross-season ratings with era adjustment.
- **Community layer** — predictions, tier lists, discussion (only if moderation
  is sustainable).
- **Multi-region** — MPL PH/MY with the same pipeline, for international
  comparisons.

---

## 11. Risks and non-goals

### Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Upstream API changes or disappears | Medium | Adapter modules + fixture tests; DB is the durable artifact |
| Liquipedia access restricted | Medium | Cache wikitext; degrade gracefully to API-only data |
| Small samples produce misleading rankings | **High** | Shrinkage + CI + visible `n`; never headline `n < 5` |
| Alias / roster churn corrupts history | Medium | Global alias file with season scoping; reconciliation gate |
| Multi-season refactor breaks S18 | Medium | Byte-identical output check before/after Phase 0 |
| Scope creep (other regions, live tracking) | High | Phases and non-goals are explicit |
| Bus factor of one | High | Documents, tests, and reproducible builds are the mitigation |

### Non-goals

- Live in-match tracking or real-time win probability.
- Betting odds or gambling-adjacent features.
- Fabricating MANIAC / SAVAGE or any unavailable statistic.
- Scraping authenticated, paid, or explicitly disallowed sources.
- Full LoL-style timeline analytics (gold curves, vision, objective control) —
  the data does not exist publicly for MPL ID.
- Replacing the official broadcast or the official MPL site.

---

## 12. After Phase 3 (remaining work)

1. **Season 19 onboarding** — follow the README checklist. This is config/data
   only, but it remains an unexecuted test until S19 data exists.
2. **Deployment** — publish the single-file artifact (or a `dist/` index) to
   Pages. E4 needs credentials and is not performed from this repo.
3. **Source-gated upgrades** — patch per week (B8), season objective totals (B9)
   and historical backfill (B11). Do not infer missing values; add the source
   adapter and fixture test first.
4. **Explainers** — method text is in-product for analytics and Prep; add per-
   metric `?` tooltips if usability testing asks for them.
5. **Multi-season / regions** — E1/E3 once a second season or region pipeline
   exists. The registry and `--season` wrappers are ready; the data is not.

---

## 13. How we will know it worked

- Onboarding a new season takes **under one day** and touches **no application
  code**.
- Every number on screen has a definition, a sample size, and a source.
- A coach can answer "what does ONIC ban on red side, and who do we exploit?"
  in **two clicks**.
- The project publishes at least six analyses that no other public MPL ID source
  does: role-normalised player ratings, opponent-adjusted performance, hero-pool
  flex map, composition archetype win rates, map-mode tendencies, and a
  generated scouting report.
- A stranger can clone the repo, run two commands, and get a working build.

---

*Last updated: 2026-10-22. This document is the plan of record; changes should
be proposed as edits to this file so the roadmap stays reviewable.*
