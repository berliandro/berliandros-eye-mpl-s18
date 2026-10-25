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
    rc = subprocess.call([sys.executable, str(ROOT / "tools" / "build_s18_db.py")])
    if rc != 0:
        return rc
    # The API has no picks, per-game lanes or map mode; Liquipedia fills them.
    # Keeping this in the pipeline means a rebuild is never half-enriched.
    print(f"enrich drafts/lanes/maps for {season['id']}")
    return subprocess.call([sys.executable, str(ROOT / "tools" / "enrich_drafts.py"),
                            "--season", season["id"]])


if __name__ == "__main__":
    raise SystemExit(main())
