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
import math
import re

from . import projects, thumbnails
from .config import env

MARGIN = 0.05        # page margin, as a fraction of the page
GUTTER = 0.018       # between panels
FONT = "'Comic Sans MS', 'Comic Neue', 'Chalkboard', 'Segoe Print', sans-serif"   # Comic Neue: the server's, for renders
LINE = 1.22          # line height, in em
CHAR = 0.62          # average glyph width, in em — enough for wrapping
SIZES = {"caption": 0.0175, "balloon": 0.019, "whisper": 0.018, "thought": 0.019, "shout": 0.023}
SFX_SIZES = {"small": 0.03, "medium": 0.045, "large": 0.065, "huge": 0.09}
ANCHORS = {   # keyword -> (x, y) inside the panel
    "top-left": (0.24, 0.18), "top": (0.5, 0.16), "top-right": (0.76, 0.18),
    "left": (0.22, 0.5), "middle": (0.5, 0.5), "center": (0.5, 0.5), "right": (0.78, 0.5),
    "bottom-left": (0.24, 0.82), "bottom": (0.5, 0.84), "bottom-right": (0.76, 0.82),
}
KINDS = ("balloon", "whisper", "thought", "shout", "caption", "sfx")


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


def balloon_wrap(text, limit):
    """Comic balloons are read in short lines: roughly as wide as they are tall."""
    per_line = min(limit, max(12, round((len(text) * 2.1) ** 0.5)))
    return wrap(text, per_line)


def wrap(text, per_line):
    words, lines, line = str(text).split(), [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if len(trial) > per_line and line:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines or [""]


def items(spec):
    """Every lettering item on the page, in reading order, with its index in the layout."""
    out = []
    for i, item in enumerate(spec.get("items") or []):
        if item.get("type") in KINDS:
            out.append({"i": i, **item})
    return out


def nudge(box, placed, bounds):
    """Move a balloon down (then right) until it stops overlapping the ones already placed."""
    x0, y0, x1, y1 = box
    bx0, by0, bx1, by1 = bounds
    for _ in range(40):
        hit = next((p for p in placed if x0 < p[2] and p[0] < x1 and y0 < p[3] and p[1] < y1), None)
        if not hit:
            break
        drop = hit[3] - y0 + 6
        if y1 + drop <= by1:
            y0, y1 = y0 + drop, y1 + drop
        else:                      # no room below: start a new column
            shift = hit[2] - x0 + 8
            x0, x1 = x0 + shift, x1 + shift
            y0, y1 = by0, by0 + (y1 - y0)
            if x1 > bx1:
                break
    return x0, y0, x1, y1


def svg(spec, ctx=None):
    """The page's text layer: transparent SVG, balloons and captions over the art."""
    ctx = ctx or {}
    W, H = page_size()
    rects = panel_rects(spec)
    number = spec.get("page", 0)
    chapter = ctx.get("chapter")
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
           f'<g font-family="{FONT}" text-anchor="middle">']
    label = f"CHAPTER {chapter} — PAGE {number}" if chapter and number == 1 else f"PAGE {number}"
    placed = []
    out.append(f'<text x="{round(W * MARGIN)}" y="{round(H * MARGIN * 0.6)}" text-anchor="start" '
               f'font-size="{round(W * 0.016)}" fill="#7ec8ff">{html.escape(label)}</text>')
    for item in items(spec):
        kind = item["type"]
        rect = rects.get(item.get("panel"), (MARGIN, MARGIN, 1 - 2 * MARGIN, 1 - 2 * MARGIN))
        cx, cy = (v for v in spot(item, rect))
        px, py = cx * W, cy * H
        text = " ".join(str(item.get("text", "")).split()).upper()
        speaker = (item.get("speaker") or "").upper()
        if speaker and text.startswith(speaker + ":"):
            text = text[len(speaker) + 1:].strip()
        if kind == "sfx":
            size = SFX_SIZES.get(item.get("size", "medium"), 0.045) * W
            out.append(f'<text x="{px:.0f}" y="{py:.0f}" font-size="{size:.0f}" font-weight="bold" '
                       f'fill="#fff" stroke="#111" stroke-width="{size * 0.12:.1f}" paint-order="stroke" '
                       f'transform="rotate(-6 {px:.0f} {py:.0f})">{html.escape(text)}</text>')
            continue
        size = SIZES.get(kind, 0.019) * W
        width = min(rect[2] * 0.8, 0.38) * W
        limit = max(8, int(width / (size * CHAR)))
        lines = wrap(text, limit) if kind == "caption" else balloon_wrap(text, limit)
        box_w = max(len(l) for l in lines) * size * CHAR
        box_h = len(lines) * size * LINE
        rx = box_w / 2 + size * 1.2
        ry = max(box_h / 2 + size * 0.9, rx * 0.45)
        pad = size * 0.5
        bounds = (rect[0] * W, rect[1] * H, (rect[0] + rect[2]) * W, (rect[1] + rect[3]) * H)
        x0, y0, x1, y1 = nudge((px - rx - pad, py - ry - pad, px + rx + pad, py + ry + pad), placed, bounds)
        placed.append((x0, y0, x1, y1))
        px, py = (x0 + x1) / 2, (y0 + y1) / 2
        dark = item.get("invert")
        fill, ink = ("#111", "#fff") if dark else ("#fff", "#111")
        dash = ' stroke-dasharray="6 5"' if kind == "whisper" else ""
        if kind == "caption":
            cw, ch = box_w + size * 1.4, box_h + size * 0.9
            out.append(f'<rect x="{px - cw / 2:.0f}" y="{py - ch / 2:.0f}" width="{cw:.0f}" '
                       f'height="{ch:.0f}" rx="{size * 0.3:.0f}" fill="{fill}" stroke="{ink}" stroke-width="2"/>')
        elif kind == "thought":
            out.append(f'<ellipse cx="{px:.0f}" cy="{py:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" '
                       f'fill="{fill}" stroke="{ink}" stroke-width="2" stroke-dasharray="2 7"/>')
            for k, r in ((1.0, 0.5), (1.8, 0.32), (2.4, 0.2)):
                out.append(f'<circle cx="{px + rx * 0.5:.0f}" cy="{py + ry + size * k:.0f}" '
                           f'r="{size * r:.0f}" fill="{fill}" stroke="{ink}" stroke-width="2"/>')
        elif kind == "shout":
            pts = []
            for a in range(24):
                ang = math.pi * 2 * a / 24
                rr = 0.66 if a % 2 else 1.0
                pts.append(f"{px + math.cos(ang) * rx * rr * 1.15:.0f},{py + math.sin(ang) * ry * rr * 1.2:.0f}")
            out.append(f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{ink}" stroke-width="2"/>')
        else:
            if speaker and item.get("tail", "auto") != "none":   # tail first: the balloon covers its base
                tx, ty = rect[0] * W + rect[2] * W / 2, (rect[1] + rect[3] * 0.82) * H
                dx, dy = (tx - px), (ty - py)
                norm = max((dx ** 2 + dy ** 2) ** 0.5, 1)
                ox, oy = -dy / norm * size * 0.9, dx / norm * size * 0.9
                out.append(f'<polygon points="{px + ox:.0f},{py + oy:.0f} {px - ox:.0f},{py - oy:.0f} '
                           f'{px + dx * 0.5:.0f},{py + dy * 0.5:.0f}" fill="{fill}" stroke="{ink}" '
                           f'stroke-width="2" stroke-linejoin="round"/>')
            out.append(f'<ellipse cx="{px:.0f}" cy="{py:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" '
                       f'fill="{fill}" stroke="{ink}" stroke-width="2"{dash}/>')
        y = py - box_h / 2 + size * 0.95
        for line in lines:
            out.append(f'<text x="{px:.0f}" y="{y:.0f}" font-size="{size:.0f}" fill="{ink}">'
                       f'{html.escape(line)}</text>')
            y += size * LINE
    out += ["</g>", "</svg>"]
    return "\n".join(out)


# ---- reading and writing the layout's text ---------------------------------------------

def page_spec(slug, page, version=None):
    specs, _ = thumbnails.parse_layouts(projects.read_artifact(slug, "layouts.md", version))
    return next((s for s in specs if s.get("page") == page), None)


def page_items(slug, page, version=None):
    spec = page_spec(slug, page, version)
    return items(spec) if spec else []


def set_items(slug, page, changes):
    """changes: {item index: {"text": ..., "at": ...}}. Rewrites that page's block in layouts.md."""
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
        if "text" in change:
            all_items[i]["text"] = " ".join(str(change["text"]).split())
        if change.get("at"):
            if change["at"] not in ANCHORS:
                raise ValueError(f"{change['at']!r} isn't one of {', '.join(ANCHORS)}")
            all_items[i]["at"] = change["at"]
            all_items[i].pop("x", None)
            all_items[i].pop("y", None)
    write_spec(slug, page, spec)
    return spec


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
    """Save the page's layout block, and redraw the sketch, which is drawn from it."""
    md = projects.read_artifact(slug, "layouts.md") or ""
    layouts = replace_block(md, page, spec)
    projects.write_artifact(slug, "layouts.md", layouts)
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
