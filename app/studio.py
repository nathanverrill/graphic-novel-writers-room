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
import os
import re
import shutil
import threading
import time

from . import artcheck, config, magic, openitems, phases, projects, render, review, riff, room, storydesk, thumbnails, usage
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


def _shown(slug, n):
    """The page as a reader sees it: the newest lettering made since the art was drawn - the
    room's layer (lettered/) or a page Sunburst lettered whole (lettered-model/) - else None."""
    a = _art(slug, "art", n)
    if not a.is_file():
        return None
    done = [p for p in (_art(slug, "lettered", n), _art(slug, "lettered-model", n))
            if p.is_file() and p.stat().st_mtime >= a.stat().st_mtime]
    return max(done, key=lambda p: p.stat().st_mtime) if done else None


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
    took = [v["seconds"] for v in checks.values() if v.get("state") == "done" and v.get("seconds")]
    est = round(sum(took) / len(took)) if took else DRAW_SECONDS
    laid = {s["page"] for s in render.book(slug)}
    script = projects.read_artifact(slug, "script.md") or ""
    texts = {}
    for m in re.finditer(r"^##\s+Page\s+(\d+)\b[^\n]*\n(.*?)(?=^##\s+Page\s+\d+|\Z)", script, re.M | re.S):
        texts[int(m.group(1))] = m.group(0).strip()
    nums = sorted(set(texts) | {s["page"] for s in render.book(slug)})
    out = []
    for n in nums:
        a, l, m = _art(slug, "art", n), _art(slug, "lettered", n), _art(slug, "lettered-model", n)
        st = checks.get(str(n), {})
        out.append({"page": n, "script": texts.get(n, ""),
                    "art": int(a.stat().st_mtime) if a.is_file() else 0,
                    "lettered": int(l.stat().st_mtime) if l.is_file() else 0,
                    "model": int(m.stat().st_mtime) if m.is_file() else 0,
                    "state": st.get("state") or "", "problems": [p.get("what", "") for p in (st.get("check") or {}).get("problems") or []][:6],
                    "laid_out": n in laid,
                    **({"stage": st.get("stage") or "drawing", "attempt": st.get("attempt") or 1, "tries": artcheck.TRIES,
                        "job": st.get("job") or "", "started": st.get("started") or 0,
                        "est": est * (2 if st.get("job") in ("fix", "fix-letter") else 1)} if st.get("state") == "drawing" else {})})
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
             f"renders/{TAG}/art", f"renders/{TAG}/lettered", f"renders/{TAG}/lettered-model", f"renders/{TAG}/overlay", "style/locks")
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


# ---- one page: its words, and a chat that fixes it ---------------------------------------------
#
# The page editor: the page full size, its words as plain fields, and a chat. The chat sees the
# page as drawn and lettered, asks what it needs to, and when the change is clear applies it: a
# lettering change at once (free), an art change by redrawing this page from itself (Sunburst,
# art-checked), the drawing before kept so it can be brought back.

PAGE_SYSTEM = """You help the showrunner of {title} fix one finished comic page: page {n}. The page as it is
now is attached: drawn art with the lettering over it.

Two kinds of fix:
- WORDS: a balloon's words, its spot, its tail, or the balloon itself. The page is then lettered
  again by the artist from the clean art, keeping the other balloons, about ${cost:.2f}.
- ART: anything in the drawing - hands, fingers, poses, faces, props, who is where. The page is then
  redrawn from itself with only that change, then lettered again, about ${cost2:.2f}, and the page
  before is kept. Words and art in one reply cost the same as the art alone.
- SOUND EFFECTS: any redraw draws every sound effect into the art, big and hand-lettered, spelled as
  the layout has it, and takes it off the lettering layer. So to make a sound effect bigger, bolder or
  move it, send an ART fix and keep the item (change its "text" if the spelling changes) - never
  delete it.

Look at the page yourself. When the showrunner's ask is clear, apply it - don't ask for permission.
When it is not clear which character, panel or hand they mean, ask one short question. Never change
the script's words unless the showrunner asks for new words.

To apply, end your reply with one fenced block, and say in one plain line before it what you did:

```apply
{{"words": {{"<item number>": {{"text": "new words"}} | {{"delete": true}} | {{"tail": [x, y]}} | {{"tail": "none"}} | {{"at": "<spot>"}}}},
 "art": "for the artist: exactly what to change, where (panel, character, which hand), and what to keep"}}
```

Use only the keys you need ("words", "art" or both). "tail": [x, y] points the tail at that spot,
in percent of the whole page (0,0 top-left; 100,100 bottom-right) - aim at the speaker's mouth or head.
A spot is one of: {spots}. Keep "art" concrete and visual: "Panel 3: Min points with her RIGHT index finger;
her left hand rests on the table, five fingers" - never a story note.

The lettering on the page, by item number (positions in percent of the page):
{items}

The script for this page:
{script}"""


def _page_file(slug, n):
    d = _dir(slug) / "pages"
    d.mkdir(exist_ok=True)
    return d / f"p{n:02d}.json"


def page_chat(slug, n):
    try:
        return json.loads(_page_file(slug, n).read_text())
    except (OSError, ValueError):
        return []


def _geometry(slug, n):
    """(spec, rects, boxes, tails) for page n, the panels measured from its drawn art."""
    from . import lettering, prompts
    spec = lettering.page_spec(slug, n)
    if not spec:
        raise ValueError(f"page {n} has no layout yet, so its words can't be edited here")
    rects = lettering.panel_rects(spec)
    art = _art(slug, "art", n)
    if art.is_file():
        rects = lettering.detect_rects(spec, art.read_bytes()) or rects
    _, boxes, tails = lettering.layer(spec, prompts.context(slug), rects)
    return spec, rects, boxes, tails


def page_words(slug, n):
    """The page's words in reading order, for the editor's fields."""
    from . import lettering
    spec = lettering.page_spec(slug, n)
    drawn = _sfx_drawn(slug, n)
    return [{"i": it["i"], "text": it["text"], "type": it["type"]} for it in lettering.items(spec)
            if not (drawn and it["type"] == "sfx")] if spec else []


def _sfx_drawn(slug, n):
    return bool(render.status(slug)["models"].get(TAG, {}).get("pages", {}).get(str(n), {}).get("sfx_art"))


def _items_text(slug, n):
    from . import lettering
    try:
        spec, rects, boxes, tails = _geometry(slug, n)
    except ValueError:
        return "(this page isn't laid out yet, so it has no lettering to change)"
    pc = lambda v: round(v * 100)
    drawn = _sfx_drawn(slug, n)
    lines = []
    for it in lettering.items(spec):
        i, r = it["i"], rects.get(it.get("panel"))
        where = f"panel {it.get('panel')}" + (f" (page x {pc(r[0])}-{pc(r[0] + r[2])}, y {pc(r[1])}-{pc(r[1] + r[3])})" if r else "")
        box = boxes.get(i)
        at = f"; box x {pc(box[0])}-{pc(box[2])}, y {pc(box[1])}-{pc(box[3])}" if box else ""
        tail = f"; tail points at x {pc(tails[i][0])}, y {pc(tails[i][1])}" if i in tails else ""
        who = f" {it['speaker']}" if it.get("speaker") else ""
        if it["type"] == "sfx" and drawn:
            lines.append(f"{i}. sound effect, {where}, drawn into the art (change it with an art fix, not words): \"{it['text']}\"")
            continue
        lines.append(f"{i}. {it['type']}{who}, {where}{at}{tail}: \"{it['text']}\"")
    return "\n".join(lines) or "(no lettering)"


def _page_image(slug, n):
    """The page as the showrunner sees it, small enough to send: a JPEG data URL, or None."""
    import io
    from PIL import Image
    a = _art(slug, "art", n)
    src = _shown(slug, n) or a
    if not src.is_file():
        return None
    im = Image.open(src).convert("RGB")
    im.thumbnail((1100, 1650))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=85)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def _script_of(slug, n):
    script = projects.read_artifact(slug, "script.md") or ""
    m = re.search(rf"^##\s*Page\s+{n}\b.*?(?=^##\s*Page\s+\d+|\Z)", script, re.M | re.S | re.I)
    return m.group(0).strip() if m else "(no script for this page)"


def page_say(slug, n, text, texts=None, delete=None):
    """One update of the page: the words changed in the fields, exactly as typed, and whatever the
    message asks. Both go into one redraw - the lettering, or the art and then its lettering."""
    from . import lettering
    text = (text or "").strip()
    fields = {str(i): {"text": t} for i, t in (texts or {}).items()}
    fields.update({str(i): {"delete": True} for i in delete or []})
    if not text and not fields:
        raise ValueError("say what should change")
    if not text:
        return save_words(slug, n, texts, delete)
    _check_free(slug, n)
    key = riff._key()
    from . import easy
    kept = _art(slug, "art", n).is_file()
    if kept:
        easy._keep_copy(slug, [n])      # before any word changes: the copy has the words it showed
    fnote = _apply_words(slug, n, fields)[1] if fields else ""
    hist = page_chat(slug, n)
    hist.append({"role": "user", "content": text[:8000] + (f"\n\n(Changed in the word fields already, exactly as typed:\n{fnote})" if fnote else ""),
                 "t": time.time()})
    system = PAGE_SYSTEM.format(title=title(slug), n=n, cost=COST_PAGE, cost2=2 * COST_PAGE, spots=", ".join(lettering.ANCHORS),
                                items=_items_text(slug, n), script=_script_of(slug, n)[:12000])
    msgs = [{"role": m["role"], "content": m["content"]} for m in hist[-20:]]
    pic = _page_image(slug, n)
    if pic:      # the page as it is now, with the newest message
        msgs[-1] = {"role": "user", "content": [{"type": "image_url", "image_url": {"url": pic}},
                                               {"type": "text", "text": msgs[-1]["content"]}]}
    t0 = time.time()
    reply, cost = riff._ask([{"role": "system", "content": system}] + msgs, key, max_tokens=3000)
    usage.ledger(slug, "studio", "page-chat", riff.MODEL, cost, time.time() - t0, page=n)
    shown, done = reply, []
    m = re.search(r"```apply\s*(\{.*?\})\s*```", reply, re.S)
    if m:
        shown = (reply[:m.start()] + reply[m.end():]).strip()
        try:
            act = json.loads(m.group(1))
        except ValueError:
            act = None
            done.append("couldn't read the change - say it again")
        if isinstance(act, dict):
            if act.get("words") and (act.get("art") or "").strip():
                # a redraw draws the sound effects into the art, so a sound effect the chat moves there stays
                # in the layout (the drawing prompt lists it, the overlay then leaves it out)
                sfx = {it["i"] for it in lettering.items(lettering.page_spec(slug, n) or {}) if it["type"] == "sfx"}
                act["words"] = {k: v for k, v in act["words"].items()
                                if not (isinstance(v, dict) and v.get("delete") and str(k).isdigit() and int(k) in sfx)}
            note = fnote
            if act.get("words"):
                try:
                    _check_free(slug, n)
                    said, more = _apply_words(slug, n, act["words"])
                    note = "\n".join(x for x in (note, more) if x)
                    done.append(said)
                except ValueError as e:
                    done.append(f"words not changed: {e}")
            if (act.get("art") or "").strip():
                try:
                    fix_page(slug, n, act["art"].strip(), note, kept=kept)
                    done.append("redrawing the page")
                except ValueError as e:
                    done.append(f"not redrawn: {e}")
            elif note and _art(slug, "art", n).is_file():
                try:
                    reletter(slug, n, note, kept=kept)
                    done.append("lettering the page again")
                except ValueError as e:
                    done.append(f"not lettered: {e}")
    if fnote and not done and _art(slug, "art", n).is_file():
        try:
            reletter(slug, n, fnote, kept=kept)
            done.append("lettering the page again")
        except ValueError as e:
            done.append(f"not lettered: {e}")
    hist.append({"role": "assistant", "content": shown or "Done.", "t": time.time(), "cost": cost, "done": done,
                 "art": (act.get("art") if m and isinstance(act, dict) else None)})
    _page_file(slug, n).write_text(json.dumps(hist, indent=1))
    return page_state(slug, n)


def _apply_words(slug, n, words):
    """The chat's or the fields' lettering changes - text, a tail aimed at a spot on the page, a
    spot, a deletion - into the layout. Returns (summary, note): the note tells the lettering
    redraw what changed. The page itself is lettered again by Sunburst (reletter)."""
    from . import lettering
    spec, rects, _, _ = _geometry(slug, n)
    items = {it["i"]: it for it in lettering.items(spec)}
    changes, drop, notes = {}, [], []
    for k, ch in (words or {}).items():
        i = int(k)
        if i not in items or not isinstance(ch, dict):
            raise ValueError(f"no item {k} on this page")
        old = items[i]["text"]
        if ch.get("delete"):
            drop.append(i)
            notes.append(f'remove the {items[i]["type"]} "{old}" entirely')
            continue
        c = {}
        if "text" in ch and " ".join(str(ch["text"]).split()) != " ".join(str(old).split()):
            c["text"] = str(ch["text"])
            notes.append(f'the {items[i]["type"]} that read "{old}" now reads "{" ".join(str(ch["text"]).split())}"')
        if ch.get("at"):
            c["at"] = ch["at"]
            notes.append(f'move "{old}" to the {ch["at"]} of its panel')
        t = ch.get("tail")
        if t == "none":
            c["tail"] = "none"
            notes.append(f'"{old}" has no tail (the speaker is off panel)')
        elif isinstance(t, (list, tuple)) and len(t) == 2:
            notes.append(f'point the tail of "{old}" at the spot {round(float(t[0]))}% across and {round(float(t[1]))}% down the page')
            r = rects.get(items[i].get("panel")) or (0, 0, 1, 1)
            c["tail_x"] = (float(t[0]) / 100 - r[0]) / r[2] * 100      # page percent to panel percent
            c["tail_y"] = (float(t[1]) / 100 - r[1]) / r[3] * 100
        if c:
            changes[str(i)] = c
    if changes:
        lettering.set_items(slug, n, changes)
    for i in sorted(drop, reverse=True):
        lettering.delete_item(slug, n, i)
    k = len(changes) + len(drop)
    return f"changed {k} balloon{'s' if k != 1 else ''}", "\n".join(f"- {x}" for x in notes)


def save_words(slug, n, texts, delete):
    """The editor's fields: new words by item number, and the items struck out."""
    words = {str(i): {"text": t} for i, t in (texts or {}).items()}
    for i in delete or []:
        words[str(i)] = {"delete": True}
    if not words:
        return page_state(slug, n)
    _check_free(slug, n)
    from . import easy
    drawn = _art(slug, "art", n).is_file()
    if drawn:
        easy._keep_copy(slug, [n])      # before the words change, so the copy has the words it showed
    _, note = _apply_words(slug, n, words)
    if note and drawn:
        reletter(slug, n, note, kept=True)
    return page_state(slug, n)


def _check_free(slug, n):
    from . import easy
    if (_fix_jobs.get((slug, n)) or {}).get("state") == "running" or easy.running(slug):
        raise ValueError("this page is being drawn - wait for it to finish")


def _letter_lines(slug, n):
    from . import lettering
    spec = lettering.page_spec(slug, n) or {}
    drawn = _sfx_drawn(slug, n)
    return "\n".join(f'- Panel {i.get("panel")}, {i["type"]}' + (f' ({i["speaker"]})' if i.get("speaker") else "") + f': "{i["text"]}"'
                     for i in lettering.items(spec) if i.get("text") and not (drawn and i["type"] == "sfx"))


LETTER_PROMPT = """Letter this comic page. Image 1 is the finished art: keep every line of it EXACTLY the same and change nothing in the drawing. {now}
Add only the lettering below, designed into the panels{ref}: clean white speech balloons with short tails and thin outlines, in calm space beside the speaker, the tail pointing at the speaker's mouth, never over a face, a hand or the key object; captions as small cream boxes with dark text in panel corners; place-and-time captions as small yellow boxes top-left. Use exactly these words, spelled and punctuated exactly, in uppercase comic lettering, in reading order. ADD NO OTHER TEXT: no captions, titles, place names, dates or words that are not in this list.
{lines}"""


def _letter_with_model(slug, n, note, key):
    """Sunburst letters the clean art whole - the balloons drawn into the page - checked word for
    word, into lettered-model/, which the page then shows. Returns the cost."""
    art = _art(slug, "art", n)
    shown = _shown(slug, n)
    refs = [("the finished art: keep it exactly, add only the lettering", art)]
    if shown:
        base = art.parent / f".letter-p{n:02d}.png"
        shutil.copyfile(shown, base)
        refs.append(("the page as lettered now: keep each balloon's spot, size and look unless the changes say otherwise", base))
    lref = projects.campaign_dir(slug) / "style" / "lettering-reference.png"
    if lref.is_file():
        refs.append(("lettering reference: letter in exactly this style", lref))
    lines = _letter_lines(slug, n)
    prompt = LETTER_PROMPT.format(
        now=("Image 2 is the page as lettered now: keep its balloons where they are and as they look, and make only these changes:\n" + note + "\n") if shown and note
        else ("Image 2 is the page as lettered now: keep its balloons where they are and as they look.\n" if shown else ""),
        ref=" like the lettering reference" if lref.is_file() else "", lines=lines)
    try:
        t0 = time.time()
        img, report, cost = artcheck.draw_checked(
            lambda text, r: render.generate(render.MODELS[TAG], text, r, key), prompt, refs, key,
            script=lines, lettered=True, stage=render.stager(slug, TAG, n))
        d = render.folder(slug, TAG, "lettered-model")
        d.mkdir(parents=True, exist_ok=True)
        (d / f"p{n:02d}.png").write_bytes(img)
        usage.ledger(slug, "studio", "page-letter", render.MODELS[TAG], cost, time.time() - t0, page=n,
                     tries=len(report["attempts"]), check_pass=report["pass"])
        return cost
    finally:
        if shown:
            base.unlink(missing_ok=True)


def reletter(slug, n, note, kept=False):
    """Letter page n again with Sunburst after its words changed, in the background."""
    from . import easy
    key = render.api_key()
    if not key:
        raise ValueError("no OpenRouter key")
    jk = (slug, n)
    if not kept:
        easy._keep_copy(slug, [n])
    _fix_jobs[jk] = {"state": "running", "started": time.time(), "note": note}
    render._update(slug, TAG, n, state="drawing", stage="drawing", attempt=1, job="letter", started=time.time())

    def work():
        try:
            cost = _letter_with_model(slug, n, note, key)
            render._update(slug, TAG, n, state="done", stage=None, error=None)
            _fix_jobs[jk] = {"state": "done", "cost": cost}
        except Exception as e:      # noqa: BLE001 - shown on the page
            render._update(slug, TAG, n, state="done", stage=None, error=str(e)[:400])
            _fix_jobs[jk] = {"state": "failed", "error": str(e)[:300]}

    threading.Thread(target=work, daemon=True).start()
    return _fix_jobs[jk]


_fix_jobs = {}


def fix_page(slug, n, note, letter_note="", kept=False):
    """Redraw page n from its own drawing with one change, art-checked; the drawing before is kept."""
    from . import easy, prompts
    key = render.api_key()
    if not key:
        raise ValueError("no OpenRouter key")
    art = _art(slug, "art", n)
    if not art.is_file():
        raise ValueError("the page isn't drawn yet")
    spec = next((s for s in render.book(slug) if s["page"] == n), None)
    if not spec:
        raise ValueError("the page has no layout")
    jk = (slug, n)
    if (_fix_jobs.get(jk) or {}).get("state") == "running" or easy.running(slug):
        raise ValueError("this book is being drawn - wait for it to finish")
    if not kept:
        easy._keep_copy(slug, [n])
    ctx = {**prompts.context(slug), "slug": slug, "lettering": "layer"}
    base = art.parent / f".fix-p{n:02d}.png"      # the drawing being fixed, kept still while the new one lands
    shutil.copyfile(art, base)
    refs = [("this page as drawn now - redraw this same page, changing only what the fix says", base)]
    refs += [r for r in render.references(slug, TAG, spec, ctx) if "as drawn before" not in r[0]]
    refs = refs[:render.MAX_REFS]
    sfx = render.sfx_words(spec, ctx)
    prompt = (render.prompt_for(spec, ctx, refs) +
              f"\n\n**THE FIX.** Image 1 is this page as drawn now. Redraw it the same - same panels, "
              f"compositions, characters, colours and style - and change only this:\n{note}\n")
    _fix_jobs[jk] = {"state": "running", "started": time.time(), "note": note}
    render._update(slug, TAG, n, state="drawing", stage="drawing", attempt=1, job="fix", started=time.time())

    def work():
        t0 = time.time()
        try:
            img, report, cost = artcheck.draw_checked(
                lambda text, r: render.generate(render.MODELS[TAG], text, r, key), prompt, refs, key,
                script=f"{_script_of(slug, n)}\n\nThis drawing is a fix of the page: {note}", lettered=sfx or False,
                stage=render.stager(slug, TAG, n))
            art.write_bytes(img)
            render._update(slug, TAG, n, cost=cost, error=None, sfx_art=bool(sfx),
                           check={"pass": report["pass"], "problems": report["problems"], "tries": len(report["attempts"])})
            usage.ledger(slug, "studio", "page-fix", render.MODELS[TAG], cost, time.time() - t0, page=n,
                         tries=len(report["attempts"]), check_pass=report["pass"])
            render.after_drawing(slug, TAG, n)      # the overlay files, balloons where the user placed them
            render._update(slug, TAG, n, stage="drawing", attempt=1, job="fix-letter")
            cost += _letter_with_model(slug, n, letter_note, key)      # and the page lettered whole
            render._update(slug, TAG, n, state="done", stage=None, seconds=round(time.time() - t0))
            _fix_jobs[jk] = {"state": "done", "cost": cost}
        except Exception as e:      # noqa: BLE001 - shown on the page
            render._update(slug, TAG, n, state="failed", error=str(e)[:400])
            _fix_jobs[jk] = {"state": "failed", "error": str(e)[:300]}
        finally:
            base.unlink(missing_ok=True)

    threading.Thread(target=work, daemon=True).start()
    return _fix_jobs[jk]


def page_state(slug, n):
    p = next((x for x in pages(slug) if x["page"] == n), None)
    if not p:
        raise FileNotFoundError(f"no page {n}")
    from . import easy
    from . import lettering
    spec = lettering.page_spec(slug, n)
    panels = [[round(v, 4) for v in r] for _, r in sorted(lettering.panel_rects(spec).items())] if spec else []
    return {**p, "words": page_words(slug, n), "chat": page_chat(slug, n), "panels": panels,
            "fix": _fix_jobs.get((slug, n)) or {}, "earlier": bool(easy._earlier(slug, n)), "cost_page": COST_PAGE,
            "layout_job": _layout_jobs.get((slug, n)) or {}, "now": time.time()}


# ---- an undrawn page: lay it out, then draw it -------------------------------------------------

DRAW_SECONDS = 120      # a page's draw, check and lettering when the book has no timings yet
_layout_jobs = {}

LAYOUT_ASK = """You are the layout artist of {title}. Lay out page {n} only, as one ```layout block of JSON.

{rules}

Hard rules:
- Every balloon, caption and sound effect carries the script's words EXACTLY - same spelling, punctuation
  and capitals. Never add, cut, merge or reword a line. Speakers are the names the script uses.
- Every line of dialogue and caption on the script's page appears, in the script's order.
- "page": {n}, "side": "{side}".
- Match the neighbouring pages' manner: the same kind of panel descriptions, the same characters' looks.
- Reply with the block only."""


def _layout_rules():
    role = (config.ROOT / "agents" / "layout" / "role.md").read_text() if (config.ROOT / "agents" / "layout" / "role.md").is_file() else ""
    i = role.find("# The layout block")
    rules = role[i:] if i >= 0 else role
    return rules.split('- "file" is one of')[0].strip()


def _norm(t):
    t = str(t).replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    return " ".join(t.lower().split())


def _layout_block(md, n):
    for m in thumbnails.LAYOUT_RE.finditer(md or ""):
        try:
            if int(json.loads(re.sub(r",(\s*[\]}])", r"\1", m.group(1))).get("page", 0)) == n:
                return m.group(1).strip()
        except ValueError:
            continue
    return ""


def lay_out_page(slug, n):
    """Write page n's layout from its script page, in the manner of the pages around it, and add it
    to layouts.md. The words are checked against the script; a layout that changes them is not kept."""
    if any(s["page"] == n for s in render.book(slug)):
        raise ValueError(f"page {n} is already laid out")
    script = _script_of(slug, n)
    if script.startswith("(no script"):
        raise ValueError(f"page {n} has no script yet")
    jk = (slug, n)
    if (_layout_jobs.get(jk) or {}).get("state") == "running":
        raise ValueError("this page is already being laid out")
    key = riff._key()
    _layout_jobs[jk] = {"state": "running", "started": time.time()}
    md = projects.read_artifact(slug, "layouts.md") or ""
    near = sorted({s["page"] for s in render.book(slug)}, key=lambda p: abs(p - n))[:2]
    side = "right" if n % 2 else "left"
    system = LAYOUT_ASK.format(title=title(slug), n=n, side=side, rules=_layout_rules())
    parts = [f"## The script's page {n}\n\n{script}"]
    parts += [f"## Page {p}'s layout, for its manner\n\n```layout\n{_layout_block(md, p)}\n```" for p in sorted(near)]
    for name in ("characters.md", "world.md"):
        text = projects.read_artifact(slug, name, desk=projects.PRE) or projects.read_artifact(slug, name) or ""
        if text:
            parts.append(f"## {name}\n\n{text[:12000]}")
    msgs = [{"role": "system", "content": system}, {"role": "user", "content": "\n\n".join(parts)}]
    threading.Thread(target=_lay_out, args=(slug, n, script, msgs, key, side), daemon=True).start()
    return page_state(slug, n)


def _lay_out(slug, n, script, msgs, key, side):
    jk, t0, spent = (slug, n), time.time(), 0.0
    try:
        for _ in range(2):
            reply, cost = riff._ask(msgs, key, max_tokens=6000)
            spent += cost or 0
            specs, errors = thumbnails.parse_layouts(reply if "```layout" in reply else f"```layout\n{reply}\n```")
            if not specs:
                problem = "; ".join(errors) or "no layout block"
            else:
                spec = {**specs[0], "page": n, "side": specs[0].get("side") or side}
                said = _norm(script)
                changed = [i.get("text", "") for i in spec.get("items") or []
                           if i.get("type") in thumbnails.LETTERING and _norm(i.get("text", "")) not in said]
                problem = ("these words aren't the script's: " + " | ".join(changed)) if changed else ""
            if not problem:
                break
            msgs += [{"role": "assistant", "content": reply},
                     {"role": "user", "content": f"Not kept - {problem}. Write the block again with the script's exact words."}]
        else:
            raise ValueError(f"the layout wasn't kept: {problem}")
        _add_layout(slug, n, spec)
        usage.ledger(slug, "studio", "page-layout", riff.MODEL, spent, time.time() - t0, page=n)
        _layout_jobs[jk] = {"state": "done", "cost": spent}
    except Exception as e:      # noqa: BLE001 - shown on the page
        _layout_jobs[jk] = {"state": "failed", "error": str(e)[:300]}


def _add_layout(slug, n, spec):
    """Page n's block into layouts.md, in page order. The file keeps its time, so a run does not
    take the new page for a change to every drawn page and redraw them."""
    path = projects.project_dir(slug) / "layouts.md"
    md = path.read_text() if path.is_file() else f"# {title(slug)} — Layouts\n"
    section = f"## Page {n} ({spec['side']})\n\n```layout\n{json.dumps(spec, ensure_ascii=False, indent=1)}\n```\n\n"
    later = [m for m in re.finditer(r"^## Page (\d+)\b", md, re.M) if int(m.group(1)) > n]
    md = md[:later[0].start()] + section + md[later[0].start():] if later else md.rstrip("\n") + "\n\n" + section
    times = path.stat() if path.is_file() else None
    projects.write_artifact(slug, "layouts.md", md)
    if times:
        os.utime(path, (times.st_atime, times.st_mtime))


def draw_page(slug, n):
    """Draw one laid-out page that isn't drawn yet - the same draw, check and lettering as a run."""
    from . import easy
    if _art(slug, "art", n).is_file():
        raise ValueError("the page is drawn - say what should change in the chat instead")
    if not any(s["page"] == n for s in render.book(slug)):
        raise ValueError(f"page {n} isn't laid out yet")
    if (_fix_jobs.get((slug, n)) or {}).get("state") == "running":
        raise ValueError("this page is being drawn")
    easy.draw(slug, [n])
    return page_state(slug, n)
