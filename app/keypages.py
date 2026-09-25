"""Key pages: finished pages the showrunner locks - their look for the whole book, their words
and panels for themselves.

    campaigns/<slug>/keypages/ch01-p01.md    the page: purpose, description, dialogue, layout, notes
    campaigns/<slug>/keypages/ch01-p01.jpg   the page as drawn and lettered (.png and .webp also do)
    campaigns/<slug>/keypages/notes.md       what they do NOT lock: where a page is off-model, the canon wins

A key page is chapter N's page K. Its place in the book comes from the chapter map
(magic.chapter_pages); chapter 1's pages are book pages 1, 2, 3 ... whatever the map says.

What a key page locks, and where:
    the look      every agent that sees images is sent the key pages as the book's style
                  reference, and every page packet names them as attachments
    the words     its dialogue and captions, word for word: the Draft Editor may not touch them,
                  the writer scripts that page with them, and the gate sends a script that
                  drops or changes one back to the writer
    the panels    its layout is the Layout Agent's for that page
"""
import re

from . import projects

FOLDER = "keypages"
NAME_RE = re.compile(r"^ch(\d+)-p(\d+)\.(md|jpg|jpeg|png|webp)$", re.I)
MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
DIALOGUE = re.compile(r"^#{2,3}\s*Dialogue\b[^\n]*\n(.*?)(?=^#{1,3}\s|\Z)", re.M | re.S | re.I)
LAYOUT = re.compile(r"^#{2,3}\s*Layout\b[^\n]*\n(.*?)(?=^#{1,3}\s|\Z)", re.M | re.S | re.I)


def folder(slug):
    return projects.campaign_dir(slug) / FOLDER


def book_page(slug, chapter, page):
    """Chapter N's page K, as a page of the book - or None when the chapter's start is unknown."""
    from . import magic      # magic imports the room, which imports this
    for c in magic.chapter_pages(slug):
        if c["chapter"] == chapter:
            return c["first"] + page - 1
    return page if chapter == 1 else None


def lines(text):
    """The page's words, as [(speaker or None, words)], from its Dialogue section."""
    m = DIALOGUE.search(text or "")
    out = []
    for item in re.findall(r"^\s*[-*]\s+(.+)$", m.group(1) if m else "", re.M):
        item = item.strip().replace("**", "")
        who = re.match(r"^([A-Z][A-Z0-9 .'-]{1,30}):\s+(.+)$", item)
        out.append((who.group(1).strip(), who.group(2).strip()) if who else (None, item))
    return out


def pages(slug):
    """[{chapter, page, book, title, text, art, lines, layout}], in book order."""
    d = folder(slug)
    found = {}
    for f in sorted(d.iterdir()) if d.is_dir() else []:
        m = NAME_RE.match(f.name)
        if not m:
            continue
        k = (int(m.group(1)), int(m.group(2)))
        entry = found.setdefault(k, {"chapter": k[0], "page": k[1], "text": "", "art": None})
        if m.group(3).lower() == "md":
            entry["text"] = f.read_text()
        else:
            entry["art"] = f
    out = []
    for (ch, p), e in sorted(found.items()):
        head = re.search(r"^#\s+(.+)$", e["text"], re.M)
        lay = LAYOUT.search(e["text"])
        out.append({**e, "book": book_page(slug, ch, p), "title": head.group(1).strip() if head else f"Chapter {ch}, page {p}",
                    "lines": lines(e["text"]), "layout": lay.group(1).strip() if lay else ""})
    return out


def of(slug, n):
    """The key page that is book page n, if there is one."""
    return next((k for k in pages(slug) if k["book"] == n), None)


def images(slug, limit=9):
    """The key pages' art as (label, mime, bytes): the book's look, for agents that see images."""
    out = []
    for k in pages(slug):
        if k["art"] and len(out) < limit:
            but = exceptions(slug)
            out.append((f"key page {k['book'] or '?'} ({k['title']}) - the locked look of the book, lettered"
                        + (f"; the canon wins where it differs: {but}" if but else ""),
                        MIME.get(k["art"].suffix.lower(), "image/jpeg"), k["art"].read_bytes()))
    return out


def notes(slug):
    """keypages/notes.md: what the key pages do NOT lock - where a page is off-model and the canon wins."""
    f = folder(slug) / "notes.md"
    return f.read_text().strip() if f.is_file() else ""


def exceptions(slug):
    """The notes' bullets, run together on one line, for an image label or a packet line."""
    bullets = re.findall(r"^\s*[-*]\s+(.+?)(?=^\s*[-*]\s|\Z)", notes(slug), re.M | re.S)
    return " ".join(re.sub(r"\s+", " ", b).strip() for b in bullets).replace("**", "")


def brief(slug):
    """The key pages, as the room is told them: which pages, and their locked words and panels."""
    ks = pages(slug)
    if not ks:
        return ""
    parts = ["# Key pages - locked by the showrunner",
             "These pages are finished. Their look is the look of the whole book. Their words - every "
             "caption and line below - are used exactly as written, on that page, and never edited. Their "
             "layout is that page's layout."]
    if notes(slug):
        parts.append(notes(slug).replace("# What the key pages", "## What the key pages", 1))
    for k in ks:
        where = f"book page {k['book']}" if k["book"] else "book page not yet known"
        said = "\n".join(f"- {w + ': ' if w else ''}{t}" for w, t in k["lines"]) or "- (no words)"
        parts.append(f"## {k['title']} - chapter {k['chapter']}, page {k['page']} ({where})\n\n"
                     f"Words, locked:\n{said}\n\nLayout, locked:\n{k['layout'] or '(as drawn)'}")
    return "\n\n".join(parts)


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower().replace("’", "'")).strip()


def check(slug, script):
    """Key-page words missing from their page of the script: ["page 9: '...' is not word for word"]."""
    out = []
    for k in pages(slug):
        if not k["book"] or not k["lines"]:
            continue
        m = re.search(rf"^##\s*Page\s+{k['book']}\b.*?(?=^##\s*Page\s+\d+|\Z)", script or "", re.M | re.S | re.I)
        if not m:
            out.append(f"page {k['book']} is a key page and is missing from the script")
            continue
        here = norm(m.group(0))
        for _, words in k["lines"]:
            if norm(words) not in here:
                out.append(f"page {k['book']}: key-page line not word for word: \"{words[:70]}\"")
    return out
