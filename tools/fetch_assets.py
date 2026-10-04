"""Fetch missing hero/item assets so EVERY referenced asset exists locally (STRICT).

Refs come from data/csv/game_players.csv + game_bans.csv (+ live API for artwork):
- heroes: every name in players/bans must have a manifest key + file on disk
- items: every equipment ID (equipment/<id> AND equip/<id> URL patterns) plus every
  opaque scoregg item URL (/m/...) must have a manifest key + file on disk

Artwork sources: mlbbhub live /match API hero_image (preferred, same CDN family as
existing assets), Liquipedia infobox via Special:FilePath (fallback),
mlbb-image.scoregg.com for items.

Usage: python tools/fetch_assets.py [--check-only]
Exit 0 = all refs covered, 1 = gaps remain.
"""
import csv
import gzip
import hashlib
import json
import re
import sqlite3
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).parent
ROOT = BASE.parent
UA = {'User-Agent': 'MPL-S18-assets/1.0 (local ETL)',
      'Accept-Encoding': 'gzip'}
HUB = 'https://mpl.mlbbhub.com/api/v1/id'
LIQ = 'https://liquipedia.net/mobilelegends'
fails = []


def fetch_raw(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        if r.headers.get('Content-Encoding') == 'gzip' or raw[:2] == b'\x1f\x8b':
            try:
                raw = gzip.decompress(raw)
            except OSError:
                pass
        return raw, r.headers.get_content_type()


def fetch_bytes(url, timeout=40):
    req = urllib.request.Request(url, headers={'User-Agent': UA['User-Agent']})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def is_image(b):
    return (b[:4] == b'\x89PNG' or b[:3] == b'\xff\xd8\xff') and len(b) > 1500


def load_csv(name):
    with open(ROOT / 'data' / 'csv' / f'{name}.csv', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def refs(live=False):
    praw = load_csv('game_players')
    bans = load_csv('game_bans')
    heroes = sorted({r['hero'] for r in praw if r.get('hero')}
                    | {r['hero'] for r in bans if r.get('hero')})
    con = sqlite3.connect(ROOT / 'data' / 'mpl_id_s18.db')
    eq_ids, opaque = set(), set()
    for (js,) in con.execute('SELECT items_json FROM game_players'):
        for u in (json.loads(js or '[]') or []):
            if not u:
                continue
            m = re.search(r'(?:equipment|equip)/(\d+)\.png', u)
            if m:
                eq_ids.add(m.group(1))
            elif 'scoregg.com' in u:
                opaque.add(u.split('?')[0])
    con.close()
    if live:
        lh, le, lo = live_refs()
        heroes = sorted(set(heroes) | lh)
        eq_ids |= le
        opaque |= lo
    return heroes, sorted(eq_ids), sorted(opaque)


def live_refs():
    """Scan live /matches + /match APIs (season may have progressed)."""
    heroes, eq_ids, opaque = set(), set(), set()
    try:
        raw, _ = fetch_raw(f'{HUB}/matches')
        ms = json.loads(raw.decode('utf-8'))
    except Exception as e:
        print(f'live /matches failed: {str(e)[:80]}')
        return heroes, eq_ids, opaque
    ids = sorted({str(m.get('match_detail_id')) for m in ms
                  if re.match(r'^\d+$', str(m.get('match_detail_id') or ''))})
    print(f'live scan: {len(ids)} matches')
    for did in ids:
        try:
            raw, _ = fetch_raw(f'{HUB}/match/{did}')
            d = json.loads(raw.decode('utf-8'))
        except Exception:
            continue
        for g in d.get('games', []):
            for p in g.get('players', []) or []:
                if p.get('hero'):
                    heroes.add(p['hero'])
                for u in p.get('items', []) or []:
                    if not u:
                        continue
                    m = re.search(r'(?:equipment|equip)/(\d+)\.png', u)
                    if m:
                        eq_ids.add(m.group(1))
                    elif 'scoregg.com' in u:
                        opaque.add(u.split('?')[0])
    return heroes, eq_ids, opaque


def live_hero_images(need, match_ids):
    """hero name -> hero_image from live /match API (players only)."""
    out = {}
    for did in match_ids:
        try:
            raw, _ = fetch_raw(f'{HUB}/match/{did}')
            d = json.loads(raw.decode('utf-8'))
        except Exception as e:
            print(f'  live match {did} failed: {str(e)[:80]}')
            continue
        for g in d.get('games', []):
            for p in g.get('players', []):
                h = p.get('hero')
                if h in need and h not in out and p.get('hero_image'):
                    out[h] = p['hero_image']
        if len(out) == len(need):
            break
    return out


def liq_infobox(hero):
    """Direct commons image URL for a hero's Liquipedia infobox, or None."""
    q = urllib.parse.urlencode({'action': 'parse', 'page': hero,
                                'prop': 'wikitext', 'format': 'json',
                                'origin': '*'})
    try:
        raw, _ = fetch_raw(f'{LIQ}/api.php?{q}')
        wt = json.loads(raw.decode('utf-8'))['parse']['wikitext']['*']
    except Exception as e:
        print(f'  liquipedia wikitext {hero}: {str(e)[:80]}')
        return None
    m = re.search(r'\|image\s*=\s*([^\n\|]+)', wt)
    if not m:
        return None
    fn = m.group(1).strip()
    q2 = urllib.parse.urlencode({'action': 'query', 'titles': 'File:' + fn,
                                 'prop': 'imageinfo', 'iiprop': 'url|size',
                                 'iiurlwidth': 400, 'format': 'json'})
    try:
        raw2, _ = fetch_raw(f'{LIQ}/api.php?{q2}')
        pages = json.loads(raw2.decode('utf-8'))['query']['pages']
        for p in pages.values():
            ii = (p.get('imageinfo') or [{}])[0]
            return ii.get('thumburl') or ii.get('url')
    except Exception as e:
        print(f'  liquipedia imageinfo {hero}: {str(e)[:80]}')
    return None


def save(url, dest, tries=3):
    err = ''
    for a in range(tries):
        try:
            b = fetch_bytes(url)
        except Exception as e:
            err = f'download failed: {str(e)[:80]}'
        else:
            if is_image(b):
                ext = '.png' if b[:4] == b'\x89PNG' else '.jpg'
                dest = dest.with_suffix(ext)
                dest.write_bytes(b)
                return dest
            err = f'not a valid image ({len(b)} bytes)'
        if a < tries - 1:
            import time
            time.sleep(1 + a)
    return err


def main():
    check_only = '--check-only' in sys.argv
    use_live = '--live' in sys.argv
    heroes, eq_ids, opaque = refs(live=use_live)
    print(f'refs: {len(heroes)} heroes, {len(eq_ids)} equipment ids, '
          f'{len(opaque)} opaque item urls')
    man_path = ROOT / 'assets' / 'manifest.json'
    man = json.loads(man_path.read_text(encoding='utf-8'))
    heroes_m, items_m = man.setdefault('heroes', {}), man.setdefault('items', {})

    def ok_file(rel):
        p = ROOT / rel
        return p.exists() and p.stat().st_size > 1500

    missing_heroes = [h for h in heroes
                      if h not in heroes_m or not ok_file(heroes_m[h])]
    missing_eq = [i for i in eq_ids
                  if i not in items_m or not ok_file(items_m[i])]
    missing_op = [u for u in opaque
                  if u not in items_m or not ok_file(items_m[u])]
    print(f'missing: heroes={missing_heroes} equip={missing_eq} '
          f'opaque={len(missing_op)}')

    if check_only:
        bad = missing_heroes + missing_eq + missing_op
        print('CHECK-ONLY:', 'ALL COVERED' if not bad else f'GAPS {bad[:8]}')
        return 0 if not bad else 1

    # --- heroes: resolve artwork urls ---
    hwant = [h for h in missing_heroes]
    art = {}
    if hwant:
        if use_live:
            try:
                raw, _ = fetch_raw(f'{HUB}/matches')
                ms = json.loads(raw.decode('utf-8'))
                ids = sorted({str(m.get('match_detail_id')) for m in ms
                              if re.match(r'^\d+$', str(m.get('match_detail_id') or ''))})
            except Exception as e:
                print(f'live /matches failed: {str(e)[:80]}')
                ids = []
        else:
            con = sqlite3.connect(ROOT / 'data' / 'mpl_id_s18.db')
            ids = [r[0] for r in con.execute(
                'SELECT DISTINCT match_detail_id FROM game_players').fetchall()]
            con.close()
        art = live_hero_images(set(hwant), ids)
        print('live hero_image:', {k: v[:60] for k, v in art.items()})
        for h in hwant:
            if h not in art:
                url = liq_infobox(h)
                if url:
                    art[h] = url
                    print(f'liquipedia fallback {h} -> {url[:80]}')
    for h in hwant:
        if h not in art:
            fails.append(f'hero artwork unresolvable: {h}')
            continue
        safe = re.sub(r'[^\w\-]+', '_', h).strip('_') or 'hero'
        res = save(art[h], ROOT / 'assets' / 'heroes' / safe)
        if isinstance(res, Path):
            heroes_m[h] = str(res.relative_to(ROOT)).replace('\\', '/')
            print(f'hero {h} -> {heroes_m[h]} ({res.stat().st_size}b)')
        else:
            fails.append(f'hero {h}: {res}')

    # --- items: /equip/<id>.png are stable scoregg urls ---
    for i in missing_eq:
        res = save(f'https://mlbb-image.scoregg.com/equip/{i}.png',
                   ROOT / 'assets' / 'items' / i)
        if isinstance(res, Path):
            items_m[i] = str(res.relative_to(ROOT)).replace('\\', '/')
            print(f'item {i} -> {items_m[i]}')
        else:
            fails.append(f'item {i}: {res}')

    # --- items: opaque urls keyed by full url ---
    for n, u in enumerate(missing_op):
        fn = 'm_' + hashlib.md5(u.encode()).hexdigest()[:10]
        res = save(u, ROOT / 'assets' / 'items' / fn)
        if isinstance(res, Path):
            items_m[u] = str(res.relative_to(ROOT)).replace('\\', '/')
            print(f'opaque item -> {items_m[u]}')
        else:
            fails.append(f'opaque item {u[:60]}: {res}')

    man_path.write_text(json.dumps(man, ensure_ascii=False, indent=1),
                        encoding='utf-8')

    # heroes_index.json is the legacy name->path map; keep in sync
    hip = ROOT / 'assets' / 'heroes_index.json'
    try:
        hi = json.loads(hip.read_text(encoding='utf-8'))
        hi.update({h: heroes_m[h] for h in heroes if h in heroes_m})
        hip.write_text(json.dumps(hi, ensure_ascii=False, indent=1),
                       encoding='utf-8')
    except Exception as e:
        print('heroes_index sync skipped:', str(e)[:80])

    # final STRICT re-audit from disk
    man = json.loads(man_path.read_text(encoding='utf-8'))
    gaps = [h for h in heroes
            if h not in man['heroes'] or not ok_file(man['heroes'][h])]
    gaps += [i for i in eq_ids
             if i not in man['items'] or not ok_file(man['items'][i])]
    gaps += [u for u in opaque
             if u not in man['items'] or not ok_file(man['items'][u])]
    # players: no remote photo source exists, so new names can only be
    # reported (refresh button keeps the initials fallback for them)
    con = sqlite3.connect(ROOT / 'data' / 'mpl_id_s18.db')
    all_players = {r[0] for r in con.execute(
        'SELECT DISTINCT player FROM game_players')}
    con.close()
    man_p = {k.lower(): k for k in man.get('players', {})}
    new_players = sorted(p for p in all_players if p.lower() not in man_p)
    if new_players:
        print(f'NOTE {len(new_players)} players have no photo '
              f'(initials fallback): {new_players[:8]}')
    if gaps:
        print(f'STRICT FAIL: {len(gaps)} gaps remain: {gaps[:8]}')
        return 1
    print(f'STRICT PASS: {len(heroes)} heroes + {len(eq_ids)} equip ids + '
          f'{len(opaque)} opaque urls all on disk')
    if fails:
        print('warnings:', fails)
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
