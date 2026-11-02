#!/usr/bin/env python3
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OFF = REPO / "analysis" / "evidence" / "game-offsets.json"
MANIFEST = REPO / "analysis" / "sources" / "source-manifest.json"
CACHE = REPO / "analysis" / "cache" / "timed"

def find_boundary(transcript_lines, team_a, team_b):
    for i, line in enumerate(transcript_lines):
        t = line.upper()
        if team_a.upper() in t and team_b.upper() in t:
            return i
    for i, line in enumerate(transcript_lines):
        t = line.upper()
        if len(team_a) >= 3 and team_a[:3].upper() in t and len(team_b) >= 3 and team_b[:3].upper() in t:
            return i
    return None

def main():
    offs = json.loads(OFF.read_text(encoding='utf-8'))
    manifest = {s['source_id']: s for s in json.loads(MANIFEST.read_text(encoding='utf-8'))['sources']}
    
    refined = 0
    for sid, data in offs['sources'].items():
        if sid not in manifest:
            continue
        align_path = CACHE / f"{sid}.json"
        if not align_path.exists():
            continue
        try:
            align = json.loads(align_path.read_text(encoding='utf-8'))
        except Exception:
            continue
        captions = align.get('timed_captions', [])
        lines = [c['text'] for c in captions]
        for idx, series in enumerate(data['series']):
            if series.get('start_seconds') is not None and series.get('confidence') in ['high', 'med']:
                continue
            ta = series['team_a']
            tb = series['team_b']
            b = find_boundary(lines, ta, tb)
            if b is not None and captions[b].get('start') is not None:
                start = max(0, int(captions[b]['start'] - 60))
                series['start_seconds'] = start
                series['confidence'] = 'med'
                series['provenance']['method'] = 'transcript_boundary_detection'
                series['provenance']['boundary_line'] = b + 1
                series['provenance']['boundary_text'] = lines[b][:120]
                series['status'] = 'detected_pending_review'
                refined += 1
    
    OFF.write_text(json.dumps(offs, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Refined {refined} series offsets')
    for sid in ['src-s18-w01d01', 'src-s18-w09d03']:
        if sid in offs['sources']:
            print(f'=== {sid}')
            for s in offs['sources'][sid]['series']:
                print(f"  {s['match_detail_id']}: {s['start_seconds']}s conf={s['confidence']} status={s['status']}")

if __name__ == '__main__':
    main()
