"""The renderer: every page of the book drawn by each image model; lettering is a second step.

For each model and each page of layouts.md:

    art        the page packet's prompt, sent with reference images: the style plate (the
               book's look), the model's own lock of every character on the page, and - for a
               key page - the key page's art, to be close to it. No balloons or captions; the
               sound effects are drawn in, part of the scene (unless the book's "sfx" is "layer")
    checked    every drawing is looked over by artcheck (fingers, limbs, faces, clones, text,
               characters off their locks, sound effects spelled right) and redrawn with the
               problems named, up to three tries
    placed     one look at the drawn page (place_lettering) puts each balloon and caption in
               calm space and points each tail at its speaker, saved in layouts.md
    overlay    the lettering alone, as SVG and as a transparent PNG (letter_pages)
    lettered   the overlay composited over the art: the words exactly the script's, the art
               unchanged. Editing words letters the page again, free

    campaigns/<slug>/renders/<model>/art/p01.png
    campaigns/<slug>/renders/<model>/overlay/p01.svg, p01.png
    campaigns/<slug>/renders/<model>/lettered/p01.png
    campaigns/<slug>/renders/status.json      page by page: done, failed, how long, what it cost

A character's lock for a model is the campaign's own "<name>-<model>" folder under
campaigns/<slug>/style/locks/ (built in Sheets, then kept with the campaign); the plate is
campaigns/<slug>/style/plate.* - both are one book's look, never shared across campaigns. A page is drawn once; drawing
it again is asked for by name. Runs in a thread per model, a few pages at a time, and picks up
where it stopped.
"""
import base64
import concurrent.futures
import io
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request

from . import artcheck, keypages, keys, lettering, projects, prompts, thumbnails, usage

MODELS = {"sunburst": "openai/gpt-image-2.5-sunburst"}   # the only drawing model (Gemini dropped 2026-10-17: its pages looked cheap)
OPENROUTER = "https://openrouter.ai/api/v1"
MAX_REFS = 6            # the plate, then the page's key art, then up to four locks
WORKERS = int(os.getenv("RENDER_WORKERS") or 8)   # pages at a time, per model; the provider's rate limit is the ceiling
TIMEOUT = 300
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}

_lock = threading.Lock()
_threads = {}


def folder(slug, tag=None, kind=None):
    d = projects.campaign_dir(slug) / "renders"
    return d / tag / kind if kind else d / tag if tag else d


# ---- status ----------------------------------------------------------------------------------

def status(slug):
    f = folder(slug) / "status.json"
    return json.loads(f.read_text()) if f.exists() else {"models": {}}


def _update(slug, tag, page=None, **changes):
    with _lock:
        st = status(slug)
        m = st["models"].setdefault(tag, {"state": "idle", "pages": {}})
        if page is None:
            m.update(changes)
        else:
            m["pages"].setdefault(str(page), {}).update(changes)
        folder(slug).mkdir(parents=True, exist_ok=True)
        (folder(slug) / "status.json").write_text(json.dumps(st, indent=1))


# ---- references ------------------------------------------------------------------------------

def plate(slug):
    """The campaign's own style plate (campaigns/<slug>/style/plate.*). A plate is one book's
    look, so a campaign without one gets none - never another campaign's."""
    d = projects.campaign_dir(slug) / "style"
    found = sorted(d.glob("plate.*")) if d.is_dir() else []
    return found[0] if found else None


def full_name(name, bible):
    """A speaker as the layouts write them ("ALEX") as the canon names them ("Alex Phantum"):
    the canon entry that is the name, or else the one entry it starts. "TOMAS" stays Tomas, the
    miner, and never becomes Tomas Reed."""
    entries = prompts.character_entries(bible or "")
    low = (name or "").strip().lower()
    exact = [e for e in entries if e.lower() == low]
    if exact:
        return exact[0]
    starts = [e for e in entries if e.lower().split()[0] == low]
    return starts[0] if len(starts) == 1 else name


def lock_for(slug, name, tag, bible=""):
    """The model's kept lock of a character: the subject folder whose name, less "-<model>",
    is in the character's full name (cassian-lock-gemini for DIRECTOR CASSIAN LOCK).

    Locks are the campaign's own, under campaigns/<slug>/style/locks/ - a cast belongs to one
    book, so another campaign's lock is never matched, whatever the names share."""
    base = projects.campaign_dir(slug) / "style" / "locks"
    words = set(re.findall(r"[a-z0-9]+", full_name(name, bible).lower()))
    best = None
    for d in base.glob(f"*-{tag}") if base.is_dir() else []:
        stem = set(re.findall(r"[a-z0-9]+", d.name[:-len(tag) - 1]))
        locks = [p for p in d.glob("lock.*") if p.suffix.lower() in MIME]
        if stem and stem <= words and locks and (best is None or len(stem) > best[0]):
            best = (len(stem), locks[0])
    return best[1] if best else None


def references(slug, tag, spec, ctx):
    """[(label, path)]: what this page is drawn from, most important first."""
    out = []
    if plate(slug):
        out.append(("the style plate - draw in exactly this style", plate(slug)))
    key = keypages.of(slug, spec.get("page"))
    if key and key["art"]:
        out.append((f"this page as drawn before - stay close to its composition", key["art"]))
    names, _, _ = prompts.page_cast(spec, ctx)
    for n in names:
        lock = lock_for(slug, n, tag, ctx.get("bible"))
        if lock and all(p != lock for _, p in out):
            out.append((f"{n}: draw this character exactly as this lock", lock))
    return out[:MAX_REFS]


# ---- one page --------------------------------------------------------------------------------

def api_key():
    return os.getenv("OPENROUTER_API_KEY") or keys.get(OPENROUTER)


def data_url(path):
    return f"data:{MIME.get(path.suffix.lower(), 'image/png')};base64," + base64.b64encode(path.read_bytes()).decode()


def generate(model, prompt, refs, key):
    """One image from OpenRouter's images endpoint, with reference images. Returns (bytes, cost)."""
    payload = {"model": model, "prompt": prompt}
    if refs:
        payload["input_references"] = [{"type": "image_url", "image_url": {"url": data_url(p)}} for _, p in refs]
    req = urllib.request.Request(f"{OPENROUTER}/images", data=json.dumps(payload).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                          "HTTP-Referer": "https://github.com/writers-room", "X-Title": "render"})
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                result = json.loads(r.read())
            break
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code} {e.read()[:300].decode(errors='replace')}")
        except (ConnectionResetError, TimeoutError, urllib.error.URLError) as e:
            if attempt == 2:
                raise RuntimeError(f"no answer: {e}")
    item = (result.get("data") or [{}])[0]
    if not item.get("b64_json"):
        raise RuntimeError(f"no image in the reply: {json.dumps(result)[:300]}")
    return base64.b64decode(item["b64_json"]), (result.get("usage") or {}).get("cost")


def prompt_for(spec, ctx, refs):
    """The page packet's prompt, told what each attached image is."""
    text = prompts.page_prompt(spec, ctx)
    if refs:
        text += "\n\n**The attached images, in order:**\n\n" + "\n".join(f"{i}. {label}" for i, (label, _) in enumerate(refs, 1))
    if keypages.exceptions(ctx.get("slug", "")):
        text += "\n\n" + keypages.exceptions(ctx["slug"])
    return text


def overlay(art_bytes, spec, ctx):
    """(svg, png): the lettering alone - balloons, captions, tails, the script's exact words -
    as SVG and as a transparent PNG the size of the art, to lay over it."""
    import cairosvg
    from PIL import Image
    art = Image.open(io.BytesIO(art_bytes))
    rects = lettering.detect_rects(spec, art_bytes)   # the drawn grid, not the assumed one
    size = (1000, round(1000 * art.height / art.width))   # the layer in the art's own proportions
    svg = lettering.svg(spec, {**ctx, "page_label": False, "page_size": size}, rects)
    return svg, cairosvg.svg2png(bytestring=svg.encode(), output_width=art.width, output_height=art.height)


def letter(art_bytes, spec, ctx, layer=None):
    """The room's lettering drawn over the art: the same drawing, the script's exact words."""
    from PIL import Image
    art = Image.open(io.BytesIO(art_bytes)).convert("RGBA")
    layer = layer or overlay(art_bytes, spec, ctx)[1]
    out = Image.alpha_composite(art, Image.open(io.BytesIO(layer)).convert("RGBA").resize(art.size))
    buf = io.BytesIO()
    out.convert("RGB").save(buf, "PNG")
    return buf.getvalue()


def sfx_words(spec, ctx):
    """The sound effects this page's art draws in, as text for the art check - "" when the art
    carries no text (no sound effects, or the book letters them on the layer)."""
    if ctx.get("lettering") != "layer" or not prompts.sfx_in_art(ctx):
        return ""
    return ", ".join(f'"{" ".join(str(i.get("text", "")).split()).upper()}"'
                     for i in spec.get("items") or [] if i.get("type") == "sfx" and i.get("text"))


def page(slug, tag, spec, ctx, key):
    """Draw the art - with its sound effects drawn in, unless the book letters those on the
    layer - then place the balloons on the drawn page (place_lettering) and letter it."""
    n = spec["page"]
    refs = references(slug, tag, spec, ctx)
    sfx = sfx_words(spec, ctx)
    _update(slug, tag, n, state="drawing", stage="drawing", attempt=1, refs=[str(p.name) for _, p in refs],
            started=time.time())
    try:
        art, report, cost = artcheck.draw_checked(lambda text, r: generate(MODELS[tag], text, r, key),
                                                  prompt_for(spec, ctx, refs), refs, key, lettered=sfx or False,
                                                  stage=stager(slug, tag, n))
        d = folder(slug, tag, "art")
        d.mkdir(parents=True, exist_ok=True)
        (d / f"p{n:02d}.png").write_bytes(art)
        _update(slug, tag, n, cost=cost, error=None, sfx_art=bool(sfx),
                check={"pass": report["pass"], "problems": report["problems"], "tries": len(report["attempts"])})
        after_drawing(slug, tag, n, redo=True)
        seconds = round(time.time() - _page_started(slug, tag, n))
        _update(slug, tag, n, state="done", stage=None, seconds=seconds)
        usage.ledger(slug, "renderer", "page", MODELS[tag], cost, seconds, page=n,
                     tries=len(report["attempts"]), check_pass=report["pass"],
                     problems=[p.get("what", "")[:120] for p in report["problems"]])
    except Exception as e:      # noqa: BLE001 - one page failing never stops the book
        _update(slug, tag, n, state="failed", error=str(e)[:400])
        usage.ledger(slug, "renderer", "page", MODELS[tag], None, None, page=n, error=str(e)[:300])


def stager(slug, tag, n):
    """A draw_checked stage callback that records where page n's drawing is, for the progress shown."""
    return lambda name, attempt: _update(slug, tag, n, stage=name, attempt=attempt)


def after_drawing(slug, tag, n, redo=False):
    """A page was just drawn: place its balloons and tails on the drawing, then letter it.
    Never fails the drawing - a page that can't be placed is lettered where the layout says."""
    _update(slug, tag, n, stage="placing")
    try:
        place_lettering(slug, tag, [n], redo=redo)
    except Exception:      # noqa: BLE001
        pass
    _update(slug, tag, n, stage="lettering")
    try:
        letter_pages(slug, tag, [n])
    except Exception:      # noqa: BLE001
        pass


def letter_pages(slug, tag, pages=None):
    """The second step: the current text layer composited over the drawn art, one lettered PNG
    per page. Only pages whose art exists are lettered; returns {page: "ok" | why not}.
    A page whose art carries its sound effects gets only its balloons and captions."""
    drawn_sfx = {k for k, v in status(slug)["models"].get(tag, {}).get("pages", {}).items() if v.get("sfx_art")}
    ctx = prompts.context(slug)
    specs = {s["page"]: s for s in book(slug)}
    art_dir = folder(slug, tag, "art")
    out_dir = folder(slug, tag, "lettered")
    ov_dir = folder(slug, tag, "overlay")
    results = {}
    for n in sorted(int(p) for p in (pages or specs)):
        src = art_dir / f"p{n:02d}.png"
        if n not in specs:
            results[n] = "no layout"
        elif not src.is_file():
            results[n] = "art not drawn yet"
        else:
            try:
                out_dir.mkdir(parents=True, exist_ok=True)
                ov_dir.mkdir(parents=True, exist_ok=True)
                art = src.read_bytes()
                svg, layer = overlay(art, specs[n], {**ctx, "skip_sfx": str(n) in drawn_sfx})
                (ov_dir / f"p{n:02d}.svg").write_text(svg)     # the three files of a finished page:
                (ov_dir / f"p{n:02d}.png").write_bytes(layer)  # art/, overlay/ and lettered/
                (out_dir / f"p{n:02d}.png").write_bytes(letter(art, specs[n], ctx, layer))
                results[n] = "ok"
            except Exception as e:      # noqa: BLE001
                results[n] = str(e)[:200]
    return results


def _page_started(slug, tag, n):
    return status(slug)["models"].get(tag, {}).get("pages", {}).get(str(n), {}).get("started") or time.time()


# ---- what the book needs drawn ------------------------------------------------------------------

def needs(slug, props=()):
    """Every character, place and prop the laid-out book draws, with the pages it is on - what
    has to have a reference before rendering. Characters by their canon names ("ALEX" is Alex
    Phantum); a prop is on a page whose panels or script name it (or its last word, "chip").
    With no layouts yet, the canon's characters, on no pages."""
    specs = book(slug)
    ctx = prompts.context(slug)
    script = projects.read_artifact(slug, "script.md") or ""
    chars, places, found = {}, {}, {p: [] for p in props if p.strip()}
    for s in specs:
        n = s["page"]
        names, where, described = prompts.page_cast(s, ctx)
        for name in names:
            chars.setdefault(full_name(name, ctx["bible"]), []).append(n)
        for place in where:
            places.setdefault(place, []).append(n)
        m = re.search(rf"^##\s*Page\s+{n}\b.*?(?=^##\s*Page\s+\d+|\Z)", script, re.M | re.S | re.I)
        text = (described + " " + (m.group(0) if m else "")).lower()
        for prop in found:
            words = [w for w in re.findall(r"[a-z0-9']+", prop.lower()) if len(w) > 3]
            if prop.lower() in text or (words and re.search(rf"\b{re.escape(words[-1])}\b", text)):
                found[prop].append(n)
    if not specs:
        chars = {e: [] for e in prompts.character_entries(ctx["bible"])}
    row = lambda d: [{"name": k, "pages": sorted(set(v))} for k, v in sorted(d.items(), key=lambda kv: (-len(set(kv[1])), kv[0]))]
    return {"source": "layouts" if specs else "canon", "pages": len(specs),
            "characters": row(chars), "places": row(places), "props": row(found)}


# ---- the book --------------------------------------------------------------------------------

def book(slug):
    specs, _ = thumbnails.parse_layouts(projects.read_artifact(slug, "layouts.md"))
    return sorted(specs, key=lambda s: s["page"])


def start(slug, tags=None, pages=None, redo=False):
    """Draw the book with each model, in the background. Pages already drawn are kept unless redo."""
    key = api_key()
    if not key:
        raise ValueError("no OpenRouter key: save one in the room's model settings")
    specs = [s for s in book(slug) if not pages or s["page"] in pages]
    if not specs:
        raise ValueError("layouts.md has no pages yet - lay the book out first")
    ctx = {**prompts.context(slug), "slug": slug, "lettering": "layer"}
    started = []
    for tag in tags or list(MODELS):
        if tag not in MODELS:
            raise ValueError(f"no model {tag!r}: {', '.join(MODELS)}")
        with _lock:
            if _threads.get((slug, tag)) and _threads[(slug, tag)].is_alive():
                continue
        todo = [s for s in specs if redo or not (folder(slug, tag, "art") / f"p{s['page']:02d}.png").exists()]
        _update(slug, tag, state="running", total=len(todo), started=time.time(), finished=None)

        def run(tag=tag, todo=todo):
            with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
                list(pool.map(lambda s: page(slug, tag, s, ctx, key), todo))
            _update(slug, tag, state="done", finished=time.time())

        t = threading.Thread(target=run, daemon=True)
        with _lock:
            _threads[(slug, tag)] = t
        t.start()
        started.append(tag)
    return {"started": started, "pages": [s["page"] for s in specs], **status(slug)}


# ---- where the balloons go: placed on the drawn page ------------------------------------------

PLACE_MODEL = artcheck.CONFIRM_MODEL     # Opus: placing balloons is judging space, faces and gaze
PLACE_ASK = """This is one drawn page of a graphic novel, with no balloons or captions on it yet. A letterer
will add the ones below. Place each one the way a good comic letterer would.

The panels, as fractions of the WHOLE PAGE (x from 0 at the left edge to 1 at the right; y from 0 at
the top to 1 at the bottom):
{panels}

For each item give "spot": the centre of where it should sit, inside its own panel, as page fractions.
Its size is given: the whole box must fit inside the panel. Put it in calm space - sky, wall, shadow,
floor - near its speaker, never over a face, a hand, or the thing the panel is about. In each panel,
the line read first sits higher and further left. A caption goes against a panel corner or edge.
For each speech balloon also give "speaker": where the speaker's mouth is (or their head, if the
mouth isn't visible), as page fractions; or "offpanel": true if they aren't drawn in that panel.

{lines}

Reply with ONLY JSON: {{"items": [{{"item": <number>, "spot": [x, y], "speaker": [x, y]}} or {{"item": <number>, "spot": [x, y], "offpanel": true}}]}}"""

TAILED = ("balloon", "whisper", "shout", "thought")
PLACED = TAILED + ("caption", "screen", "sign", "headline")     # the location header always sits top-left


def place_lettering(slug, tag, pages=None, redo=False):
    """One look at each drawn page places its balloons and captions in the drawing's calm space
    and points each tail at its speaker. Written into layouts.md as x/y and tail_x/tail_y
    (percent of the panel), so lettering again costs nothing and the editor can still move them.
    redo=False leaves items already placed. {page: result}."""
    key = api_key()
    specs = {s["page"]: s for s in book(slug)}
    todo = sorted(int(p) for p in (pages or specs))
    ctx = prompts.context(slug)

    def one(n):
        spec, art = specs.get(n), folder(slug, tag, "art") / f"p{n:02d}.png"
        if not spec or not art.is_file():
            return n, "no art"
        want = [i for i in lettering.items(spec) if i["type"] in PLACED and (redo or "x" not in i)]
        if not want:
            return n, "nothing to place"
        rects = lettering.detect_rects(spec, art.read_bytes()) or lettering.panel_rects(spec)
        _, boxes, _ = lettering.layer(spec, ctx, rects)
        f = lambda v: f"{v:.2f}"
        panels = "\n".join(f"- panel {k}: x {f(r[0])} to {f(r[0] + r[2])}, y {f(r[1])} to {f(r[1] + r[3])}" for k, r in sorted(rects.items()))
        lines = []
        for i in want:
            b = boxes.get(i["i"])
            size = f", size {f(b[2] - b[0])} wide x {f(b[3] - b[1])} tall" if b else ""
            who = f' {i["speaker"]}' if i.get("speaker") and i["type"] in TAILED else ""
            lines.append(f'- item {i["i"]}: {i["type"]}{who}, panel {i.get("panel")}{size}: "{i.get("text", "")[:120]}"')
        t0 = time.time()
        answer, cost = artcheck._ask([{"type": "text", "text": PLACE_ASK.format(panels=panels, lines="\n".join(lines))},
                                      {"type": "image_url", "image_url": {"url": data_url(art)}}], key, PLACE_MODEL)
        usage.ledger(slug, "letterer", "place", PLACE_MODEL, cost, time.time() - t0, page=n)
        found = {int(r["item"]): r for r in ((artcheck._json(answer) or {}).get("items") or [])
                 if isinstance(r, dict) and str(r.get("item", "")).isdigit()}
        changes = {}
        for i in want:
            r = found.get(i["i"])
            x0, y0, w, h = rects.get(i.get("panel"), (0, 0, 1, 1))
            pct = lambda pt: (round((float(pt[0]) - x0) / w * 100, 1), round((float(pt[1]) - y0) / h * 100, 1))
            c = {}
            try:
                if r and isinstance(r.get("spot"), list) and len(r["spot"]) == 2:
                    c["x"], c["y"] = pct(r["spot"])
                if r and i["type"] in TAILED and i.get("speaker") and i.get("tail") != "none" and not r.get("offpanel") \
                        and isinstance(r.get("speaker"), list) and len(r["speaker"]) == 2:
                    c["tail_x"], c["tail_y"] = pct(r["speaker"])
            except (TypeError, ValueError):
                continue
            if c:
                changes[i["i"]] = c
        if changes:
            with _write_lock:      # every page's pass rewrites the one layouts.md
                lettering.set_items(slug, n, changes)
        return n, f"{len(changes)} of {len(want)} placed"

    out = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for n, r in pool.map(lambda n: _safe(one, n), todo):
            out[n] = r
    return out


def place_tails(slug, tag, pages=None, redo=False):
    """Kept for callers of the old pass: placing the lettering points the tails too."""
    return place_lettering(slug, tag, pages, redo)


_lock_tails = threading.Lock()     # one pass at a time
_write_lock = threading.Lock()     # one layouts.md write at a time


def _safe(fn, n):
    try:
        return fn(n)
    except Exception as e:      # noqa: BLE001 - one page failing never stops the book
        return n, f"failed: {str(e)[:200]}"
