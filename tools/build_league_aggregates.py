#!/usr/bin/env python3
"""Compute reproducible league aggregates from the canonical database.

Outputs a machine-readable evidence file and a data appendix. All numbers come
from tools/stats_query.py with the catalog snapshot hash.

Usage:
    python tools/build_league_aggregates.py
"""

from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import stats_query as sq

REPO = Path(__file__).resolve().parent.parent
OUT_JSON = REPO / "analysis" / "evidence" / "league-aggregates.json"
OUT_MD = REPO / "analysis" / "reports" / "league-data.md"


def pct(value: float | None, digits: int = 1) -> str:
    return "—" if value is None else f"{value * 100:.{digits}f}%"


def ratio(wins: int, games: int) -> float | None:
    return wins / games if games else None


def main() -> int:
    schedule = sq.schedule_all()
    games = sq.all_games()
    team_games = sq.all_team_games()
    players = sq.all_player_games()
    picks = sq.all_picks()
    bans = sq.all_bans()
    team_season = sq.all_team_season()
    player_season = sq.all_player_season()
    hero_stats = sq.all_hero_stats()

    schedule_rows = schedule.rows
    game_rows = games.rows
    team_game_rows = team_games.rows
    player_rows = players.rows
    pick_rows = picks.rows
    ban_rows = bans.rows

    # Game lookup: match/game -> game row and winner team name.
    game_by_key: dict[tuple[str, int], dict[str, Any]] = {}
    winner_by_key: dict[tuple[str, int], str] = {}
    for game in game_rows:
        key = (str(game["match_detail_id"]), int(game["game_no"]))
        game_by_key[key] = game
        winner_by_key[key] = str(game["team_a"] if game["winner"] == "team_a" else game["team_b"])

    # Team-game lookup for opponent gold comparison.
    team_game_by_key: dict[tuple[str, int, str], dict[str, Any]] = {
        (str(row["match_detail_id"]), int(row["game_no"]), str(row["team"])): row for row in team_game_rows
    }

    series_by_team: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in schedule_rows:
        for team, opponent in ((row["team_a"], row["team_b"]), (row["team_b"], row["team_a"])):
            series_by_team[str(team)].append({
                "match_detail_id": str(row["match_detail_id"]),
                "opponent": str(opponent),
                "won": str(row["winner"]) == "team_a" if team == row["team_a"] else str(row["winner"]) == "team_b",
                "score_for": row["score_a"] if team == row["team_a"] else row["score_b"],
                "score_against": row["score_b"] if team == row["team_a"] else row["score_a"],
            })

    team_games_by_team: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in team_game_rows:
        team_games_by_team[str(row["team"])].append(row)

    team_blocks: dict[str, Any] = {}
    for season_row in team_season.rows:
        team = str(season_row["team"])
        rows = team_games_by_team.get(team, [])
        side = {"blue": {"games": 0, "wins": 0}, "red": {"games": 0, "wins": 0}}
        maps: dict[str, dict[str, int]] = defaultdict(lambda: {"games": 0, "wins": 0})
        close = {"wins": 0, "losses": 0}
        blowout = {"wins": 0, "losses": 0}
        gold_diffs: list[int] = []
        for row in rows:
            key = (str(row["match_detail_id"]), int(row["game_no"]))
            game = game_by_key.get(key, {})
            team_side = game.get("team_a_side") if str(game.get("team_a")) == team else game.get("team_b_side")
            won = int(row.get("win") or 0) == 1
            if team_side in side:
                side[team_side]["games"] += 1
                side[team_side]["wins"] += int(won)
            map_mode = game.get("map_mode")
            if map_mode:
                maps[str(map_mode)]["games"] += 1
                maps[str(map_mode)]["wins"] += int(won)
            opponent = team_game_by_key.get((key[0], key[1], str(row["opponent"])))
            if opponent:
                diff = int(row.get("gold") or 0) - int(opponent.get("gold") or 0)
                gold_diffs.append(diff)
                if abs(diff) < 3000:
                    close["wins" if won else "losses"] += 1
                if abs(diff) >= 10000:
                    blowout["wins" if won else "losses"] += 1
        series_rows = series_by_team.get(team, [])
        series_wins = sum(1 for row in series_rows if row["won"])
        sweep_wins = sum(1 for row in series_rows if row["won"] and row["score_for"] == 2 and row["score_against"] == 0)
        sweep_losses = sum(1 for row in series_rows if not row["won"] and row["score_for"] == 0)
        deciders = sum(1 for row in series_rows if row["score_for"] == 2 and row["score_against"] == 1 or row["score_for"] == 1 and row["score_against"] == 2)
        team_blocks[team] = {
            "team_name": season_row.get("team_name"),
            "season": season_row,
            "series": {
                "wins": series_wins,
                "losses": len(series_rows) - series_wins,
                "sweep_wins": sweep_wins,
                "sweep_losses": sweep_losses,
                "deciders": deciders,
            },
            "side": side,
            "maps": {name: {**value, "win_rate": ratio(value["wins"], value["games"])} for name, value in sorted(maps.items())},
            "close_games": close,
            "blowout_games": blowout,
            "avg_gold_diff": round(statistics.mean(gold_diffs), 1) if gold_diffs else None,
            "duration_seconds": {
                "min": min((int(row["duration_sec"]) for row in rows), default=None),
                "max": max((int(row["duration_sec"]) for row in rows), default=None),
                "avg": round(statistics.mean(int(row["duration_sec"]) for row in rows), 1) if rows else None,
                "median": round(statistics.median(int(row["duration_sec"]) for row in rows), 1) if rows else None,
            },
        }

    # Hero aggregates from actual picks/bans.
    hero_block: dict[str, Any] = {}
    for row in pick_rows:
        hero = str(row["hero"])
        block = hero_block.setdefault(hero, {"picks": 0, "wins": 0, "bans": 0, "teams": defaultdict(lambda: {"picks": 0, "wins": 0}), "players": Counter()})
        block["picks"] += 1
        block["players"][str(row["player"])] += 1
        team = str(row["team"])
        block["teams"][team]["picks"] += 1
        key = (str(row["match_detail_id"]), int(row["game_no"]))
        if winner_by_key.get(key) == team:
            block["wins"] += 1
            block["teams"][team]["wins"] += 1
    for row in ban_rows:
        hero = str(row["hero"])
        hero_block.setdefault(hero, {"picks": 0, "wins": 0, "bans": 0, "teams": defaultdict(lambda: {"picks": 0, "wins": 0}), "players": Counter()})["bans"] += 1
    hero_rows = []
    for hero, block in hero_block.items():
        picks_n = block["picks"]
        hero_rows.append({
            "hero": hero,
            "picks": picks_n,
            "wins": block["wins"],
            "losses": picks_n - block["wins"],
            "pick_rate": ratio(picks_n, len(game_rows)),
            "win_rate": ratio(block["wins"], picks_n),
            "bans": block["bans"],
            "contest_rate": ratio(picks_n + block["bans"], len(game_rows)),
            "teams": {team: {**value, "win_rate": ratio(value["wins"], value["picks"])} for team, value in sorted(block["teams"].items())},
            "top_players": [{"player": player, "picks": count} for player, count in block["players"].most_common(5)],
        })
    hero_rows.sort(key=lambda row: (-row["picks"], -row["bans"], row["hero"]))

    # Player aggregates from per-game rows.
    player_blocks: dict[str, Any] = {}
    for row in player_rows:
        player = str(row["player"])
        block = player_blocks.setdefault(player, {"team": str(row["team"]), "lane": str(row["lane"]), "games": 0, "kills": 0, "deaths": 0, "assists": 0, "gold": 0, "gold_per_min": [], "hero_damage": 0, "damage_taken": 0, "tower_damage": 0, "heroes": Counter(), "damage_shares": []})
        block["games"] += 1
        block["kills"] += int(row["kills"])
        block["deaths"] += int(row["deaths"])
        block["assists"] += int(row["assists"])
        block["gold"] += int(row["gold"])
        block["gold_per_min"].append(float(row["gold_per_min"]))
        block["hero_damage"] += int(row["hero_damage"])
        block["damage_taken"] += int(row["damage_taken"])
        block["tower_damage"] += int(row["tower_damage"])
        block["heroes"][str(row["hero"])] += 1
        team_row = team_game_by_key.get((str(row["match_detail_id"]), int(row["game_no"]), str(row["team"])))
        if team_row and int(team_row.get("hero_damage") or 0) > 0:
            block["damage_shares"].append(int(row["hero_damage"]) / int(team_row["hero_damage"]))
    player_blocks_out = {}
    for player, block in player_blocks.items():
        games_n = block["games"]
        player_blocks_out[player] = {
            "team": block["team"],
            "lane": block["lane"],
            "games": games_n,
            "kills": block["kills"],
            "deaths": block["deaths"],
            "assists": block["assists"],
            "kda": round((block["kills"] + block["assists"]) / max(block["deaths"], 1), 2),
            "avg_gold": round(block["gold"] / games_n, 1),
            "avg_gold_per_min": round(statistics.mean(block["gold_per_min"]), 1),
            "avg_hero_damage": round(block["hero_damage"] / games_n, 1),
            "avg_damage_taken": round(block["damage_taken"] / games_n, 1),
            "avg_tower_damage": round(block["tower_damage"] / games_n, 1),
            "avg_damage_share": round(statistics.mean(block["damage_shares"]), 4) if block["damage_shares"] else None,
            "top_heroes": [{"hero": hero, "games": count} for hero, count in block["heroes"].most_common(5)],
        }

    # League-level game stats.
    durations = [int(game["duration_sec"]) for game in game_rows]
    blue_games = sum(1 for game in game_rows if game.get("team_a_side") == "blue")
    blue_wins = sum(1 for game in game_rows if game.get("team_a_side") == "blue" and game["winner"] == "team_a") + sum(
        1 for game in game_rows if game.get("team_b_side") == "blue" and game["winner"] == "team_b"
    )
    map_block: dict[str, Any] = {}
    for game in game_rows:
        map_mode = game.get("map_mode")
        if not map_mode:
            continue
        block = map_block.setdefault(str(map_mode), {"games": 0, "blue_wins": 0, "durations": []})
        block["games"] += 1
        block["durations"].append(int(game["duration_sec"]))
        if (game.get("team_a_side") == "blue" and game["winner"] == "team_a") or (game.get("team_b_side") == "blue" and game["winner"] == "team_b"):
            block["blue_wins"] += 1
    map_out = {
        name: {
            "games": value["games"],
            "blue_wins": value["blue_wins"],
            "blue_win_rate": ratio(value["blue_wins"], value["games"]),
            "avg_duration_sec": round(statistics.mean(value["durations"]), 1),
        }
        for name, value in sorted(map_block.items())
    }

    series_length = Counter(len([g for g in game_rows if str(g["match_detail_id"]) == str(row["match_detail_id"])]) for row in schedule_rows)
    month_block: dict[str, Any] = defaultdict(lambda: {"series": 0, "games": 0})
    for row in schedule_rows:
        month = str(row["iso_date"])[:7]
        month_block[month]["series"] += 1
    for game in game_rows:
        month = next((str(row["iso_date"])[:7] for row in schedule_rows if str(row["match_detail_id"]) == str(game["match_detail_id"])), "?")
        month_block[month]["games"] += 1

    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "snapshot_id": schedule.snapshot_id,
        "snapshot_sha256": schedule.snapshot_sha256,
        "league": {
            "series": len(schedule_rows),
            "games": len(game_rows),
            "teams": len(team_season.rows),
            "players": len(player_season.rows),
            "heroes_in_stats": len(hero_stats.rows),
            "heroes_picked": sum(1 for row in hero_rows if row["picks"] > 0),
            "heroes_in_pool": len(hero_rows),
            "picks": len(pick_rows),
            "bans": len(ban_rows),
            "duration_sec": {
                "min": min(durations),
                "max": max(durations),
                "avg": round(statistics.mean(durations), 1),
                "median": round(statistics.median(durations), 1),
            },
            "blue_side": {"games": blue_games, "wins": blue_wins, "win_rate": ratio(blue_wins, blue_games)},
            "maps": map_out,
            "series_lengths": dict(sorted(series_length.items())),
            "months": dict(sorted(month_block.items())),
        },
        "teams": team_blocks,
        "heroes": hero_rows,
        "players": player_blocks_out,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Data appendix.
    lines = [
        "# League data appendix",
        "",
        f"Generated by `tools/build_league_aggregates.py` from snapshot `{schedule.snapshot_id}` (`{schedule.snapshot_sha256[:12]}…`). "
        "For interpretation and limits, read `analysis/reports/league-meta.md`.",
        "",
        "## League totals",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Series / games | {len(schedule_rows)} / {len(game_rows)} |",
        f"| Picks / bans | {len(pick_rows)} / {len(ban_rows)} |",
        f"| Average duration | {payload['league']['duration_sec']['avg']:.0f}s |",
        f"| Median duration | {payload['league']['duration_sec']['median']:.0f}s |",
        f"| Shortest / longest | {payload['league']['duration_sec']['min']}s / {payload['league']['duration_sec']['max']}s |",
        f"| Blue-side win rate | {pct(payload['league']['blue_side']['win_rate'])} ({blue_wins}/{blue_games}) |",
        f"| Series lengths | {', '.join(f'{k} games: {v}' for k, v in sorted(series_length.items()))} |",
        "",
        "## Team season table",
        "",
        "| Team | Series W-L | Game W-L | Sweeps won/lost | Deciders | Avg duration | Blue W-L | Red W-L | Close W-L | Blowout W-L |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for team, block in sorted(team_blocks.items(), key=lambda item: (-item[1]["series"]["wins"], item[0])):
        season = block["season"]
        blue = block["side"]["blue"]
        red = block["side"]["red"]
        lines.append(
            f"| {team} | {block['series']['wins']}-{block['series']['losses']} | {season['wins']}-{season['losses']} | "
            f"{block['series']['sweep_wins']}/{block['series']['sweep_losses']} | {block['series']['deciders']} | "
            f"{block['duration_seconds']['avg']:.0f}s | {blue['wins']}-{blue['games'] - blue['wins']} | "
            f"{red['wins']}-{red['games'] - red['wins']} | {block['close_games']['wins']}-{block['close_games']['losses']} | "
            f"{block['blowout_games']['wins']}-{block['blowout_games']['losses']} |"
        )

    lines += [
        "",
        "Close = final gold difference under 3,000; blowout = 10,000 or more.",
        "",
        "## Map and side splits",
        "",
        "| Map | Games | Blue win rate | Avg duration |",
        "|---|---:|---:|---:|",
    ]
    for name, block in map_out.items():
        lines.append(f"| {name} | {block['games']} | {pct(block['blue_win_rate'])} | {block['avg_duration_sec']:.0f}s |")

    lines += [
        "",
        "## Hero priority (top 30 by picks)",
        "",
        "| Hero | Picks | Win rate | Bans | Contest rate |",
        "|---|---:|---:|---:|---:|",
    ]
    for hero in hero_rows[:30]:
        lines.append(
            f"| {hero['hero']} | {hero['picks']} | {pct(hero['win_rate'])} | {hero['bans']} | {pct(hero['contest_rate'])} |"
        )

    lines += [
        "",
        "## Team hero pools (top 8 picks each)",
        "",
    ]
    for team, block in sorted(team_blocks.items()):
        team_heroes = [
            (hero["hero"], hero["teams"][team]["picks"], hero["teams"][team]["win_rate"])
            for hero in hero_rows if team in hero["teams"]
        ]
        team_heroes.sort(key=lambda item: (-item[1], item[0]))
        rendered = ", ".join(f"{name} ({picks}, {pct(win)})" for name, picks, win in team_heroes[:8])
        lines.append(f"- **{team}:** {rendered}")

    lines += [
        "",
        "## Player leaders",
        "",
        "### KDA (minimum 10 games)",
        "",
        "| Player | Team | Lane | Games | KDA | Avg gold/min | Damage share |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    ranked = sorted((block for block in player_blocks_out.items() if block[1]["games"] >= 10), key=lambda item: -item[1]["kda"])
    for player, block in ranked[:20]:
        lines.append(
            f"| {player} | {block['team']} | {block['lane']} | {block['games']} | {block['kda']} | "
            f"{block['avg_gold_per_min']:.0f} | {pct(block['avg_damage_share'], 1)} |"
        )

    lines += [
        "",
        "### Hero pools for selected players",
        "",
    ]
    for player, block in sorted(player_blocks_out.items()):
        if block["games"] < 20:
            continue
        heroes = ", ".join(f"{entry['hero']} ({entry['games']})" for entry in block["top_heroes"][:3])
        lines.append(f"- **{player}** ({block['team']}, {block['lane']}, {block['games']} games): {heroes}")

    lines += [
        "",
        "## Calendar split",
        "",
        "| Month | Series | Games |",
        "|---|---:|---:|",
    ]
    for month, block in sorted(month_block.items()):
        lines.append(f"| {month} | {block['series']} | {block['games']} |")

    lines += [
        "",
        "## Limits",
        "",
        "- No patch/version field exists, so calendar splits are not patch splits.",
        "- No objective counts, gold timelines, vision, communications, or intent are available.",
        "- Hero win rates are descriptive, not causal; draft context and player skill are confounded.",
        "- The database has 174 games; per-map and per-team samples are small.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload["league"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
