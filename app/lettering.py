"""The text layer — lettering rendered here, over art drawn without any text.

The layout's items already say what every balloon, caption and sound effect says and where
it sits, so the room can draw the letters itself instead of asking an image model to spell
them. Two files per page:

    the art     from an image model, using the page prompt in "separate layer" mode:
                finished art with no lettering at all, and the balloon areas kept clear
    the letters this module's SVG: transparent, balloons and captions on top of the art

Change a line and only the SVG is redrawn — the art never moves, and the words are exactly
what you typed. Everything is in page fractions (0-1), so the overlay fits any resolution.
"""
import html
import json
import os
import math
import re
from pathlib import Path

from . import projects, thumbnails
from .config import env

MARGIN = 0.012       # page margin, as a fraction of the page: rendered art is near full-bleed,
                     # so the layer's grid must match the drawn page, not a print trim - a 5%
                     # margin put every panel 5% inside the art and skewed all the lettering
GUTTER = 0.01        # between panels: the models draw thin gutters
FONT = "'Comic Sans MS', 'Comic Neue', 'Chalkboard', 'Segoe Print', sans-serif"   # Comic Neue: the server's, for renders
CHAR = 0.62          # average glyph width, in em: a sound effect's hit area
SIZES = {"caption": 0.014, "balloon": 0.0148, "whisper": 0.014, "thought": 0.0148, "shout": 0.018,
         "location": 0.015, "screen": 0.0115, "sign": 0.012, "headline": 0.0135}
SFX_SIZES = {"small": 0.024, "medium": 0.036, "large": 0.055, "huge": 0.08}
SFX_STYLES = ("drawn", "classic", "impact", "quake", "boom")   # how dramatic the display lettering is
ANCHORS = {   # keyword -> (x, y) inside the panel
    "top-left": (0.24, 0.18), "top": (0.5, 0.16), "top-right": (0.76, 0.18),
    "left": (0.22, 0.5), "middle": (0.5, 0.5), "center": (0.5, 0.5), "right": (0.78, 0.5),
    "bottom-left": (0.24, 0.82), "bottom": (0.5, 0.84), "bottom-right": (0.76, 0.82),
}
KINDS = ("balloon", "whisper", "thought", "shout", "caption", "location", "screen", "sign", "headline", "sfx")
BOXED = ("caption", "location", "screen", "sign", "headline")   # headline = a newspaper headline on newsprint   # boxes, not balloons: screen = a device readout, sign = printed text
YELLOW = "#f4d978"      # the place-and-time box ("KEEL. 2043."), dark letters on yellow
SCREEN = ("#fbf0b4", "#1d1a12")   # a device readout: pale yellow, as the approved Sunburst pages lettered screens
PAPER, INK = "#fdfcf6", "#141414"
FONT_DIR = Path(__file__).resolve().parent / "fonts"
DEFAULT_FONT = "comic-neue-bold"  # a book picks another with "font" in round-settings.json
LETTER_SCALE = 1.15  # every SIZES entry, 15% up: the size chosen against Sunburst's pages
LEAD = 1.12          # line height, in em
TRACK = 0.025        # letter spacing, in em
STROKE = 3.0         # outline width at 1000 px across
BALLOON_ASPECT = 2.3 # a balloon's text block, width to height
FALLBACK = {"\u2212": "-", "\u2011": "-"}   # characters a font may lack, drawn as these


def page_size():
    w, h = (float(v) for v in (env("PAGE_TRIM") or "6.625x10.25").lower().split("x"))
    return 1000, round(1000 * h / w)


def panel_rects(spec):
    """{panel number: (x, y, w, h)} in page fractions."""
    tiers = spec.get("tiers") or []
    heights = [float(t.get("h", t.get("height", 1))) or 1 for t in tiers]
    total_h = sum(heights) or 1
    usable_h = 1 - 2 * MARGIN - GUTTER * max(0, len(tiers) - 1)
    rects, y, n = {}, MARGIN, 0
    for tier, h in zip(tiers, heights):
        ph = usable_h * h / total_h
        panels = tier.get("panels") or [{}]
        widths = [float(p.get("w", 1)) or 1 for p in panels]
        total_w = sum(widths) or 1
        usable_w = 1 - 2 * MARGIN - GUTTER * max(0, len(panels) - 1)
        x = MARGIN
        for p, w in zip(panels, widths):
            n += 1
            pw = usable_w * w / total_w
            rects[n] = (x, y, pw, ph)
            x += pw + GUTTER
        y += ph + GUTTER
    return rects


def spot(item, rect):
    """Where an item sits, in page fractions, from its x/y percentages or its `at` keyword."""
    x0, y0, w, h = rect
    if "x" in item or "y" in item:
        fx, fy = float(item.get("x", 50)) / 100, float(item.get("y", 50)) / 100
    else:
        fx, fy = ANCHORS.get(item.get("at", "middle"), (0.5, 0.5))
    return x0 + w * min(max(fx, 0.08), 0.92), y0 + h * min(max(fy, 0.08), 0.92)


def items(spec):
    """Every lettering item on the page, in reading order, with its index in the layout."""
    out = []
    for i, item in enumerate(spec.get("items") or []):
        if item.get("type") in KINDS:
            # a writer's *emphasis* marks are not lettered: the words are, plain
            text = re.sub(r"\*+([^*]+)\*+", r"\1", str(item.get("text", ""))).replace("*", "")
            out.append({"i": i, **item, "text": text})
    return out



class Face:
    """A lettering font from app/fonts/<name>.json (scripts/font_outlines.py makes one): each
    character's advance and outline, so the layer measures real widths and draws the letters as
    paths - no font has to be installed wherever the SVG is shown."""
    def __init__(self, name):
        data = json.loads((FONT_DIR / f"{name}.json").read_text(encoding="utf-8"))
        self.name, self.upm, self.glyphs = name, data["upm"], data["glyphs"]
        self.cap = data["cap"] / data["upm"]

    def glyph(self, ch):
        return self.glyphs.get(ch) or self.glyphs.get(FALLBACK.get(ch, "?")) or self.glyphs["?"]

    def width(self, text, size):
        return (sum(self.glyph(c)[0] for c in text) * size / self.upm + TRACK * size * max(0, len(text) - 1))

    def uses(self, text, size, x, baseline, defs):
        """A line of text, its left end at x on the baseline, as <use>s of glyph outlines; each
        glyph's outline goes into `defs` once ({id: outline}) and every letter refers to it."""
        s, out = size / self.upm, []
        for c in text:
            adv, d = self.glyph(c)
            if d:
                gid = f"g-{self.name}-{ord(c):x}"     # one id per font and character: SVGs on one page may share it
                defs[gid] = d
                out.append(f'<use href="#{gid}" xlink:href="#{gid}" transform="matrix({s:.6f} 0 0 {-s:.6f} {x:.2f} {baseline:.2f})"/>')
            x += adv * s + TRACK * size
        return "".join(out)


_FACES = {}


def face(ctx=None):
    """The book's lettering font: "font" in round-settings.json, else DEFAULT_FONT."""
    name = (ctx or {}).get("font") or DEFAULT_FONT
    if name not in _FACES:
        _FACES[name] = Face(name if (FONT_DIR / f"{name}.json").is_file() else DEFAULT_FONT)
    return _FACES[name]


def balanced(text, f, size, max_w, boxed=False, max_h=None):
    """The text broken into lines. A balloon's lines swell in the middle, the way a lettered
    balloon reads, at about the shape of a comic balloon; a box takes the fewest lines that fit."""
    words = text.split() or [""]
    n, sp = len(words), f.width(" ", size)
    ww = [f.width(w, size) for w in words]
    line_w = lambda i, j: sum(ww[i:j]) + sp * (j - i - 1)
    total, best = line_w(0, n), None
    for k in range(1, min(n, 10) + 1):
        shape = [(0.74 + 0.26 * math.sin(math.pi * (i + 0.5) / k)) if not boxed and k > 2 else 1.0 for i in range(k)]
        base = total / sum(shape)
        inf = float("inf")
        dp = [[inf] * (n + 1) for _ in range(k + 1)]
        cut = [[0] * (n + 1) for _ in range(k + 1)]
        dp[0][0] = 0
        for li in range(1, k + 1):
            for j in range(li, n + 1):
                for i in range(li - 1, j):
                    w = line_w(i, j)
                    if dp[li - 1][i] == inf or (w > max_w and j - i > 1):
                        continue
                    c = dp[li - 1][i] + (w - base * shape[li - 1]) ** 2
                    if c < dp[li][j]:
                        dp[li][j], cut[li][j] = c, i
        if dp[k][n] == inf:
            continue
        lines, j = [], n
        for li in range(k, 0, -1):
            lines.insert(0, " ".join(words[cut[li][j]:j]))
            j = cut[li][j]
        if boxed:
            return lines
        bw = max(f.width(l, size) for l in lines)
        bh = (k - 1) * size * LEAD + size * f.cap
        score = dp[k][n] / base ** 2 + 3.0 * math.log((bw / bh) / BALLOON_ASPECT) ** 2
        if max_h and bh > max_h:
            score += 100
        if best is None or score < best[0]:
            best = (score, lines)
    return best[1] if best else words


def fit_ellipse(halfs, extents, pad_x, pad_y):
    """The smallest balloon holding every line: each line's half width and the distance of its
    far edge from the centre, plus padding."""
    best, top = None, max(extents) + pad_y
    for step in range(120):
        ry = top * (1.04 + step * 0.012)
        rx, ok = 0, True
        for hw, e in zip(halfs, extents):
            t = (e + pad_y) / ry
            if t >= 1:
                ok = False
                break
            rx = max(rx, (hw + pad_x) / math.sqrt(1 - t * t))
        if ok and 1.05 <= rx / ry <= 2.8 and (best is None or rx * ry < best[0]):
            best = (rx * ry, rx, ry)
    if best is None:
        return (max(halfs) + pad_x) * 1.42, top * 1.42
    return best[1], best[2]


def tail_path(cx, cy, rx, ry, tx, ty, size):
    """A short curved wedge from the balloon toward (tx, ty), its base inside the balloon so the
    two read as one shape."""
    t0 = math.atan2((ty - cy) / ry, (tx - cx) / rx)
    ex, ey = cx + rx * math.cos(t0), cy + ry * math.sin(t0)
    d = math.hypot(tx - ex, ty - ey)
    ux, uy = ((tx - ex) / d, (ty - ey) / d) if d > 1 else (math.cos(t0), math.sin(t0))
    reach = min(max(0.55 * d, 1.2 * size), 2.3 * size)
    tip = (ex + ux * reach, ey + uy * reach)
    px, py, half, inset, bend = -uy, ux, 0.62 * size, 0.25 * size, 0.22 * reach
    b1 = (ex - ux * inset + px * half, ey - uy * inset + py * half)
    b2 = (ex - ux * inset - px * half, ey - uy * inset - py * half)
    c1 = ((b1[0] + tip[0]) / 2 + px * bend * 1.3, (b1[1] + tip[1]) / 2 + py * bend * 1.3)
    c2 = ((b2[0] + tip[0]) / 2 + px * bend * 0.6, (b2[1] + tip[1]) / 2 + py * bend * 0.6)
    return (f"M{b1[0]:.1f},{b1[1]:.1f} Q{c1[0]:.1f},{c1[1]:.1f} {tip[0]:.1f},{tip[1]:.1f} "
            f"Q{c2[0]:.1f},{c2[1]:.1f} {b2[0]:.1f},{b2[1]:.1f} Z")


def free_spot(x, y, hx, hy, placed, bounds):
    """(x, y, True) when a box of half size hx, hy there clears every placed box, else the
    nearest centre inside bounds that does, else (x, y, False)."""
    hits = lambda cx, cy: any(cx - hx < p[2] and p[0] < cx + hx and cy - hy < p[3] and p[1] < cy + hy for p in placed)
    if not hits(x, y):
        return x, y, True
    x0, y0, x1, y1 = bounds
    for r in range(6, 420, 6):
        for a in range(0, 360, 15):
            cx, cy = x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a))
            if x0 + hx <= cx <= x1 - hx and y0 + hy <= cy <= y1 - hy and not hits(cx, cy):
                return cx, cy, True
    return x, y, False


def svg(spec, ctx=None, rects=None):
    """The page's text layer: transparent SVG, balloons and captions over the art."""
    return layer(spec, ctx, rects)[0]


def layer(spec, ctx=None, rects=None):
    """(svg, boxes, tails): the drawn layer, each item's drawn box in page fractions
    (x0, y0, x1, y1) for hit areas, and each tailed balloon's tail target (x, y).
    `rects` overrides the panel grid - detect_rects measures it from the drawn art.
    A panel whose lettering can't all find clear room is lettered 10% smaller, up to four times."""
    scale = {}
    for _ in range(5):
        drawn, crowded = _layer(spec, ctx, rects, scale)
        if not crowded:
            break
        for p in crowded:
            scale[p] = scale.get(p, 1.0) * 0.9
    return drawn


def _layer(spec, ctx, rects, scale):
    ctx = ctx or {}
    W, H = ctx.get("page_size") or page_size()    # the drawn art's proportions, when lettering over it
    rects = rects or panel_rects(spec)
    f = face(ctx)
    number = spec.get("page", 0)
    chapter = ctx.get("chapter")
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           f'viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
           f'<g font-family="{FONT}" text-anchor="middle">']
    label = f"CHAPTER {chapter} — PAGE {number}" if chapter and number == 1 else f"PAGE {number}"
    placed, boxes, tails, crowded, defs = [], {}, {}, set(), {}
    if ctx.get("page_label", True):     # a marker on the lettering screen; never on a finished page
        out.append(f'<text x="{round(W * 0.015)}" y="{round(H * 0.012) + round(W * 0.016)}" text-anchor="start" '
                   f'font-size="{round(W * 0.016)}" fill="#7ec8ff" stroke="#10304a" '
                   f'stroke-width="2.5" paint-order="stroke">{html.escape(label)}</text>')
    for item in items(spec):
        kind = item["type"]
        if kind == "sfx" and ctx.get("skip_sfx"):     # this page's art carries its sound effects
            continue
        start = len(out)      # everything this item draws is wrapped in <g data-item> below
        rect = rects.get(item.get("panel"), (MARGIN, MARGIN, 1 - 2 * MARGIN, 1 - 2 * MARGIN))
        cx, cy = (v for v in spot(item, rect))
        px, py = cx * W, cy * H
        text = " ".join(str(item.get("text", "")).split()).upper()
        speaker = (item.get("speaker") or "").upper()
        if speaker and text.startswith(speaker + ":"):
            text = text[len(speaker) + 1:].strip()
        if kind == "sfx":
            size = SFX_SIZES.get(item.get("size", "medium"), 0.045) * W
            style = item.get("style") if item.get("style") in SFX_STYLES else "drawn"
            if style == "drawn":   # drawn into the scene: warm hand-lettered caps in the scene's light, thin dark edge, slanted
                color = item.get("color") or "#f4e3a1"
                out.append(f'<text x="{px:.0f}" y="{py:.0f}" font-size="{size:.0f}" '
                           f'font-family="\'Impact\', \'Arial Narrow\', sans-serif" font-weight="900" letter-spacing="1" '
                           f'fill="{color}" stroke="#2b1d0e" stroke-width="{size * 0.035:.1f}" paint-order="stroke" '
                           f'transform="rotate(-4 {px:.0f} {py:.0f}) skewX(-10)">{html.escape(text)}</text>')
            elif style == "impact":
                out.append(f'<text x="{px:.0f}" y="{py:.0f}" font-size="{size * 1.1:.0f}" '
                           f'font-family="\'Arial Black\', \'Impact\', sans-serif" font-weight="900" '
                           f'fill="#fff" stroke="#111" stroke-width="{size * 0.17:.1f}" paint-order="stroke" '
                           f'letter-spacing="-1" transform="rotate(-4 {px:.0f} {py:.0f}) '
                           f'skewX(-8)">{html.escape(text)}</text>')
            elif style == "quake":
                tspans = "".join(
                    f'<tspan dy="{(size * 0.14) * (1 if j % 2 else -1):.0f}" '
                    f'rotate="{(7 if j % 2 else -7)}">{html.escape(c)}</tspan>'
                    for j, c in enumerate(text))
                out.append(f'<text x="{px:.0f}" y="{py:.0f}" font-size="{size:.0f}" font-weight="900" '
                           f'fill="#fff" stroke="#111" stroke-width="{size * 0.16:.1f}" paint-order="stroke" '
                           f'transform="rotate(-3 {px:.0f} {py:.0f})">{tspans}</text>')
            elif style == "boom":
                common = (f'x="{px:.0f}" y="{py:.0f}" font-size="{size * 1.2:.0f}" font-weight="900" '
                          f'transform="rotate(-6 {px:.0f} {py:.0f})"')
                out.append(f'<text {common} fill="none" stroke="#111" '
                           f'stroke-width="{size * 0.3:.1f}" stroke-linejoin="round">{html.escape(text)}</text>')
                out.append(f'<text {common} fill="#ffd21f" stroke="#b1261b" '
                           f'stroke-width="{size * 0.07:.1f}" paint-order="stroke">{html.escape(text)}</text>')
            else:
                out.append(f'<text x="{px:.0f}" y="{py:.0f}" font-size="{size:.0f}" font-weight="bold" '
                           f'fill="#fff" stroke="#111" stroke-width="{size * 0.12:.1f}" paint-order="stroke" '
                           f'transform="rotate(-6 {px:.0f} {py:.0f})">{html.escape(text)}</text>')
            w = max(len(text), 2) * size * CHAR * (1.2 if style == "boom" else 1)
            boxes[item["i"]] = (max(0, (px - w / 2) / W), max(0, (py - size * 1.3) / H),
                                min(1, (px + w / 2) / W), min(1, (py + size * 0.5) / H))
            out[start:] = [f'<g data-item="{item["i"]}">'] + out[start:] + ["</g>"]
            continue
        size = SIZES.get(kind, 0.019) * LETTER_SCALE * scale.get(item.get("panel"), 1.0) * W
        boxed = kind in BOXED
        width = (float(item["w"]) / 100 * rect[2] if "w" in item else min(rect[2] * 0.86, 0.6) * (1 if boxed else 0.9)) * W
        lines = balanced(text, f, size, width, boxed, rect[3] * H * 0.62)
        lead, cap = size * LEAD, size * f.cap
        block_h = (len(lines) - 1) * lead + cap
        widths = [f.width(l, size) for l in lines]
        if boxed:              # a box is as tall as its lines, not as round as a balloon
            rx = max(widths) / 2 + size * (1.0 if kind == "location" else 0.7)
            ry = block_h / 2 + size * 0.55
        else:
            mids = [-block_h / 2 + k * lead + cap / 2 for k in range(len(lines))]
            rx, ry = fit_ellipse([w / 2 for w in widths], [abs(m) + cap / 2 for m in mids], size * 0.75, size * 0.3)
            if kind == "shout":    # the spikes stand outside the words
                rx, ry = rx * 1.3, ry * 1.35
        pad = size * (0.3 if boxed else 0.5)
        fy = float(item["y"]) / 100 if "y" in item else ANCHORS.get(item.get("at", "middle"), (0.5, 0.5))[1]
        edge_x, edge_y = rect[2] * 0.02 * W, rect[3] * 0.015 * H
        exact = item.get("place") == "exact"      # a cover or a designed page: the x/y given, nothing hugged
        if exact:
            pass
        elif kind == "location":   # a place-and-time header always sits in the panel's top-left corner
            px, py = rect[0] * W + edge_x + rx + pad, rect[1] * H + edge_y + ry + pad
        else:
            if boxed:              # a caption at a side of the panel sits against that side
                fx = float(item["x"]) / 100 if "x" in item else ANCHORS.get(item.get("at", "middle"), (0.5, 0.5))[0]
                if fx <= 0.3:
                    px = rect[0] * W + edge_x + rx + pad
                elif fx >= 0.7:
                    px = (rect[0] + rect[2]) * W - edge_x - rx - pad
            if fy <= 0.3:          # anything at the top of a panel sits against its top edge, as lettered books do
                py = rect[1] * H + edge_y + ry + pad
            elif fy >= 0.7:
                py = (rect[1] + rect[3]) * H - edge_y - ry - pad
        bounds = (rect[0] * W, rect[1] * H, (rect[0] + rect[2]) * W, (rect[1] + rect[3]) * H)
        hx, hy = rx + pad, ry + pad
        if 2 * hx <= bounds[2] - bounds[0]:       # keep the box inside its drawn panel when it fits
            px = min(max(px, bounds[0] + hx), bounds[2] - hx)
        if 2 * hy <= bounds[3] - bounds[1]:
            py = min(max(py, bounds[1] + hy), bounds[3] - hy)
        if not exact:
            px, py, ok = free_spot(px, py, hx, hy, placed, bounds)
            if not ok:
                crowded.add(item.get("panel"))
        placed.append((px - hx, py - hy, px + hx, py + hy))
        boxes[item["i"]] = ((px - hx) / W, (py - hy) / H, (px + hx) / W, (py + hy) / H)
        dark = item.get("invert", False)
        fill, ink = (INK, PAPER) if dark else (PAPER, INK)
        if kind == "location" and not dark:    # place-and-time headers: the book's yellow box
            fill = YELLOW
        elif kind == "screen" and not dark:    # a device readout: the pale yellow box the book letters screens in
            fill, ink = SCREEN
        elif kind == "sign":                   # printed matter in the scene: dark ink on paper
            fill, ink = "#f3ead6", "#2a2118"
        elif kind == "headline":               # a newspaper headline: black on newsprint
            fill, ink = "#ece3c8", "#111"
        if boxed:
            corner = 0 if kind == "location" else size * 0.3
            box = f'x="{px - rx:.1f}" y="{py - ry:.1f}" width="{2 * rx:.1f}" height="{2 * ry:.1f}" rx="{corner:.1f}"'
            out.append(f'<rect {box} transform="translate(3 3)" fill="#000" opacity="0.3"/>')
            out.append(f'<rect {box} fill="{fill}" stroke="{INK}" stroke-width="{STROKE * 0.8:.1f}"/>')
        elif kind == "thought":
            out.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" '
                       f'stroke="{INK}" stroke-width="{STROKE:.1f}" stroke-dasharray="2 7" stroke-linecap="round"/>')
            for k, r in ((1.0, 0.5), (1.8, 0.32), (2.4, 0.2)):
                out.append(f'<circle cx="{px + rx * 0.5:.1f}" cy="{py + ry + size * k:.1f}" r="{size * r:.1f}" '
                           f'fill="{fill}" stroke="{INK}" stroke-width="{STROKE * 0.8:.1f}"/>')
        elif kind == "shout":
            pts = " ".join(f"{px + math.cos(math.pi * a / 12) * rx * (0.72 if a % 2 else 1):.1f},"
                           f"{py + math.sin(math.pi * a / 12) * ry * (0.72 if a % 2 else 1):.1f}" for a in range(24))
            out.append(f'<polygon points="{pts}" fill="{fill}" stroke="{INK}" stroke-width="{STROKE:.1f}" stroke-linejoin="round"/>')
        else:
            shapes = [f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{rx:.1f}" ry="{ry:.1f}"/>']
            if speaker and item.get("tail", "auto") != "none":
                if item.get("tail_x") is not None and item.get("tail_y") is not None:
                    tx = (rect[0] + rect[2] * float(item["tail_x"]) / 100) * W
                    ty = (rect[1] + rect[3] * float(item["tail_y"]) / 100) * H
                else:
                    tx, ty = rect[0] * W + rect[2] * W / 2, (rect[1] + rect[3] * 0.82) * H
                tails[item["i"]] = (round(tx / W, 4), round(ty / H, 4))
                shapes.append(f'<path d="{tail_path(px, py, rx, ry, tx, ty, size)}"/>')
            # outline under, fill over: balloon and tail read as one shape
            dash = ' stroke-dasharray="7 5"' if kind == "whisper" else ""
            under = "none" if kind == "whisper" else INK
            out.append(f'<g fill="{under}" stroke="{INK}" stroke-width="{STROKE * 2:.1f}" stroke-linejoin="round"{dash}>'
                       + "".join(shapes) + "</g>")
            out.append(f'<g fill="{fill}">' + "".join(shapes) + "</g>")
        base = py - block_h / 2 + cap
        out.append(f'<g fill="{ink}">' + "".join(
            f.uses(line, size, px - w / 2, base + k * lead, defs) for k, (line, w) in enumerate(zip(lines, widths))) + "</g>")
        out[start:] = [f'<g data-item="{item["i"]}">'] + out[start:] + ["</g>"]
    out.insert(1, "<defs>" + "".join(f'<path id="{k}" d="{d}"/>' for k, d in sorted(defs.items())) + "</defs>")
    out += ["</g>", "</svg>"]
    return ("\n".join(out), {i: [round(v, 4) for v in b] for i, b in boxes.items()}, tails), crowded


# ---- reading and writing the layout's text ---------------------------------------------

def page_spec(slug, page, version=None):
    specs, _ = thumbnails.parse_layouts(projects.read_artifact(slug, "layouts.md", version))
    return next((s for s in specs if s.get("page") == page), None)


def page_items(slug, page, version=None):
    spec = page_spec(slug, page, version)
    return items(spec) if spec else []


def set_items(slug, page, changes):
    """changes: {item index: {"text" | "at" | "x","y" | "type" | "speaker" | "size" | "invert"}}.
    Rewrites that page's block in layouts.md."""
    spec = page_spec(slug, page)
    if not spec:
        raise ValueError(f"no layout for page {page}")
    all_items = spec.get("items") or []
    for i, change in changes.items():
        i = int(i)
        if not 0 <= i < len(all_items):
            raise ValueError(f"no item {i} on page {page}")
        if isinstance(change, str):
            change = {"text": change}
        item = all_items[i]
        if "text" in change:
            item["text"] = " ".join(str(change["text"]).split())
        if change.get("at"):
            if change["at"] not in ANCHORS:
                raise ValueError(f"{change['at']!r} isn't one of {', '.join(ANCHORS)}")
            item["at"] = change["at"]
            item.pop("x", None)
            item.pop("y", None)
        if change.get("x") is not None and change.get("y") is not None:
            item["x"] = max(0, min(100, float(change["x"])))
            item["y"] = max(0, min(100, float(change["y"])))
            item.pop("at", None)
        if change.get("panel") is not None:
            panel = int(change["panel"])
            if panel not in panel_rects(spec):
                raise ValueError(f"no panel {panel} on page {page}")
            item["panel"] = panel
        if change.get("tail_x") is not None and change.get("tail_y") is not None:
            item["tail_x"] = max(-20, min(120, float(change["tail_x"])))
            item["tail_y"] = max(-20, min(120, float(change["tail_y"])))
        if change.get("tail") in ("auto", "none"):
            if change["tail"] == "none":
                item["tail"] = "none"
            else:
                item.pop("tail", None)
        if change.get("type"):
            if change["type"] not in KINDS:
                raise ValueError(f"{change['type']!r} isn't one of {', '.join(KINDS)}")
            item["type"] = change["type"]
        if change.get("speaker") is not None:
            item["speaker"] = str(change["speaker"]).strip()
            if not item["speaker"]:
                item.pop("speaker", None)
        if change.get("size"):
            if change["size"] not in SFX_SIZES:
                raise ValueError(f"{change['size']!r} isn't one of {', '.join(SFX_SIZES)}")
            item["size"] = change["size"]
        if change.get("style"):
            if change["style"] not in SFX_STYLES:
                raise ValueError(f"{change['style']!r} isn't one of {', '.join(SFX_STYLES)}")
            item["style"] = change["style"]
        if "invert" in change:
            if change["invert"]:
                item["invert"] = True
            else:
                item.pop("invert", None)
    write_spec(slug, page, spec)
    return spec


def add_item(slug, page, item):
    """A new balloon, caption, location header or sound effect on the page. Returns its index."""
    kind = item.get("type")
    if kind not in KINDS:
        raise ValueError(f"type must be one of {', '.join(KINDS)}")
    spec = page_spec(slug, page)
    if not spec:
        raise ValueError(f"no layout for page {page}")
    panels = panel_rects(spec)
    new = {"type": kind, "text": " ".join(str(item.get("text", "")).split()) or "..."}
    try:
        new["panel"] = int(item.get("panel") or 1)
    except (TypeError, ValueError):
        new["panel"] = 1
    if new["panel"] not in panels:
        new["panel"] = 1
    try:
        new["x"] = max(0, min(100, float(item.get("x", 50))))
        new["y"] = max(0, min(100, float(item.get("y", 50))))
    except (TypeError, ValueError):
        new["x"], new["y"] = 50, 50
    if item.get("speaker"):
        new["speaker"] = str(item["speaker"]).strip()
    if kind == "sfx":
        new["size"] = item.get("size") if item.get("size") in SFX_SIZES else "medium"
        if item.get("style") in SFX_STYLES:
            new["style"] = item["style"]
    if item.get("invert"):
        new["invert"] = True
    all_items = spec.get("items") or []
    all_items.append(new)
    spec["items"] = all_items
    write_spec(slug, page, spec)
    return len(all_items) - 1


MOVES_RE = re.compile(r"```moves\s*\n(.*?)\n```", re.S)


def moves_in(text):
    """The Letterer's ```moves blocks: [(page, [{"item", "at" | "x","y"}])], bad JSON skipped."""
    out = []
    for m in MOVES_RE.finditer(text or ""):
        try:
            block = json.loads(re.sub(r",(\s*[\]}])", r"\1", m.group(1)))
        except ValueError:
            continue
        if isinstance(block, dict) and block.get("moves"):
            out.append((int(block.get("page", 0)), [x for x in block["moves"] if isinstance(x, dict)]))
    return out


def apply_moves(slug, text, locked=()):
    """Move balloons and captions as the Letterer asked in lettering.md. Only the position of a
    lettering item changes - never its words, never a figure, never a locked page. Returns
    [(page, item, what)] for what was applied."""
    done = []
    for page, moves in moves_in(text):
        if page in locked:
            continue
        spec = page_spec(slug, page)
        if not spec:
            continue
        all_items = spec.get("items") or []
        changed = False
        for mv in moves:
            try:
                i = int(mv.get("item"))
            except (TypeError, ValueError):
                continue
            if not 0 <= i < len(all_items) or all_items[i].get("type") not in KINDS:
                continue
            if mv.get("at") in ANCHORS:
                all_items[i]["at"] = mv["at"]
                all_items[i].pop("x", None); all_items[i].pop("y", None)
                done.append((page, i, mv["at"])); changed = True
            elif mv.get("x") is not None and mv.get("y") is not None:
                try:
                    x, y = float(mv["x"]), float(mv["y"])
                except (TypeError, ValueError):
                    continue
                all_items[i]["x"], all_items[i]["y"] = max(0, min(100, x)), max(0, min(100, y))
                all_items[i].pop("at", None)
                done.append((page, i, f"{x:g},{y:g}")); changed = True
        if changed:
            write_spec(slug, page, spec)
    return done


def delete_item(slug, page, index):
    """Drop one balloon, caption or sound effect from the page."""
    spec = page_spec(slug, page)
    if not spec:
        raise ValueError(f"no layout for page {page}")
    all_items = spec.get("items") or []
    index = int(index)
    if not 0 <= index < len(all_items):
        raise ValueError(f"no item {index} on page {page}")
    kind = all_items[index].get("type")
    if kind not in KINDS:
        raise ValueError(f"item {index} on page {page} is a {kind}, not lettering")
    all_items.pop(index)
    spec["items"] = all_items
    write_spec(slug, page, spec)
    return spec


def write_spec(slug, page, spec):
    """Save the page's layout block, and redraw the sketch, which is drawn from it. layouts.md keeps
    its time: a lettering edit is not a new layout, so a run must not redraw the drawn pages for it.
    A page approved in the proof is locked: it raises until the page is unlocked."""
    from . import proof
    proof.check_unlocked(slug, page)
    md = projects.read_artifact(slug, "layouts.md") or ""
    layouts = replace_block(md, page, spec)
    path = projects.project_dir(slug) / "layouts.md"
    times = path.stat() if path.is_file() else None
    projects.write_artifact(slug, "layouts.md", layouts)
    if times:
        os.utime(path, (times.st_atime, times.st_mtime))
    drawn, _, _ = thumbnails.render_layouts(layouts, projects.read_artifact(slug, "thumbnails.md"))
    projects.write_artifact(slug, "thumbnails.md", drawn)


def replace_block(markdown, page, spec):
    """Put `spec` back in its ```layout block, leaving the rest of layouts.md alone."""
    blocks = list(thumbnails.LAYOUT_RE.finditer(markdown or ""))
    for m in blocks:
        try:
            found = json.loads(re.sub(r",(\s*[\]}])", r"\1", m.group(1)))
        except ValueError:
            continue
        if int(found.get("page", 0)) == page:
            body = json.dumps(spec, indent=1)
            return markdown[:m.start(1)] + body + "\n" + markdown[m.end(1):]
    raise ValueError(f"no layout block for page {page}")


# ---- the drawn grid: detected from the art, because the model's page is the real page ----

def gutter_rects(spec, art_bytes, white=232, cover=0.92):
    """{panel: (x, y, w, h)} from the drawn page's white gutters, or None when the drawn grid
    does not have the tiers and panels the spec asks for. A tier is a stretch between
    full-width white bands; a panel, a stretch of its tier between full-height white bands."""
    import io
    from PIL import Image
    tiers = spec.get("tiers") or []
    if not tiers:
        return None
    im = Image.open(io.BytesIO(art_bytes)).convert("L")
    im = im.resize((512, round(512 * im.height / im.width)))
    W, H = im.size
    px = im.load()

    def bands(n, is_white, min_len):
        """[(start, end)] of the stretches between white bands, each at least min_len long."""
        out, s = [], None
        for i in range(n + 1):
            content = i < n and not is_white(i)
            if content and s is None:
                s = i
            if not content and s is not None:
                if i - s >= min_len:
                    out.append((s, i))
                s = None
        return out

    row_white = lambda y, x0=0, x1=W: sum(px[x, y] >= white for x in range(x0, x1)) >= cover * (x1 - x0)
    tier_spans = bands(H, row_white, H * 0.06)
    if len(tier_spans) != len(tiers):
        return None
    rects, n = {}, 0
    for (y0, y1), tier in zip(tier_spans, tiers):
        col_white = lambda x: sum(px[x, y] >= white for y in range(y0, y1)) >= cover * (y1 - y0)
        cols = bands(W, col_white, W * 0.06)
        if len(cols) != len(tier.get("panels") or [{}]):
            return None
        for x0, x1 in cols:
            n += 1
            rects[n] = (x0 / W, y0 / H, (x1 - x0) / W, (y1 - y0) / H)
    return rects


def band_rects(spec, art_bytes, white=200, cover=0.75):
    """{panel: (x, y, w, h)} with each tier from the drawn page's full-width gutters, or None
    when their count isn't the spec's. Full-width gutters survive an off-white tint or a
    glowing edge that spoils gutter_rects. In a tier whose columns don't measure as the spec's,
    the spec's widths split the measured tier."""
    import io
    from PIL import Image
    tiers = spec.get("tiers") or []
    im = Image.open(io.BytesIO(art_bytes)).convert("L")
    im = im.resize((512, round(512 * im.height / im.width)))
    W, H = im.size
    px = im.load()

    def bands(n, is_white, min_len):
        out, s = [], None
        for i in range(n + 1):
            content = i < n and not is_white(i)
            if content and s is None:
                s = i
            if not content and s is not None:
                if i - s >= min_len:
                    out.append((s, i))
                s = None
        return out

    rows = bands(H, lambda y: sum(px[x, y] >= white for x in range(W)) >= cover * W, H * 0.06)
    if not tiers or len(rows) != len(tiers):
        return None
    rects, n = {}, 0
    for (y0, y1), tier in zip(rows, tiers):
        panels = tier.get("panels") or [{}]
        cols = bands(W, lambda x: sum(px[x, y] >= white for y in range(y0, y1)) >= cover * (y1 - y0), W * 0.06)
        if len(cols) != len(panels):
            lo, hi = (cols[0][0], cols[-1][1]) if cols else (0, W)
            widths = [float(p.get("w", 1)) or 1 for p in panels]
            usable = hi - lo - W * GUTTER * (len(widths) - 1)
            cols, x = [], lo
            for w in widths:
                cols.append((x, x + usable * w / sum(widths)))
                x += usable * w / sum(widths) + W * GUTTER
        for x0, x1 in cols:
            n += 1
            rects[n] = (x0 / W, y0 / H, (x1 - x0) / W, (y1 - y0) / H)
    return rects


def detect_rects(spec, art_bytes):
    """{panel: (x, y, w, h)} measured from the drawn art, or None when there is no art.

    The white gutters first (gutter_rects): exact when the drawn grid has the spec's tiers and
    panels, which is nearly always. Then band_rects: the tiers alone from the gutters, when a
    glowing edge or an off-white gutter spoils the strict check. The measurement below is the
    last fallback.

    The models draw their own margins and gutters - asymmetric ones, since the prompt names
    the page's side of the book - so the grid the lettering can trust is the one in the
    pixels. The content box is measured outright; each expected cut (from the spec's tier
    and panel proportions) snaps to the nearest thin uniform band when one is visible and
    stays proportional when not. Downscaled analysis, PIL only."""
    import io
    from PIL import Image
    tiers = spec.get("tiers") or []
    if not tiers:
        return None
    try:
        found = gutter_rects(spec, art_bytes) or band_rects(spec, art_bytes)
        if found:
            return found
    except Exception:      # noqa: BLE001 - an unreadable image falls through to the fallback
        pass
    try:
        im = Image.open(io.BytesIO(art_bytes)).convert("L").resize((240, 360))
    except Exception:
        return None
    W, H = im.size
    px = list(im.getdata())

    def spread(vals):
        m = sorted(vals)[len(vals) // 2]
        return sum(abs(v - m) for v in vals) / len(vals)

    def profile(along, lo_c, hi_c, horizontal):
        """Uniformity score per row (or column), over the central span of the other axis."""
        out = []
        for i in range(along):
            vals = (px[i * W + lo_c:i * W + hi_c] if horizontal
                    else [px[y * W + i] for y in range(lo_c, hi_c)])
            out.append(spread(vals))
        return out

    def content(profile_, thr):
        """Trim the thin outer margin only: a dark, uniform stretch of drawing is content,
        not margin, so the trim is capped at a tenth of the span each side."""
        span = len(profile_)
        lo = next((i for i in range(span - 2) if all(v > thr for v in profile_[i:i + 3])), 0)
        hi = next((i for i in range(span - 1, 1, -1) if all(v > thr for v in profile_[i - 2:i + 1])), span)
        return min(lo, round(span * 0.1)), max(hi + 1, round(span * 0.9))

    def thin_runs(profile_, thr, span):
        """Midpoints of thin uniform bands - the drawn gutters."""
        runs, s = [], None
        for i in range(len(profile_) + 1):
            inlow = i < len(profile_) and profile_[i] < thr
            if inlow and s is None:
                s = i
            if not inlow and s is not None:
                if i - s <= max(3, span * 0.05):
                    runs.append((s + i) / 2)
                s = None
        return runs

    def edge_peaks(horizontal, lo_c, hi_c, span):
        """Rows (or columns) where a panel border crosses: strong, locally maximal gradient
        across the central band. A thin gutter blurs away when downscaled; its border edge
        does not."""
        grad = [0.0]
        for i in range(1, span - 1):
            if horizontal:
                vals = [abs(px[(i + 1) * W + x] - px[(i - 1) * W + x]) for x in range(lo_c, hi_c)]
            else:
                vals = [abs(px[y * W + i + 1] - px[y * W + i - 1]) for y in range(lo_c, hi_c)]
            grad.append(sum(vals) / len(vals))
        grad.append(0.0)
        floor = sorted(grad)[round(len(grad) * 0.88)]
        peaks = []
        for i in range(2, span - 2):
            if grad[i] > floor and grad[i] == max(grad[i - 2:i + 3]):
                if peaks and i - peaks[-1][0] < span * 0.03:
                    if grad[i] > peaks[-1][1]:
                        peaks[-1] = (i, grad[i])
                else:
                    peaks.append((i, grad[i]))
        return peaks

    def edges_for(weights, lo, hi, profile_, thr, span, peaks):
        """Cut positions between lo and hi: the drawn cuts outright when exactly the expected
        number is visible (gutters first, border edges second), else proportional cuts
        snapped to the nearest candidate."""
        total = sum(weights)
        margin = span * 0.04
        runs = [r for r in thin_runs(profile_, thr, span) if lo + margin < r < hi - margin]
        strong = [float(i) for i, _ in peaks if lo + margin < i < hi - margin]
        for exact in (runs, strong):
            if len(exact) == len(weights) - 1:
                return [float(lo)] + exact + [float(hi)]
        candidates = sorted(set(runs + strong))
        out, acc = [float(lo)], 0.0
        for w_ in weights[:-1]:
            acc += w_
            expected = lo + (hi - lo) * acc / total
            near = [r for r in candidates if abs(r - expected) <= span * 0.12]
            out.append(min(near, key=lambda r: abs(r - expected)) if near else expected)
        return out + [float(hi)]

    rows = profile(H, round(W * 0.12), round(W * 0.88), True)
    thr = max(8.0, sorted(rows)[H // 2] * 0.45)
    top, bottom = content(rows, thr)
    if bottom - top < H * 0.6:
        return None
    heights = [float(t_.get("h", t_.get("height", 1))) or 1 for t_ in tiers]
    edges = edges_for(heights, top, bottom, rows, thr, H, edge_peaks(True, round(W * 0.12), round(W * 0.88), H))
    rects, n = {}, 0
    for t_i, tier in enumerate(tiers):
        y0, y1 = edges[t_i], edges[t_i + 1]
        if y1 - y0 < H * 0.03:
            return None
        panels = tier.get("panels") or [{}]
        cols = profile(W, round(y0 + (y1 - y0) * 0.12), round(y0 + (y1 - y0) * 0.88), False)
        cthr = max(8.0, sorted(cols)[W // 2] * 0.45)
        left, right = content(cols, cthr)
        if right - left < W * 0.5:
            left, right = 0, W
        widths = [float(p_.get("w", 1)) or 1 for p_ in panels]
        xs = edges_for(widths, left, right, cols, cthr, W,
                       edge_peaks(False, round(y0 + (y1 - y0) * 0.12), round(y0 + (y1 - y0) * 0.88), W) if len(panels) > 1 else [])
        for p_i in range(len(panels)):
            n += 1
            x0, x1 = xs[p_i], xs[p_i + 1]
            if x1 - x0 < W * 0.03:
                return None
            rects[n] = (x0 / W, y0 / H, (x1 - x0) / W, (y1 - y0) / H)
    return rects
