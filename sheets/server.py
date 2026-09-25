#!/usr/bin/env python3
"""The sheets page: sheets.py behind one small web page, in its own container.

    python3 sheets/server.py            # http://localhost:8001

Same folders as the command line (sheets/<character>/...), so the two can be mixed. A subject
is a character or a place (kind.txt). The page can also read markdown from the campaigns
folder - a character's section of characters.md, a place's section of world.md - to fill in
the description. Standard library only; one thread per request, and the
generation of a step runs in a thread of its own while the page polls."""
import base64
import json
import mimetypes
import os
import re
import sys
import threading
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sheets as core                                  # noqa: E402
if os.getenv("SECRETS_FILE"):
    core.SECRETS = Path(os.getenv("SECRETS_FILE"))

ROOT = Path(os.getenv("SHEETS_DIR") or core.HERE).resolve()            # where the characters live
MD_ROOTS = [Path(p).resolve() for p in (os.getenv("MD_DIRS") or str(core.HERE.parent / "campaigns")).split(":") if p]
PORT = int(os.getenv("PORT") or 8001)
PREFIX = (os.getenv("PREFIX") or "").rstrip("/")     # "/sheets" when the room's app proxies to us
DRY = bool(os.getenv("SHEETS_DRY"))

_running = {}          # (character, step) -> {"status": "running"|"done"|"failed", "errors": [...]}
_lock = threading.Lock()


# ---- helpers ------------------------------------------------------------------------------------

def character(name):
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,40}", name or ""):
        raise ValueError("a character is a short lowercase folder name")
    return ROOT / name


def load(name, need=True):
    d = character(name)
    if not d.is_dir():
        if need:
            raise FileNotFoundError(name)
        return None
    if not (d / "description.txt").exists() or not list(d.glob("lock.*")):
        return None          # made, not ready
    return core.Character(d)


def stage_file(d, stage_id):
    return d / "runs" / stage_id / "stage.json"


def stage_state(d, stage_id):
    f = stage_file(d, stage_id)
    return json.loads(f.read_text()) if f.exists() else {"rounds": [], "pick": None}


def save_stage(d, stage_id, st):
    f = stage_file(d, stage_id)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(st, indent=1))


def style_text():
    """The book's visual direction, if a brief is in reach: the first campaign's brief.md."""
    for root in MD_ROOTS:
        for b in sorted(root.glob("*/production/brief.md")) if root.is_dir() else []:
            m = re.search(r"^#+[^\n]*\b(visual|style|look)\b[^\n]*\n(.*?)(?=^#|\Z)", b.read_text(), re.S | re.M | re.I)
            if m:
                return " ".join(m.group(2).split())[:600]
    return None


PLATE_DIR = ROOT / "_style"      # the book's style plate: a kept lock every new lock can be rolled from


def plate():
    """(path, the subject it came from) - or (None, None) when there is no style plate."""
    found = [p for p in PLATE_DIR.glob("plate.*")] if PLATE_DIR.is_dir() else []
    src = PLATE_DIR / "from.txt"
    return (found[0], src.read_text().strip() if src.exists() else None) if found else (None, None)


def set_plate(name):
    """This subject's lock becomes the book's style plate; no name clears it."""
    for old in PLATE_DIR.glob("plate.*") if PLATE_DIR.is_dir() else []:
        old.unlink()
    (PLATE_DIR / "from.txt").unlink(missing_ok=True)
    if not name:
        return None
    char = core.Character(character(name), need_lock=False)
    if not char.lock:
        raise ValueError("lock this one first")
    PLATE_DIR.mkdir(exist_ok=True)
    import shutil
    shutil.copyfile(char.lock, PLATE_DIR / f"plate{char.lock.suffix}")
    (PLATE_DIR / "from.txt").write_text(name + "\n")
    return name


def kept_rates():
    """{model: [kept, rolled]} over every subject's lineage: how often a model's candidate was the one kept."""
    out = {}
    for f in ROOT.glob("*/lineage.jsonl"):
        for line in f.read_text().splitlines():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if not r.get("model") or r.get("error"):
                continue
            if core.excluded(r["model"]):
                continue
            n = out.setdefault(r["model"], [0, 0])
            n[0 if r.get("picked") else 1] += 1
    return out


def stages(char):
    """[(id, n, title, instruction, parent_name)] - the lock, then the steps."""
    first = ("the approved establishing view: wide, eye level, daylight, nobody in frame" if char.kind == "place"
             else "the approved starting view: full-length front, neutral, plain background")
    out = [("00-lock", 0, "lock", first, None)]
    for n, (step, instruction, parent) in enumerate(char.steps, 1):
        out.append((f"{n:02d}-{step}", n, step, instruction, parent))
    return out


def kept_for(char, stage_id, title):
    if stage_id == "00-lock":
        return char.lock
    return char.pick_of(title)


def parent_for(char, stage_id, n, parent_name):
    """The image a stage builds on: the pick of one of its own rolls if there is one (roll
    again), else the named step's keep, else the nearest earlier keep, else the lock."""
    st = stage_state(char.dir, stage_id)
    pick = st.get("pick")
    if pick:
        p = char.dir / "runs" / stage_id / pick["round"] / pick["file"]
        if p.exists():
            return p, True
    if stage_id == "00-lock":
        return None, False
    if parent_name:
        return char.pick_of(parent_name), False
    parent = char.lock
    for sid, k, title, _, _ in stages(char):
        if 0 < k < n and char.pick_of(title):
            parent = char.pick_of(title)
    return parent, False


def roll(name, stage_id, notes, models, each, base=None, batch=False, variants=None):
    d = character(name)
    if not (d / "description.txt").exists():
        raise ValueError("write the description first")
    char = core.Character(d, need_lock=False)
    found = next((x for x in stages(char) if x[0] == stage_id), None)
    if not found:
        raise ValueError(f"no stage {stage_id}")
    _, n, title, instruction, parent_name = found
    if base == "kept":                    # redo a kept stage from what was kept, with the note
        parent, from_pick = kept_for(char, stage_id, title), True
        if parent is None:
            raise ValueError("nothing kept for this stage yet")
    elif base == "parent":                # start the stage over from its parent, ignoring the pick
        parent, from_pick = (None, False) if stage_id == "00-lock" else (parent_for(char, stage_id, n, parent_name)[0], False)
        st0 = stage_state(d, stage_id); st0["pick"] = None; save_stage(d, stage_id, st0)
        if stage_id != "00-lock" and parent is None:
            raise ValueError("this step's parent has nothing kept yet")
    else:
        parent, from_pick = parent_for(char, stage_id, n, parent_name)
    if stage_id != "00-lock" and parent is None:
        raise ValueError("this step's parent has nothing kept yet - lock first, or keep the step it builds on")
    from_reference, plan = False, None
    if stage_id == "00-lock" and parent is None and char.reference is not None and base != "kept":
        parent, from_reference = char.reference, True       # what is where comes from the reference
        prompt = core.reference_prompt(char, style_text(), notes)
    elif stage_id == "00-lock":
        prompt = core.lock_prompt(char, style_text(), notes, from_pick=from_pick)
    else:
        prompt = core.prompt_for(char, instruction, notes, from_pick=from_pick)
    plate_img = plate()[0]
    if stage_id == "00-lock" and not from_pick and plate_img:   # a fresh lock: plain, with the plate, or both
        wanted = [v for v in (variants or ["plain", "styled"]) if v in ("plain", "styled")] or ["plain"]
        styled = (core.reference_prompt(char, style_text(), notes, plate=True) if from_reference
                  else core.lock_prompt(char, style_text(), notes, plate=True))
        plan = [v for v in [("plain", prompt, parent), ("styled", styled, [parent, plate_img] if parent else plate_img)]
                if v[0] in wanted]
    st = stage_state(d, stage_id)
    k = len(st["rounds"]) + 1
    folder = d / "runs" / stage_id / f"r{k}"
    key = "" if DRY else core.api_key()
    gen = core.fake if DRY else core.generate
    with _lock:
        if _running.get((name, stage_id), {}).get("status") == "running":
            raise ValueError("that stage is already rolling")
        _running[(name, stage_id)] = {"status": "running", "errors": []}
    import time as _t
    st["rounds"].append({"round": f"r{k}", "notes": notes or "", "from_pick": from_pick, "from_reference": from_reference, "pick_before": st.get("pick"),
                         "parent": parent.name if parent else None, "candidates": [], "errors": [], "models": list(models),
                         "each": each * (len(plan) if plan else 1), "variants": [v[0] for v in plan] if plan else None, "started": _t.time(), "seconds": None, "batch": batch})
    save_stage(d, stage_id, st)

    _stop.discard((name, stage_id))

    def landed(m, path, took, variant=None):
        with _lock:
            if (name, stage_id) in _stop:
                return                      # stopped: late arrivals are left in the folder, unlisted
            st2 = stage_state(d, stage_id)
            st2["rounds"][-1]["candidates"].append({"model": m, "file": path.name, "seconds": took, "variant": variant})
            save_stage(d, stage_id, st2)
            with (d / "timings.jsonl").open("a") as f:
                f.write(json.dumps({"model": m, "seconds": took}) + "\n")

    def work():
        try:
            _, cands, errors = core.make_candidates(char, n, title, instruction, parent, models, each, gen, key,
                                                    say=lambda m: None, folder=folder, prompt=prompt, on_candidate=landed,
                                                    variants=plan)
            if (name, stage_id) in _stop:
                return
            st2 = stage_state(d, stage_id)
            have = {c["file"] for c in st2["rounds"][-1]["candidates"]}
            st2["rounds"][-1]["candidates"] += [{"model": m, "file": p.name} for m, p in cands if p.name not in have]
            st2["rounds"][-1].update(errors=errors, seconds=round(_t.time() - st2["rounds"][-1]["started"], 1))
            save_stage(d, stage_id, st2)
            _running[(name, stage_id)] = {"status": "done" if cands else "failed", "errors": errors}
        except Exception as e:      # noqa: BLE001
            st2 = stage_state(d, stage_id)
            st2["rounds"][-1]["errors"] = [str(e)[:300]]
            save_stage(d, stage_id, st2)
            _running[(name, stage_id)] = {"status": "failed", "errors": [str(e)[:300]]}
    threading.Thread(target=work, daemon=True).start()


_batch = {}
_stop = set()           # (character, stage) rolls the showrunner asked to stop


def stop_roll(name, stage_id):
    """Stop waiting on the rest of a roll: what has landed stays, the rest is let go."""
    _stop.add((name, stage_id))
    d = character(name)
    st = stage_state(d, stage_id)
    if st["rounds"] and st["rounds"][-1].get("seconds") is None:
        import time as _t
        st["rounds"][-1]["stopped"] = True
        st["rounds"][-1]["seconds"] = round(_t.time() - st["rounds"][-1]["started"], 1)
        save_stage(d, stage_id, st)
    _running[(name, stage_id)] = {"status": "stopped", "errors": []}


def fix_all(name, notes, models, each):
    """One note, every kept stage: each is rolled again from what was kept, with the note,
    one stage after another (its candidates still in parallel). You then review each."""
    if not notes:
        raise ValueError("say what to fix")
    d = character(name)
    char = core.Character(d, need_lock=False)
    todo = [(sid, title) for sid, n, title, _, _ in stages(char) if kept_for(char, sid, title)]
    if not todo:
        raise ValueError("nothing kept yet")
    if _batch.get(name, {}).get("status") == "running":
        raise ValueError("a fix is already running")
    _batch[name] = {"status": "running", "done": 0, "total": len(todo), "current": None, "notes": notes}

    def work():
        import time as _t
        for sid, title in todo:
            _batch[name]["current"] = sid
            try:
                roll(name, sid, notes, models, each, base="kept", batch=True)
                while _running.get((name, sid), {}).get("status") == "running":
                    _t.sleep(1)
            except ValueError:
                pass
            _batch[name]["done"] += 1
        _batch[name].update(status="done", current=None)
    threading.Thread(target=work, daemon=True).start()


def set_zip(name):
    """The finished set: every kept image with its caption, and the lock, ready to train on."""
    import io, zipfile
    d = character(name)
    char = core.Character(d, need_lock=False)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        if char.lock:
            z.write(char.lock, f"{name}/00-lock{char.lock.suffix}")
            z.writestr(f"{name}/00-lock.txt", f"{char.trigger}, " + ("wide establishing view, eye level, daylight" if char.kind == "place"
                                                                    else "full-length front view, neutral pose, plain background") + "\n")
        for p in sorted((d / "set").iterdir()) if (d / "set").is_dir() else []:
            z.write(p, f"{name}/{p.name}")
        z.writestr(f"{name}/README.txt", f"Training set for {name}, a {char.kind}. Trigger word: {char.trigger}.\n"
                   f"Each image has a .txt caption beside it. Train a {char.kind} LoRA on this folder;\n"
                   "use the trigger word in every prompt afterwards.\n")
    buf.seek(0)
    return buf.read()


RESET_WORD = "evoke"


def reset(name, confirm):
    """Start this subject over: the reference, the lock, every roll, every kept image and the
    logs move to previous/<time>/ inside its folder. The setup text stays: description, notes,
    style, steps, kind. Confirmed by typing the word, checked here as well."""
    if (confirm or "").strip().lower() != RESET_WORD:
        raise ValueError(f"type {RESET_WORD} to confirm")
    d = character(name)
    if not d.is_dir():
        raise FileNotFoundError(name)
    if any(v.get("status") == "running" for (n, _), v in _running.items() if n == name) or _batch.get(name, {}).get("status") == "running":
        raise ValueError("wait for the roll to finish")
    import shutil, time as _t
    work = [p for p in d.iterdir() if p.name in ("runs", "set", "lineage.jsonl", "timings.jsonl") or p.name.startswith(("lock.", "reference."))]
    stamp = _t.strftime("%Y%m%d-%H%M%S")
    if work:
        prev = d / "previous" / stamp
        prev.mkdir(parents=True, exist_ok=True)
        for p in work:
            shutil.move(str(p), str(prev / p.name))
    (d / "runs").mkdir(exist_ok=True)
    (d / "set").mkdir(exist_ok=True)
    for k in [k for k in _running if k[0] == name]:
        del _running[k]
    _batch.pop(name, None)
    return stamp if work else None


def undo(name, stage_id):
    """Drop the last roll of a stage and put the pick back where it was before it."""
    d = character(name)
    st = stage_state(d, stage_id)
    if not st["rounds"]:
        raise ValueError("nothing to undo")
    if _running.get((name, stage_id), {}).get("status") == "running":
        raise ValueError("wait for the roll to finish")
    last = st["rounds"].pop()
    folder = d / "runs" / stage_id / last["round"]
    if folder.is_dir():
        import shutil
        shutil.rmtree(folder)
    if st.get("pick") and st["pick"]["round"] == last["round"]:
        st["pick"] = last.get("pick_before")
    save_stage(d, stage_id, st)
    return len(st["rounds"])


_catalog = {"t": 0, "models": []}


def typical_seconds():
    """{model: median seconds} from every character's timings, for the estimate beside Roll."""
    times = {}
    for f in ROOT.glob("*/timings.jsonl"):
        for line in f.read_text().splitlines():
            try:
                r = json.loads(line)
                times.setdefault(r["model"], []).append(float(r["seconds"]))
            except (ValueError, KeyError, TypeError):
                continue
    return {m: sorted(v)[len(v) // 2] for m, v in times.items() if v}


def allowed(models):
    """The models asked for, less any excluded since the page loaded; the defaults if none are left."""
    return [m for m in models or [] if not core.excluded(m)] or core.DEFAULT_MODELS


def catalog():
    """Image models that take a reference image, from OpenRouter (cached an hour); the good
    ones first. Without a key, the good ones alone."""
    import time as _t
    if _t.time() - _catalog["t"] < 3600 and _catalog["models"]:
        return _catalog["models"]
    ids = []
    try:
        key = core.api_key() if not DRY else None
        if key:
            req = urllib.request.Request(f"{core.OPENROUTER}/images/models", headers={"Authorization": f"Bearer {key}"})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.load(r).get("data", [])
            ids = [m["id"] for m in data if (m.get("supported_parameters") or {}).get("input_references")]
    except (SystemExit, Exception):        # noqa: BLE001 - the page still works without the catalog
        ids = []
    # the list: the defaults, then every other model that takes a reference
    models = [m for m in core.DEFAULT_MODELS if not ids or m in ids] + sorted(m for m in ids if m not in core.DEFAULT_MODELS and not core.excluded(m))
    _catalog.update(t=_t.time(), models=models)
    return models


def dismiss(name, stage_id):
    """The batch roll for this stage was no better: keep what was kept, drop the review flag."""
    d = character(name)
    st = stage_state(d, stage_id)
    if st["rounds"] and st["rounds"][-1].get("batch"):
        st["rounds"][-1]["kept_from"] = True
        save_stage(d, stage_id, st)


def pick(name, stage_id, round_name, file):
    d = character(name)
    if not (d / "runs" / stage_id / round_name / file).exists():
        raise ValueError("no such candidate")
    st = stage_state(d, stage_id)
    st["pick"] = {"round": round_name, "file": file}
    save_stage(d, stage_id, st)


def keep(name, stage_id):
    """The pick becomes the lock, or the step's kept image with its caption."""
    d = character(name)
    char = core.Character(d, need_lock=False)
    st = stage_state(d, stage_id)
    if not st.get("pick"):
        raise ValueError("pick the closest candidate first")
    src = d / "runs" / stage_id / st["pick"]["round"] / st["pick"]["file"]
    for r in st["rounds"]:
        r["kept_from"] = r["round"] == st["pick"]["round"]
    save_stage(d, stage_id, st)
    rnd = next(r for r in st["rounds"] if r["round"] == st["pick"]["round"])
    cand = next((c for c in rnd["candidates"] if c["file"] == src.name), {})
    if stage_id == "00-lock":
        for old in d.glob("lock.*"):
            old.unlink()
        dst = d / f"lock{src.suffix}"
        dst.write_bytes(src.read_bytes())
        char.log(step="lock", model=cand.get("model"), parent=None, candidate=str(src.relative_to(d)), picked=True, kept=dst.name,
                 **({"variant": cand["variant"]} if cand.get("variant") else {}))
        return dst.name
    _, n, title, instruction, _ = next(x for x in stages(char) if x[0] == stage_id)
    parent = Path(rnd["parent"] or "lock")
    return core.keep(char, n, title, instruction, parent, cand.get("model"), src).name


def status(name):
    """Everything the page shows for one character."""
    d = character(name)
    desc = (d / "description.txt").read_text() if (d / "description.txt").exists() else ""
    notes = (d / "notes.txt").read_text() if (d / "notes.txt").exists() else ""
    steps_file = d / "steps.txt"
    steps_text = steps_file.read_text() if steps_file.exists() else (core.HERE / "steps.txt").read_text()
    char = core.Character(d, need_lock=False) if desc.strip() else None
    kind_file = d / "kind.txt"
    kind = "place" if kind_file.exists() and kind_file.read_text().strip() == "place" else "character"
    if not steps_file.exists() and kind == "place":
        steps_text = (core.HERE / "steps-place.txt").read_text()
    style = (d / "style.txt").read_text() if (d / "style.txt").exists() else ""
    out = {"name": name, "kind": kind, "description": desc, "notes": notes, "style": style, "brief_style": style_text() or "", "steps_text": steps_text,
           "own_steps": steps_file.exists(),
           "lock": char.lock.name if char and char.lock else None,
           "reference": f"{PREFIX}/files/{name}/{char.reference.name}?v={int(char.reference.stat().st_mtime)}" if char and char.reference else None,
           "lock_v": int(char.lock.stat().st_mtime) if char and char.lock else 0,
           "trigger": char.trigger if char else None, "stages": [], "set": []}
    img, src = plate()
    out["plate"] = img and {"url": f"{PREFIX}/files/{img.relative_to(ROOT)}?v={int(img.stat().st_mtime)}", "from": src}
    if not char:
        return out
    for sid, n, title, instruction, parent_name in stages(char):
        st = stage_state(d, sid)
        live = _running.get((name, sid), {})
        kept = kept_for(char, sid, title)
        rounds = [dict(r, candidates=[dict(c, url=f"{PREFIX}/files/{name}/runs/{sid}/{r['round']}/{c['file']}") for c in r["candidates"]])
                  for r in st["rounds"]]
        last = st["rounds"][-1] if st["rounds"] else None
        review = bool(last and last.get("batch") and last.get("candidates") and not (st.get("pick") or {}).get("round") == last["round"]
                      and not (kept and last.get("kept_from")))
        out["stages"].append({"id": sid, "n": n, "title": title, "instruction": instruction, "parent": parent_name,
                              "kept": f"{PREFIX}/files/{name}/{kept.relative_to(d)}?v={int(kept.stat().st_mtime)}" if kept else None,
                              "rounds": rounds, "pick": st.get("pick"), "running": live.get("status") == "running",
                              "review": review})
    for p in sorted((d / "set").iterdir()) if (d / "set").is_dir() else []:
        if p.suffix != ".txt":
            cap = p.with_suffix(".txt")
            out["set"].append({"file": p.name, "url": f"{PREFIX}/files/{name}/set/{p.name}", "caption": cap.read_text().strip() if cap.exists() else ""})
    b = _batch.get(name)
    out["batch"] = b and {k: b[k] for k in ("status", "done", "total", "current", "notes")}
    out["done"] = bool(out["stages"]) and all(x["kept"] for x in out["stages"]) and not any(x["review"] or x["running"] for x in out["stages"])
    out["previous"] = sorted(p.name for p in (d / "previous").iterdir() if p.is_dir()) if (d / "previous").is_dir() else []
    return out


def campaigns():
    """The campaign folders under the markdown roots that have a characters.md or a world.md."""
    out = []
    for root in MD_ROOTS:
        for d in sorted(root.iterdir()) if root.is_dir() else []:
            if d.is_dir() and not d.name.startswith(("_", ".")) and (room_file(d, "characters.md") or room_file(d, "world.md")):
                out.append(d.name)
    return out


def room_file(d, name):
    """production/<name> if the room has been there, else intake's copy, else the root."""
    for rel in (f"production/{name}", f"preproduction/{name}", name):
        if (d / rel).exists():
            return d / rel
    return None


def subjects(campaign):
    """The campaign's characters (from characters.md) and places (from world.md), each with
    the text that becomes its description."""
    d = next((r / campaign for r in MD_ROOTS if (r / campaign).is_dir()), None)
    if d is None:
        raise FileNotFoundError(campaign)
    people, world, story = room_file(d, "characters.md"), room_file(d, "world.md"), room_file(d, "story.md")
    if not people and not world:
        raise FileNotFoundError(f"{campaign} has no characters.md or world.md")
    rel = lambda f: str(f.relative_to(f.parents[2])) if f else None
    where = places(world) if world else []
    return {"campaign": campaign, "file": rel(people), "characters": cast(people) if people else [],
            "hard_sf": bool(world and "80/15/5" in world.read_text()),      # the world declares the rule: places start with it
            "world_file": rel(world), "places": where,
            "story_file": rel(story), "scenes": scenes(story, where) if story else [],
            "props": listed(world, "key props") if world else [],            # the canon's own lists:
            "key_scenes": listed(story, "key scenes") if story else []}      # what the Art Department draws


def listed(f, title):
    """[{name, look}] - the "### Name" entries under a "## <title>" section (Key props in world.md,
    Key scenes in story.md): lists the canon keeps on purpose, so nothing has to be guessed."""
    out, inside = [], False
    for sec in md_read_file(f)["sections"]:
        if sec["depth"] <= 2:
            inside = sec["heading"].strip().lower() == title
        elif inside and sec["depth"] == 3 and sec["body"]:
            out.append({"name": sec["heading"].strip(), "look": sec["body"]})
    return out


def scenes(f, where):
    """[(name, look)] from story.md, in story order: the numbered lines of a page plot
    ("5. Explore the abandoned mine...") and the ### sections under a chapter heading. Each
    scene's look is its own text, then the world.md text of every place it names, so the
    lock can be rolled from what the story says happens there and what the place looks like."""
    secs = md_read_file(f)["sections"]
    out, chapter = [], None
    for sec in secs:
        head = sec["heading"]
        if sec["depth"] <= 2:
            m = re.match(r"(?:chapter|ch\.?)\s*(\d+|[ivx]+)\b", head, re.I)
            chapter = f"ch{m.group(1)}" if m else None
            if sec["depth"] == 2 and re.search(r"\bpage(s| plot|-by-page)\b|\bbeats\b", head, re.I):
                for n, text in re.findall(r"^\s*(\d+)[.)]\s+(.+)$", sec["body"], re.M):
                    out.append({"name": f"p{n} · {text.strip().rstrip('.')}", "look": text.strip()})
        elif sec["depth"] == 3 and chapter and sec["body"] and not re.match(r"function|chapter change|material status", head, re.I):
            out.append({"name": f"{chapter} · {head}", "look": sec["body"]})
    for sc in out:
        named = [w for w in where if re.search(r"\b" + re.escape(re.sub(r" \(.*\)$", "", w["name"])) + r"\b", sc["look"], re.I)]
        seen = set()
        for w in named:
            base = re.sub(r" \(.*\)$", "", w["name"])
            if base in seen or base.lower() in ("setting and geography", "daily life and lived texture"):
                continue
            seen.add(base)
            sc["look"] += f"\n\nWhere, from world.md - {w['name']}: {w['look']}"
    return out


PLACE = re.compile(r"\b(setting|geograph\w*|location\w*|place\w*|city|cities|environment|texture|district\w*|building\w*|rooms?)\b", re.I)


def places(f):
    """[(name, look)] from world.md: every section under a heading that reads like a place -
    or, when nothing does, every section. A section's look is its own text and its
    subsections', so "Keel" carries everything said about Keel."""
    secs = md_read_file(f)["sections"]
    out = []
    for i, s in enumerate(secs):
        if s["depth"] == 1:
            continue
        chain, depth = [s["heading"]], s["depth"]
        for prev in reversed(secs[:i]):
            if prev["depth"] < depth:
                chain.append(prev["heading"]); depth = prev["depth"]
        parts = [s["body"]] if s["body"] else []
        for nxt in secs[i + 1:]:
            if nxt["depth"] <= s["depth"]:
                break
            if nxt["body"]:
                parts.append(f"{nxt['heading']}: {nxt['body']}")
        out.append({"name": s["heading"], "under": chain[1] if len(chain) > 1 else "", "look": "\n".join(parts).strip(),
                    "placey": any(PLACE.search(h) for h in chain)})
    if any(x["placey"] for x in out):
        out = [x for x in out if x["placey"]]
    out = [x for x in out if x["look"]]
    count = {}
    for x in out:
        count[x["name"]] = count.get(x["name"], 0) + 1
    for x in out:
        if count[x["name"]] > 1 and x["under"]:
            x["name"] = f"{x['name']} ({x['under']})"
        x.pop("placey"); x.pop("under")
    return out


def cast(f):
    """[(name, look)] from the campaign's characters.md: each character heading and its section."""
    text = f.read_text()
    people = re.compile(r"\bcharacters?\b|\bcast\b|\bensemble\b", re.I)
    out, name, body, inside, top = [], None, [], False, None
    def close():
        if name:
            look = "\n".join(body).strip()
            if look:
                out.append({"name": name, "look": look})
    for line in text.split("\n"):
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if not m:
            if name is not None:
                body.append(line)
            continue
        depth, head = len(m.group(1)), m.group(2).strip().rstrip("*").strip()
        if depth == 1:
            close(); name, body = None, []
            top = head; inside = bool(people.search(head))
        elif depth == 2:
            close(); name, body = None, []
            if people.search(head):
                inside = True
            elif inside and top and people.search(top) and 1 <= len(head.split()) <= 4:
                name = head          # "# Characters" then "## Ada"
            else:
                inside = False
        elif depth == 3 and inside and 1 <= len(head.split()) <= 4:
            close(); name, body = head, []
        elif name is not None:
            body.append(line)        # a deeper heading inside the character's own section
    close()
    return out


def md_files():
    out = []
    for root in MD_ROOTS:
        if not root.is_dir():
            continue
        for p in sorted(root.rglob("*.md")):
            rel = p.relative_to(root)
            if any(part.startswith(("_", ".")) or part == "previous" for part in rel.parts):
                continue
            out.append(f"{root.name}/{rel}")
    return out


def md_read(path):
    root_name, _, rel = path.partition("/")
    root = next((r for r in MD_ROOTS if r.name == root_name), None)
    if root is None:
        raise FileNotFoundError(path)
    p = (root / rel).resolve()
    if root not in p.parents or p.suffix != ".md" or not p.exists():
        raise FileNotFoundError(path)
    d = md_read_file(p)
    return {"path": path, "text": d["text"], "sections": [s for s in d["sections"] if s["body"]]}


def md_read_file(p):
    """{text, sections: [{heading, depth, body}]} - every heading, with its own text (which may be empty)."""
    text = p.read_text()
    sections, cur = [], None
    for line in text.split("\n"):
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            cur = {"heading": m.group(2).strip().rstrip("*").strip(), "depth": len(m.group(1)), "body": []}
            sections.append(cur)
        elif cur is not None:
            cur["body"].append(line)
    for s in sections:
        s["body"] = "\n".join(s["body"]).strip()
    return {"text": text, "sections": sections}


# ---- the page ---------------------------------------------------------------------------------------

PAGE = r"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sheets</title>
<style>
:root{--bg:#171717;--panel:#222;--line:#3a3a3a;--ink:#eee;--muted:#9a9a9a;--go:#2563eb;--ok:#22c55e;--bad:#ef4444}
body{margin:0;font:14px/1.45 system-ui,sans-serif;background:var(--bg);color:var(--ink)}
header{display:flex;gap:.8rem;align-items:center;padding:.6rem 1rem;border-bottom:1px solid var(--line);flex-wrap:wrap}
header h1{font-size:1rem;margin:0 .4rem 0 0}header select,header button{font:inherit;padding:.3rem .5rem;background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:4px}
main{display:grid;grid-template-columns:minmax(16rem,22rem) 1fr;gap:1rem;padding:1rem}
@media(max-width:60rem){main{grid-template-columns:1fr}}
.card{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:.8rem;margin-bottom:1rem}
.card h2{font-size:.8rem;margin:0 0 .5rem;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
textarea,input[type=text]{width:100%;box-sizing:border-box;font:inherit;font-size:.82rem;background:var(--bg);color:var(--ink);border:1px solid var(--line);border-radius:4px;padding:.4rem}
textarea.mono{font-family:ui-monospace,monospace;min-height:10rem}
button{font:inherit;padding:.35rem .7rem;border:1px solid var(--line);border-radius:4px;background:var(--panel);color:var(--ink);cursor:pointer}
button.go{background:var(--go);border-color:var(--go)}button.ok{background:var(--ok);border-color:var(--ok);color:#111}button:disabled{opacity:.45;cursor:default}
.hint{color:var(--muted);font-size:.78rem}.row{display:flex;gap:.5rem;align-items:center;flex-wrap:wrap;margin:.4rem 0}
.err{color:var(--bad);font-size:.76rem}.good{color:var(--ok)}
details summary{cursor:pointer;color:var(--muted);font-size:.8rem;margin:.2rem 0}
/* captured: the lock big, the kept steps small */
.captured .lock img{width:100%;border-radius:4px;border:1px solid var(--line)}
.captured .lock .empty{border:1px dashed var(--line);border-radius:4px;padding:1.4rem .8rem;text-align:center;color:var(--muted);font-size:.8rem}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(88px,1fr));gap:.4rem;margin-top:.6rem}
.grid figure{margin:0;cursor:pointer;position:relative}.grid img{width:100%;border-radius:3px;border:2px solid transparent;display:block}
.grid figure.kept::after{content:"redo";position:absolute;top:.3rem;right:.3rem;font-size:.62rem;padding:.05rem .35rem;border-radius:3px;background:rgba(0,0,0,.65);color:#fff;opacity:0;transition:opacity .15s}
.grid figure.kept:hover::after{opacity:1}.grid figure:hover img{border-color:var(--go)}
.captured .lock{position:relative;cursor:pointer}.captured .lock:hover img{outline:2px solid var(--go)}
.grid figure.now img{border-color:var(--go)}.grid figure.kept img{border-color:var(--ok)}
.grid figcaption{font-size:.64rem;color:var(--muted);margin-top:.15rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.grid .todo{aspect-ratio:2/3;border:1px dashed var(--line);border-radius:3px;display:grid;place-items:center;color:var(--muted);font-size:.7rem}
/* the workspace */
.strip{display:flex;gap:.3rem;flex-wrap:wrap;margin-bottom:.6rem}
.strip button{font-size:.72rem;padding:.15rem .5rem;font-family:ui-monospace,monospace}
.strip button.kept{border-color:var(--ok)}.strip button.now{background:var(--go);border-color:var(--go)}
.stage-head{display:flex;gap:1rem;align-items:flex-start;margin-bottom:.6rem}
.stage-head img{width:96px;border-radius:4px;border:1px solid var(--line)}
.stage-head h3{margin:0 0 .2rem;font-size:1rem}.stage-head h3 b{font-family:ui-monospace,monospace;color:var(--muted);font-weight:500;margin-right:.4rem}
.roll{border:1px solid var(--line);border-radius:6px;padding:.5rem .7rem;margin-bottom:.6rem}
.roll.now{border-color:var(--go)}.roll .who{font-size:.76rem;color:var(--muted)}
.check{background:#3b2a05;border:1px solid #b45309;color:#fde68a;border-radius:6px;padding:.55rem .8rem;margin:.5rem 0;font-size:.8rem;line-height:1.5}
.check b{color:#fff;font-size:.86rem;letter-spacing:.02em}
.cands figure.pick::before{content:"looked closely? hands · fingers · eyes · overlaps";position:absolute;left:.3rem;right:.3rem;bottom:.3rem;font-size:.62rem;text-align:center;padding:.2rem;background:rgba(180,83,9,.9);color:#fff;border-radius:3px}
.cands figure{position:relative}
.cands figure.waiting{cursor:default;border-color:transparent;background:#1a1a1a}
.cands figure.waiting:hover{border-color:transparent}
.cands .slot{aspect-ratio:2/3;border-radius:3px;background:linear-gradient(110deg,#1e1e1e 30%,#262626 50%,#1e1e1e 70%);background-size:200% 100%;animation:shimmer 1.6s linear infinite;display:grid;place-items:center;color:var(--muted);font-size:.7rem}
@keyframes shimmer{to{background-position:-200% 0}}
.cands figure.failed .slot{animation:none;background:#2a1717;color:var(--bad)}
.cands{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:.6rem;margin-top:.5rem}
.cands figure{margin:0;background:var(--bg);padding:.3rem;border-radius:4px;cursor:pointer;border:2px solid transparent}
.cands figure:hover{border-color:var(--go)}.cands figure.pick{border-color:var(--ok)}
.cands img{width:100%;border-radius:3px;display:block}.cands figcaption{font-size:.68rem;color:var(--muted);margin-top:.2rem}
.acts{position:sticky;bottom:0;background:var(--panel);padding:.6rem 0 0;border-top:1px solid var(--line);margin-top:.6rem}
.models{display:flex;gap:.3rem;flex-wrap:wrap;margin:.3rem 0 .5rem}
.models label{font-size:.72rem;font-family:ui-monospace,monospace;padding:.15rem .5rem;border:1px solid var(--line);border-radius:12px;cursor:pointer;color:var(--muted)}
.models label.on{border-color:var(--go);color:var(--ink);background:color-mix(in srgb,var(--go) 18%,var(--panel))}
.models input{display:none}.models i{font-style:normal;opacity:.7;margin-left:.3rem}
.roll .who button{font-size:.68rem;padding:.05rem .4rem;margin-left:.4rem}
.done{background:#052e16;border:1px solid var(--ok);border-radius:6px;padding:.8rem 1rem;margin-bottom:.8rem}
.done h3{margin:0 0 .3rem;color:var(--ok)}.done a.go{display:inline-block;text-decoration:none;color:#fff;margin-top:.4rem}
.sheet{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:.5rem;margin-top:.6rem}
.sheet figure{margin:0;background:var(--bg);padding:.3rem;border-radius:4px}.sheet img{width:100%;border-radius:3px;display:block}
.sheet figcaption{font-size:.64rem;color:var(--muted);margin-top:.2rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.strip button.review{border-color:#f59e0b;color:#fde68a}.grid figure.review img{border-color:#f59e0b}
.batch{background:#1e293b;border:1px solid #3b82f6;border-radius:6px;padding:.5rem .8rem;margin-bottom:.6rem;font-size:.8rem}
.working{display:inline-block;width:.5rem;height:.5rem;border-radius:50%;background:var(--go);animation:pulse 1.2s infinite;margin-right:.4rem}
@keyframes pulse{50%{opacity:.2}}
#view{position:fixed;inset:0;background:rgba(0,0,0,.92);z-index:50;display:grid;grid-template-rows:auto 1fr auto;grid-template-columns:3rem 1fr 3rem;color:var(--ink)}
#view[hidden]{display:none}
.v-top{grid-column:1/-1;display:flex;gap:1rem;align-items:center;padding:.5rem 1rem;font-size:.85rem}.v-top #v-title{font-weight:600}.v-top button{margin-left:auto}
.v-img{display:grid;place-items:center;overflow:auto;padding:.5rem}.v-img img{max-width:100%;max-height:calc(100vh - 8rem);cursor:zoom-in;border-radius:4px}
.v-img img.zoom{max-width:none;max-height:none;width:200%;cursor:zoom-out}
.v-nav{font-size:2rem;background:transparent;border:0;color:var(--ink);cursor:pointer}.v-nav:disabled{opacity:.2}
.v-bottom{grid-column:1/-1;display:flex;gap:1rem;align-items:center;justify-content:center;padding:.6rem 1rem;flex-wrap:wrap}
.v-check{color:#fde68a;font-size:.8rem}
dialog{background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:6px;width:min(720px,92vw);max-height:80vh}
dialog .sec{padding:.4rem .5rem;border-bottom:1px solid var(--line);cursor:pointer}dialog .sec:hover{background:var(--bg)}
dialog .sec small{color:var(--muted);display:block;white-space:pre-wrap;max-height:4.5em;overflow:hidden}
</style>
<header><h1>Sheets</h1>
  <label class="hint">campaign <select id="camp"></select></label>
  <label class="hint">character, scene or place <select id="cast"><option value="">choose…</option></select></label>
  <button id="make" class="go">Start</button>
  <span class="hint">· open</span><select id="who"></select>
  <span class="hint" id="top-hint"></span></header>
<main>
<aside>
  <div class="card"><details id="setup"><summary>Setup: description, notes, steps, models</summary>
    <h2 style="margin-top:.6rem">Description</h2>
    <textarea id="desc" rows="7" placeholder="The character's look from characters.md, a place from world.md - or paste your own."></textarea>
    <div class="row"><button id="from-md">From a .md file…</button></div>
    <h2 style="margin-top:.8rem">Notes for every prompt</h2>
    <textarea id="notes" rows="2" placeholder="'always the burn scar on the left hand', 'never a hat'"></textarea>
    <h2 style="margin-top:.8rem">Style</h2>
    <textarea id="style" rows="3" placeholder="How it is drawn. Empty: the brief's visual direction."></textarea>
    <div class="row"><button id="style-photo">Photo-real</button><button id="notes-hardsf" title="adds the 80/15/5 rule to the notes for every prompt">Hard SF 80/15/5</button><span class="hint" id="style-hint"></span></div>
    <h2 style="margin-top:.8rem">Steps</h2>
    <textarea id="steps" class="mono" spellcheck="false"></textarea>
    <p class="hint" style="margin:.3rem 0 0"><code>name | what to change | parent</code> per line. Parent: a step name or <code>lock</code>; empty builds on the previous keep. <span id="steps-hint"></span></p>
    <h2 style="margin-top:.8rem">Models</h2>
    <p class="hint" style="margin:0">Toggled beside the Roll button, before every roll. Add one by id here:</p>
    <div class="row"><input id="model-add" type="text" placeholder="provider/model-id" style="flex:1"><button id="model-add-go">Add</button></div>
    <div class="row"><label class="hint">candidates per model <input id="each" type="number" min="1" max="4" value="2" style="width:3rem"></label></div>
    <div class="row"><button class="go" id="save">Save setup</button><span class="hint" id="said"></span></div>
    <div class="row" style="margin-top:.8rem"><button id="reset" title="start this one over; the reference and the work so far go to previous/">Reset…</button><span class="hint" id="reset-hint"></span></div>
    <div class="row"><label><input type="file" id="lock-file" accept="image/*" hidden><button onclick="document.getElementById('lock-file').click()">Upload a lock image instead</button></label>
      <label><input type="file" id="ref-file" accept="image/*" hidden><button onclick="document.getElementById('ref-file').click()">Roll the lock from a reference image…</button></label></div>
    <p class="hint" style="margin:.2rem 0 0">A reference (a screenshot, a photo, a game scene) fixes what is where; the lock is redrawn from it in the book's style, with your note. It is never kept itself.</p>
  </details></div>
  <div class="card captured"><h2>Captured</h2>
    <div class="lock" id="lock-box"></div>
    <div class="grid" id="kept-grid"></div>
    <p class="hint" id="set-hint" style="margin:.5rem 0 0"></p></div>
  <div class="card" id="fix-card"><details id="fix-box"><summary>Fix everywhere: one note, every kept image</summary>
    <p class="hint" style="margin:.4rem 0">Spotted something that carried through - a strap blurring into a hand, a wrong button? One note, and every kept image (the lock too) is rolled again from itself with it. Then you review each.</p>
    <textarea id="fix-notes" rows="2" placeholder="'the shoulder strap must not touch the hand; the hand is fully clear of it'"></textarea>
    <div class="row"><button class="go" id="fix-all">Fix everywhere</button><label class="hint">per model <input id="fix-each" type="number" min="1" max="3" value="1" style="width:3rem"></label><span class="hint" id="fix-said"></span></div>
  </details></div>
</aside>
<section>
  <div class="card"><div class="strip" id="strip"></div><div id="work"></div></div>
</section>
</main>
<div id="view" hidden>
  <div class="v-top"><span id="v-title"></span><span class="hint">← → to move · click the image or <b>Enter</b> to pick · Esc to close</span><button id="v-close">✕</button></div>
  <button class="v-nav" id="v-prev">‹</button>
  <div class="v-img"><img id="v-pic" alt=""></div>
  <button class="v-nav" id="v-next">›</button>
  <div class="v-bottom">
    <span class="v-check" id="v-check"></span>
    <button class="ok" id="v-pick">Pick this one</button>
  </div>
</div>
<dialog id="md"><div class="row"><select id="md-file" style="flex:1"></select><button onclick="document.getElementById('md').close()">close</button></div>
  <p class="hint">Click a section to use it as the description.</p><div id="md-secs"></div></dialog>
<script>
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const DEFAULT_MODELS = %MODELS%;
const BASE = "%PREFIX%";
const PHOTO = %PHOTO%;
const HARD_SF = %HARD_SF%;
let who = null, st = null, poll = null, castData = null, current = null, lastDrawn = "", notesDraft = {};
let catalog = [], on = new Set(), typical = {}, keptRate = {};
/* a fresh lock with a style plate: rolled from the words alone, with the plate, or both side by side */
let variants = new Set(JSON.parse(localStorage.getItem("sheets-variants") || '["plain","styled"]'));
const VARIANT = { plain: "text only", styled: "with the style plate" };
/* what to look for before picking, by kind */
const CHECK = {
  character: { short: "⚠ zoom in: hands and fingers · anything passing through anything · eyes · the costume as described · no text",
    long: `hands and fingers (count them) · a limb or hair passing <i>through</i> clothes, props or the body · eyes level and matching · extra or missing straps, buttons, pockets · the costume exactly as described · nothing the description does not have · no text or watermark.` },
  place: { short: "⚠ zoom in: perspective · doors, stairs and windows at one scale · nothing floating · repeated tiles · no readable text",
    long: `perspective lines that agree · doors, stairs, windows and furniture at one believable scale · nothing floating or cut off mid-air · the same texture stamped over and over · the place exactly as described · nothing the description does not have · no readable signs, text or watermark.` },
};
const check = () => CHECK[st?.kind === "place" ? "place" : "character"];
function loadModels(d) {
  catalog = d.models; typical = d.seconds || {}; keptRate = d.kept || {};
  const saved = JSON.parse(localStorage.getItem("sheets-on") || "null");
  const extra = JSON.parse(localStorage.getItem("sheets-extra") || "[]");
  for (const m of extra) if (!catalog.includes(m)) catalog.push(m);
  const stamp = JSON.stringify(d.default);
  const fresh = localStorage.getItem("sheets-default") !== stamp;     // the defaults changed: take them
  if (fresh) localStorage.setItem("sheets-default", stamp);
  on = new Set((fresh ? d.default : (saved || d.default)).filter((m) => catalog.includes(m)));
  if (!on.size) on = new Set(d.default);
}
const chosen = () => catalog.filter((m) => on.has(m));
const secs = (n) => n == null ? "" : n >= 90 ? `${Math.round(n / 60)}m` : `${Math.round(n)}s`;
function modelChips() {
  const rate = (m) => keptRate[m]?.[1] ? ` <i>${keptRate[m][0]}/${keptRate[m][1]} kept</i>` : "";
  return `<div class="models" id="models">${catalog.map((m) => `<label class="${on.has(m) ? "on" : ""}" title="${typical[m] ? `usually ${secs(typical[m])}` : "no timing yet"}${keptRate[m]?.[1] ? ` · ${keptRate[m][0]} kept of ${keptRate[m][1]} rolled, every subject` : ""}"><input type="checkbox" data-m="${esc(m)}" ${on.has(m) ? "checked" : ""}>${esc(m)}${typical[m] ? ` <i>${secs(typical[m])}</i>` : ""}${rate(m)}</label>`).join("")}</div>`;
}
/* a roll takes about as long as its slowest model (they run at once) */
function estimate() {
  const known = chosen().map((m) => typical[m]).filter(Boolean);
  return known.length ? Math.max(...known) : null;
}
async function api(path, opts = {}) {
  const r = await fetch(BASE + path, { method: opts.method || "GET", headers: { "content-type": "application/json" }, body: opts.body ? JSON.stringify(opts.body) : undefined });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.error || r.statusText);
  return d;
}
/* ---- who ---- */
async function listWho() {
  const { characters, kinds } = await api("/api/characters");
  $("#who").innerHTML = `<option value="">${characters.length ? "started…" : "(none yet)"}</option>` + characters.map((c) => `<option value="${esc(c)}" ${c === who ? "selected" : ""}>${esc(c)}${kinds?.[c] === "place" ? " (place)" : ""}</option>`).join("");
  if (!who && characters.length) { who = characters[0]; $("#who").value = who; }
}
async function listCampaigns() {
  const { campaigns } = await api("/api/campaigns");
  $("#camp").innerHTML = campaigns.map((c) => `<option ${c === localStorage.getItem("sheets-camp") ? "selected" : ""}>${esc(c)}</option>`).join("") || `<option value="">(no campaign with a characters.md)</option>`;
  await listCast();
}
async function listCast() {
  const camp = $("#camp").value; castData = null;
  $("#cast").innerHTML = `<option value="">choose…</option>`;
  if (!camp) return;
  localStorage.setItem("sheets-camp", camp);
  try {
    castData = await api(`/api/campaigns/${encodeURIComponent(camp)}`);
    const group = (label, list, k) => list.length ? `<optgroup label="${label}">${list.map((c, i) => `<option value="${k}${i}">${esc(c.name)}</option>`).join("")}</optgroup>` : "";
    $("#cast").innerHTML = `<option value="">choose…</option>` + group("characters", castData.characters, "c") + group("scenes, from the story", castData.scenes || [], "s") + group("places, from the world", castData.places, "p");
  } catch (err) { $("#top-hint").textContent = err.message; }
}
$("#camp").onchange = listCast;
$("#make").onclick = async () => {
  const v = $("#cast").value, list = { c: "characters", s: "scenes", p: "places" }[v[0]], kind = list === "characters" ? "character" : "place";
  const c = castData?.[list]?.[+v.slice(1)];
  if (!c) { $("#top-hint").textContent = "choose a character, a scene or a place first"; return; }
  const name = c.name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40);
  try {
    await api("/api/characters", { method: "POST", body: { name, kind } });
    await api(`/api/characters/${name}`, { method: "PUT", body: { description: `${c.name}: ${c.look}`, ...(kind === "place" && castData.hard_sf ? { notes: HARD_SF } : {}) } });
    who = name; current = null; lastDrawn = ""; await listWho(); await load(true);
    $("#top-hint").textContent = `${c.name}: description filled from ${{ characters: castData.file, scenes: castData.story_file, places: castData.world_file }[list]}.`;
  } catch (err) { $("#top-hint").textContent = err.message; }
};
$("#who").onchange = async () => { if ($("#who").value) { who = $("#who").value; current = null; lastDrawn = ""; await load(true); } };

/* ---- load: redraw only when something changed, so nothing blinks ---- */
setInterval(() => {
  const now = Date.now() / 1000;
  document.querySelectorAll(".elapsed[data-since]").forEach((el) => { const t = +el.dataset.since; if (t) el.textContent = `working ${secs(now - t)}`; });
}, 1000);
async function load(force) {
  if (!who) { $("#work").innerHTML = `<p class="hint">Choose a campaign and a character, then Start.</p>`; return; }
  st = await api(`/api/characters/${who}`);
  const key = JSON.stringify([st.stages, st.set, st.lock, st.lock_v, current, st.batch, st.done, st.plate]);
  if (force || key !== lastDrawn) { lastDrawn = key; draw(); }
  if (force) {
    $("#desc").value = st.description; $("#notes").value = st.notes || ""; $("#style").value = st.style || ""; $("#steps").value = st.steps_text;
    $("#style-hint").textContent = st.brief_style ? `empty means the brief's: “${st.brief_style.slice(0, 90)}…”` : "";
    $("#steps-hint").textContent = st.own_steps ? "These are this one's own steps; the default file no longer applies to it." : `The default for a ${st.kind}; edit to give this one its own.`;
    $("#reset-hint").textContent = st.previous?.length ? `${st.previous.length} previous version${st.previous.length > 1 ? "s" : ""} in sheets/characters/${who}/previous/` : "";
  }
  $("#top-hint").textContent = st.trigger ? `${who}${st.kind === "place" ? " (a place)" : ""} · trigger word ${st.trigger}` : "";
  $("#v-check").textContent = check().short;
  const busy = st.stages.some((s) => s.running) || st.batch?.status === "running";
  if (busy && !poll) poll = setInterval(load, 2500);
  if (!busy && poll) { clearInterval(poll); poll = null; loadModels(await api("/api/models")); lastDrawn = ""; draw(); }
}
function draw() {
  if (!st.stages.length) { $("#work").innerHTML = `<p class="hint">Open Setup on the left and write the description first.</p>`; $("#strip").innerHTML = ""; return; }
  if (!current || !st.stages.find((s) => s.id === current)) current = (st.stages.find((s) => !s.kept) || st.stages[st.stages.length - 1]).id;
  drawCaptured(); drawStrip(); drawStage();
  const fixing = st.batch?.status === "running";
  $("#fix-all").disabled = fixing || !st.stages.some((s) => s.kept);
  $("#fix-said").textContent = fixing ? `fixing ${st.batch.done + 1} of ${st.batch.total}: ${st.batch.current}` : st.batch?.status === "done" ? `rolled ${st.batch.total} stages with “${st.batch.notes}” - review each (amber)` : "";
}
/* ---- left: what is captured ---- */
function drawCaptured() {
  const lock = st.stages[0];
  $("#lock-box").innerHTML = lock.kept ? `<img src="${lock.kept}" title="the lock">` : `<div class="empty">no lock yet - roll it on the right</div>`;
  $("#kept-grid").innerHTML = st.stages.slice(1).map((s) => `<figure data-go="${esc(s.id)}" class="${s.kept ? "kept" : ""} ${s.review ? "review" : ""} ${s.id === current ? "now" : ""}">
    ${s.kept ? `<img src="${s.kept}">` : `<div class="todo">${s.n}</div>`}<figcaption title="${esc(s.title)}">${esc(s.title)}</figcaption></figure>`).join("");
  const done = st.stages.slice(1).filter((s) => s.kept).length;
  $("#set-hint").textContent = `${done} of ${st.stages.length - 1} steps kept${done ? ` · sheets/characters/${who}/set/` : ""}. Click any tile to open it, or redo it.`;
}
$("#kept-grid").onclick = (e) => { const f = e.target.closest("figure[data-go]"); if (f) { current = f.dataset.go; lastDrawn = ""; draw(); } };
$("#lock-box").onclick = () => { current = "00-lock"; lastDrawn = ""; draw(); };
/* ---- right: the workspace ---- */
function drawStrip() {
  $("#strip").innerHTML = st.stages.map((s) => `<button data-go="${esc(s.id)}" class="${s.kept ? "kept" : ""} ${s.review ? "review" : ""} ${s.id === current ? "now" : ""}">${s.n === 0 ? "lock" : String(s.n).padStart(2, "0")}${s.running ? " …" : s.review ? " !" : ""}</button>`).join("");
}
$("#strip").onclick = (e) => { const b = e.target.closest("button[data-go]"); if (b) { current = b.dataset.go; lastDrawn = ""; draw(); } };
/* one dark card per candidate still to come, labelled with its model; failures in red */
function slots(r, running) {
  const expected = (r.models || []).flatMap((m) => Array.from({ length: r.each || 1 }, () => m));
  const back = r.candidates.map((c) => c.model);
  for (const m of back) { const i = expected.indexOf(m); if (i >= 0) expected.splice(i, 1); }
  const failed = (r.errors || []).map((e) => e.split(" #")[0]);
  for (const m of failed) { const i = expected.indexOf(m); if (i >= 0) expected.splice(i, 1); }
  return (running ? expected.map((m) => `<figure class="waiting"><div class="slot">waiting on<br>${esc(m.split("/").pop())}</div><figcaption>${esc(m)}${typical[m] ? ` · usually ${secs(typical[m])}` : ""}</figcaption></figure>`).join("") : "")
    + failed.map((m) => `<figure class="waiting failed"><div class="slot">failed</div><figcaption>${esc(m)}</figcaption></figure>`).join("");
}
function drawStage() {
  const s = st.stages.find((x) => x.id === current);
  const isLock = s.n === 0, rounds = s.rounds || [], pick = s.pick;
  const next = st.stages.find((x) => x.n > s.n && !x.kept);
  const prev = st.stages.find((x) => x.id === current) && st.stages[st.stages.indexOf(s) - 1];
  const parentImg = isLock ? (s.kept ? null : st.reference) : (s.parent ? st.stages.find((x) => x.title === s.parent)?.kept : (st.stages.slice(0, st.stages.indexOf(s)).reverse().find((x) => x.kept)?.kept));
  const can = isLock || parentImg;
  const plated = isLock && !pick && !s.kept && st.plate;      // the next roll can use the style plate
  const perModel = (plated ? [...variants].filter((v) => VARIANT[v]).length || 1 : 1) * (+$("#each").value || 2);
  const reviews = st.stages.filter((x) => x.review);
  const nextReview = reviews.find((x) => x.id !== current) || null;
  const doneBanner = st.done ? `<div class="done"><h3>✓ ${esc(who)} is done: the lock and ${st.stages.length - 1} steps, every one kept.</h3>
      <div class="hint">This is the ${st.kind === "place" ? "location" : "character"} sheet. Download it and train the LoRA on the folder: each image has its caption, trigger word <b>${esc(st.trigger)}</b>. Spot something later? Fix everywhere on the left, or click any tile to redo one.</div>
      <a class="go" href="${BASE}/api/characters/${who}/set.zip">Download the training set (.zip)</a>
      <div class="sheet">${st.stages.map((x) => `<figure><img src="${x.kept}"><figcaption>${esc(x.n === 0 ? "lock" : x.title)}</figcaption></figure>`).join("")}</div></div>` : "";
  const batchBanner = st.batch?.status === "running" ? `<div class="batch"><span class="working"></span>Fixing everywhere with “${esc(st.batch.notes)}”: ${st.batch.done} of ${st.batch.total} rolled, now ${esc(st.batch.current || "")}. Review the amber ones as they land.</div>`
    : reviews.length ? `<div class="batch">${reviews.length} stage${reviews.length > 1 ? "s" : ""} to review after the fix: ${s.review ? "this one first - " : ""}${nextReview ? `<a href="#" id="go-review">${esc(nextReview.n === 0 ? "lock" : nextReview.title)}</a>` : ""}. On each: keep the fixed one, or <b>Keep the old one</b> if the fix made it worse.</div>` : "";
  $("#work").innerHTML = doneBanner + batchBanner + `
    <div class="stage-head">
      ${parentImg ? `<img src="${parentImg}" title="${isLock ? "the reference: what is where" : "builds on this"}">` : s.kept && isLock ? `<img src="${s.kept}" title="the lock">` : ""}
      <div><h3><b>${isLock ? "lock" : String(s.n).padStart(2, "0")}</b>${esc(isLock ? "The lock" : s.title)}</h3>
        <div class="hint">${esc(s.instruction)}${!isLock ? ` · builds on ${esc(s.parent || "the previous keep")}` : st.reference && !s.kept ? " · redrawn from the reference: say in the note what to change, and how it should look" : ""}</div>
        ${plated ? `<div class="hint" style="margin-top:.3rem"><img src="${st.plate.url}" style="width:40px;vertical-align:middle;border-radius:3px;margin-right:.4rem" title="the style plate">style plate from <b>${esc(st.plate.from || "?")}</b>: its rendering, not its content. Tick below to roll text only, with the plate, or both side by side.</div>` : ""}
        ${isLock && s.kept ? `<div class="row" style="margin:.3rem 0 0">${st.plate?.from === who
            ? `<span class="good">✓ This lock is the book's style plate: new locks can be rolled with it.</span><button id="plate-clear">Clear it</button>`
            : `<button id="plate-set" title="new locks of other characters and places are rolled with this image for line, palette and light - never its content">Use as the book's style</button>${st.plate ? `<span class="hint">replaces the plate from ${esc(st.plate.from || "?")}</span>` : ""}`}</div>` : ""}
        ${s.kept ? `<div class="good" style="margin-top:.3rem">✓ kept${isLock ? " as the lock" : ""}. ${next ? `Next: <a href="#" id="go-next">${esc(next.n === 0 ? "lock" : next.title)}</a>.` : "Every step is kept."}</div>
        <div class="hint" style="margin-top:.2rem">Not right in context? Say what is off and <b>Fix the kept one</b>, or <b>Start over</b> from ${isLock ? "the description" : "its parent"}. Or click another candidate below and Keep it.</div>` : ""}
        ${!can ? `<div class="err" style="margin-top:.3rem">Nothing to build on yet: ${s.parent ? `keep <b>${esc(s.parent)}</b> first` : "lock first"}.</div>` : ""}
      </div></div>
    ${rounds.map((r, i) => `<div class="roll ${i === rounds.length - 1 ? "now" : ""}">
      <div class="who"><b>roll ${i + 1}</b> ${r.batch ? "fix everywhere" : r.from_pick ? (r.parent && s.kept && r.parent === s.kept.split("/").pop().split("?")[0] ? "fixing the kept one" : "from your pick") : r.from_reference ? "from the reference" : isLock ? "from the description" : "from the parent"}${r.notes ? ` · “${esc(r.notes)}”` : ""}${i === rounds.length - 1 && s.running ? ` <span class="working"></span><span class="elapsed" data-since="${r.started || 0}">working</span> · ${r.candidates.length} of ${(r.models || []).length * (r.each || 1)} back${estimate() ? `, usually about ${secs(estimate())}` : ""}` : r.stopped ? ` · stopped at ${r.candidates.length} of ${(r.models || []).length * (r.each || 1)}` : r.seconds ? ` · ${secs(r.seconds)}` : ""}${pick && pick.round === r.round ? ` · <span class="good">the pick is here</span>` : ""}</div>
      ${(r.errors || []).length ? `<div class="err">${r.errors.map(esc).join("<br>")}</div>` : ""}
      ${r.candidates.length && i === rounds.length - 1 ? `<div class="check"><b>⚠ LOOK CLOSELY BEFORE YOU PICK.</b> One flaw here is in every image trained from it. Zoom in and check:
        ${check().long}
        <b>Double-click a candidate to see it large</b> and step through with ← →. A candidate that is 90% right with one flaw loses to one that is 80% right and clean.</div>` : ""}
      ${r.candidates.length || (i === rounds.length - 1 && s.running) ? `<div class="cands">${r.candidates.map((c) => `<figure data-round="${esc(r.round)}" data-file="${esc(c.file)}" class="${pick && pick.round === r.round && pick.file === c.file ? "pick" : ""}"><img src="${c.url}"><figcaption>${esc(c.model)}${c.variant ? ` · <b>${esc(VARIANT[c.variant] || c.variant)}</b>` : ""}${c.seconds ? ` · ${secs(c.seconds)}` : ""}</figcaption></figure>`).join("")}${slots(r, i === rounds.length - 1 && s.running)}</div>` : ""}
    </div>`).join("")}
    ${!rounds.length && can ? `<p class="hint">Roll, then click the closest, say what is off, and roll again from it until one is right. Any candidate from any roll can be the pick. Double-click a candidate to see it full size.</p>` : ""}
    <div class="acts">
      ${modelChips()}
      ${plated ? `<div class="models" id="variants">${Object.entries(VARIANT).map(([v, label]) => `<label class="${variants.has(v) ? "on" : ""}"><input type="checkbox" data-v="${v}" ${variants.has(v) ? "checked" : ""}>${label}</label>`).join("")}</div>` : ""}
      <textarea id="stage-notes" rows="2" placeholder="${rounds.length ? "What is off in the closest one? Then roll again from it." : isLock && st.reference ? "How to redraw it: 'not a game scene: photo-real graphic novel, weathered concrete and steel, dusk'." : "Anything for this first roll (optional)."}">${esc(notesDraft[current] || "")}</textarea>
      <div class="row">
        ${s.running ? `<button id="stop" title="keep what has landed, stop waiting for the rest">Stop waiting</button>` : ""}
        ${s.kept ? `<button class="go" id="fix" ${s.running || !on.size ? "disabled" : ""}>Fix the kept one</button><button id="over" ${s.running || !can || !on.size ? "disabled" : ""}>Start over</button>`
                 : `<button class="go" id="roll" ${s.running || !can || !on.size ? "disabled" : ""}>${rounds.length ? (pick ? "Roll again from the pick" : "Roll again") : "Roll"}</button>`}
        <button class="ok" id="keep" ${pick ? "" : "disabled"} title="Looked at it at full size?">${isLock ? "Lock this one" : "Keep this one"}</button>
        ${s.review ? `<button id="dismiss" title="the fix made it worse: keep what was kept">Keep the old one</button>` : ""}
        <button id="undo" ${rounds.length && !s.running ? "" : "disabled"} title="drop the last roll and put the pick back">Undo last roll</button>
        <span class="hint" id="roll-hint">${s.running ? (pick ? "you can keep the pick now, or stop waiting and roll again from it" : "click one that is close enough as soon as it lands") : pick ? `pick: ${esc(pick.round)} ${esc(pick.file)}` : rounds.length ? "click the closest candidate, in any roll" : ""}${!s.running ? ` · ${on.size} model${on.size === 1 ? "" : "s"} × ${perModel}${estimate() ? `, about ${secs(estimate())}` : ""}` : ""}</span>
      </div></div>`;
  $("#models").onchange = (e) => {
    const m = e.target.dataset.m; if (!m) return;
    e.target.checked ? on.add(m) : on.delete(m);
    localStorage.setItem("sheets-on", JSON.stringify([...on]));
    e.target.parentElement.classList.toggle("on", e.target.checked);
    for (const id of ["#roll", "#fix", "#over"]) { const b = $(id); if (b) b.disabled = s.running || !can || !on.size; }
  };
  $("#variants")?.addEventListener("change", (e) => {
    const v = e.target.dataset.v; if (!v) return;
    e.target.checked ? variants.add(v) : variants.delete(v);
    if (!variants.size) { variants.add(v); e.target.checked = true; }       // one of the two, always
    localStorage.setItem("sheets-variants", JSON.stringify([...variants]));
    lastDrawn = ""; draw();
  });
  const setPlate = (name) => async () => {
    try { await api("/api/style", { method: "POST", body: { name } }); lastDrawn = ""; await load(true); }
    catch (err) { $("#top-hint").textContent = err.message; }
  };
  $("#plate-set")?.addEventListener("click", setPlate(who));
  $("#plate-clear")?.addEventListener("click", setPlate(null));
  $("#stop")?.addEventListener("click", async () => {
    try { await api(`/api/characters/${who}/stages/${current}/stop`, { method: "POST", body: {} }); lastDrawn = ""; await load(true); }
    catch (err) { $("#top-hint").textContent = err.message; }
  });
  $("#undo").onclick = async () => {
    try { await api(`/api/characters/${who}/stages/${current}/undo`, { method: "POST", body: {} }); lastDrawn = ""; await load(true); }
    catch (err) { $("#top-hint").textContent = err.message; }
  };
  $("#stage-notes").oninput = (e) => { notesDraft[current] = e.target.value; };
  $("#go-next")?.addEventListener("click", (e) => { e.preventDefault(); current = next.id; lastDrawn = ""; draw(); });
  $("#go-review")?.addEventListener("click", (e) => { e.preventDefault(); current = nextReview.id; lastDrawn = ""; draw(); });
  $("#dismiss")?.addEventListener("click", async () => {
    try { await api(`/api/characters/${who}/stages/${current}/dismiss`, { method: "POST", body: {} }); await load(true); const r = st.stages.find((x) => x.review); if (r) { current = r.id; lastDrawn = ""; draw(); } }
    catch (err) { $("#top-hint").textContent = err.message; }
  });
  const rollWith = (base) => async () => {
    try {
      await api(`/api/characters/${who}`, { method: "PUT", body: { description: $("#desc").value, notes: $("#notes").value, style: $("#style").value } });
      await api(`/api/characters/${who}/stages/${current}/roll`, { method: "POST", body: { notes: $("#stage-notes").value, models: chosen(), each: +$("#each").value || 2, base, variants: [...variants] } });
      notesDraft[current] = ""; await load(true);
    } catch (err) { $("#said").textContent = err.message; $("#top-hint").textContent = err.message; }
  };
  if ($("#roll")) $("#roll").onclick = rollWith(null);
  if ($("#fix")) $("#fix").onclick = rollWith("kept");
  if ($("#over")) $("#over").onclick = rollWith("parent");
  $("#keep").onclick = async () => {
    if (!confirm(`Looked at it full size? ${check().short.replace("⚠ zoom in: ", "")}. Keep it?`)) return;
    try {
      if (s.running) await api(`/api/characters/${who}/stages/${current}/stop`, { method: "POST", body: {} });
      await api(`/api/characters/${who}/stages/${current}/keep`, { method: "POST", body: {} });
      await load(true);
      const nxt = st.stages.find((x) => x.review) || st.stages.find((x) => x.n > s.n && !x.kept);
      if (nxt) { current = nxt.id; lastDrawn = ""; draw(); }
    } catch (err) { $("#top-hint").textContent = err.message; }
  };
}
/* ---- the overlay: one candidate large, arrows through the roll, pick from there ---- */
const view = { list: [], i: 0 };
function openView(round, file) {
  const s = st.stages.find((x) => x.id === current);
  view.list = (s.rounds || []).flatMap((r) => r.candidates.map((c) => ({ round: r.round, file: c.file, url: c.url, model: c.model, roll: r.round })));
  view.i = Math.max(0, view.list.findIndex((c) => c.round === round && c.file === file));
  $("#view").hidden = false; showView();
}
function showView() {
  const c = view.list[view.i]; if (!c) return;
  const s = st.stages.find((x) => x.id === current), isPick = s.pick && s.pick.round === c.round && s.pick.file === c.file;
  $("#v-pic").src = c.url; $("#v-pic").classList.remove("zoom");
  $("#v-title").textContent = `${view.i + 1} of ${view.list.length} · ${c.roll} · ${c.model}${isPick ? " · the pick" : ""}`;
  $("#v-prev").disabled = view.i === 0; $("#v-next").disabled = view.i === view.list.length - 1;
  $("#v-pick").textContent = isPick ? "This is the pick" : "Pick this one";
}
async function pickFromView() {
  const c = view.list[view.i]; if (!c) return;
  try { await api(`/api/characters/${who}/stages/${current}/pick`, { method: "POST", body: { round: c.round, file: c.file } }); await load(true); showView(); }
  catch (err) { $("#top-hint").textContent = err.message; }
}
$("#v-close").onclick = () => { $("#view").hidden = true; };
$("#v-prev").onclick = () => { if (view.i > 0) { view.i--; showView(); } };
$("#v-next").onclick = () => { if (view.i < view.list.length - 1) { view.i++; showView(); } };
$("#v-pick").onclick = pickFromView;
$("#v-pic").onclick = (e) => e.target.classList.toggle("zoom");
document.addEventListener("keydown", (e) => {
  if ($("#view").hidden) return;
  if (e.key === "Escape") $("#view").hidden = true;
  else if (e.key === "ArrowLeft") $("#v-prev").click();
  else if (e.key === "ArrowRight") $("#v-next").click();
  else if (e.key === "Enter") pickFromView();
});
$("#work").addEventListener("dblclick", (e) => {
  const fig = e.target.closest("figure[data-round]"); if (fig) openView(fig.dataset.round, fig.dataset.file);
});
$("#work").addEventListener("click", async (e) => {
  const fig = e.target.closest("figure[data-round]"); if (!fig) return;
  try { await api(`/api/characters/${who}/stages/${current}/pick`, { method: "POST", body: { round: fig.dataset.round, file: fig.dataset.file } }); await load(true); }
  catch (err) { $("#top-hint").textContent = err.message; }
});
/* ---- setup ---- */
$("#fix-all").onclick = async () => {
  const notes = $("#fix-notes").value.trim(); if (!notes) { $("#fix-said").textContent = "say what to fix"; return; }
  if (!confirm(`Roll the lock and every kept step again from itself with: “${notes}”? ${chosen().length} model(s) × ${+$("#fix-each").value || 1} each, one stage at a time.`)) return;
  try { await api(`/api/characters/${who}/fix-all`, { method: "POST", body: { notes, models: chosen(), each: +$("#fix-each").value || 1 } }); $("#fix-notes").value = ""; lastDrawn = ""; await load(true); }
  catch (err) { $("#fix-said").textContent = err.message; }
};
$("#model-add-go").onclick = () => {
  const m = $("#model-add").value.trim(); if (!m) return;
  const extra = JSON.parse(localStorage.getItem("sheets-extra") || "[]");
  if (!extra.includes(m)) extra.push(m);
  localStorage.setItem("sheets-extra", JSON.stringify(extra));
  if (!catalog.includes(m)) catalog.push(m);
  on.add(m); localStorage.setItem("sheets-on", JSON.stringify([...on]));
  $("#model-add").value = ""; lastDrawn = ""; draw();
};
$("#save").onclick = async () => {
  try {
    await api(`/api/characters/${who}`, { method: "PUT", body: { description: $("#desc").value, notes: $("#notes").value, style: $("#style").value, steps_text: $("#steps").value } });
    $("#said").textContent = "saved"; lastDrawn = ""; await load(true);
  } catch (err) { $("#said").textContent = err.message; }
};
const upload = (what) => async (e) => {
  const f = e.target.files[0]; if (!f) return;
  const data_url = await new Promise((res) => { const r = new FileReader(); r.onload = () => res(r.result); r.readAsDataURL(f); });
  try {
    await api(`/api/characters/${who}/${what}`, { method: "POST", body: { data_url } });
    if (what === "reference") { current = "00-lock"; $("#said").textContent = "reference saved: say how to redraw it, then Roll the lock"; }
    lastDrawn = ""; await load(true);
  } catch (err) { $("#said").textContent = err.message; }
  e.target.value = "";
};
$("#notes-hardsf").onclick = () => { if (!$("#notes").value.includes("80/15/5")) $("#notes").value = ($("#notes").value.trim() ? $("#notes").value.trim() + "\n" : "") + HARD_SF; $("#said").textContent = "hard SF added to the notes for every prompt: save setup, or just Roll (it saves)"; };
$("#style-photo").onclick = () => { $("#style").value = PHOTO; $("#said").textContent = "style set: save setup, or just Roll (it saves)"; };
$("#reset").onclick = async () => {
  if (!who) return;
  const word = prompt(`Reset ${who}? The reference image, the lock, every roll, every kept image and the logs move to previous/ inside its folder. Only the description, notes, style and steps stay.\n\nType evoke to confirm.`);
  if (word === null) return;
  try {
    const { previous } = await api(`/api/characters/${who}/reset`, { method: "POST", body: { confirm: word } });
    current = null; lastDrawn = ""; notesDraft = {}; await load(true);
    $("#reset-hint").textContent = previous ? `reset: the work so far is in previous/${previous}` : "nothing to reset";
  } catch (err) { $("#reset-hint").textContent = err.message; }
};
$("#lock-file").onchange = upload("lock");
$("#ref-file").onchange = upload("reference");
$("#from-md").onclick = async () => {
  const { files } = await api("/api/md");
  $("#md-file").innerHTML = files.map((f) => `<option>${esc(f)}</option>`).join("") || "<option value=''>(no .md files found)</option>";
  $("#md").showModal(); showMd();
};
$("#md-file").onchange = showMd;
async function showMd() {
  const path = $("#md-file").value; if (!path) return;
  const d = await api(`/api/md?path=${encodeURIComponent(path)}`);
  $("#md-secs").innerHTML = d.sections.map((s, i) => `<div class="sec" data-i="${i}"><b>${"#".repeat(s.depth)} ${esc(s.heading)}</b><small>${esc(s.body.slice(0, 300))}</small></div>`).join("");
  $("#md-secs").onclick = (e) => { const el = e.target.closest(".sec"); if (!el) return; const s = d.sections[+el.dataset.i]; $("#desc").value = `${s.heading}: ${s.body}`; $("#md").close(); };
}
(async () => { loadModels(await api("/api/models")); await listCampaigns(); await listWho(); await load(true); if (st && !st.description) $("#setup").open = true; })();
</script></html>"""


# ---- the server -------------------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):   # quieter: the page polls
        if "GET /api/characters/" not in (args[0] if args else "") and "/files/" not in (args[0] if args else ""):
            super().log_message(fmt, *args)

    def send_json(self, data, code=200):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}") if n else {}

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(url.query)
        try:
            if url.path == "/":
                page = PAGE.replace("%MODELS%", json.dumps(",".join(core.DEFAULT_MODELS))).replace("%PREFIX%", PREFIX).replace("%PHOTO%", json.dumps(core.PHOTO)).replace("%HARD_SF%", json.dumps(core.HARD_SF)).encode()
                self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(page))); self.end_headers(); self.wfile.write(page)
            elif url.path == "/api/characters":
                names = sorted(p.name for p in ROOT.iterdir() if p.is_dir() and re.fullmatch(r"[a-z0-9][a-z0-9_-]*", p.name))
                is_place = lambda n: (ROOT / n / "kind.txt").exists() and (ROOT / n / "kind.txt").read_text().strip() == "place"
                self.send_json({"characters": names, "kinds": {n: "place" if is_place(n) else "character" for n in names}})
            elif url.path.startswith("/api/characters/") and url.path.endswith("/set.zip"):
                name = url.path.split("/")[3]
                data = set_zip(name)
                self.send_response(200); self.send_header("Content-Type", "application/zip")
                self.send_header("Content-Disposition", f'attachment; filename="{name}-training-set.zip"')
                self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
            elif url.path.startswith("/api/characters/"):
                self.send_json(status(url.path.split("/")[3]))
            elif url.path == "/api/md":
                self.send_json(md_read(q["path"][0]) if "path" in q else {"files": md_files()})
            elif url.path == "/api/models":
                self.send_json({"models": catalog(), "default": core.DEFAULT_MODELS, "seconds": typical_seconds(), "kept": kept_rates()})
            elif url.path == "/api/campaigns":
                self.send_json({"campaigns": campaigns()})
            elif url.path.startswith("/api/campaigns/"):
                self.send_json(subjects(urllib.parse.unquote(url.path.split("/")[3])))
            elif url.path.startswith("/files/"):
                rel = urllib.parse.unquote(url.path[len("/files/"):])
                p = (ROOT / rel).resolve()
                if ROOT not in p.parents or not p.is_file():
                    raise FileNotFoundError(rel)
                data = p.read_bytes()
                self.send_response(200); self.send_header("Content-Type", mimetypes.guess_type(str(p))[0] or "application/octet-stream")
                self.send_header("Content-Length", str(len(data))); self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(data)
            else:
                self.send_json({"error": "not found"}, 404)
        except FileNotFoundError as e:
            self.send_json({"error": f"not found: {e}"}, 404)
        except (ValueError, KeyError) as e:
            self.send_json({"error": str(e)}, 400)

    def do_POST(self):
        parts = self.path.split("?")[0].split("/")
        try:
            data = self.body()
            if self.path == "/api/style":
                self.send_json({"from": set_plate(data.get("name"))})
            elif self.path == "/api/characters":
                d = character(data.get("name", ""))
                d.mkdir(exist_ok=True)
                if data.get("kind") == "place":
                    (d / "kind.txt").write_text("place\n")
                elif "kind" in data and (d / "kind.txt").exists():
                    (d / "kind.txt").unlink()
                self.send_json({"ok": True, "name": d.name})
            elif len(parts) == 5 and parts[4] in ("lock", "reference"):
                head, _, b64 = data.get("data_url", "").partition(",")
                if "image/" not in head or not b64:
                    raise ValueError("expected an image")
                ext = head.split("image/")[1].split(";")[0].replace("jpeg", "jpg")
                d = character(parts[3])
                for old in d.glob(f"{parts[4]}.*"):
                    old.unlink()
                (d / f"{parts[4]}.{ext}").write_bytes(base64.b64decode(b64))
                self.send_json({"ok": True})
            elif len(parts) == 7 and parts[4] == "stages" and parts[6] == "roll":
                roll(parts[3], parts[5], (data.get("notes") or "").strip(), allowed(data.get("models")), int(data.get("each") or 2), data.get("base"),
                     variants=data.get("variants"))
                self.send_json({"ok": True})
            elif len(parts) == 7 and parts[4] == "stages" and parts[6] == "pick":
                pick(parts[3], parts[5], data.get("round", ""), data.get("file", ""))
                self.send_json({"ok": True})
            elif len(parts) == 7 and parts[4] == "stages" and parts[6] == "keep":
                self.send_json({"kept": keep(parts[3], parts[5])})
            elif len(parts) == 7 and parts[4] == "stages" and parts[6] == "undo":
                self.send_json({"rounds": undo(parts[3], parts[5])})
            elif len(parts) == 7 and parts[4] == "stages" and parts[6] == "stop":
                stop_roll(parts[3], parts[5]); self.send_json({"ok": True})
            elif len(parts) == 7 and parts[4] == "stages" and parts[6] == "dismiss":
                dismiss(parts[3], parts[5]); self.send_json({"ok": True})
            elif len(parts) == 5 and parts[4] == "reset":
                self.send_json({"previous": reset(parts[3], data.get("confirm"))})
            elif len(parts) == 5 and parts[4] == "fix-all":
                fix_all(parts[3], (data.get("notes") or "").strip(), allowed(data.get("models")), int(data.get("each") or 1))
                self.send_json({"ok": True})
            else:
                self.send_json({"error": "not found"}, 404)
        except FileNotFoundError as e:
            self.send_json({"error": f"not found: {e}"}, 404)
        except (ValueError, KeyError, SystemExit) as e:
            self.send_json({"error": str(e)}, 400)

    def do_PUT(self):
        parts = self.path.split("/")
        try:
            data = self.body()
            if len(parts) == 4 and parts[2] == "characters":
                d = character(parts[3])
                if not d.is_dir():
                    raise FileNotFoundError(parts[3])
                if "description" in data:
                    (d / "description.txt").write_text(data["description"].strip() + "\n")
                if "style" in data:
                    (d / "style.txt").write_text(data["style"].strip() + "\n")
                if "notes" in data:
                    (d / "notes.txt").write_text(data["notes"].strip() + "\n")
                if "steps_text" in data:
                    kind_file = d / "kind.txt"
                    default = core.HERE / ("steps-place.txt" if kind_file.exists() and kind_file.read_text().strip() == "place" else "steps.txt")
                    if data["steps_text"].strip() == default.read_text().strip():
                        (d / "steps.txt").unlink(missing_ok=True)     # the default: follow it if it changes
                    else:
                        (d / "steps.txt").write_text(data["steps_text"].rstrip() + "\n")
                        core.read_steps(d / "steps.txt")     # complains now rather than at run time
                self.send_json({"ok": True})
            else:
                self.send_json({"error": "not found"}, 404)
        except FileNotFoundError as e:
            self.send_json({"error": f"not found: {e}"}, 404)
        except (ValueError, SystemExit) as e:
            self.send_json({"error": str(e)}, 400)


if __name__ == "__main__":
    ROOT.mkdir(parents=True, exist_ok=True)
    print(f"sheets: http://0.0.0.0:{PORT}{PREFIX or ''}  characters in {ROOT}  markdown from {', '.join(map(str, MD_ROOTS))}"
          + ("  (DRY: no model is called)" if DRY else ""), flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
