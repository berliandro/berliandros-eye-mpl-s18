# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary visitors are MPL Indonesia fans and analysts who arrive to browse a season of data —
a favourite player, a team's season, a match scoreboard, the hero meta — and read what
happened. The same surface serves a second, deeper user: a coach or team staffer who needs a
one-page series prep report against a specific opponent (rating, form, likely picks and bans,
weak and strong maps, lane matchups) in under ten minutes.

Confirmed 2026-11-15: both audiences, with the fan arriving first. Success for both is
comprehension — a fan finds an answer quickly, and a coach can turn the same numbers into a
decision.

## Product Purpose

Berliandro's Eye is the deepest public record of MPL Indonesia that answers *why*, not just
*who won*: draft patterns, player edges, team tendencies and matchup weaknesses a head coach
can act on, readable at fan level and one click from the evidence.

The project counts itself complete when:

- onboarding a new season is config and data only, with no application-code fork;
- every displayed rate carries a sample size and a confidence band;
- a coach can produce a series prep sheet for an opponent in under ten minutes;
- at least six published analyses exist that Liquipedia, id-mpl and mlbbhub do not publish;
- one command rebuilds any season from committed sources, with CI proving it.

## Positioning

The mechanism is a reconciled, committed relational dataset with metrics derived from it under
visible uncertainty. Per game the project holds ten player rows (kills, deaths, assists, gold,
GPM, damage, damage taken, tower damage, emblem, six items, three talents), ten ordered bans,
five picks per side with a lane and a lane-source tag, map mode and a VOD link — cross-checked
against standings, schedule and Liquipedia drafts before publish.

Competing public sources publish tables of what happened. This project publishes normalized
comparisons (role percentiles, shrinkage toward lane and role means, opponent- and
hero-adjusted residuals, Bradley-Terry team ratings with bootstrap intervals) and states the
sample behind each one.

## Operating Context

- A season is nine weeks of regular-season play plus playoffs. Season 18 covers 72 completed
  series and 174 games across nine teams: 61 players with completed game rows, 93 heroes picked
  or banned, 114 item identifiers.
- The app ships as one HTML file plus the committed `assets/` folder (double-click both, or serve the folder over HTTP), and
  refreshes from the mlbbhub API on demand; the committed snapshot renders instantly offline.
- Builds run from committed SQLite/CSV through the Python tools in `tools/`. The artifact is
  generated from `tools/templates/{doc.html,style.css,app.js}` by `tools/gen_dark.py`, and
  `python tools/verify.py` gates it (18 verification suites plus a regeneration parity check).
- Collection is manual, never scheduled: one ETL run makes roughly 70 sequential requests with
  identifying user agents; one in-app refresh makes about 60 detail requests at 6-way
  concurrency.
- A separate transcript and coaching layer lives in `analysis/`: broadcast transcripts are
  imported with SHA-256 manifests, verified, aligned to series and games, and published as
  evidence records and coaching briefs. Raw transcripts and captured frames stay local and
  Git-ignored.
- CI runs the build and `tools/verify.py` on pushes to `main` and pull requests targeting it.

## Capabilities and Constraints

Views: Overview (season front page: latest result, standings, MVP race, pending playoffs),
Teams (nine-club league board plus a season dossier per club), Players (grid and list), Player
profile (full page), Matches (fixtures and scoreboard, list and grid, regular and playoffs, bracket
preview), Stats (series-MVP race, hero dashboard), Analytics (player impact and draft) and Prep
(opponent scouting report). Cross-cutting: drill-down dialogs for hero, item, emblem,
talent, opponent and game; `Ctrl/⌘K` search; URL-permalink state; sortable columns; CSV and
print/PDF export; versioned `localStorage` cache; live refresh that merges per match and never
partially overwrites good records.

Source ceilings to design around rather than paper over:

- no per-game Lord/Turtle/Tower counts, no gold or damage timelines, no draft pick order, no
  MANIAC/SAVAGE data, no physical/magic/true damage split;
- game MVP is a heuristic (highest KDA on the winning team) because the API exposes none; series
  MVP comes from Liquipedia;
- Season 18 keeps the `legacy` repository layout; a new season is added through
  `data/registry.json` plus a season directory, not code branches.

Operating constraints:

- The project is unofficial and non-commercial. It calls public JSON and MediaWiki endpoints
  only on manual invocation with identifying user agents; robots.txt and terms-of-service
  compliance are not claimed.
- The project has a bus factor of one; tests, reproducible builds and documentation are what keep
  it alive.

Open decisions recorded 2026-11-15:

- The single-file self-contained artifact and the current presentation of evidence are the
  present implementation, not binding constraints. Either may be reconsidered.
- GitHub Pages publishes `mpl_id_s18_dark.html` plus `assets/` from `main` through
  `.github/workflows/pages.yml`; the deployed site is the same embedded snapshot, with artwork on
  relative paths, and the manual Refresh still calls the public API.
- Visual proof for the coaching layer is unresolved (0 same-frame `00:00` boundaries), so
  gameplay observations remain text-only for now.

## Brand Commitments

- Name: **Berliandro's Eye**, or **Berliandro's Eye — MPL Indonesia Season 18** when the season
  matters. Repository: `berliandros-eye-mpl-s18`.
- Explicitly unofficial: no claimed affiliation with Moonton, MPL or any team, and no
  replacement for the official broadcast or the official MPL site.
- Voice in the existing product and docs is numeric and self-limiting: claims are scoped
  ("descriptive proxy, not causal"), absolutes are avoided, and an unavailable number is shown
  as `–` with its reason rather than estimated.

## Evidence on Hand

Committed and verified:

- Database: 72 matches, 174 games, 1,740 player rows, 1,740 picks, 1,738 ban rows with order,
  348 team-game rows, 9 team season aggregates, 133 hero stat rows — reconciled against
  standings and Liquipedia, with exceptions listed in `data/seasons/s18/quality.json`.
- Provenance: `data/seasons/s18/meta.json` records schema version, sources, row counts and build
  commit; the parity gate proves the committed artifact matches a fresh build.
- Analysis: 27/27 sources validated, 72/72 match reports with database evidence, 27
  transcript-covered series (24 complete, 3 partial), 45 database-only series, 313 accepted
  observations, nine team briefs and one head-coach brief under `analysis/`.
- Screenshots: eight 2880×1800 captures in `github/assets/`, produced by `tools/shots.py` under a
  fixed spec (system zoom 150%, site zoom 125%).
- Raw broadcast transcripts, captured frames and provenance sidecars exist locally but are
  Git-ignored, so they are not reproducible from a clean clone.

Absences future work must not fabricate: per-game objective counts, gold and damage timelines,
draft pick order, MANIAC/SAVAGE, damage-type splits, and verified same-frame visual proof for
gameplay claims.

## Product Principles

1. **Never fabricate.** A missing number renders as `–` with its reason; heuristics are labelled
   as heuristics, never as official measurements.
2. **Sample size travels with the number.** Every rate shows `n` and, where it exists, a 95%
   Wilson or bootstrap interval. Rates under five games are de-emphasised, never hidden and never
   headlined.
3. **Adjusted beats raw.** Compare inside a lane, against opponent strength and the hero
   baseline, before ranking anyone.
4. **Explain it in the product.** Every derived metric carries its definition, formula and
   caveats where the number appears, not only in code comments.
5. **Season-agnostic and provenance-first.** Season differences live in data, and every build
   records sources, counts, timestamp and a content hash.

## Accessibility & Inclusion

Current baseline: visible focus, a skip link, nav landmarks with `aria-current`, a tablist/tabpanel model with roving tabindex, a focus trap
in dialogs, a sticky first column and 34 px controls on mobile, a print stylesheet, and
`aria-live` refresh status. The stated target goes further: contrast of at least 4.5:1, 44 px tap
targets on touch, and full keyboard operation as a requirement rather than a nicety.
