"""The studio (/studio): every book on one shelf, and one book at a time in four modes -
create, run, pages, versions - with the room's machinery out of sight.

    create    one chat box; anything in it can be saved as material (input/), research
              (references/) or a character's art lock (style/locks/<name>-sunburst/, drawn by
              Sunburst from the words, or a dropped image as it is)
    run       one button with a budget: intake (taking the suggested answers), production, a
              preview page as early as the book allows, then every page drawn in order. A bar,
              an ETA, the dollars spent, and a stop that keeps whatever is finished
    pages     the book as pages: drawn where drawn, the script set as a page where not
    versions  a named copy of the book's words and pages, to compare and to bring back

It calls what the room already does - room rounds, open items, magic, render.page - and keeps
its own state under campaigns/<slug>/studio/:

    chat.json            the conversation
    run.json             the last run: budget, steps, spent, status
    versions/<id>/       saved versions (meta.json beside a copy of the files)
"""
import base64
import concurrent.futures
import json
import re
import shutil
import threading
import time

from . import artcheck, magic, openitems, phases, projects, render, review, riff, room, storydesk, usage
from .agents import load_roles

TAG = "sunburst"
COST_PAGE = 0.40            # a drawn page, art check and redraws included
PREVIEW_PAGE = 1
DRAW_WORKERS = 4            # pages at a time: few enough that they arrive roughly in order
MAX_INTAKE_ROUNDS = 5
KINDS = {"material": projects.INPUT, "research": projects.REFERENCES, "rule": projects.RULES}
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp")

_threads = {}
_stops = set()
_lock = threading.Lock()


def _dir(slug):
    d = projects.campaign_dir(slug) / "studio"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _load(slug, name, default):
    p = _dir(slug) / name
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return default


def _save(slug, name, data):
    p = _dir(slug) / name
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=1))
    tmp.replace(p)


# ---- the shelf -------------------------------------------------------------------------------

def title(slug):
    head = (projects.pitch(slug) or "").splitlines()[:1]
    t = re.sub(r"^#\s*", "", head[0]).strip() if head else ""
    return t or slug.replace("-", " ").title()


def _art(slug, kind, n):
    return render.folder(slug, TAG, kind) / f"p{n:02d}.png"


def running(slug):
    t = _threads.get(slug)
    return bool(t and t.is_alive()) or magic.state(slug)["active"] or bool(room.active_run(slug)) \
        or bool(render._threads.get((slug, TAG)) and render._threads[(slug, TAG)].is_alive())


def mode(slug):
    """Which view a book opens in: run while anything works on it, pages once there is a
    script or art, create before that."""
    if running(slug):
        return "run"
    if (projects.read_artifact(slug, "script.md") or "").strip() or any(render.folder(slug, TAG, "art").glob("p*.png")):
        return "pages"
    return "create"


def _spent_by_project():
    out = {}
    for r in usage.read_ledger():
        if isinstance(r.get("cost_usd"), (int, float)):
            out[r["project"]] = out.get(r["project"], 0) + r["cost_usd"]
    return out


def books():
    spent = _spent_by_project()
    out = []
    for slug in projects.list_projects():
        let, art = render.folder(slug, TAG, "lettered"), render.folder(slug, TAG, "art")
        drawn = sorted(art.glob("p*.png"))
        cover = next((p for p in (let / "p01.png", art / "p01.png") if p.is_file()), None) \
            or (drawn[0] if drawn else None)
        d = projects.campaign_dir(slug)
        out.append({"slug": slug, "title": title(slug), "mode": mode(slug),
                    "drawn": len(drawn), "pages": len(render.book(slug)),
                    "cover": cover and f"/api/studio/{slug}/page/{cover.name}?kind={cover.parent.name}",
                    "spent": round(spent.get(slug, 0), 2),
                    "updated": max((p.stat().st_mtime for p in d.glob("*/*") if p.is_file()), default=0)})
    return sorted(out, key=lambda b: -b["updated"])


# ---- create: the chat, and what is saved from it ----------------------------------------------

CHAT_SYSTEM = """You are the creative partner of the showrunner of {title}, a graphic novel in the making.
The showrunner pastes and drops material in here and works it up with you, the way they would in any
chat: ideas, characters, the world, research, scenes. Their saved material, rules and character looks are above.

Be concrete and specific to this book. Keep replies tight: short paragraphs, plain words, no filler.
When asked to write or rewrite something, write the finished text itself, ready to save, not a
description of it. When asked for a character's look, write it as one paragraph an artist could draw
from: age, build, skin, face, hair, clothes and colors, signature details. Rules are binding: never
contradict them. Research is about the real world: keep it factual and say where you are unsure."""


def files(slug):
    out = []
    base = projects.campaign_dir(slug)
    for kind, sub in KINDS.items():
        d = base / sub
        for p in sorted(d.glob("*")) if d.is_dir() else []:
            if p.is_file() and not p.name.startswith("."):
                out.append({"kind": kind, "path": f"{sub}/{p.name}", "name": p.name, "size": p.stat().st_size,
                            "image": p.suffix.lower() in IMAGE_SUFFIXES})
    return out


def _path(slug, rel):
    sub, _, name = (rel or "").partition("/")
    if sub not in KINDS.values() or not name or "/" in name or name.startswith("."):
        raise ValueError("not a material, research or lock file")
    return projects.campaign_dir(slug) / sub / name


def read_file(slug, rel):
    p = _path(slug, rel)
    if not p.is_file():
        raise FileNotFoundError(rel)
    return p


def _context(slug, cap=150_000):
    """The saved material, research and locks, newest last, cut to fit."""
    parts = []
    for f in files(slug):
        if f["image"]:
            continue
        try:
            text = read_file(slug, f["path"]).read_text(errors="replace")
        except OSError:
            continue
        label = {"material": "MATERIAL", "research": "RESEARCH", "rule": "RULE (binding)"}[f["kind"]]
        parts.append(f"## {label}: {f['path']}\n\n{text[:40_000]}")
    for lk in locks(slug):
        if lk["look"]:
            parts.append(f"## CHARACTER LOOK (art lock): {lk['name']}\n\n{lk['look']}")
    text = "\n\n".join(parts) or "(nothing saved yet)"
    return "# THE BOOK SO FAR\n\n" + text[-cap:]


def chat_history(slug):
    return _load(slug, "chat.json", [])


def say(slug, text):
    text = (text or "").strip()
    if not text:
        raise ValueError("say something")
    key = riff._key()
    hist = chat_history(slug)
    hist.append({"role": "user", "content": text[:60_000], "t": time.time()})
    msgs = [{"role": m["role"], "content": m["content"][:20_000]} for m in hist[-30:]]
    system = [{"type": "text", "text": _context(slug), "cache_control": {"type": "ephemeral"}},
              {"type": "text", "text": CHAT_SYSTEM.format(title=title(slug))}]
    t0 = time.time()
    reply, cost = riff._ask([{"role": "system", "content": system}] + msgs, key, max_tokens=8000)
    usage.ledger(slug, "studio", "chat", riff.MODEL, cost, time.time() - t0)
    hist.append({"role": "assistant", "content": reply, "t": time.time(), "cost": cost})
    _save(slug, "chat.json", hist)
    return {"messages": hist, "cost": cost}


def clear_chat(slug):
    hist = chat_history(slug)
    if hist:
        (_dir(slug) / f"chat-{time.strftime('%Y%m%d-%H%M%S')}.json").write_text(json.dumps(hist, indent=1))
    _save(slug, "chat.json", [])
    return {"messages": []}


def _free_name(d, name, suffix):
    stem = re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")[:60] or "untitled"
    p = d / f"{stem}{suffix}"
    i = 2
    while p.exists():
        p = d / f"{stem}-{i}{suffix}"
        i += 1
    return p


def save_text(slug, kind, name, text):
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {', '.join(KINDS)}")
    text = (text or "").strip()
    if not text:
        raise ValueError("nothing to save")
    d = projects.campaign_dir(slug) / KINDS[kind]
    d.mkdir(exist_ok=True)
    p = _free_name(d, name, ".md")
    p.write_text(text + "\n")
    return {"path": f"{KINDS[kind]}/{p.name}", "files": files(slug)}


def save_image(slug, kind, name, data):
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {', '.join(KINDS)}")
    suffix = "." + (name.rsplit(".", 1)[-1].lower() if "." in name else "png")
    if suffix not in IMAGE_SUFFIXES:
        raise ValueError("images must be png, jpg or webp")
    raw = base64.b64decode(data.split(",", 1)[-1])
    if len(raw) > 15_000_000:
        raise ValueError("that image is over 15 MB")
    d = projects.campaign_dir(slug) / KINDS[kind]
    d.mkdir(exist_ok=True)
    p = _free_name(d, name.rsplit(".", 1)[0], suffix)
    p.write_bytes(raw)
    return {"path": f"{KINDS[kind]}/{p.name}", "files": files(slug)}


def remove_file(slug, rel):
    """Moved aside, never deleted: campaigns/<slug>/studio/removed/<time>-<name>."""
    p = read_file(slug, rel)
    to = _dir(slug) / "removed"
    to.mkdir(exist_ok=True)
    shutil.move(str(p), to / f"{time.strftime('%Y%m%d-%H%M%S')}-{p.parent.name}-{p.name}")
    return {"files": files(slug)}


# ---- character art locks -------------------------------------------------------------------

LOCKS_DIR = "style/locks"
_lock_jobs = {}


def _lock_dir(slug, name):
    stem = projects.slugify(name)
    if not stem:
        raise ValueError("give the character a name")
    return projects.campaign_dir(slug) / LOCKS_DIR / f"{stem}-{TAG}"


def locks(slug):
    """Every character drawn with Sunburst: the lock, the newest candidate waiting, the words."""
    out = []
    for d in storydesk._lock_dirs(slug):
        if not d.name.endswith(f"-{TAG}"):
            continue
        img = storydesk._img(d)
        cands = sorted((d / "candidates").glob("cand-*.png"), key=lambda p: p.stat().st_mtime) if (d / "candidates").is_dir() else []
        look = (d / "look.md").read_text().strip() if (d / "look.md").is_file() else ""
        if not img and not cands and not look:
            continue
        name = (d / "name.txt").read_text().strip() if (d / "name.txt").is_file() else d.name[:-len(TAG) - 1].replace("-", " ").title()
        out.append({"folder": d.name, "name": name, "look": look,
                    "image": img.name if img else None, "version": int(img.stat().st_mtime) if img else 0,
                    "candidate": cands[-1].name if cands else None,
                    "job": _lock_jobs.get((slug, d.name))})
    return out


def save_lock(slug, name, look=None, data=None, draw=True):
    """A character's lock: an image as it is, or words that Sunburst draws from. The words are
    also saved as material (input/<name>-look.md), so the room writes the character to match."""
    name = (name or "").strip()[:60]
    if draw and not data and (look or "").strip() and not render.api_key():
        raise ValueError("no OpenRouter key: add one in the room, or save the words without drawing")
    d = _lock_dir(slug, name)
    d.mkdir(parents=True, exist_ok=True)
    (d / "name.txt").write_text(name + "\n")
    if data:
        raw = base64.b64decode(data.split(",", 1)[-1])
        if len(raw) > 15_000_000:
            raise ValueError("that image is over 15 MB")
        old = storydesk._img(d)
        if old:
            (d / "previous").mkdir(exist_ok=True)
            old.rename(d / "previous" / f"lock-{time.strftime('%Y%m%d-%H%M%S')}{old.suffix}")
        (d / "lock.png").write_bytes(raw)
    if (look or "").strip():
        (d / "look.md").write_text(look.strip() + "\n")
        mat = projects.campaign_dir(slug) / projects.INPUT
        mat.mkdir(exist_ok=True)
        (mat / f"{d.name[:-len(TAG) - 1]}-look.md").write_text(f"# {name}: look\n\n{look.strip()}\n")
        if draw and not data:
            redraw_lock(slug, d.name)
    return {"locks": locks(slug), "files": files(slug)}


def redraw_lock(slug, folder, note=""):
    """Sunburst draws the character from their words, art-checked. The first drawing becomes the
    lock; after that each one waits as a candidate to keep or discard."""
    key = render.api_key()
    if not key:
        raise ValueError("no OpenRouter key")
    d = projects.campaign_dir(slug) / LOCKS_DIR / storydesk._safe(folder)
    look = (d / "look.md").read_text().strip() if (d / "look.md").is_file() else ""
    if not look:
        raise ValueError("this character has no words to draw from: save a look for them first")
    jk = (slug, d.name)
    if (_lock_jobs.get(jk) or {}).get("state") == "running":
        return _lock_jobs[jk]
    name = (d / "name.txt").read_text().strip() if (d / "name.txt").is_file() else folder
    refs = []
    plate = render.plate(slug)
    if plate:
        refs.append(("the style plate - draw in exactly this style", plate))
    old = storydesk._img(d)
    if old:
        refs.append((f"{name}'s current lock - keep everything the words do not change", old))
    prompt = storydesk.REDRAW_PROMPT.format(
        name=name, look=re.sub(r"\*\*", "", look),
        old="The second attached image is the current lock: keep the same person, and change only what the "
            "description above says differently.\n" if old and plate else "",
        note=f"Note for this drawing: {note.strip()}\n" if (note or "").strip() else "")
    if refs:
        prompt += "\nThe attached images, in order: " + "; ".join(f"{i}. {w}" for i, (w, _) in enumerate(refs, 1))
    _lock_jobs[jk] = {"state": "running", "started": time.time()}

    def work():
        try:
            t0 = time.time()
            art, report, cost = artcheck.draw_checked(
                lambda text, r: render.generate(render.MODELS[TAG], text, r, key), prompt, refs, key,
                script=f"A character lock: one full-body figure of {name}, no text.\n\nLook: {look}", lettered=False)
            usage.ledger(slug, "studio", "lock", render.MODELS[TAG], cost, time.time() - t0,
                         character=name, tries=len(report["attempts"]), check_pass=report["pass"])
            if storydesk._img(d):
                (d / "candidates").mkdir(parents=True, exist_ok=True)
                (d / "candidates" / f"cand-{time.strftime('%Y%m%d-%H%M%S')}.png").write_bytes(art)
            else:
                (d / "lock.png").write_bytes(art)
            _lock_jobs[jk] = {"state": "done", "cost": cost}
        except Exception as e:      # noqa: BLE001 - shown beside the lock
            _lock_jobs[jk] = {"state": "failed", "error": str(e)[:300]}
    threading.Thread(target=work, daemon=True).start()
    return _lock_jobs[jk]


def keep_lock(slug, folder, file):
    storydesk.keep(slug, folder, file)
    return {"locks": locks(slug)}


def discard_lock(slug, folder, file):
    storydesk.discard(slug, folder, file)
    return {"locks": locks(slug)}


# ---- run: the whole book, under a budget --------------------------------------------------------

STEPS = [("intake", "Reading your material"), ("development", "Planning the book"),
         ("audition", "Two writers try the opening"), ("preview", "Drawing a preview page"),
         ("writing", "Writing the script"), ("coldread", "Test readers read it"),
         ("analysis", "Checking it works"), ("execution", "Laying out the pages"),
         ("drawing", "Drawing the pages")]
TITLES = dict(STEPS)


def run_state(slug):
    st = _load(slug, "run.json", {"status": "idle"})
    if st.get("status") == "running" and not (_threads.get(slug) and _threads[slug].is_alive()):
        st.update(status="stopped", error="The app restarted during the run. Run again to go on.")
        _save(slug, "run.json", st)
    st["spent"] = round(_spent_since(slug, st.get("started_iso")), 2) if st.get("started_iso") else 0
    now = time.time()
    total = sum(s["est"] for s in st.get("steps", []))
    done = 0
    for s in st.get("steps", []):
        if s.get("end"):
            done += s["est"]
        elif s.get("start"):
            done += min(now - s["start"], s["est"] * 0.95)
    st["progress"] = round(done / total, 3) if total else 0
    st["eta"] = round(max(0, total - done)) if st.get("status") == "running" else 0
    return st


def _set(slug, **changes):
    with _lock:
        st = _load(slug, "run.json", {})
        st.update(changes)
        _save(slug, "run.json", st)
        return st


def _step(slug, sid, **changes):
    with _lock:
        st = _load(slug, "run.json", {})
        for s in st.get("steps", []):
            if s["id"] == sid:
                s.update(changes)
        if changes.get("start"):
            st["step"] = sid
        _save(slug, "run.json", st)


def _spent_since(slug, iso):
    return sum(r["cost_usd"] for r in usage.read_ledger(slug)
               if isinstance(r.get("cost_usd"), (int, float)) and (r.get("time") or "") >= iso)


def _estimates(slug, steps):
    roles = {r.id: r for r in load_roles()}
    plan = {p["step"]: p["seconds"] for p in magic.plan(slug)}
    intake_s = room.estimates([roles["script_coordinator"]]).get("script_coordinator", 600) if "script_coordinator" in roles else 600
    pages = review.settings(slug).get("pages") or len(render.book(slug)) or 24
    est = {"intake": intake_s * 3, "development": plan.get("development", 600),
           "audition": plan.get("audition", 600), "preview": plan.get("page1", 300) + 180,
           "writing": plan.get("writing", 600), "coldread": plan.get("coldread", 400) * 1.5,
           "analysis": plan.get("analysis", 0) * 1.5, "execution": plan.get("execution", 600),
           "drawing": -(-pages // DRAW_WORKERS) * 150}
    return [{"id": s, "title": TITLES[s], "est": max(30, int(est[s]))} for s in steps]


def where(slug):
    """Where a run picks up: the steps still to do."""
    approved = review.settings(slug).get("approved")
    m = magic.state(slug)
    if not approved:
        return [s for s, _ in STEPS]
    if m["status"] == "done":
        return ["drawing"]
    step = m["step"] if m["status"] in ("failed", "stopped") and m.get("step") else "development"
    order = ["development", "audition", "preview", "writing", "coldread", "analysis", "execution", "drawing"]
    step = {"page1": "preview", "drafts": "development", "layouts": "execution", "final": "execution"}.get(step, step)
    if step not in order:
        step = "development"
    return order[order.index(step):]


def start_run(slug, budget, fresh=False):
    if budget is None or budget <= 0:
        raise ValueError("set a budget above $0")
    if running(slug):
        raise RuntimeError("this book is already being worked on")
    render.api_key() or riff._key()
    steps = where(slug)
    if fresh and "intake" not in steps:
        steps = ["development", "audition", "preview", "writing", "coldread", "analysis", "execution", "drawing"]
    _stops.discard(slug)
    _save(slug, "run.json", {"status": "running", "budget": float(budget), "started": time.time(),
                             "started_iso": time.strftime("%Y-%m-%dT%H:%M:%S"), "finished": None,
                             "error": None, "step": steps[0], "steps": _estimates(slug, steps),
                             "preview": None, "log": []})
    t = threading.Thread(target=_run, args=(slug, steps), daemon=True)
    _threads[slug] = t
    t.start()
    threading.Thread(target=_watch, args=(slug,), daemon=True).start()
    return run_state(slug)


def stop_run(slug, why="Stopped. Everything finished so far is kept."):
    _stops.add(slug)
    _set(slug, stopping=why)
    if magic.state(slug)["active"]:
        magic.stop(slug)
    run = room.active_run(slug)
    if run:
        run.stop_requested = True
        with run.cond:
            run.cond.notify_all()
    return run_state(slug)


def _log(slug, text):
    with _lock:
        st = _load(slug, "run.json", {})
        st.setdefault("log", []).append({"t": time.time(), "text": text})
        _save(slug, "run.json", st)


class Stopped(Exception):
    pass


def _check(slug):
    if slug in _stops:
        raise Stopped()


def _watch(slug):
    """The budget: stop before the next piece of work would go over it."""
    while _threads.get(slug) and _threads[slug].is_alive():
        st = run_state(slug)
        margin = COST_PAGE * DRAW_WORKERS if st.get("step") == "drawing" else 1.0
        if st["spent"] + margin >= st["budget"] and slug not in _stops:
            stop_run(slug, f"Stopped at ${st['spent']:.2f} of the ${st['budget']:.2f} budget. Everything finished so far is kept.")
        time.sleep(5)


def _run(slug, steps):
    try:
        for sid in steps:
            _check(slug)
            _step(slug, sid, start=time.time())
            {"intake": _intake, "development": _magic_to_page1, "audition": _audition, "preview": _preview,
             "writing": _magic_to_final, "coldread": _noop, "analysis": _noop, "execution": _noop,
             "drawing": _draw}[sid](slug, steps)
            _step(slug, sid, end=time.time())
        _set(slug, status="done", finished=time.time())
        _log(slug, "Done.")
    except Stopped:
        st = _load(slug, "run.json", {})
        _set(slug, status="stopped", finished=time.time(), error=st.get("stopping"))
    except Exception as e:      # noqa: BLE001 - the run must say what failed and end
        _set(slug, status="failed", finished=time.time(), error=f"{type(e).__name__}: {e}"[:400])


def _noop(slug, steps):
    pass


def _wait_round(slug, run):
    with run.cond:
        run.cond.wait_for(lambda: run.done)
    status = run.version.meta.get("status")
    if status == "stopped" or slug in _stops:
        raise Stopped()
    if status not in ("done", "awaiting_showrunner_decisions", "ready_for_review"):
        raise RuntimeError(f"intake round {run.version.id} ended with status {status!r}")


def _intake(slug, steps):
    """Intake until pre-production is ready, taking the room's suggested answer to every open
    item, then approve it. Every answer goes to rules/decisions.md as if typed on the desk."""
    if not projects.read_artifact(slug, "story.md", desk=projects.PRE):
        if not any(f["kind"] in ("material", "rule") for f in files(slug)):
            raise ValueError("there is no material yet: save something in Create first")
    for _ in range(MAX_INTAKE_ROUNDS):
        _check(slug)
        answered = 0
        for item in openitems.state(slug)["items"]:
            if item.get("answer") or item.get("status") == openitems.DEFERRED:
                continue
            opts = item.get("options") or []
            opt = next((o for o in opts if o.get("id") == item.get("suggested")), None) or (opts[0] if opts else None)
            if opt:
                openitems.answer(slug, item["n"], opt["text"].split(" (suggested", 1)[0].strip())
            else:
                openitems.note_on(slug, item["n"], "defer", "no options offered; left for development")
            answered += 1
        if answered:
            _log(slug, f"Took the suggested answer to {answered} open question{'s' if answered > 1 else ''}.")
            time.sleep(2)       # rounds are stamped to the second: answers must be older than the round
        ready = phases.readiness(slug)
        if ready["ready"]:
            break
        phases.go_to(slug, "intake")
        _wait_round(slug, room.start_round(slug))
    else:
        ready = phases.readiness(slug)
    if not ready["ready"]:
        raise RuntimeError(f"pre-production is not ready after {MAX_INTAKE_ROUNDS} rounds: {ready['why']}")
    phases.approve_preproduction(slug, phases.CONFIRM_WORD)
    _log(slug, "The plan is settled.")


def _wait_magic(slug, *ok):
    while magic.state(slug)["active"]:
        if slug in _stops:
            magic.stop(slug)
        time.sleep(3)
        st = magic.state(slug)
        cur = {"page1": "preview", "layouts": "execution", "final": "execution"}.get(st.get("step"), st.get("step"))
        for sid in ("development", "audition", "writing", "coldread", "analysis", "execution"):
            if sid == cur:
                _mark_through(slug, sid)
    st = magic.state(slug)
    if st["status"] == "stopped" or slug in _stops:
        raise Stopped()
    if st["status"] not in ok:
        raise RuntimeError(st.get("error") or f"production ended as {st['status']}")


def _mark_through(slug, sid):
    """The chain moved on to sid: every step before it is done, sid has started."""
    with _lock:
        st = _load(slug, "run.json", {})
        ids = [s["id"] for s in st.get("steps", [])]
        if sid not in ids:
            return
        for s in st["steps"][:ids.index(sid)]:
            s.setdefault("start", time.time())
            s.setdefault("end", time.time())
        cur = st["steps"][ids.index(sid)]
        cur.setdefault("start", time.time())
        st["step"] = sid
        _save(slug, "run.json", st)


def _magic_to_page1(slug, steps):
    magic.start(slug, "development", until="page1")
    _wait_magic(slug, "page1")


def _audition(slug, steps):
    """Only when a run picks up at the audition: development already ran with it."""
    st = magic.state(slug)
    if steps[0] == "audition" and st["status"] in ("failed", "stopped"):
        magic.start(slug, "audition", until="page1")
        _wait_magic(slug, "page1")


def _preview(slug, steps):
    """One finished page, as early as there is a layout for it."""
    if magic.state(slug).get("status") == "failed" and magic.state(slug).get("step") == "page1":
        magic.start(slug, "page1", until="page1")
        _wait_magic(slug, "page1")
    if any(s["page"] == PREVIEW_PAGE for s in render.book(slug)):
        _draw_pages(slug, [PREVIEW_PAGE], redo=True)
        _set(slug, preview=PREVIEW_PAGE)


def _magic_to_final(slug, steps):
    st = magic.state(slug)
    step = "writing"
    if steps and steps[0] in ("coldread", "analysis", "execution") and st["status"] in ("failed", "stopped"):
        step = st["step"] if st["step"] in magic.STEPS else steps[0]
    magic.start(slug, step, until="final")
    _wait_magic(slug, "done")


def _layouts_time(slug):
    p = projects.project_dir(slug) / "layouts.md"
    return p.stat().st_mtime if p.is_file() else 0


def _draw(slug, steps):
    if "writing" not in steps and "execution" in steps:
        _magic_to_final(slug, ["execution"])
    laid = _layouts_time(slug)
    todo = [s["page"] for s in render.book(slug)
            if not _art(slug, "art", s["page"]).is_file() or _art(slug, "art", s["page"]).stat().st_mtime < laid]
    if not todo:
        _log(slug, "Every page is already drawn.")
        return
    _draw_pages(slug, todo, redo=True)


def _draw_pages(slug, pages, redo=False):
    key = render.api_key()
    if not key:
        raise ValueError("no OpenRouter key")
    specs = {s["page"]: s for s in render.book(slug)}
    from . import prompts
    ctx = {**prompts.context(slug), "slug": slug, "lettering": "layer"}
    todo = [specs[n] for n in sorted(pages) if n in specs]
    render._update(slug, TAG, state="running", total=len(todo), started=time.time(), finished=None)
    render._threads[(slug, TAG)] = threading.current_thread()

    def one(spec):
        if slug in _stops:
            return
        render.page(slug, TAG, spec, ctx, key)
        try:
            render.letter_pages(slug, TAG, [spec["page"]])
        except Exception:       # noqa: BLE001 - an unlettered page still shows its art
            pass
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=DRAW_WORKERS) as pool:
            list(pool.map(one, todo))
    finally:
        render._update(slug, TAG, state="done", finished=time.time())
        render._threads.pop((slug, TAG), None)
    _check(slug)


# ---- pages ---------------------------------------------------------------------------------

def pages(slug):
    """The book page by page: art, lettering, the script text, and the art check."""
    checks = render.status(slug)["models"].get(TAG, {}).get("pages", {})
    script = projects.read_artifact(slug, "script.md") or ""
    texts = {}
    for m in re.finditer(r"^##\s+Page\s+(\d+)\b[^\n]*\n(.*?)(?=^##\s+Page\s+\d+|\Z)", script, re.M | re.S):
        texts[int(m.group(1))] = m.group(0).strip()
    nums = sorted(set(texts) | {s["page"] for s in render.book(slug)})
    out = []
    for n in nums:
        a, l = _art(slug, "art", n), _art(slug, "lettered", n)
        st = checks.get(str(n), {})
        out.append({"page": n, "script": texts.get(n, ""),
                    "art": int(a.stat().st_mtime) if a.is_file() else 0,
                    "lettered": int(l.stat().st_mtime) if l.is_file() else 0,
                    "state": st.get("state") or "", "problems": [p.get("what", "") for p in (st.get("check") or {}).get("problems") or []][:6]})
    return out


def state(slug):
    projects.project_dir(slug)
    return {"slug": slug, "title": title(slug), "mode": mode(slug), "running": running(slug),
            "files": files(slug), "locks": locks(slug), "run": run_state(slug), "next": [TITLES[s] for s in where(slug)],
            "pages": pages(slug), "settings": {"pages": review.settings(slug).get("pages")},
            "versions": versions(slug), "cost_page": COST_PAGE,
            "has_key": bool(render.api_key())}


def set_pages(slug, n):
    if n is not None and not 1 <= n <= 200:
        raise ValueError("pages must be 1-200")
    review.save_settings(slug, pages=n)
    return {"pages": n}


# ---- versions ------------------------------------------------------------------------------

SNAP_DIRS = (projects.INPUT, projects.REFERENCES, projects.RULES, projects.DRAFTS,
             f"renders/{TAG}/art", f"renders/{TAG}/lettered", "style/locks")
SNAP_FILES = (projects.PRE, projects.PROD)      # their top-level files, not their rounds


def versions(slug):
    d = _dir(slug) / "versions"
    out = []
    for p in sorted(d.iterdir(), reverse=True) if d.is_dir() else []:
        try:
            out.append(json.loads((p / "meta.json").read_text()))
        except (OSError, ValueError):
            continue
    return out


def save_version(slug, name, auto=False):
    name = (name or "").strip()[:80] or time.strftime("%b %d %H:%M")
    vid = time.strftime("%Y%m%d-%H%M%S") + "-" + (re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40] or "v")
    base, to = projects.campaign_dir(slug), _dir(slug) / "versions" / vid
    for sub in SNAP_DIRS:
        if (base / sub).is_dir():
            shutil.copytree(base / sub, to / sub, ignore=shutil.ignore_patterns(".*", "previous"))
    for sub in SNAP_FILES:
        for p in (base / sub).glob("*") if (base / sub).is_dir() else []:
            if p.is_file():
                (to / sub).mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, to / sub / p.name)
    drawn = len(list((to / f"renders/{TAG}/art").glob("p*.png"))) if (to / f"renders/{TAG}/art").is_dir() else 0
    meta = {"id": vid, "name": name, "t": time.time(), "auto": auto, "drawn": drawn,
            "pages": len(render.book(slug))}
    to.mkdir(parents=True, exist_ok=True)
    (to / "meta.json").write_text(json.dumps(meta, indent=1))
    return meta


def _version_dir(slug, vid):
    if not re.fullmatch(r"[0-9]{8}-[0-9]{6}-[a-z0-9-]+", vid or ""):
        raise ValueError("no such version")
    d = _dir(slug) / "versions" / vid
    if not d.is_dir():
        raise FileNotFoundError(vid)
    return d


def version_page(slug, vid, n):
    d = _version_dir(slug, vid) / "renders" / TAG
    for kind in ("lettered", "art"):
        p = d / kind / f"p{n:02d}.png"
        if p.is_file():
            return p
    raise FileNotFoundError(f"page {n}")


def restore_version(slug, vid):
    """Put a version back. What is there now is saved as a version first, so this can be undone."""
    if running(slug):
        raise RuntimeError("stop the run first")
    src = _version_dir(slug, vid)
    meta = json.loads((src / "meta.json").read_text())
    save_version(slug, f"before bringing back {meta['name']}", auto=True)
    base = projects.campaign_dir(slug)
    for sub in SNAP_DIRS:
        if (src / sub).is_dir():
            if (base / sub).is_dir():
                for p in (base / sub).glob("*"):
                    if p.is_file():
                        p.unlink()
            shutil.copytree(src / sub, base / sub, dirs_exist_ok=True)
    for sub in SNAP_FILES:
        for p in (src / sub).glob("*") if (src / sub).is_dir() else []:
            shutil.copy2(p, base / sub / p.name)
    return meta
