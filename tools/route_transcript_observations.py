#!/usr/bin/env python3
"""Route accepted transcript observations to player/team/hero/strategy pages.

The match report remains the primary destination. Cross-destinations are added
to the staging ledger and rendered as compact, source-linked entries on the
non-match pages. No raw transcript or canonical database mutation.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLAN = REPO / "analysis/evidence/transcript-pipeline-plan.json"
PLAYERS_INDEX = REPO / "analysis/index.md"

TEAM_NAMES = {
    "AE": "ALTER EGO ESPORTS",
    "BTR": "BIGETRON BY VIT",
    "DEWA": "DEWA UNITED",
    "EVOS": "EVOS",
    "GEEK": "GEEK FAM",
    "NAVI": "NAVI",
    "ONIC": "ONIC",
    "RRQ": "RRQ HOSHI",
    "TLID": "TEAM LIQUID ID",
}

PLAYER_ALIASES = {
    "ALBERT": "ALBERTTT",
    "ALBERTTT": "ALBERTTT",
    "RENDY": "RENDYYY",
    "RANDY": "RENDYYY",
    "RENDYYY": "RENDYYY",
    "MUEZA": "MUEZZA",
    "MUZA": "MUEZZA",
    "MUEZZA": "MUEZZA",
    "MORENO": "MORENOOO",
    "MORENOOO": "MORENOOO",
    "HAZEL": "HAZLE",
    "HAZLE": "HAZLE",
    "FAVIAN": "FAVIANNN",
    "FAVIANNN": "FAVIANNN",
    "MAYBE": "MAYBEEE",
    "MAYBEEE": "MAYBEEE",
    "SAMUEL": "SSAMUEL",
    "SSAMUEL": "SSAMUEL",
    "ZEON": "ZEONN",
    "ZEONN": "ZEONN",
    "RIZA": "RYZAA",
    "RYZAA": "RYZAA",
    "NNAEL": "NNAEL",
    "DALVIN": "DALVIN",
    "JOSHUA": "JOSHUA",
    "NINO": "NINO",
    "SAID": "SAID",
    "HAJIRIN": "HAJIRIN",
    "KAIRI": "KAIRI",
    "KEVIN": "KEVIN",
    "ARAN": "ARAN",
    "KELRA": "KELRA",
    "KIBOY": "KIBOY",
    "DEMONKITE": "DEMONKITE",
    "ARTHUR": "ARTHUR",
    "CLAY": "CLAYYY",
    "DRIAN": "DRIANW",
    "DRIANW": "DRIANW",
}

HERO_ALIASES = {"PAKITO": "PAQUITO"}
CANONICAL_HEROES = {
    "PAQUITO", "MARCEL", "NOLAN", "EUDORA", "MELISSA", "RAFAELA", "SELENA",
    "ATLAS", "FREYA", "KIMMY", "BELERICK", "TIGREAL", "BARATS", "URANUS",
    "MOSKOV", "LILIA", "HILDA", "DYRROTH", "ZHUXIN", "AULUS", "HAYABUSA",
}

STRATEGY_BY_TOPIC = {
    "draft": "analysis/strategy/draft.md",
    "objective": "analysis/strategy/objectives.md",
    "macro": "analysis/strategy/macro-map.md",
    "map": "analysis/strategy/macro-map.md",
    "micro": "analysis/strategy/micro.md",
    "patch": "analysis/strategy/patch-meta.md",
    "meta": "analysis/strategy/patch-meta.md",
}


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def load_player_paths() -> dict[str, str]:
    paths: dict[str, str] = {}
    for line in PLAYERS_INDEX.read_text(encoding="utf-8").splitlines():
        if "[dossier](" not in line:
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 4:
            continue
        match = re.search(r"\((players/[^)]+)\)", parts[3])
        if match:
            paths[parts[0].upper()] = match.group(1)
    return paths


def format_clock(seconds: float | None) -> str:
    if seconds is None:
        return "timestamp n/a"
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def claim_teams(claim: str, entity_teams: list[str]) -> set[str]:
    upper = claim.upper()
    found = set()
    for code, name in TEAM_NAMES.items():
        aliases = {code.upper(), name.upper()}
        if any(re.search(rf"(?<![A-Z0-9]){re.escape(alias)}(?![A-Z0-9])", upper) for alias in aliases):
            found.add(code)
    return found or set(entity_teams)


def claim_players(claim: str, entity_players: list[str]) -> set[str]:
    upper = claim.upper()
    found = set()
    for alias, canonical in PLAYER_ALIASES.items():
        if re.search(rf"(?<![A-Z0-9]){re.escape(alias)}(?![A-Z0-9])", upper):
            found.add(canonical)
    if found:
        return found
    for name in entity_players:
        canonical = PLAYER_ALIASES.get(name.upper())
        if canonical:
            found.add(canonical)
    return found


def claim_heroes(claim: str, entity_heroes: list[str]) -> set[str]:
    upper = claim.upper()
    found = set()
    for hero in CANONICAL_HEROES:
        if re.search(rf"(?<![A-Z0-9]){re.escape(hero)}(?![A-Z0-9])", upper):
            found.add(hero)
    if found:
        return found
    for name in entity_heroes:
        canonical = HERO_ALIASES.get(name.upper(), name.upper())
        if canonical in CANONICAL_HEROES:
            found.add(canonical)
    return found


def entry_line(record: dict, match_id: str, report_name: str, page_dir: str) -> str:
    claim = str(record.get("claim", "")).replace("\n", " ").strip()
    link = record.get("timestamp_link")
    source = f"[source]({link})" if link else "source timestamp n/a"
    rel_report = f"../matches/{report_name}"
    return (
        f"- `{record['observation_id']}` · match {match_id} · "
        f"{format_clock(record.get('cue_start'))} · *{record.get('claim_type')}* — "
        f"{claim} ([match]({rel_report}), {source})"
    )


def render_page(title: str, subtitle: str, entries: list[str], out_path: Path) -> None:
    lines = [
        f"# {title}",
        "",
        subtitle,
        "",
        "## Accepted transcript observations",
        "",
        "Only accepted, source-linked observations are listed. Caster claims are commentary, not proof of an in-game event. Full quotes and provenance remain in the linked match reports.",
        "",
    ] + entries + [
        "",
        "## Limits",
        "",
        "- This page is a cross-file index; it does not duplicate full quotations.",
        "- Raw transcripts and the canonical database remain unchanged.",
        "- No visual claim is promoted here.",
        "",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def upsert_player_section(path: Path, entries: list[str]) -> None:
    section = [
        "## Transcript observations (accepted)",
        "",
        "<!-- transcript-routing:start -->",
        "Accepted, source-linked observations. Caster claims are commentary, not proof of an in-game event.",
        "",
    ] + entries + [
        "<!-- transcript-routing:end -->",
        "",
    ]
    text = path.read_text(encoding="utf-8")
    start = text.find("<!-- transcript-routing:start -->")
    end = text.find("<!-- transcript-routing:end -->")
    if start >= 0 and end > start:
        text = text[:start] + "\n".join(section[2:]) + text[end + len("<!-- transcript-routing:end -->"):]
    else:
        marker = "## References"
        block = "\n".join(section)
        if marker in text:
            text = text.replace(marker, block + "\n" + marker, 1)
        else:
            text += "\n" + block
    path.write_text(text, encoding="utf-8")


def main() -> int:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    player_paths = load_player_paths()
    pages: dict[str, list[str]] = defaultdict(list)
    page_titles: dict[str, tuple[str, str]] = {}
    routed = 0
    total_cross = 0
    missing_players = Counter()

    for entry in plan["sources"]:
        ledger_path = REPO / entry["observation_ledger"]
        records = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        match_id = entry["match_detail_id"]
        report_name = Path(entry["match_report"]).name
        for record in records:
            if record.get("record_type") != "observation" or record.get("status") != "accepted":
                continue
            routed += 1
            entities = record.get("entities") or {}
            claim = str(record.get("claim", ""))
            cross: set[str] = set()

            for team in claim_teams(claim, list(entities.get("teams") or [])):
                path = f"analysis/teams/{team.lower()}.md"
                cross.add(path)
                pages[path].append(entry_line(record, match_id, report_name, "teams"))
                page_titles[path] = (f"{team} — {TEAM_NAMES[team]} transcript notes", f"Team page for {TEAM_NAMES[team]} ({team}).")

            for player in claim_players(claim, list(entities.get("players") or [])):
                rel = player_paths.get(player)
                if not rel:
                    missing_players[player] += 1
                    continue
                path = f"analysis/{rel}"
                cross.add(path)
                pages[path].append(entry_line(record, match_id, report_name, "players"))

            for hero in claim_heroes(claim, list(entities.get("heroes") or [])):
                path = f"analysis/heroes/{slug(hero)}.md"
                cross.add(path)
                pages[path].append(entry_line(record, match_id, report_name, "heroes"))
                page_titles[path] = (f"{hero.title()} — transcript notes", f"Hero page for {hero.title()}. ASR spellings are preserved in the source quote; this page uses the canonical name where clear.")

            topic = str(record.get("topic", "other"))
            strategy_path = STRATEGY_BY_TOPIC.get(topic)
            if strategy_path is None and topic in {"team", "player", "hero", "other"}:
                strategy_path = "analysis/strategy/index.md"
            if strategy_path:
                cross.add(strategy_path)
                pages[strategy_path].append(entry_line(record, match_id, report_name, "strategy"))
                if strategy_path not in page_titles:
                    label = Path(strategy_path).stem.replace("-", " ").title()
                    page_titles[strategy_path] = (f"{label} — transcript notes", f"Transcript-derived {label.lower()} observations.")

            record["cross_destinations"] = sorted(cross)
            total_cross += len(cross)
        ledger_path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")

    # Create team/hero/strategy pages.
    for path, entries in pages.items():
        if path.startswith("analysis/players/"):
            continue
        title, subtitle = page_titles.get(path, (Path(path).stem.replace("-", " ").title(), "Transcript-derived observations."))
        render_page(title, subtitle, entries, REPO / path)

    # Upsert player sections.
    for path, entries in pages.items():
        if path.startswith("analysis/players/"):
            upsert_player_section(REPO / path, entries)

    manifest = {
        "schema_version": 1,
        "generated_at": "2026-11-13T00:00:00Z",
        "accepted_observations": routed,
        "cross_destination_links": total_cross,
        "pages": {path: len(entries) for path, entries in sorted(pages.items())},
        "missing_player_pages": dict(missing_players),
    }
    out = REPO / "analysis/evidence/transcript-routing.json"
    out.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("accepted", routed, "cross links", total_cross, "pages", len(pages))
    print("missing player pages", dict(missing_players))
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
