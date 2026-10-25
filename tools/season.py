"""Season registry resolver.

Single source of truth for per-season paths. Tools accept `--season <id>` and
call `resolve()` instead of hardcoding file names, so adding a season is a
registry + data change rather than an application-code change.

Layouts:
- "legacy"     paths live at their historical locations (Season 18 today).
- "season-dir" paths default to data/seasons/<id>/ (future seasons).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "data" / "registry.json"


def registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def ids():
    return [s["id"] for s in registry()["seasons"]]


def resolve(season_id=None):
    """Return absolute paths for a season. Raises SystemExit on unknown id."""
    reg = registry()
    sid = season_id or reg.get("default")
    entry = next((s for s in reg["seasons"] if s["id"] == sid), None)
    if entry is None:
        raise SystemExit(f"unknown season {sid!r}; known: {', '.join(ids())}")

    layout = entry.get("layout", "season-dir")
    if layout == "season-dir":
        defaults = {
            "config": f"data/seasons/{sid}/season.json",
            "database": f"data/seasons/{sid}/mpl_id_{sid}.db",
            "csvDir": f"data/seasons/{sid}/csv",
            "playoffs": f"data/seasons/{sid}/playoffs.json",
            "meta": f"data/seasons/{sid}/meta.json",
            "patches": f"data/seasons/{sid}/patches.json",
        }
    else:
        defaults = {
            "config": "data/season.json",
            "database": "data/mpl_id_s18.db",
            "csvDir": "data/csv",
            "playoffs": "data/playoffs.json",
            "meta": f"data/seasons/{sid}/meta.json",
            "patches": f"data/seasons/{sid}/patches.json",
        }

    out = {"id": sid, "displayName": entry.get("displayName", sid), "layout": layout}
    for key, default in defaults.items():
        value = entry.get(key, default)
        out[key] = (ROOT / value) if value else None
    return out


if __name__ == "__main__":
    import sys
    s = resolve(sys.argv[1] if len(sys.argv) > 1 else None)
    for k, v in s.items():
        print(f"{k:12s} {v}")
