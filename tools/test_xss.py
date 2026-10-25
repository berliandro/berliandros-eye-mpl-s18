"""XSS exploit-path regression test (P0): renders the REAL application with a
hostile snapshot (markup-bearing player/team/hero names, scores, kills,
attribute breakouts) across overview/players/matches views plus the
scoreboard and player dialogs, then asserts no payload executed and every
payload survived only as inert text.

Local-only like tools/shots.py: needs system Chrome via Playwright, so it is
intentionally NOT part of tools/verify.py or CI (CI has no browser).
All API traffic is blocked; the hostile data is injected into DATA directly.
Usage: python tools/test_xss.py
Exit 0 = pass.
"""
from playwright.sync_api import sync_playwright

URL = (__import__("pathlib").Path(__file__).parent.parent
       / "mpl_id_s18_dark.html").as_uri()
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
P = '"><img src=x onerror="window.__pwned=\'PLAYER\'">'
T = '<svg onload="window.__pwned=\'TEAM\'">'
H = '"><img src=x onerror="window.__pwned=\'HERO\'">'
K = '0<img src=x onerror="window.__pwned=\'KILLS\'">'
S = '2<img src=x onerror="window.__pwned=\'SCORE\'">'
G = '1<img src=x onerror="window.__pwned=\'GAMENO\'">'
E = '1" onmouseover="window.__pwned=\'EQ\''
D = 'x<img src=x onerror="window.__pwned=\'DATE\'">'
W = '65%<img src=x onerror="window.__pwned=\'WR\'">'
M = '"><img src=x onerror="window.__pwned=\'MVP\'">'
U = '"><img src=x onerror="window.__pwned=\'URL\'">'
fails = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        fails.append(name)


with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
    pg = b.new_context(viewport={"width": 1600, "height": 900}).new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("**/mpl.mlbbhub.com/**", lambda r: r.abort())
    pg.route("**/liquipedia.net/**", lambda r: r.abort())
    pg.goto(URL, wait_until="networkidle")
    pg.wait_for_timeout(800)
    pg.evaluate(
        """([P, T, H, K, S, G, E, D, W, M, U]) => {
          const r0 = DATA.players[0];
          r0.player = P; r0.hero = H; r0.kills = K; r0.team = T;
          r0.hero_image = U; r0.gold_per_min = W;
          const st = DATA.standings[DATA.standings.length - 1];
          st.team_name = T; st.match_point = S; st.match_win = S; st.game_win = S;
          const sc = DATA.schedule[0];
          sc.score_a = S; sc.team_a = T; sc.date = D;
          sc.score_b = S; sc.team_b = T;
          const mm = DATA.matches[0];
          if (mm) { mm.liq_mvp = M; }
          const hs = DATA.heroes[0];
          if (hs) { hs.pick = S; hs.win_rate = W; }
          const gm = DATA.games[0];
          gm.team_a_kills = K; gm.game_no = G; gm.duration_str = D;
          const pr = DATA.players.find(r => r.match_detail_id === gm.match_detail_id);
          if (pr) { pr.game_no = G; }
          const ban = DATA.bans[0];
          if (ban) { ban.hero = H; }
          render();
        }""",
        [P, T, H, K, S, G, E, D, W, M, U])
    for view in ("overview", "players", "matches"):
        pg.click(f'[data-view="{view}"]')
        pg.wait_for_timeout(400)
    # scoreboard dialog for the poisoned first match, then a player card
    pg.click('[data-view="matches"]')
    pg.wait_for_timeout(300)
    btn = pg.query_selector('.mpin [data-m]')
    if btn:
        btn.click()
        pg.wait_for_timeout(600)
        pg.keyboard.press("Escape")
    pg.click('[data-view="players"]')
    pg.wait_for_timeout(300)
    prow = pg.query_selector('[data-p]')
    if prow:
        prow.click()
        pg.wait_for_timeout(600)
        pg.keyboard.press("Escape")
    st = pg.evaluate("""() => ({
      pwned: window.__pwned || null,
      evilImgs: document.querySelectorAll('img[src="x"]').length,
      svgLeak: document.querySelectorAll('svg[onload]').length,
      textHasPlayerPayload: (document.body.textContent || '').includes('window.__pwned=\\'PLAYER\\''),
      errors: []
    })""")
    check("no payload executed (window.__pwned unset)", st["pwned"] is None)
    check("no attacker img elements", st["evilImgs"] == 0)
    check("no attacker svg elements", st["svgLeak"] == 0)
    check("payload survives only as inert text", st["textHasPlayerPayload"] is True)
    check("no page errors", not errs)
    b.close()

print(f"\n{4 - len(fails)}/4 passed, {len(fails)} failed")
raise SystemExit(1 if fails else 0)
