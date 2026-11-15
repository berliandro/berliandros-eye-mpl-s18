# Surface brief — player profile + rail

Mode: Operate. Target: `mpl_id_s18_dark.html` (`#view=player&player=<name>`).
Audience: fan arriving from the Players grid, coach arriving from Prep. Job: know who this
player is and how he performed, in one viewport, then drill into heroes and games. Constraints:
58 portraits at 192×192, single generated artifact, offline-first, never invent a number.

## Direction contract

THESIS: The player is the page, not a row in it. A full-bleed identity plate replaces the
stock dialog; the season's numbers become one glass band laid across the portrait instead of
eight equal tiles.

OWN-WORLD: Warm near-black ground (#131311), frosted glass surfaces with hairline rules,
Space Grotesk at 700 for the name and all figures, JetBrains Mono for labels and measurement,
one red (#e60023) held back for live or negative states. Team logos and cut-out portraits are
the only photographic material.

STORY: In the first viewport the visitor knows the IGN, team, lane, and the season's line —
games, record, KDA, K/D/A, GPM, kill participation, damage share — with the season row set
against the last five games. Scrolling reveals hero pool, derived stats and the game log.
The band shows no playoff split: no player has playoff game rows in the committed snapshot,
so a "Playoffs" row would be permanently empty.

FIRST VIEWPORT: Hero card at ~540px tall. Name left, uppercase, clamp(50–110px), tracking
−0.038em, capped at 58% width so long IGNs wrap instead of reaching the portrait; meta line
under it (games · series record · KDA). Portrait anchored bottom-right at ~500px tall,
standing behind a 7-column glass band pinned to the bottom edge and overlapping it by the
band's height. Ghost wordmark at 2.8% white behind; players without a cut-out get a 6% white
monogram in the portrait's position.

FORM: User-pinned composition from the NBA player-profile reference, quoted: "I love this
player profile look so much. The glass UI at the bottom, the big bold player image, the minimal
texts but clear." seed: none (pinned)

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the
verdict, DESIGN.md, and every shipping raster carrying its provenance
