"""ASCII page previews at true lettering scale.

One character cell = one letter of comic lettering. With lettering at
LETTERING_PT points, a cell is about 0.55 x pt wide and 1.2 x pt tall (one line of
lettering), so a 6.625" x 10.25" page at 7.5 pt is ~116 x 82 cells, and a balloon
in the preview is the size it will be on the printed page.

The Penciller writes one ```layout JSON block per page in layouts.md:

    {"page": 3, "side": "right",
     "tiers": [{"h": 2, "panels": [{"w": 1, "shot": "wide", "angle": "high",
                                    "horizon": 40, "bleed": false,
                                    "description": "what is drawn in the panel"}]}],
     "items": [{"panel": 1, "type": "balloon", "speaker": "WREN", "text": "...", "at": "top-left"},
               {"panel": 1, "type": "figure", "label": "WREN", "at": "bottom-right",
                "size": 70, "pose": "standing", "facing": "left"}]}

Tier heights and panel widths are relative weights. Items are placed with "at"
(top-left ... bottom-right, 9 positions) or "x"/"y" percentages of the panel.
Item types: balloon, whisper, thought, shout, caption, sfx, figure, object.

A page renders in three layers: art (figures, horizon; or model-drawn / image art),
frame (panel borders), lettering (balloons, captions, SFX). Art is clipped to
the panels; frame and lettering always win, so art can't damage them.

Any cell can also be shown inverted (light on dark), e.g. a night panel. Inversion
is a separate mask, stored after the page as a ```invert block of the same size
("#" = inverted). A panel or an item with "invert": true starts inverted;
lettering stays light unless its own item says "invert": true.
"""
import hashlib
import io
import json
import math
import re
import textwrap
import zlib
from dataclasses import dataclass, field

from . import asciitext
from .config import env

ANCHORS = {"top-left", "top", "top-right", "left", "middle", "right",
           "bottom-left", "bottom", "bottom-right", "center"}
LETTERING = {"balloon", "whisper", "thought", "shout", "caption", "sfx"}
SPEECH = {"balloon", "whisper", "thought", "shout"}
RAMP = " .:-=+*#%@"
MAX_WORDS_PER_PANEL = 25
T = "\0"   # transparent cell in a sprite


@dataclass
class Geometry:
    pt: float
    cell_w: float    # inches
    cell_h: float
    cols: int
    rows: int
    mx: int          # live-area margin, cells
    my: int
    gx: int          # gutters
    gy: int


def geometry():
    pt = float(env("LETTERING_PT") or 7.5)
    w_in, h_in = (float(v) for v in (env("PAGE_TRIM") or "6.625x10.25").lower().split("x"))
    cw, ch = 0.55 * pt / 72, 1.2 * pt / 72
    return Geometry(pt=pt, cell_w=cw, cell_h=ch,
                    cols=round(w_in / cw), rows=round(h_in / ch),
                    mx=max(1, round(0.375 / cw)), my=max(1, round(0.375 / ch)),
                    gx=max(1, round(0.125 / cw)), gy=max(1, round(0.125 / ch)))


@dataclass
class Panel:
    n: int
    x0: int
    y0: int
    x1: int
    y1: int
    spec: dict

    @property
    def inner(self):
        return self.x0 + 1, self.y0 + 1, self.x1 - 1, self.y1 - 1

    @property
    def size(self):
        x0, y0, x1, y1 = self.inner
        return x1 - x0 + 1, y1 - y0 + 1


@dataclass
class Page:
    number: int
    side: str
    geo: Geometry
    panels: list = field(default_factory=list)
    art: list = None
    frame: list = None
    letters: list = None
    owner: list = None
    issues: list = field(default_factory=list)
    faces: list = field(default_factory=list)   # (label, panel, set of head cells)
    invert: list = None                          # rows of bools: cells shown light on dark
    fills: dict = field(default_factory=dict)   # character name -> silhouette fill
    cast: dict = field(default_factory=dict)    # panel -> ["% WREN", "[=] lens"]
    sfx: dict = field(default_factory=dict)     # panel -> ["KRAKK"] (drawn as art)

    def legend(self):
        out = []
        for p in self.panels:
            s = p.spec
            bits = [b for b in (s.get("shot"), s.get("angle")) if b]
            head = f"P{p.n}" + (f" {' / '.join(bits).upper()}" if bits else "")
            line = f"{head}: {s.get('description', '').strip() or '(no description)'}"
            extras = self.cast.get(p.n, []) + [f"SFX {w}" for w in self.sfx.get(p.n, [])]
            out.append(line + (f" — {', '.join(extras)}" if extras else ""))
        return out


def _grid(g, fill):
    return [[fill] * g.cols for _ in range(g.rows)]


def _split(total, weights, gap):
    avail = total - gap * (len(weights) - 1)
    raw = [avail * w / sum(weights) for w in weights]
    sizes = [int(r) for r in raw]
    for i in sorted(range(len(raw)), key=lambda i: raw[i] - sizes[i], reverse=True)[:avail - sum(sizes)]:
        sizes[i] += 1
    return sizes


# ---- sprites ---------------------------------------------------------------

def _wrap(text, panel_w):
    text = " ".join(text.upper().split())
    width = max(8, min(round(math.sqrt(len(text) * 6)), panel_w - 6))
    return textwrap.wrap(text, width) or [""], width


def speech_sprite(kind, lines):
    """Balloons drawn only with art characters (see asciitext): the text inside is the only text."""
    w = max(len(l) for l in lines)
    body = [l.center(w) for l in lines]
    top, bottom = {"balloon": ("_", "~"), "whisper": ("_ ", "~ "), "thought": ("~", "~"),
                   "shout": ("/\\", "\\/")}[kind]
    rows = [T + (top * (w + 2))[:w + 2] + T]
    for i, l in enumerate(body):
        if kind == "shout":
            lft, rgt = "<", ">"
        elif kind == "whisper":
            lft, rgt = "{", "}"
        elif len(body) == 1 or kind == "thought":
            lft, rgt = "(", ")"
        elif i == 0:
            lft, rgt = "/", "\\"
        elif i == len(body) - 1:
            lft, rgt = "\\", "/"
        else:
            lft, rgt = "|", "|"
        rows.append(lft + " " + l + " " + rgt)
    rows.append(T + (bottom * (w + 2))[:w + 2] + T)
    return rows


def caption_sprite(lines):
    w = max(len(l) for l in lines)
    edge = "+" + "=" * (w + 2) + "+"
    return [edge] + ["| " + l.ljust(w) + " |" for l in lines] + [edge]


def sfx_sprite(text, size, max_w):
    """small/medium: the word itself (text), set off with art. large/huge: figlet
    lettering, drawn with art characters only."""
    import pyfiglet
    text = text.upper()
    if size in ("large", "huge"):
        fonts = ["big", "standard", "small"] if size == "huge" else ["standard", "small"]
        for font in fonts:
            art = pyfiglet.figlet_format(text, font=font, width=1000).rstrip("\n").split("\n")
            art = [asciitext.sanitize(l.rstrip()) for l in art]
            while art and not art[-1].strip():
                art.pop()
            if art and max(map(len, art)) <= max_w:
                return [l.replace(" ", T) for l in art]
    word = " ".join(text) if size != "small" else text
    framed = f"\\\\ {word} //" if size != "small" else f"* {word} *"
    line = framed if len(framed) <= max_w else text[:max_w]
    return [line.replace(" ", T)]


FILLS = "%#@&$"


def fill_for(label, taken):
    """A stable fill character per character name, unique on the page."""
    start = zlib.crc32(label.upper().encode()) % len(FILLS)
    for i in range(len(FILLS)):
        c = FILLS[(start + i) % len(FILLS)]
        if c not in taken.values() or taken.get(label.upper()) == c:
            return c
    return FILLS[start]


def figure_sprite(h, pose="standing", facing=None, fill="%"):
    """A filled silhouette, `h` rows tall, drawn with proportions corrected for tall cells.
    Names are text, so figures carry no label: the fill character identifies them."""
    h = max(h, 5)
    k = 2.18                         # cell height / cell width
    rows = []
    if pose == "closeup":
        hh = max(3, round(h * 0.75))
        hw = max(5, round(hh * k * 0.75))
        W = max(hw + 4, round(h * k * 0.9))
        for r in range(hh):
            t = (r + 0.5) / hh * 2 - 1
            wr = max(1, round(hw * math.sqrt(max(0.0, 1 - t * t))))
            line = (fill * wr).center(W)
            if r == round(hh * 0.4) and wr >= 5:
                eyes = "*" + " " * max(1, wr // 3) + "*"
                line = line[:W // 2 - len(eyes) // 2] + eyes + line[W // 2 - len(eyes) // 2 + len(eyes):]
            rows.append(line)
        for r in range(h - hh):
            rows.append((fill * min(W, hw + 2 + r * 4)).center(W))
        face = set((x, y) for y, l in enumerate(rows[:hh]) for x, c in enumerate(l) if c != " ")
    else:
        hh = max(2, round(h / 7))
        hw = max(3, round(hh * k * 0.8))
        sw = max(hw + 2, round(h * 0.25 * k))
        W = sw + 4
        torso = max(2, round(h * 0.42))
        for r in range(hh):
            t = (r + 0.5) / hh * 2 - 1
            wr = max(2, round(hw * math.sqrt(max(0.0, 1 - t * t))))
            rows.append((fill * wr).center(W))
        face = set((x, y) for y, l in enumerate(rows) for x, c in enumerate(l) if c != " ")
        for r in range(torso):
            tw = round(sw - (sw * 0.25) * r / torso)
            arms = r < torso * 0.8
            rows.append(((("|" if arms else " ") + " " + fill * tw + " " + ("|" if arms else " ")).center(W)))
        legs = h - hh - torso
        lw = max(1, round(sw * 0.28))
        gap = max(1, round(sw * 0.15))
        for r in range(legs):
            spread = round(r * 0.6) if pose == "running" else 0
            rows.append((fill * lw + " " * (gap + 2 * spread) + fill * lw).center(W))
        if facing in ("left", "right") and hh >= 2:
            r = hh // 2
            line = rows[r]
            idx = (line.rstrip().__len__()) if facing == "right" else (len(line) - len(line.lstrip()) - 1)
            if 0 <= idx < W:
                rows[r] = line[:idx] + (">" if facing == "right" else "<") + line[idx + 1:]
    width = max(map(len, rows))
    return [l.ljust(width).replace(" ", T) for l in rows], face


def object_sprite(w, h):
    w, h = max(w, 5), max(h, 3)
    edge = "[" + "=" * (w - 2) + "]"
    return [edge] + ["[" + T * (w - 2) + "]" for _ in range(h - 2)] + [edge]


# ---- placement ---------------------------------------------------------------

def _place(item, sprite, inner, issues, where):
    x0, y0, x1, y1 = inner
    sw, sh = max(map(len, sprite)), len(sprite)
    iw, ih = x1 - x0 + 1, y1 - y0 + 1
    if "x" in item or "y" in item:
        cx = x0 + round(float(item.get("x", 50)) / 100 * (iw - 1))
        cy = y0 + round(float(item.get("y", 50)) / 100 * (ih - 1))
        left, top = cx - sw // 2, cy - sh // 2
    else:
        at = item.get("at", "middle")
        if at not in ANCHORS:
            issues.append(f"{where}: unknown position {at!r}; using middle")
            at = "middle"
        v, _, hz = at.partition("-") if "-" in at else (at, "", at)
        top = {"top": y0 + 1}.get(v, y1 - sh if v == "bottom" else (y0 + y1 - sh + 1) // 2)
        left = {"left": x0 + 1}.get(hz, x1 - sw if hz == "right" else (x0 + x1 - sw + 1) // 2)
        if item.get("type") in ("figure", "object") and v == "bottom":
            top = y1 - sh + 1   # figures stand on the panel's bottom edge
    return left, top, sw, sh


def _stamp(layer, sprite, left, top, clip, owner=None, who=None, conflicts=None):
    x0, y0, x1, y1 = clip
    clipped = False
    for j, line in enumerate(sprite):
        for i, c in enumerate(line):
            if c == T:
                continue
            x, y = left + i, top + j
            if not (x0 <= x <= x1 and y0 <= y <= y1):
                clipped = True
                continue
            if owner is not None:
                prev = owner[y][x]
                if prev is not None and prev != who and conflicts is not None:
                    conflicts.add(prev)
                owner[y][x] = who
            layer[y][x] = c
    return clipped


# ---- rendering ---------------------------------------------------------------

def render_page(spec, geo=None):
    geo = geo or geometry()
    number = spec.get("page", 0)
    side = spec.get("side") or ("right" if number % 2 else "left")
    page = Page(number=number, side=side, geo=geo)
    page.art, page.frame = _grid(geo, " "), _grid(geo, None)
    page.letters, page.owner = _grid(geo, None), _grid(geo, None)
    page.invert = _grid(geo, False)
    issues = page.issues
    if spec.get("side") and number and spec["side"] != ("right" if number % 2 else "left"):
        issues.append(f"Page {number} is marked {spec['side']}, but odd pages are right-hand pages")

    tiers = spec.get("tiers") or []
    if not tiers:
        issues.append("no tiers")
        return page
    heights = [float(t.get("h", t.get("height", 1))) for t in tiers]
    if min(heights) <= 0:
        issues.append("tier heights must be positive")
        return page
    hs = _split(geo.rows - 2 * geo.my, heights, geo.gy)
    y = geo.my
    n = 0
    for ti, (tier, h) in enumerate(zip(tiers, hs)):
        panels = tier.get("panels") or [{}]
        widths = [float(p.get("w", 1)) for p in panels]
        if min(widths) <= 0:
            issues.append(f"row {ti + 1}: panel widths must be positive")
            widths = [1] * len(panels)
        ws = _split(geo.cols - 2 * geo.mx, widths, geo.gx)
        x = geo.mx
        for pi, (p, w) in enumerate(zip(panels, ws)):
            n += 1
            x0, y0, x1, y1 = x, y, x + w - 1, y + h - 1
            if p.get("bleed"):
                if ti == 0:
                    y0 = 0
                if ti == len(tiers) - 1:
                    y1 = geo.rows - 1
                if pi == 0:
                    x0 = 0
                if pi == len(panels) - 1:
                    x1 = geo.cols - 1
            if w < 8 or h < 4:
                issues.append(f"panel {n} is only {w}x{h} cells — too small to read")
            page.panels.append(Panel(n, x0, y0, x1, y1, p))
            x += w + geo.gx
        y += h + geo.gy

    for p in page.panels:
        _draw_panel(page, p)
    _draw_items(page, spec.get("items") or [])
    return page


def _draw_panel(page, p):
    """ ____
       |    |
       |____|   — art characters only; panel numbers and shots live in the legend."""
    f = page.frame
    for x in range(p.x0 + 1, p.x1):
        f[p.y0][x] = f[p.y1][x] = "_"
    for y in range(p.y0 + 1, p.y1 + 1):
        f[y][p.x0] = f[y][p.x1] = "|"
    if p.spec.get("invert"):
        x0, y0, x1, y1 = p.inner
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                page.invert[y][x] = True
    if p.spec.get("horizon") is not None:
        x0, y0, x1, y1 = p.inner
        hy = y0 + round(float(p.spec["horizon"]) / 100 * (y1 - y0))
        for x in range(x0, x1 + 1):
            page.art[hy][x] = "_"


def _draw_items(page, items):
    issues = page.issues
    panels = {p.n: p for p in page.panels}
    placed_speech = []          # (order, left, top, label)
    words = {}
    figures = {}                # panel -> [(label, center_x, top)]
    lettering = []

    for idx, item in enumerate(items):
        kind = item.get("type", "balloon")
        pn = item.get("panel")
        where = f"panel {pn}, {kind} {idx + 1}"
        if pn not in panels:
            issues.append(f"item {idx + 1}: no panel {pn!r}")
            continue
        p = panels[pn]
        inner = p.inner
        iw, ih = p.size
        if kind in ("figure", "object"):
            label = item.get("label") or item.get("text") or ""
            if kind == "figure":
                size = float(item.get("size", 90 if item.get("pose") == "closeup" else 70))
                fill = page.fills.setdefault(label.upper(), fill_for(label, page.fills))
                sprite, face = figure_sprite(max(5, round(ih * size / 100)),
                                             item.get("pose", "standing"), item.get("facing"), fill)
            else:
                sprite = object_sprite(round(iw * float(item.get("w", 20)) / 100),
                                       round(ih * float(item.get("h", 20)) / 100))
                face = set()
            page.cast.setdefault(pn, []).append(
                f"{page.fills[label.upper()]} {label}" if kind == "figure" else f"[=] {label}")
            left, top, sw, sh = _place(item, sprite, inner, issues, where)
            _stamp(page.art, sprite, left, top, inner)
            if item.get("invert"):
                _mark(page.invert, sprite, left, top, inner, True)
            if face:
                page.faces.append((label, pn, {(left + x, top + y) for x, y in face}))
            figures.setdefault(pn, []).append((label.upper(), left + sw // 2, top))
        elif kind in LETTERING:
            lettering.append((idx, item, p))
        else:
            issues.append(f"{where}: unknown item type")

    for idx, item, p in lettering:
        kind = item.get("type", "balloon")
        pn = p.n
        inner = p.inner
        iw, ih = p.size
        speaker = (item.get("speaker") or "").upper()
        text = item.get("text", "")
        if kind in SPEECH and speaker and text.upper().startswith(speaker + ":"):
            text = text[len(speaker) + 1:].strip()
        where = f"panel {pn}, {kind} {('(' + speaker + ') ') if speaker else ''}\"{text[:24]}\""
        if kind != "sfx":
            words[pn] = words.get(pn, 0) + len(text.split())

        if kind == "sfx":
            sprite = sfx_sprite(text, item.get("size", "medium"), iw - 2)
            if item.get("size") in ("large", "huge"):
                page.sfx.setdefault(pn, []).append(text.upper())
        elif kind == "caption":
            lines, _ = _wrap(text, iw)
            sprite = caption_sprite(lines)
        else:
            lines, _ = _wrap(text, iw)
            sprite = speech_sprite(kind, lines)
        if len(sprite) > ih:
            issues.append(f"{where}: too much copy — {len(sprite)} lines tall in a {ih}-line panel")

        left, top, sw, sh = _place(item, sprite, inner, issues, where)
        clip = (0, 0, page.geo.cols - 1, page.geo.rows - 1) if item.get("breakout") else inner
        conflicts = set()
        who = f"{kind} {speaker or text[:16]!r}"
        if _stamp(page.letters, sprite, left, top, clip, page.owner, who, conflicts):
            issues.append(f"{where}: runs off the page" if item.get("breakout") else
                          f"{where}: runs past the panel border (set \"breakout\": true if intended)")
        for other in sorted(conflicts):
            issues.append(f"panel {pn}: {who} overlaps {other}")
        g = page.geo
        if item.get("breakout") and (left < g.mx or top < g.my or left + sw > g.cols - g.mx or top + sh > g.rows - g.my):
            issues.append(f"{where}: breaks out past the live area — it may be trimmed")

        if kind in SPEECH and item.get("tail", "auto") != "none":
            _draw_tail(page, kind, left, top, sw, sh, speaker, figures.get(pn, []), inner)
        # lettering stays light on dark panels unless the item asks to be inverted
        _mark(page.invert, sprite, left, top, clip, bool(item.get("invert")), solid=kind != "sfx")
        if kind in SPEECH:
            placed_speech.append((idx, left, top, speaker))

    for pn, count in words.items():
        if count > MAX_WORDS_PER_PANEL:
            issues.append(f"panel {pn}: {count} words — over ~{MAX_WORDS_PER_PANEL}, likely crowded")
    for (i, l1, t1, s1), (j, l2, t2, s2) in zip(placed_speech, placed_speech[1:]):
        if t2 + 1 < t1 and l2 + 2 < l1:
            issues.append(f"balloon {j + 1} ({s2}) sits above and left of balloon {i + 1} ({s1}) "
                          "but is read after it — reading order fights the layout")
    for label, pn, cells in page.faces:
        covered = sum(1 for x, y in cells if page.letters[y][x] is not None)
        if cells and covered / len(cells) > 0.4:
            issues.append(f"panel {pn}: lettering covers {round(100 * covered / len(cells))}% of {label or 'a'}'s head")


def _mark(mask, sprite, left, top, clip, value, solid=False):
    """Set inversion under a sprite; `solid` covers its transparent corners' insides too (balloon bodies)."""
    x0, y0, x1, y1 = clip
    for j, line in enumerate(sprite):
        cells = [i for i, c in enumerate(line) if c != T]
        if not cells:
            continue
        span = range(cells[0], cells[-1] + 1) if solid else cells
        for i in span:
            x, y = left + i, top + j
            if x0 <= x <= x1 and y0 <= y <= y1:
                mask[y][x] = value


def _draw_tail(page, kind, left, top, sw, sh, speaker, figures, inner):
    x0, y0, x1, y1 = inner
    target = next((cx for label, cx, _ in figures if speaker and label.startswith(speaker)), None)
    base_y = top + sh
    mid = left + sw // 2
    if target is None:
        ch, x = "|", mid
    elif target < left + 2:
        ch, x = "/", left + 3
    elif target > left + sw - 3:
        ch, x = "\\", left + sw - 4
    else:
        ch, x = "|", max(left + 2, min(target, left + sw - 3))
    marks = ["@", "*"] if kind == "thought" else [ch, ch]
    for k, c in enumerate(marks):
        tx = x + (k if ch == "\\" else -k if ch == "/" else 0)
        ty = base_y + k
        if x0 <= tx <= x1 and y0 <= ty <= y1 and page.letters[ty][tx] is None:
            page.letters[ty][tx] = c


def compose(page, art=None):
    """Final text: art clipped to panels, then frame, then lettering on top."""
    g = page.geo
    base = art or page.art
    out = _grid(g, " ")
    for p in page.panels:
        x0, y0, x1, y1 = p.inner
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                c = base[y][x] if y < len(base) and x < len(base[y]) else " "
                out[y][x] = c if c.isprintable() else " "
    for layer in (page.frame, page.letters):
        for y in range(g.rows):
            for x in range(g.cols):
                if layer[y][x] is not None:
                    out[y][x] = layer[y][x]
    return "\n".join("".join(r) for r in out)


def mask_text(mask):
    """Rows of "#" (inverted) and " ", trailing spaces trimmed; "" when nothing is inverted."""
    rows = ["".join("#" if v else " " for v in row).rstrip() for row in mask or []]
    return "\n".join(rows).rstrip("\n") if any(rows) else ""


def text_to_mask(text, geo):
    lines = (text or "").split("\n")
    lines = (lines + [""] * geo.rows)[:geo.rows]
    return [[x < len(l) and l[x] != " " for x in range(geo.cols)] for l in lines]


def compose_invert(page, mask=None):
    """Final inversion: `mask` (e.g. an artist's) or the layout's, with lettering cells
    kept exactly as the layout set them."""
    base = mask or page.invert
    out = [row[:] for row in base]
    for y, row in enumerate(page.letters):
        for x, c in enumerate(row):
            if c is not None:
                out[y][x] = page.invert[y][x]
    return out


def protected_count(page, art):
    """How many frame/lettering cells a model's drawing tried to change."""
    changed = 0
    for layer in (page.frame, page.letters):
        for y, row in enumerate(layer):
            for x, c in enumerate(row):
                if c is not None and y < len(art) and x < len(art[y]) and art[y][x] != c:
                    changed += 1
    return changed


def text_to_grid(text, geo):
    lines = text.split("\n")
    grid = [list(l[:geo.cols].ljust(geo.cols)) for l in lines[:geo.rows]]
    while len(grid) < geo.rows:
        grid.append([" "] * geo.cols)
    return grid, (len(lines), max((len(l) for l in lines), default=0))


# ---- images --------------------------------------------------------------------

def image_size_for(panel, geo):
    w, h = panel.size
    aspect = (w * geo.cell_w) / (h * geo.cell_h)
    return "1536x1024" if aspect > 1.25 else "1024x1536" if aspect < 0.8 else "1024x1024"


def image_to_ascii(data, cols, rows, geo):
    """Convert an image to a cols x rows block of cells.

    Each cell is sampled at 4x8 sub-pixels (cells are ~2x taller than wide). Where a
    cell holds a strong stroke, the stroke's direction picks the character
    (- / | \\); elsewhere the cell's average darkness picks one from RAMP.
    """
    from PIL import Image, ImageFilter, ImageOps
    img = ImageOps.autocontrast(Image.open(io.BytesIO(data)).convert("L"))
    target = (cols * geo.cell_w) / (rows * geo.cell_h)
    w, h = img.size
    if w / h > target:                       # cover-fit: crop to the panel's shape
        nw = round(h * target)
        img = img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = round(w / target)
        img = img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    dark = ImageOps.invert(img.resize((cols * 4, rows * 8), Image.Resampling.LANCZOS))
    gx = dark.filter(ImageFilter.Kernel((3, 3), [-1, 0, 1, -2, 0, 2, -1, 0, 1], scale=8, offset=128))
    gy = dark.filter(ImageFilter.Kernel((3, 3), [-1, -2, -1, 0, 0, 0, 1, 2, 1], scale=8, offset=128))
    D, X, Y = dark.load(), gx.load(), gy.load()
    top = len(RAMP) - 1
    out = []
    for cy in range(rows):
        row = []
        for cx in range(cols):
            tone = peak = sx = sy = 0
            for y in range(cy * 8, cy * 8 + 8):
                for x in range(cx * 4, cx * 4 + 4):
                    v = D[x, y]
                    tone += v
                    peak = max(peak, v)
                    ex, ey = X[x, y] - 128, Y[x, y] - 128
                    sx += ex * ex - ey * ey      # double-angle sum: both sides of a line agree
                    sy += 2 * ex * ey
            tone /= 32
            if peak > 110 and math.hypot(sx, sy) / 32 > 60 and tone < 150:
                line_angle = (math.degrees(math.atan2(sy, sx)) / 2 + 90) % 180
                row.append("-" if line_angle < 22.5 or line_angle >= 157.5 else
                           "/" if line_angle < 67.5 else "|" if line_angle < 112.5 else "\\")
            else:
                row.append(RAMP[round(tone * top / 255)])
        out.append(row)
    return out


# ---- layouts.md <-> pages ---------------------------------------------------------

LAYOUT_RE = re.compile(r"```layout[^\n]*\n(.*?)```", re.S)


def parse_layouts(markdown):
    """Returns ([spec, ...], [error, ...]) from the ```layout blocks, sorted by page."""
    specs, errors = [], []
    for i, block in enumerate(LAYOUT_RE.findall(markdown or "")):
        try:
            spec = json.loads(block)
            if not isinstance(spec, dict):
                raise ValueError("a layout block must be a JSON object")
            spec["page"] = int(spec.get("page", 0))
            specs.append(spec)
        except (ValueError, TypeError) as e:
            errors.append(f"layout block {i + 1}: {e}")
    specs.sort(key=lambda s: s["page"])
    return specs, errors


def layout_hash(spec):
    return hashlib.sha1(json.dumps(spec, sort_keys=True).encode()).hexdigest()[:10]


def _heading(number, side, edited=False, layout=None):
    return (f"## Page {number} ({side})" + (" — edited" if edited else "")
            + (f" <!-- layout {layout} -->" if layout else ""))


def _blocks(art_text, invert_text):
    out = ["```text", art_text, "```"]
    if invert_text and invert_text.strip():
        out += ["```invert", invert_text.rstrip("\n"), "```"]
    return out


def page_markdown(page, art_text, notes=(), spec=None, invert=None):
    issues = list(page.issues) + list(notes)
    invert = mask_text(page.invert) if invert is None else invert
    parts = [_heading(page.number, page.side, layout=spec and layout_hash(spec)), "",
             *_blocks(art_text, invert), ""]
    parts += [f"- {l}" for l in page.legend()]
    if issues:
        parts += ["", "**Issues**", ""] + [f"- ⚠ {i}" for i in issues]
    return "\n".join(parts) + "\n"


def document(title, pages_md, errors=(), geo=None):
    geo = geo or geometry()
    head = [f"# {title}", "",
            f"<!-- generated; {geo.cols}x{geo.rows} cells, one cell = one letter at {geo.pt:g} pt lettering -->", ""]
    if errors:
        head += ["**Layout errors**", ""] + [f"- ⚠ {e}" for e in errors] + [""]
    return "\n".join(head) + "\n".join(pages_md)


# A page section: heading, a ```text block, an optional ```invert block, then notes until the next page.
PAGE_RE = re.compile(r"^## Page (\d+)([^\n]*)\n+```text\n(.*?)\n```\n(?:```invert\n(.*?)\n```\n)?(.*?)(?=^## Page |\Z)",
                     re.S | re.M)
EDITED_NOTE = "hand-edited — kept when previews are regenerated"
CHANGED_NOTE = "the layout changed after this page was hand-edited — revert it to see the new render"
REVERTED_NOTE = "hand edits reverted — the page will be redrawn on the next run"


def parse_thumbnails(markdown):
    """thumbnails*.md -> {page: {art, invert, notes, edited, side, layout}}"""
    pages = {}
    for m in PAGE_RE.finditer(markdown or ""):
        rest = m.group(2)
        side = re.search(r"\((\w+)\)", rest)
        layout = re.search(r"layout ([0-9a-f]+)", rest)
        pages[int(m.group(1))] = {
            "art": m.group(3), "invert": m.group(4) or "", "notes": m.group(5).strip(), "edited": "— edited" in rest,
            "side": side.group(1) if side else "", "layout": layout.group(1) if layout else None,
        }
    return pages


def _section(number, p):
    blocks = "\n".join(_blocks(p["art"], p.get("invert", "")))
    return f"{_heading(number, p['side'], p['edited'], p['layout'])}\n\n{blocks}\n\n{p['notes']}\n"


def _with_note(notes, note, present):
    lines = [l for l in notes.split("\n") if note not in l]
    text = "\n".join(lines).strip()
    return (text + ("\n\n" if text else "") + f"- ⚠ {note}") if present else text


def keep_edited(p, number, spec=None):
    """Markdown for a hand-edited page carried over a regeneration."""
    changed = spec is not None and p["layout"] is not None and p["layout"] != layout_hash(spec)
    return _section(number, {**p, "notes": _with_note(p["notes"], CHANGED_NOTE, changed)})


def merge_edited(generated_md, current_md):
    """Put hand-edited pages from current_md back into freshly generated markdown."""
    edited = {n: p for n, p in parse_thumbnails(current_md).items() if p["edited"]}
    if not edited:
        return generated_md
    matches = list(PAGE_RE.finditer(generated_md))
    if not matches:
        return generated_md
    out = [generated_md[:matches[0].start()]]
    for m in matches:
        n = int(m.group(1))
        out.append(_section(n, edited[n]) if n in edited else m.group(0))
    return "".join(out)


def replace_page(markdown, number, art=None, edited=None, invert=None):
    """Set a page's art, inversion mask and/or edited flag in a thumbnails document."""
    matches = list(PAGE_RE.finditer(markdown or ""))
    target = next((m for m in matches if int(m.group(1)) == number), None)
    if target is None:
        raise KeyError(f"page {number}")
    p = parse_thumbnails(target.group(0))[number]
    if art is not None:
        p["art"] = art
    if invert is not None:
        p["invert"] = invert
    if edited is not None:
        p["edited"] = edited
        if not edited:
            p["layout"] = None   # forget which layout it was drawn from, so it gets redrawn
        p["notes"] = _with_note(p["notes"], EDITED_NOTE, edited)
        p["notes"] = _with_note(p["notes"], CHANGED_NOTE, False)
        p["notes"] = _with_note(p["notes"], REVERTED_NOTE, not edited)
    return markdown[:target.start()] + _section(number, p) + markdown[target.end():]


def render_layouts(markdown, previous=None):
    """layouts.md -> (thumbnails.md content, specs, feedback for the Penciller).
    Hand-edited pages in `previous` are kept."""
    geo = geometry()
    specs, errors = parse_layouts(markdown)
    prev = parse_thumbnails(previous)
    pages, feedback = [], list(errors)
    for spec in specs:
        page = render_page(spec, geo)
        feedback += [f"page {page.number}: {i}" for i in page.issues]
        old = prev.get(page.number)
        if old and old["edited"]:
            pages.append(keep_edited(old, page.number, spec))
        else:
            pages.append(page_markdown(page, compose(page), spec=spec))
    return document("Thumbnails — layout render", pages, errors, geo), specs, feedback


def script_for_page(script, number):
    """The '## Page N' section of the script, if the Scripter used that heading."""
    m = re.search(rf"^#+ *Page {number}\b.*?(?=^#+ *Page \d+\b|\Z)", script or "", re.S | re.M | re.I)
    return m.group(0).strip() if m else ""


def labels_by_panel(page):
    """Figure/object labels per panel, from the spec the page was rendered with."""
    out = {}
    for label, pn, _ in page.faces:
        out.setdefault(pn, []).append(label)
    return out


def looks_for(bible, labels):
    """The bible paragraph describing each label, verbatim, so image prompts stay on model."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", bible or "") if p.strip()]
    found = []
    for label in dict.fromkeys(labels):
        hits = [p for p in paras if label.lower() in p.lower()]
        best = next((p for p in hits if "visual" in p.lower()), hits[0] if hits else None)
        if best:
            found.append(best[:500])
    return " ".join(found)
