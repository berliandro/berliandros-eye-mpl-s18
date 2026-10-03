# MPL ID Season 18 — Berliandro's Eye

Self-contained single-file webapps (no build step, work from `file://` or any static server):

- `mpl_id_s18_dark.html` — current app: frosted-glass dark Pinterest board (Overview / Players / Matches / Stats), per-game scoreboards with local item/emblem/hero photos, live-data Refresh.
- `archive/` — retired legacy light-theme version (see above).
- `assets/` — all local images (items, heroes, emblems, runes, teams, players) + `manifest.json`.
- `archive/` — retired legacy light-theme `mpl_id_s18_pinboard.html` + `gen_webapp.py` (kept for revert only, not used).
- `data/` — `mpl_id_s18.db` (SQLite), `csv/` exports, `lanes.json` (Liquipedia roles).
- `tools/` — `build_s18_db.py` (API → DB + CSV), `gen_dark.py` (builds the dark app from `tools/templates/` + `data/` + `assets/manifest.json`), `check_parity.py` (regen parity gate).
- `docs/` — tournament research notes.

Run: open the HTML file, or serve the folder (`python -m http.server`) for full speed.
Regenerate: `python tools/gen_dark.py` (needs `data/` + `assets/manifest.json`).
Parity check: `python tools/check_parity.py` (must print PASS).
Edit UI in `tools/templates/` (`style.css`, `app.js`, `doc.html`), never by hand in the built HTML.
