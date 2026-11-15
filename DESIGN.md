---
name: Berliandro's Eye — MPL ID Season 18
description: An evidence desk for MPL Indonesia, built out of dark stone and measured light
colors:
  kiln: "#131311"
  basalt: "#1a1a18"
  salt: "#f2f1ec"
  pewter: "#a6a39b"
  seam: "#2b2b28"
  seam-lift: "#3d3d39"
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
    fontSize: "9.5px"
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
    textColor: "{colors.salt}"
    rounded: "{rounded.sm}"
    padding: "10px"
  chip:
    backgroundColor: "transparent"
    textColor: "{colors.pewter}"
    rounded: "{rounded.pill}"
    padding: "3px 10px"
  button-primary:
    backgroundColor: "{colors.salt}"
    textColor: "{colors.kiln}"
    rounded: "{rounded.xs}"
    padding: "9px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.salt}"
    rounded: "{rounded.xs}"
    padding: "8px 14px"
  card-player:
    backgroundColor: "{colors.basalt}"
    textColor: "{colors.salt}"
    rounded: "{rounded.md}"
    padding: "16px"
  input:
    backgroundColor: "{colors.basalt}"
    textColor: "{colors.salt}"
    rounded: "{rounded.xs}"
    padding: "9px 12px"
---

# Design System: Berliandro's Eye

## Overview

**Creative North Star: "The Tape Room"**

A dark room where broadcast tape and a match database are reviewed on the same desk. The walls are
stone, not glass: the ground is a warm near-black, panels sit on it as flat slabs with a single
hairline, and light is spent only where a number or a face needs to be read. Nothing shimmers,
because a review room does not shimmer — the drama belongs to the footage, and the surface's job is
to disappear behind it.

The system has two readers and one surface scale. A fan scans a grid of sixty-one players; a coach
opens one of them and reads the shape of a season. Both are served by the same instruments at
different pressures: a card that leads with one number, a profile that can afford to be dense. Where
the two would conflict, the fan's first five seconds win and the coach gets depth one click away.

Colour is information or it is absent. A signal red marks where you are and what was lost, a pitch
green marks a win, and each team's crest colour is sampled from its own logo. There is no accent
kept for decoration.

**Key Characteristics:**
- Kiln ground, salt type, seam hairlines; depth is tonal, never shadowed.
- One headline figure per card; everything else supports at 12px or smaller.
- Charts always draw their 50th percentile and say which direction is better.
- Mono is chrome — rail, tables, legends — never a card's voice.

## Colors

Warm near-black, one signal hue, and a generated family of crest accents.

### Primary
- **Signal Red** (#e60023): the eye in the mark, the active rail tab, and loss. Never a fill, never
  decoration, never more than a 2px rule or a status pill.
- **Pitch Green** (#3ddc84): wins only — result pills, and nothing else.

### Secondary
- **Crest Accents** (generated): one per team, sampled from the committed logo by
  `tools/derive_team_colors.py` and clamped to L 0.52–0.66 / S 0.55–0.88, so a navy crest stays
  visible and a neon cannot glow. NAVI `#f0e119`, TLID `#1a6cef`, EVOS `#4182c8`, BTR `#f01919`,
  RRQ `#f2aa36`, DEWA `#e6bb62`, AE `#e62336`, GEEK `#ef1c24`. ONIC derives nothing and falls back
  to a 42% salt hairline rather than a guessed colour.

### Neutral
- **Kiln** (#131311): page ground.
- **Basalt** (#1a1a18): every panel and card — opaque, with no blur.
- **Salt** (#f2f1ec): primary text, primary button fill, the name plate.
- **Pewter** (#a6a39b): secondary text, table headers, supporting figures.
- **Seam** (#2b2b28): every hairline; **Seam Lift** (#3d3d39) on hover.

### Named Rules
**The One Signal Rule.** Red is used on ≤2% of a screen: the active rail tab and a loss. Anywhere
else it must name a failure.

**The Crest Is Data Rule.** A team's colour is sampled from its logo and clamped, never chosen. A
team with no saturated hue gets the neutral hairline; it never gets an invented colour.

## Typography

**Display Font:** Space Grotesk (Manrope, system-ui fallback)
**Body Font:** Manrope (SF Pro Display, Segoe UI Variable fallback)
**Label/Mono Font:** JetBrains Mono, for chrome only

**Character:** A geometric face for identity and figures, a humanist sans for everything a reader has
to parse, and a mono kept to the rail, the tables and the legends — the places where a column must
line up. The pairing reads as instruments in a room, not as a dashboard skin.

### Hierarchy
- **Display** (700, clamp 50–110px, 0.84): the player IGN on the profile page, capped at 58% width so
  long names wrap instead of colliding with the portrait.
- **Headline** (700, 24px, 1.0): the single lead figure on a card — lane impact — and the score on the
  season plate at its larger clamp.
- **Title** (600, 17px, 1.3): card names and panel titles.
- **Body** (400, 12px, 1.45): supporting figures, notes, method text; captions at 12px, never below.
- **Label** (600, 9.5px, 0.09em, uppercase): axis labels, table headers, block subtitles.

### Named Rules
**The One Headline Rule.** A card carries exactly one figure at 22–24px. Everything else on it is
12px or smaller, and the second-largest mark is the name.

**The Chrome-Only Mono Rule.** JetBrains Mono never appears inside a player card. It belongs to the
rail, tables, legends and machine values, where columns must align.

**The Tabular Rule.** Every number that can change column is `font-variant-numeric: tabular-nums`.

## Layout

A centred 1200px wrap on a 1440px canvas, with a 220px rail (196px between 1180 and 1320px) that
takes navigation above 1180px. Below that the header's tabs return, and below 640px the filters move
into a bottom sheet behind a `Filters` pill, leaving the header at ~230px instead of ~370.

Cards live in an auto-fill grid at a 250px minimum, four across at 1440. The player profile uses a
1.55fr / 1fr split that collapses at 980px; the season front page uses the same split for standings
and the MVP race, with the playoff panel stacked beneath it.

Spacing runs 8 / 14 / 18 / 24. Inside a panel: 18–20px. Between panels: 18px. A heading sits closer
to what it governs than to what precedes it.

## Elevation & Depth

Depth is tonal and linear. Panels are a lighter grade of the ground with a 1px seam; cards are
opaque basalt with no blur, because there is nothing behind them to sample. The system ships no
panel shadows. The only shadows in the product are the player portrait's
`drop-shadow(0 26px 48px rgba(0,0,0,.62))` and the playoff bracket's win glow.

Glass survives in exactly two places, both of which overlap content: the stat band across the bottom
of a player portrait, and the sticky header before it was made opaque on mobile.

### Named Rules
**The Overlap-Only Glass Rule.** `backdrop-filter` is allowed only where a surface sits over imagery
or scrolling content. A blurred card on a flat ground is refused.

**The Seam-First Rule.** Separate two surfaces with a 1px seam or a tone change. Never a shadow.

## Shapes

Gently curved instruments: 10px for cards, 14–16px for panels and hero plates, 6–8px for controls,
full pills for status and filters, 8px squares for portraits and crests. Borders are always 1px and
always seam; a team or state accent is a separate 2px rule at an edge, never a thicker border on the
same box. Circles are reserved for avatars inside badges, emblems, runes and icons.

## Components

### Buttons
- **Shape:** 6px radius; ghost variants carry a 1px seam.
- **Primary:** salt fill, kiln text, 600 weight — the single committed action.
- **Ghost:** transparent, salt text, seam border, lifting to Seam Lift on hover.
- **Pill action:** 9999px, mono 9.5px uppercase, used on the season plate.

### Chips
- **Style:** transparent, 1px seam, pewter text, 11px uppercase.
- **State:** selected flips to salt fill with kiln text. On coarse pointers every chip is 44px tall;
  on a mouse it stays a 20px pill.

### Cards / Containers
- **Corner Style:** 10px cards, 14px panels, 16px hero plates.
- **Background:** opaque basalt.
- **Border:** 1px seam, hovering to Seam Lift.
- **Internal Padding:** 16px cards, 18–20px panels.

### Inputs / Fields
- **Style:** basalt fill, 1px seam, 6px radius, 9px/12px padding. Form controls inherit the UI face
  (`button,select,input,textarea{font-family:inherit}`) — a UA default face is a defect.
- **Focus:** the global 2px salt ring at 2px offset.

### Navigation
- **Rail:** 220px, section labels in 9.5px mono, 40px rows with an 18px drawn icon. The active row
  takes a raised surface and a 2px bar at the rail's content edge; that bar turns the current team's
  crest colour on a player page and returns to signal red when you leave.
- **Header:** sticky; search, filter pill and tabs. Below 640px the controls collapse into a bottom
  sheet, and the header carries the snapshot status instead.
- **Mobile:** tabs scroll in one row with a fade at the edge.

### Player Card (signature)
278px, opaque basalt, a 2px crest edge. Portrait 44px, IGN 17px Space Grotesk, team · lane in
Manrope 10.5px uppercase, the crest at the far right. Then one headline: lane impact at 24px, its
label and `n` right-aligned to the card edge. A 12px Manrope line carries win rate, KDA and GPM.
Then a **six-axis percentile hexagon** — damage share, kill participation, gold share, tower share,
KDA and inverted deaths — over a dotted 50th-percentile ring, labels at 9.5px. Hero names close the
card. The whole card is one link.

### Percentile Hexagon (signature)
Six axes at 60°, radius 50 in a 240×168 viewBox. Outer ring at 100%, dotted ring at 50%, 1px axes,
a value polygon at 13% salt fill with a 1.4px stroke, and a 1.7px dot at each vertex. Outward is
better on every axis; death share is inverted, and the legend says so.

### Stat Band (signature)
A glass strip across the bottom of a player plate, overlapping the portrait: a row label, then GP,
game W-L, KDA, K/D/A, gold/min, kill participation and damage share. Labels are pewter; figures are
salt at 16px; compound values drop to mono 12px.

## Do's and Don'ts

### Do:
- **Do** lead every card with one figure at 22–24px and keep the rest at 12px or smaller.
- **Do** draw the 50th percentile on any percentile chart, and name which direction is better.
- **Do** sample team colour from the crest and clamp it for the dark ground.
- **Do** keep numerals tabular and aligned to their column.
- **Do** test 390 and 1440 before calling a surface finished.

### Don't:
- **Don't** put JetBrains Mono inside a player card.
- **Don't** leave a UA font on a control: inherit the UI face.
- **Don't** blur a panel that sits on flat ground.
- **Don't** fill a card or row with a team colour; the accent is a 2px edge or a tint.
- **Don't** use signal red for anything that is not location or loss.
- **Don't** invent a colour for a team whose crest has none.
