# Overdrive contract — Berliandro's Eye

Written before `/impeccable overdrive` replaces the visual world, look, hierarchy, IA and
navigation. This file is the brief: everything here is either an invariant the new world must carry
or a defect it must not reproduce. Source: whole-app critique, 22/40, dual-agent, 2026-11-15.

## 1. Invariants — must survive any redesign

- **Never fabricate.** A missing value renders as `—` with its reason. Heuristic values are labelled
  (game MVP is highest-KDA on the winning team).
- **Sample size travels with the number.** Every rate shows `n`, and 95% Wilson or bootstrap
  intervals where they exist. Rates under five games are dimmed, never hidden.
- **Source ceilings are permanent:** no per-game objective counts, no gold/damage timelines, no
  draft pick order, no MANIAC/SAVAGE, no physical/magic/true split. The new world must not invent a
  chart shape that implies any of them exists.
- **Season-agnostic core.** Season differences live in `data/`, never in branches.
- **One committed dataset.** 72 series, 174 games, nine teams, 61 players; the build is gated by
  `tools/verify.py` (28 suites) plus a regeneration parity check.
- **Offline-first single artifact.** ~1.6 MB, all assets local, no runtime dependency.
- **390 px floor.** Every surface works at 390 before it ships.

## 2. Defects the new world must not inherit

Ordered by how easily a reskin hides them. Each is measured, not suspected.

1. **No hierarchy of what leads.** Every view is a stack of equally weighted slabs with nothing
   between the 9.5 px label and the 24 px number. The new world must name, per surface, the one
   thing that leads and the one number that answers its question.
2. **Matches buries matches.** First fixture at y=1117 on a 900 px screen, behind a phase card and
   two panels duplicated from Overview and Analytics.
3. **Print/PDF is blank.** Black text on hard-coded dark panels; four of seven Prep panels at
   `opacity: 0` under print because the scroll reveal never fired. The coach's export must be a
   first-class render of the same markup.
4. **Dialogs are inconsistent.** No body scroll lock (the page scrolled 900 px behind the
   scoreboard), no backdrop close, a focus trap that skips `a[href]` (the VOD link), and a command
   palette that opens with 0 rows and has no arrow-key model.
5. **Motion ignores the user.** The 600 ms card entrance keeps animating under
   `prefers-reduced-motion: reduce`; chips have no hover state at all; rows and primary buttons
   change instantly with no transition.
6. **Accessibility is bolted on.** No `h1` on five of seven views; a card's accessible name is
   "Open <name> profile" with impact, win rate and the chart missing; sub-tabs are `aria-pressed`
   buttons without tab semantics; the mobile filter sheet has no dialog role or focus trap.
7. **Controls lie.** `/` is printed in the search field and does nothing; browser Back exits the
   app; the Filters pill on Analytics opens a sheet with no filters; filters are absent from the
   URL.
8. **Dead weight.** MANIAC/SAVAGE columns that can never fill, `.pl-strip`/`.pb`/`.pl-nums` CSS from
   the retired card, and two panel systems (10 px and 14 px) chosen by page rather than by role.

## 3. Colour — one owner, one exception

**Team crest owns colour.** Identity appears as a 2 px edge, a tinted ghost wordmark, or a ground
wash — never a filled block. Sampled from the logo and lightness-clamped
(`tools/derive_team_colors.py`); a team with no saturated hue takes the neutral hairline.

**Outcome is a shape, not a hue.** Win/loss is carried by a pill's form and label, not by green and
red alone.

**Exception — match side.** Inside any game or scoreboard context, blue and red stay as the side
signal, because side decides first pick and first pick has carried real advantage across the last
four seasons. Rules for it:

- Allowed only where a specific **game** is shown (scoreboard, game list, draft view, prep matchups).
- Rendered as a 2–3 px edge, a side badge, or a small labelled chip — never a glow, never a fill,
  never a gradient.
- Always paired with the word `Blue` or `Red` so it is not colour-only meaning.
- Never used for outcome, and never for team identity.

## 4. Navigation and IA — free to change

The rail/tab duality, the seven-view set and the URL grammar are all in scope. Whatever replaces
them must still: keep every view reachable in one action, keep shareable state in the URL, and give
browser Back the meaning a user expects.

## 5. First surface

Build the new world on the **player card and the player profile** first — they are the app's two
identity moments and where the current system takes its only real risk. The season front page
follows, because it carries the hierarchy decision for every other view.
