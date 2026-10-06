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

MARGIN = 0.012       # page margin, as a fraction of the page: rendered art is near full-bleed,
                     # so the layer's grid must match the drawn page, not a print trim - a 5%
                     # margin put every panel 5% inside the art and skewed all the lettering
GUTTER = 0.01        # between panels: the models draw thin gutters
FONT = "'Comic Sans MS', 'Comic Neue', 'Chalkboard', 'Segoe Print', sans-serif"   # Comic Neue: the server's, for renders
LINE = 1.22          # line height, in em
CHAR = 0.62          # average glyph width, in em — enough for wrapping
SIZES = {"caption": 0.0175, "balloon": 0.019, "whisper": 0.018, "thought": 0.019, "shout": 0.023,
         "location": 0.02}
SFX_SIZES = {"small": 0.03, "medium": 0.045, "large": 0.065, "huge": 0.09}
SFX_STYLES = ("classic", "impact", "quake", "boom")   # how dramatic the display lettering is
ANCHORS = {   # keyword -> (x, y) inside the panel
    "top-left": (0.24, 0.18), "top": (0.5, 0.16), "top-right": (0.76, 0.18),
    "left": (0.22, 0.5), "middle": (0.5, 0.5), "center": (0.5, 0.5), "right": (0.78, 0.5),
    "bottom-left": (0.24, 0.82), "bottom": (0.5, 0.84), "bottom-right": (0.76, 0.82),
}
KINDS = ("balloon", "whisper", "thought", "shout", "caption", "location", "sfx")


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


def svg(spec, ctx=None, rects=None):
    """The page's text layer: transparent SVG, balloons and captions over the art."""
    return layer(spec, ctx, rects)[0]


def layer(spec, ctx=None, rects=None):
    """(svg, boxes, tails): the drawn layer, each item's drawn box in page fractions
    (x0, y0, x1, y1) for hit areas, and each tailed balloon's tail target (x, y).
    `rects` overrides the panel grid - detect_rects measures it from the drawn art."""
    ctx = ctx or {}
    W, H = page_size()
    rects = rects or panel_rects(spec)
    number = spec.get("page", 0)
    chapter = ctx.get("chapter")
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
           f'<g font-family="{FONT}" text-anchor="middle">']
    label = f"CHAPTER {chapter} — PAGE {number}" if chapter and number == 1 else f"PAGE {number}"
    placed, boxes, tails = [], {}, {}
    out.append(f'<text x="{round(W * 0.015)}" y="{round(H * 0.012) + round(W * 0.016)}" text-anchor="start" '
               f'font-size="{round(W * 0.016)}" fill="#7ec8ff" stroke="#10304a" '
               f'stroke-width="2.5" paint-order="stroke">{html.escape(label)}</text>')
    for item in items(spec):
        kind = item["type"]
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
            style = item.get("style") if item.get("style") in SFX_STYLES else "classic"
            if style == "impact":
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
        size = SIZES.get(kind, 0.019) * W
        width = min(rect[2] * 0.86, 0.6) * W
        limit = max(8, int(width / (size * CHAR)))
        lines = wrap(text, limit) if kind in ("caption", "location") else balloon_wrap(text, limit)
        # a balloon must fit its panel: in a short strip tier, wrap flat and wide instead of tall
        max_lines = max(1, int((rect[3] * H * 0.62) / (size * LINE)))
        if len(lines) > max_lines:
            per_line = min(limit, max(10, -(-len(text) // max_lines)))
            lines = wrap(text, per_line)
        box_w = max(len(l) for l in lines) * size * CHAR
        box_h = len(lines) * size * LINE
        rx = box_w / 2 + size * 1.2
        ry = max(box_h / 2 + size * 0.9, rx * 0.45)
        pad = size * 0.5
        bounds = (rect[0] * W, rect[1] * H, (rect[0] + rect[2]) * W, (rect[1] + rect[3]) * H)
        x0, y0, x1, y1 = nudge((px - rx - pad, py - ry - pad, px + rx + pad, py + ry + pad), placed, bounds)
        bw, bh = x1 - x0, y1 - y0        # keep the box inside its drawn panel when it fits
        if bw <= bounds[2] - bounds[0]:
            x0 = min(max(x0, bounds[0]), bounds[2] - bw); x1 = x0 + bw
        if bh <= bounds[3] - bounds[1]:
            y0 = min(max(y0, bounds[1]), bounds[3] - bh); y1 = y0 + bh
        placed.append((x0, y0, x1, y1))
        boxes[item["i"]] = (x0 / W, y0 / H, x1 / W, y1 / H)
        px, py = (x0 + x1) / 2, (y0 + y1) / 2
        dark = item.get("invert", kind == "location")   # location headers run dark by default
        fill, ink = ("#111", "#fff") if dark else ("#fff", "#111")
        dash = ' stroke-dasharray="6 5"' if kind == "whisper" else ""
        if kind == "location":
            cw, ch = box_w + size * 2.0, box_h + size * 1.1
            out.append(f'<rect x="{px - cw / 2:.0f}" y="{py - ch / 2:.0f}" width="{cw:.0f}" '
                       f'height="{ch:.0f}" fill="{fill}" stroke="{ink}" stroke-width="2.5"/>')
            y = py - box_h / 2 + size * 0.95
            for line in lines:
                out.append(f'<text x="{px:.0f}" y="{y:.0f}" font-size="{size:.0f}" fill="{ink}" '
                           f'font-weight="bold" letter-spacing="1.5">{html.escape(line)}</text>')
                y += size * LINE
            out[start:] = [f'<g data-item="{item["i"]}">'] + out[start:] + ["</g>"]
            continue
        if kind == "caption":
            # action text: a bright box with a heavy border, so it reads against any art
            fill, ink = ("#111", "#ffe14d") if dark else ("#ffe14d", "#111")
            cw, ch = box_w + size * 1.4, box_h + size * 0.9
            out.append(f'<rect x="{px - cw / 2:.0f}" y="{py - ch / 2:.0f}" width="{cw:.0f}" '
                       f'height="{ch:.0f}" rx="{size * 0.3:.0f}" fill="{fill}" stroke="{ink}" stroke-width="3"/>')
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
            if speaker and item.get("tail", "auto") != "none":
                # the tail target is still tracked (the lettering desk drags it),
                # but no pointer is drawn: against real art the arrows kept landing wrong
                if item.get("tail_x") is not None and item.get("tail_y") is not None:
                    tx = (rect[0] + rect[2] * float(item["tail_x"]) / 100) * W
                    ty = (rect[1] + rect[3] * float(item["tail_y"]) / 100) * H
                else:
                    tx, ty = rect[0] * W + rect[2] * W / 2, (rect[1] + rect[3] * 0.82) * H
                tails[item["i"]] = (round(tx / W, 4), round(ty / H, 4))
            out.append(f'<ellipse cx="{px:.0f}" cy="{py:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" '
                       f'fill="{fill}" stroke="{ink}" stroke-width="2"{dash}/>')
            if speaker:                 # the tail used to say who speaks; now a small name does
                out.append(f'<text x="{px:.0f}" y="{py - ry - size * 0.35:.0f}" font-size="{size * 0.72:.0f}" '
                           f'fill="{ink}" font-weight="bold" letter-spacing="1" stroke="{fill}" '
                           f'stroke-width="3" paint-order="stroke">{html.escape(speaker)}</text>')
        y = py - box_h / 2 + size * 0.95
        for line in lines:
            out.append(f'<text x="{px:.0f}" y="{y:.0f}" font-size="{size:.0f}" fill="{ink}">'
                       f'{html.escape(line)}</text>')
            y += size * LINE
        out[start:] = [f'<g data-item="{item["i"]}">'] + out[start:] + ["</g>"]
    out += ["</g>", "</svg>"]
    return "\n".join(out), {i: [round(v, 4) for v in b] for i, b in boxes.items()}, tails


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


# ---- the drawn grid: detected from the art, because the model's page is the real page ----

def detect_rects(spec, art_bytes):
    """{panel: (x, y, w, h)} measured from the drawn art, or None when there is no art.

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
