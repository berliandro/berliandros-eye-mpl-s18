"""Parity gate: regen must be byte-identical unless data/templates changed on purpose.
Usage: python tools/check_parity.py
Exit 0 = PASS, 1 = FAIL.
"""
import hashlib
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent
ROOT = BASE.parent
OUT = ROOT / 'mpl_id_s18_dark.html'

before = OUT.read_bytes()
h_before = hashlib.sha256(before).hexdigest()

r = subprocess.run([sys.executable, str(BASE / 'gen_dark.py')], capture_output=True, text=True)
print(r.stdout.strip())
if r.returncode != 0:
    print("FAIL: gen_dark.py crashed")
    print(r.stderr[-2000:])
    sys.exit(1)

after = OUT.read_bytes()
h_after = hashlib.sha256(after).hexdigest()

errors = []
if h_before != h_after:
    errors.append(f"byte mismatch: {h_before[:12]} -> {h_after[:12]} (regen changed output)")
txt = after.decode('utf-8', errors='replace')
for token in ('__DATA__', '__CSS__', '__JS__', '__ASSETS__', '__TEAMS__', '__SEASON__'):
    if token in txt:
        errors.append(f"leftover placeholder {token}")
for needle in ('id="board"', 'data-view="overview"', 'trendChart', 'wireCharts'):
    if needle not in txt:
        errors.append(f"missing expected {needle}")

if errors:
    print("FAIL:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"PASS parity {h_after[:12]} ({len(after)} bytes)")
