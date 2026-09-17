"""The ASCII Artist, one panel at a time.

A whole 116 x 82 page in one reply is too much for most models: they lose track of
columns, repeat themselves, or give up after a few shapes. So each panel is drawn
separately, on a canvas cropped to the panel, with numbered rows:

    1. crop the panel from the skeleton (lettering in place, silhouettes marking
       where the characters stand) and number its rows
    2. ask for the finished canvas, with the panel's description, cast, looks,
       script, the showrunner's taste and example panels
    3. check it in code: row count and width, repeated rows, blank or untouched
       canvas, leftover silhouettes, and ink density; on a problem, say what was
       wrong and ask again
    4. optionally one "look at it as a reader and improve it" pass
    5. paste the panels into the page; the frame and lettering go back on top

Panels are drawn in parallel.
"""
import re
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from . import asciitext, llm, projects, review, thumbnails

ROW_RE = re.compile(r"^\s*(\d{1,3})\s*\|(.*)$")
FILLS = set(thumbnails.FILLS)

PANEL_HOW = """# How to work

You draw one comic panel at a time as ASCII art, on a canvas cropped to the panel.

- The canvas has numbered rows: `07|...|`. Reply with the finished canvas in ONE ```text
  block: the same row numbers, every row exactly the canvas width between the bars.
- Text already on the canvas is lettering (balloons, captions, sound effects). Leave those
  cells exactly as they are and keep the drawing clear of them.
- Blocks of `% # @ & $` are placeholders showing where each character stands and how big they
  are. Replace every one with the actual character, drawn: head, face, hair, body, clothes,
  hands, pose — at that position and size.
- Fill the panel. A finished panel has a readable setting (ground, walls, sky, furniture,
  props), texture (brick, wood grain, foliage, water, fabric folds) and shading, not just an
  outline or two. Aim for a third to two thirds of the cells inked; leave air around the
  lettering and let empty space mean something (sky, light, silence).
- Draw only with art characters: `_ | / \\ ( ) [ ] { } < > = + * # % @ ~ ^ & $ \\``.
  Letters, digits and `. , ! ? ' " - : ;` are reserved for lettering.
- A cell is about twice as tall as it is wide: a round head is about twice as many
  columns as rows.
- The canvas is the inside of the panel: the border is already there, so don't draw a frame
  around the edge.
- Keep any planning short: the drawing is what counts.
"""


def ruler(width):
    tens = "".join(str(i // 10 % 10) if i % 10 == 0 else " " for i in range(width))
    ones = "".join(str(i % 10) for i in range(width))
    return f"   {tens}\n   {ones}"


def canvas_text(rows):
    return "\n".join(f"{i + 1:02d}|{r}|" for i, r in enumerate(rows))


def crop(lines, panel):
    x0, y0, x1, y1 = panel.inner
    return [lines[y][x0:x1 + 1] for y in range(y0, y1 + 1)]


def parse_canvas(text, width, height):
    """Numbered rows back into a height x width block. Returns (rows, info)."""
    blocks = re.findall(r"```([a-z]*)\n(.*?)```", text, re.S)
    body = max((b for tag, b in blocks if tag != "invert"), key=len, default=text)
    rows = [" " * width] * height
    numbered = total = 0
    widths_off = 0
    seen = []
    for line in body.split("\n"):
        if not line.strip():
            continue
        total += 1
        m = ROW_RE.match(line)
        if not m:
            continue
        numbered += 1
        n, content = int(m.group(1)), m.group(2)
        if content.endswith("|") and len(content) >= width + 1:
            content = content[:-1]
        if abs(len(content) - width) > 2:
            widths_off += 1
        content = content.expandtabs(4)[:width].ljust(width)
        seen.append(content)
        if 1 <= n <= height:
            rows[n - 1] = content
    return rows, {"lines": total, "numbered": numbered, "widths_off": widths_off, "rows": seen}


def problems(rows, info, start, keep, width, height, min_density):
    """What's wrong with a drawn panel, in words the model can act on."""
    out = []
    if info["numbered"] == 0:
        return [f"no numbered rows came back — reply with the canvas: rows `01|` to `{height:02d}|`"]
    if info["numbered"] > height * 1.3 + 2:
        out.append(f"you returned {info['numbered']} rows; the canvas has exactly {height}")
    elif info["numbered"] < height * 0.8:
        out.append(f"you returned only {info['numbered']} of {height} rows")
    if info["widths_off"] > max(2, height * 0.25):
        out.append(f"{info['widths_off']} rows were more than 2 characters off the {width}-character width")
    repeats = Counter(r for r in info["rows"] if r.strip())
    if repeats:
        row, count = repeats.most_common(1)[0]
        if count > max(4, height * 0.35):
            out.append(f"the same row is repeated {count} times — draw the scene, don't repeat a pattern")
    if rows == start:
        out.append("the canvas came back unchanged")
    blobs = sum(1 for y, r in enumerate(start) for x, c in enumerate(r)
                if c in FILLS and rows[y][x] == c)
    total_blobs = sum(1 for r in start for c in r if c in FILLS)
    if total_blobs and blobs / total_blobs > 0.6:
        out.append("the character placeholders are still blocks — draw the actual characters there")
    free = sum(1 for y in range(height) for x in range(width) if (x, y) not in keep)
    inked = sum(1 for y in range(height) for x in range(width)
                if (x, y) not in keep and rows[y][x] != " ")
    density = inked / free if free else 1
    if density < min_density:
        out.append(f"too sparse: only {density:.1%} of the free cells are inked — add the setting, "
                   f"props, texture and shading (aim for at least {min_density:.0%})")
    return out


def loved_examples(slug, limit=2, max_width=60):
    """Crops of panels from pages the showrunner loved: the best style guide there is."""
    found = []
    for n, lock in sorted(review.locks(slug).items()):
        if lock.get("verdict") != "love" or not lock.get("layout"):
            continue
        page = thumbnails.render_page(lock["layout"])
        lines = lock["ascii"].split("\n")
        for p in page.panels:
            w, h = p.size
            if w <= max_width and h >= 8:
                found.append((f"page {n}, panel {p.n}", crop(lines, p)))
                break
        if len(found) >= limit:
            break
    return found


class PanelArtist:
    def __init__(self, agent, page, script, bible, taste, system, note):
        self.a = agent
        self.page = page
        self.script = script
        self.bible = bible
        self.taste = taste
        self.system = system
        self.note = note
        cfg = agent.cfg
        self.min_density = cfg.min_density if cfg.min_density is not None else 0.25
        self.retries = 2
        self.refine = cfg.refine_passes if cfg.refine_passes is not None else 1
        # panels where the model used the whole budget and drew nothing — counted across the run
        if not hasattr(agent, "silent_panels"):
            agent.silent_panels = 0
            agent.silent_lock = threading.Lock()

    def give_up(self):
        return self.a.silent_panels >= 2

    def brief(self, panel, start, inverted):
        s = panel.spec
        w, h = panel.size
        shot = " / ".join(b.upper() for b in (s.get("shot"), s.get("angle")) if b) or "unspecified"
        cast = self.page.cast.get(panel.n, [])
        labels = [c.split(" ", 1)[1] for c in cast if not c.startswith("[=]")]
        parts = [
            f"Page {self.page.number} ({self.page.side}), panel {panel.n} of {len(self.page.panels)}. Shot: {shot}.",
            f"What happens: {s.get('description') or '(no description — draw what the script implies)'}",
            ("In this panel (placeholder -> who): " + ", ".join(cast)) if cast else "No placeholders in this panel.",
        ]
        looks = thumbnails.looks_for(self.bible, labels)
        if looks:
            parts.append(f"How they look (from the bible): {looks}")
        section = thumbnails.script_for_page(self.script, self.page.number)
        if section:
            parts.append(f"The script for this page:\n{section[:3000]}")
        if inverted:
            parts.append("This panel is shown inverted — light on dark. Draw the light things (lamps, "
                         "windows, faces, rim light); empty cells read as darkness.")
        if self.note:
            parts.append(f"Showrunner's note: {self.note}")
        parts.append(f"# Canvas — {w} columns x {h} rows\n```text\n{ruler(w)}\n{canvas_text(start)}\n```\n"
                     f"Reply with the finished canvas: rows 01-{h:02d}, each exactly {w} characters between the bars.")
        return "\n\n".join(parts)

    def call(self, messages, w, h, full=False):
        """The drawing needs about one token per 1.4 cells; reasoning models also think
        first, inside the same budget, so leave them room."""
        cfg = self.a.cfg
        cap = cfg.max_tokens or 16000
        limit = cap if full else min(cap, int(w * h / 1.4) + 900 + 4000)
        return llm.chat(_with_max_tokens(cfg, limit), messages, log=self.a.log)

    def draw(self, panel):
        """Returns (rows or None, notes). A failed model call costs only this panel."""
        try:
            return self._draw(panel)
        except llm.LLMError as e:
            self.a.emit("warn", text=f"page {self.page.number} panel {panel.n}: {e}")
            return None, [f"P{panel.n}: model call failed — kept the layout's placeholders ({str(e)[:120]})"]

    def _draw(self, panel):
        lines = thumbnails.compose(self.page).split("\n")
        start = crop(lines, panel)
        w, h = panel.size
        x0, y0, _, _ = panel.inner
        keep = {(x - x0, y - y0) for y, row in enumerate(self.page.letters) for x, c in enumerate(row)
                if c is not None and x0 <= x < x0 + w and y0 <= y < y0 + h}
        inv_cells = sum(1 for y in range(y0, y0 + h) for x in range(x0, x0 + w) if self.page.invert[y][x])
        messages = [{"role": "system", "content": self.system},
                    {"role": "user", "content": self.brief(panel, start, inv_cells > w * h / 2)}]
        notes, best, full = [], None, False
        for attempt in range(1 + self.retries):
            if self.a.should_stop():
                return best, notes
            if self.give_up():
                notes.append(f"P{panel.n}: skipped — the model drew nothing on two panels even with the "
                             "whole token budget (it thinks too long: set a thinking budget, or use another model)")
                return best, notes
            message = self.call(messages, w, h, full)
            reply = llm.text_of(message)
            rows, info = parse_canvas(reply, w, h)
            issues = problems(rows, info, start, keep, w, h, self.min_density)
            if message.get("finish_reason") == "length" and info["numbered"] == 0 and full:
                with self.a.silent_lock:
                    self.a.silent_panels += 1
                notes.append(f"P{panel.n}: the model used the whole token budget without drawing — stopped")
                return best, notes
            if message.get("finish_reason") == "length" and info["numbered"] < h:
                full = True   # give the retry the whole budget
                issues = [f"you ran out of room before finishing the canvas ({info['numbered']} of {h} rows) — "
                          "keep planning to a minimum and output the drawing"] + issues[1:]
            if not issues:
                best = rows
                break
            notes.append(f"P{panel.n} try {attempt + 1}: " + "; ".join(issues))
            if info["numbered"] and info["numbered"] <= h * 1.3 + 2 and best is None:
                best = rows          # imperfect but usable, if nothing better comes
            messages += [{"role": "assistant", "content": reply[:6000]},
                         {"role": "user", "content": "Problems with that panel:\n- " + "\n- ".join(issues)
                          + f"\n\nRedraw the whole canvas: rows 01-{h:02d}, each exactly {w} characters between the bars."}]
        else:
            if best is None:
                notes.append(f"P{panel.n}: no usable drawing — kept the layout's placeholders")
                return None, notes
        for _ in range(self.refine if not issues else 0):
            messages += [{"role": "assistant", "content": f"```text\n{canvas_text(best)}\n```"},
                         {"role": "user", "content": (
                             "Now look at that panel as a reader who hasn't seen the script. Does each "
                             "character read (head, face, body, pose)? Does the setting read? Is the action "
                             "clear, and is there enough detail and texture? Improve it — stronger shapes, "
                             "more detail, clearer staging — and return the full canvas again, same rows and width.")}]
            reply = llm.text_of(self.call(messages, w, h, True))
            rows, info = parse_canvas(reply, w, h)
            if not problems(rows, info, start, keep, w, h, self.min_density):
                best = rows
                notes.append(f"P{panel.n}: refined")
        return best, notes


def _with_max_tokens(cfg, limit):
    import dataclasses
    return dataclasses.replace(cfg, max_tokens=limit)


def draw_page(agent, page, script, bible, guides, figma_text, note, hat):
    """Draw every panel of a page. Returns (art grid, notes)."""
    taste = projects.read_artifact(agent.slug, "taste-writers.md") or ""
    system = agent.system_prompt(guides, figma_text, False, hat)
    examples = loved_examples(agent.slug)
    if examples:
        system += "\n\n# Panels the showrunner loved — match this level of finish\n" + "\n\n".join(
            f"{label}:\n```text\n" + "\n".join(rows) + "\n```" for label, rows in examples)
    if taste:
        system += f"\n\n# The showrunner's taste (taste-writers.md)\n{taste}"
    artist = PanelArtist(agent, page, script, bible, taste, system, note)
    art = [row[:] for row in page.art]
    notes = []
    workers = max(1, min(agent.cfg.parallel or 3, len(page.panels)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(artist.draw, page.panels))
    for panel, (rows, panel_notes) in zip(page.panels, results):
        notes += panel_notes
        if rows is None:
            continue
        x0, y0, _, _ = panel.inner
        for j, row in enumerate(rows):
            art[y0 + j][x0:x0 + len(row)] = list(row)
    lettering = {(x, y) for y, row in enumerate(page.letters) for x, c in enumerate(row) if c is not None}
    stray = asciitext.art_violations(art, lettering)
    for x, y, c in stray:
        art[y][x] = asciitext.art_char(c)
    if stray:
        notes.append(f"{len(stray)} text characters used as art were swapped for art characters")
    return art, notes
