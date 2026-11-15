#!/usr/bin/env python3
"""Generate missing hero pages from canonical aggregates and accepted observations.

Existing hero pages are never overwritten. New pages carry the same
"## Evidence-backed profile" marker used by the coverage matrix.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AGG = REPO / "analysis" / "evidence" / "league-aggregates.json"
HERO_DIR = REPO / "analysis" / "heroes"
OBS_DIR = REPO / "analysis" / "evidence" / "transcript-observations"


def slug(name: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return value


def pct(value) -> str:
    return "—" if value is None else f"{value * 100:.1f}%"


def main() -> int:
    aggregates = json.loads(AGG.read_text(encoding="utf-8"))
    hero_rows = aggregates["heroes"]

    observations = []
    for path in sorted(OBS_DIR.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                if row.get("status") == "accepted":
                    observations.append(row)

    by_hero: dict[str, list[dict]] = defaultdict(list)
    for row in observations:
        for hero in row.get("entities", {}).get("heroes") or []:
            by_hero[str(hero).casefold()].append(row)

    existing = {p.stem for p in HERO_DIR.glob("*.md")}
    created = []
    for row in hero_rows:
        hero = str(row["hero"])
        page = HERO_DIR / f"{slug(hero)}.md"
        if page.stem in existing or page.exists():
            continue
        picks = int(row.get("picks") or 0)
        wins = int(row.get("wins") or 0)
        bans = int(row.get("bans") or 0)
        rate = row.get("win_rate")
        contest = row.get("contest_rate")
        team_items = sorted(
            (
                (team, int(data.get("picks") or 0), int(data.get("wins") or 0), data.get("win_rate"))
                for team, data in (row.get("teams") or {}).items()
            ),
            key=lambda item: (-item[1], item[0]),
        )
        top_teams = ", ".join(
            f"{team} {wins}-{p - wins} ({pct(rate)})"
            for team, p, wins, rate in team_items[:4]
        ) or "none"
        players = ", ".join(f"{entry['player']} ({entry['picks']})" for entry in (row.get("top_players") or [])[:4]) or "none"

        if picks >= 40:
            read = (
                f"High-volume pick ({picks} games). The season rate is {pct(rate)}, but the team split is the actionable part: "
                f"{top_teams}. Treat it as a system pick, not a universal priority."
            )
        elif picks >= 15:
            read = (
                f"Rotation pick ({picks} games at {pct(rate)}). The sample is large enough to describe a tendency, "
                "not to assign a causal tier."
            )
        elif picks >= 1:
            read = (
                f"Small-sample pick ({picks} game{'s' if picks != 1 else ''} at {pct(rate)}). "
                "Do not infer a tier or a matchup rule from this volume."
            )
        else:
            read = (
                f"No picks recorded; {bans} bans. This page records ban pressure only; there is no win-rate evidence."
            )

        if picks >= 15 and rate is not None and rate < 0.45:
            counter = "The volume is losing. The burden is on a team-specific matchup explanation, not on a generic 'priority' label."
        elif team_items and len(team_items) >= 2 and (team_items[0][3] or 0) - (team_items[-1][3] or 0) >= 0.30:
            counter = "The same hero ranges widely by team; team context dominates the season rate."
        elif picks >= 1 and rate is not None and rate > 0.55:
            counter = "The rate is above 55%, but it is descriptive; check the team split before treating it as a rule."
        else:
            counter = "The season rate is descriptive; it does not identify a cause."

        transcript = by_hero.get(hero.casefold(), [])
        if transcript:
            obs_lines = ["## Accepted transcript observations", "", "Only accepted records tagged with this hero are listed.", ""]
            for obs in transcript[:6]:
                obs_lines.append(
                    f"- `{obs['observation_id']}` · *{obs.get('claim_type', 'observation')}* — {str(obs.get('claim', '')).strip()}"
                )
        else:
            obs_lines = ["## Transcript observations", "", "No accepted transcript observation names this hero. This page is database-only."]

        text = "\n".join([
            f"# {hero} — evidence profile",
            "",
            f"Hero page for {hero}. Generated from the canonical database snapshot; transcript observations are listed only when an accepted ledger record is tagged with this hero.",
            "",
            "## Evidence-backed profile",
            "",
            f"**Season:** {picks} picks ({picks / 174 * 100:.1f}% of 174 games), {wins} wins ({pct(rate)}), {bans} bans, {pct(contest)} contest rate. "
            "Source: `Q-ALL-HERO-STATS`, `Q-ALL-PICKS`, `Q-ALL-BANS`, snapshot `mpl-s18-db-20c5ea2c51f3`.",
            "",
            f"**Team split:** {top_teams}.",
            "",
            f"**Top players:** {players}.",
            "",
            f"**Read.** {read}",
            "",
            f"**Counterexample/limit.** {counter}",
            "",
            *obs_lines,
            "",
            "## Limits",
            "",
            "- Descriptive only; no causal identification.",
            "- No patch/version field, so this is a season aggregate, not a patch tier.",
            "- Hero win rate is confounded by team strength, player skill and matchup.",
            "- The database has no pick order, objective counts, vision or communications.",
            "",
        ])
        page.write_text(text, encoding="utf-8")
        created.append(page.name)

    print(json.dumps({"created": len(created), "files": created}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
