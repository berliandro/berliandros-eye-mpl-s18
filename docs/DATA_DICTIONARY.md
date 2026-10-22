# Data Dictionary — MPL ID Season 18

Status: current for `data/seasons/s18/meta.json` (schema version 1). This file
describes every table and the derived numbers shown in the app. If a value is
not in a source, it is shown as `–`; it is never inferred without a label.

## Sources

| Source | Used for | Notes |
|---|---|---|
| `mpl.mlbbhub.com/api/v1/id` | per-player stats, schedule, standings, match results | unofficial; the durable artifact is the committed DB/CSV |
| `liquipedia.net/mobilelegends/api.php` | picks, ordered bans, lane slots, map mode, VOD, duration, MVP | low-rate API use; page `MPL/Indonesia/Season_18/Regular_Season` |
| `id-mpl.com` | cross-checks / artwork | season-level objective totals are **not** ingested |

Snapshot: 69 completed series, 167 games, 1,670 player rows, 1,670 picks,
1,669 ordered bans, 9 teams. `data/seasons/s18/meta.json` records the source
URLs, row counts and ETL commit.

## Tables

### `matches` (69 rows)

`match_detail_id` (PK), `schedule_id`, `team_a`, `team_b`, `score_a`, `score_b`,
`date`, `iso_date`, `iso_datetime`, `status`, `winner`, `vod_url`,
`match_detail_url`, `liq_mvp`.

- One row per completed series. `liq_mvp` is the Liquipedia series MVP, not a
  per-game MVP.

### `games` (167 rows)

`match_detail_id` + `game_no` (PK), `team_a`, `team_b`, `team_a_kills`,
`team_b_kills`, `winner` (`team_a`/`team_b`), `duration_str`, `duration_sec`,
`team_a_side`, `team_b_side` (`blue`/`red`), `vod_url`, `map_mode`.

- `team_*_side` is the recorded side, not a guess. `map_mode` is missing for 21
  games (Week 9 source gap) and is shown as `Unknown` in analytics.
- `vod_url` is populated for 167/167 games.

### `game_players` (1,670 rows)

`match_detail_id`, `game_no`, `team`, `player`, `lane`, `hero`, `kills`,
`deaths`, `assists`, `kda`, `gold`, `gold_per_min`, `hero_damage`,
`damage_taken`, `tower_damage`, `emblem`, `items_json`, `talents_json`,
`lane_source`.

- 10 rows per completed game. `lane` is one of EXP/JUNGLE/MID/GOLD/ROAM.
- `lane_source` records how the lane was obtained. Current snapshot:
  `liq_slot` for 1,670/1,670 rows. No lane is stored without a source tag.
- `items_json` / `talents_json` are arrays of item/rune references; artwork is
  resolved through `data/global/item_classes.json` and the local asset manifest.

### `game_picks` (1,670 rows)

`match_detail_id`, `game_no`, `team`, `side`, `slot`, `lane`, `hero`, `player`.

- 5 picks per team per game. `slot` is Liquipedia's lane-order slot
  (EXP→JUNGLE→MID→GOLD→ROAM), **not** pick order. Pick order is not published.

### `game_bans` (1,669 rows)

`match_detail_id`, `game_no`, `side` (`A`/`B`), `hero`, `ban_order`.

- 10 bans per game, ordered. 166/167 games have 10 unique bans; match 1088
  game 1 has 9 because the API returned a duplicate that was removed. The
  exception is asserted in `tools/test_enrich.py`.

### `hero_stats` (133 rows)

`hero`, `hero_image`, `pick`, `ban`, `win`, `win_rate`.

- One row per hero in the season snapshot (including zero-pick heroes).
- Analytics recompute from `game_picks`/`game_bans`; this table is the
  season-summary source for the Stats view.

### `player_season_stats` (66 rows)

`player`, `team`, `team_slug`, `lane`, `total_games`, `total_kills`,
`avg_kills`, `total_deaths`, `avg_deaths`, `total_assists`, `avg_assists`,
`avg_kda`, `kill_participation`.

- Season totals from the API. The app's player analytics use per-game rows, not
  these aggregates.

### `standings` (9 rows)

`rank`, `team_name`, `team_slug`, `match_point`, `match_win`, `match_lose`,
`game_win`, `game_lose`, `net_game_win`.

- Official regular-season standings snapshot.

### `schedule_all` (80 rows)

`schedule_id`, `team_a`, `team_b`, `score_a`, `score_b`, `date`, `iso_date`,
`iso_datetime`, `status`, `winner`, `vod_url`, `match_detail_id`,
`match_detail_url`.

- 72 regular-season + 8 playoff fixtures. `match_detail_id` is empty/null for
  fixtures that have not been played.

### `team_games` (334 rows, derived)

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

- Sums `team_games` per team. Wins/losses reconcile with `standings` 9/9.

## JSON configuration

| File | Purpose |
|---|---|
| `data/registry.json` | season ids, display names, directories, `layout` (`legacy` for S18) |
| `data/global/aliases.json` | canonical player/team spellings, rosters, primary lanes |
| `data/global/hero_classes.json` | 133 heroes: role, primary lane, specialties, damage type, empirical lane shares |
| `data/global/item_classes.json` | item identifiers → category/artwork grouping |
| `data/seasons/s18/season.json` | season rules, endpoints, priors |
| `data/seasons/s18/meta.json` | schema version, sources, row counts, ETL commit |
| `data/seasons/s18/playoffs.json` | bracket/seed snapshot |

## Derivations used in the app

### Lane resolution chain

1. Liquipedia slot (`liq_slot`).
2. Player's ≥80% stable lane (`inferred_player`).
3. Hero's modal lane (`inferred_hero`).
4. Player's season lane (`inferred_season`).

The current snapshot resolves all 1,670 rows at step 1. Every row keeps
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
- Impact = 35% damage-share percentile + 25% KP percentile + 20% gold-share
  percentile + 10% tower-share percentile − 10% death-share percentile. Each
  component is a lane percentile shrunk toward the lane mean with a 5-game prior.

### Uncertainty

- Wilson 95% intervals for win rates; `n` is always shown.
- Rows with `n < 5` are muted and labelled indicative.
- Team ratings: Bradley-Terry on game results with a 1–1 prior against an
  average team and 100 bootstrap resamples; displayed as
  `1500 + 400·log10(strength)`. SOS is the mean fitted opponent rating.
- Pair synergy: pair WR − average of the two heroes' individual WRs.
- Counter delta: hero A WR vs B − average of A's WR and B's loss rate.
- Ban score = opponent presence per game × opponent WR on the hero. It does not
  model our draft or pick order.
- Composition archetypes: frontline = Tank/Fighter count; damage = 3+ physical
  or 3+ magic picks; CC = specialties mentioning Crowd Control/Initiator/Engage.

## Data-quality gates

`python tools/verify.py` runs 18 suites, including:

- 167/167 completed games have 10 picks.
- 166/167 have 10 unique bans; the exception is listed.
- 1,670/1,670 player rows have a lane and `lane_source`.
- API vs Liquipedia bans reconciled; score/ban mismatches reported.
- Team aggregates reconcile with player sums and standings.
- Orphan checks for `game_players` → `games`/`matches`.
- Generated-output parity, XSS sinks, season config, ruff, and analytics tests.

## Known gaps (do not infer)

- No per-game Lord/Turtle/Tower counts.
- No gold/damage timelines, gold-diff-at-15, comeback curves or objective control.
- No pick order (Liquipedia slots are lane order).
- No MANIAC/SAVAGE counts.
- Map mode missing for 21 games (Week 9 source gap).
- No official damage-type split; composition analysis uses the labelled proxy.
- No player-vs-player head-to-head; matchup explorer compares lane-level
  season metrics only.
