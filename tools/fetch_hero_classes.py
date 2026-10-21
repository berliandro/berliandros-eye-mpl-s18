"""Build data/global/hero_classes.json from Liquipedia hero pages.

Why this exists: the API publishes no role, lane or damage-type metadata, and
hand-transcribing 133 heroes is error-prone. Liquipedia's `Infobox hero` carries
primary role, primary lane and specialties. Damage type has no infobox field, so
it is derived from counts of "Physical Damage" / "Magic Damage" in the ability
text and labelled `derived:ability_text` — never presented as official.

Empirical lane shares are computed from game_picks so the file can be audited
against actual play.

Usage:
  python tools/fetch_hero_classes.py [--season s18] [--check-only]
"""
import argparse
import gzip
import json
import re
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from season import ROOT, resolve

API = "https://liquipedia.net/mobilelegends/api.php"
UA = {"User-Agent": "MPL-S18-research/1.0 (local ETL metadata)", "Accept-Encoding": "gzip"}
# DB spelling -> Liquipedia page title, only where the source differs.
PAGE_OVERRIDES = {"Yi Sun-Shin": "Yi Sun-shin"}
OUT = ROOT / "data" / "global" / "hero_classes.json"


def fetch_batch(titles):
    q = urllib.parse.urlencode({
        "action": "query", "prop": "revisions", "rvslots": "main", "rvprop": "content",
        "format": "json", "redirects": "1", "titles": "|".join(titles),
    })
    req = urllib.request.Request(f"{API}?{q}", headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        raw = r.read()
        if r.headers.get("Content-Encoding") == "gzip" or raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
    return json.loads(raw.decode("utf-8"))


def infobox(wt):
    m = re.search(r"\{\{Infobox hero(.*?)\n\}\}", wt or "", re.S)
    return m.group(1) if m else (wt or "")


def field(box, name):
    m = re.search(r"^\|\s*" + re.escape(name) + r"\s*=\s*([^\n]*)", box, re.M)
    return m.group(1).strip() if m else ""


def norm_lane(value):
    key = re.sub(r"[^a-z]", "", (value or "").lower())
    for prefix, lane in (("exp", "EXP"), ("jungle", "JUNGLE"), ("mid", "MID"),
                         ("gold", "GOLD"), ("roam", "ROAM")):
        if key == prefix or key == prefix + "lane":
            return lane
    return (value or "").strip().upper()


def classify_damage(wt):
    phys = len(re.findall(r"physical\s+(?:damage|dmg)", wt or "", re.I))
    mag = len(re.findall(r"magic\s+(?:damage|dmg)", wt or "", re.I))
    if phys == 0 and mag == 0:
        kind = "unknown"
    elif mag >= 2 * phys:
        kind = "magic"
    elif phys >= 2 * mag:
        kind = "physical"
    else:
        kind = "mixed"
    return kind, {"physical": phys, "magic": mag}


def fetch_all(heroes):
    pages = {}
    title_to_hero = {PAGE_OVERRIDES.get(h, h): h for h in heroes}
    titles = list(title_to_hero)
    for i in range(0, len(titles), 50):
        batch = titles[i:i + 50]
        print(f"fetch heroes {i + 1}-{i + len(batch)}/{len(titles)}")
        data = fetch_batch(batch)
        for page in (data.get("query", {}).get("pages") or {}).values():
            if "missing" in page or not page.get("revisions"):
                continue
            wt = page["revisions"][0]["slots"]["main"]["*"]
            title = page["title"]
            hero = title_to_hero.get(title)
            if hero is None:
                hero = next((h for t, h in title_to_hero.items() if t.lower() == title.lower()), None)
            if hero:
                pages[hero] = wt
        if i + 50 < len(titles):
            time.sleep(1.0)
    return pages


def main():
    ap = argparse.ArgumentParser(description="Build hero role/lane metadata from Liquipedia.")
    ap.add_argument("--season", default="s18")
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    season = resolve(args.season)
    con = sqlite3.connect(season["database"])
    heroes = sorted({r[0] for r in con.execute("SELECT DISTINCT hero FROM game_players")} |
                    {r[0] for r in con.execute("SELECT hero FROM hero_stats")})
    picks = {}
    for hero, lane, n in con.execute(
            "SELECT hero, lane, COUNT(*) FROM game_picks GROUP BY hero, lane"):
        picks.setdefault(hero, Counter())[lane] = n
    con.close()

    pages = fetch_all(heroes)
    out = {}
    missing = []
    for hero in heroes:
        wt = pages.get(hero)
        if not wt:
            missing.append(hero)
            continue
        box = infobox(wt)
        lane = norm_lane(field(box, "lane"))
        role = field(box, "primaryrole")
        specialties = [x for x in (field(box, "specialty1"), field(box, "specialty2")) if x]
        damage, counts = classify_damage(wt)
        empirical = picks.get(hero, Counter())
        total = sum(empirical.values())
        out[hero] = {
            "primary_role": role or None,
            "primary_lane": lane or None,
            "primary_lane_source": "liquipedia" if lane else None,
            "specialties": specialties,
            "damage_type": damage,
            "damage_type_source": "derived:ability_text",
            "damage_counts": counts,
            "resource": field(box, "resourcebar") or None,
            "release_date": field(box, "releasedate") or None,
            "lanes_empirical": {
                ln: {"picks": n, "share": round(n / total, 4)}
                for ln, n in empirical.most_common()
            } if total else {},
        }

    payload = {
        "_note": ("Role/lane/specialties from Liquipedia Infobox hero; damage_type "
                  "is derived from ability-text mentions and is not official; "
                  "lanes_empirical comes from game_picks."),
        "schema_version": 1,
        "source": "https://liquipedia.net/mobilelegends/",
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "heroes": out,
    }

    no_role = [h for h, v in out.items() if not v["primary_role"]]
    no_lane = [h for h, v in out.items() if not v["primary_lane"]]
    print(f"heroes: {len(heroes)}  found: {len(out)}  missing: {missing}")
    print(f"no role: {no_role}")
    print(f"no lane: {no_lane}")
    print("damage types:", Counter(v["damage_type"] for v in out.values()))
    if args.check_only:
        print("check-only: not written")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
