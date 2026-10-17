"""The easy desk (/easy): one campaign, and what can be done with it next, in plain words.

It reads what the room already keeps and calls what the room already does - render.start for
drawing, the lettering layer for words, the story desk for character locks. The one thing it adds
is a copy of every drawing before it is drawn again:

    campaigns/<slug>/renders/sunburst/previous/<time>/art/p01.png
    campaigns/<slug>/renders/sunburst/previous/<time>/lettered/p01.png

so "bring back the earlier drawing" is always one button away."""
import shutil
import time

from . import phases, projects, render

TAG = "sunburst"        # the only model the book is drawn with
COST_PAGE = 0.40        # roughly, per page, art check and redraws included


def _png(d, n):
    return d / f"p{n:02d}.png"


def _mtime(p):
    return int(p.stat().st_mtime) if p.is_file() else 0


def running(slug):
    t = render._threads.get((slug, TAG))
    return bool(t and t.is_alive())


def _previous(slug):
    d = render.folder(slug, TAG) / "previous"
    return sorted((p for p in d.iterdir() if p.is_dir()), reverse=True) if d.is_dir() else []


def _earlier(slug, n):
    """The newest kept copy of page n's art, or None."""
    return next((p for p in _previous(slug) if _png(p / "art", n).is_file()), None)


def status(slug):
    """Where the book stands, page by page, and which stage it is at:
    write (no pages laid out yet), draw (laid out, nothing drawn) or art (drawn)."""
    projects.project_dir(slug)          # a missing campaign is a 404
    phase = phases.state(slug)["phase"]
    art, let = render.folder(slug, TAG, "art"), render.folder(slug, TAG, "lettered")
    checks = render.status(slug)["models"].get(TAG, {}).get("pages", {})
    pages = []
    for spec in render.book(slug):
        n = spec["page"]
        st = checks.get(str(n), {})
        a, l = _mtime(_png(art, n)), _mtime(_png(let, n))
        check = st.get("check") or {}
        pages.append({"page": n, "art": a, "lettered": l,
                      "needs_letters": bool(a and l < a),
                      "flagged": bool(a and check.get("pass") is False),
                      "problems": [p.get("what", "") for p in check.get("problems") or []][:6],
                      "state": st.get("state") or ("done" if a else "not drawn"),
                      "error": st.get("error"),
                      "earlier": bool(_earlier(slug, n))})
    drawn = [p for p in pages if p["art"]]
    stage = "write" if not pages else "draw" if not drawn else "art"
    return {"slug": slug, "phase": phase, "desk": projects.desk_for(phase), "stage": stage,
            "running": running(slug), "cost_page": COST_PAGE, "pages": pages,
            "counts": {"pages": len(pages), "drawn": len(drawn),
                       "lettered": sum(1 for p in pages if p["lettered"]),
                       "flagged": sum(1 for p in pages if p["flagged"]),
                       "needs_letters": sum(1 for p in pages if p["needs_letters"]),
                       "drawing": sum(1 for p in pages if p["state"] == "drawing")}}


def _keep_copy(slug, pages):
    """Copy the current art and lettering of these pages aside before they are drawn again."""
    art, let = render.folder(slug, TAG, "art"), render.folder(slug, TAG, "lettered")
    to = render.folder(slug, TAG) / "previous" / (time.strftime("%Y%m%d-%H%M%S") + f"-{int(time.time() * 1000) % 1000:03d}")
    kept = []
    for n in pages:
        for src, kind in ((_png(art, n), "art"), (_png(let, n), "lettered")):
            if src.is_file():
                (to / kind).mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, to / kind / src.name)
                if kind == "art":
                    kept.append(n)
    return kept


def draw(slug, pages=None, again=False):
    """Draw pages with Sunburst in the background. again=False draws only pages not drawn yet;
    again=True draws the named pages (or every page) again, after keeping a copy of each."""
    if running(slug):
        raise ValueError("the book is already being drawn - wait for it to finish")
    laid_out = [s["page"] for s in render.book(slug)]
    if not laid_out:
        raise ValueError("the book has no pages laid out yet")
    targets = [n for n in (pages or laid_out) if n in laid_out]
    if not targets:
        raise ValueError("none of those pages are laid out")
    kept = _keep_copy(slug, targets) if again else []
    out = render.start(slug, [TAG], targets, redo=again)
    return {"started": out.get("started", []), "pages": targets, "kept_copy": kept}


def restore(slug, n):
    """Put back the newest kept copy of page n. What is there now is kept first, so this can be
    undone the same way."""
    if running(slug):
        raise ValueError("wait for the drawing to finish first")
    src = _earlier(slug, n)
    if not src:
        raise FileNotFoundError(f"no earlier drawing of page {n}")
    _keep_copy(slug, [n])
    art, let = render.folder(slug, TAG, "art"), render.folder(slug, TAG, "lettered")
    art.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(_png(src / "art", n), _png(art, n))          # copyfile: the art is new, so
    if _png(src / "lettered", n).is_file():                       # its lettering, copied after,
        let.mkdir(parents=True, exist_ok=True)                    # is newer still
        shutil.copyfile(_png(src / "lettered", n), _png(let, n))
    for kind in ("art", "lettered"):     # this page's copy is back in place; the one just kept
        _png(src / kind, n).unlink(missing_ok=True)    # replaces it. Other pages' copies stay
    for d in (src / "art", src / "lettered", src):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()
    return status(slug)
