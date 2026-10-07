"""README screenshots — SHOOTING SPEC (do not change without user approval):
  canvas:        2880x1800 PNG (exact — verified from PNG header after capture)
  system zoom:   150%  (viewport 1920x1200 CSS @ device_scale_factor 1.5)
  website zoom:  125%  (body CSS zoom; combined content scale 1.875x)
  result:        high-resolution but zoomed-in, matching the reference photo
  readiness:     every shot waits for webfonts + ALL <img> complete
                 (no fixed sleeps before capture) so photos/icons are loaded
  tool:          headless system Chrome via Playwright (in-tool screenshots
                 cannot run here — no visible desktop window)
Usage: python tools/shots.py [--zoom]
  default: 2880x1800 CSS @ dsf 1 (native, spec-deviation — needs approval)
  --zoom:  the spec above (always use this for README)
Output: github/assets/*.png (01-overview, 02-players, 03-matches-list,
  04-matches-grid, 05-scoreboard, 06-player, 07-stats-mvp, 08-stats-heroes)
"""
import struct
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent.parent
OUT = ROOT / 'github' / 'assets'
OUT.mkdir(parents=True, exist_ok=True)
URL = (ROOT / 'mpl_id_s18_dark.html').as_uri()
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
ZOOM = '--zoom' in sys.argv

VP = {'width': 1920, 'height': 1200} if ZOOM else {'width': 2880, 'height': 1800}
DSF = 1.5 if ZOOM else 1.0

SHOTS = []


def ready(page, timeout=25000):
    """Block until webfonts settle and every IN-VIEWPORT image finished
    loading (below-fold lazy images are excluded — they load on scroll)."""
    try:
        page.wait_for_function("document.fonts.status === 'loaded'",
                               timeout=10000)
    except Exception as e:
        print('fonts wait skipped:', str(e)[:60])
    page.wait_for_function(
        "Array.from(document.images)"
        ".filter(i => { const r = i.getBoundingClientRect();"
        " return r.bottom > 0 && r.top < window.innerHeight; })"
        ".every(i => i.complete)",
        timeout=timeout)
    page.wait_for_timeout(400)


def shot(page, name):
    ready(page)
    p = OUT / name
    page.screenshot(path=str(p))
    SHOTS.append(name)
    print('shot', name)


with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=CHROME,
                           args=['--no-sandbox', '--force-device-scale-factor=1'])
    ctx = b.new_context(viewport=VP, device_scale_factor=DSF)
    pg = ctx.new_page()
    pg.goto(URL, wait_until='networkidle')
    if ZOOM:
        pg.evaluate('document.body.style.zoom = "125%"')
    ready(pg)

    shot(pg, '01-overview.png')

    pg.click('[data-view="players"]')
    shot(pg, '02-players.png')

    pg.click('[data-view="matches"]')
    try:
        pg.click('#layList')
    except Exception as e:
        print('layList:', str(e)[:80])
    shot(pg, '03-matches-list.png')

    try:
        pg.click('#layGrid')
    except Exception as e:
        print('layGrid:', str(e)[:80])
    shot(pg, '04-matches-grid.png')

    # opened scoreboard: first completed match card
    # (wait for the live-data dialog body: player rows present)
    btn = pg.query_selector('.mpin [data-m]')
    if btn:
        btn.click()
        pg.wait_for_function(
            "document.querySelectorAll('#db .sb-p').length > 0",
            timeout=30000)
        shot(pg, '05-scoreboard.png')
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(400)

    # opened player card
    pg.click('[data-view="players"]')
    prow = pg.query_selector('[data-p]')
    if prow:
        prow.click()
        pg.wait_for_function(
            "document.querySelectorAll('#db table tr').length > 1",
            timeout=15000)
        shot(pg, '06-player.png')
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(400)

    # stats revamp: MVP race + heroes table
    pg.click('[data-view="stats"]')
    shot(pg, '07-stats-mvp.png')
    try:
        pg.click('[data-stat="heroes"]')
    except Exception as e:
        print('heroes subtab:', str(e)[:80])
    shot(pg, '08-stats-heroes.png')

    b.close()
for n in SHOTS:
    w, h = struct.unpack('>II', (OUT / n).read_bytes()[16:24])
    assert (w, h) == (2880, 1800), f'{n} is {w}x{h}, spec violated'
    print('ok 2880x1800', n)
print('done:', SHOTS)
