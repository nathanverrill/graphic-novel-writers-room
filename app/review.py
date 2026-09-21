"""Human review rounds, page locks, the readiness gate, and page exports.

A review says one of two things about a page, and neither is a grade:

    kept     the page is done. Script, layout and sketch are locked and never change again.
    open     the room can work on it. Anything you say about it — a comment, an edit to the
             sketch — is feedback it works from; an edited page is locked as your version
             and the room brings script and layout into line with it.

A page you say nothing about is simply open: the room carries on with it.

Submitting creates a human round (or a final round) with your pages, per-page diffs
against the AI pages, and review.md — the instructions the next AI round works from.
Locks are enforced in code on every write (enforce_locks).
"""
import json
import re

from . import asciitext, lettering, notes, projects, prompts, thumbnails

DRAFT = "review-draft.json"
LOCKS = "locks.json"
SETTINGS = "round-settings.json"
KEPT, EDITED = "keep", "edited"        # the two kinds of lock a page can carry
OLD_KINDS = {"love": KEPT, "changes": EDITED}   # locks written before the verdicts went away
DEFAULT_SETTINGS = {"pages": None, "chapter": None, "lettering": "art", "max_passes": 2, "references": None,
                    "min_text_match": 0.95, "min_layout_match": 0.8, "auto_rounds": 0,
                    "use_references_during_synthesis": True,    # see app/intake.py, pass 1
                    "phase": "intake", "writer": None}      # where the book is: see phases.py


# ---- small json state files in the working copy ----------------------------------

def _load(slug, name, default):
    path = projects.project_dir(slug) / name
    return json.loads(path.read_text()) if path.exists() else default


def _save(slug, name, data):
    (projects.project_dir(slug) / name).write_text(json.dumps(data, indent=2))


def settings(slug):
    return {**DEFAULT_SETTINGS, **_load(slug, SETTINGS, {})}


def save_settings(slug, **changes):
    current = _load(slug, SETTINGS, {})
    current.update({k: v for k, v in changes.items() if v is not None})
    if changes.get("references") == ["*"]:   # back to "every library file"
        current.pop("references", None)
    _save(slug, SETTINGS, current)
    return settings(slug)


def locks(slug):
    out = {}
    for k, v in _load(slug, LOCKS, {}).items():
        kind = v.get("kind") or OLD_KINDS.get(v.get("verdict"), v.get("verdict"))
        out[int(k)] = {**v, "kind": kind}
    return out


def draft(slug):
    d = _load(slug, DRAFT, {})
    d["pages"] = {int(k): v for k, v in d.get("pages", {}).items()}
    return d


# ---- the pages under review --------------------------------------------------------

FILES = {"drawn": "thumbnails-drawn.md", "layout": "thumbnails.md"}


def canonical_file(slug):
    return FILES["layout"]


def canonical(slug):
    """(method, {page: parsed thumbnail}) — the page sketch the showrunner reviews: the
    ASCII layout render of the Layout Agent's layout."""
    name = canonical_file(slug)
    method = "drawn" if name == FILES["drawn"] else "layout"
    return method, thumbnails.parse_thumbnails(projects.read_artifact(slug, name))


def latest_round(slug, kind=None):
    for meta in projects.list_versions(slug):
        if kind is None or meta.get("kind", "ai") == kind:
            return meta
    return None


PAGE_COUNT_RE = re.compile(r"^\s*\**PAGE COUNT:?\**\s*(\d+)\s*[—:-]*\s*(.*)$", re.M | re.I)


def page_proposal(slug):
    """The room can ask for more or fewer pages by putting a line in notes.md:

        PAGE COUNT: 5 — the Leona reveal needs a page of its own

    It's only a proposal: the count doesn't change until the showrunner accepts it."""
    m = PAGE_COUNT_RE.search(projects.read_artifact(slug, "notes.md") or "")
    if not m:
        return None
    want = int(m.group(1))
    now = settings(slug)["pages"]
    if not want or want == now:
        return None
    return {"pages": want, "now": now, "reason": m.group(2).strip(),
            "direction": "expand" if now and want > now else "contract"}


def state(slug):
    """Everything the review screen needs."""
    method, pages = canonical(slug)
    d = draft(slug)
    last = latest_round(slug)
    lk = locks(slug)
    out = {}
    for n, p in sorted(pages.items()):
        entry = d["pages"].get(n, {})
        art = entry.get("art") or p["art"]
        invert = entry["invert"] if "invert" in entry else p["invert"]
        out[n] = {"ai_art": p["art"], "art": art, "ai_invert": p["invert"], "invert": invert,
                  "notes": p["notes"], "kept": bool(entry.get("kept")), "comment": entry.get("comment", ""),
                  "edited": art != p["art"] or _mask(invert) != _mask(p["invert"]),
                  "locked": lk.get(n, {}).get("kind")}
    open_for_review = bool(last and last.get("kind", "ai") == "ai" and last.get("status") == "done" and pages
                           and settings(slug)["phase"] == "execution")     # pages are reviewed in execution only
    g = thumbnails.geometry()
    return {"method": method, "pages": out, "round": last and last["id"],
            "open": open_for_review, "comment": d.get("comment", ""), "settings": settings(slug),
            "gate": last and last.get("gate"), "cols": g.cols, "rows": g.rows,
            "page_proposal": page_proposal(slug)}


def _mask(text):
    """Normalized inversion mask text, for comparing."""
    return thumbnails.mask_text(thumbnails.text_to_mask(text or "", thumbnails.geometry()))


def save_page(slug, n, kept=None, comment=None, art=None, invert=None):
    method, pages = canonical(slug)
    if n not in pages:
        raise KeyError(f"page {n}")
    d = draft(slug)
    entry = d["pages"].setdefault(n, {})
    if art is not None:
        grid, _ = thumbnails.text_to_grid(art.replace("`" * 3, "'" * 3), thumbnails.geometry())
        art = "\n".join("".join(r) for r in grid)
        if art == pages[n]["art"]:
            entry.pop("art", None)
        else:
            entry["art"] = art
    if invert is not None:
        invert = _mask(invert)
        if invert == _mask(pages[n]["invert"]):
            entry.pop("invert", None)
        else:
            entry["invert"] = invert
    if comment is not None:
        entry["comment"] = comment.strip()
    if kept is not None:
        entry["kept"] = bool(kept)
    _save(slug, DRAFT, {**d, "pages": {str(k): v for k, v in d["pages"].items()}})
    return entry


def save_comment(slug, comment):
    d = draft(slug)
    d["comment"] = comment.strip()
    _save(slug, DRAFT, {**d, "pages": {str(k): v for k, v in d["pages"].items()}})


# ---- script / layout sections --------------------------------------------------------

def _script_span(script, n):
    m = re.search(rf"^#+ *Page {n}\b.*?(?=^#+ *Page \d+\b|\Z)", script or "", re.S | re.M | re.I)
    return m


def replace_script_section(script, n, section):
    m = _script_span(script, n)
    if m:
        return script[:m.start()] + section.rstrip() + "\n\n" + script[m.end():].lstrip("\n")
    return (script or "").rstrip() + "\n\n" + section.rstrip() + "\n"


def layout_block(spec):
    return "```layout\n" + json.dumps(spec, indent=1) + "\n```"


def replace_layout(markdown, n, spec):
    for m in thumbnails.LAYOUT_RE.finditer(markdown or ""):
        try:
            page = int(json.loads(m.group(1)).get("page", 0))
        except (ValueError, TypeError):
            continue
        if page == n:
            return markdown[:m.start()] + layout_block(spec) + markdown[m.end():]
    return (markdown or "").rstrip() + "\n\n" + layout_block(spec) + "\n"


def keep_page(slug, page, where="kept mid-round"):
    """Keep a page as it stands: the same lock a review writes, set while the room is working.

    From here on enforce_locks puts this page's script section, layout block and sketch back
    into whatever an agent saves, and the gate stops reporting layout issues for it."""
    specs, _ = thumbnails.parse_layouts(projects.read_artifact(slug, "layouts.md"))
    spec = next((s for s in specs if s["page"] == page), None)
    if spec is None:
        raise ValueError(f"page {page} has no layout yet, so there is nothing to keep")
    _, pages = canonical(slug)
    drawn = pages.get(page, {})
    section = _script_span(projects.read_artifact(slug, "script.md") or "", page)
    lk = locks(slug)
    lk[page] = {"kind": KEPT, "round": where, "ascii": drawn.get("art", ""),
                "invert": drawn.get("invert", ""), "script": section.group(0).strip() if section else None,
                "layout": spec}
    _save(slug, LOCKS, {str(k): v for k, v in lk.items()})
    return lk[page]


def release_page(slug, page):
    """Let the room work on the page again."""
    lk = locks(slug)
    lk.pop(page, None)
    _save(slug, LOCKS, {str(k): v for k, v in lk.items()})


def kept(slug):
    """{page: what keeps it} — pages the room must leave alone."""
    return {n: l.get("round") for n, l in locks(slug).items() if l.get("kind") == KEPT}


def enforce_locks(slug, name, content):
    """Put locked pages back into a file an agent is saving. Returns (content, pages restored)."""
    lk = locks(slug)
    restored = []
    if not lk:
        return content, restored
    if name == "script.md":
        for n, l in lk.items():
            if l.get("script"):
                m = _script_span(content, n)
                if not m or m.group(0).strip() != l["script"].strip():
                    content = replace_script_section(content, n, l["script"])
                    restored.append(n)
    elif name == "layouts.md":
        specs = {s["page"]: s for s in thumbnails.parse_layouts(content)[0]}
        for n, l in lk.items():
            if l.get("layout") and specs.get(n) != l["layout"]:
                content = replace_layout(content, n, l["layout"])
                restored.append(n)
    elif name == canonical_file(slug):   # the reviewed pages; the other preview keeps showing its own render
        pages = thumbnails.parse_thumbnails(content)
        for n, l in lk.items():
            invert = l.get("invert", "")
            if n in pages and (pages[n]["art"] != l["ascii"] or not pages[n]["edited"]
                               or _mask(pages[n]["invert"]) != _mask(invert)):
                content = thumbnails.replace_page(content, n, l["ascii"], True, invert)
                restored.append(n)
    return content, sorted(set(restored))


# ---- submitting a review ---------------------------------------------------------------

def _page_instructions(n, kept, comment, diff_md, has_edit):
    if kept:
        head, body = "kept", "LOCKED. This page is done. Do not change it."
    elif has_edit:
        head, body = "the showrunner's version", (
            "LOCKED as the showrunner's version (below). Bring script.md and layouts.md into line "
            "with it: dialogue exactly as written on the page, panels and staging as drawn.")
    elif comment:
        head, body = "open, with a note", "Work on this page from the note below, and change nothing else."
    else:
        head, body = "open", "The showrunner said nothing about this page. Carry on with it."
    parts = [f"## Page {n} — {head}", "", body]
    if comment:
        parts += ["", f"Showrunner: {comment}"]
    if has_edit:
        parts += ["", "What the showrunner changed on the page:", "", diff_md]
    return "\n".join(parts)


def submit(slug, action, comment=None):
    """action: 'send' (to the room) or 'finalize'. Returns the new round's id."""
    if action not in ("send", "finalize"):
        raise ValueError("action must be 'send' or 'finalize'")
    if comment is not None:
        save_comment(slug, comment)
    st = state(slug)
    if not st["open"]:
        raise ValueError("there is no finished AI round waiting for review")
    pages = st["pages"]
    loose = [n for n, p in pages.items() if not (p["kept"] or p["edited"] or p["comment"])]

    specs = {s["page"]: s for s in thumbnails.parse_layouts(projects.read_artifact(slug, "layouts.md"))[0]}
    script = projects.read_artifact(slug, "script.md") or ""
    geo = thumbnails.geometry()
    h = projects.Round(slug, kind="final" if action == "finalize" else "human",
                       reviewed_round=st["round"], action=action, method=st["method"])
    record = {"round": h.id, "reviewed_round": st["round"], "action": action,
              "comment": st["comment"], "pages": {}}
    instructions = []
    lk = locks(slug)
    for n, p in pages.items():
        panels = thumbnails.render_page(specs[n], geo).panels if n in specs else []
        diff = asciitext.page_diff(p["ai_art"], p["art"], panels, p["ai_invert"], p["invert"])
        diff_md = asciitext.diff_markdown(diff)
        section = _script_span(script, n)
        section = section.group(0).strip() if section else ""
        kept = p["kept"]
        record["pages"][n] = {"kept": kept, "comment": p["comment"], "edited": p["edited"],
                              "text_similarity": diff["text_similarity"],
                              "art_similarity": diff["art_similarity"], "text_changes": diff["text"]}
        pre = f"p{n:02d}"
        h.write_file(f"{pre}-ascii.txt", p["art"])
        if p["invert"].strip():
            h.write_file(f"{pre}-invert.txt", p["invert"])
        if p["edited"]:
            h.write_file(f"{pre}-ai-ascii.txt", p["ai_art"])
            if p["ai_invert"].strip():
                h.write_file(f"{pre}-ai-invert.txt", p["ai_invert"])
            h.write_file(f"{pre}-diff.md", f"# Page {n}: AI ({st['round']}) → showrunner ({h.id})\n\n{diff_md}\n")
        if section:
            h.write_file(f"{pre}-script.md", section + "\n")
        if n in specs:
            h.write_file(f"{pre}-layout.json", json.dumps(specs[n], indent=2))
        label = "kept" if kept else "the showrunner's version" if p["edited"] else "open"
        h.write_file(f"{pre}-review.md",
                     f"# Page {n}\n\n**{label}**\n\n{p['comment'] or '(no comment)'}\n\n{diff_md}\n")
        instructions.append(_page_instructions(n, kept, p["comment"], diff_md, p["edited"]))

        if kept or p["edited"]:
            lk[n] = {"kind": KEPT if kept else EDITED, "round": h.id,
                     "ascii": p["art"], "invert": p["invert"],
                     "script": section if kept else None,
                     "layout": specs.get(n) if kept else None}
        else:                       # nothing holds this page: the room is free to redraw it
            lk.pop(n, None)

    counts = {"kept": sum(1 for p in pages.values() if p["kept"]),
              "edited": sum(1 for p in pages.values() if p["edited"] and not p["kept"]),
              "noted": sum(1 for p in pages.values() if p["comment"] and not p["kept"] and not p["edited"])}
    head = [f"# Review {h.id} of {st['round']}", "",
            f"{counts['kept']} kept · {counts['edited']} redrawn by the showrunner · "
            f"{counts['noted']} with a note", ""]
    if st["comment"]:
        head += ["## Showrunner's overall note", "", st["comment"], ""]
    jotted = notes.take(slug, h.id)
    if jotted:
        head += [jotted, ""]
        h.write_file("showrunner-notes.md", jotted)
    review_md = "\n".join(head) + "\n" + "\n\n".join(instructions) + "\n"
    h.write("review.md", review_md)
    h.write_file("review.json", json.dumps(record, indent=2))
    _save(slug, LOCKS, {str(k): v for k, v in lk.items()})

    # the working copy's pages: locked pages become the showrunner's; the rest get redrawn
    name = FILES[st["method"]]
    md = projects.read_artifact(slug, name) or ""
    for n in loose:
        if n in thumbnails.parse_thumbnails(md):
            md = thumbnails.replace_page(md, n, None, False)
    md, _ = enforce_locks(slug, name, md)
    h.write(name, md)

    page_prompts, book_prompts = prompts.build(slug)
    for n, text in page_prompts.items():
        h.write_file(f"p{n:02d}-prompt.md", text)
    h.write("page-prompts.md", book_prompts)
    letters = text_layers(slug)
    for n, svg in letters.items():
        h.write_file(f"p{n:02d}-letters.svg", svg)
    projects.export_output(slug, page_prompts, book_prompts, h.id, letters)
    if action == "finalize":
        h.write_file("book-prompts.md", book_prompts)
        book = "\n\n".join(f"{'=' * 20} PAGE {n} {'=' * 20}\n{p['art']}" for n, p in pages.items())
        h.write_file("book-ascii.txt", book + "\n")
        inverted = "\n\n".join(f"{'=' * 20} PAGE {n} {'=' * 20}\n{p['invert']}" for n, p in pages.items() if p["invert"].strip())
        if inverted:
            h.write_file("book-invert.txt", inverted + "\n")
    _save(slug, DRAFT, {})
    h.update(status="done", finished=projects.now(), counts=counts)
    return h.id


# ---- the readiness gate ------------------------------------------------------------------

BLOCKERS_RE = re.compile(r"^\s*BLOCKERS:\s*(\d+)", re.M | re.I)
FIX_RE = re.compile(r"^\s*FIX:\s*(.+)$", re.M | re.I)


def dial_in(slug, n, spec, locked_ascii):
    """How closely the layout render of page n matches the showrunner's locked page."""
    page = thumbnails.render_page(spec)
    render = thumbnails.compose(page)
    frame = lambda text: "\n".join("".join(c if c in "_|+=" else " " for c in line) for line in text.split("\n"))
    return {"text": asciitext.text_similarity(render, locked_ascii),
            "layout": asciitext.art_similarity(frame(render), frame(locked_ascii)),
            "diff": asciitext.diff_markdown(asciitext.page_diff(render, locked_ascii, page.panels))}


def gate(slug, role_titles):
    """Is the round ready for the showrunner? Returns reasons and which roles should fix what."""
    st = settings(slug)
    want = st["pages"]
    specs, errors = thumbnails.parse_layouts(projects.read_artifact(slug, "layouts.md"))
    lk = locks(slug)
    reasons, fix, notes = [], set(), []
    numbers = [s["page"] for s in specs]
    if errors:
        reasons.append(f"{len(errors)} layout blocks don't parse")
        notes += errors
        fix.add("layout")
    if want and sorted(numbers) != list(range(1, want + 1)):
        reasons.append(f"layouts.md has pages {numbers}, the brief asks for pages 1-{want}")
        fix.add("layout")
    issues = []
    for s in specs:
        if lk.get(s["page"], {}).get("kind") == KEPT:
            continue
        issues += [f"page {s['page']}: {i}" for i in thumbnails.render_page(s).issues]
    if issues:
        reasons.append(f"{len(issues)} layout issues")
        notes += issues
        fix.add("layout")

    notes_md = projects.read_artifact(slug, "notes.md") or ""
    m = BLOCKERS_RE.search(notes_md)
    blockers = int(m.group(1)) if m else None
    if blockers:
        reasons.append(f"{blockers} continuity blockers")
        f = FIX_RE.search(notes_md)
        for word in re.split(r"[,;/]| and ", f.group(1) if f else ""):
            word = word.strip().lower()
            for rid, title in role_titles.items():
                if word and (word == rid or word == title.lower() or word in title.lower()):
                    fix.add(rid)
        notes.append("See the Blockers in notes.md.")

    dialed = {}
    for n, l in lk.items():
        if l.get("kind") != EDITED:
            continue
        spec = next((s for s in specs if s["page"] == n), None)
        if spec is None:
            continue
        d = dial_in(slug, n, spec, l["ascii"])
        dialed[n] = {"text": d["text"], "layout": d["layout"]}
        if d["text"] < st["min_text_match"]:
            fix.add("layout")            # the script is locked by now: the layout carries the lettering
            reasons.append(f"page {n} dialogue matches the showrunner's page {d['text']:.0%}")
            notes.append(f"Page {n}: make the layout's lettering match the showrunner's page exactly.\n{d['diff']}")
        elif d["layout"] < st["min_layout_match"]:
            fix.add("layout")
            reasons.append(f"page {n} panel layout matches the showrunner's page {d['layout']:.0%}")
            notes.append(f"Page {n}: move panels and lettering to where the showrunner drew them.\n{d['diff']}")
    return {"ready": not reasons, "reasons": reasons, "fix": sorted(fix), "notes": notes,
            "blockers": blockers, "layout_issues": len(issues), "pages": numbers, "dialed_in": dialed}


# ---- per-page exports for an AI round ------------------------------------------------------

def text_layers(slug, version=None):
    """{page: SVG} — the lettering as its own transparent layer, for art drawn without text."""
    specs, _ = thumbnails.parse_layouts(projects.read_artifact(slug, "layouts.md", version))
    ctx = prompts.context(slug, version)
    return {s["page"]: lettering.svg(s, ctx) for s in specs}


def export_pages(slug, rnd):
    """Write <round>-pNN-{prompt,ascii,script,layout}.* into the round folder, and the
    page prompts (the room's deliverable) into the working copy and the round. Before
    execution there are no layouts, so there are no pages and nothing is written."""
    page_prompts, book_prompts = prompts.build(slug)
    if not page_prompts:
        return []
    rnd.write("page-prompts.md", book_prompts)
    for n, text in page_prompts.items():
        rnd.write_file(f"p{n:02d}-prompt.md", text)
    letters = text_layers(slug)
    for n, svg in letters.items():
        rnd.write_file(f"p{n:02d}-letters.svg", svg)
    projects.export_output(slug, page_prompts, book_prompts, rnd.id, letters)
    method, pages = canonical(slug)
    renders = thumbnails.parse_thumbnails(projects.read_artifact(slug, "thumbnails.md"))
    specs = {s["page"]: s for s in thumbnails.parse_layouts(projects.read_artifact(slug, "layouts.md"))[0]}
    script = projects.read_artifact(slug, "script.md") or ""
    for n in sorted(set(pages) | set(specs)):
        pre = f"p{n:02d}"
        if n in pages:
            rnd.write_file(f"{pre}-ascii.txt", pages[n]["art"])
            if pages[n]["invert"].strip():
                rnd.write_file(f"{pre}-invert.txt", pages[n]["invert"])
        if n in renders and method != "layout":
            rnd.write_file(f"{pre}-render.txt", renders[n]["art"])
        if n in specs:
            rnd.write_file(f"{pre}-layout.json", json.dumps(specs[n], indent=2))
        section = _script_span(script, n)
        if section:
            rnd.write_file(f"{pre}-script.md", section.group(0).strip() + "\n")
    return sorted(pages)
