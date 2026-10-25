"""Season-aware build entry point.

Usage: python tools/build.py [--season s18]

Resolves the season through data/registry.json and delegates to the generator.
The wrapper exists so every build is invoked by season id; the generator can
become fully path-driven without changing callers or CI.
"""
import argparse
import subprocess
import sys

from season import ROOT, ids, resolve


def main():
    ap = argparse.ArgumentParser(description="Build a season's application.")
    ap.add_argument("--season", default=None, choices=ids(),
                    help="season id (default: registry default)")
    args = ap.parse_args()
    season = resolve(args.season)
    print(f"build {season['id']} ({season['displayName']})")
    return subprocess.call([sys.executable, str(ROOT / "tools" / "gen_dark.py")])


if __name__ == "__main__":
    raise SystemExit(main())
