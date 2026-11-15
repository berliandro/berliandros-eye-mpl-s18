---
name: Berliandro's Eye — MPL ID Season 18
description: An instrument-panel data desk for MPL Indonesia, lit from above
colors:
  graphite: "#101211"
  plate: "#171a18"
  plate-high: "#1a1e1b"
  chalk: "#eef1ee"
  pewter: "#9aa29c"
  seam: "#2a2f2c"
  seam-lift: "#3a423c"
  signal-red: "#e60023"
  pitch-green: "#3ddc84"
typography:
  display:
    fontFamily: "Space Grotesk, Manrope, system-ui, sans-serif"
    fontSize: "clamp(50px, 7.4vw, 110px)"
    fontWeight: 700
    lineHeight: 0.84
    letterSpacing: "-0.038em"
  headline:
    fontFamily: "Space Grotesk, Manrope, system-ui, sans-serif"
    fontSize: "24px"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Space Grotesk, Manrope, system-ui, sans-serif"
    fontSize: "17px"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Manrope, 'SF Pro Display', 'Segoe UI Variable', system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: "Manrope, 'SF Pro Display', 'Segoe UI Variable', system-ui, sans-serif"
    fontSize: "11px"
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: "0.09em"
rounded:
  xs: "6px"
  sm: "8px"
  md: "10px"
  lg: "14px"
  xl: "16px"
  pill: "9999px"
spacing:
  xs: "8px"
  sm: "14px"
  md: "18px"
  lg: "24px"
components:
  nav-item:
    backgroundColor: "transparent"
    textColor: "{colors.pewter}"
    rounded: "{rounded.sm}"
    padding: "10px"
  nav-item-active:
    backgroundColor: "rgba(255,255,255,0.065)"
    textColor: "{colors.chalk}"
    rounded: "{rounded.sm}"
    padding: "10px"
  chip:
    backgroundColor: "transparent"
    textColor: "{colors.pewter}"
    rounded: "{rounded.pill}"
    padding: "3px 10px"
  button-primary:
    backgroundColor: "{colors.chalk}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.xs}"
    padding: "9px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.chalk}"
    rounded: "{rounded.xs}"
    padding: "8px 14px"
  card-player:
    backgroundColor: "{colors.plate}"
    textColor: "{colors.chalk}"
    rounded: "{rounded.md}"
    padding: "16px"
  input:
    backgroundColor: "{colors.plate}"
    textColor: "{colors.chalk}"
    rounded: "{rounded.xs}"
    padding: "9px 12px"
  teams-board:
    backgroundColor: "{colors.plate}"
    textColor: "{colors.chalk}"
    rounded: "{rounded.lg}"
    padding: "18px"
  club-dossier:
    backgroundColor: "{colors.plate}"
    textColor: "{colors.chalk}"
    rounded: "{rounded.lg}"
    padding: "24px 26px"
---

# Design System: Berliandro's Eye

## Overview

**Creative North Star: "The Instrument Panel"**

The app is a rack of instruments on a graphite desk, lit from above. Surfaces are plates, not cards:
each one carries a 1px seam, an inset highlight along its top edge so the light catches the lip, and a
9px corner tick at the bottom right, the way a machined panel marks its corners. Nothing floats.
Nothing glows. The only movement is the movement of data.

Two readers share one rack. A fan scans sixty-one players; a coach opens one and reads a season's
shape. The instruments answer both at different pressures: a card leads with one number, a profile is
allowed to be dense. Where they conflict, the fan's first five seconds win.

Colour is information or it is absent. Team crest owns identity, outcome is a shape rather than a hue,
and blue/red appears only inside a game context where side decides first pick.

**Key Characteristics:**
- Graphite ground, chalk type, seam hairlines; plates lifted by an inset highlight, never a shadow.
- One headline figure per card at 22–24px; every other mark is 12px or smaller.
- Charts draw their 50th percentile and say which direction is better.
- Mono is chrome — rail, tables, legends — never a card's voice.

## Colors

Cool graphite, one signal hue, and a generated family of crest accents.

### Primary
- **Signal Red** (#e60023): the eye in the mark, the active rail tab, and loss. Never a fill, never a
  gradient, never more than a 2px rule or a status pill.
- **Pitch Green** (#3ddc84): wins only — result pills, and nothing else.

### Secondary
- **Crest Accents** (generated): one per team, sampled from the committed logo by
  `tools/derive_team_colors.py` and clamped to L 0.52–0.66 / S 0.55–0.88. NAVI `#f0e119`,
  TLID `#1a6cef`, EVOS `#4182c8`, BTR `#f01919`, RRQ `#f2aa36`, DEWA `#e6bb62`, AE `#e62336`,
  GEEK `#ef1c24`. ONIC derives nothing and takes a 42% chalk hairline instead of a guessed colour.

### Neutral
- **Graphite** (#101211): the ground, cooler than it was in the previous world.
- **Plate** (#171a18) → **Plate High** (#1a1e1b): the vertical gradient every panel carries.
- **Chalk** (#eef1ee): primary text and the primary button fill.
- **Pewter** (#9aa29c): secondary text, table headers, supporting figures.
- **Seam** (#2a2f2c): every hairline; **Seam Lift** (#3a423c) on hover.

### Named Rules
**The One Signal Rule.** Red is used on ≤2% of a screen: the active rail tab and a loss. Anywhere else
it must name a failure.

**The Crest Is Data Rule.** A team's colour is sampled from its logo and clamped, never chosen.

**The Side Is an Exception Rule.** Blue and red survive only where a specific game is shown, as a
2–3px edge or a labelled chip, always with the word Blue or Red. Never for outcome, never for identity.

## Typography

**Display Font:** Space Grotesk (Manrope, system-ui fallback)
**Body Font:** Manrope (SF Pro Display, Segoe UI Variable fallback)
**Label/Mono Font:** JetBrains Mono, for chrome only

**Character:** A geometric face for identity and figures, a humanist sans for everything read as a
sentence, and a mono kept to the rail, tables and legends where columns must line up.

### Hierarchy
- **Display** (700, clamp 50–110px, 0.84): the player IGN on the profile, capped at 58% width.
- **Headline** (700, 24px, 1.0): one figure per card — lane impact — and the season-plate score.
- **Title** (600, 17px, 1.3): card names; view titles at 22px in the shared head.
- **Body** (400, 12px, 1.45): supporting figures, notes, captions.
- **Label** (600, 11px, 0.09em, uppercase): card captions, axis labels, table headers.

### Named Rules
**The One Headline Rule.** A card carries exactly one figure at 22–24px; the second-largest mark is the
name.

**The Chrome-Only Mono Rule.** JetBrains Mono never appears inside a player card.

**The Tabular Rule.** Every number that can change column is tabular.

## Layout

A 1200px wrap on 1440, with a 220px rail (196px between 1180 and 1320) that owns navigation above
1180. The rail groups **Board** (Overview, Teams, Players, Matches) and **Analysis** (Stats,
Analytics, Prep), with mono counts on the first three. Below 1180 the header's tabs return; below 640
they form a 4×2 grid with Prep spanning the last two cells, so the current view is always on screen.
On Players and Matches the controls collapse into a bottom sheet behind a Filters pill; the pill is
not rendered on views with nothing to filter. A List/Grid toggle joins the header there, and Compact
hides the radar and tightens the card to about 200px.

Every view opens with a shared head: a 22px `h1` and a one-line lead, separated from the content by a
rule. Cards sit in an auto-fill grid at 250px minimum, four across at 1440. The player profile uses
1.55fr / 1fr; the season page uses the same split for standings and the race, with the playoff panel
stacked beneath.

Teams opens with a nine-row league board, then nine club dossiers. The top three in competition order
open; the other six collapse to their identity strip. The dossier uses 1.06fr / 1fr — roster and
tendencies in the left stack, draft, map record and head-to-head in the right.

Spacing runs 8 / 14 / 18 / 24. Inside a panel 18–20px; between panels 18px.

## Elevation & Depth

Depth is light, not shadow. A plate is a vertical gradient from Plate High to Plate with a 1px seam and
an inset top highlight; hover lifts the seam to Seam Lift. There are no drop shadows on panels — only
the portrait's `drop-shadow(0 26px 48px rgba(0,0,0,.62))` and the bracket's win glow.

**The Lit-From-Above Rule.** The ground carries one gradient from the top of the page and a faint crown
radial. Nothing is lit from below, from the side, or from a colour.

## Shapes

10px cards, 14px panels, 16px hero plates, 6–8px controls, full pills for status and filters, 8px
squares for portraits and crests. Corner ticks are 9px L-marks at 15% chalk. Circles are reserved for
emblems, runes and icons inside badges.

## Components

### Buttons
6px radius; primary is a chalk fill with graphite text; ghost carries a seam and lifts on hover; the
season plate uses a 9999px pill with a mono 9.5px uppercase label.

### Chips
Transparent, 1px seam, pewter text, 11px uppercase. Selected flips to chalk fill. On coarse pointers
each chip is a 44px target.

### Cards / Containers
Plate gradient, 1px seam, 10px radius, 16px padding, corner tick, crest edge on player cards only.

### Inputs / Fields
Plate fill, 1px seam, 6px radius. Form controls inherit the UI face — a UA default is a defect. Focus
is the global 2px chalk ring at 2px offset.

### Navigation
Rail at 220px with 10px mono section labels and a 40px row rhythm; the active row carries a raised
surface and a 2px bar that turns the current team's crest colour on a player page. Header is sticky,
opaque on mobile. The seven tabs sit in a 4×2 grid below 640 — Prep spans the last two cells — and the
active one is marked with a raised surface, chalk text and a 2px rule; the header slides away on
scroll down and returns on scroll up.

### Player Card (signature)
278px, plate gradient, 2px crest edge, corner tick. Portrait 44px, IGN 17px, team · lane 11px
uppercase with a 14px crest inline. One headline: lane impact at 24px over a fading gauge rule, its
caption and `n` right-aligned at 11px. A 12px line carries win rate, KDA, GPM. Then the hexagon.

### Percentile Hexagon (signature)
Six axes at 60°, radius 50 in a 240×168 viewBox, labels at 10.5px on a 1.46R ring. Outer ring at 100%,
dotted ring at 50%, 1px spokes, a value polygon at 13% chalk with a 1.4px stroke, and a dot per vertex.
Outward is better on every axis; deaths is inverted and the legend says so. The whole card's
`aria-label` carries the six values, so the shape is never colour- or sight-only.

### Teams Board (signature)
One plate, nine rows. The sort is the page's argument: **Rating** leads, **Standings** is the league's
own order — playoff seeding while the bracket is live, then final placement once the grand final
reaches four wins, with 5–6 alphabetical. A **Δ** column appears only when the two orders disagree;
when they agree, the note says so. Columns: Pts, series, games, game win% (95% CI), rating (95% CI),
SOS, Form5, blue/red, gold diff. Below 760 the table becomes a nine-row club index (rank, crest, code,
name, series, rating, chevron) so a phone never scrolls a thirteen-column table sideways.

### Club Dossier (signature)
A native `<details>` per club. The summary is the identity strip: a 3px crest edge, 76px crest, team
name at 50px, ghost code at 8% crest colour, official rank · series · games, and the model rating at
28px. The body opens with a **frosted band** — seven cells, translucent fill and inset lip, no
`backdrop-filter` — then two stacks. Left: roster (five lanes, portrait, GP, impact, KDA, WR) and
tendencies (tempo, gold diff, blowout, G3, series close, five-dot form). Right: draft (picks, bans,
first bans, pockets, HHI), map record at n≥5, and a 4×2 head-to-head. Actions: Prep vs, Matches, Copy
link. The player profile keeps the one true glass band; nine 22px blurs would be a performance and
world violation.

### Print
The same markup on paper: white plates, black ink, seams at `#bbb`, chrome removed, ghosts hidden,
charts re-stroked in grey and black, the tile grid collapsed to four columns. Cards print three across
with the radar capped at 200px. The Teams sheet prints the board as a table and every dossier open:
closed `<details>` are forced open, ghost wordmarks and actions removed. `verify.py` plus a
print-emulation check keep it honest.

## Do's and Don'ts

### Do:
- **Do** lead each view with its head: an `h1` and a one-line answer.
- **Do** lead each card with one figure at 22–24px and keep the rest at 12px or smaller.
- **Do** draw the 50th percentile on any percentile chart and name the better direction.
- **Do** sample team colour from the crest and clamp it for the ground.
- **Do** give each entity one tab: Overview is the season, Teams the clubs, Players the people,
  Matches the series, Stats the record, Analytics the models, Prep the plan.
- **Do** print the same markup, not a second layout.

### Don't:
- **Don't** put JetBrains Mono inside a player card.
- **Don't** leave a UA font on a control.
- **Don't** blur a panel on flat ground, or shadow one to separate it.
- **Don't** fill a card with a team colour; the accent is a 2px edge or a tint.
- **Don't** animate an entrance on every render, or ignore `prefers-reduced-motion`.
- **Don't** let a card's accessible name drop the numbers it shows.
