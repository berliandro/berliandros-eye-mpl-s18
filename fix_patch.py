import json
path = 'analysis/sources/source-manifest.json'
with open(path, 'r', encoding='utf-8') as f:
    m = json.load(f)
for s in m['sources']:
    if s['source_id'] == 'src-s18-w09d02':
        s['citation_policy'] = 'quarantined'
        s['citation_policy_reason'] = '37 short ad/transition/interjection lines without trustworthy timestamps; excluded from timestamp citations until resolved or explicitly approved'
        break
with open(path, 'w', encoding='utf-8') as f:
    json.dump(m, f, indent=2, ensure_ascii=False)
    f.write('\n')
print('done')
