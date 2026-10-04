"""Dark minimalist Pinterest-style webapp (v2) from CSV data. No external deps.
Single-source templates live in tools/templates/ (style.css, app.js, doc.html).
"""
import csv, json, re, sqlite3
from pathlib import Path
BASE = Path(__file__).parent
ROOT = BASE.parent
TPL = BASE / 'templates'

def load(name):
    with open(ROOT/'data'/'csv'/f'{name}.csv', encoding='utf-8') as f:
        return list(csv.DictReader(f))

sched = load('schedule_all')
games = load('games')
for g in games:
    for k in ('game_no', 'team_a_kills', 'team_b_kills', 'duration_sec'):
        try: g[k] = int(float(g[k])) if g[k] not in ('', None) else 0
        except: g[k] = 0
season = load('player_season_stats')
stand = load('standings')
matches = load('matches')
praw = load('game_players')
hero_stats = load('hero_stats')
playoffs = json.loads((ROOT / 'data' / 'playoffs.json').read_text(encoding='utf-8'))
praw = load('game_players')
players = [{k: r[k] for k in ('match_detail_id','game_no','team','player','lane','hero','kills','deaths','assists','kda','gold','gold_per_min','hero_damage','damage_taken','tower_damage')} for r in praw]
for r in players:
    for k in ('game_no','kills','deaths','assists','gold','hero_damage','damage_taken','tower_damage'):
        try: r[k] = int(float(r[k])) if r[k] not in ('',None) else 0
        except: r[k] = 0
    for k in ('kda','gold_per_min'):
        try: r[k] = float(r[k]) if r[k] not in ('',None) else 0
        except: r[k] = 0
from collections import Counter, defaultdict
pool = defaultdict(Counter)
for r in players:
    pool[r['player']][r['hero']] += 1
hero_pool = {p: sorted(c.items(), key=lambda x: -x[1])[:6] for p,c in pool.items()}
_con = sqlite3.connect(ROOT / 'data' / 'mpl_id_s18.db')
for _r in players:
    _row = _con.execute('SELECT emblem, talents_json, items_json FROM game_players WHERE match_detail_id=? AND game_no=? AND team=? AND player=? AND hero=?', (str(_r['match_detail_id']), int(_r['game_no']), _r['team'], _r['player'], _r['hero'])).fetchone()
    if _row:
        _me = re.search(r'emblem/(\d+)\.png', _row[0] or '')
        _r['e'] = _me.group(1) if _me else None
        _r['t'] = [mm.group(1) for _u in json.loads(_row[1] or '[]') for mm in [re.search(r'rune/(\d+)\.png', _u)] if mm]
        def _iref(_u):
            _m = re.search(r'(?:equipment|equip)/(\d+)\.png', _u or '')
            if _m:
                return _m.group(1)
            # opaque scoregg item urls have no numeric id: keep the stable url
            # (manifest keys them by full url)
            if _u and 'scoregg.com' in _u:
                return _u.split('?')[0]
            return None
        _r['i'] = [_f for _u in json.loads(_row[2] or '[]') for _f in [_iref(_u)] if _f]
_con.close()
DATA = {"schedule": sched, "games": games, "players": players, "hero_pool": hero_pool, "season": season, "standings": stand, "matches": matches, "heroes": hero_stats, "playoffs": playoffs}
data_js = json.dumps(DATA, ensure_ascii=False, separators=(',', ':')).replace('</scr'+'ipt>', '<\\/scr'+'ipt>')
TEAMS = ["AE","BTR","DEWA","EVOS","GEEK","NAVI","ONIC","RRQ","TLID"]

css = (TPL / 'style.css').read_text(encoding='utf-8')
js = (TPL / 'app.js').read_text(encoding='utf-8')
doc = (TPL / 'doc.html').read_text(encoding='utf-8')

manifest = json.loads((ROOT / 'assets' / 'manifest.json').read_text(encoding='utf-8'))
doc = doc.replace('__CSS__', css).replace('__JS__', js.replace('__DATA__', data_js).replace('__TEAMS__', json.dumps(TEAMS))).replace('__ASSETS__', json.dumps(manifest))
out = ROOT / 'mpl_id_s18_dark.html'
out.write_text(doc, encoding='utf-8')
print('wrote', out, len(doc))
