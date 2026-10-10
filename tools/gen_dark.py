"""Dark minimalist Pinterest-style webapp (v2) from CSV data. No external deps.
Single-source templates live in tools/templates/ (style.css, app.js, doc.html).
Season rules come from data/season.json (validated before every build).
"""
import csv, json, re, sqlite3
from pathlib import Path
from collections import Counter, defaultdict
BASE = Path(__file__).parent
ROOT = BASE.parent
TPL = BASE / 'templates'

REQUIRED_SEASON_KEYS = ("seasonId", "teams", "aliases", "totalTeams",
                        "roundRobinRounds", "seriesPerTeam", "totalRegularFixtures",
                        "playoffMatches", "playoffSlots", "upperBracketSlots",
                        "tiebreakers", "matchFormat", "endpoints", "database",
                        "csvDir", "playoffsJson", "cacheNamespace", "cacheSchema",
                        "model")


def validate_season(cfg):
    """Strict season-configuration validation. Returns a list of problems
    (empty = valid). Pure function over the parsed JSON object — no I/O,
    safe to import for unit tests."""
    problems = []

    def err(m):
        problems.append(m)

    if not isinstance(cfg, dict):
        return ["season config is not an object"]
    for k in REQUIRED_SEASON_KEYS:
        if k not in cfg:
            err(f"missing required field '{k}'")
    if problems:
        return problems
    teams = cfg["teams"]
    if not isinstance(teams, list) or not teams or any(not isinstance(t, str) or not t for t in teams):
        err("teams must be a non-empty list of strings")
        teams = []
    lowered = [t.lower() for t in teams if isinstance(t, str)]
    if len(set(lowered)) != len(lowered):
        err("duplicate teams")
    n = len(teams)
    if cfg["totalTeams"] != n:
        err(f"totalTeams {cfg['totalTeams']} != len(teams) {n}")
    rr = cfg["roundRobinRounds"]
    if not isinstance(rr, int) or rr < 1:
        err("roundRobinRounds must be a positive int")
    elif isinstance(rr, int) and rr >= 1 and n:
        if cfg["seriesPerTeam"] != rr * (n - 1):
            err("seriesPerTeam != roundRobinRounds*(teams-1)")
        if cfg["totalRegularFixtures"] != rr * n * (n - 1) // 2:
            err("totalRegularFixtures != rounds*n*(n-1)/2")
    ps, ub = cfg["playoffSlots"], cfg["upperBracketSlots"]
    if not isinstance(ps, int) or not 1 <= ps < max(n, 1):
        err("playoffSlots must satisfy 1 <= slots < teams")
    if not isinstance(ub, int) or not 0 <= ub <= (ps if isinstance(ps, int) else 0):
        err("upperBracketSlots must satisfy 0 <= slots <= playoffSlots")
    if not isinstance(cfg["tiebreakers"], list) or not cfg["tiebreakers"]:
        err("tiebreakers must be a non-empty list")
    al = cfg["aliases"]
    if not isinstance(al, dict) or not al:
        err("aliases must be a non-empty map")
    else:
        for t in teams:
            if al.get(t.lower()) != t:
                err(f"aliases missing self-key for team '{t}'")
        teamset = set(lowered)
        for k, v in al.items():
            if not isinstance(k, str) or not k or str(v).lower() not in teamset:
                err(f"alias '{k}' does not resolve to a known team")
                break
    ep = cfg["endpoints"]
    if not isinstance(ep, dict) or not all(isinstance(ep.get(k), str) and ep[k] for k in ("hub", "liquipediaApi", "liquipediaSeasonPage")):
        err("endpoints.hub/liquipediaApi/liquipediaSeasonPage must be non-empty strings")
    for k in ("database", "csvDir", "playoffsJson", "matchFormat"):
        if not isinstance(cfg[k], str) or not cfg[k]:
            err(f"'{k}' must be a non-empty string")
    if not isinstance(cfg["cacheNamespace"], str) or not cfg["cacheNamespace"]:
        err("cacheNamespace must be a non-empty string")
    if not isinstance(cfg["cacheSchema"], int) or cfg["cacheSchema"] < 1:
        err("cacheSchema must be a positive int")
    mo = cfg["model"]
    if not isinstance(mo, dict):
        err("model must be an object")
    else:
        if mo.get("winProb") not in ("bradley-terry", "even"):
            err("model.winProb must be 'bradley-terry' or 'even'")
        pw, pg = mo.get("priorWins"), mo.get("priorGames")
        if not isinstance(pw, int) or not isinstance(pg, int) or not 0 < pw < pg:
            err("model prior requires 0 < priorWins < priorGames (interior estimates)")
        if not isinstance(mo.get("trials"), int) or mo["trials"] < 1:
            err("model.trials must be a positive int")
        if not isinstance(mo.get("seed"), int) or mo["seed"] < 0:
            err("model.seed must be a non-negative int")
    return problems


def load(name):
    with open(ROOT/'data'/'csv'/f'{name}.csv', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def main():
    season = json.loads((ROOT / 'data' / 'season.json').read_text(encoding='utf-8'))
    problems = validate_season(season)
    if problems:
        print("SEASON CONFIG INVALID:")
        for p in problems:
            print(" -", p)
        raise SystemExit(1)
    sched = load('schedule_all')
    games = load('games')
    for g in games:
        for k in ('game_no', 'team_a_kills', 'team_b_kills', 'duration_sec'):
            try: g[k] = int(float(g[k])) if g[k] not in ('', None) else 0
            except: g[k] = 0
    season_stats = load('player_season_stats')
    stand = load('standings')
    matches = load('matches')
    praw = load('game_players')
    hero_stats = load('hero_stats')
    playoffs = json.loads((ROOT / 'data' / 'playoffs.json').read_text(encoding='utf-8'))
    bans_raw = load('game_bans')
    bans = [{'match_detail_id': str(r['match_detail_id']), 'game_no': int(r['game_no']), 'side': r['side'], 'hero': r['hero']} for r in bans_raw]
    players = [{k: r[k] for k in ('match_detail_id','game_no','team','player','lane','hero','kills','deaths','assists','kda','gold','gold_per_min','hero_damage','damage_taken','tower_damage')} for r in praw]
    for r in players:
        for k in ('game_no','kills','deaths','assists','gold','hero_damage','damage_taken','tower_damage'):
            try: r[k] = int(float(r[k])) if r[k] not in ('',None) else 0
            except: r[k] = 0
        for k in ('kda','gold_per_min'):
            try: r[k] = float(r[k]) if r[k] not in ('',None) else 0
            except: r[k] = 0
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
    DATA = {"schedule": sched, "games": games, "players": players, "bans": bans, "hero_pool": hero_pool, "season": season_stats, "standings": stand, "matches": matches, "heroes": hero_stats, "playoffs": playoffs}
    data_js = json.dumps(DATA, ensure_ascii=False, separators=(',', ':')).replace('</scr'+'ipt>', '<\\/scr'+'ipt>')
    TEAMS = season["teams"]

    css = (TPL / 'style.css').read_text(encoding='utf-8')
    js = (TPL / 'app.js').read_text(encoding='utf-8')
    doc = (TPL / 'doc.html').read_text(encoding='utf-8')

    manifest = json.loads((ROOT / 'assets' / 'manifest.json').read_text(encoding='utf-8'))
    season_js = json.dumps(season, ensure_ascii=False, separators=(',', ':'))
    doc = doc.replace('__CSS__', css).replace('__JS__', js.replace('__DATA__', data_js).replace('__SEASON__', season_js).replace('__TEAMS__', json.dumps(TEAMS))).replace('__ASSETS__', json.dumps(manifest))
    out = ROOT / 'mpl_id_s18_dark.html'
    # Platform-independent output: inputs are read in universal-newline mode
    # (already LF-only in memory), so write with newline='\n' to keep the
    # committed file byte-identical on Windows and Linux. A CRLF build would
    # break the parity gate on case-sensitive CI runners.
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(doc.replace('\r\n', '\n'))
    print('wrote', out, len(doc))


if __name__ == '__main__':
    main()
