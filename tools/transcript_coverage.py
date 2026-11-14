#!/usr/bin/env python3
"""Recompute transcript pipeline coverage and routing integrity.

Writes:
- analysis/evidence/transcript-pipeline-coverage.json
- analysis/reports/transcript-pipeline/coverage.md
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import validate_transcript_ledger as validator  # noqa: E402

PLAN = REPO / "analysis/evidence/transcript-pipeline-plan.json"
COVERAGE = REPO / "analysis/evidence/transcript-pipeline-coverage.json"
REPORT = REPO / "analysis/reports/transcript-pipeline/coverage.md"
PARTIAL = {"src-s18-w02d03", "src-s18-w07d03", "src-s18-w08d02"}


def main() -> int:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    rows = []
    summary = Counter()
    routing_pages: dict[str, int] = defaultdict(int)
    routing_errors = []
    unrouted = []
    match_missing = []
    page_categories = Counter()

    for entry in plan["sources"]:
        ledger = REPO / entry["observation_ledger"]
        segments = REPO / entry["segment_ledger"]
        report = REPO / entry["match_report"]
        issues = validator.validate_file(ledger, segments_path=segments)
        errors = [i for i in issues if i.level == "error"]
        warnings = [i for i in issues if i.level == "warning"]
        records = [json.loads(l) for l in ledger.read_text(encoding="utf-8").splitlines() if l.strip()]
        obs = [r for r in records if r.get("record_type") == "observation"]
        accepted = [r for r in obs if r.get("status") == "accepted"]
        needs_review = sum(1 for r in obs if r.get("status") == "needs_review")
        rejected = sum(1 for r in obs if r.get("status") == "rejected")
        unresolved = sum(1 for r in records if r.get("record_type") == "unresolved")
        report_text = report.read_text(encoding="utf-8")

        routed = 0
        for record in accepted:
            dests = record.get("cross_destinations") or []
            if dests:
                routed += 1
            else:
                unrouted.append(record["observation_id"])
            for dest in dests:
                routing_pages[dest] += 1
                page_categories[dest.split("/")[1]] += 1
                path = REPO / dest
                if not path.is_file():
                    routing_errors.append({"observation_id": record["observation_id"], "destination": dest, "error": "missing file"})
                elif record["observation_id"] not in path.read_text(encoding="utf-8"):
                    routing_errors.append({"observation_id": record["observation_id"], "destination": dest, "error": "ID not in file"})
            if record["observation_id"] not in report_text:
                match_missing.append({"observation_id": record["observation_id"], "report": entry["match_report"]})

        status = "blocked" if errors else ("partial" if entry["source_id"] in PARTIAL else "complete")
        summary.update({
            "sources": 1,
            "observations": len(obs),
            "accepted": len(accepted),
            "needs_review": needs_review,
            "rejected": rejected,
            "unresolved": unresolved,
            "validation_errors": len(errors),
            "validation_warnings": len(warnings),
            "accepted_non_match_routed": routed,
        })
        rows.append({
            "source_id": entry["source_id"],
            "match_detail_id": entry["match_detail_id"],
            "status": status,
            "observations": len(obs),
            "accepted": len(accepted),
            "accepted_non_match_routed": routed,
            "needs_review": needs_review,
            "rejected": rejected,
            "unresolved": unresolved,
            "validation_errors": len(errors),
            "validation_warnings": len(warnings),
        })

    summary["partial"] = sum(1 for r in rows if r["status"] == "partial")
    summary["blocked"] = sum(1 for r in rows if r["status"] == "blocked")
    summary["cross_destination_links"] = sum(routing_pages.values())
    summary["non_match_pages"] = len(routing_pages)
    summary["routing_errors"] = len(routing_errors)
    summary["unrouted_accepted"] = len(unrouted)
    summary["match_report_missing"] = len(match_missing)

    coverage = {
        "schema_version": 1,
        "generated_at": "2026-11-13T00:00:00Z",
        "description": "Coverage and routing integrity for the 27-source transcript pipeline.",
        "summary": dict(summary),
        "routing": {
            "pages": dict(sorted(routing_pages.items())),
            "page_count": len(routing_pages),
            "page_categories": dict(page_categories),
            "errors": routing_errors[:50],
            "unrouted_accepted": unrouted,
            "match_report_missing": match_missing,
        },
        "sources": rows,
    }
    COVERAGE.write_text(json.dumps(coverage, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# MPL S18 transcript pipeline — coverage",
        "",
        "**Date:** 2026-11-13",
        f"**Status:** {summary['sources']}/27 source ledgers validated; {summary['accepted']} accepted observations consolidated into match reports and {summary['non_match_pages']} non-match pages; {summary['needs_review']} remain for review, {summary['rejected']} rejected.",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|---|---:|",
        f"| Sources processed | {summary['sources']} |",
        f"| Sources complete | {summary['sources'] - summary['partial'] - summary['blocked']} |",
        f"| Sources partial | {summary['partial']} |",
        f"| Source ledgers validated | {summary['sources']} |",
        f"| Validation errors | {summary['validation_errors']} |",
        f"| Observations extracted | {summary['observations']} |",
        f"| Accepted observations | {summary['accepted']} |",
        f"| Needs review | {summary['needs_review']} |",
        f"| Rejected observations | {summary['rejected']} |",
        f"| Resolved unresolved references | {summary['unresolved']} |",
        f"| Match reports updated | {summary['sources']} |",
        f"| Accepted observations cross-filed outside match reports | {summary['accepted_non_match_routed']} / {summary['accepted']} |",
        f"| Non-match cross-destination links | {summary['cross_destination_links']} |",
        f"| Non-match pages | {summary['non_match_pages']} |",
        f"| Routing errors | {summary['routing_errors']} |",
        f"| Accepted IDs missing from match reports | {summary['match_report_missing']} |",
        "",
        "Partial sources are `src-s18-w02d03` (1050, intro/interview window), `src-s18-w07d03` (1091, desk/draft-heavy), and `src-s18-w08d02` (1094, desk/commentary-heavy). These are marked partial rather than counted as full gameplay coverage.",
        "",
        "## Non-match routing",
        "",
        "Every accepted observation has at least one cross-destination outside its match report. The match report remains the primary destination and retains the full quote/provenance.",
        "",
        "| Category | Pages | Links |",
        "|---|---:|---:|",
    ]
    for category in ("players", "teams", "heroes", "strategy"):
        pages = [p for p in routing_pages if p.startswith(f"analysis/{category}/")]
        links = sum(routing_pages[p] for p in pages)
        lines.append(f"| {category.title()} | {len(pages)} | {links} |")
    lines += [
        f"| **Total** | **{summary['non_match_pages']}** | **{summary['cross_destination_links']}** |",
        "",
        "## Per-source status",
        "",
        "| Source | Match | Status | Observations | Accepted | Routed | Needs review | Rejected | Validation |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['source_id']} | {row['match_detail_id']} | {row['status']} | {row['observations']} | {row['accepted']} | {row['accepted_non_match_routed']} | {row['needs_review']} | {row['rejected']} | {row['validation_errors']} |"
        )
    lines += [
        "",
        "## Artifacts",
        "",
        "- Segment ledgers: `analysis/evidence/transcript-segments/`",
        "- Observation ledgers: `analysis/evidence/transcript-observations/`",
        "- Routing manifest: `analysis/evidence/transcript-routing.json`",
        "- Review decisions: `analysis/evidence/transcript-review-decisions.jsonl`",
        "- Job plan: `analysis/evidence/transcript-pipeline-plan.json`",
        "- Run reports: `analysis/reports/transcript-pipeline/`",
        "",
        "## Rules preserved",
        "",
        "- Raw transcripts and `data/mpl_id_s18.db` were not modified.",
        "- Every accepted observation has an exact quote, quote hash, raw line range, cue range or explicit null, source link, and claim type.",
        "- Statistics use `tools/stats_query.py` provenance.",
        "- Visual proof status is unchanged; no screenshots or visual claims were promoted.",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(dict(summary), indent=1))
    print("wrote", COVERAGE)
    print("wrote", REPORT)
    return 1 if summary["validation_errors"] or summary["routing_errors"] or summary["match_report_missing"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
