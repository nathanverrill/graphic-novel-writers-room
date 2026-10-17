"""The story desk: the book at a high level, before you press run.

Three views of one desk's files (pre-production by default, the desk development reads):

    outline     story.md as cards, one per heading: edit, add, remove, move. Every write is
                checked against the hash of what you were looking at, so a file the room
                rewrote meanwhile is never overwritten blind.
    structure   a model maps the outline onto a story structure - the hero's journey (twelve
                stages) or the seven-point structure - and says, stage by stage, which beats
                carry it, how strongly, and what would make it stronger. Saved beside story.md
                as structure-<framework>.json, with the story's hash, so a stale check says so.
    locks       each character's visual lock as the page prompts paste it (characters.md) beside
                its drawn lock (campaigns/<slug>/style/locks/<name>-<model>/lock.png). Edit the
                words; compare the drawing with the words (a vision model lists what differs and
                proposes revised words); redraw the drawing with Sunburst from the plate, the old
                lock and the words, art-checked. A redraw is a candidate until you keep it; the
                lock it replaces goes to previous/.
"""
import hashlib
import json
import re
import threading
import time
from pathlib import Path

from . import artcheck, projects, render, usage

TEXT_MODEL = "anthropic/claude-opus-5.5"
LOCK_MODEL = "sunburst"          # locks are drawn with GPT Image 2.5 Sunburst only
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_lock = threading.Lock()
_jobs = {}                       # (slug, kind, key) -> {"state", "started", "error", ...}


def _hash(text):
    return hashlib.sha1((text or "").encode()).hexdigest()[:12]


def _desk(desk):
    if desk not in projects.DESKS:
        raise ValueError(f"desk is one of {', '.join(projects.DESKS)}")
    return desk


def _path(slug, name, desk):
    return projects.project_dir(slug, _desk(desk)) / name


def _read(slug, name, desk):
    p = _path(slug, name, desk)
    return p.read_text() if p.exists() else ""


# ---- the outline: story.md as sections --------------------------------------------------------

def parse(text):
    """[{level, title, body, raw}]: a preamble (level 0) and then one entry per heading. Headings
    inside fenced code are text, not headings. `raw` is the section exactly as written, so a
    section nobody touched is written back byte for byte."""
    out = [{"level": 0, "title": "", "lines": []}]
    fenced = False
    for line in (text or "").splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
        m = None if fenced else HEADING.match(line)
        if m:
            out.append({"level": len(m.group(1)), "title": m.group(2), "lines": [line]})
        else:
            out[-1]["lines"].append(line)
    for s in out:
        lines = s.pop("lines")
        s["raw"] = "\n".join(lines)
        s["body"] = "\n".join(lines[1:] if s["level"] else lines).strip("\n")
        s["orig"] = (s["title"], s["body"])
    if not out[0]["raw"].strip():
        out.pop(0)
    return out


def join(sections):
    parts = []
    for s in sections:
        if s.get("orig") == (s["title"], s["body"]) and "raw" in s:
            parts.append(s["raw"])
            continue
        head = f"{'#' * s['level']} {s['title']}" if s["level"] else ""
        parts.append("\n\n".join(x for x in (head, s["body"].strip("\n")) if x) + "\n")
    return "\n".join(parts).rstrip("\n") + "\n"


def _subtree(sections, i):
    """The end (exclusive) of section i and everything nested under it."""
    lvl = sections[i]["level"] or 99
    j = i + 1
    while j < len(sections) and (sections[j]["level"] or 99) > lvl:
        j += 1
    return j


EDITABLE = ("story.md", "characters.md", "world.md")     # the three working files, section by section


def _file(name):
    if name not in EDITABLE:
        raise ValueError(f"only {', '.join(EDITABLE)} can be edited here")
    return name


def outline(slug, desk=projects.PRE, name="story.md"):
    text = _read(slug, _file(name), desk)
    sections = parse(text)
    return {"desk": desk, "file": name, "hash": _hash(text), "exists": bool(text),
            "sections": [{"level": s["level"], "title": s["title"], "body": s["body"], "i": i, "hash": _hash(s["title"] + "\n" + s["body"])} for i, s in enumerate(sections)]}


def _edit(slug, desk, file_hash, change, name="story.md"):
    """Apply change(sections) to the file if it is still the file the showrunner saw."""
    with _lock:
        text = _read(slug, _file(name), desk)
        if file_hash != _hash(text):
            raise ConflictError(f"{name} changed since you opened it - reload to see the new version")
        sections = parse(text)
        change(sections)
        out = join(sections)
        _path(slug, name, desk).write_text(out if text.endswith("\n") else out.rstrip("\n"))
    return outline(slug, desk, name)


class ConflictError(Exception):
    pass


def _clean_title(title):
    return re.sub(r"\s+", " ", title or "").strip()


def update_section(slug, desk, file_hash, i, title, body, name="story.md"):
    def change(sections):
        if not 0 <= i < len(sections):
            raise ValueError("no such section")
        if sections[i]["level"]:
            sections[i]["title"] = _clean_title(title) or sections[i]["title"]
        sections[i]["body"] = (body or "").strip("\n")
    return _edit(slug, desk, file_hash, change, name)


def add_section(slug, desk, file_hash, after, level, title, body, name="story.md"):
    def change(sections):
        lvl = max(1, min(6, int(level or 3)))
        at = _subtree(sections, after) if 0 <= after < len(sections) else len(sections)
        sections.insert(at, {"level": lvl, "title": _clean_title(title) or "New beat", "body": (body or "").strip("\n")})
    return _edit(slug, desk, file_hash, change, name)


def delete_section(slug, desk, file_hash, i, name="story.md"):
    def change(sections):
        if not 0 <= i < len(sections):
            raise ValueError("no such section")
        del sections[i:_subtree(sections, i)]
    return _edit(slug, desk, file_hash, change, name)


def move_section(slug, desk, file_hash, i, direction, name="story.md"):
    """Swap section i (with what is nested under it) with its neighbour at the same level."""
    def change(sections):
        if not 0 <= i < len(sections):
            raise ValueError("no such section")
        lvl, end = sections[i]["level"], _subtree(sections, i)
        if direction < 0:
            j = i - 1
            while j >= 0 and sections[j]["level"] > lvl:
                j -= 1
            if j < 0 or sections[j]["level"] != lvl:
                return
            sections[j:end] = sections[i:end] + sections[j:i]
        else:
            if end >= len(sections) or sections[end]["level"] != lvl:
                return
            nxt = _subtree(sections, end)
            sections[i:nxt] = sections[end:nxt] + sections[i:end]
    return _edit(slug, desk, file_hash, change, name)


# ---- structure: the outline against a story structure -----------------------------------------

FRAMEWORKS = {
    "hero": {"title": "Hero's journey", "stages": [
        ("ordinary", "The ordinary world", "the hero's normal life, and what is wrong or missing in it"),
        ("call", "The call to adventure", "something disrupts that life and offers a way out or a problem"),
        ("refusal", "Refusal of the call", "fear, duty or doubt makes the hero hesitate"),
        ("mentor", "Meeting the mentor", "someone or something gives advice, a tool or confidence"),
        ("threshold", "Crossing the threshold", "the hero commits and leaves the known world"),
        ("tests", "Tests, allies, enemies", "the new world's rules; who helps, who opposes"),
        ("approach", "Approach to the inmost cave", "preparation for the central danger; tension tightens"),
        ("ordeal", "The ordeal", "the greatest crisis so far; a death and rebirth, real or symbolic"),
        ("reward", "The reward", "what the hero takes from surviving: a truth, an object, a bond"),
        ("road_back", "The road back", "consequences chase the hero; the stakes turn back toward home"),
        ("resurrection", "The resurrection", "the final test, where the hero must use everything learned"),
        ("elixir", "Return with the elixir", "the hero comes home changed, carrying something that helps others"),
    ]},
    "seven": {"title": "Seven-point structure", "stages": [
        ("hook", "Hook", "the starting state, the opposite of the resolution"),
        ("plot1", "Plot turn 1", "the event that sets the story moving and changes the hero's world"),
        ("pinch1", "Pinch 1", "the antagonist applies pressure; the hero is forced to act"),
        ("midpoint", "Midpoint", "the hero moves from reacting to acting; a new understanding"),
        ("pinch2", "Pinch 2", "everything goes wrong; the plan fails and the hero seems to lose"),
        ("plot2", "Plot turn 2", "the hero finds the last piece needed to resolve the story"),
        ("resolution", "Resolution", "the climax and the new state of the world"),
    ]},
}

STRUCTURE_ASK = """You are a story editor for a graphic novel. Read the outline below and map it onto the {title}.

For each stage, find the beat or beats in the outline that carry it, using the outline's own section
titles and page numbers where it has them. Rate how well the outline delivers that stage:
- "strong": a clear, dramatized beat does this job, in the right place
- "thin": something gestures at it, but it is weak, rushed, out of order or only told
- "missing": nothing in the outline does this job

Not every good story needs every stage at full strength. Judge it as an editor who wants this book to work
for its audience, not as a checklist: say when a stage is deliberately subverted and that choice works.

The stages:
{stages}

Reply with ONLY a JSON object, no prose around it:
{{"summary": "two or three plain sentences: how well the outline follows the structure, and the single biggest gap",
  "score": <0-100: how well the outline delivers the structure's work>,
  "stages": [{{"id": "<stage id>", "rating": "strong|thin|missing",
              "beats": ["<the outline's section titles or page numbers that carry this stage>"],
              "where": "<pages or issue, if the outline says>",
              "note": "<one or two sentences: what the outline does here>",
              "suggestion": "<one concrete change that would strengthen this stage, or empty if strong>"}}]}}

Plain words, short sentences. Quote the outline's titles exactly so they can be found.

=== THE OUTLINE (story.md) ===

{story}
"""


def _structure_file(slug, desk, framework):
    return _path(slug, f"structure-{framework}.json", desk)


def structure(slug, desk=projects.PRE, framework="hero"):
    if framework not in FRAMEWORKS:
        raise ValueError("unknown framework")
    f = FRAMEWORKS[framework]
    text = _read(slug, "story.md", desk)
    p = _structure_file(slug, desk, framework)
    saved = json.loads(p.read_text()) if p.exists() else None
    job = _jobs.get((slug, "structure", f"{desk}/{framework}"))
    return {"framework": framework, "title": f["title"],
            "stages": [{"id": i, "name": n, "job": j} for i, n, j in f["stages"]],
            "result": saved, "stale": bool(saved and saved.get("story_hash") != _hash(text)),
            "job": job}


def check_structure(slug, desk=projects.PRE, framework="hero"):
    if framework not in FRAMEWORKS:
        raise ValueError("unknown framework")
    text = _read(slug, "story.md", desk)
    if not text.strip():
        raise ValueError("story.md is empty on this desk - run intake first")
    key = render.api_key()
    if not key:
        raise ValueError("no OpenRouter key - add one on the room's screen")
    jk = (slug, "structure", f"{desk}/{framework}")
    if (_jobs.get(jk) or {}).get("state") == "running":
        return structure(slug, desk, framework)
    _jobs[jk] = {"state": "running", "started": time.time()}
    f = FRAMEWORKS[framework]

    def work():
        try:
            ask = STRUCTURE_ASK.format(title=f["title"], story=text,
                                       stages="\n".join(f'- "{i}" {n}: {j}' for i, n, j in f["stages"]))
            t0 = time.time()
            answer, cost = artcheck._ask([{"type": "text", "text": ask}], key, TEXT_MODEL)
            usage.ledger(slug, "story_desk", f"structure-{framework}", TEXT_MODEL, cost, time.time() - t0, desk=desk)
            data = artcheck._json(answer)
            if not data or not isinstance(data.get("stages"), list):
                raise RuntimeError("the model's answer could not be read")
            data.update(story_hash=_hash(text), model=TEXT_MODEL, cost=cost, checked=time.time())
            _structure_file(slug, desk, framework).write_text(json.dumps(data, indent=1))
            _jobs[jk] = {"state": "done", "started": _jobs[jk]["started"], "cost": cost}
        except Exception as e:      # noqa: BLE001 - reported on the screen
            _jobs[jk] = {"state": "failed", "started": _jobs[jk]["started"], "error": str(e)[:300]}
    threading.Thread(target=work, daemon=True).start()
    return structure(slug, desk, framework)


# ---- locks: the words and the drawing of each character ---------------------------------------

LOOK_FIELDS = ("Visual lock", "Look")
FIELD = re.compile(r"^\*\*([A-Z][^*]{0,40}?):?\*\*\s*(?:—|:|-)?\s*")


def _characters_desk(slug, desk):
    """The desk shown is the desk edited: pre-production's characters.md is what development
    starts from, production's is what the page prompts paste."""
    return _desk(desk)


def _entries(text):
    """[(name, start, end)] line spans of each '### Name' entry in characters.md."""
    lines = text.splitlines()
    heads = [(i, HEADING.match(l)) for i, l in enumerate(lines)]
    heads = [(i, m) for i, m in heads if m]
    out = []
    for k, (i, m) in enumerate(heads):
        if len(m.group(1)) != 3:
            continue
        end = next((j for j, mm in heads[k + 1:] if len(mm.group(1)) <= 3), len(lines))
        out.append((m.group(2).strip(), i, end))
    return out


def _look_span(lines, start, end):
    """(first, last, field, text) of the entry's look paragraph(s), or None."""
    for i in range(start + 1, end):
        m = FIELD.match(lines[i])
        if m and m.group(1).strip() in LOOK_FIELDS:
            j = i + 1
            while j < end and not FIELD.match(lines[j]) and not lines[j].startswith("---") and not HEADING.match(lines[j]):
                j += 1
            body = "\n".join([lines[i][m.end():]] + lines[i + 1:j]).strip()
            return i, j, m.group(1).strip(), body
    return None


def _title_name(name):
    """ALEX PHANTUM -> Alex Phantum; mixed case stays as written."""
    if not name.isupper():
        return name
    return " ".join(w.title() if len(w) > 2 or w.endswith(".") else w for w in name.split())


def _lock_dirs(slug):
    base = projects.campaign_dir(slug) / "style" / "locks"
    return sorted(d for d in base.iterdir() if d.is_dir()) if base.is_dir() else []


def _img(d):
    found = [p for p in d.glob("lock.*") if p.suffix.lower() in render.MIME]
    return found[0] if found else None


def locks(slug, desk=projects.PRE):
    cdesk = _characters_desk(slug, desk)
    text = _read(slug, "characters.md", cdesk)
    lines = text.splitlines()
    used, people = set(), []
    for name, start, end in _entries(text):
        look = _look_span(lines, start, end)
        drawn = []
        for tag in render.MODELS:
            p = render.lock_for(slug, name, tag, text)
            if p:
                used.add(p.parent.name)
                drawn.append(_lock_info(slug, p.parent, tag))
        people.append({"name": name, "display": _title_name(name), "field": look[2] if look else None,
                       "look": look[3] if look else "", "locks": drawn,
                       "hash": _hash(look[3] if look else ""),
                       "job": _jobs.get((slug, "redraw", name))})
    orphans = [_lock_info(slug, d, d.name.rsplit("-", 1)[-1]) for d in _lock_dirs(slug) if d.name not in used and _img(d)]
    plate = render.plate(slug)
    return {"desk": cdesk, "file": "characters.md", "people": people, "orphans": orphans,
            "plate": plate.name if plate else None, "file_hash": _hash(text)}


def _lock_info(slug, d, tag):
    img = _img(d)
    cands = sorted((d / "candidates").glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True) if (d / "candidates").is_dir() else []
    reports = {}
    rp = d / "candidates" / "reports.json"
    if rp.exists():
        reports = json.loads(rp.read_text())
    return {"folder": d.name, "model": tag, "image": img.name if img else None,
            "version": int(img.stat().st_mtime) if img else 0,
            "candidates": [{"file": c.name, "check": reports.get(c.name)} for c in cands[:6]],
            "compare": json.loads((d / "compare.json").read_text()) if (d / "compare.json").exists() else None}


def lock_file(slug, folder, name):
    d = projects.campaign_dir(slug) / "style" / "locks" / _safe(folder)
    p = d / _safe(name) if name != "plate" else render.plate(slug)
    if name.startswith("cand-"):
        p = d / "candidates" / _safe(name)
    if not p or not p.exists():
        raise FileNotFoundError(name)
    return p


def _safe(name):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.\-]{0,80}", name or "") or ".." in name:
        raise ValueError("bad name")
    return name


def save_look(slug, desk, name, look_hash, text):
    """Replace one character's look paragraph in characters.md."""
    cdesk = _characters_desk(slug, desk)
    with _lock:
        full = _read(slug, "characters.md", cdesk)
        lines = full.splitlines()
        entry = next(((s, e) for n, s, e in _entries(full) if n == name), None)
        if not entry:
            raise ValueError(f"no character named {name}")
        span = _look_span(lines, *entry)
        if _hash(span[3] if span else "") != look_hash:
            raise ConflictError(f"{name}'s look changed since you opened it - reload")
        body = re.sub(r"\n{3,}", "\n\n", (text or "").strip())
        if span:
            first, last, field, _ = span
            sep = " — " if field == "Visual lock" else " "
            label = "**Visual lock**" if field == "Visual lock" else f"**{field}:**"
            lines[first:last] = (label + sep + body).splitlines() + ([""] if last < len(lines) else [])
        else:
            label = "**Visual lock** — " if cdesk == projects.PROD else "**Look:** "
            lines[entry[0] + 1:entry[0] + 1] = ["", label + body]
        _path(slug, "characters.md", cdesk).write_text("\n".join(lines).rstrip() + "\n")
    return locks(slug, desk)


COMPARE_ASK = """You check a graphic novel's character locks. The first image is the drawn lock of {name}: the
picture every page is drawn from. The text below is the visual lock: the words pasted into every page prompt.
They must describe the same person, or the pages will drift.

Compare them carefully: age, build, height, skin, face, eyes, hair (length, texture, cut, color), clothes
and their colors, accessories, signature details, silhouette. {plate}

Reply with ONLY a JSON object:
{{"match": <0-100, how well the words and the drawing agree>,
  "differences": [{{"what": "<the feature>", "drawing": "<what the drawing shows>", "words": "<what the text says>",
                   "fix": "words|drawing", "why": "<one short line: which should change, and why>"}}],
  "revised": "<the visual lock rewritten so it describes exactly what the drawing shows, where the drawing is
              the better choice, and keeps the words where they are better; same form, same length, same tone>"}}

Prefer the drawing where it is specific and good, and the words where the story needs them (a story detail
the drawing lost, like a wristband or a scar, is a fix to the drawing).

=== THE VISUAL LOCK ===

{look}
"""


def compare(slug, desk, name, folder):
    """A vision model's read of one drawn lock against its words. Saved as compare.json."""
    key = render.api_key()
    if not key:
        raise ValueError("no OpenRouter key - add one on the room's screen")
    person = next((p for p in locks(slug, desk)["people"] if p["name"] == name), None)
    if not person:
        raise ValueError(f"no character named {name}")
    d = projects.campaign_dir(slug) / "style" / "locks" / _safe(folder)
    img = _img(d)
    if not img:
        raise ValueError("that lock has no drawing")
    plate = render.plate(slug)
    content = [{"type": "text", "text": COMPARE_ASK.format(
        name=person["display"], look=person["look"] or "(no visual lock written yet - write one from the drawing)",
        plate="The second image is the book's style plate, for context only." if plate else "")},
        {"type": "image_url", "image_url": {"url": render.data_url(img)}}]
    if plate:
        content.append({"type": "image_url", "image_url": {"url": render.data_url(plate)}})
    t0 = time.time()
    answer, cost = artcheck._ask(content, key, TEXT_MODEL)
    usage.ledger(slug, "story_desk", "lock-compare", TEXT_MODEL, cost, time.time() - t0, desk=desk, character=name)
    data = artcheck._json(answer)
    if not data:
        raise RuntimeError("the model's answer could not be read")
    data.update(look_hash=person["hash"], image_version=int(img.stat().st_mtime), cost=cost, checked=time.time())
    (d / "compare.json").write_text(json.dumps(data, indent=1))
    return data


REDRAW_PROMPT = """A CHARACTER LOCK for a graphic novel: one full-body drawing of {name}, standing in a relaxed,
characterful three-quarter pose, head to boots in frame, on a plain warm cream background. Portrait.
This image is the reference every page of the book is drawn from, so every detail must be clear.

{name}: {look}

Draw it exactly in the style of the style plate: the same line, color, light and rendering.
{old}{note}
No text, no labels, no names, no numbers, no frame, no other people."""


def redraw(slug, desk, name, note=""):
    """Sunburst draws a new lock for one character, checked by artcheck; kept as a candidate."""
    key = render.api_key()
    if not key:
        raise ValueError("no OpenRouter key - add one on the room's screen")
    person = next((p for p in locks(slug, desk)["people"] if p["name"] == name), None)
    if not person:
        raise ValueError(f"no character named {name}")
    if not person["look"].strip():
        raise ValueError("write the visual lock first - the drawing is made from it")
    jk = (slug, "redraw", name)
    if (_jobs.get(jk) or {}).get("state") == "running":
        return _jobs[jk]
    existing = next((l for l in person["locks"] if l["model"] == LOCK_MODEL), None)
    base = projects.campaign_dir(slug) / "style" / "locks"
    d = base / existing["folder"] if existing else base / f"{projects.slugify(person['display'])}-{LOCK_MODEL}"
    refs = []
    plate = render.plate(slug)
    if plate:
        refs.append(("the style plate - draw in exactly this style", plate))
    old = _img(d) if d.is_dir() else None
    if old:
        refs.append((f"{person['display']}'s current lock - keep everything the words do not change", old))
    look = re.sub(r"\*\*", "", person["look"]).strip()       # markdown bold, and the stray ** some locks end on
    prompt = REDRAW_PROMPT.format(
        name=person["display"], look=look,
        old="The second attached image is the current lock: keep the same person, and change only what the "
            "description above says differently.\n" if old else "",
        note=f"Note for this drawing: {note.strip()}\n" if (note or "").strip() else "")
    if refs:
        prompt += "\nThe attached images, in order: " + "; ".join(f"{i}. {w}" for i, (w, _) in enumerate(refs, 1))
    _jobs[jk] = {"state": "running", "started": time.time(), "folder": d.name}

    def work():
        try:
            t0 = time.time()
            art, report, cost = artcheck.draw_checked(
                lambda text, r: render.generate(render.MODELS[LOCK_MODEL], text, r, key), prompt, refs, key,
                script=f"A character lock: one full-body figure of {person['display']}, no text.\n\n"
                       f"Visual lock: {look}", lettered=False)
            usage.ledger(slug, "story_desk", "lock-redraw", render.MODELS[LOCK_MODEL], cost, time.time() - t0,
                         character=name, tries=len(report["attempts"]), check_pass=report["pass"])
            (d / "candidates").mkdir(parents=True, exist_ok=True)
            fname = f"cand-{time.strftime('%Y%m%d-%H%M%S')}.png"
            (d / "candidates" / fname).write_bytes(art)
            rp = d / "candidates" / "reports.json"
            reports = json.loads(rp.read_text()) if rp.exists() else {}
            reports[fname] = {"pass": report["pass"], "problems": report["problems"],
                              "tries": len(report["attempts"]), "cost": cost, "note": note, "prompt": prompt}
            rp.write_text(json.dumps(reports, indent=1))
            _jobs[jk] = {"state": "done", "started": _jobs[jk]["started"], "folder": d.name, "file": fname, "cost": cost}
        except Exception as e:      # noqa: BLE001 - reported on the screen
            _jobs[jk] = {"state": "failed", "started": _jobs[jk]["started"], "error": str(e)[:300]}
    threading.Thread(target=work, daemon=True).start()
    return _jobs[jk]


def keep(slug, folder, file):
    """The candidate becomes the lock; the lock it replaces goes to previous/, never deleted."""
    d = projects.campaign_dir(slug) / "style" / "locks" / _safe(folder)
    src = d / "candidates" / _safe(file)
    if not src.exists():
        raise FileNotFoundError(file)
    with _lock:
        old = _img(d)
        if old:
            (d / "previous").mkdir(exist_ok=True)
            old.rename(d / "previous" / f"lock-{time.strftime('%Y%m%d-%H%M%S')}{old.suffix}")
        (d / "lock.png").write_bytes(src.read_bytes())
        src.unlink()
        cmp = d / "compare.json"
        if cmp.exists():
            cmp.unlink()            # it described the old drawing
    return {"kept": f"{folder}/lock.png"}


def discard(slug, folder, file):
    d = projects.campaign_dir(slug) / "style" / "locks" / _safe(folder)
    src = d / "candidates" / _safe(file)
    if src.exists():
        (d / "candidates" / "discarded").mkdir(exist_ok=True)
        src.rename(d / "candidates" / "discarded" / src.name)
    return {"ok": True}
