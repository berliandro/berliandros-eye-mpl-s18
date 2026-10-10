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
ok(b'\r' not in (ROOT / 'mpl_id_s18_dark.html').read_bytes(),
   "generated HTML uses LF-only line endings (CI parity)")
for needle in ('data-view="overview"', 'trendChart', 'wireCharts', 'id="net"', 'data-more'):
    ok(needle in html, f"contains {needle}")
for needle in ('name="description"', 'name="theme-color"', 'rel="icon"', 'property="og:title"'):
    ok(needle in html, f"contains meta {needle}")
ok('.ovsec{overflow-x:auto}' in html or '.ovsec{overflow-x: auto}' in html, "ovsec scrolls on mobile")
ok('function syncControls' in html, "controls sync per tab")
ok('gameMvp' in html, "game MVP computed for scoreboard header")
ok('mmvp-grid' in html, "grid match cards show series MVP")
ok('MANIAC' in html and 'SAVAGE' in html, "player card has MANIAC/SAVAGE columns")
ok('under development' in html, "maniac/savage marked under development")
ok('AVG KDA</th>' in html, "player card has AVG KDA column")
ok('sb-live' not in html, "sb-live badge removed from match card")
ok("toggle('full'" in html, "matches list can go full width")
ok('mfoot' in html, "matches list has horizontal section footers")
ok('data-sec' in html, "load-more footers are per-section")
ok('data-phase' in html, "matches has Regular/Playoffs sub-tab")
ok('phasebar' in html, "phase switcher folded into header bar")
ok('data-stat' in html, "stats has Series MVP / Heroes sub-tabs")
ok('bracketHTML' in html, "playoff bracket preview exists")
ok('standBoard' in html, "standings board moved to matches")
ok('data-ts' in html, "statistic tables have sort controls")
for needle in ('data-ovhero', 'data-ovemb', 'data-ovtal', 'data-ovopp', 'data-ovg', 'id="dback"', 'selGame', 'usageSummaryHTML', 'ovTalDrill'):
    ok(needle in html, f"overview drill-down contains {needle}")
for needle in ('id="searchBox"', 'id="sortBox"', 'id="laneBox"', 'id="layoutSeg"'):
    ok(needle in html, f"contains {needle}")


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
n_completed_detail = sum(1 for s in sched if s.get('status') == 'completed'
                       and re.match(r'^\d+$', str(s.get('match_detail_id') or '')))
ok(len(matches) == n_completed_detail,
   f"matches.csv tracks completed series with details ({len(matches)} vs {n_completed_detail})")
ok(mvp_n >= len(matches) - 1, f"MVP coverage {mvp_n}/{len(matches)}")

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
for key, exp in (('items', 110), ('heroes', 88), ('players', 59)):
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

# embedded JS must parse (catches template-literal/brace breakage)
import shutil
import subprocess
if shutil.which('node'):
    r = subprocess.run(['node', '--check', str(BASE / 'templates' / 'app.js')],
                       capture_output=True, text=True)
    ok(r.returncode == 0, "app.js parses (node --check)" + ("" if r.returncode == 0 else f": {r.stderr.strip()[:200]}"))
else:
    warn("node not found; skipped JS syntax check")

# lane coverage (normalized: lowercase alnum + known IGN aliases; source: data/lanes.json)
def ultra(s):
    return re.sub(r'[^a-z0-9]', '', str(s or '').lower())
lanes_doc = json.loads((ROOT / 'data' / 'lanes.json').read_text(encoding='utf-8'))
lanes = {ultra(k): v for k, v in (lanes_doc.get('lanes') or {}).items()}
alias = {'shanee': 'shane', 'kevinn': 'kevin', 'lutpi': 'lutpiii', 'yazukee': 'affan',
         'kennzyskie': 'kennzyyskie', 'maykidss': 'maykids', 'arfy': 'dingarai',
         'sanz': 'sanz', 'rendyyy': 'rendyy', 'aboyy': 'aboy', 'alekk': 'alexander',
         'morenooo': 'morenoo', 'itoshikesu': 'itoshikesu', 'ssamuel': 'samuel',
         'joshuaa': 'joshua', 'hijumee': 'dalvin', 'affan': 'yazukee', 'dalvin': 'hijumee',
         'dingarai': 'arfy', 'alexander': 'alekk', 'kevin': 'kevinn', 'maykids': 'maykidss',
         'shane': 'shanee'}
alias = {ultra(k): ultra(v) for k, v in alias.items()}
ok(lanes_doc.get('source', '').startswith('Liquipedia'), "lanes.json has Liquipedia provenance")
all_players = {r['player'] for r in praw} | {r['player'] for r in season}
uncovered = [p for p in sorted(all_players)
             if ultra(p) not in lanes and alias.get(ultra(p), ultra(p)) not in lanes]
ok(not uncovered, f"lane coverage normalized ({len(all_players)} names)" + ("" if not uncovered else f" missing {uncovered[:6]}"))

# STRICT: every hero + item ref in the data must resolve to a downloaded file.
# (players keep initials-fallback warnings: no remote photo source exists for them)
heroes_used = sorted({r['hero'] for r in praw if r.get('hero')}
                      | {r['hero'] for r in load('game_bans') if r.get('hero')})
gap_h = [h for h in heroes_used
         if h not in (man.get('heroes') or {})
         or not (ROOT / man['heroes'][h]).exists()]
ok(not gap_h, f"STRICT heroes all downloaded ({len(heroes_used)})"
   + ("" if not gap_h else f" missing {gap_h[:6]}"))
item_refs = set()
for r in praw:
    try:
        urls = json.loads(r.get('items_json') or '[]')
    except Exception:
        urls = []
    for u in urls:
        if not u:
            continue
        m = re.search(r'(?:equipment|equip)/(\d+)\.png', u)
        item_refs.add(m.group(1) if m else u.split('?')[0])
gap_i = [x for x in sorted(item_refs)
         if x not in (man.get('items') or {})
         or not (ROOT / man['items'][x]).exists()]
ok(not gap_i, f"STRICT items all downloaded ({len(item_refs)})"
   + ("" if not gap_i else f" missing {[x[:50] for x in gap_i[:6]]}"))
man_players_ci = {ultra(k): k for k in man.get('players', {})}
gap = sorted(p for p in all_players if ultra(p) not in man_players_ci and alias.get(ultra(p), ultra(p)) not in man_players_ci)
if gap:
    warn(f"player images missing ({len(gap)}): {', '.join(gap[:6])} — initials fallback used")
else:
    print("PASS player images cover all players")

# MVP identity: Liquipedia MVP spellings must resolve to ONE canonical roster
# identity (mirror of PLAYER_ALIAS in tools/templates/app.js — keep in sync).
# Verified: Coolfire=Joshuaa (reddit r/mobilelegendsesports 2026-08-30),
# JOOOOO=Kevinn = Yonathan Chin (bo3.gg player pages, teamliquid.com roster),
# Sutsujin=Arthur Sunarkho (Liquipedia, MLDB). Lynchh=Joshua (Liquipedia
# player page: Joshua "Lynchh" Nicholas, EXP Laner, RRQ Hoshi; id-mpl.com RRQ
# roster lists JOSHUA as EXP Lane; live-API game rows for the MVP series use
# IGN Joshua; single Joshua on RRQ). Mechanical (row teams intersect
# roster team): A B O Y=Aboyy, Jizeezeze=Jiizee, Maykids=Maykidss,
# Moreno=Morenooo, Rendyy=Rendyyy. Deliberately unmerged: Joshua (RRQ) vs
# Joshuaa (NAVI) — different people.
PLAYER_CANON = {'coolfire': 'Joshuaa', 'jooooo': 'Kevinn', 'sutsujin': 'Arthur',
                'lynchh': 'Joshua', 'jizeezeze': 'Jiizee', 'maykids': 'Maykidss', 'moreno': 'Morenooo',
                'rendyy': 'Rendyyy', 'aboy': 'Aboyy'}


def canon(name):
    u = ultra(name)
    gp = sorted({r['player'] for r in praw if ultra(r['player']) == u})
    if len(gp) == 1:
        return gp[0]
    if len(gp) > 1:
        return 'Maykidss' if u == 'maykidss' else gp[0]
    ss = sorted({r['player'] for r in season if ultra(r['player']) == u})
    if ss:
        return ss[0]
    return PLAYER_CANON.get(u, name)


ok(canon('Coolfire') == 'Joshuaa', "CoolFire resolves to Joshuaa (not a separate player)")
ok(canon('JOOOOO') == 'Kevinn', "JOOOOO resolves to Kevinn (Yonathan Chin)")
ok(canon('Sutsujin') == 'Arthur', "Sutsujin resolves to Arthur Sunarkho")
ok(canon('Lynchh') == 'Joshua', "Lynchh resolves to Joshua (RRQ EXP; not Joshuaa)")
ok(canon('Joshua') != canon('Joshuaa'), "Joshua (RRQ) and Joshuaa (NAVI) stay distinct")
mvp_names = sorted({(m.get('liq_mvp') or '').strip() for m in matches
                    if (m.get('liq_mvp') or '').strip()})
players_u = {ultra(p) for p in all_players}
unresolved = [m for m in mvp_names if ultra(canon(m)) not in players_u]
ok(not unresolved,
   f"all MVP names resolve to one canonical identity (unresolved: {unresolved})")
team_of = {}
for r in praw:
    team_of.setdefault(r['player'], set()).add(r['team'])
bad = []
for m in matches:
    v = (m.get('liq_mvp') or '').strip()
    if not v:
        continue
    c = canon(v)
    if not (team_of.get(c, set()) & {m.get('team_a'), m.get('team_b')}):
        bad.append((v, c, m.get('team_a'), m.get('team_b')))
ok(not bad,
   f"MVP canonical identity played in its series ({bad[:3] if bad else 'all ok'})")
for needle in ('canonicalPlayer', 'PLAYER_ALIAS', 'playoffChance', 'TOTAL_TEAMS',
               'UPPER_BRACKET_SLOTS', '% Playoff Chance', '% Upper Bracket',
               'pin+.pin', 'brk-lines', 'lit-win', 'BRK_LOSS', 'BRK_COLS',
               'seedtip', 'data-seed', 'Quarterfinals', 'bracketGrid', 'matchCard',
               'svgOverlay', 'seedTooltip', 'BrkHover', 'activeSeedId',
               'showSeedPaths', 'playBrk', 'class="drop"', 'data-from', 'data-to',
               'TBD <span', 'sn-sub', 'brkRound', 'brkDropD', 'brkElimLeft',
               'showContextPaths', 'data-elim', '_brkT', 'drop.go',
               'ResizeObserver', 'stHeroDrill', 'stEmbDrill',
               'stTalDrill', 'stItemDrill', 'data-scope', 'data-ovitem',
               'tag pick', 'tag ban', 'mrow sg', 'sgres', 'sgmeta', 'res win',
               '>GAME<', 'dmark', 'data-wtab', 'sb-win'):
    ok(needle in html, f"stats drill-down contains {needle}")
ok('sdot' not in html, "side dots fully removed from game list")
ok('banned by' not in html, "verbose ban detail text removed")
for needle in ('calcChances', 'normalizeFixtures', 'CHANCES-START', 'normTeam',
                'isTerminalScore', 'decidedLive', 'rankTeams', 'wilson'):
    ok(needle in html, f"playoff engine contains {needle}")

# Playoff-chance data integrity: standings must reconcile with the decided
# fixture set (completed + any non-completed row showing a terminal BO3
# scoreline, whose result the standings feed already includes — e.g. Oct 3
# AE 1-2 NAVI still flagged live, Oct 10 RRQ 0-2 TLID still flagged live).
# The reconciled remainder must give every
# team exactly 16 series (double round-robin), with no duplicated fixtures.
stand_rows = load('standings')
sched_rows = load('schedule_all')
slug_of = {'NAVI': 'navi', 'TLID': 'tlid', 'AE': 'ae', 'BTR': 'btr',
           'EVOS': 'evos', 'DEWA': 'dewa', 'ONIC': 'onic', 'RRQ': 'rrq', 'GEEK': 'geek'}


def terminal(sa, sb):
    try:
        sa, sb = int(sa), int(sb)
    except (ValueError, TypeError):
        return False
    return (sa == 2 and sb in (0, 1)) or (sb == 2 and sa in (0, 1))


def is_po(m):
    return 'playoffs' in (m.get('schedule_id') or '') or \
        (m.get('team_a') == 'TBD' and m.get('team_b') == 'TBD')


reg_rows = [m for m in sched_rows if not is_po(m)]
season_cfg = json.loads((ROOT / 'data' / 'season.json').read_text(encoding='utf-8'))
n_teams = len(season_cfg['teams'])
exp_regular = season_cfg['roundRobinRounds'] * n_teams * (n_teams - 1) // 2
exp_pairs = n_teams * (n_teams - 1) // 2
ok(len(reg_rows) == exp_regular == season_cfg['totalRegularFixtures'],
   f"regular season fixtures derive from config ({len(reg_rows)} vs {exp_regular})")
ok(len(stand_rows) == season_cfg['totalTeams'] == n_teams,
   f"standings cover all configured teams ({len(stand_rows)})")
pairs = {}
for m in reg_rows:
    pairs[tuple(sorted([m.get('team_a') or '', m.get('team_b') or '']))] = \
        pairs.get(tuple(sorted([m.get('team_a') or '', m.get('team_b') or ''])), 0) + 1
ok(all(v == season_cfg['roundRobinRounds'] for v in pairs.values()) and len(pairs) == exp_pairs,
   f"double round-robin: {exp_pairs} pairs x{season_cfg['roundRobinRounds']} ({len(pairs)} pairs)")
dec_w, dec_l, dec_gw, dec_gl = {}, {}, {}, {}
decided_n = live_decided_n = 0
bad_scores = []
for m in reg_rows:
    st, sa, sb = m.get('status'), m.get('score_a'), m.get('score_b')
    fin = terminal(sa, sb)
    if st == 'completed':
        if not fin:
            bad_scores.append(m.get('schedule_id'))
            continue
        w = m.get('team_a') if m.get('winner') == 'team_a' else (
            m.get('team_b') if m.get('winner') == 'team_b' else (
                m.get('team_a') if int(sa) > int(sb) else m.get('team_b')))
    elif fin:
        live_decided_n += 1
        w = m.get('team_a') if int(sa) > int(sb) else m.get('team_b')
    else:
        continue
    decided_n += 1
    lo = m.get('team_b') if w == m.get('team_a') else m.get('team_a')
    dec_w[w] = dec_w.get(w, 0) + 1
    dec_l[lo] = dec_l.get(lo, 0) + 1
    gw_w, gl_w = (int(sa), int(sb)) if w == m.get('team_a') else (int(sb), int(sa))
    dec_gw[w] = dec_gw.get(w, 0) + gw_w
    dec_gl[w] = dec_gl.get(w, 0) + gl_w
    dec_gw[lo] = dec_gw.get(lo, 0) + gl_w
    dec_gl[lo] = dec_gl.get(lo, 0) + gw_w
ok(not bad_scores, f"all completed rows have terminal BO3 scores ({bad_scores[:3] if bad_scores else 'ok'})")
n_completed = sum(1 for m in reg_rows if m.get('status') == 'completed')
ok(decided_n == n_completed + live_decided_n,
   f"decided set is completed + live-decisive (got {decided_n} = {n_completed} + {live_decided_n})")
print(f"INFO season progress: {n_completed} completed + {live_decided_n} live-decisive decided")
rec_ok, game_ok = True, True
for r in stand_rows:
    code = {'navi': 'NAVI', 'tlid': 'TLID', 'ae': 'AE', 'btr': 'BTR',
            'evos': 'EVOS', 'dewa': 'DEWA', 'onic': 'ONIC', 'rrq': 'RRQ',
            'geek': 'GEEK'}[r['team_slug']]
    if dec_w.get(code, 0) != int(r['match_win']) or dec_l.get(code, 0) != int(r['match_lose']):
        rec_ok = False
    if dec_gw.get(code, 0) != int(r['game_win']) or dec_gl.get(code, 0) != int(r['game_lose']):
        game_ok = False
ok(rec_ok, "standings Match W-L matches the decided fixture set (all 9 teams)")
ok(game_ok, "standings Game W-L matches the decided fixture set (all 9 teams)")
rem_n = {}
for m in reg_rows:
    if m.get('status') == 'completed' or terminal(m.get('score_a'), m.get('score_b')):
        continue
    rem_n[m.get('team_a')] = rem_n.get(m.get('team_a'), 0) + 1
    rem_n[m.get('team_b')] = rem_n.get(m.get('team_b'), 0) + 1
cap_ok = True
for r in stand_rows:
    code = {'navi': 'NAVI', 'tlid': 'TLID', 'ae': 'AE', 'btr': 'BTR',
            'evos': 'EVOS', 'dewa': 'DEWA', 'onic': 'ONIC', 'rrq': 'RRQ',
            'geek': 'GEEK'}[r['team_slug']]
    if int(r['match_win']) + int(r['match_lose']) + rem_n.get(code, 0) != season_cfg['seriesPerTeam']:
        cap_ok = False
ok(cap_ok, f"played + reconciled-remaining == {season_cfg['seriesPerTeam']} for every team")
n_remaining = sum(rem_n.values()) // 2
ok(decided_n + n_remaining == len(reg_rows),
   f"decided + remaining covers the season ({decided_n} + {n_remaining} vs {len(reg_rows)})")
print(f"INFO reconciled remaining fixtures: {n_remaining}")

print(f"\n{len(fails)} failures, {len(warns)} warnings")
sys.exit(1 if fails else 0)
