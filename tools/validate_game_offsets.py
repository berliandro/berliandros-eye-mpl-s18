#!/usr/bin/env python3
import json
import csv
from pathlib import Path
from collections import defaultdict

REPO = Path(__file__).resolve().parent.parent
OFF = REPO / "analysis" / "evidence" / "game-offsets.json"
SCHED = REPO / "data" / "csv" / "schedule_all.csv"
MANIFEST = REPO / "analysis" / "sources" / "source-manifest.json"

def main():
    offs = json.loads(OFF.read_text(encoding='utf-8'))
    manifest = {s['source_id']: s for s in json.loads(MANIFEST.read_text(encoding='utf-8'))['sources']}
    sched = defaultdict(list)
    with open(SCHED, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['status'] == 'completed':
                sched[r['iso_date']].append(r)
    for k in sched:
        sched[k].sort(key=lambda x: x['iso_datetime'])
    
    errors = []
    warnings = []
    for sid, data in offs['sources'].items():
        bd = data.get('broadcast_date')
        if sid not in manifest:
            errors.append(f"{sid}: not in manifest")
            continue
        if bd in sched:
            expected = [s['match_detail_id'] for s in sched[bd]]
            got = [s['match_detail_id'] for s in data['series']]
            if expected != got:
                errors.append(f"{sid}: series mismatch expected {expected} got {got}")
        for s in data['series']:
            if not s.get('provenance'):
                errors.append(f"{sid}/{s['match_detail_id']}: missing provenance")
        if any(x.get('confidence') == 'low' for x in data['series']):
            warnings.append(f"{sid}: has low confidence entries")
    
    result = {"errors": errors, "warnings": warnings[:10], "ok": len(errors) == 0, "sources_checked": len(offs['sources'])}
    print(json.dumps(result, indent=2))
    return 0 if result['ok'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
