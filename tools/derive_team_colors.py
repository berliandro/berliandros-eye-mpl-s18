"""Derive a usable team accent colour from each committed team logo.

The colour is data, not taste: it is the most common saturated hue in the
logo, then clamped in lightness and saturation so it stays legible on the
near-black canvas (a navy crest would otherwise disappear) and never turns
into a neon that fights the interface.

Output: data/global/team_colors.json
  {"NAVI": {"hex": "#e7d21b", "soft": "rgba(...,.55)", "tint": "rgba(...,.06)"}, ...}

Run: python tools/derive_team_colors.py
"""
import colorsys
import json
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "teams"
OUT = ROOT / "data" / "global" / "team_colors.json"

# Legibility window on #131311: L 0.52-0.66 keeps dark crests visible and
# stops bright crests from glowing; S 0.55-0.88 keeps them recognisable
# without turning the UI into a highlighter.
L_MIN, L_MAX = 0.52, 0.66
S_MIN, S_MAX = 0.55, 0.88


def dominant_rgb(path):
    im = Image.open(path).convert("RGBA")
    counts = Counter()
    sums = {}
    for r, g, b, a in im.getdata():
        if a < 200:
            continue
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if s < 0.35 or v < 0.12:
            continue
        key = (int(h * 24) % 24, round(s * 4), round(v * 4))
        counts[key] += 1
        sr, sg, sb = sums.get(key, (0, 0, 0))
        sums[key] = (sr + r, sg + g, sb + b)
    if not counts:
        return None
    key = counts.most_common(1)[0][0]
    n = counts[key]
    return tuple(c / n / 255 for c in sums[key])


def adjust(rgb):
    h, l, s = colorsys.rgb_to_hls(*rgb)
    l = min(L_MAX, max(L_MIN, l))
    s = min(S_MAX, max(S_MIN, s))
    return colorsys.hls_to_rgb(h, l, s)


def rgba(rgb, alpha):
    r, g, b = (round(c * 255) for c in rgb)
    return f"rgba({r},{g},{b},{alpha})"


def main():
    out = {}
    for path in sorted(SRC.glob("*.png")):
        rgb = dominant_rgb(path)
        if rgb is None:
            print(f"skip {path.name}: no saturated pixels")
            continue
        r, g, b = adjust(rgb)
        out[path.stem.upper()] = {
            "hex": "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255)),
            "soft": rgba((r, g, b), 0.55),
            "tint": rgba((r, g, b), 0.06),
            "ghost": rgba((r, g, b), 0.045),
        }
        print(f"{path.stem.upper():6} {out[path.stem.upper()]['hex']}")
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(out)} teams)")


if __name__ == "__main__":
    main()
