# MPL ID Season 18 — Player/Match Database

Format chosen: **SQLite (`mpl_id_s18.db`) + CSV exports (`csv/`)**. SQLite = proper relational storage (queryable, typed, single file); CSV = portable fallback. Builder: `build_s18_db.py`. Quick check: `verify_db.py`.

## Sources (fetched Oct 3 2026)
- Liquipedia `MPL/Indonesia/Season_18/Regular_Season` wikitext via `api.php` (71 series parsed) — used only for `liq_mvp` merge.
- mlbbhub API `https://mpl.mlbbhub.com/api/v1/id`:
  - `/matches` (80 entries), `/schedule`, `/standings` (9), `/stats/players` (64), `/drafts`, `/match/<detail_id>` (50 completed)

## Coverage (audited)
- `schedule_all`: 80 rows = 50 completed + 2 live + 28 upcoming (all Season 18 fixtures).
- `matches`: 50 rows (detail_ids 1036–1085 + 1087; 1086 = live GEEK-DEWA, no detail yet). 49/50 have Liquipedia MVP (Oct 3 BTR-RRQ MVP blank in source).
- `games`: 115 rows (avg 2.3 games/series).
- `game_players`: 1150 rows (115×10), 61 distinct players. `gold_per_min` computed, 0 NULLs.
- `game_bans`: 1150 rows (10 bans/game).
- `player_season_stats`: 64 rows (includes 0-game subs e.g. Miguel, Reyy).
- `standings`: 9 rows (NAVI 9-2 top at fetch).

## Schema
- `matches(match_detail_id PK, schedule_id, team_a, team_b, score_a/b, date, iso_date, iso_datetime, status, winner, vod_url, match_detail_url, liq_mvp)`
- `schedule_all(schedule_id PK, team_a/b, score_a/b, date, iso_date, iso_datetime, status, winner, vod_url, match_detail_id, match_detail_url)` — full 80-fixture list.
- `games(match_detail_id, game_no PK, team_a/b, team_a/b_kills, winner, duration_str, duration_sec, team_a/b_side, vod_url)`
- `game_players(match_detail_id, game_no, team, player, lane, hero, kills/deaths/assists, kda, gold, gold_per_min (=gold/(sec/60)), hero_damage, damage_taken, tower_damage, emblem, items_json, talents_json)`
- `game_bans(match_detail_id, game_no, side[A/B], hero)`
- `player_season_stats(player PK, team, team_slug, lane, total_games/kills/deaths/assists, avg_*, avg_kda, kill_participation)`
- `standings(rank PK, team_name/slug, match_point, match_win/lose, game_win/lose, net_game_win)`

## Gaps (source limits, not ETL bugs)
- Per-game team objectives (Lord/Turtle/Tower counts) are **not** in mlbbhub `/match` API — only per-player `tower_damage` + season-total Lord/Turtle/Tower on `id-mpl.com/statistics` (see `MPL_ID_S18_Statistics.md:26-36`). Stored what exists.
- `gold_per_min` is derived (total gold / minutes); native per-minute series not provided.
- `lane` is NULL in per-game rows (source leaves it null; use `player_season_stats.lane` for primary role).
- 2 live games (AE 1-2 NAVI Oct 3, GEEK 1-1 DEWA) have scores in `schedule_all` but no per-game detail yet; re-run `build_s18_db.py` after completion.

## Example queries
```sql
-- all games for a player
SELECT * FROM game_players WHERE player='Nnael' ORDER BY match_detail_id, game_no;
-- series with MVP + VOD
SELECT match_detail_id, team_a, team_b, score_a, score_b, liq_mvp, vod_url FROM matches;
-- top gold/min (min 15 min games to avoid short-game inflation)
SELECT player, hero, gold, duration_str, gold_per_min FROM game_players JOIN games USING(match_detail_id,game_no)
WHERE duration_sec >= 900 ORDER BY gold_per_min DESC LIMIT 10;
```
