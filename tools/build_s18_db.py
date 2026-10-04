"""MPL ID Season 18 ETL -> SQLite + CSV.
Sources:
- Liquipedia api.php (series results, MVPs, drafts, durations) - authoritative for schedule/scores
- mlbbhub API https://mpl.mlbbhub.com/api/v1/id (per-game per-player KDA/gold/damage)
  - /matches, /schedule, /standings, /stats/players, /drafts, /match/<detail_id>
Output: mpl_id_s18.db (SQLite) + csv/ exports.
"""
import json, re, sqlite3, urllib.request, urllib.parse, os, sys
from pathlib import Path

BASE = Path(__file__).parent
ROOT = BASE.parent
DB = ROOT / "data" / "mpl_id_s18.db"
CSVDIR = ROOT / "data" / "csv"
LIQ_API = "https://liquipedia.net/mobilelegends/api.php"
HUB = "https://mpl.mlbbhub.com/api/v1/id"
UA = {"User-Agent": "Mozilla/5.0 (opencode MPL research)"}

def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def get_liq_wikitext(page):
    import gzip
    q = urllib.parse.urlencode({"action":"parse","page":page,"prop":"wikitext","format":"json","origin":"*"})
    req = urllib.request.Request(f"{LIQ_API}?{q}", headers={"User-Agent": "MPL-S18-research/1.0 (local ETL)", "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
        if r.headers.get("Content-Encoding") == "gzip" or raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
        j = json.loads(raw.decode("utf-8"))
    return j["parse"]["wikitext"]["*"]

def parse_duration(s):
    # "17:24" -> seconds
    m = re.match(r"(\d+):(\d+)", s or "")
    if not m: return None
    return int(m.group(1))*60 + int(m.group(2))

def main():
    print("fetch mlbbhub lists...")
    matches = get_json(f"{HUB}/matches")
    standings = get_json(f"{HUB}/standings")
    player_stats = get_json(f"{HUB}/stats/players")
    hero_stats = get_json(f"{HUB}/stats/heroes")
    try:
        playoffs = get_json(f"{HUB}/playoffs")
    except Exception as e:
        print("playoffs fetch failed", e); playoffs = {}
    try:
        drafts = get_json(f"{HUB}/drafts")
    except Exception as e:
        print("drafts fetch failed", e); drafts = {}
    print(f"matches entries={len(matches)} standings={len(standings)} players={len(player_stats)}")

    print("fetch liquipedia regular season wikitext for MVP merge...")
    wt = get_liq_wikitext("MPL/Indonesia/Season 18/Regular Season")
    blocks2 = [m.group(1) for m in re.finditer(r"\|M\d+=\{\{Match([\s\S]*?)(?=\|M\d+=\{\{Match)", wt)]
    liq = []
    for b in blocks2:
        t1 = (re.search(r"opponent1=\{\{TeamOpponent\|([^\}\|\n]+)", b) or [None,""])[1].strip()
        t2 = (re.search(r"opponent2=\{\{TeamOpponent\|([^\}\|\n]+)", b) or [None,""])[1].strip()
        date = (re.search(r"\|date=([^\n]+)", b) or [None,""])[1].strip()[:120]
        mvp = (re.search(r"\|mvp=([^\n\|]*)", b) or [None,""])[1].strip()
        wins = re.findall(r"\|winner=(\d)", b)
        w1 = wins.count("1"); w2 = wins.count("2")
        score = f"{w1}-{w2}" if (w1 or w2) else "vs"
        liq.append({"t1":t1,"t2":t2,"date":date,"mvp":mvp,"score":score})
    print(f"liq series parsed={len(liq)}")

    # map detail_id -> liq MVP by order (both lists are chronological for regular season; mlbbhub /matches order matches liq order for first 50)
    # Build lookup by normalized team pair + score to be safe, fallback by index.
    numeric = [m for m in matches if re.match(r"^\d+$", str(m.get("match_detail_id") or ""))]
    print(f"numeric detail matches={len(numeric)}")
    # mlbbhub match_detail_ids are 1036..1087 range for completed
    detail_ids = sorted(set(str(m["match_detail_id"]) for m in numeric), key=int)
    print("detail_ids:", detail_ids[:10], "...", detail_ids[-10:], f"total {len(detail_ids)}")

    if os.path.exists(DB): os.remove(DB)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.executescript("""
    CREATE TABLE matches(
      match_detail_id TEXT PRIMARY KEY,
      schedule_id TEXT, team_a TEXT, team_b TEXT,
      score_a INTEGER, score_b INTEGER,
      date TEXT, iso_date TEXT, iso_datetime TEXT,
      status TEXT, winner TEXT, vod_url TEXT, match_detail_url TEXT,
      liq_mvp TEXT
    );
    CREATE TABLE games(
      match_detail_id TEXT, game_no INTEGER,
      team_a TEXT, team_b TEXT,
      team_a_kills INTEGER, team_b_kills INTEGER,
      winner TEXT, duration_str TEXT, duration_sec INTEGER,
      team_a_side TEXT, team_b_side TEXT, vod_url TEXT,
      PRIMARY KEY(match_detail_id, game_no)
    );
    CREATE TABLE game_players(
      match_detail_id TEXT, game_no INTEGER,
      team TEXT, player TEXT, lane TEXT, hero TEXT,
      kills INTEGER, deaths INTEGER, assists INTEGER,
      kda REAL, gold INTEGER, gold_per_min REAL,
      hero_damage INTEGER, damage_taken INTEGER, tower_damage INTEGER,
      emblem TEXT, items_json TEXT, talents_json TEXT,
      PRIMARY KEY(match_detail_id, game_no, team, player, hero)
    );
    CREATE TABLE game_bans(
      match_detail_id TEXT, game_no INTEGER, side TEXT, hero TEXT
    );
    CREATE TABLE player_season_stats(
      player TEXT PRIMARY KEY, team TEXT, team_slug TEXT, lane TEXT,
      total_games INTEGER, total_kills INTEGER, avg_kills REAL,
      total_deaths INTEGER, avg_deaths REAL, total_assists INTEGER, avg_assists REAL,
      avg_kda REAL, kill_participation TEXT
    );
    CREATE TABLE standings(
      rank INTEGER PRIMARY KEY, team_name TEXT, team_slug TEXT,
      match_point INTEGER, match_win INTEGER, match_lose INTEGER,
      game_win INTEGER, game_lose INTEGER, net_game_win INTEGER
    );
    CREATE TABLE hero_stats(
      hero TEXT PRIMARY KEY, hero_image TEXT,
      pick INTEGER, ban INTEGER, win INTEGER, win_rate TEXT
    );
    CREATE TABLE schedule_all(
      schedule_id TEXT PRIMARY KEY, team_a TEXT, team_b TEXT,
      score_a INTEGER, score_b INTEGER,
      date TEXT, iso_date TEXT, iso_datetime TEXT,
      status TEXT, winner TEXT, vod_url TEXT,
      match_detail_id TEXT, match_detail_url TEXT
    );
    """)

    for s in standings:
        cur.execute("INSERT INTO standings VALUES(?,?,?,?,?,?,?,?,?)",
            (s.get("rank"), s.get("team_name"), s.get("team_slug"), s.get("match_point"),
             s.get("match_win"), s.get("match_lose"), s.get("game_win"), s.get("game_lose"), s.get("net_game_win")))
    for m in matches:
        cur.execute("INSERT OR REPLACE INTO schedule_all VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (m.get("match_id"), m.get("team_a"), m.get("team_b"), m.get("score_a"), m.get("score_b"),
             m.get("date"), m.get("iso_date"), m.get("iso_datetime"), m.get("status"), m.get("winner"),
             m.get("vod_url"), str(m.get("match_detail_id") or ""), m.get("match_detail_url")))
    for p in player_stats:
        cur.execute("INSERT OR REPLACE INTO player_season_stats VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (p.get("player"), p.get("team"), p.get("team_slug"), p.get("lane"), p.get("total_games"),
             p.get("total_kills"), p.get("avg_kills"), p.get("total_deaths"), p.get("avg_deaths"),
             p.get("total_assists"), p.get("avg_assists"), p.get("avg_kda"), p.get("kill_participation")))
    for h in (hero_stats or []):
        cur.execute("INSERT OR REPLACE INTO hero_stats VALUES(?,?,?,?,?,?)",
            (h.get("hero"), h.get("hero_image"), h.get("pick"), h.get("ban"),
             h.get("win"), h.get("win_rate")))
    with open(ROOT / "data" / "playoffs.json", "w", encoding="utf-8") as f:
        json.dump(playoffs, f, ensure_ascii=False)

    # MVP merge: liq list is 72 long in chronological order; numeric hub matches are first 50ish completed in same order.
    # Align by matching team pair (normalized) where possible.
    def norm(t): return re.sub(r"\s+", " ", (t or "").lower().replace("esports","").strip())
    TEAM_ALIAS = {"rrq hoshi":"rrq","geek fam id":"geek","geek fam":"geek","bigetron by vitality":"btr","team liquid id":"tlid",
                  "natus vincere":"navi","alter ego":"ae","dewa united esports":"dewa","onic":"onic","evos":"evos"}
    def canon(t):
        n = norm(t)
        return TEAM_ALIAS.get(n, n)
    liq_idx = 0
    mvp_map = {}
    # simple chronological attach: for each hub numeric in iso_datetime order, attach next liq with same canon pair
    hub_sorted = sorted(numeric, key=lambda m: (m.get("iso_datetime") or "", str(m.get("match_detail_id"))))
    liq_remaining = liq[:]
    for h in hub_sorted:
        ha, hb = canon(h.get("team_a")), canon(h.get("team_b"))
        found = None
        for i, l in enumerate(liq_remaining):
            if {canon(l["t1"]), canon(l["t2"])} == {ha, hb}:
                found = liq_remaining.pop(i); break
        if found is None and liq_remaining:
            found = liq_remaining.pop(0)
        mvp_map[str(h["match_detail_id"])] = (found or {}).get("mvp","")

    n_games = n_rows = n_bans = 0
    fails = []
    for did in detail_ids:
        try:
            d = get_json(f"{HUB}/match/{did}")
        except Exception as e:
            fails.append((did, str(e))); continue
        # find schedule row
        sched = next((m for m in numeric if str(m.get("match_detail_id"))==str(did)), {})
        cur.execute("INSERT OR REPLACE INTO matches VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (str(did), sched.get("match_id"), d.get("team_a"), d.get("team_b"),
             d.get("score_a"), d.get("score_b"), sched.get("date"), sched.get("iso_date"),
             sched.get("iso_datetime"), sched.get("status"), sched.get("winner"),
             sched.get("vod_url"), sched.get("match_detail_url"), mvp_map.get(str(did),"")))
        for g in d.get("games", []):
            dur = g.get("duration"); sec = parse_duration(dur)
            cur.execute("INSERT OR REPLACE INTO games VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (str(did), g.get("game"), g.get("team_a"), g.get("team_b"),
                 g.get("team_a_kills"), g.get("team_b_kills"), g.get("winner"),
                 dur, sec, g.get("team_a_side"), g.get("team_b_side"), g.get("vod_url")))
            n_games += 1
            for b in (g.get("bans_a") or []):
                cur.execute("INSERT INTO game_bans VALUES(?,?,?,?)", (str(did), g.get("game"), "A", b)); n_bans+=1
            for b in (g.get("bans_b") or []):
                cur.execute("INSERT INTO game_bans VALUES(?,?,?,?)", (str(did), g.get("game"), "B", b)); n_bans+=1
            for pl in (g.get("players") or []):
                gold = pl.get("gold") or 0
                gpm = round(gold/(sec/60), 1) if sec else None
                cur.execute("INSERT OR REPLACE INTO game_players VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (str(did), g.get("game"), pl.get("team"), pl.get("player"), pl.get("lane"), pl.get("hero"),
                     pl.get("kill"), pl.get("death"), pl.get("assist"), pl.get("kda"), gold, gpm,
                     pl.get("hero_damage"), pl.get("damage_taken"), pl.get("tower_damage"),
                     pl.get("emblem"), json.dumps(pl.get("items") or []), json.dumps(pl.get("talents") or [])))
                n_rows += 1
    con.commit()
    print(f"stored games={n_games} player_rows={n_rows} bans={n_bans} fails={fails}")
    # also store upcoming (non-numeric / no detail) schedule rows
    upcoming = [m for m in matches if not re.match(r"^\d+$", str(m.get("match_detail_id") or ""))]
    print(f"upcoming/no-detail entries={len(upcoming)} (not in DB matches; see schedule API)")
    # quick audits
    for q in ["SELECT COUNT(*) FROM matches","SELECT COUNT(*) FROM schedule_all","SELECT COUNT(*) FROM games","SELECT COUNT(*) FROM game_players",
              "SELECT COUNT(DISTINCT player) FROM game_players","SELECT COUNT(*) FROM game_bans"]:
        print(q, cur.execute(q).fetchone()[0])
    print("sample:", cur.execute("SELECT match_detail_id,game_no,team,player,hero,kills,deaths,assists,kda,gold,gold_per_min FROM game_players LIMIT 3").fetchall())
    con.close()

    # CSV exports
    import csv
    CSVDIR.mkdir(exist_ok=True)
    con = sqlite3.connect(DB)
    for tbl in ["matches","schedule_all","games","game_players","game_bans","player_season_stats","hero_stats","standings"]:
        rows = con.execute(f"SELECT * FROM {tbl}").fetchall()
        cols = [d[0] for d in con.execute(f"SELECT * FROM {tbl} LIMIT 0").description]
        with open(CSVDIR/f"{tbl}.csv","w",newline="",encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(cols); w.writerows(rows)
        print(f"csv {tbl}: {len(rows)} rows")
    con.close()
    print("done:", DB)

if __name__ == "__main__":
    main()
