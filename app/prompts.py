"""Page packets — the writers' room's deliverable.

For every page, one self-contained markdown packet to paste into an image model
(outside the room) to draw the finished comic page. Assembled in code, not by a
model, so it always matches the room's files and the character descriptions go in
word for word (a model would paraphrase them and the characters would drift):

    format        trim, orientation, left/right page
    style         the brief's visual direction (the same on every page)
    characters    characters.md's description of everyone on the page, verbatim
    layout        a box map of the page drawn to scale, then rows and panels with their share
    sketch        the layout drawn at print scale (one cell = one letter), balloons boxed
    panels        shot, angle, light, what happens, who is where, the clear space for lettering
    rules         no text on the page (the lettering is a layer, added afterwards)
    checklist     what to look for before accepting the image
    script        the page's script, for reference

And one book packet in front of them: how to use the packets, the rules that hold for every
page, a character sheet prompt to draw first, and a page index.
"""
import json
import re

from . import projects, thumbnails, keypages
from .config import env

DEFAULTS = {"lettering": "layer"}   # the same default as review.DEFAULT_SETTINGS (review imports this module)

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
HOW_TO_USE = """## How to use these packets

1. **Start with the sheets** below: the character sheet, then the location sheet. Paste each,
   keep the results, and attach them as reference images with every page that names them
   (each page packet says which). Approve one page as your style page and attach that too.
   For a long book, train a LoRA on the approved sheets and pages; references alone drift.
2. **One page at a time.** Paste everything under a page's heading, nothing else. Keep the
   same model and settings for the whole book so the style and the characters stay put.
3. **No text on the pages.** The words are added afterwards, in the room, as a layer over
   your art - so a beautiful model that cannot spell is fine. If the model draws any letters,
   regenerate; do not keep a page with text on it.
4. **Check the page** against its checklist before you keep it. One thing wrong: regenerate
   with the same packet, and only then adjust wording.
5. **Upload each kept page** in the room (Production, Lettering tab) and run the lettering:
   the room draws every balloon and caption where the layout put them, and you download the
   finished, lettered page.

## Rules for every page

- Never render text of any kind: no balloons, captions, sound effects, page numbers,
  titles, chapter names, signatures, watermarks, nameplates or labels.
- Keep the areas each panel lists as clear: uncluttered art (sky, wall, shadow) where a
  balloon will sit, never a face or the thing the panel is about.
- Draw every character exactly as described, every time. The description wins over the
  previous page's picture.
- Panel count, panel shape and reading order are fixed by the map. Do not add, merge or
  reshape panels."""

PAGE_HEAD = "_Copy everything under this heading and paste it into the image model._"


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


def book_title(pitch, slug=""):
    m = re.search(r"^#\s+(.+)$", pitch or "", re.M)
    return m.group(1).strip() if m else slug.replace("-", " ").title() or "Untitled"


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


def page_cast(spec, ctx):
    """(names, places, described): who and where a page draws - the people its items name and
    the ones its panels describe, and the places its panels are set in."""
    items = spec.get("items") or []
    panel_specs = [p for t in spec.get("tiers") or [] for p in (t.get("panels") or [{}])]
    names = []
    for i in items:
        for name in (i.get("label") if i.get("type") == "figure" else None, i.get("speaker")):
            if name and name.upper() not in [n.upper() for n in names]:
                names.append(name)
    # Whoever the panels describe but nobody names: a page where Alex works in silence still
    # has to carry his visual lock, or the artist draws a different boy every page.
    described = " ".join(str(p.get("description") or "") for p in panel_specs)
    for name in named_in(ctx["bible"], described):
        if name.upper() not in [n.upper() for n in names]:
            names.append(name)
    return names, places_on(ctx, described), described


def page_prompt(spec, ctx):
    """One page's prompt. In "layer" mode the art is drawn with no text at all and the
    lettering is rendered separately (see lettering.py)."""
    number = spec.get("page", 0)
    side = spec.get("side") or ("right" if number % 2 else "left")
    panel_specs = [p for t in spec.get("tiers") or [] for p in (t.get("panels") or [{}])]
    items = spec.get("items") or []
    names, places, described = page_cast(spec, ctx)
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
    layer = ctx.get("lettering") == "layer"
    if layer:                    # the art is drawn with no text: say so where the model reads first
        out[2] = out[2].replace(", and professional comic lettering.", ". NO TEXT anywhere on the page.")
    out.insert(1, PAGE_HEAD)
    if names:
        out += ["", "**Characters — draw them exactly as described:**", ""]
        for name in names:
            look = clean_look(looks_for(ctx["bible"], [name]))
            out.append(f"- **{name.upper()}** — {look or '(no description in the bible yet)'}")
    out += ["", reference_line(names, places, ctx)]
    if not layer:
        out += ["", f"**Page number:** in the top-left corner of the page, in small light-blue lettering: \"{label}\"."]
    out += ["", "**Page layout, top to bottom** (the map is the page itself, panels to scale):", "",
            *panel_map(spec), "", *layout_lines(spec), ""]
    sketch = (ctx.get("sketches") or {}).get(number)
    if sketch:
        fence = "`" * 3
        out += ["**Layout sketch at print scale** (one character cell is one letter of lettering; "
                "figures are the shaded shapes, and the boxed words are where balloons and captions "
                "will go" + (" - keep those areas clear" if layer else "") + "):", "",
                fence + "text", sketch.rstrip("\n"), fence, ""]
    by_panel = {}
    for item in items:
        by_panel.setdefault(item.get("panel"), []).append(item)
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
        out += ["", *checklist(spec, panel_specs, by_panel, names, side)]
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


def checklist(spec, panel_specs, by_panel, names, side):
    """What to look at before the image is kept: the count, each panel's one thing, the
    people, the clear space, and no text. Written for the showrunner, not the model."""
    lines = ["**Before you keep this image, check:**", "",
             f"- [ ] {len(panel_specs)} panels, shaped and ordered as the map shows; a {side}-hand page"]
    for n, p in enumerate(panel_specs, 1):
        gist = " ".join(str(p.get("description") or "").split())
        gist = re.split(r"(?<=[.;!?])\s", gist, 1)[0][:110].rstrip(".;, ")
        if gist:
            lines.append(f"- [ ] Panel {n}: {gist}")
    if names:
        lines.append(f"- [ ] {', '.join(n.upper() for n in names)}: as described, same as the other pages")
    clear = []
    for n in range(1, len(panel_specs) + 1):
        spots = [where(i) for i in by_panel.get(n, []) if i.get("type") in KIND or i.get("type") == "sfx"]
        if spots:
            clear.append(f"panel {n} {', '.join(dict.fromkeys(spots))}")
    if clear:
        lines.append(f"- [ ] Clear, uncluttered space at: {'; '.join(clear)}")
    lines += ["- [ ] No letters, numbers, balloons, captions, signatures or watermarks anywhere",
              "", "_One box fails: regenerate with the same packet. Then upload the page in the room and letter it._"]
    return lines


# ---- who is on the page: characters.md -----------------------------------

def character_entries(bible):
    """The character headings in characters.md: "### ALEX PHANTUM" under a "## Characters" section,
    or "## Alex Phantum" straight under a "# Characters" title — agents write both.

    Used to find who is on a page when nobody names them — a panel description says Alex is
    waist-deep in a maintenance pit, and the artist still needs his visual lock."""
    people = re.compile(r"\bcharacters?\b|\bcast\b|\bensemble\b", re.I)
    not_a_name = re.compile(r"\btest\b|^open\b|\bwants?\b|\bnotes?\b", re.I)
    names, in_people, file_is_people = [], False, False
    for line in (bible or "").split("\n"):
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if not m:
            continue
        depth, head = len(m.group(1)), m.group(2).strip().rstrip("*").strip()
        is_name = 1 <= len(head.split()) <= 4 and not head.endswith(":") and not not_a_name.search(head)
        if depth == 1:
            file_is_people = in_people = bool(people.search(head)) and not not_a_name.search(head)
        elif depth == 2 and (people.search(head) or not file_is_people or not is_name):
            in_people = bool(people.search(head)) and not not_a_name.search(head)
        elif in_people and is_name:
            names.append(head)
    return names


ARTICLES = {"the", "a", "an", "old", "young", "mr", "mrs", "ms", "dr"}


def named_in(bible, text):
    """Bible characters a passage mentions, by full name or by the name they go by."""
    found = []
    for name in character_entries(bible):
        words = name.split()
        first = words[0]
        if first.lower() in ARTICLES and len(words) > 1:    # "The Founder": the whole name, or nothing
            if re.search(rf"\b{re.escape(name)}\b", text or "", re.I):
                found.append(name)
            continue
        if re.search(rf"\b{re.escape(first)}\b", text or "", re.I):
            found.append(first.title() if not first.isupper() or len(first) > 6 else first)
    return found


def looks_for(bible, labels):
    """The bible's description of each label, verbatim, so image prompts stay on model.

    A character's own entry wins over any other entry that merely mentions them: the bible says
    "Ada, who challenges his lone-wolf independence" inside Alex's entry, and matching on the
    name alone handed Ada his description — and every page prompt drew two of him."""
    entries = []            # (heading, body) for each "### Name" block, in order
    heading, buf = "", []
    for line in (bible or "").split("\n"):
        if re.match(r"^#{1,6}\s", line):
            if buf:
                entries.append((heading, "\n".join(buf).strip()))
            heading, buf = re.sub(r"^#+\s*", "", line).strip(), []
        else:
            buf.append(line)
    if buf:
        entries.append((heading, "\n".join(buf).strip()))

    found = []
    for label in dict.fromkeys(labels):
        word = re.compile(rf"\b{re.escape(label)}\b", re.I)
        own = [body for head, body in entries if word.search(head) and body]
        if not own:         # no entry of their own: fall back to whoever describes them
            paras = [p.strip() for p in re.split(r"\n\s*\n", bible or "") if p.strip()]
            hits = [p for p in paras if word.search(p)]
            own = [next((p for p in hits if "visual" in p.lower()), hits[0])] if hits else []
        if own:
            best = next((b for b in own if "visual" in b.lower()), own[0])
            found.append(best[:500])
    return " ".join(found)


def context(slug, version=None):
    read = lambda name: projects.read_artifact(slug, name, version) or ""
    w_in, h_in = (float(v) for v in (env("PAGE_TRIM") or "6.625x10.25").lower().split("x"))
    settings_file = projects.project_dir(slug) / "round-settings.json"
    settings = json.loads(settings_file.read_text()) if settings_file.exists() else {}
    settings = {**DEFAULTS, **settings}
    chapter = settings.get("chapter")
    return {
        "keypages": [k["book"] for k in keypages.pages(slug) if k["art"]],
        "keypage_notes": keypages.exceptions(slug),
        "title": book_title(projects.pitch(slug), slug),
        "pages": settings.get("pages"),
        "chapter": chapter,
        "lettering": settings.get("lettering") or "layer",
        "style": section(read("brief.md"), "visual", "style", "look"),
        "bible": read("characters.md"),
        "world": read("world.md"),
        "script": read("script.md"),
        "trim": f"{w_in:g} x {h_in:g} inches",
        "sketches": {n: p["art"] for n, p in thumbnails.parse_thumbnails(read("thumbnails.md")).items()},
    }


def character_sheet(ctx):
    """A prompt for one reference image of the whole cast, to draw before any page."""
    entries = character_entries(ctx["bible"])
    if not entries:
        return None
    out = ["## Character sheet — draw this first", "", PAGE_HEAD, "",
           "Draw one character reference sheet: every character below standing full length in a "
           "row, front view, neutral pose, even daylight, plain light background, in the book's "
           "style. Same scale for everyone so heights compare. No text, names, labels or captions "
           "anywhere on the sheet.", "",
           "**Style:**", "", ctx["style"] or "(no visual direction in the brief yet)", "",
           "**Characters — draw them exactly as described:**", ""]
    for name in entries:
        look = clean_look(looks_for(ctx["bible"], [name]))
        if look:
            out.append(f"- **{name.upper()}** — {look}")
    return "\n".join(out)


PLACES = re.compile(r"\bsetting|\bplaces?\b|\blocations?\b|\benvironment|\bgeograph", re.I)


def location_entries(world):
    """The places in world.md: the "###" headings under its setting / places / locations
    section, each with the first paragraph of its description."""
    out, inside, name, body = [], False, None, []
    def close():
        if name:
            text = " ".join(" ".join(body).split())
            out.append((name, text[:420].rsplit(".", 1)[0] + "." if "." in text[:420] else text[:420]))
    for line in (world or "").split("\n"):
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            depth, head = len(m.group(1)), m.group(2).strip().rstrip("*").strip()
            if depth <= 2:
                close(); name, body = None, []
                inside = bool(PLACES.search(head))
            elif depth == 3:
                close(); name, body = None, []
                if inside and 1 <= len(head.split()) <= 5 and not re.search(r"travel|access|distance", head, re.I):
                    name = head
            continue
        if name and line.strip() and not body and not line.lstrip().startswith(("-", "*", "|")):
            body.append(line.strip())
        elif name and body and line.strip() and not line.lstrip().startswith(("-", "*", "|")):
            if len(" ".join(body)) < 420:
                body.append(line.strip())
    close()
    return out


def location_sheet(ctx):
    """A prompt for one reference image per place, to draw before the pages."""
    places = location_entries(ctx.get("world"))
    if not places:
        return None
    out = ["## Location sheet — draw this next", "", PAGE_HEAD, "",
           "Draw one establishing view of each place below, in the book's style, as separate images "
           "or one sheet: wide shot, daylight unless the description says otherwise, no people in "
           "the foreground. No text, names, labels or captions anywhere.", "",
           "**Style:**", "", ctx["style"] or "(no visual direction in the brief yet)", "",
           "**Places — draw them exactly as described:**", ""]
    for name, look in places:
        out.append(f"- **{name.upper()}** — {look or '(no description yet)'}")
    return "\n".join(out)


def places_on(ctx, text):
    """Which of the world's places a page's descriptions name."""
    found = []
    for name, _ in location_entries(ctx.get("world")):
        key = name.split()[-1] if name.split()[0].lower() in ARTICLES else name.split()[0]
        if len(key) > 3 and re.search(rf"\b{re.escape(key)}\b", text or "", re.I):
            found.append(name)
    return found


def reference_line(names, places, ctx):
    """What to attach to this page, for a model that takes reference images."""
    bits = []
    if names:
        bits.append(f"the character sheet ({', '.join(n.upper() for n in names)})")
    if places:
        bits.append(f"the location sheet ({', '.join(p.upper() for p in places)})")
    bits.append("the key pages (keypages/ in the packet) as the book's style reference"
                + (f" - for style only where they differ from the descriptions: {ctx['keypage_notes']}" if ctx.get("keypage_notes") else "")
                if ctx.get("keypages") else "your approved style page")
    return ("**Reference images to attach** (if the model takes them): " + "; ".join(bits)
            + ". The descriptions below still win where the two differ.")


def page_index(specs, ctx):
    """Page | panels | who is on it | where the lettering goes - the book at a glance."""
    rows = ["| Page | Panels | On the page | Clear space for lettering |", "|---|---|---|---|"]
    for s in specs:
        items = s.get("items") or []
        panels = [p for t in s.get("tiers") or [] for p in (t.get("panels") or [{}])]
        who = []
        for i in items:
            name = i.get("label") if i.get("type") == "figure" else i.get("speaker")
            if name and name.upper() not in who:
                who.append(name.upper())
        spots = {}
        for i in items:
            if i.get("type") in KIND or i.get("type") == "sfx":
                spots.setdefault(i.get("panel"), []).append(where(i))
        clear = "; ".join(f"p{n} {', '.join(dict.fromkeys(v))}" for n, v in sorted(spots.items(), key=lambda kv: kv[0] or 0))
        rows.append(f"| {s.get('page', 0)} | {len(panels)} | {', '.join(who) or '—'} | {clear or '—'} |")
    return "\n".join(rows)


def build(slug, version=None):
    """({page: prompt}, book markdown) from the working copy or a round."""
    specs, errors = thumbnails.parse_layouts(projects.read_artifact(slug, "layouts.md", version))
    ctx = context(slug, version)
    pages = {s["page"]: page_prompt(s, ctx) for s in specs}
    n = len(pages)
    head = [f"# Page packets — {ctx['title']}", "",
            f"{n} page{'s' if n != 1 else ''}, {ctx['trim']}" + (f", chapter {ctx['chapter']}" if ctx.get("chapter") else "")
            + ". Made by the writers' room; every packet below is complete on its own.", "", HOW_TO_USE, ""]
    if errors:
        head += ["**Layout errors (these pages are missing):**", ""] + [f"- {e}" for e in errors] + [""]
    if not pages:
        head.append("_No page layouts yet — run the room first._")
    else:
        for sheet in (character_sheet(ctx), location_sheet(ctx)):
            if sheet:
                head += [sheet, ""]
        head += ["## The pages at a glance", "", page_index(sorted(specs, key=lambda s: s["page"]), ctx), ""]
    book = "\n".join(head) + "\n---\n\n" + "\n---\n\n".join(pages[n] for n in sorted(pages))
    return pages, book


def book_packet(slug, version=None):
    """The book packet alone: how to use, the rules, the character sheet, the index."""
    _, book = build(slug, version)
    return book.split("\n---\n\n", 1)[0]
