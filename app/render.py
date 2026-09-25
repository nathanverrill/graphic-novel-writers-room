"""The renderer: every page of the book drawn by each image model, then lettered by the room.

For each model and each page of layouts.md:

    art        the page packet's prompt (no text on the page), sent with reference images:
               the style plate (the book's look), the model's own lock of every character on
               the page, and - for a key page - the key page's art, to be close to it
    lettered   the room's lettering layer (lettering.py) drawn over that same art, so the words
               are exactly the script's and art and lettered are the same drawing

    campaigns/<slug>/renders/<model>/art/p01.png
    campaigns/<slug>/renders/<model>/lettered/p01.png
    campaigns/<slug>/renders/status.json      page by page: done, failed, how long, what it cost

A character's lock for a model is its Sheets subject "<name>-<model>" (alex-phantum-gemini),
kept there by the showrunner; the plate is Sheets' style plate. A page is drawn once; drawing
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

from . import keypages, keys, lettering, projects, prompts, thumbnails
from .draftedit import SHEETS_DIR

MODELS = {"gemini": "google/gemini-3.1-flash-image", "sunburst": "openai/gpt-image-2.5-sunburst"}
OPENROUTER = "https://openrouter.ai/api/v1"
MAX_REFS = 4            # the plate, then the page's key art, then locks - what the models take well
WORKERS = 3             # pages at a time, per model
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

def plate():
    found = sorted((SHEETS_DIR / "_style").glob("plate.*")) if (SHEETS_DIR / "_style").is_dir() else []
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


def lock_for(name, tag, bible=""):
    """The model's kept lock of a character: the Sheets subject whose name, less "-<model>",
    is in the character's full name (cassian-lock-gemini for DIRECTOR CASSIAN LOCK)."""
    words = set(re.findall(r"[a-z0-9]+", full_name(name, bible).lower()))
    best = None
    for d in SHEETS_DIR.glob(f"*-{tag}") if SHEETS_DIR.is_dir() else []:
        stem = set(re.findall(r"[a-z0-9]+", d.name[:-len(tag) - 1]))
        locks = [p for p in d.glob("lock.*") if p.suffix.lower() in MIME]
        if stem and stem <= words and locks and (best is None or len(stem) > best[0]):
            best = (len(stem), locks[0])
    return best[1] if best else None


def references(slug, tag, spec, ctx):
    """[(label, path)]: what this page is drawn from, most important first."""
    out = []
    if plate():
        out.append(("the style plate - draw in exactly this style", plate()))
    key = keypages.of(slug, spec.get("page"))
    if key and key["art"]:
        out.append((f"this page as drawn before - stay close to its composition", key["art"]))
    names, _, _ = prompts.page_cast(spec, ctx)
    for n in names:
        lock = lock_for(n, tag, ctx.get("bible"))
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


def letter(art_bytes, spec, ctx):
    """The room's lettering drawn over the art: the same drawing, the script's exact words."""
    import cairosvg
    from PIL import Image
    art = Image.open(io.BytesIO(art_bytes)).convert("RGBA")
    layer = cairosvg.svg2png(bytestring=lettering.svg(spec, ctx).encode(), output_width=art.width, output_height=art.height)
    out = Image.alpha_composite(art, Image.open(io.BytesIO(layer)).convert("RGBA").resize(art.size))
    buf = io.BytesIO()
    out.convert("RGB").save(buf, "PNG")
    return buf.getvalue()


def page(slug, tag, spec, ctx, key):
    n = spec["page"]
    refs = references(slug, tag, spec, ctx)
    _update(slug, tag, n, state="drawing", refs=[str(p.name) for _, p in refs], started=time.time())
    try:
        art, cost = generate(MODELS[tag], prompt_for(spec, ctx, refs), refs, key)
        for kind, data in (("art", art), ("lettered", letter(art, spec, ctx))):
            d = folder(slug, tag, kind)
            d.mkdir(parents=True, exist_ok=True)
            (d / f"p{n:02d}.png").write_bytes(data)
        _update(slug, tag, n, state="done", cost=cost, seconds=round(time.time() - _page_started(slug, tag, n)), error=None)
    except Exception as e:      # noqa: BLE001 - one page failing never stops the book
        _update(slug, tag, n, state="failed", error=str(e)[:400])


def _page_started(slug, tag, n):
    return status(slug)["models"].get(tag, {}).get("pages", {}).get(str(n), {}).get("started") or time.time()


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
