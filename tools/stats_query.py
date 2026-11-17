#!/usr/bin/env python3
"""Read-only statistics bridge for the MPL S18 canonical database.

Every result carries the query id, SQL, parameters, snapshot id/hash, field list,
and provenance from ``analysis/evidence/query-catalog.json``.  The bridge never
writes to the database and never accepts arbitrary SQL from a caller.

Examples:
    python tools/stats_query.py --match 1037 --stat result
    python tools/stats_query.py --player MORENOOO --stat season
    python tools/stats_query.py --team "BIGETRON BY VIT" --stat season
    python tools/stats_query.py --hero LING --stat season
    python tools/stats_query.py --match 1037 --game 1 --stat players
    python tools/stats_query.py --query Q-MATCH-RESULT --params "{\"match_detail_id\":\"1037\"}"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
# The semantic/coaching layer analyzes the frozen regular-season snapshot
# (72 series, 174 games). The app database carries the completed season
# (80 series, 215 games); cite the right snapshot when quoting a query.
DEFAULT_DB = REPO / "analysis" / "snapshots" / "mpl_id_s18_regular.db"
DEFAULT_CATALOG = REPO / "analysis" / "evidence" / "query-catalog.json"


class StatsQueryError(RuntimeError):
    """Raised when a query cannot be executed safely."""


class SnapshotMismatch(StatsQueryError):
    """Raised when the database does not match the query catalog snapshot."""


@dataclass(frozen=True)
class QueryResult:
    query_id: str
    description: str
    sql: str
    params: dict[str, Any]
    fields: list[str]
    provenance: str
    snapshot_id: str
    snapshot_sha256: str
    snapshot_verified: bool
    rows: list[dict[str, Any]]

    @property
    def row_count(self) -> int:
        return len(self.rows)

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_id": self.query_id,
            "description": self.description,
            "sql": self.sql,
            "params": self.params,
            "fields": self.fields,
            "provenance": self.provenance,
            "snapshot_id": self.snapshot_id,
            "snapshot_sha256": self.snapshot_sha256,
            "snapshot_verified": self.snapshot_verified,
            "row_count": self.row_count,
            "rows": self.rows,
        }


def load_catalog(catalog_path: Path = DEFAULT_CATALOG) -> dict[str, Any]:
    try:
        return json.loads(catalog_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise StatsQueryError(f"query catalog not found: {catalog_path}") from exc
    except json.JSONDecodeError as exc:
        raise StatsQueryError(f"query catalog is not valid JSON: {exc}") from exc


def _connect_readonly(db_path: Path) -> sqlite3.Connection:
    if not db_path.is_file():
        raise StatsQueryError(f"database not found: {db_path}")
    uri = f"{db_path.resolve().as_uri()}?mode=ro"
    try:
        con = sqlite3.connect(uri, uri=True)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA query_only = ON")
        return con
    except sqlite3.Error as exc:
        raise StatsQueryError(f"cannot open database read-only: {exc}") from exc


def _database_sha256(db_path: Path) -> str:
    return hashlib.sha256(db_path.read_bytes()).hexdigest()


def run_query(
    query_id: str,
    params: dict[str, Any] | None = None,
    *,
    db_path: Path = DEFAULT_DB,
    catalog_path: Path = DEFAULT_CATALOG,
    verify_snapshot: bool = True,
) -> QueryResult:
    """Run one whitelisted catalog query and return rows plus provenance."""
    catalog = load_catalog(catalog_path)
    queries = catalog.get("queries", {})
    query = queries.get(query_id)
    if not query:
        raise StatsQueryError(f"unknown query id: {query_id}")

    params = dict(params or {})
    snapshot_sha = str(catalog.get("snapshot_sha256", ""))
    actual_sha = _database_sha256(db_path)
    verified = actual_sha == snapshot_sha
    if verify_snapshot and not verified:
        raise SnapshotMismatch(
            "database snapshot mismatch: "
            f"catalog={snapshot_sha or 'missing'} actual={actual_sha}"
        )

    con = _connect_readonly(db_path)
    try:
        cursor = con.execute(query["sql"], params)
        rows = [dict(zip(query["fields"], row)) for row in cursor.fetchall()]
    except sqlite3.Error as exc:
        raise StatsQueryError(f"{query_id} failed: {exc}") from exc
    finally:
        con.close()

    return QueryResult(
        query_id=query_id,
        description=str(query.get("description", "")),
        sql=str(query["sql"]),
        params=params,
        fields=list(query["fields"]),
        provenance=str(query.get("provenance", "")),
        snapshot_id=str(catalog.get("snapshot_id", "")),
        snapshot_sha256=snapshot_sha,
        snapshot_verified=verified,
        rows=rows,
    )


def _filter_rows(
    result: QueryResult,
    predicate: Callable[[dict[str, Any]], bool],
) -> QueryResult:
    rows = [row for row in result.rows if predicate(row)]
    return replace(result, rows=rows, provenance=result.provenance + " (filtered in memory)")


def match_result(match_id: str | int, **kwargs: Any) -> QueryResult:
    return run_query("Q-MATCH-RESULT", {"match_detail_id": str(match_id)}, **kwargs)


def match_detail(match_id: str | int, **kwargs: Any) -> QueryResult:
    return run_query("Q-MATCH-DETAIL", {"match_detail_id": str(match_id)}, **kwargs)


def games(match_id: str | int, **kwargs: Any) -> QueryResult:
    return run_query("Q-GAMES", {"match_detail_id": str(match_id)}, **kwargs)


def team_games(match_id: str | int, **kwargs: Any) -> QueryResult:
    return run_query("Q-TEAM-GAMES", {"match_detail_id": str(match_id)}, **kwargs)


def player_season(player: str, **kwargs: Any) -> QueryResult:
    return run_query("Q-PLAYER-SEASON", {"player": player.upper()}, **kwargs)


def player_games(player: str, hero: str | None = None, **kwargs: Any) -> QueryResult:
    result = run_query("Q-PLAYER-GAMES", {"player": player.upper()}, **kwargs)
    if hero:
        result = _filter_rows(result, lambda row: str(row.get("hero", "")).upper() == hero.upper())
    return result


def player_picks(player: str, hero: str | None = None, **kwargs: Any) -> QueryResult:
    result = run_query("Q-PLAYER-PICKS", {"player": player.upper()}, **kwargs)
    if hero:
        result = _filter_rows(result, lambda row: str(row.get("hero", "")).upper() == hero.upper())
    return result


def player_mvp_series(player: str, **kwargs: Any) -> QueryResult:
    return run_query("Q-PLAYER-MVP-SERIES", {"player": player.upper()}, **kwargs)


def team_season(team: str, **kwargs: Any) -> QueryResult:
    return run_query("Q-TEAM-SEASON", {"team": team}, **kwargs)


def hero_season(hero: str, **kwargs: Any) -> QueryResult:
    return run_query("Q-HERO-SEASON", {"hero": hero}, **kwargs)


def game_players(match_id: str | int, game_no: str | int, **kwargs: Any) -> QueryResult:
    return run_query(
        "Q-GAME-PLAYERS",
        {"match_detail_id": str(match_id), "game_no": str(game_no)},
        **kwargs,
    )


def schedule_all(**kwargs: Any) -> QueryResult:
    """All 72 completed series in schedule orientation."""
    return run_query("Q-SCHEDULE", {}, **kwargs)


def all_games(**kwargs: Any) -> QueryResult:
    """Every game with winner, duration, sides, map mode and VOD."""
    return run_query("Q-ALL-GAMES", {}, **kwargs)


def all_team_games(**kwargs: Any) -> QueryResult:
    """Every team-game aggregate in the season."""
    return run_query("Q-ALL-TEAM-GAMES", {}, **kwargs)


def all_player_games(**kwargs: Any) -> QueryResult:
    """Compact per-player per-game scoreboard for the whole season."""
    return run_query("Q-ALL-PLAYER-GAMES", {}, **kwargs)


def match_player_lines(match_id: str | int, **kwargs: Any) -> QueryResult:
    """Compact scoreboard lines for one series, without item/talent URLs."""
    return run_query("Q-MATCH-PLAYER-LINES", {"match_detail_id": str(match_id)}, **kwargs)


def all_picks(**kwargs: Any) -> QueryResult:
    """Every draft pick in the season."""
    return run_query("Q-ALL-PICKS", {}, **kwargs)


def all_bans(**kwargs: Any) -> QueryResult:
    """Every draft ban in the season."""
    return run_query("Q-ALL-BANS", {}, **kwargs)


def all_team_season(**kwargs: Any) -> QueryResult:
    """Season aggregate for every team."""
    return run_query("Q-ALL-TEAM-SEASON", {}, **kwargs)


def all_player_season(**kwargs: Any) -> QueryResult:
    """Season aggregate for every player."""
    return run_query("Q-ALL-PLAYER-SEASON", {}, **kwargs)


def all_hero_stats(**kwargs: Any) -> QueryResult:
    """Season pick/ban/win aggregate for every hero."""
    return run_query("Q-ALL-HERO-STATS", {}, **kwargs)


def all_match_details(**kwargs: Any) -> QueryResult:
    """Series MVP for every completed match."""
    return run_query("Q-ALL-MATCH-DETAIL", {}, **kwargs)


def get_player_stat(player: str, stat: str = "season", hero: str | None = None) -> QueryResult:
    """Facade for the player questions exposed by the catalog."""
    key = stat.lower()
    if key in {"season", "summary"}:
        if hero:
            raise StatsQueryError("hero filtering is not available for a season aggregate")
        return player_season(player)
    if key in {"games", "game"}:
        return player_games(player, hero=hero)
    if key in {"picks", "draft"}:
        return player_picks(player, hero=hero)
    if key in {"mvp", "mvps"}:
        return player_mvp_series(player)
    raise StatsQueryError(f"unknown player stat: {stat}")


def get_team_stat(team: str, stat: str = "season") -> QueryResult:
    if stat.lower() not in {"season", "summary"}:
        raise StatsQueryError(f"unknown team stat: {stat}")
    return team_season(team)


def get_hero_stat(hero: str, stat: str = "season") -> QueryResult:
    if stat.lower() not in {"season", "summary"}:
        raise StatsQueryError(f"unknown hero stat: {stat}")
    return hero_season(hero)


def get_match_stat(match_id: str | int, stat: str = "result") -> QueryResult:
    key = stat.lower()
    if key in {"result", "schedule"}:
        return match_result(match_id)
    if key in {"detail", "match"}:
        return match_detail(match_id)
    if key in {"games", "game"}:
        return games(match_id)
    if key in {"teams", "team_games"}:
        return team_games(match_id)
    raise StatsQueryError(f"unknown match stat: {stat}")


def get_game_stat(match_id: str | int, game_no: str | int, stat: str = "players") -> QueryResult:
    if stat.lower() not in {"players", "items", "scoreboard"}:
        raise StatsQueryError(f"unknown game stat: {stat}")
    return game_players(match_id, game_no)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--query", help="catalog query id, e.g. Q-MATCH-RESULT")
    parser.add_argument("--params", default="{}", help="JSON object for --query")
    parser.add_argument("--player")
    parser.add_argument("--team")
    parser.add_argument("--hero")
    parser.add_argument("--match", dest="match_id")
    parser.add_argument("--game", dest="game_no")
    parser.add_argument("--stat", help="question name: season, games, picks, mvp, result, detail, teams, players")
    parser.add_argument("--no-snapshot-check", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = _build_parser().parse_args(argv)
    kwargs = {"verify_snapshot": not args.no_snapshot_check}

    try:
        if args.query:
            result = run_query(args.query, json.loads(args.params), **kwargs)
        elif args.player:
            result = get_player_stat(args.player, args.stat or "season", hero=args.hero)
        elif args.team:
            result = get_team_stat(args.team, args.stat or "season")
        elif args.hero:
            result = get_hero_stat(args.hero, args.stat or "season")
        elif args.match_id and args.game_no:
            result = get_game_stat(args.match_id, args.game_no, args.stat or "players")
        elif args.match_id:
            result = get_match_stat(args.match_id, args.stat or "result")
        else:
            _build_parser().error("provide --query, --player, --team, --hero, or --match")
            return 2
    except (StatsQueryError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
