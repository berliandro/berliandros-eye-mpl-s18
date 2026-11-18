"""Generate card-sized portrait derivatives for the player grid.

The committed portraits are 500x500 Liquipedia originals. The grid paints them
at 44px (56px at most), so shipping the 500px file there costs ~1 MB of decoded
bitmap per card and a visible decode/paint stall on the Players view (measured:
the grid switch halves when portraits are blocked). This tool writes a 160px
LANCZOS downscale next to the originals and records its provenance chain.

Usage:
    python tools/make_player_cards.py           # regenerate + provenance
    python tools/make_player_cards.py --check   # verify committed derivatives
"""
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parent.parent
SRC = ROOT / 'assets' / 'players'
OUT = SRC / 'cards'
SIZE = 160
PROV = OUT / 'provenance.json'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_players():
    manifest = json.loads((ROOT / 'assets' / 'manifest.json').read_text(encoding='utf-8'))
    return manifest.get('players') or {}


def build():
    players = load_players()
    OUT.mkdir(parents=True, exist_ok=True)
    entries = {}
    total = 0
    for name, rel in sorted(players.items()):
        src = ROOT / rel
        if not src.exists():
            print(f'MISSING source for {name}: {rel}')
            continue
        im = Image.open(src).convert('RGBA')
        im.thumbnail((SIZE, SIZE), Image.LANCZOS)
        dest = OUT / src.name
        im.save(dest, format='PNG', optimize=True)
        total += dest.stat().st_size
        entries[name] = {
            'file': src.name,
            'source': rel.replace('\\', '/'),
            'source_sha256': sha256(src),
            'source_width': Image.open(src).width,
            'source_height': Image.open(src).height,
            'width': im.width,
            'height': im.height,
            'sha256': sha256(dest),
        }
    doc = {
        'schema': 1,
        'kind': 'player-card-thumbnail',
        'source': 'assets/players/*.png (Liquipedia Commons, CC-BY-SA 3.0)',
        'note': ('160px LANCZOS downscale of the committed 500px portrait, used only '
                 'where the interface paints the portrait at 56px or less. The full '
                 'file remains the profile hero and championship-plate source.'),
        'size': SIZE,
        'generated': '2026-11-18',
        'players': entries,
    }
    PROV.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    print(f'wrote {len(entries)} cards, {total / 1024:.0f} KB total, provenance {PROV}')


def check():
    problems = []
    players = load_players()
    if not PROV.exists():
        problems.append(f'missing {PROV}')
        prov = {'players': {}}
    else:
        prov = json.loads(PROV.read_text(encoding='utf-8'))
    for name, rel in sorted(players.items()):
        src = ROOT / rel
        dest = OUT / src.name
        entry = (prov.get('players') or {}).get(name)
        if not dest.exists():
            problems.append(f'missing card for {name}: {dest.relative_to(ROOT)}')
            continue
        if not entry:
            problems.append(f'no provenance entry for {name}')
            continue
        if entry.get('sha256') != sha256(dest):
            problems.append(f'card hash drift for {name}')
        if src.exists() and entry.get('source_sha256') != sha256(src):
            problems.append(f'source hash drift for {name}')
    for p in problems:
        print('FAIL', p)
    if problems:
        return 1
    print(f'PASS player cards: {len(players)} derivatives match provenance')
    return 0


if __name__ == '__main__':
    sys.exit(check() if '--check' in sys.argv else (build() or 0))
