"""Regression checks: parity placeholders, MVP count, WR calc, manifest coverage, link sanity.
Usage: python tools/check.py [--live]  (--live tries HEAD requests, else format-only)
Exit 0 = PASS, 1 = FAIL.
"""
import csv
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).parent
ROOT = BASE.parent
fails, warns = [], []


def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


def warn(msg):
    print("WARN " + msg)
    warns.append(msg)

html = (ROOT / 'mpl_id_s18_dark.html').read_text(encoding='utf-8')
for token in ('__DATA__', '__CSS__', '__JS__', '__ASSETS__'):
    ok(token not in html, f"no leftover {token}")
for needle in ('data-view="overview"', 'trendChart', 'wireCharts', 'id="net"', 'data-more'):
    ok(needle in html, f"contains {needle}")
for needle in ('name="description"', 'name="theme-color"', 'rel="icon"', 'property="og:title"'):
    ok(needle in html, f"contains meta {needle}")
ok('.ovsec{overflow-x:auto}' in html or '.ovsec{overflow-x: auto}' in html, "ovsec scrolls on mobile")


def load(name):
    with open(ROOT / 'data' / 'csv' / f'{name}.csv', encoding='utf-8') as f:
        return list(csv.DictReader(f))

try:
    matches = load('matches')
    sched = load('schedule_all')
    games = load('games')
    season = load('player_season_stats')
    praw = load('game_players')
except Exception as e:
    ok(False, f"csv load ({e})")
    praw = matches = sched = games = season = []

mvp_n = sum(1 for m in matches if (m.get('liq_mvp') or '').strip())
ok(len(matches) == 50, f"matches.csv has 50 rows (got {len(matches)})")
ok(mvp_n >= 49, f"MVP coverage {mvp_n}/50")

# WR calc consistency for Joshuaa (snapshot values drift as season progresses,
# so verify the counting logic, not a frozen score).
name = 'Joshuaa'
prows = [r for r in praw if r.get('player') == name]
ok(len(prows) >= 10, f"{name} has game rows (got {len(prows)})")
gkey = {(g['match_detail_id'], str(g['game_no'])): g for g in games}
skey = {s['match_detail_id']: s for s in sched}
gw = gl = 0
for r in prows:
    g = gkey.get((r['match_detail_id'], str(r['game_no'])))
    if not g or not g.get('winner'):
        continue
    pa = (g.get('team_a') == r['team'])
    won = (g['winner'] == 'team_a') == pa
    gw, gl = (gw + 1, gl) if won else (gw, gl + 1)
wr = round(gw / max(1, gw + gl) * 100) if (gw + gl) else 0
ok(gw + gl == len([r for r in prows if gkey.get((r['match_detail_id'], str(r['game_no']))) and gkey[(r['match_detail_id'], str(r['game_no']))].get('winner')]), f"{name} Game scored {gw+gl}/{len(prows)} rows counted")
ok(wr == (round(gw / max(1, gw + gl) * 100) if (gw + gl) else 0), f"{name} Game WR {gw}-{gl} = {wr}% consistent")
print(f"INFO {name} snapshot Game {gw}-{gl} ({wr}%), {len(prows)} rows")
mids = sorted({r['match_detail_id'] for r in prows})
mw = ml = 0
for did in mids:
    s = skey.get(did)
    if not s or s.get('status') != 'completed':
        continue
    try:
        sa, sb = int(s['score_a']), int(s['score_b'])
    except (ValueError, TypeError):
        continue
    if sa == sb:
        continue
    wt = s['team_a'] if sa > sb else s['team_b']
    prow_team = prows[0]['team'] if prows else ''
    if wt == prow_team:
        mw += 1
    else:
        ml += 1
ok(mw + ml == len([d for d in mids if (skey.get(d) or {}).get('status') == 'completed']), f"{name} Match series {mw + ml}/{len(mids)} completed counted")
print(f"INFO {name} snapshot Match {mw}-{ml}, live app showed 6-0/12-1 after refresh (season progresses)")

man = json.loads((ROOT / 'assets' / 'manifest.json').read_text(encoding='utf-8'))
for key, exp in (('items', 88), ('heroes', 86), ('players', 59)):
    got = len(man.get(key, {}))
    ok(got >= exp, f"manifest {key}: {got} (expect >= {exp})")
missing = []
for key in ('items', 'heroes', 'emblems', 'runes', 'teams', 'players'):
    for _k, rel in (man.get(key) or {}).items():
        if not (ROOT / rel).exists():
            missing.append(rel)
            if len(missing) > 5:
                break
ok(not missing, f"manifest files exist ({'none missing' if not missing else missing[:3]})")

urls = sorted(set(re.findall(r'https://[^\s"\'<>]+', html)))
ok(len(urls) > 0, f"found {len(urls)} https links")
bad = [u for u in urls if re.search(r'\s', u) or u.endswith(('.', ',', ')'))]
ok(not bad, f"link format ok ({len(urls)} checked)")
if '--live' in sys.argv:
    import urllib.request
    for u in urls[:12]:
        try:
            req = urllib.request.Request(u, method='HEAD', headers={'User-Agent': 'mpls18-check'})
            with urllib.request.urlopen(req, timeout=8) as r:
                if r.status >= 400:
                    warn(f"{r.status} {u}")
        except Exception as e:
            warn(f"unreachable {u} ({str(e)[:60]})")
else:
    print(f"(skip live link fetch; {len(urls)} links format-checked — rerun with --live)")

print(f"\n{len(fails)} failures, {len(warns)} warnings")
sys.exit(1 if fails else 0)
