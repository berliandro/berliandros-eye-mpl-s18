#!/usr/bin/env python3
import json
import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "analysis" / "sources" / "source-manifest.json"
SCHED = REPO / "data" / "csv" / "schedule_all.csv"
OUT = REPO / "analysis" / "evidence" / "game-offsets.json"

def main():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    sched = defaultdict(list)
    with open(SCHED, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['status'] == 'completed':
                sched[r['iso_date']].append(r)
    for k in sched:
        sched[k].sort(key=lambda x: x['iso_datetime'])
    
    result = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "description": "Maps broadcast sources to series/game start offsets within multi-hour VODs. Offsets are in seconds from video start.",
        "sources": {}
    }
    
    for s in manifest['sources']:
        sid = s['source_id']
        bd = s.get('broadcast_date')
        if not bd or bd not in sched:
            continue
        series_list = sched[bd]
        entries = []
        for idx, sr in enumerate(series_list):
            if idx == 0:
                start_sec = 300
                conf = "low"
                method = "schedule_order_heuristic"
            else:
                start_sec = None
                conf = "low"
                method = "schedule_order_heuristic"
            entries.append({
                "series_index": idx,
                "match_detail_id": sr['match_detail_id'],
                "team_a": sr['team_a'],
                "team_b": sr['team_b'],
                "game_no": 1,
                "start_seconds": start_sec,
                "end_seconds": None,
                "confidence": conf,
                "provenance": {
                    "method": method,
                    "source": str(SCHED),
                    "broadcast_date": bd,
                    "scheduled_start": sr['iso_datetime'],
                    "note": "Heuristic initial placement; requires validation against transcript/boundaries/frames"
                },
                "verified_by": None,
                "status": "pending_validation"
            })
        result["sources"][sid] = {
            "video_id": s.get('video_id'),
            "broadcast_date": bd,
            "video_duration_seconds": s.get('video_duration_seconds'),
            "series": entries,
            "validation_status": "pending"
        }
    
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"Wrote {OUT}")
    print(f"Sources with series: {len(result['sources'])}")

if __name__ == '__main__':
    main()
