"""MPL ID Season 18 ETL -> SQLite + CSV.
Sources:
- Liquipedia api.php (series results, MVPs, drafts, durations) - authoritative for schedule/scores
- mlbbhub API https://mpl.mlbbhub.com/api/v1/id (per-game per-player KDA/gold/damage)
  - /matches, /schedule, /standings, /stats/players, /drafts, /match/<detail_id>
Output: mpl_id_s18.db (SQLite) + csv/ exports.
"""
import json, re, sqlite3, urllib.request, urllib.parse, os, shutil
from pathlib import Path
from gen_dark import validate_season

BASE = Path(__file__).parent
ROOT = BASE.parent
CFG = json.loads((ROOT / "data" / "season.json").read_text(encoding="utf-8"))
_CFG_PROBLEMS = validate_season(CFG)
if _CFG_PROBLEMS:
    print("SEASON CONFIG INVALID:")
    for _p in _CFG_PROBLEMS:
        print(" -", _p)
    raise SystemExit(1)
DB = ROOT / CFG["database"]
CSVDIR = ROOT / CFG["csvDir"]
PLAYOFFS_JSON = ROOT / CFG["playoffsJson"]
LIQ_SEASON_PAGE = CFG["endpoints"]["liquipediaSeasonPage"]
# Alias keys are lowercase alphanumeric (no spaces/punctuation); the same
# normalization must be used for every lookup (cf. normTeamCode in app.js).
TEAM_ALIAS = CFG["aliases"]


def norm_team(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


def canon_team(t):
    # Alias values use display case; canonical codes are lowercase.
    return TEAM_ALIAS.get(norm_team(t), norm_team(t)).lower()


# One hero appears under two spellings in the API: hero_stats says "Zetian"
# while per-player rows say "Wu/Zetian". They are the same hero (16 picks
# each), so fold the variant at ingestion rather than losing the identity.
HERO_RENAMES = {
    "wuzetian": "Zetian",
    "lapulapu": "Lapu-Lapu",
    "yisunshin": "Yi Sun-Shin",
    "cici": "Cici",
}


def canon_hero(h):
    return HERO_RENAMES.get(norm_team(h), h)


def clean_bans(bans):
    """Deduplicate ban heroes and drop empty placeholder ids.

    An empty string is a missing ban, not a hero named "". The API occasionally
    emits one in place of a fifth ban; it must never enter game_bans.
    """
    return [b for b in dict.fromkeys(bans or []) if b and str(b).strip()]


def attach_mvps(hub_numeric, liq):
    """Map hub match_detail_id -> Liquipedia MVP by normalized team pair.

    Both lists are chronological; duplicate pairs (double round-robin legs)
    consume blocks in order. Unmatched rows keep a blank MVP — never attach
    an unrelated block (that misattributes MVPs across series).
    Returns {detail_id: mvp}."""
    liq_remaining = list(liq)
    out = {}
    hub_sorted = sorted(hub_numeric,
                        key=lambda m: (m.get("iso_datetime") or "", str(m.get("match_detail_id"))))
    for h in hub_sorted:
        ha, hb = canon_team(h.get("team_a")), canon_team(h.get("team_b"))
        found = None
        for i, l in enumerate(liq_remaining):
            if {canon_team(l["t1"]), canon_team(l["t2"])} == {ha, hb}:
                found = liq_remaining.pop(i)
                break
        out[str(h["match_detail_id"])] = (found or {}).get("mvp", "")
    return out
# Staging lives inside data/ so os.replace() publication stays on one
# filesystem (atomic); it is removed after a successful publish.
STAGING = ROOT / "data" / ".staging-s18"
# Endpoint literals below are defaults only: main() replaces them from the
# validated season config before any request, so the config is authoritative.
LIQ_API = "https://liquipedia.net/mobilelegends/api.php"
HUB = "https://mpl.mlbbhub.com/api/v1/id"
UA = {"User-Agent": "MPL-S18-research/1.0 (local ETL)"}

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

def parse_liq_matches(wikitext):
    """Split Liquipedia wikitext into per-series match dicts.

    A block ends at the next match marker OR at end-of-input, so the final
    block is captured even though no subsequent marker follows it.
    Returns [{t1, t2, date, mvp, score}]; never raises on malformed input.
    """
    try:
        blocks = [m.group(1) for m in re.finditer(
            r"\|M\d+=\{\{Match([\s\S]*?)(?=\|M\d+=\{\{Match|\Z)", wikitext or "")]
    except re.error:
        return []
    liq = []
    for b in blocks:
        try:
            t1 = (re.search(r"opponent1=\{\{TeamOpponent\|([^\}\|\n]+)", b) or [None, ""])[1].strip()
            t2 = (re.search(r"opponent2=\{\{TeamOpponent\|([^\}\|\n]+)", b) or [None, ""])[1].strip()
            date = (re.search(r"\|date=([^\n]+)", b) or [None, ""])[1].strip()[:120]
            mvp = (re.search(r"\|mvp=([^\n\|]*)", b) or [None, ""])[1].strip()
            wins = re.findall(r"\|winner=(\d)", b)
            w1 = wins.count("1"); w2 = wins.count("2")
            score = f"{w1}-{w2}" if (w1 or w2) else "vs"
        except (IndexError, TypeError):
            continue
        liq.append({"t1": t1, "t2": t2, "date": date, "mvp": mvp, "score": score})
    return liq


def _is_playoff_schedule(row):
    """True for bracket rows, never for a regular-season fixture."""
    sid = str(row.get("schedule_id") or "").lower()
    return "playoff" in sid or (row.get("team_a") == "TBD" and row.get("team_b") == "TBD")


def _score_winner(row):
    """Return the winning team code from a decided schedule row, else None."""
    try:
        sa, sb = int(row.get("score_a")), int(row.get("score_b"))
    except (TypeError, ValueError):
        return None
    if sa == sb:
        return None
    return row.get("team_a") if sa > sb else row.get("team_b")

def winner_from_detail_score(score_a, score_b):
    """Return the winning side relative to the match-detail row's team order."""
    try:
        a, b = int(score_a), int(score_b)
    except (TypeError, ValueError):
        return None
    if a == b:
        return None
    return "team_a" if a > b else "team_b"


def validate_build(con, fails, playoff_payload, season=None):
    """Phase-aware completeness gate for a freshly built (staging) database.

    Returns a list of human-readable problems (empty = publishable). This is
    deliberately stricter than "tables are non-empty": every completed
    regular-season schedule row must have its detail, every declared series
    score must be backed by exactly that many game rows, and the derived
    Match/Game W-L must reconcile with the published standings.

    A season that still has unplayed regular-season fixtures may publish a
    partial snapshot, but it is never called final: finality requires all
    configured regular fixtures to be completed and present. Finality/scope is
    also recorded by tools/write_meta.py from the same database.
    Never touches the network; operates on the given connection only.
    """
    season = season or {}
    exp_regular = int(season.get("totalRegularFixtures", 72))
    exp_playoffs = int(season.get("playoffMatches", 8))
    aliases = {re.sub(r"[^a-z0-9]", "", str(k).lower()): str(v).upper()
               for k, v in (season.get("aliases") or {}).items()}
    def canon(team):
        key = re.sub(r"[^a-z0-9]", "", str(team or "").lower())
        return aliases.get(key, key.upper())
    problems = []
    con.row_factory = sqlite3.Row
    try:
        tables = {r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    except Exception as e:
        return [f"schema unreadable: {e}"]
    for t in ("matches", "schedule_all", "games", "game_players",
              "player_season_stats", "hero_stats", "standings", "team_games"):
        if t not in tables:
            problems.append(f"missing table {t}")
    if problems:
        return problems

    sched = [dict(r) for r in con.execute(
        "SELECT schedule_id, team_a, team_b, score_a, score_b, status, winner, "
        "match_detail_id FROM schedule_all")]
    regular = [r for r in sched if not _is_playoff_schedule(r)]
    playoffs = [r for r in sched if _is_playoff_schedule(r)]
    completed = [r for r in regular if str(r.get("status")) == "completed"]
    n_sched = len(sched)
    if n_sched != exp_regular + exp_playoffs:
        problems.append(f"schedule_all has {n_sched} rows, expected {exp_regular + exp_playoffs}")
    if len(regular) != exp_regular:
        problems.append(f"regular schedule has {len(regular)} rows, expected {exp_regular}")
    if len(playoffs) != exp_playoffs:
        problems.append(f"playoff schedule has {len(playoffs)} rows, expected {exp_playoffs}")
    phase = str(season.get("regularSeasonStatus") or "in-progress")
    if phase == "final" and len(completed) != exp_regular:
        problems.append(
            f"final phase requires {exp_regular} completed regular fixtures, "
            f"found {len(completed)}")
    if phase not in ("in-progress", "final"):
        problems.append(f"unknown regularSeasonStatus {phase!r}")
    if con.execute("SELECT COUNT(*) FROM standings").fetchone()[0] <= 0:
        problems.append("standings empty")
    if not isinstance(playoff_payload, dict):
        problems.append("playoffs payload malformed")
    if fails:
        problems.append(f"{len(fails)} match-detail fetches failed: "
                        + ",".join(str(d) for d, _ in fails[:5]))

    # Every completed regular fixture must have a numeric detail id, a
    # terminal score, and that detail must be present in matches.
    detail_ids = {}
    expected_games = 0
    for r in completed:
        sid = r.get("schedule_id")
        did = str(r.get("match_detail_id") or "")
        if not re.match(r"^\d+$", did):
            problems.append(f"completed fixture {sid} has no numeric match detail id")
            continue
        if did in detail_ids:
            problems.append(f"duplicate match detail id {did} in completed schedule")
            continue
        detail_ids[did] = r
        sa, sb = r.get("score_a"), r.get("score_b")
        try:
            sa, sb = int(sa), int(sb)
        except (TypeError, ValueError):
            problems.append(f"completed fixture {sid} has non-numeric score {sa!r}-{sb!r}")
            continue
        if sa == sb or not ((sa == 2 and sb in (0, 1)) or (sb == 2 and sa in (0, 1))):
            problems.append(f"completed fixture {sid} has non-terminal BO3 score {sa}-{sb}")
            continue
        expected_games += sa + sb

    match_rows = {str(r[0]): dict(zip(
        ("match_detail_id", "team_a", "team_b", "score_a", "score_b", "status", "winner"), r))
        for r in con.execute("SELECT match_detail_id, team_a, team_b, score_a, score_b, status, winner FROM matches")}
    for did, detail in match_rows.items():
        expected_winner = winner_from_detail_score(detail.get("score_a"), detail.get("score_b"))
        if expected_winner is None:
            problems.append(f"detail {did} has invalid/tied match score; winner cannot be derived")
        elif detail.get("winner") != expected_winner:
            problems.append(
                f"detail {did} winner {detail.get('winner')!r} disagrees with detail-order score "
                f"{detail.get('score_a')}-{detail.get('score_b')} (expected {expected_winner})"
            )
    if set(match_rows) != set(detail_ids):
        missing = sorted(set(detail_ids) - set(match_rows))
        extra = sorted(set(match_rows) - set(detail_ids))
        if missing:
            problems.append(f"matches missing completed detail ids: {','.join(missing[:8])}")
        if extra:
            problems.append(f"matches contains ids not in completed schedule: {','.join(extra[:8])}")
    for did, sched_row in detail_ids.items():
        m = match_rows.get(did)
        if not m:
            continue
        same_order = (canon(m.get("team_a")) == canon(sched_row.get("team_a")) and
                      canon(m.get("team_b")) == canon(sched_row.get("team_b")))
        flipped = (canon(m.get("team_a")) == canon(sched_row.get("team_b")) and
                   canon(m.get("team_b")) == canon(sched_row.get("team_a")))
        try:
            if same_order:
                same_score = (int(m.get("score_a")) == int(sched_row.get("score_a")) and
                              int(m.get("score_b")) == int(sched_row.get("score_b")))
            elif flipped:
                same_score = (int(m.get("score_a")) == int(sched_row.get("score_b")) and
                              int(m.get("score_b")) == int(sched_row.get("score_a")))
            else:
                same_score = False
        except (TypeError, ValueError):
            same_score = False
        if not same_score:
            problems.append(f"detail {did} teams/score do not match schedule "
                            f"{m.get('team_a')} {m.get('score_a')}-{m.get('score_b')} {m.get('team_b')} vs "
                            f"{sched_row.get('team_a')} {sched_row.get('score_a')}-{sched_row.get('score_b')} "
                            f"{sched_row.get('team_b')}")

    n_games = con.execute("SELECT COUNT(*) FROM games").fetchone()[0]
    if n_games != expected_games:
        problems.append(f"games has {n_games} rows, expected {expected_games} from completed series scores")
    bad_winner = con.execute(
        "SELECT COUNT(*) FROM games WHERE winner NOT IN ('team_a','team_b')").fetchone()[0]
    if bad_winner:
        problems.append(f"{bad_winner} games have no valid winner")
    for did, sched_row in detail_ids.items():
        expected = int(sched_row["score_a"]) + int(sched_row["score_b"])
        got = con.execute("SELECT COUNT(*) FROM games WHERE match_detail_id=?", (did,)).fetchone()[0]
        if got != expected:
            problems.append(f"detail {did} has {got} games, expected {expected}")
        game_nos = {r[0] for r in con.execute(
            "SELECT game_no FROM games WHERE match_detail_id=?", (did,))}
        if game_nos != set(range(1, expected + 1)):
            problems.append(f"detail {did} game numbers are not 1..{expected}: {sorted(game_nos)}")
        wins = {canon(sched_row.get("team_a")): 0, canon(sched_row.get("team_b")): 0}
        for g_a, g_b, g_winner in con.execute(
                "SELECT team_a, team_b, winner FROM games WHERE match_detail_id=?", (did,)):
            win = canon(g_a) if g_winner == "team_a" else (
                canon(g_b) if g_winner == "team_b" else None)
            if win in wins:
                wins[win] += 1
        want_a = int(sched_row["score_a"])
        want_b = int(sched_row["score_b"])
        if (wins.get(canon(sched_row.get("team_a"))) != want_a or
                wins.get(canon(sched_row.get("team_b"))) != want_b):
            problems.append(
                f"detail {did} game winners do not match series score "
                f"{sched_row.get('score_a')}-{sched_row.get('score_b')}: {wins}")

    n_tg = con.execute("SELECT COUNT(*) FROM team_games").fetchone()[0]
    if n_tg != 2 * n_games:
        problems.append(f"team_games has {n_tg} rows, expected {2 * n_games}")
    bad_tg = con.execute(
        "SELECT COUNT(*) FROM (SELECT match_detail_id, game_no, COUNT(*) c, SUM(win) w "
        "FROM team_games GROUP BY 1,2 HAVING c<>2 OR w<>1)").fetchone()[0]
    if bad_tg:
        problems.append(f"{bad_tg} games do not have exactly two team rows with one winner")
    wrong_tg_teams = con.execute(
        "SELECT COUNT(*) FROM games g WHERE (SELECT COUNT(*) FROM team_games t "
        "WHERE t.match_detail_id=g.match_detail_id AND t.game_no=g.game_no "
        "AND t.team IN (g.team_a, g.team_b)) <> 2").fetchone()[0]
    if wrong_tg_teams:
        problems.append(f"{wrong_tg_teams} games have team-game rows for the wrong teams")
    bad_players = con.execute(
        "SELECT COUNT(*) FROM (SELECT match_detail_id, game_no, COUNT(*) c "
        "FROM game_players GROUP BY 1,2 HAVING c<>10)").fetchone()[0]
    if bad_players:
        problems.append(f"{bad_players} games do not have exactly ten player rows")
    if con.execute("SELECT COUNT(*) FROM game_players").fetchone()[0] <= 0:
        problems.append("game_players empty")

    # Reconcile both records with the published standings, not with a
    # separately stored aggregate. This is the cross-view contract.
    official = {canon(r[0]): dict(zip(
        ("team_slug", "match_win", "match_lose", "game_win", "game_lose"), r))
        for r in con.execute(
            "SELECT team_slug, match_win, match_lose, game_win, game_lose FROM standings")}
    derived = {}
    def rec(team):
        return derived.setdefault(canon(team), {
            "match_win": 0, "match_lose": 0, "game_win": 0, "game_lose": 0})
    for r in completed:
        a, b = canon(r.get("team_a")), canon(r.get("team_b"))
        if a == b or a not in official or b not in official:
            problems.append(f"completed fixture {r.get('schedule_id')} has unknown/self teams")
            continue
        winner = canon(r.get("team_a")) if _score_winner(r) == r.get("team_a") else canon(r.get("team_b"))
        rec(a)["match_win" if winner == a else "match_lose"] += 1
        rec(b)["match_win" if winner == b else "match_lose"] += 1
    # Sides can swap between games in the same series, so use each game's own
    # team_a/team_b orientation rather than a per-match orientation cache.
    for r in con.execute("SELECT team_a, team_b, winner FROM games"):
        a, b = canon(r[0]), canon(r[1])
        winner = r[2]
        if winner not in ("team_a", "team_b"):
            continue
        win = a if winner == "team_a" else b
        lose = b if win == a else a
        if win not in official or lose not in official:
            continue
        rec(win)["game_win"] += 1
        rec(lose)["game_lose"] += 1
    if set(official) != set(derived):
        problems.append(f"standings/derived team sets differ: official={sorted(official)} derived={sorted(derived)}")
    total_match_wins = sum(int(v.get("match_win") or 0) for v in official.values())
    total_game_wins = sum(int(v.get("game_win") or 0) for v in official.values())
    if total_match_wins != len(completed):
        problems.append(f"standings match wins {total_match_wins} != completed matches {len(completed)}")
    if total_game_wins != n_games:
        problems.append(f"standings game wins {total_game_wins} != games {n_games}")
    for team, o in official.items():
        d = derived.get(team)
        if not d:
            continue
        for key in ("match_win", "match_lose", "game_win", "game_lose"):
            if int(o.get(key) or 0) != d[key]:
                problems.append(f"{team} {key} official {o.get(key)} != derived {d[key]}")
    return problems


TABLES = ["matches", "schedule_all", "games", "game_players", "game_bans",
          "game_picks", "team_games", "team_season_stats", "player_season_stats",
          "hero_stats", "standings"]

# Canonical schema. CREATE IF NOT EXISTS so a standalone aggregate refresh can
# run the same definition against an already-built database.
SCHEMA = """
CREATE TABLE IF NOT EXISTS matches(
  match_detail_id TEXT PRIMARY KEY,
  schedule_id TEXT, team_a TEXT, team_b TEXT,
  score_a INTEGER, score_b INTEGER,
  date TEXT, iso_date TEXT, iso_datetime TEXT,
  status TEXT, winner TEXT, vod_url TEXT, match_detail_url TEXT,
  liq_mvp TEXT
);
CREATE TABLE IF NOT EXISTS games(
  match_detail_id TEXT, game_no INTEGER,
  team_a TEXT, team_b TEXT,
  team_a_kills INTEGER, team_b_kills INTEGER,
  winner TEXT, duration_str TEXT, duration_sec INTEGER,
  team_a_side TEXT, team_b_side TEXT, vod_url TEXT,
  map_mode TEXT,
  PRIMARY KEY(match_detail_id, game_no)
);
CREATE TABLE IF NOT EXISTS game_players(
  match_detail_id TEXT, game_no INTEGER,
  team TEXT, player TEXT, lane TEXT, hero TEXT,
  kills INTEGER, deaths INTEGER, assists INTEGER,
  kda REAL, gold INTEGER, gold_per_min REAL,
  hero_damage INTEGER, damage_taken INTEGER, tower_damage INTEGER,
  emblem TEXT, items_json TEXT, talents_json TEXT,
  lane_source TEXT,
  PRIMARY KEY(match_detail_id, game_no, team, player, hero)
);
CREATE TABLE IF NOT EXISTS game_bans(
  match_detail_id TEXT, game_no INTEGER, side TEXT, hero TEXT,
  ban_order INTEGER
);
CREATE TABLE IF NOT EXISTS game_picks(
  match_detail_id TEXT, game_no INTEGER, team TEXT, side TEXT,
  slot INTEGER, lane TEXT, hero TEXT, player TEXT,
  PRIMARY KEY(match_detail_id, game_no, team, slot)
);
CREATE TABLE IF NOT EXISTS team_games(
  match_detail_id TEXT, game_no INTEGER, team TEXT, opponent TEXT,
  players INTEGER, kills INTEGER, deaths INTEGER, assists INTEGER,
  gold INTEGER, hero_damage INTEGER, damage_taken INTEGER, tower_damage INTEGER,
  kda REAL, win INTEGER, map_mode TEXT, duration_sec INTEGER,
  PRIMARY KEY(match_detail_id, game_no, team)
);
CREATE TABLE IF NOT EXISTS team_season_stats(
  team TEXT PRIMARY KEY, games INTEGER, wins INTEGER, losses INTEGER,
  kills INTEGER, deaths INTEGER, assists INTEGER, gold INTEGER,
  hero_damage INTEGER, damage_taken INTEGER, tower_damage INTEGER,
  kda REAL, win_rate REAL, avg_gold REAL, avg_duration_sec REAL,
  team_name TEXT, team_slug TEXT
);
CREATE TABLE IF NOT EXISTS player_season_stats(
  player TEXT PRIMARY KEY, team TEXT, team_slug TEXT, lane TEXT,
  total_games INTEGER, total_kills INTEGER, avg_kills REAL,
  total_deaths INTEGER, avg_deaths REAL, total_assists INTEGER, avg_assists REAL,
  avg_kda REAL, kill_participation TEXT
);
CREATE TABLE IF NOT EXISTS standings(
  rank INTEGER PRIMARY KEY, team_name TEXT, team_slug TEXT,
  match_point INTEGER, match_win INTEGER, match_lose INTEGER,
  game_win INTEGER, game_lose INTEGER, net_game_win INTEGER
);
CREATE TABLE IF NOT EXISTS hero_stats(
  hero TEXT PRIMARY KEY, hero_image TEXT,
  pick INTEGER, ban INTEGER, win INTEGER, win_rate TEXT
);
CREATE TABLE IF NOT EXISTS schedule_all(
  schedule_id TEXT PRIMARY KEY, team_a TEXT, team_b TEXT,
  score_a INTEGER, score_b INTEGER,
  date TEXT, iso_date TEXT, iso_datetime TEXT,
  status TEXT, winner TEXT, vod_url TEXT,
  match_detail_id TEXT, match_detail_url TEXT
);
"""


def rebuild_team_aggregates(con):
    """Derive team-level facts from player rows and game results.

    Idempotent: clears and rebuilds both tables. One definition is shared by
    the ETL and tools/aggregate_teams.py so refreshes cannot drift.
    """
    con.execute("DELETE FROM team_games")
    con.execute("""
        INSERT INTO team_games
        SELECT p.match_detail_id, p.game_no, p.team,
               CASE WHEN p.team=g.team_a THEN g.team_b ELSE g.team_a END,
               p.players, p.kills, p.deaths, p.assists, p.gold,
               p.hero_damage, p.damage_taken, p.tower_damage, p.kda,
               CASE WHEN (g.winner='team_a' AND p.team=g.team_a)
                          OR (g.winner='team_b' AND p.team=g.team_b)
                    THEN 1 ELSE 0 END,
               g.map_mode, g.duration_sec
        FROM (
            SELECT match_detail_id, game_no, team, COUNT(*) AS players,
                   COALESCE(SUM(kills),0) AS kills,
                   COALESCE(SUM(deaths),0) AS deaths,
                   COALESCE(SUM(assists),0) AS assists,
                   COALESCE(SUM(gold),0) AS gold,
                   COALESCE(SUM(hero_damage),0) AS hero_damage,
                   COALESCE(SUM(damage_taken),0) AS damage_taken,
                   COALESCE(SUM(tower_damage),0) AS tower_damage,
                   ROUND((COALESCE(SUM(kills),0)+COALESCE(SUM(assists),0))*1.0
                         / NULLIF(SUM(deaths),0), 3) AS kda
            FROM game_players GROUP BY match_detail_id, game_no, team
        ) p
        JOIN games g ON g.match_detail_id=p.match_detail_id AND g.game_no=p.game_no
    """)
    con.execute("DELETE FROM team_season_stats")
    con.execute("""
        INSERT INTO team_season_stats(
            team, games, wins, losses, kills, deaths, assists, gold,
            hero_damage, damage_taken, tower_damage, kda, win_rate,
            avg_gold, avg_duration_sec)
        SELECT team, COUNT(*), SUM(win),
               SUM(CASE WHEN win=0 THEN 1 ELSE 0 END),
               SUM(kills), SUM(deaths), SUM(assists), SUM(gold),
               SUM(hero_damage), SUM(damage_taken), SUM(tower_damage),
               ROUND((SUM(kills)+SUM(assists))*1.0/NULLIF(SUM(deaths),0), 3),
               ROUND(SUM(win)*1.0/COUNT(*), 4),
               ROUND(AVG(gold), 1), ROUND(AVG(duration_sec), 1)
        FROM team_games GROUP BY team
    """)
    # Slugs are the stable join key to standings (team codes use the same
    # letters, while standings display names are spelled out).
    for name, slug in con.execute("SELECT team_name, team_slug FROM standings"):
        con.execute("UPDATE team_season_stats SET team_name=?, team_slug=? WHERE team=?",
                    (name, slug, (slug or "").upper()))
    con.commit()


def publish_build(staging, db_path, csv_dir, playoffs_path):
    """Atomically publish a validated staging build.

    staging holds <db name>, csv/<tbl>.csv and <playoffs name>. Every target
    is replaced with os.replace (same filesystem) and staging is removed.
    Raises on any failure without touching remaining targets.
    """
    staging = Path(staging)
    os.replace(staging / Path(db_path).name, db_path)
    for tbl in TABLES:
        os.replace(staging / "csv" / f"{tbl}.csv", Path(csv_dir) / f"{tbl}.csv")
    os.replace(staging / Path(playoffs_path).name, playoffs_path)
    shutil.rmtree(staging, ignore_errors=True)


def main():
    global HUB, LIQ_API
    HUB = CFG["endpoints"]["hub"]
    LIQ_API = CFG["endpoints"]["liquipediaApi"]
    print("fetch mlbbhub lists...")
    matches = get_json(f"{HUB}/matches")
    standings = get_json(f"{HUB}/standings")
    player_stats = get_json(f"{HUB}/stats/players")
    hero_stats = get_json(f"{HUB}/stats/heroes")
    try:
        playoffs = get_json(f"{HUB}/playoffs")
    except Exception as e:
        print("playoffs fetch failed", e); playoffs = {}
    print(f"matches entries={len(matches)} standings={len(standings)} players={len(player_stats)}")

    print("fetch liquipedia regular season wikitext for MVP merge...")
    wt = get_liq_wikitext(LIQ_SEASON_PAGE)
    liq = parse_liq_matches(wt)
    print(f"liq series parsed={len(liq)}")

    # map detail_id -> liq MVP via pair-matched chronological attach (see attach_mvps).
    numeric = [m for m in matches if re.match(r"^\d+$", str(m.get("match_detail_id") or ""))]
    print(f"numeric detail matches={len(numeric)}")
    detail_ids = sorted(set(str(m["match_detail_id"]) for m in numeric), key=int)
    print("detail_ids:", detail_ids[:10], "...", detail_ids[-10:], f"total {len(detail_ids)}")

    # Build into staging: the live database, CSVs and playoffs.json are only
    # replaced after the integrity gate passes, so a failed build can never
    # destroy the last known-good dataset.
    if STAGING.exists():
        shutil.rmtree(STAGING)
    (STAGING / "csv").mkdir(parents=True)
    con = sqlite3.connect(STAGING / DB.name)
    cur = con.cursor()
    cur.executescript(SCHEMA)

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
            (canon_hero(h.get("hero")), h.get("hero_image"), h.get("pick"), h.get("ban"),
             h.get("win"), h.get("win_rate")))
    with open(STAGING / PLAYOFFS_JSON.name, "w", encoding="utf-8") as f:
        json.dump(playoffs, f, ensure_ascii=False)

    # MVP merge: pair-matched chronological attach (see attach_mvps).
    mvp_map = attach_mvps(numeric, liq)

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
             sched.get("iso_datetime"), sched.get("status"), winner_from_detail_score(d.get("score_a"), d.get("score_b")),
             sched.get("vod_url"), sched.get("match_detail_url"), mvp_map.get(str(did),"")))
        for g in d.get("games", []):
            dur = g.get("duration"); sec = parse_duration(dur)
            cur.execute("INSERT OR REPLACE INTO games VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (str(did), g.get("game"), g.get("team_a"), g.get("team_b"),
                 g.get("team_a_kills"), g.get("team_b_kills"), g.get("winner"),
                 dur, sec, g.get("team_a_side"), g.get("team_b_side"), g.get("vod_url"),
                 g.get("map_mode")))
            n_games += 1
            for side, bans in (("A", g.get("bans_a")), ("B", g.get("bans_b"))):
                # Exact duplicate bans are a known API defect (e.g. 1088 game 1
                # lists Nolan twice); dedupe on ingest, never in the UI.
                for b in clean_bans(bans):
                    cur.execute("INSERT INTO game_bans VALUES(?,?,?,?,?)",
                                (str(did), g.get("game"), side, canon_hero(b), None))
                    n_bans += 1
            for pl in (g.get("players") or []):
                gold = pl.get("gold") or 0
                gpm = round(gold/(sec/60), 1) if sec else None
                cur.execute("INSERT OR REPLACE INTO game_players VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (str(did), g.get("game"), pl.get("team"), pl.get("player"), pl.get("lane"),
                     canon_hero(pl.get("hero")),
                     pl.get("kill"), pl.get("death"), pl.get("assist"), pl.get("kda"), gold, gpm,
                     pl.get("hero_damage"), pl.get("damage_taken"), pl.get("tower_damage"),
                     pl.get("emblem"), json.dumps(pl.get("items") or []), json.dumps(pl.get("talents") or []),
                     pl.get("lane_source")))
                n_rows += 1
    con.commit()
    rebuild_team_aggregates(con)
    print(f"stored games={n_games} player_rows={n_rows} bans={n_bans} fails={fails}")
    print(f"team_games={cur.execute('SELECT COUNT(*) FROM team_games').fetchone()[0]} "
          f"team_season={cur.execute('SELECT COUNT(*) FROM team_season_stats').fetchone()[0]}")
    # also store upcoming (non-numeric / no detail) schedule rows
    upcoming = [m for m in matches if not re.match(r"^\d+$", str(m.get("match_detail_id") or ""))]
    print(f"upcoming/no-detail entries={len(upcoming)} (not in DB matches; see schedule API)")
    # quick audits
    for q in ["SELECT COUNT(*) FROM matches","SELECT COUNT(*) FROM schedule_all","SELECT COUNT(*) FROM games","SELECT COUNT(*) FROM game_players",
              "SELECT COUNT(DISTINCT player) FROM game_players","SELECT COUNT(*) FROM game_bans"]:
        print(q, cur.execute(q).fetchone()[0])
    print("sample:", cur.execute("SELECT match_detail_id,game_no,team,player,hero,kills,deaths,assists,kda,gold,gold_per_min FROM game_players LIMIT 3").fetchall())
    con.close()

    # CSV exports (into staging)
    import csv
    staging_csv = STAGING / "csv"
    con = sqlite3.connect(STAGING / DB.name)
    for tbl in TABLES:
        rows = con.execute(f"SELECT * FROM {tbl}").fetchall()
        cols = [d[0] for d in con.execute(f"SELECT * FROM {tbl} LIMIT 0").description]
        with open(staging_csv/f"{tbl}.csv","w",newline="",encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(cols); w.writerows(rows)
        print(f"csv {tbl}: {len(rows)} rows")
    con.close()

    # Integrity gate: publish only a complete, validated build.
    gate = sqlite3.connect(STAGING / DB.name)
    problems = validate_build(gate, fails, playoffs, CFG)
    gate.close()
    if problems:
        print("BUILD VALIDATION FAILED — keeping last known-good dataset:")
        for p in problems:
            print(" -", p)
        shutil.rmtree(STAGING, ignore_errors=True)
        raise SystemExit(1)
    CSVDIR.mkdir(exist_ok=True)
    publish_build(STAGING, DB, CSVDIR, PLAYOFFS_JSON)
    print("done:", DB)
    print("note: picks/lanes/map_mode come from Liquipedia; run tools/etl.py for a complete build")

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        print(f"BUILD FAILED ({e}) — last known-good dataset retained")
        raise SystemExit(1)
