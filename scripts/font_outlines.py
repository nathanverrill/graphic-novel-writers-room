"""Turn a TTF/OTF into the outline file the lettering layer draws with: app/fonts/<name>.json.

    pip install fonttools          # only here, never on the server
    python3 scripts/font_outlines.py path/to/Font-Bold.ttf comic-neue-bold [--axes wght=700]

The server needs no font installed and no font library: each character's advance and outline
(font units, y up) are in the JSON, and app/lettering.py places them. A book picks its font
with "font" in production/round-settings.json; the default is lettering.DEFAULT_FONT.
"""
import json
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

# Basic Latin, Latin-1, and the punctuation a script uses: dashes, curly quotes, ellipsis
RANGES = [(0x20, 0x7E), (0xA0, 0xFF), (0x2010, 0x2027), (0x2030, 0x203A)]


def main(src, name, axes=None):
    font = TTFont(src)
    if axes:
        from fontTools.varLib import instancer
        font = instancer.instantiateVariableFont(font, axes)
    cmap, gs, hmtx = font.getBestCmap(), font.getGlyphSet(), font["hmtx"]
    upm = font["head"].unitsPerEm
    cap = getattr(font["OS/2"], "sCapHeight", 0) or round(upm * 0.7)
    glyphs = {}
    for lo, hi in RANGES:
        for code in range(lo, hi + 1):
            g = cmap.get(code)
            if not g:
                continue
            pen = SVGPathPen(gs)
            gs[g].draw(pen)
            glyphs[chr(code)] = [hmtx[g][0], pen.getCommands()]
    out = Path(__file__).resolve().parents[1] / "app" / "fonts" / f"{name}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"name": name, "source": Path(src).name, "upm": upm, "cap": cap, "glyphs": glyphs},
                              ensure_ascii=False, separators=(",", ":")))
    print(f"{out}: {len(glyphs)} characters, {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    args = sys.argv[1:]
    axes = {}
    if "--axes" in args:
        k = args.index("--axes")
        axes = {a.split("=")[0]: float(a.split("=")[1]) for a in args[k + 1].split(",")}
        args = args[:k] + args[k + 2:]
    main(args[0], args[1], axes)
