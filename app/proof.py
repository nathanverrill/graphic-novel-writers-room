"""The proof: the cheap pass that gets a page right before the final lettering.

Art checked with the bubbles off and redrawn from a note; words edited in place; balloons and tails
dragged to the right speaker - all over the drawn art, all free but the art redraws. What the proof
says is the script: every edit rewrites the candidate script (script.md), which starts as the
showrunner's draft. A page is locked once it is drawn (render.page locks it), and nothing - an editor,
the page chat, a layout run, a bring back, a redraw - changes it until it is unlocked; locking it again
keeps it as it then is. Sunburst letters locked pages only, and only when asked: it is the last step.

    production/proof.json   {"pages": {"37": {"locked": true, "at": "...", "spec": {...}}}}
"""
import json
import re
import threading
import time

from . import projects, thumbnails

_io = threading.Lock()


def _file(slug):
    return projects.project_dir(slug) / "proof.json"


def _load(slug):
    f = _file(slug)
    try:
        return json.loads(f.read_text()) if f.is_file() else {"pages": {}}
    except ValueError:
        return {"pages": {}}


def _save(slug, data):
    _file(slug).write_text(json.dumps(data, ensure_ascii=False, indent=1))


def locked(slug):
    """{page: when} for every locked page."""
    return {int(k): v.get("at") for k, v in _load(slug)["pages"].items() if v.get("locked")}


def is_locked(slug, n):
    return int(n) in locked(slug)


def check_unlocked(slug, n):
    if is_locked(slug, n):
        raise ValueError(f"page {n} is approved and locked - unlock it to change it")


def _spec(slug, n):
    specs, _ = thumbnails.parse_layouts(projects.read_artifact(slug, "layouts.md") or "")
    return next((s for s in specs if s.get("page") == n), None)


def lock(slug, n):
    """Approve page n as it is: its layout is kept as approved, and guarded."""
    spec = _spec(slug, n)
    if not spec:
        raise ValueError(f"page {n} has no layout")
    with _io:
        data = _load(slug)
        data["pages"][str(n)] = {"locked": True, "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "spec": spec}
        _save(slug, data)
    return status(slug)


def unlock(slug, n):
    with _io:
        data = _load(slug)
        data["pages"].pop(str(n), None)
        _save(slug, data)
    return status(slug)


def keep_locked(slug, markdown):
    """layouts.md about to be written whole (a layout run, a hand edit, the room): the locked
    pages keep their approved blocks."""
    from . import lettering
    pages = _load(slug)["pages"]
    for k, v in pages.items():
        if v.get("locked") and v.get("spec"):
            try:
                markdown = lettering.replace_block(markdown, int(k), v["spec"])
            except ValueError:      # the new file dropped the page: leave that to the showrunner
                pass
    return markdown


def status(slug):
    lk = locked(slug)
    return {"locked": sorted(lk), "at": {str(k): v for k, v in lk.items()}}


# ---- the candidate script: what the proof says, page by page -----------------------------------

def candidate(slug):
    """The script as the proof has it now: each page's panels and, under each, its words by speaker."""
    from . import render
    out = [f"```markdown\n# {slug} — Script (the proof: edited words are the script)\n"]
    for sp in render.book(slug):
        out.append(f"## Page {sp['page']} ({sp.get('side', '')})\n")
        words = [i for i in sp.get("items") or [] if i.get("type") != "figure" and i.get("text")]
        k = 0
        for t in sp.get("tiers") or []:
            for p in t.get("panels") or []:
                k += 1
                out.append(f"**{p.get('label') or f'Panel {k}'}.** {p.get('description') or ''}\n")
                said = [f"{(i.get('speaker') or i.get('type', '')).upper()}: {i['text']}" for i in words if i.get("panel") == k]
                if said:
                    out.append("\n".join(said) + "\n")
    out.append("```\n")
    return "\n".join(out)


def write_candidate(slug):
    projects.write_artifact(slug, "script.md", candidate(slug))


# ---- the showrunner's draft for a page ------------------------------------------------------------

_PAGE_HEAD = re.compile(r"^\W*page\s+\d+\b.*$", re.I | re.M)


def _norm(t):
    t = (t or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9' ]", " ", t)).strip()


def _chapter_file(slug, n):
    """The draft file holding page n's chapter: chapters.json gives the chapter, drafts/ its file in order."""
    f = projects.project_dir(slug) / "chapters.json"
    try:
        chapters = json.loads(f.read_text()) if f.is_file() else []
    except ValueError:
        chapters = []
    k = next((j for j, c in enumerate(chapters) if c.get("first", 0) <= n <= c.get("last", 0)), None)
    files = sorted(p for p in (projects.project_dir(slug).parent / "drafts").glob("*.md")) \
        if (projects.project_dir(slug).parent / "drafts").is_dir() else []
    if k is None or k >= len(files):
        return None
    return files[k]


def draft(slug, n):
    """The showrunner's draft of page n: the draft page (or two) whose lines the page's words
    come from, and for each item whether its words are the draft's, word for word."""
    from . import lettering
    items = [i for i in lettering.items(_spec(slug, n) or {}) if i.get("text")]
    f = _chapter_file(slug, n)
    if not f:
        return {"text": "", "file": None, "same": {}}
    text = f.read_text()
    heads = list(_PAGE_HEAD.finditer(text))
    sections = [text[h.start():(heads[j + 1].start() if j + 1 < len(heads) else len(text))].strip()
                for j, h in enumerate(heads)] or [text]
    norms = [_norm(s) for s in sections]
    scores = [sum(1 for i in items if _norm(i["text"]) and _norm(i["text"]) in s) for s in norms]
    best = sorted(range(len(sections)), key=lambda j: -scores[j])[:2]
    best = sorted(j for j in best if scores[j] > 0) or ([max(range(len(sections)), key=lambda j: scores[j])] if sections else [])
    joined = " ".join(norms[j] for j in best)
    rel = f.relative_to(projects.project_dir(slug).parent)
    return {"text": "\n\n".join(sections[j] for j in best), "file": str(rel),
            "same": {str(i["i"]): bool(_norm(i["text"]) and _norm(i["text"]) in joined) for i in items}}
