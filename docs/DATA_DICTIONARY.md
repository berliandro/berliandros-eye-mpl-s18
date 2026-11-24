# Data Dictionary — MPL ID Season 18

Status: current for `data/seasons/s18/meta.json` (schema version 1). This file
describes every table and the derived numbers shown in the app. If a value is
not in a source, it is shown as `–`; it is never inferred without a label.

## Sources

| Source | Used for | Notes |
|---|---|---|
| `mpl.mlbbhub.com/api/v1/id` | per-player stats, schedule, standings, match results | unofficial; the durable artifact is the committed DB/CSV |
| `liquipedia.net/mobilelegends/api.php` | picks, ordered bans, lane slots, map mode, VOD, duration, MVP | low-rate API use; pages `MPL/Indonesia/Season_18/Regular_Season` and `/Playoffs` |
| `id-mpl.com` | cross-checks / artwork | season-level objective totals are **not** ingested |

Snapshot: 80 completed series, 215 games, 2,150 player rows, 2,150 picks,
2,149 ordered bans, 430 team-game rows, 9 teams. `data/seasons/s18/meta.json`
labels this snapshot `final`, scope `completed regular season and playoffs`,
verified as of 2026-11-08, and records the source URLs, row counts,
reconciliation and ETL commit.

## Snapshot and metric contracts

- **Canonical snapshot.** `data/mpl_id_s18.db` is the committed source of truth.
  `data/csv/*` and the embedded `DATA` object in `mpl_id_s18_dark.html` are
  generated from that snapshot. `tools/reconcile.py` derives records from raw
  `matches`/`games` rows and compares them with the official `standings` table.
- **Series/match W-L.** Official standings are regular-season only; the app's
  team records also include the eight playoff series. A series is won by the
  decisive score; playoff rows are identified by `schedule_id`.
- **Game W-L.** Completed games won/lost across the whole season. Derived from
  `games.winner`, with exactly one winner per game; the official standings
  table remains the regular-season slice.
- **GP.** In Analytics -> Teams and Team profiles, GP means game appearances
  (team-game rows), not series played. Series W-L is shown separately.
- **Scope.** The current final snapshot has **80 completed series and 215 games**
  (72 regular-season fixtures + 8 playoff series). The official `standings` table
  remains the **72-series / 174-game regular season**, so standings checks filter
  playoff rows explicitly rather than comparing them with the bracket. The ETL
  gate validates every completed series; `tools/write_meta.py` writes
  `snapshot_status: final` only when the regular season is final and the
  declared playoff fixtures, detail rows, game rows and standings all agree;
  otherwise it writes `partial`.
- **Official standings.** Preserved as source-published match/game records and
  used as a reconciliation target. They are not substituted for derived tables.
- **Refresh/cache.** A successful live refresh merges raw rows, preserves
  enrichment fields (map mode, recorded sides, VOD, lane, ban order), keeps
  last-good ordered bans for any game whose API payload has none, rebuilds
  picks/team games/team season stats from that same raw snapshot, clears cached
  analytics, and stores all of those inputs under cache schema 4. A refresh is
  complete for the **72-fixture regular season**: all configured regular
  fixtures have detail rows, the standings totals match that schedule, and every
  game still has ten picks, two team rows, recorded sides and at least nine
  ordered bans. The committed final snapshot additionally carries the 8 playoff
  series. Failed IDs, missing completed results and draft gaps keep the
  last-good rows and are labelled `partially updated`.
  The cache fingerprint covers standings, schedule, raw detail, picks and
  derived aggregates; cache validation re-derives those aggregates from the
  cache's own raw rows, rejects a mixed entry, and rejects a cache claiming
  complete while results are missing.

## Tables

### `matches` (80 rows)

`match_detail_id` (PK), `schedule_id`, `team_a`, `team_b`, `score_a`, `score_b`,
`date`, `iso_date`, `iso_datetime`, `status`, `winner`, `vod_url`,
`match_detail_url`, `liq_mvp`.

- One row per completed series. The final 80 include the eight playoff series;
  `schedule_id` identifies them. `liq_mvp` is the Liquipedia series MVP, not a
  per-game MVP.

### `games` (215 rows)

`match_detail_id` + `game_no` (PK), `team_a`, `team_b`, `team_a_kills`,
`team_b_kills`, `winner` (`team_a`/`team_b`), `duration_str`, `duration_sec`,
`team_a_side`, `team_b_side` (`blue`/`red`), `vod_url`, `map_mode`.

- `team_*_side` is the recorded side, not a guess. `map_mode` is missing for 21
  games (Week 9 source gap) and is shown as `Unknown` in analytics.
- `vod_url` is populated for 206/215 games.

### `game_players` (2,150 rows)

`match_detail_id`, `game_no`, `team`, `player`, `lane`, `hero`, `kills`,
`deaths`, `assists`, `kda`, `gold`, `gold_per_min`, `hero_damage`,
`damage_taken`, `tower_damage`, `emblem`, `items_json`, `talents_json`,
`lane_source`.

- 10 rows per completed game. `lane` is one of EXP/JUNGLE/MID/GOLD/ROAM.
- `lane_source` records how the lane was obtained. Current snapshot:
  `liq_slot` for 2,150/2,150 rows. No lane is stored without a source tag.
- `items_json` / `talents_json` are arrays of item/rune references; artwork is
  resolved through `data/global/item_classes.json` and the local asset manifest.

### `game_picks` (2,150 rows)

`match_detail_id`, `game_no`, `team`, `side`, `slot`, `lane`, `hero`, `player`.

- 5 picks per team per game. `slot` is Liquipedia's lane-order slot
  (EXP→JUNGLE→MID→GOLD→ROAM), **not** pick order. Pick order is not published.

### `game_bans` (2,149 rows)

`match_detail_id`, `game_no`, `side` (`A`/`B`), `hero`, `ban_order`.

- 10 bans per game, ordered. 214/215 games have 10 unique bans; match 1088
  game 1 has 9 (the API returned a duplicate/blank row). Blank hero ids are
  filtered at ETL and enrichment; match 1107 game 2 had no API bans and was
  filled from Liquipedia. `data/seasons/s18/quality.json` records the
  exceptions and source conflicts.

### `hero_stats` (133 rows)

`hero`, `hero_image`, `pick`, `ban`, `win`, `win_rate`.

- One row per hero in the season snapshot (including zero-pick heroes).
- Analytics recompute from `game_picks`/`game_bans`; this table is the
  season-summary source for the Stats view.

### `player_season_stats` (66 rows)

`player`, `team`, `team_slug`, `lane`, `total_games`, `total_kills`,
`avg_kills`, `total_deaths`, `avg_deaths`, `total_assists`, `avg_assists`,
`avg_kda`, `kill_participation`.

- Season totals from the API, including playoff games in this final snapshot.
  The app's player analytics use per-game rows, not these aggregates.

### `standings` (9 rows)

`rank`, `team_name`, `team_slug`, `match_point`, `match_win`, `match_lose`,
`game_win`, `game_lose`, `net_game_win`.

- Official regular-season standings snapshot.

### `schedule_all` (80 rows)

`schedule_id`, `team_a`, `team_b`, `score_a`, `score_b`, `date`, `iso_date`,
`iso_datetime`, `status`, `winner`, `vod_url`, `match_detail_id`,
`match_detail_url`.

- 72 regular-season + 8 playoff fixtures. All 80 have details in this final
  snapshot.

### `team_games` (430 rows, derived)

`match_detail_id`, `game_no`, `team`, `opponent`, `players`, `kills`, `deaths`,
`assists`, `gold`, `hero_damage`, `damage_taken`, `tower_damage`, `kda`, `win`,
`map_mode`, `duration_sec`.

- Two rows per completed game. All totals are sums of the team's five
  `game_players` rows; `win` is derived from `games.winner`; `opponent` is the
  other team. No new source is used.
- `players` is the count of player rows reconciled (expected 5).
- Rebuilt by `tools/aggregate_teams.py`; the same SQL is used by the ETL.

### `team_season_stats` (9 rows, derived)

`team`, `games`, `wins`, `losses`, `kills`, `deaths`, `assists`, `gold`,
`hero_damage`, `damage_taken`, `tower_damage`, `kda`, `win_rate`, `avg_gold`,
`avg_duration_sec`, `team_name`, `team_slug`.

- Sums `team_games` per team across the completed season, so the dossier record
  includes playoffs. The official regular-season `standings` reconcile with the
  regular-season slice of `team_games`, not with this whole-season aggregate.

## JSON configuration

| File | Purpose |
|---|---|
| `data/registry.json` | season ids, display names, directories, `layout` (`legacy` for S18) |
| `data/global/aliases.json` | canonical player/team spellings, rosters, primary lanes |
| `data/global/hero_classes.json` | 133 heroes: role, primary lane, specialties, damage type, empirical lane shares |
| `data/global/item_classes.json` | item identifiers → category/artwork grouping |
| `data/season.json` | season rules, endpoints, priors (legacy layout) |
| `data/seasons/s18/meta.json` | snapshot status/scope, sources, row counts, reconciliation, ETL commit |
| `data/seasons/s18/quality.json` | source conflicts, blank-ban disposition, missing map/lane counts |
| `data/seasons/s18/playoffs.json` | bracket/seed snapshot |

## Derivations used in the app

### Lane resolution chain

1. Liquipedia slot (`liq_slot`).
2. Player's ≥80% stable lane (`inferred_player`).
3. Hero's modal lane (`inferred_hero`).
4. Player's season lane (`inferred_season`).

The current snapshot resolves all 2,150 rows at step 1. Every row keeps
`lane_source` so the UI can label inferred values if the source changes.

### Hero classes

- Role, primary lane and specialties: Liquipedia infobox.
- `damage_type`: **derived** by counting physical/magic/true references in the
  ability text; stored as `derived:ability_text`, not an official field.
- `lanes_empirical`: pick shares per lane from `game_picks`.

### Player analytics (`buildPlayerMetrics`)

- KDA = (kills + assists) / max(1, deaths), averaged per game.
- Damage/gold/tower/death shares = player value / team value for that game.
- Kill participation = (kills + assists) / team kills.
- Consistency = p10/p25/p50/p75/p90 and IQR of per-game KDA.
- Form delta = mean KDA of the last 5 games − season mean KDA.
- Off-lane delta = mean KDA outside the modal lane − mean KDA in the modal lane.
- Hero-adjusted damage = mean(damage share − that hero's league mean damage share).
- Effective pool = heroes with ≥2 games and ≥50% WR.
- Comfort = max over heroes of (usage share × hero WR).
- Close-game record = win rate when the final kill difference is ≤5 (proxy;
  no timeline exists).
- Opponent split = stats vs teams with season WR ≥50% vs <50%.
- Impact = 30% damage-share percentile + 20% KP percentile + 15% gold-share
  percentile + 10% tower-share percentile + 15% KDA percentile − 10% death-share
  percentile. Each component is a lane percentile shrunk toward the lane mean
  with a 5-game prior. `tools/test_analytics.js` pins these weights.

### Uncertainty

- Wilson 95% intervals for win rates; `n` is always shown.
- Rows with `n < 5` are muted and labelled indicative.
- Team ratings: Bradley-Terry on **one paired observation per game** with a
  1–1 prior against an average team. The bootstrap resamples whole games, keeping
  opponents paired, and uses 100 resamples; displayed as
  `1500 + 400·log10(strength)`. SOS is the mean fitted opponent rating.
- Player death share: player deaths / that team’s total deaths in the same
  game. A zero-team-death game yields 0 for every player, never a division by
  team kills or an invented value.
- Pair synergy: pair WR − average of the two heroes' individual WRs.
- Counter delta: hero A WR vs B − average of A's WR and B's loss rate.
- Ban threat score = opponent **pick presence** (picks / games) × opponent
  win rate on that hero. The opponent’s own bans are reported separately as
  contest context and do not enter the score. It is a proxy for pick threat,
  not evidence of their draft intent, and it does not model our draft or pick
  order. Ban-only heroes are not treated as pick threats.
- Composition archetypes: frontline = Tank/Fighter count; damage = 3+ physical
  or 3+ magic picks; CC = specialties mentioning Crowd Control/Initiator/Engage.
- Meta movement uses the last two **non-empty 7-day date windows** counted from
  the first game date. They are not official competition weeks; the UI states
  whether the compared windows are adjacent. Windows can straddle the
  regular-season/playoff boundary if future data adds playoffs.
- Pair and counter tables are sorted by **sample size**, so their labels say
  "most observed". `delta` versus baseline is the effect measure; it is
  descriptive, not causal.
- Weak/strong maps exclude `Unknown`, null, empty and unresolved labels. Missing
  map rows remain in overall team records and are surfaced as a data-quality
  count.

## Data-quality gates

`python tools/verify.py` runs 29 suites, including:

- 215/215 completed games have 10 picks and 2,150/2,150 picks have a player.
- 214/215 have 10 unique bans; the 9-ban exception (1088 game 1) is listed.
- 2,150/2,150 player rows have a lane and `lane_source`.
- 80 matches, 215 games and 430 team-game rows; every game has one winner.
- The official regular-season standings reconcile with the 72-fixture regular
  slice for all nine teams; team aggregates reconcile with player sums.
- API vs Liquipedia bans reconciled; score/ban mismatches reported.
- Orphan checks for `game_players` → `games`/`matches`.
- Generated-output parity, XSS sinks, season config, ruff, analytics tests, and
  the 160px player-card derivative provenance gate.

## Known gaps (do not infer)

- No per-game Lord/Turtle/Tower counts.
- No gold/damage timelines, gold-diff-at-15, comeback curves or objective control.
- No pick order (Liquipedia slots are lane order).
- No MANIAC/SAVAGE counts.
- Map mode missing for 21 games (source gap; listed in `quality.json`).
- Match 1107 game 2: Liquipedia lists TLID slot 3 as Zetian; the API scoreboard
  lists Drichel/Zhuxin. The canonical pick follows the API scoreboard hero and
  player (the row that owns that game's stats) and records the conflict in
  `quality.json`; this is a source conflict, not a silently merged row. The API
  also returned no side or ban fields for this game; sides and the ten ordered
  bans come from Liquipedia and are labelled as such in `quality.json`.
- No official damage-type split; composition analysis uses the labelled proxy.
- No player-vs-player head-to-head; matchup explorer compares lane-level
  season metrics only.
