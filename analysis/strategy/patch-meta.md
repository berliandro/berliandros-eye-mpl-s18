# Patch Meta — transcript notes

Transcript-derived patch meta observations.

## Evidence-backed analysis

**There is no patch field.** The canonical database records dates, not patch/version identifiers. Do not split the season into patches from memory or from the broadcast's wording. Any "patch meta" claim needs a dated patch map added to the evidence layer first.

**Calendar split is not a patch split.** The completed season has 24 series / 57 games in August, 23 / 52 in September, and 25 / 65 in October. That is scheduling, not a ruleset boundary. Use it only as a coarse time split and label it as such.

**Rule-change evidence is transcript-only.** 1084 describes the healing Turtle rework: it now grants revitalize and targets the strongest enemy tower instead of shielding allies (`TOBS-1084-G1-001`, `-002`). 1076 mentions a gold reduction that may reactivate tank junglers (`TOBS-1076-G1-007`). 1091 explains the golden turret's 3,960 gold distribution (`TOBS-1091-G1-005`). These are caster explanations, not verified patch notes.

**What can be said honestly.** If a hero's usage or a team's results change across months, report the change and label the cause unknown. Do not attribute it to a patch without patch metadata. Do not compare a pre-change and post-change sample as if the rules were constant.

**Action to make this real.** Add a dated patch map or a `patch_id` column to the evidence layer, tag each game, then re-run `tools/build_league_aggregates.py`. Until then, this page stays a limits page, not a patch-tier list.

## Accepted transcript observations

Only accepted, source-linked observations are listed. Caster claims are commentary, not proof of an in-game event. Full quotes and provenance remain in the linked match reports.

- `TOBS-1050-G1-006` · match 1050 · 05:50:29 · *commentary* — The caster agrees that coaching changes matter less than whether players can execute. ([match](../matches/1050-onic-vs-btr.md), [source](https://youtu.be/C-H_iCLxtL8?t=21029))
- `TOBS-1076-G1-007` · match 1076 · 01:08:43 · *commentary* — Patch gold reduction may reactivate tank junglers. ([match](../matches/1076-onic-vs-geek.md), [source](https://youtu.be/wRRWT8fO_h0?t=4123))
- `TOBS-1084-G1-001` · match 1084 · 00:52:41 · *commentary* — The caster explains the new healing turtle objective now grants revitalize and no longer shields allies, moving toward the strongest enemy lane. ([match](../matches/1084-geek-vs-btr.md), [source](https://youtu.be/Nd_s3qCnRPY?t=3161))
- `TOBS-1068-G1-001` · match 1068 · 00:49:28 · *commentary* — The caster introduces the series as the first match of the day: EVOS vs Dewa United. ([match](../matches/1068-evos-vs-dewa.md), [source](https://youtu.be/7Fk2t0Kc9-Q?t=2968))
- `TOBS-1098-G1-001` · match 1098 · 04:57:35 · *commentary* — The caster frames the match as a life-or-death playoff decider for RRQ. ([match](../matches/1098-rrq-vs-onic.md), [source](https://youtu.be/jz3rH4xDoak?t=17855))
- `TOBS-1098-G1-003` · match 1098 · 05:05:51 · *commentary* — The caster outlines the scenario where ONIC wins game 3 and RRQ is eliminated. ([match](../matches/1098-rrq-vs-onic.md), [source](https://youtu.be/jz3rH4xDoak?t=18351))

## Limits

- This page is a cross-file index; it does not duplicate full quotations.
- Raw transcripts and the canonical database remain unchanged.
- No visual claim is promoted here.
