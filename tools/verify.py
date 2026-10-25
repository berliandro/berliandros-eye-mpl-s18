"""Standard verification workflow (Area 4): the single documented regression
command. Runs every required suite in order and fails clearly (never silently
skips) when a runtime or suite is missing. No network access required.
Usage: python tools/verify.py
Exit 0 = all suites pass.
"""
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent
ROOT = BASE.parent

STEPS = [
    ("node --check app.js", ["node", "--check", str(BASE / "templates" / "app.js")], "node"),
    ("probability engine", ["node", str(BASE / "test_chances.js")], "node"),
    ("analytics engine", ["node", str(BASE / "test_analytics.js")], "node"),
    ("snapshot derivation", ["node", str(BASE / "test_snapshot.js")], "node"),
    ("cross-view reconciliation", [sys.executable, str(BASE / "test_reconcile.py")], None),
    ("xss sink units", ["node", str(BASE / "test_xss.js")], "node"),
    ("transforms + fetch retry", ["node", str(BASE / "test_transforms.js")], "node"),
    ("item category classifier", ["node", str(BASE / "test_item_classes.js")], "node"),
    ("alias registry", [sys.executable, str(BASE / "test_aliases.py")], "python"),
    ("draft/lane enrichment", [sys.executable, str(BASE / "test_enrich.py")], None),
    ("hero classes", [sys.executable, str(BASE / "test_hero_classes.py")], None),
    ("team aggregates", [sys.executable, str(BASE / "test_aggregates.py")], None),
    ("refresh merge", ["node", str(BASE / "test_refresh.js")], "node"),
    ("cache versioning", ["node", str(BASE / "test_cache.js")], "node"),
    ("liquipedia parser + ETL gates", [sys.executable, str(BASE / "test_liqparse.py")], None),
    ("schedule VOD resolver + metadata gates", [sys.executable, str(BASE / "test_resolve_and_align_sources.py")], None),
    ("yt-dlp JavaScript runtime selection", [sys.executable, str(BASE / "test_link_video_source.py")], None),
    ("match winner orientation repair", [sys.executable, str(BASE / "test_repair_match_winner_orientation.py")], None),
    ("database inventory warning accuracy", [sys.executable, str(BASE / "test_analysis_inventory.py")], None),
    ("season config (python)", [sys.executable, str(BASE / "test_config.py")], None),
    ("season config (node)", ["node", str(BASE / "test_config.js")], "node"),
    ("ruff lint (pip install ruff if missing)", [sys.executable, "-m", "ruff", "check", "tools/",
     "--select", "F401,F841,E722,E9", "--line-length", "200"], None),
    ("data integrity + assets + JS syntax", [sys.executable, str(BASE / "check.py")], None),
    ("generated-output parity", [sys.executable, str(BASE / "check_parity.py")], None),
]

results = []
for name, cmd, runtime in STEPS:
    if runtime and not shutil.which(runtime):
        print(f"FAIL {name}: required runtime '{runtime}' not found on PATH")
        results.append((name, False))
        continue
    try:
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=600)
    except FileNotFoundError:
        print(f"FAIL {name}: executable not found: {cmd[0]}")
        results.append((name, False))
        continue
    tail = (r.stdout.strip().splitlines() or ["(no output)"])[-3:]
    print(f"--- {name} (exit {r.returncode})")
    for line in tail:
        print("    " + line)
    if r.returncode != 0:
        # On failure, preserve enough diagnostics to identify the actual cause.
        # The old five-line stderr tail hid unittest assertion names and Ruff locations.
        diagnostics = (r.stdout + "\\n" + r.stderr).strip().splitlines()
        for line in diagnostics[-80:]:
            print("    ! " + line)
        results.append((name, False))
    else:
        results.append((name, True))

bad = [n for n, ok_ in results if not ok_]
print()
if bad:
    print(f"VERIFY FAIL ({len(bad)}/{len(results)} suites failed): " + ", ".join(bad))
    sys.exit(1)
print(f"VERIFY PASS ({len(results)}/{len(results)} suites)")
