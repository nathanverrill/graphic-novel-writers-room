"""The ASCII page character rule, and page diffs built on it.

Text characters — letters, digits and simple punctuation (. , ! ? ' " - : ;) — are
used only for text: dialogue, captions, sound effects, signs. Every other printable
character is art. Because the two never mix, a page splits cleanly into a text
layer and an art layer, and a diff of two pages is a dialogue diff plus an art diff.
"""
import difflib

TEXT_PUNCT = set(".,!?'\"-:;")

# what a text character becomes when it turns up in art (model-drawn pages)
ART_FOR = {".": "_", ",": "_", "'": "`", '"': "^", "-": "=", ":": "|", ";": "|", "!": "|", "?": "^",
           "o": "@", "O": "@", "0": "@", "l": "|", "I": "|", "1": "|", "i": "|", "j": "|",
           "v": "^", "V": "^", "x": "*", "X": "*"}


def is_text(c):
    return c.isascii() and (c.isalnum() or c in TEXT_PUNCT)


def art_char(c):
    return ART_FOR.get(c, "#") if is_text(c) else c


def sanitize(text):
    """Replace text characters with art characters (for art-only strings)."""
    return "".join(art_char(c) for c in text)


def lines_of(page):
    return page.split("\n") if isinstance(page, str) else ["".join(r) for r in page]


# ---- text layer ----------------------------------------------------------------

def text_blocks(page):
    """Runs of text on each row (single spaces allowed inside a run), merged down
    the page into blocks — one per balloon, caption or sign."""
    runs = []
    for y, line in enumerate(lines_of(page)):
        x, n = 0, len(line)
        while x < n:
            if not is_text(line[x]):
                x += 1
                continue
            start = x
            while x < n and (is_text(line[x]) or (line[x] == " " and x + 1 < n and is_text(line[x + 1]))):
                x += 1
            runs.append((y, start, x - 1, line[start:x]))
    blocks = []
    for y, x0, x1, text in runs:
        for b in blocks:
            if b["y1"] == y - 1 and x0 <= b["x1"] + 2 and x1 >= b["x0"] - 2:
                b.update(text=b["text"] + " " + text, y1=y, x0=min(b["x0"], x0), x1=max(b["x1"], x1))
                break
        else:
            blocks.append({"text": text, "y0": y, "y1": y, "x0": x0, "x1": x1})
    return blocks


def _overlap(a, b):
    return not (a["x1"] < b["x0"] or b["x1"] < a["x0"] or a["y1"] < b["y0"] or b["y1"] < a["y0"])


def text_diff(before, after):
    """[{kind: changed|moved|added|removed, before, after, at}]"""
    old, new = text_blocks(before), text_blocks(after)
    used, out = set(), []
    for b in new:
        match = next((i for i, a in enumerate(old) if i not in used and _overlap(a, b)), None)
        if match is None:
            match = max((i for i in range(len(old)) if i not in used),
                        key=lambda i: difflib.SequenceMatcher(None, old[i]["text"], b["text"]).ratio(),
                        default=None)
            if match is not None and difflib.SequenceMatcher(None, old[match]["text"], b["text"]).ratio() < 0.6:
                match = None
        if match is None:
            out.append({"kind": "added", "before": None, "after": b["text"], "at": _at(b)})
            continue
        used.add(match)
        a = old[match]
        if a["text"] != b["text"]:
            out.append({"kind": "changed", "before": a["text"], "after": b["text"], "at": _at(b)})
        elif abs(a["y0"] - b["y0"]) + abs(a["x0"] - b["x0"]) > 2:
            out.append({"kind": "moved", "before": a["text"], "after": b["text"],
                        "at": f"{_at(a)} → {_at(b)}"})
    for i, a in enumerate(old):
        if i not in used:
            out.append({"kind": "removed", "before": a["text"], "after": None, "at": _at(a)})
    return out


def _at(b):
    return f"row {b['y0'] + 1}, col {b['x0'] + 1}"


def text_similarity(before, after):
    a = " ".join(b["text"] for b in text_blocks(before))
    b = " ".join(b["text"] for b in text_blocks(after))
    return 1.0 if a == b else round(difflib.SequenceMatcher(None, a, b).ratio(), 3)


# ---- art layer -----------------------------------------------------------------

def art_grid(page):
    return [[" " if is_text(c) else c for c in line] for line in lines_of(page)]


def art_similarity(before, after):
    """Share of non-blank art cells that are identical."""
    a, b = art_grid(before), art_grid(after)
    same = total = 0
    for y in range(max(len(a), len(b))):
        ra = a[y] if y < len(a) else []
        rb = b[y] if y < len(b) else []
        for x in range(max(len(ra), len(rb))):
            ca = ra[x] if x < len(ra) else " "
            cb = rb[x] if x < len(rb) else " "
            if ca == " " and cb == " ":
                continue
            total += 1
            same += ca == cb
    return 1.0 if total == 0 else round(same / total, 3)


def art_regions(before, after, tile=(12, 6), crop_limit=(60, 20)):
    """Areas where the art changed: changed cells grouped into connected tiles."""
    a, b = art_grid(before), art_grid(after)
    rows = max(len(a), len(b))
    cols = max((len(r) for r in a + b), default=0)
    get = lambda g, x, y: g[y][x] if y < len(g) and x < len(g[y]) else " "
    tw, th = tile
    hot = {}
    for y in range(rows):
        for x in range(cols):
            if get(a, x, y) != get(b, x, y):
                hot[(x // tw, y // th)] = hot.get((x // tw, y // th), 0) + 1
    regions, seen = [], set()
    for start in hot:
        if start in seen:
            continue
        stack, group = [start], []
        seen.add(start)
        while stack:
            tx, ty = stack.pop()
            group.append((tx, ty))
            for nb in ((tx + 1, ty), (tx - 1, ty), (tx, ty + 1), (tx, ty - 1)):
                if nb in hot and nb not in seen:
                    seen.add(nb)
                    stack.append(nb)
        x0 = min(t[0] for t in group) * tw
        y0 = min(t[1] for t in group) * th
        x1 = min(cols, (max(t[0] for t in group) + 1) * tw) - 1
        y1 = min(rows, (max(t[1] for t in group) + 1) * th) - 1
        cw, ch = min(x1 - x0 + 1, crop_limit[0]), min(y1 - y0 + 1, crop_limit[1])
        crop = lambda g: "\n".join("".join(get(g, x, y) for x in range(x0, x0 + cw)).rstrip()
                                   for y in range(y0, y0 + ch))
        regions.append({"x0": x0, "y0": y0, "x1": x1, "y1": y1,
                        "cells": sum(hot[t] for t in group),
                        "before": crop(a), "after": crop(b)})
    regions.sort(key=lambda r: (r["y0"], r["x0"]))
    return regions


def page_diff(before, after, panels=()):
    """Everything a model needs to understand a hand edit to a page."""
    regions = art_regions(before, after)
    for r in regions:
        r["panel"] = next((p.n for p in panels
                           if p.x0 <= (r["x0"] + r["x1"]) // 2 <= p.x1 and p.y0 <= (r["y0"] + r["y1"]) // 2 <= p.y1), None)
    return {"text": text_diff(before, after), "art": regions,
            "text_similarity": text_similarity(before, after),
            "art_similarity": art_similarity(before, after)}


def diff_markdown(diff, max_regions=6):
    lines = [f"Text match {diff['text_similarity']:.0%} · art match {diff['art_similarity']:.0%}", ""]
    if diff["text"]:
        lines.append("Text changes:")
        for c in diff["text"]:
            if c["kind"] == "changed":
                lines.append(f"- {c['at']}: \"{c['before']}\" → \"{c['after']}\"")
            elif c["kind"] == "added":
                lines.append(f"- {c['at']}: added \"{c['after']}\"")
            elif c["kind"] == "removed":
                lines.append(f"- {c['at']}: removed \"{c['before']}\"")
            else:
                lines.append(f"- moved \"{c['after']}\": {c['at']}")
    else:
        lines.append("No text changes.")
    lines.append("")
    if diff["art"]:
        lines.append(f"Art changes ({len(diff['art'])} areas):")
        for r in diff["art"][:max_regions]:
            where = f"panel {r['panel']}, " if r.get("panel") else ""
            lines += [f"- {where}rows {r['y0'] + 1}-{r['y1'] + 1}, cols {r['x0'] + 1}-{r['x1'] + 1} ({r['cells']} cells)",
                      "  before:", "```text", r["before"], "```", "  after:", "```text", r["after"], "```"]
        if len(diff["art"]) > max_regions:
            lines.append(f"- … and {len(diff['art']) - max_regions} more areas")
    else:
        lines.append("No art changes.")
    return "\n".join(lines)


def art_violations(page, protected):
    """Text characters outside the protected (lettering) cells: [(x, y, char)]."""
    out = []
    for y, line in enumerate(lines_of(page)):
        for x, c in enumerate(line):
            if is_text(c) and (x, y) not in protected:
                out.append((x, y, c))
    return out
