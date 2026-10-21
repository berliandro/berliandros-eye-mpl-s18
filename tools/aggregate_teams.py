"""Rebuild team-level aggregates from player rows and export their CSVs.

The ETL computes these at build time; this refreshes an already-built database
without a network rebuild, using the same schema and SQL.

Usage: python tools/aggregate_teams.py [--season s18] [--check-only]
"""
import argparse
import csv
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_s18_db import SCHEMA, rebuild_team_aggregates
from season import resolve

TABLES = ("team_games", "team_season_stats")


def export(con, csv_dir, tables):
    csv_dir.mkdir(parents=True, exist_ok=True)
    for tbl in tables:
        cur = con.execute(f"SELECT * FROM {tbl}")
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        with open(csv_dir / f"{tbl}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(cols)
            w.writerows(rows)
        print(f"csv {tbl}: {len(rows)} rows")


def main():
    ap = argparse.ArgumentParser(description="Rebuild team aggregates.")
    ap.add_argument("--season", default="s18")
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()
    season = resolve(args.season)
    con = sqlite3.connect(season["database"])
    # These tables are derived; recreate them so a schema change cannot leave
    # an old column layout behind.
    con.executescript("DROP TABLE IF EXISTS team_games; DROP TABLE IF EXISTS team_season_stats;")
    con.executescript(SCHEMA)
    if args.check_only:
        for t in TABLES:
            print(f"{t}: {con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]} rows")
        con.close()
        return 0
    rebuild_team_aggregates(con)
    export(con, season["csvDir"], TABLES)
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
