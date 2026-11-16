# Championship plate — visual record

Four captures of the season-final state that shipped with the championship
plate (`5f94e14`, refined by `6060f0d`).

- `plate-1440.png`, `plate-390.png` — the championship hero at desktop and phone width.
- `overview-1440.png`, `overview-390.png` — the full Overview in the committed
  snapshot, which is **not** a season final: these prove the fallback hero is
  unchanged when the grand final is still undecided.

Fixture note: the committed snapshot has the grand final as TBD, so the two
plate captures were produced by injecting a completed 4–2 TLID over NAVI final
in the live page only — six synthetic game rows, no data file edited. The
Overview captures use the committed snapshot unmodified.

Reproduce: `python tools/gen_dark.py`, then open `mpl_id_s18_dark.html` and inject
the final before `render()` (see `tools/test_season_final.js` for the derivation
cases the plate depends on).
