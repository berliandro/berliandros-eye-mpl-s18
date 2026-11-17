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

Beneath the player hero the two columns are independent stacks, never grid rows: the wide column
carries hero pool, KDA trend, sides and opponent record; the narrow column carries derived stats,
recent games and items. Cards follow their column down, so a short card never leaves a card-shaped
hole under its neighbour. Only the ragged end of the shorter column is allowed, and the closing
definitions run full width under both.

The season page reads the same way: standings on the left and the MVP race plus playoffs on the
right, then recent results spanning both columns underneath. Nothing sits beside a shorter
neighbour, so the page has no card-shaped hole at its foot.

Teams opens with a nine-row league board, then nine club dossiers. The top three in competition order
open; the other six collapse to their identity strip. The dossier uses 1.06fr / 1fr — roster and
tendencies in the left stack, draft, map record and head-to-head in the right.

Matches opens on the latest week; earlier weeks are one-line summaries. The scoreboard is two tables,
not two stacks of rows; the playoffs are the bracket first and the playoff series second. Below 768
the bracket stacks by round and drops its connector lines, so the Grand Final is never off-screen.

Prep is one sheet, not a dashboard. An opponent plate carries the club, its rating as the single
headline figure with its interval, the record, then one mono line of win rate, form, SOS and
deciders beside the two selects and **Print / PDF**, **Copy link** and **CSV**. Beneath it the
draft (priority bans and their bans with first-ban and side lines), the map ladder sorted weakest
first, the player table, and — only once an opponent is chosen — the lane matchup with our own
line. Every method note lives in one **How this sheet is built** disclosure in the plate's foot,
which prints open. There are no stat tiles on Prep: a figure sits in the line or table that uses it.

Stats is two records behind one switch in the head, never two pages: the Series MVP race and the hero
record. Each is one full-width plate with one mono label carrying its count. The race is a ranked
leaderboard with the player, club crest, a proportional award bar and the count, with the Liquipedia
spellings stated once beneath it instead of beside every name; the 80 award decisions fold into a
foot disclosure that prints open. The hero record is one table — hero, lane, pick, ban, presence, win
rate — with its four answers in a single line above it, so no tile repeats what the table below
already says.

Spacing runs 8 / 14 / 18 / 24. Inside a panel 18–20px; between panels 18px.

## Elevation & Depth

Depth is light, not shadow. A plate is a vertical gradient from Plate High to Plate with a 1px seam and
an inset top highlight; hover lifts the seam to Seam Lift. There are no drop shadows on panels — only
the portrait's `drop-shadow(0 26px 48px rgba(0,0,0,.62))` and the bracket's win glow.

**The Lit-From-Above Rule.** The ground carries one gradient from the top of the page and a faint crown
radial. Nothing is lit from below, from the side, or from a colour — except the championship plate's
stage: its club-coloured floor pool is the one bounce light, with a centre key and a breathing beam
behind the squad.

## Motion

Motion belongs to navigation and feedback, never to arrivals. One authored moment carries the
product: the player's portrait leaves its card and becomes the profile hero — a shared-element
morph at 420ms on `cubic-bezier(.16, 1, .3, 1)` while the frame crossfades 160/240ms underneath.
It runs only when a player is opened from a visible card, reverses on **All players**, and the grid
returns to the scroll position it left. Every other animation is short and answers a state: a
dialog lands in 240ms, a scoreboard game swaps in 180ms, a disclosure unfolds in 260ms, and the
refresh control carries a determinate 2px rail. Radars draw only for cards a filter has just
produced. The championship plate is the one ambient surface: the squad's 12s breath, a 14s centre
beam, a 10s floor pool, a 16s crest watermark, a 24s haze drift and paper at 9–16s. Every loop sits
behind the content, pauses when the plate leaves the viewport, and stops under reduced motion.
Nothing flashes, no loop is faster than 9s, and none of it is required to read the result. Reduced
motion keeps the state changes and removes the travel.

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

### Championship Plate (signature)
The Overview hero from the moment a grand final is decided: the club's **whole roster is the
image**, standing in **one line at one scale**, lane order left to right, like the team sheet shot
under the lights. Every figure shares one baseline and one height (`--ph`, 150–286 at desktop,
90–130 on phones) and overlaps its neighbour by 30% of the frame, so shoulders sit together without
hiding a face. A player with no cut-out gets a ghost monogram and his IGN in mono rather than a
broken image or an invented face.

The stage is **lit, not decorated**: a warm key from above, a narrow centre beam, a soft back halo
at shoulder height, drifting haze, a club-coloured floor pool, and a thin light line where the
cut-offs meet the band. A crest watermark sits at 7–10% behind the five men; fine paper flecks in
chalk and the club colour fall in two depths. The centre beam breathes on a 14s cycle, the floor
pool on 10s, and the squad on 12s. Nothing flashes or moves faster than the 9s paper; the whole
stage pauses when the plate leaves the viewport and stops under reduced motion. The image keeps the
portrait's depth shadow plus a 1px top rim — never an outline.

Above the lineup a 52px crest lockup, the club name at display scale and one line —
`4–2 over [crest] NAVI`. Below it one machined band carries the grand-final trace — one cell per
game **naming the game's winner**. The champion's cells carry a 3px chalk bar, the opponent's stay
dashed, so a 4–3 final reads as four BTR games and three NAVI games, never as a list of the
champion's failures. The band also carries the series MVP, the action, and the roster line in mono.
The club code sits behind the lineup at 4.5% of the crest tint; ONIC, which derives no accent, takes
a chalk hairline and a chalk ghost.

No trophy, no laurel, no gold, no gradient text, and no second focal image: the celebration is
stage light and paper, never props. Below 760 the band stacks, the name steps down, and the lineup
keeps all five on one baseline by tightening its overlap and stepping `--ph` down; a roster wider
than six may scroll rather than clip. Print drops the ghost, the atmosphere, the shadows and the
action, and reads as a black-on-white certificate.

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
when they agree, the foot line says so. The active sort's column header is the only chalk header.

Columns: rank, club, rating, Pts, series, games, win%, SOS, Form5, gold diff. Rating is the row's one
figure, 16px display, with its interval as a 9.5px mono annotation on the same baseline and no
parentheses; win% carries its interval the same way. Every other cell is 11.5px and SOS is pewter.
Side records (blue / red) live in the dossier and in Prep, not on the board.

The bar carries one state line rather than a count: "Model rating order" by default, "League order ·
playoff seeding" when flipped. The foot is one sentence — Δ's definition, or "Model and league agree:
no club moves." — above a **How the board is built** disclosure holding the seeding rules, the rating
formula, the SOS definition and the side-record pointer; the disclosure prints open. Below 760 the
table becomes a nine-row club index (rank, crest, code, name, series, rating, chevron) so a phone
never scrolls a ten-column table sideways.

### Club Dossier (signature)
A native `<details>` per club. The summary is the identity strip: a 3px crest edge, 76px crest, team
name at 50px, ghost code at 8% crest colour, official rank · series · games, and the model rating at
28px. The body opens with a **frosted band** — seven cells, translucent fill and inset lip, no
`backdrop-filter` — then two stacks. Left: roster (five lanes, portrait, GP, impact, KDA, WR) and
tendencies (tempo, gold diff, blowout, G3, series close, five-dot form). Right: draft (picks, bans,
first bans, pockets, HHI), map record at n≥5, and a 4×2 head-to-head. Actions: Prep vs, Matches, Copy
link. The player profile keeps the one true glass band; nine 22px blurs would be a performance and
world violation.

### Analytics Plate (signature)
Two modes, one plate each, and the mode switch sits at the right of the shared head rather
than in a plate of its own. **Players** is the season ranking: the plate carries one caption
(`60 players · 5 lanes`) with the lane filter beside it, then a single table — rank, player,
team, lane, games, impact as the row's one figure, KDA, GPM, damage share, kill participation,
and win% with its Wilson interval. No bar behind impact and no within-lane percentile badge on
the four context columns: the lane filter and the lane column already carry the adjustment, and
impact is the lane-adjusted read. **How impact is built** is one disclosure in the plate's foot
and prints open.
**Draft** puts the argument first: meta movement across the last two 7-day windows, then the
twenty most contested heroes, then drawers — synergy, counters, compositions, maps, and all 93
heroes — each summary carrying its own count and each table its own caveat, so a caveat is never
read away from the number it qualifies. Nothing on the view is a header plate that repeats the
view head.

### Prep Sheet (signature)
Four plates, one question each: the opponent, the draft, the maps, the players. The opponent plate is
the cover — crest, club, rating at 24px with its 95% interval, record, one mono line of win rate,
form, SOS, deciders and game 3, the two team selects, and Print / PDF as the primary action.
Priority bans are ranked rather than scored on screen; their bans, first bans and side record sit
beside them. The map ladder reads weakest first with a bar, so a club with no losing map says so at
a glance. A matchup plate appears only once our team is chosen, carrying our own line above the five
lane rows. One method disclosure prints open.

### Match Card + Week Group (signature)
The latest week opens; earlier weeks are one-line summary bars. The card is the control: no separate
button, no internal id, no “COMPLETED”; the winner is weight, the series MVP is named, and the date is
one short voice. “Open scoreboard” is a hint inside the card; the whole card is a `role=button` control
with Enter/Space. Below 640 the week collapses to one column and the list drops the 640px floor so the
chevron stays on screen.

### Scoreboard Table (signature)
Two tables, not mirrored row stacks: **Player / K/D/A / KDA / Gold / GPM / DMG / TAKEN**, tabular and
right-aligned, with a build row of emblem, talents and items per player. The series score is the
dialog title; **Series MVP (Liquipedia)** is the subtitle and **Game MVP (KDA heuristic)** sits in the
game header. Bans keep draft order with hero art; the side is a 3px edge plus a labelled Blue/Red
chip; the VOD is a chalk pill at 44px on touch. The dialog title is `h2`, each game `h3`.

### Playoff Bracket (signature)
The bracket is the playoffs page. Undecided slots name their feed (“Winner QF1”, “Loser UF”), never a
bare TBD; the playoff series sit below it. A team filter dims the other routes and says the bracket
is league-wide, rather than leaving a count that contradicts the drawing. On phones the four rounds
stack in order, without connector lines, so the final stays reachable.

### Print
The same markup on paper: white plates, black ink, seams at `#bbb`, chrome removed, ghosts hidden,
charts re-stroked in grey and black, the tile grid collapsed to four columns. Cards print three across
with the radar capped at 200px. The Teams sheet prints the board as a table, with its method paragraph
open and its summary hidden, and every dossier open: closed `<details>` are forced open, ghost
wordmarks and actions removed. The Matches sheet opens every
week group and prints the cards three across. `verify.py` plus a print-emulation check keep it honest.

## Do's and Don'ts

### Do:
- **Do** lead each view with its head: an `h1` and a one-line answer.
- **Do** lead each card with one figure at 22–24px and keep the rest at 12px or smaller.
- **Do** draw the 50th percentile on any percentile chart and name the better direction.
- **Do** sample team colour from the crest and clamp it for the ground.
- **Do** give each entity one tab: Overview is the season, Teams the clubs, Players the people,
  Matches the series, Stats the record, Analytics the models, Prep the plan.
- **Do** make the card the control and name the series before the controls.
- **Do** distinguish Series MVP (Liquipedia) from Game MVP (KDA heuristic) wherever both are shown.
- **Do** print the same markup, not a second layout.

### Don't:
- **Don't** put JetBrains Mono inside a player card.
- **Don't** leave a UA font on a control.
- **Don't** blur a panel on flat ground, or shadow one to separate it.
- **Don't** fill a card with a team colour; the accent is a 2px edge or a tint.
- **Don't** animate an entrance on every render, or ignore `prefers-reduced-motion`.
- **Don't** let a card's accessible name drop the numbers it shows.
