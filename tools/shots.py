"""README screenshots at 2880x1800 using system Chrome (headless).
Usage: python tools/shots.py
Output: github/assets/*.png
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent.parent
OUT = ROOT / 'github' / 'assets'
OUT.mkdir(parents=True, exist_ok=True)
URL = (ROOT / 'mpl_id_s18_dark.html').as_uri()
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

SHOTS = []


def shot(page, name):
    p = OUT / name
    page.screenshot(path=str(p))
    SHOTS.append(name)
    print('shot', name)


with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=CHROME,
                           args=['--no-sandbox', '--force-device-scale-factor=1'])
    pg = b.new_page(viewport={'width': 2880, 'height': 1800})
    pg.goto(URL, wait_until='networkidle')
    pg.wait_for_timeout(2500)

    shot(pg, '01-overview.png')

    pg.click('[data-view="players"]')
    pg.wait_for_timeout(1200)
    shot(pg, '02-players.png')

    pg.click('[data-view="matches"]')
    pg.wait_for_timeout(800)
    try:
        pg.click('#layList')
        pg.wait_for_timeout(800)
    except Exception as e:
        print('layList:', str(e)[:80])
    shot(pg, '03-matches-list.png')

    try:
        pg.click('#layGrid')
        pg.wait_for_timeout(800)
    except Exception as e:
        print('layGrid:', str(e)[:80])
    shot(pg, '04-matches-grid.png')

    # opened scoreboard: first completed match card
    btn = pg.query_selector('.mpin [data-m]')
    if btn:
        btn.click()
        pg.wait_for_timeout(1500)
        shot(pg, '05-scoreboard.png')
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(500)

    # opened player card
    pg.click('[data-view="players"]')
    pg.wait_for_timeout(800)
    prow = pg.query_selector('[data-p]')
    if prow:
        prow.click()
        pg.wait_for_timeout(1200)
        shot(pg, '06-player.png')

    b.close()
print('done:', SHOTS)
