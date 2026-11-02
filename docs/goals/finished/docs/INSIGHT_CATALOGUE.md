# Insight Catalogue — time filtering and derived analytics

> Companion to `docs/ROADMAP.md`. This is the idea layer: what we can *invent*
> from data we already have (or will have after Phase 1), and where a time
> filter earns its place.
>
> Nothing here is committed scope. Items are tagged so they can be promoted into
> the roadmap backlog deliberately.

---

## TL;DR

1. **Don't add a slider per tab.** Add **one global time context** in the header
   and make every aggregate read it. Per-tab sliders fragment state, drift out
   of sync, and cannot be shared by link.
2. The patch pin idea is strong, but the real unlock is **A/B compare** (Patch A
   vs Patch B), not a single range. A filter shows *what is*; a comparison shows
   *what changed*.
3. The highest-value time consumers are: **Heroes, Series MVP, Players, the
   player Overview, hero drill-down, item/emblem/talent drill-downs, and the
   future scouting report**.
4. Six coach-grade insights are buildable from the **current database alone**,
   before any new ingestion. Start there.

---

## Part 1 — Time as a global dimension

### 1.1 Why one control, not many

The app already has a single visual language: one header, one filter row, one
board. A per-tab slider would break that and create three problems:

- **State drift** — the hero tab filtered to Week 6 and the MVP tab filtered to
  full season produce two different "truths" on one screen.
- **No shareability** — a coach cannot send "this view, this patch" as a link.
- **No comparison** — two independent sliders cannot compute a delta.

**Proposal:** a single **time bar** under the header, persisted in the URL and
`localStorage`, with every aggregate reading from it. Views that cannot honour
it (official standings, playoff odds, awards) show a **"season-wide"** badge
instead of silently ignoring it.

### 1.2 Time bar spec

```
┌──────────────────────────────────────────────────────────────────────┐
│  TIME   [ Season ][ Current patch ][ Last 4 weeks ][ Playoffs ]      │
│                                                                      │
│  Aug 14        Sep 05        Oct 03        Oct 18        Nov 08      │
│  ●──────────────●──────────────●──────────────●──────────────●       │
│  │  2.1.95      │  2.1.95a     │  2.2.16      │  playoffs    │       │
│      ▲ start            ▲ end                                        │
│                                                                      │
│  Filtering 24 series · 58 games · 3 patches      [ Compare ] [ × ]   │
└──────────────────────────────────────────────────────────────────────┘
```

Requirements:

- **Dual handles** over a timeline of actual match dates (not calendar days), so
  a range always contains games.
- **Patch pins** rendered as segments + clickable labels.
- **Presets**: Full season, Current patch, Last 4 weeks, Playoffs, Custom.
- **Live scope chip**: "24 series · 58 games · 3 patches" — the filter must never
  be silently empty.
- **Compare toggle**: adds a second ghost range (A/B).
- **URL state**: `?from=2026-09-05&to=2026-10-03&cmp=2026-08-14:2026-09-04`.
- **Keyboard**: arrow keys move the focused handle by one match date.
- **Reset** returns to Full season.

### 1.3 Patch model — tournament patch, not game release

MPL plays on a **locked tournament patch**. The app must pin patches to the
**first match played on that patch**, not to the global release date.

`data/patches.json`:

```json
{
  "s18": [
    { "version": "2.1.95",  "from": "2026-08-14", "to": "2026-08-29",
      "label": "W1–W2", "source": "Liquipedia patch table" },
    { "version": "2.1.95a", "from": "2026-08-30", "to": "2026-09-18",
      "label": "W3–W5", "source": "Liquipedia patch table" },
    { "version": "2.2.16",  "from": "2026-09-19", "to": "2026-10-17",
      "label": "W6–W9", "source": "Liquipedia patch table",
      "notes": ["Masha disabled in W6"] },
    { "version": "playoffs", "from": "2026-10-18", "to": null,
      "label": "Playoffs", "source": "TBD" }
  ]
}
```

Rules:

- A patch boundary is the first **match** on that patch, not the release date.
- If a patch changes mid-week, split at match granularity.
- If the tournament patch is unknown, show "unknown patch" — never guess.
- Patch notes (which heroes changed) are a **separate, optional** source; only
  needed for the adoption/impact ideas below.

### 1.4 Where time applies

| View | What the range filters | Insight unlocked | Caveat |
|---|---|---|---|
| **Stats → Heroes** | pick / ban / win / WR | patch meta, dominant heroes, dead heroes | thin `n` per patch; show badge |
| **Stats → Series MVP** | MVP points and history | split-season MVP, momentum, "best since Week 6" | MVP is series-level, not game-level |
| **Players grid/list** | every player aggregate + sort | form rankings, hot/cold, breakout players | sample size |
| **Overview (player)** | tiles, hero pool, KDA trend, items, emblems, talents, game log | player form, patch adaptation, pool change | trend already temporal — don't double-filter |
| **Player dialog (per-hero)** | per-hero GP/KDA/K/D/A/GPM | "his Hirara since the patch" | thin `n` |
| **Hero drill-down** | tiles, item/emblem/talent breakdown, player list, game list | hero build shift, which players picked it up | thin `n` |
| **Item / emblem / talent drill-down** | usage counts and user list | meta item/talent shift, who innovated | builds are situational |
| **Draft analysis (new)** | pick/ban tendencies, first bans | patch draft meta, side scripts | needs full drafts |
| **Standings** | **not** the official table — a *form table* in the window | "table since Week 6" | must be labelled "form", not standings |
| **H2H** | recent meetings only | current-patch head-to-head | thin `n` |
| **Matches** | filter + group by patch | patch context per series | low value as a pure filter |
| **Scouting report (future)** | default = current patch / last 4 weeks | relevant prep, not stale season averages | — |

### 1.5 Where time must NOT apply

These are cumulative by definition. Filtering them would be misleading; they
should render a **"season-wide"** chip and ignore the range:

- Official standings and tiebreakers.
- Playoff qualification probabilities (they depend on the full fixture list).
- Season awards / MVP race *totals* (the race view may use a window, but the
  award itself is seasonal).
- Any "season record" claim.

### 1.6 Compare mode — the actual differentiator

A single range answers "what happened in this window". A **comparison** answers
"what changed", which is what a coach and an analyst actually need.

- Two ranges A and B, rendered as solid vs ghost handles.
- Every metric shows `A → B` with a delta and a confidence band.
- Presets: "Patch vs patch", "First half vs second half", "Before/after roster
  change", "Regular season vs playoffs".
- Deltas must carry `n` on both sides; suppress the delta below a threshold and
  say why.

This is the feature that turns the slider from a filter into an insight engine.

---

## Part 2 — The patch slider, refined

Your original interaction, tightened:

1. **Click a patch pin** → range snaps to that patch's first and last match.
2. **Click the same pin again** → range returns to the previous selection
   (toggle, not a one-way trap).
3. **Shift-click a second pin** → selects the span between two patches
   (e.g. 2.1.95 → 2.2.16).
4. **Drag a handle across a patch boundary** → the patch label highlights the
   portion covered, so partial-patch ranges are obvious.
5. **Hover a pin** → tooltip: version, date range, series/game count, and
   "Masha disabled" style notes.
6. **Compare toggle + pin click** → sets the B range to that patch, enabling
   patch-vs-patch in one gesture.

Edge cases to handle explicitly:

- A patch with **zero games** (e.g. a patch applied during a break) should render
  as a thin band with "no games", not a clickable empty range.
- The **last patch** is open-ended; its end handle is "now".
- **Playoffs** may run on a different patch than the regular season finale.
- If the tournament patch is unknown for a period, render a hatched "unknown"
  band rather than attributing games to the wrong patch.

---

## Part 3 — Insight catalogue

### How to read the tags

| Tag | Meaning |
|---|---|
| `D0` | Buildable from the **current database** |
| `D1` | Needs per-game **lane** (Phase 1) |
| `D2` | Needs full **drafts / ban order** (Phase 1) |
| `D3` | Needs **hero classes** — role, lane, damage type (Phase 1) |
| `D4` | Needs **map mode** (Phase 1) |
| `D5` | Needs **patch notes** (new source) |
| `D6` | Needs **season objective totals** (new source) |
| *S / M / L* | Effort: ≤2 days / 3–5 days / >5 days |
| ★ | Genuinely uncommon in public MPL ID coverage |

---

### A. Time & patch

**A1 · Patch meta board** ★
- *Question:* Which heroes owned each patch, and what changed?
- *Method:* P/B/WR per patch window; delta vs previous patch; `n` badge on every
  cell; patch pins drive the range.
- *Data:* `D0` + `patches.json` · *Effort:* S
- *Caveat:* per-patch samples are small; never headline a rate below `n=5`.

**A2 · Patch breakout / falloff** ★
- *Question:* Which players improved or declined after a patch?
- *Method:* role-normalised metric per patch, then `B − A` with shrinkage and a
  confidence band. Rank by delta, not absolute value.
- *Data:* `D0` (primary lane) / `D1` (true lane) · *Effort:* M
- *Caveat:* a patch can change a player's role, not just their skill.

**A3 · Meta momentum**
- *Question:* Which heroes are rising or falling right now?
- *Method:* slope of pick-rate across the last 3 weeks; show the series, not just
  an arrow.
- *Data:* `D0` · *Effort:* S

**A4 · Era split**
- *Question:* Was the first half or second half stronger?
- *Method:* team rating and hero meta computed separately per half, with
  cross-half calibration.
- *Data:* `D0` · *Effort:* M

**A5 · Patch trap** ★
- *Question:* Which heroes are still banned out of habit after being nerfed?
- *Method:* ban rate trend vs WR trend across the patch boundary.
- *Data:* `D0` + `patches.json` · *Effort:* S

**A6 · Patch adoption lag** ★
- *Question:* How fast does each team pick up newly strong heroes?
- *Method:* for each hero buffed in patch P, days from patch start to a team's
  first pick; median per team.
- *Data:* `D5` (patch notes) + `D0` · *Effort:* M
- *Caveat:* requires reliable patch notes; label as "first pick after patch",
  not "learned the patch".

---

### B. Draft & ban

**B1 · Ban efficiency — over-banned vs under-banned** ★
- *Question:* Which bans are wasted?
- *Method:* plot ban rate against WR-when-played; flag high-ban/low-WR
  (over-banned) and low-ban/high-WR (under-banned). Residual vs expected ban
  rate given WR.
- *Data:* `D0` · *Effort:* S
- *Caveat:* descriptive, not causal — teams may ban for matchup reasons we
  cannot see.

**B2 · Respect index** ★
- *Question:* Whose comfort picks get banned out?
- *Method:* for each player, share of games where ≥1 of their top-3 heroes was
  banned by the opponent; weight by hero pool concentration.
- *Data:* `D0` + `D2` (to attribute the ban to the opponent) · *Effort:* M

**B3 · Draft predictability** ★
- *Question:* How readable is a team's draft?
- *Method:* normalised entropy of pick and ban distributions, split by side;
  report "predictability %" with `n`.
- *Data:* `D2` · *Effort:* M
- *Caveat:* predictable can still be strong (comfort), so pair it with WR.

**B4 · Hero flex map** ★
- *Question:* Which heroes can occupy multiple lanes?
- *Method:* lane distribution per hero from `D1`; flex rate = share outside the
  modal lane; show which players flex them.
- *Data:* `D1` · *Effort:* S

**B5 · Synergy network** ★
- *Question:* Which hero pairs actually win together?
- *Method:* same-team hero pairs; WR delta vs expectation from individual hero
  WR; require `n ≥ 8`; shrinkage.
- *Data:* `D2` · *Effort:* M

**B6 · Counter matrix** ★
- *Question:* Which heroes beat which?
- *Method:* opposing-team hero pairs; WR with Wilson CI; shrink toward 50%;
  surface only `n ≥ 5`, and show `n`.
- *Data:* `D2` · *Effort:* M
- *Caveat:* confounded by player skill and team strength; never present as
  "counter" without the caveat.

**B7 · Pocket picks** ★
- *Question:* Who beats the meta with off-pool heroes?
- *Method:* player WR on hero minus league WR on that hero; require `n ≥ 3` and
  hero league usage below a threshold.
- *Data:* `D0` · *Effort:* S

**B8 · Pool overlap leverage** ★
- *Question:* Which ban hurts two players at once?
- *Method:* overlap of teammates' hero pools; a ban that hits both is worth more.
  Rank heroes by "shared exposure".
- *Data:* `D0` · *Effort:* S

**B9 · Comfort dependency**
- *Question:* How much does a team rely on getting its heroes?
- *Method:* team WR when they secure ≥2 of their top-5 most-picked heroes vs
  when they do not.
- *Data:* `D0` · *Effort:* S

**B10 · Side draft identity** ★
- *Question:* Does a team draft differently on blue vs red?
- *Method:* pool, first-ban and WR split by side; flag sides with `n < 8`.
- *Data:* `D2` · *Effort:* S

**B11 · Ban-order script** ★
- *Question:* What does a team ban first, and what does that reveal?
- *Method:* `b1` distribution by side; sequence patterns; transition matrix
  `b1 → b2`.
- *Data:* `D2` · *Effort:* M

**B12 · Draft similarity / copycat**
- *Question:* Which teams copy each other's drafts?
- *Method:* Jaccard similarity between team draft sets; cluster.
- *Data:* `D2` · *Effort:* M

---

### C. Player evaluation

**C1 · Role-normalised percentile card** ★
- *Question:* How good is this player *for their role*?
- *Method:* within-lane percentile for damage share, KP, gold share, tower
  damage, death share; empirical-Bayes shrinkage; show `n`.
- *Data:* `D0` (primary lane) / `D1` · *Effort:* M

**C2 · Replacement level / wins above replacement** ★
- *Question:* How much better than a league-average player at this role?
- *Method:* role median as replacement level; convert metric delta to estimated
  win contribution via a simple logistic link; show CI.
- *Data:* `D1` · *Effort:* L
- *Caveat:* "wins" is modelled, not observed — label it.

**C3 · Opponent-adjusted performance** ★
- *Question:* Who stat-pads against weak teams?
- *Method:* split games by opponent rating quartile; report metric delta and CI.
- *Data:* `D0` · *Effort:* M

**C4 · Hero-adjusted residual** ★
- *Question:* Is the player good, or is the hero good?
- *Method:* player metric minus the league average for that hero, then shrink.
- *Data:* `D0` · *Effort:* M

**C5 · Consistency cone** ★
- *Question:* How bad is their bad game?
- *Method:* per-game distribution; p10 / median / p90; IQR. Render as a cone, not
  a single average.
- *Data:* `D0` · *Effort:* S

**C6 · Form delta**
- *Question:* Who is hot right now?
- *Method:* rolling last-5 games vs season baseline, role-normalised; show both
  numbers and the delta.
- *Data:* `D0` · *Effort:* S

**C7 · Close-game composure**
- *Question:* Who performs when it is tight?
- *Method:* games with final kill diff ≤ 5; win rate and metric delta vs
  blowouts.
- *Data:* `D0` · *Effort:* S
- *Caveat:* final kill diff is a proxy, not a timeline.

**C8 · Clutch record** ★
- *Question:* Who shows up in game 3 and deciding games?
- *Method:* game-3 and series-deciding-game win rate and stats; `n` badge.
- *Data:* `D0` · *Effort:* S

**C9 · Invisible impact (plus-minus)** ★
- *Question:* Who wins without filling the stat sheet?
- *Method:* team win rate with player on the roster vs without (subs) and
  player-level kill participation vs result.
- *Data:* `D0` · *Effort:* M
- *Caveat:* roster confounding; small `n` for subs.

**C10 · Enabler vs carry** ★
- *Question:* Whose stats understate their value?
- *Method:* compare role-normalised individual output with team outcome; flag
  low-stat/high-win profiles.
- *Data:* `D1` · *Effort:* M

**C11 · Player similarity** ★
- *Question:* Who plays like whom?
- *Method:* cosine similarity over role-normalised metric vector; same-role only.
- *Data:* `D1` · *Effort:* M

**C12 · Off-role penalty** ★
- *Question:* What happens when a player flexes?
- *Method:* performance delta when lane ≠ primary lane; `n` badge.
- *Data:* `D1` · *Effort:* S

---

### D. Team style

**D1 · Tempo fingerprint**
- *Question:* How does this team win and lose?
- *Method:* win duration vs loss duration; share of wins < 15 min and > 22 min.
- *Data:* `D0` · *Effort:* S

**D2 · Gold allocation by role** ★
- *Question:* Who does this team invest in?
- *Method:* share of team gold by lane; compare to league by role.
- *Data:* `D0` (primary lane) / `D1` · *Effort:* S

**D3 · Dominance profile**
- *Question:* How convincingly do they win?
- *Method:* mean gold / damage / tower-damage differential per game; blowout rate
  (|kill diff| ≥ 10).
- *Data:* `D0` (sum the five player rows) · *Effort:* S

**D4 · Grinder vs blowout**
- *Question:* Do they win slow or fast?
- *Method:* duration distribution conditional on result.
- *Data:* `D0` · *Effort:* S

**D5 · Lineup combinations** ★
- *Question:* Which five-man units actually work?
- *Method:* group games by the exact player set; record W-L per unit; require
  `n ≥ 3`.
- *Data:* `D0` · *Effort:* S
- *Caveat:* lineups correlate with opponent strength; show schedule context.

**D6 · Sub impact** ★
- *Question:* Does the sub change the team?
- *Method:* team metrics with/without each sub; player metrics in those games.
- *Data:* `D0` · *Effort:* S

**D7 · Side dependence** ★
- *Question:* Is a team carried by blue side?
- *Method:* WR and pool split by side; delta vs league side baseline.
- *Data:* `D0` · *Effort:* S

**D8 · Map-mode profile** ★
- *Question:* Which map suits them?
- *Method:* pick/ban/WR and tempo by `map_mode`.
- *Data:* `D4` · *Effort:* S

**D9 · Style clustering** ★
- *Question:* Which teams play alike?
- *Method:* cluster on tempo, gold allocation, draft diversity, side bias.
- *Data:* `D0` + `D2` · *Effort:* M

**D10 · Pressure conversion** ★
- *Question:* Who turns gold into towers?
- *Method:* tower damage per gold, per win, per minute; role-normalised.
- *Data:* `D0` · *Effort:* S

---

### E. Matchup & prep

**E1 · Lane head-to-head** ★
- *Question:* Who wins the lane?
- *Method:* same-lane opponents in the same game; KDA/gold/damage differential;
  aggregate across meetings with CI.
- *Data:* `D1` · *Effort:* M

**E2 · Player matchup card** ★
- *Question:* How does our player do against theirs?
- *Method:* combine lane H2H, hero pools, and recent form; show `n`.
- *Data:* `D1` · *Effort:* M

**E3 · Team H2H by patch / side / map** ★
- *Question:* Does the head-to-head change with context?
- *Method:* slice existing H2H by patch, side and map mode.
- *Data:* `D0` + `D4` · *Effort:* S

**E4 · Weakness radar** ★
- *Question:* Where is this player/team below role/league median?
- *Method:* six role-normalised axes; show distance from median with CI.
- *Data:* `D1` · *Effort:* M

**E5 · Strength radar** ★
- *Question:* Where do they beat the league?
- *Method:* mirror of E4.
- *Data:* `D1` · *Effort:* S

**E6 · Scouting report**
- *Question:* Everything needed to prep a series on one page.
- *Method:* compose B2, B9, B10, D1–D8, E1–E5 into a generated one-pager.
- *Data:* all · *Effort:* L

**E7 · Ban recommender**
- *Question:* What should we ban?
- *Method:* rank by expected swing = opponent proficiency × our vulnerability;
  show assumptions and `n`.
- *Data:* `D0` + `D2` · *Effort:* M

**E8 · "How to beat them" checklist**
- *Question:* What is the actionable game plan?
- *Method:* rule-based synthesis of weaknesses (e.g. "they lose when denied first
  pick", "red-side WR 25%") with evidence links.
- *Data:* all · *Effort:* M

---

### F. Composition & builds

**F1 · Archetype win rates** ★
- *Question:* Which draft shapes win?
- *Method:* hero roles from `D3` → frontline count, damage-type balance, engage
  count; bucket into archetypes; WR with `n` and CI.
- *Data:* `D3` + `D2` · *Effort:* M

**F2 · Damage-type balance** ★
- *Question:* Does a physical/magic split matter?
- *Method:* count physical vs magic heroes per lineup; WR by balance bucket.
- *Data:* `D3` · *Effort:* S

**F3 · Frontline & engage count** ★
- *Question:* How much frontline is enough?
- *Method:* tanks + fighters per lineup vs WR; same for engage/CC tags.
- *Data:* `D3` · *Effort:* S

**F4 · Item build archetypes** ★
- *Question:* Which builds win?
- *Method:* treat the final six items as a set; cluster by similarity; WR by
  cluster; require `n ≥ 5`.
- *Data:* `D0` · *Effort:* M
- *Caveat:* winning teams can afford luxury items — correlation, not causation.

**F5 · Build deviation** ★
- *Question:* Who innovates, and does it work?
- *Method:* player build vs the hero's modal build; WR delta.
- *Data:* `D0` · *Effort:* M

**F6 · Emblem / talent meta** ★
- *Question:* Which rune setups actually win?
- *Method:* WR by emblem/talent per role; shrinkage; `n` badge.
- *Data:* `D0` · *Effort:* S

**F7 · Boots choice**
- *Question:* Does the boot upgrade correlate with outcome?
- *Method:* WR by boot item per role.
- *Data:* `D0` (item classes) · *Effort:* S

---

### G. Meta & narrative

**G1 · Must-ban list**
- *Question:* What can we not let through?
- *Method:* P+B × WR quadrant; tag "must ban", "trap ban", "free win", "ignore".
- *Data:* `D0` · *Effort:* S

**G2 · Weekly digest** ★
- *Question:* What changed this week?
- *Method:* auto-generated risers/fallers, streaks, notable lines, patch movement.
- *Data:* `D0` · *Effort:* M
- *Use:* content engine, shareable, drives return visits.

**G3 · Streak & storyline detection** ★
- *Question:* What is the narrative right now?
- *Method:* consecutive wins, player MVP streaks, hero losing streaks, team
  milestone detection.
- *Data:* `D0` · *Effort:* S

**G4 · Hero health quadrant**
- *Question:* Which heroes are strong vs popular?
- *Method:* P+B presence vs WR scatter with quadrants and confidence bands.
- *Data:* `D0` · *Effort:* S

**G5 · Conditional win rates / threshold mining** ★
- *Question:* At what point does a game swing?
- *Method:* for each player/team metric, find thresholds (e.g. jungler ≥ 4 kills)
  where WR separates; report lift, `n` and a multiple-comparison warning.
- *Data:* `D0` · *Effort:* M
- *Caveat:* data-mined thresholds overfit. Require a held-out split or report
  stability across halves.

**G6 · Hero ablation** ★
- *Question:* What happens to a team if you remove one hero from their pool?
- *Method:* recompute team WR excluding games with that hero; rank by drop.
- *Data:* `D0` · *Effort:* S
- *Caveat:* not causal; roster/opponent confounding.

**G7 · Tournament eagle-eye dashboard** ★
- *Question:* What is the state of the league in one screen?
- *Method:* compose meta snapshot, team tiers, top movers, must-ban list,
  streaks, patch impact.
- *Data:* all · *Effort:* L

**G8 · Patch-note impact analysis** ★
- *Question:* Did the buff/nerf actually change anything?
- *Method:* buffed/nerfed heroes, P/B/WR before vs after, with expected-vs-actual.
- *Data:* `D5` + `D0` · *Effort:* M
- *Caveat:* confounded by meta adaptation; present as observation.

**G9 · Prediction calibration**
- *Question:* Can we trust our own model?
- *Method:* log match predictions from the Bradley-Terry model; track Brier score
  and calibration curve over time.
- *Data:* `D0` · *Effort:* M
- *Use:* credibility. Only ship if calibration is honest.

---

## Part 4 — What other sites already do (don't rebuild parity)

To keep the "unique insight" claim honest:

| Already public | Where | We should |
|---|---|---|
| Hero pick/ban/WR season totals | mlbbhub, id-mpl | match it, don't claim novelty |
| First-ban by side, side WR | mlbbhub drafts | match it; add per-team/patch splits |
| Draft simulator, matchup matrix, tier list | mlbbhub | skip unless we add a real edge |
| Hero pools / player pools | id-mpl | match it; add role normalisation |
| MVP standings | id-mpl, mlbbhub | match it |
| Team Lord/Turtle/Tower season totals | id-mpl | ingest, label as season-level |
| Match drafts and VODs | Liquipedia | ingest and improve the presentation |

**Novelty must come from derivation, not from re-publishing the same table.**

---

## Part 5 — Build order

### Sprint 1 — six insights from data we already have (no new ingestion)

These are `D0`-only and can ship before Phase 1:

1. **Global time bar + patch pins** (Part 1) — the control everything else uses.
2. **Patch meta board** (A1) — the user's original idea, generalized.
3. **Ban efficiency** (B1) — over-banned / under-banned; instantly quotable.
4. **Tempo + gold allocation fingerprint** (D1, D2, D3) — a team identity card.
5. **Lineup combinations** (D5) — coach-relevant, trivial to compute.
6. **Conditional win rates** (G5) — with a stability check to avoid overfitting.

### Sprint 2 — after Phase 1 ingestion

7. **Role-normalised player card** (C1) + **consistency cone** (C5)
8. **Lane head-to-head** (E1) + **weakness radar** (E4)
9. **Hero flex map** (B4) + **respect index** (B2)
10. **Composition archetypes** (F1–F3)
11. **Map-mode profile** (D8)
12. **Scouting report** (E6) — composes the above

### Later

13. Player similarity (C11), style clustering (D9), WAR (C2), patch adoption (A6),
    patch-note impact (G8), eagle-eye dashboard (G7).

---

## Part 6 — Statistical guardrails

Every insight above must obey these, or it will lose a coach's trust:

1. **Show `n` always.** A rate without a denominator is an opinion.
2. **Confidence intervals on rates.** Wilson for proportions; bootstrap for
   ratings.
3. **Shrink small samples.** Never let a 2–0 hero read as "100%".
4. **Label proxies.** Final kill diff is not "closeness"; tower damage is not
   "objective control".
5. **Label correlation.** "Teams that do X win more" ≠ "do X to win".
6. **Multiple comparisons.** Threshold mining (G5) needs a stability check
   across halves or a held-out split.
7. **Deterministic ordering.** Count desc, then id asc — already the house rule.
8. **No silent zeros.** "No data" is a state, not a zero.

---

## Part 7 — Open questions

1. **Does the tournament patch differ from the live patch?** If yes, patch pins
   must follow the tournament, and we should label it explicitly.
2. **Is ban order reliable in Liquipedia?** `b1..b5` look ordered; verify against
   a broadcast before shipping "first ban" claims.
3. **How do we attribute a ban to the opponent?** Bans are per side, not per
   team; side→team mapping is in `games`, so this is solvable but must be tagged.
4. **What is the minimum `n` for a public claim?** Proposal: 5 for display,
   10 for ranking, 20 for a headline.
5. **Do we show uncertainty in the default view, or only on demand?** Proposal:
   always show `n`; show CI on hover and in detail views.
