"""Page prompts — the writers' room's deliverable.

For every page, one self-contained markdown prompt to paste into an image model
(outside the room) to draw the finished comic page. Assembled in code, not by a
model, so it always matches the room's files and the character descriptions go in
word for word (a model would paraphrase them and the characters would drift):

    format        trim, orientation, left/right page
    style         the brief's visual direction (the same on every page)
    characters    the bible's description of everyone on the page, verbatim
    layout        a box map of the page drawn to scale, then rows and panels with their share
    panels        shot, angle, light, what happens, who is where, exact lettering
    script        the page's script, for reference
"""
import json
import re

from . import projects, thumbnails
from .config import env

WHERE = {
    "top-left": "top left", "top": "top center", "top-right": "top right",
    "left": "middle left", "middle": "center", "center": "center", "right": "middle right",
    "bottom-left": "bottom left", "bottom": "bottom center", "bottom-right": "bottom right",
}
KIND = {
    "balloon": "Speech balloon", "whisper": "Whisper balloon (dashed outline)",
    "thought": "Thought bubble (cloud with bubble trail)", "shout": "Burst balloon (spiky outline, shouting)",
    "caption": "Caption box",
}
SFX_SIZE = {"small": "small", "medium": "medium", "large": "large, bold", "huge": "huge, dramatic"}
HOW_TO_USE = """How to use: paste one page's prompt (everything under its heading) into an image model
that can draw comic pages, one page at a time. Keep the same model and settings for the whole
book so the style and characters stay consistent."""


def section(markdown, *words):
    """The body of the first heading that contains any of `words` (case-insensitive)."""
    lines = (markdown or "").split("\n")
    for i, line in enumerate(lines):
        m = re.match(r"^(#+)\s+(.*)", line)
        if m and any(w in m.group(2).lower() for w in words):
            level = len(m.group(1))
            body = []
            for nxt in lines[i + 1:]:
                h = re.match(r"^(#+)\s", nxt)
                if h and len(h.group(1)) <= level:
                    break
                body.append(nxt)
            return "\n".join(body).strip()
    m = re.search(r"\*\*[^*]*(" + "|".join(words) + r")[^*]*\*\*\s*[—:-]?\s*(.+)", markdown or "", re.I)
    return m.group(2).strip() if m else ""


def clean_look(text):
    """A bible paragraph as one line: no headings, no "Visual lock" label."""
    lines = [l.strip() for l in (text or "").split("\n") if l.strip() and not l.lstrip().startswith("#")]
    joined = " ".join(lines)
    return re.sub(r"^\W*visual lock\W*", "", joined, flags=re.I).strip()


def book_title(pitch):
    m = re.search(r"^#\s+(.+)$", pitch or "", re.M)
    return m.group(1).strip() if m else "Untitled"


def where(item):
    if "x" in item or "y" in item:
        x, y = float(item.get("x", 50)), float(item.get("y", 50))
        h = "left" if x < 34 else "right" if x > 66 else "center"
        v = "upper" if y < 34 else "lower" if y > 66 else "middle"
        return "center" if (h, v) == ("center", "middle") else f"{v} {h}"
    return WHERE.get(item.get("at", "middle"), item.get("at", "center"))


def share(part, whole):
    pct = round(100 * part / whole)
    for frac, label in ((100, "the full"), (50, "half the"), (33, "a third of the"), (67, "two thirds of the"),
                        (25, "a quarter of the"), (75, "three quarters of the")):
        if abs(pct - frac) <= 2:
            return f"{label}"
    return f"about {pct}% of the"


def layout_lines(spec):
    tiers = spec.get("tiers") or []
    total_h = sum(float(t.get("h", t.get("height", 1))) for t in tiers) or 1
    out, n = [], 0
    for ti, tier in enumerate(tiers):
        h = float(tier.get("h", tier.get("height", 1)))
        panels = tier.get("panels") or [{}]
        total_w = sum(float(p.get("w", 1)) for p in panels) or 1
        pos = "top" if ti == 0 else "bottom" if ti == len(tiers) - 1 else "middle"
        cells = []
        for pi, p in enumerate(panels):
            n += 1
            side = ("" if len(panels) == 1 else
                    "left" if pi == 0 else "right" if pi == len(panels) - 1 else "center")
            width = "full width" if len(panels) == 1 else f"{side}, {share(float(p.get('w', 1)), total_w)} width"
            extra = ", bleeding off the page edge" if p.get("bleed") else ""
            cells.append(f"panel {n} ({width}{extra})")
        out.append(f"- Row {ti + 1} ({pos}, {share(h, total_h)} page height): " + "; ".join(cells))
    return out


MAP_COLS = 44          # the panel map's width in characters
CELL = 2.18            # a character cell is this much taller than it is wide


def draw_box(grid, x0, y0, x1, y1, label):
    def edge(y, x, ch):     # where two panel borders meet, a corner
        grid[y][x] = "+" if grid[y][x] in ("-", "|", "+") and grid[y][x] != ch else ch

    for x in range(x0, x1 + 1):
        edge(y0, x, "-")
        edge(y1, x, "-")
    for y in range(y0, y1 + 1):
        edge(y, x0, "|")
        edge(y, x1, "|")
    for y, x in ((y0, x0), (y0, x1), (y1, x0), (y1, x1)):
        grid[y][x] = "+"
    cy, cx = (y0 + y1) // 2, (x0 + x1) // 2 - len(label) // 2
    drawn = ""
    for i, ch in enumerate(label):
        if x0 < cx + i < x1:
            grid[cy][cx + i] = ch
            drawn += ch
    return {"row": cy, "col": cx, "text": drawn}


def panel_grid(spec, cols=MAP_COLS):
    """(lines, labels, bleeds): the page drawn as boxes — panel borders and numbers, no contents.

    Any layout the format can describe comes out right, because the boxes are the tier and
    panel fractions themselves; `labels` says where each number landed, so a screen can make
    it clickable."""
    tiers = spec.get("tiers") or []
    if not tiers:
        return [], [], False
    w_in, h_in = (float(v) for v in (env("PAGE_TRIM") or "6.625x10.25").lower().split("x"))
    heights = [float(t.get("h", t.get("height", 1))) or 1 for t in tiers]
    total_h = sum(heights) or 1
    rows = max(3 * len(tiers) + 1, round(cols * (h_in / w_in) / CELL))
    grid = [[" "] * cols for _ in range(rows)]
    labels = []
    bleeds, n, y, down = False, 0, 0, 0.0
    for ti, (tier, h) in enumerate(zip(tiers, heights)):
        down += h
        y1 = rows - 1 if ti == len(tiers) - 1 else min(rows - 1 - 2 * (len(tiers) - ti - 1),
                                                       max(y + 2, round((rows - 1) * down / total_h)))
        panels = tier.get("panels") or [{}]
        widths = [float(p.get("w", 1)) or 1 for p in panels]
        total_w = sum(widths) or 1
        x, across = 0, 0.0
        for pi, (panel, w) in enumerate(zip(panels, widths)):
            n += 1
            across += w
            x1 = cols - 1 if pi == len(panels) - 1 else min(cols - 1 - 3 * (len(panels) - pi - 1),
                                                            max(x + 3, round((cols - 1) * across / total_w)))
            bleeds = bleeds or bool(panel.get("bleed"))
            label = draw_box(grid, x, y, x1, y1, f"{n}*" if panel.get("bleed") else str(n))
            labels.append({"n": n, **label})
            x = x1
        y = y1
    return ["".join(row).rstrip() for row in grid], labels, bleeds


def panel_map(spec, cols=MAP_COLS):
    """The box diagram as markdown, for a page prompt."""
    lines, _, bleeds = panel_grid(spec, cols)
    if not lines:
        return []
    fence = "`" * 3
    return [fence + "text", *lines, fence] + (["(* bleeds off the page edge)"] if bleeds else [])


def panel_places(spec):
    """{panel number: where it sits on the page, in words}."""
    tiers = spec.get("tiers") or []
    total_h = sum(float(t.get("h", t.get("height", 1))) for t in tiers) or 1
    out, n = {}, 0
    for ti, tier in enumerate(tiers):
        h = float(tier.get("h", tier.get("height", 1)))
        panels = tier.get("panels") or [{}]
        total_w = sum(float(p.get("w", 1)) for p in panels) or 1
        for pi, panel in enumerate(panels):
            n += 1
            side = ("full width" if len(panels) == 1 else
                    ("left" if pi == 0 else "right" if pi == len(panels) - 1 else "center")
                    + f", {share(float(panel.get('w', 1)), total_w)} width")
            bleed = " · bleeds off the page edge" if panel.get("bleed") else ""
            out[n] = f"row {ti + 1} of {len(tiers)}, {share(h, total_h)} page height · {side}{bleed}"
    return out


def panel_dialog(items):
    """A panel's lettering, in reading order: who says it, where it sits, and the words."""
    out = []
    for item in items:
        kind = item.get("type")
        if kind not in KIND and kind != "sfx":
            continue
        text = " ".join(str(item.get("text", "")).split())
        speaker = (item.get("speaker") or "").upper()
        if kind in KIND and speaker and text.upper().startswith(speaker + ":"):
            text = text[len(speaker) + 1:].strip()
        if kind == "sfx":
            label = f"Sound effect, {SFX_SIZE.get(item.get('size', 'medium'), 'medium')}"
        else:
            label = KIND[kind].split("(")[0].strip()
            if speaker and kind != "caption":
                label += f" — {speaker}" + (" (off-panel)" if item.get("tail") == "none" else "")
        out.append({"kind": kind, "label": label, "where": where(item), "text": text.upper()})
    return out


def panel_figures(items):
    out = []
    for f in items:
        if f.get("type") not in ("figure", "object"):
            continue
        label = f.get("label") or f.get("text") or "object"
        if f.get("type") == "figure":
            facing = f", facing {f['facing']}" if f.get("facing") else ""
            pose = f", {f['pose']}" if f.get("pose") not in (None, "standing", "closeup") else ""
            dark = ", silhouetted" if f.get("invert") else ""
            out.append({"who": label.upper(), "what": f"{where(f)}; {size_phrase(f)}{facing}{pose}{dark}"})
        else:
            out.append({"who": label, "what": where(f)})
    return out


def page_view(spec):
    """A page for the screen: the box map, then every panel's description and its dialog.

    The map is the layout and nothing else — panel borders and a number per panel — so it
    reads the same whatever the page does: a nine-panel grid, one splash, a wide tier over
    two narrow ones."""
    lines, labels, bleeds = panel_grid(spec)
    places = panel_places(spec)
    by_panel = {}
    for item in spec.get("items") or []:
        by_panel.setdefault(item.get("panel"), []).append(item)
    panels = []
    specs = [p for t in spec.get("tiers") or [] for p in (t.get("panels") or [{}])]
    for n, panel in enumerate(specs, 1):
        items = by_panel.get(n, [])
        notes = []
        if panel.get("invert"):
            notes.append("Dark panel — night or darkness, lit by what little is in the scene.")
        if panel.get("horizon") is not None and not 34 <= float(panel["horizon"]) <= 66:
            notes.append(f"Horizon {'high' if float(panel['horizon']) < 34 else 'low'} in the frame.")
        shot = [b for b in (panel.get("shot"), panel.get("angle") and f"{panel['angle']} angle") if b]
        panels.append({"n": n, "shot": ", ".join(shot), "place": places.get(n, ""),
                       "description": panel.get("description") or "", "notes": notes,
                       "figures": panel_figures(items), "dialog": panel_dialog(items)})
    return {"page": spec.get("page", 0), "map": lines, "labels": labels,
            "bleeds": bleeds, "panels": panels}


def size_phrase(item):
    if item.get("pose") == "closeup":
        return "close-up, head and shoulders filling the panel"
    size = float(item.get("size", 70))
    return ("full figure, small in the frame" if size < 35 else
            "full figure, about half the panel height" if size < 60 else
            "full figure, most of the panel height" if size < 90 else
            "full figure, filling the panel height")


def panel_block(n, panel_spec, items, page_spec):
    s = panel_spec
    bits = [b.upper() for b in (s.get("shot"), s.get("angle") and f"{s['angle']} angle") if b]
    head = f"### Panel {n}" + (f" — {', '.join(bits)}" if bits else "")
    lines = [head, "", f"**Scene:** {s.get('description') or '(no description given)'}"]
    if s.get("invert"):
        lines += ["", "**Light:** dark panel — night or darkness; lit mostly by the few light sources in the scene."]
    if s.get("horizon") is not None and not 34 <= float(s["horizon"]) <= 66:
        lines += ["", f"**Camera:** horizon {'high' if float(s['horizon']) < 34 else 'low'} in the frame."]
    figures = [i for i in items if i.get("type") in ("figure", "object")]
    if figures:
        lines += ["", "**Who and what is where:**", ""]
        for f in figures:
            label = f.get("label") or f.get("text") or "object"
            if f.get("type") == "figure":
                facing = f", facing {f['facing']}" if f.get("facing") else ""
                pose = f", {f['pose']}" if f.get("pose") not in (None, "standing", "closeup") else ""
                dark = ", silhouetted" if f.get("invert") else ""
                lines.append(f"- {label.upper()} — {where(f)}; {size_phrase(f)}{facing}{pose}{dark}")
            else:
                lines.append(f"- {label} — {where(f)}")
    lettering = [i for i in items if i.get("type") in KIND or i.get("type") == "sfx"]
    if lettering and page_spec.get("text_layer"):
        lines += ["", "**Keep these areas clear — the lettering is added afterwards as a separate layer, "
                  "so draw no words here, just uncluttered art with room for a balloon:**", ""]
        for i, item in enumerate(lettering, 1):
            kind = item.get("type")
            room = "a sound effect" if kind == "sfx" else f"a {KIND[kind].split('(')[0].strip().lower()}"
            words = len(str(item.get("text", "")).split())
            lines.append(f"{i}. {where(item)} — space for {room} of about {words} words")
    elif lettering:
        lines += ["", "**Lettering, in reading order (letter exactly this, nothing else):**", ""]
        for i, item in enumerate(lettering, 1):
            kind = item.get("type")
            text = " ".join(str(item.get("text", "")).split())
            speaker = (item.get("speaker") or "").upper()
            if kind in KIND and speaker and text.upper().startswith(speaker + ":"):
                text = text[len(speaker) + 1:].strip()
            if kind == "sfx":
                desc = f"Sound effect, {SFX_SIZE.get(item.get('size', 'medium'), 'medium')}, drawn into the art"
            else:
                desc = KIND[kind]
                if speaker and kind != "caption":
                    tail = item.get("tail", "auto")
                    desc += f" from {speaker}" + (" (speaker off-panel, no tail)" if tail == "none" else "")
            extras = []
            if item.get("breakout"):
                extras.append("breaking out over the panel border")
            if item.get("invert"):
                extras.append("light text on a black box")
            extra = f" ({'; '.join(extras)})" if extras else ""
            lines.append(f"{i}. {desc}, {where(item)}{extra}: \"{text.upper()}\"")
    return "\n".join(lines)


def page_prompt(spec, ctx):
    """One page's prompt. In "layer" mode the art is drawn with no text at all and the
    lettering is rendered separately (see lettering.py)."""
    number = spec.get("page", 0)
    side = spec.get("side") or ("right" if number % 2 else "left")
    items = spec.get("items") or []
    panel_specs = [p for t in spec.get("tiers") or [] for p in (t.get("panels") or [{}])]
    names = []
    for i in items:
        for name in (i.get("label") if i.get("type") == "figure" else None, i.get("speaker")):
            if name and name.upper() not in [n.upper() for n in names]:
                names.append(name)
    chapter = ctx.get("chapter")
    label = f"CHAPTER {chapter} — PAGE {number}" if chapter and number == 1 else f"PAGE {number}"
    out = [
        f"## Page {number}" + (f" of {ctx['pages']}" if ctx.get("pages") else "") + f" — {ctx['title']}"
        + (f", chapter {chapter}" if chapter else ""),
        "",
        f"Draw one finished comic book page: a portrait page, {ctx['trim']} (about 2:3), the "
        f"{side}-hand page of the book, with {len(panel_specs)} panels. Fully inked and colored, "
        "clean panel borders with even white gutters, and professional comic lettering.",
        "",
        "**Style (the same on every page):**",
        "",
        ctx["style"] or "(no visual direction in the brief yet)",
    ]
    if names:
        out += ["", "**Characters — draw them exactly as described:**", ""]
        for name in names:
            look = clean_look(thumbnails.looks_for(ctx["bible"], [name]))
            out.append(f"- **{name.upper()}** — {look or '(no description in the bible yet)'}")
    if ctx.get("lettering") != "layer":
        out += ["", f"**Page number:** in the top-left corner of the page, in small light-blue lettering: \"{label}\"."]
    out += ["", "**Page layout, top to bottom** (the map is the page itself, panels to scale):", "",
            *panel_map(spec), "", *layout_lines(spec), ""]
    by_panel = {}
    for item in items:
        by_panel.setdefault(item.get("panel"), []).append(item)
    layer = ctx.get("lettering") == "layer"
    for n, p in enumerate(panel_specs, 1):
        out += [panel_block(n, p, by_panel.get(n, []), dict(spec, text_layer=layer)), ""]
    if layer:
        out += [
            "**Rules:** draw NO text anywhere on this page — no balloons, no captions, no sound "
            "effects, no page number, no titles, signatures or watermarks. The lettering is added "
            "afterwards on a transparent layer, so leave the areas listed under each panel "
            "uncluttered (sky, wall, shadow — nothing the reader needs to see). Keep the "
            "characters' looks identical to their descriptions.",
        ]
    else:
        out += [
            "**Rules:** letter every balloon, caption and sound effect exactly as written above, in "
            "all-caps comic lettering, and add no other text apart from the light-blue page number "
            "(no titles, signatures or watermarks). Keep balloons clear of faces, with tails pointing at the speaker. Keep the "
            "characters' looks identical to their descriptions.",
        ]
    script = thumbnails.script_for_page(ctx["script"], number)
    if script:
        fence = "`" * 3
        out += ["", "**The page's script, for reference:**", "", fence + "text",
                script.replace(fence, "'" * 3), fence]
    return "\n".join(out).strip() + "\n"


def context(slug, version=None):
    read = lambda name: projects.read_artifact(slug, name, version) or ""
    pages = None
    m = re.search(r"Target length:\s*(\d+)", read("pitch.md"))
    if m:
        pages = int(m.group(1))
    w_in, h_in = (float(v) for v in (env("PAGE_TRIM") or "6.625x10.25").lower().split("x"))
    settings_file = projects.project_dir(slug) / "round-settings.json"
    settings = json.loads(settings_file.read_text()) if settings_file.exists() else {}
    chapter = settings.get("chapter")
    return {
        "title": book_title(read("pitch.md")),
        "pages": pages,
        "chapter": chapter,
        "lettering": settings.get("lettering", "art"),
        "style": section(read("brief.md"), "visual", "style", "look"),
        "bible": read("bible.md"),
        "script": read("script.md"),
        "trim": f"{w_in:g} x {h_in:g} inches",
    }


def build(slug, version=None):
    """({page: prompt}, book markdown) from the working copy or a round."""
    specs, errors = thumbnails.parse_layouts(projects.read_artifact(slug, "layouts.md", version))
    ctx = context(slug, version)
    pages = {s["page"]: page_prompt(s, ctx) for s in specs}
    head = [f"# Page prompts — {ctx['title']}", "", HOW_TO_USE, ""]
    if errors:
        head += ["**Layout errors (these pages are missing):**", ""] + [f"- {e}" for e in errors] + [""]
    if not pages:
        head.append("_No page layouts yet — run the room first._")
    book = "\n".join(head) + "\n" + "\n---\n\n".join(pages[n] for n in sorted(pages))
    return pages, book
