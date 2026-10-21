"""Alias-registry tests: season-independent identity data is committed as data,
is complete, and app.js no longer carries hardcoded maps.

Usage: python tools/test_aliases.py   (exit 0 = pass)
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALIASES = json.loads((ROOT / "data" / "global" / "aliases.json").read_text(encoding="utf-8"))
APP = (ROOT / "tools" / "templates" / "app.js").read_text(encoding="utf-8")
LANES = {"EXP", "JUNGLE", "MID", "GOLD", "ROAM", "FLEX"}

fails = 0


def ok(cond, msg):
    global fails
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails += 1


# The five maps that used to live in app.js.
expected = {
    "playerAlias": 14,
    "seasonAlias": 7,
    "globalAlias": 7,
    "lanes": 66,
    "rosterSpelling": 1,
}
for key, count in expected.items():
    section = ALIASES.get(key)
    ok(isinstance(section, dict) and len(section) == count,
       f"aliases.{key} has {count} entries")

# Identity sections: normalized keys, non-empty values.
for key in expected:
    section = ALIASES.get(key, {})
    ok(all(re.fullmatch(r"[a-z0-9]+", k or "") for k in section),
       f"aliases.{key} keys are normalized")
    ok(all(isinstance(v, str) and v.strip() for v in section.values()),
       f"aliases.{key} values are non-empty strings")

# Lanes must be real roles.
bad = sorted({v for v in ALIASES.get("lanes", {}).values() if v not in LANES})
ok(not bad, f"all lane values are valid roles (bad: {bad[:5]})")

# The app must read the embedded registry, not carry the literals.
ok("window.ALIASES" in APP, "app.js reads window.ALIASES")
ok("const PLAYER_ALIAS=" in APP and "AL.playerAlias" not in APP,
   "player alias map is data-driven")
ok("merge(window.ALIASES" not in APP, "no accidental merge helper")

# No hardcoded object literals should remain for these names.
for name in ("PLAYER_ALIAS", "SALIAS", "GALIAS", "LIQLANES", "ROSTER_SPELLING"):
    literal = re.search(r"const " + name + r"=\{[^}]*:[^}]*\}", APP)
    ok(literal is None, f"no hardcoded {name} literal in app.js")
    guarded = re.search(r"const " + name + r"=.*window\.ALIASES", APP)
    ok(guarded is not None, f"{name} resolves through window.ALIASES")

print(f"\n{'ALL ALIAS TESTS PASSED' if not fails else str(fails) + ' ALIAS TEST(S) FAILED'}")
raise SystemExit(1 if fails else 0)
