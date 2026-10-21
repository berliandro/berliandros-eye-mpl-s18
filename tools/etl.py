"""Season-aware ETL entry point.

Usage: python tools/etl.py [--season s18]

Resolves the season through data/registry.json and delegates to the ETL.
Network access is required. A failed build leaves the last known-good database
untouched (the ETL publishes atomically).
"""
import argparse
import subprocess
import sys

from season import ROOT, ids, resolve


def main():
    ap = argparse.ArgumentParser(description="Rebuild a season's database.")
    ap.add_argument("--season", default=None, choices=ids(),
                    help="season id (default: registry default)")
    args = ap.parse_args()
    season = resolve(args.season)
    print(f"etl {season['id']} ({season['displayName']})")
    return subprocess.call([sys.executable, str(ROOT / "tools" / "build_s18_db.py")])


if __name__ == "__main__":
    raise SystemExit(main())
