# Database inventory

Snapshot: `mpl-s18-db-20c5ea2c51f3`

- Path: `data/mpl_id_s18.db`
- SHA-256: `20c5ea2c51f30d1a24cd2ce6927f0d182b47f951ebd8209f1aaef429941cf2ef`
- Bytes: **5,234,688**
- Inspected: 2026-11-02T07:15:54+00:00

This inventory generator opened the database read-only (`mode=ro`). Any data migration is a separate explicit operation.

## Coverage that matters for coaching

| Field/table | Present |
|---|---:|
| Completed regular series (`schedule_all`) | 72 |
| Games | 174 |
| Player-game rows | 1,740 |
| Pick rows / ban rows | 1,740 / 1,738 |
| Team-game rows | 348 |
| Standings rows | 9 |
| Games with map mode | 153/174 |
| Games with both recorded sides | 174/174 |
| Games with per-game VOD | 173/174 |
| Series with broadcast VOD | 72/72 |
| Series with Liquipedia series MVP | 72/72 |
| Distinct players / heroes | 61 / 93 |

## Lineage and caveats

- **Source-reported:** schedule results, per-game winner/duration/sides/map mode, player scoreboard stats, standings, Liquipedia series MVP.
- **Deterministic derived:** `team_games` and `team_season_stats`; picks/bans are enriched joins from Liquipedia, not API fields.
- **Heuristic/app-derived:** dashboard game MVP and all win-probability/ratings metrics. Do not present them as official.
- **Unavailable:** per-game objective counts (Lord/Turtle/Tower), gold/damage timelines, exact pick order, communications, vision, intent, official damage-type split.

### `matches.winner` orientation

No row in the current snapshot has a `matches.winner` value that conflicts with its own `score_a/score_b` and `team_a/team_b` order.
`matches.winner` is interpreted in `matches` row order; `schedule_all.winner` is interpreted in schedule row order. Map the named teams before comparing side tokens across tables.

### Recommended joins

- Series: `schedule_all.match_detail_id` → `matches` → `games` / `team_games` / `game_players` / `game_picks` / `game_bans`.
- Game: `(match_detail_id, game_no)` is the composite key for games and derived rows.
- Player identity: `game_picks.player` and `game_players.player` use the app/Liquipedia spelling. Broadcast overlays can use different names; do not join broadcast names to database handles without evidence.
- Result: `matches.winner` is relative to `matches.team_a/team_b`; `schedule_all.winner` is relative to schedule row order. Map the named teams before comparing side tokens.

## Query catalog

Reproducible read-only queries used by the pilot are in `analysis/evidence/query-catalog.json`. Each ledger database reference embeds the query ID, SQL, parameters, snapshot SHA-256 and returned rows. The validator re-executes each query and rejects a non-reproducible result.

## Source-to-series mapping

All completed regular-season series have schedule-derived broadcast-date/VOD candidates in the source manifest. Candidates are not verified until `tools/resolve_and_align_sources.py` confirms official channel/title metadata and one-to-one timed-caption alignment. Exact series/game offsets remain separate work.
