#!/usr/bin/env python3
"""The Art Department: a book's look, its people, places, props and key scenes - one full sheet per roll.

    python3 art/server.py           # http://localhost:8002  (the room serves it at /art)

The simple way to lock a book's visuals, starting fresh:

1. the style plate   upload a reference image or two, roll: every candidate is a whole style
                     plate - four panels (wide, two-shot, close-up, detail), a palette strip and
                     material swatches, no text. Keep one for each model.
   Link a campaign and its canon's characters and places are there to pick, with their looks.

2. the characters    a name, a description, a reference image if there is one; roll: every
                     candidate is a whole character sheet - front, three-quarter, side and back
                     at one scale, and four expressions. It is drawn from that model's plate, the
                     reference, the first character kept (the book's anchor) and the one kept
                     before it. Keep one for each model, then the next character.
   places            the same, as a location sheet: establishing view, reverse, street level,
                     a detail, another light - drawn from the plate and the places kept before.
   props             an object sheet: four views, a hand for scale, a close detail, its other state.
   and key scenes    a key frame: the scene's one moment, drawn from the kept sheets of whoever,
                     wherever and whatever it names.

Pick the models each roll. What is kept is per model: a Gemini sheet and a Sunburst sheet are
two sheets, because each model follows its own drawings best.

    data/<project>/project.json                  the cast, in order
    data/<project>/style/refs/ref-1.png          what the plate is rolled from
    data/<project>/<style|characters/<key>>/rolls/r1/…   every candidate, with roll.json
    data/<project>/<…>/kept/<model>.png          the one kept for each model

Image calls and the model list are Sheets' (sheets/sheets.py). Standard library only.
"""
import base64
import concurrent.futures
import json
import mimetypes
import os
import re
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(Path(os.getenv("SHEETS_CODE") or HERE.parent / "sheets")))
import sheets as core                                   # noqa: E402
if os.getenv("SECRETS_FILE"):
    core.SECRETS = Path(os.getenv("SECRETS_FILE"))

DATA = Path(os.getenv("ART_DIR") or HERE / "data").resolve()
PORT = int(os.getenv("PORT") or 8002)
PREFIX = (os.getenv("PREFIX") or "").rstrip("/")
DRY = bool(os.getenv("ART_DRY"))
MAX_REFS = 4
NAME = re.compile(r"[a-z0-9][a-z0-9_-]{0,40}")
_lock = threading.Lock()

STYLE_PROMPT = """A STYLE PLATE for a graphic novel: one portrait image that shows how every page of this book
looks, drawn exactly in the style of the attached reference image(s) - the same line, inking,
color, light, texture and level of detail.

It holds, in clean comic panels with white gutters:
1. a wide establishing panel: a place in this world, with depth and atmosphere
2. a medium panel: two characters talking, faces and hands readable
3. a close-up: one face, strongly lit, showing how emotion and skin are rendered
4. a small detail or action panel: an object, a hand, a machine
Along the bottom, a strip of six color swatches taken from the palette, and a row of four
small material swatches (metal, fabric, skin, sky or stone).

No text, no lettering, no logos, no captions, no speech balloons anywhere."""

SHEET_PROMPT = """A CHARACTER MODEL SHEET for {name}: {desc}

One landscape image on a plain light background. Top row, full body, all at exactly the same
scale, standing in a neutral pose: front view, three-quarter view, side profile, back view.
Bottom row, four head-and-shoulders close-ups: neutral, happy, angry, afraid. The same person
in every view: face, hair, build, costume, colors and every signature detail identical.

Draw it exactly in the style of the style plate (the first attached image): the same line,
color, light and rendering. {ref}{cast}No text, no labels, no names, no numbers anywhere."""


PLACE_PROMPT = """A LOCATION SHEET for {name}: {desc}

One landscape image showing this one place from several angles, so it can be drawn the same way on
every page. Top row: a wide establishing view with depth and scale, and the reverse angle.
Bottom row: a street-level or interior view where people would stand, a close detail of its
materials and signage, and the same place at night or in a different light. Every view is clearly
the same place: layout, architecture, materials, colors and landmarks identical. People appear only
small, for scale.

Draw it exactly in the style of the style plate (the first attached image): the same line, color,
light and rendering. {ref}{cast}No text, no labels, no readable signage, no numbers anywhere."""


PROP_PROMPT = """A PROP SHEET for {name}: {desc}

One landscape image of this one object on a plain light background, so it can be drawn the same
way every time it appears. Top row: front view, side view, back view and top view, all at the same
scale. Bottom row: a hand holding or using it, for scale; a close-up of its markings, wear and
material; and, if it opens, lights up or changes, that state. Every view is clearly the same
object: shape, proportions, materials, colors, marks and damage identical.

Draw it exactly in the style of the style plate (the first attached image): the same line, color,
light and rendering. {ref}{cast}No text, no labels, no numbers anywhere, unless the object itself
carries markings - then draw them as shapes, not readable words."""

SCENE_PROMPT = """A KEY FRAME for the scene "{name}": {desc}

One finished illustration of this scene's single most important moment - not a comic page, no
panels - as it should look in the book: the staging, the light, the emotion, the place. Landscape.

Draw it exactly in the style of the style plate (the first attached image). {ref}{cast}No text, no
lettering, no speech balloons, no captions anywhere."""

PROMPTS = {"character": SHEET_PROMPT, "place": PLACE_PROMPT, "prop": PROP_PROMPT, "scene": SCENE_PROMPT}
KINDS = tuple(PROMPTS)


# ---- the project on disk --------------------------------------------------------------------------

def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:40] or "x"


def project_dir(p):
    if not NAME.fullmatch(p or ""):
        raise ValueError("a project is a short lowercase name")
    return DATA / p


def meta(p):
    f = project_dir(p) / "project.json"
    return json.loads(f.read_text()) if f.exists() else None


def save_meta(p, m):
    project_dir(p).mkdir(parents=True, exist_ok=True)
    (project_dir(p) / "project.json").write_text(json.dumps(m, indent=1))


def target_dir(p, target):
    """The style plate's folder, or a character's."""
    if target == "style":
        return project_dir(p) / "style"
    if not NAME.fullmatch(target or "") or target not in (meta(p) or {}).get("order", []):
        raise ValueError("no such character")
    return project_dir(p) / "characters" / target


def images(d):
    return sorted(f for f in d.glob("*") if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")) if d.is_dir() else []


def kept_record(d):
    """{model id: {"file", "from"}} - what is kept for each model, and which candidate it was."""
    k = d / "kept" / "kept.json"
    return json.loads(k.read_text()) if k.exists() else {}


def kept(d):
    """{model id: path} - what is kept for each model."""
    return {model: d / "kept" / r["file"] for model, r in kept_record(d).items() if (d / "kept" / r["file"]).exists()}


def rolls(d):
    out = []
    for r in sorted((d / "rolls").glob("r*"), key=lambda x: int(x.name[1:]), reverse=True) if (d / "rolls").is_dir() else []:
        f = r / "roll.json"
        if f.exists():
            out.append(json.loads(f.read_text()))
    return out


def rel(p, path):
    return str(path.relative_to(project_dir(p)))


def state(p):
    m = meta(p)
    if m is None:
        raise FileNotFoundError(p)
    sd = target_dir(p, "style")
    out = {"name": p, "campaign": m.get("campaign"), "style": {"refs": [rel(p, f) for f in images(sd / "refs")], "notes": m.get("style_notes", ""),
                                "kept": {k: rel(p, v) for k, v in kept(sd).items()},
                                "kept_from": {k: r["from"] for k, r in kept_record(sd).items()}, "rolls": rolls(sd)},
           "characters": []}
    for key in m["order"]:
        cd = target_dir(p, key)
        c = m["chars"][key]
        ref = images(cd / "ref")
        out["characters"].append({"key": key, "name": c["name"], "kind": c.get("kind", "character"), "desc": c.get("desc", ""), "notes": c.get("notes", ""),
                                  "ref": rel(p, ref[0]) if ref else None,
                                  "kept": {k: rel(p, v) for k, v in kept(cd).items()},
                                  "kept_from": {k: r["from"] for k, r in kept_record(cd).items()}, "rolls": rolls(cd)})
    return out


# ---- rolling -------------------------------------------------------------------------------------

def references(p, target, model):
    """[(what, path)] for one model's roll, most important first."""
    d = target_dir(p, target)
    if target == "style":
        return [("reference", f) for f in images(d / "refs")][:MAX_REFS]
    plate = kept(target_dir(p, "style")).get(model)
    if not plate:
        raise ValueError(f"keep a style plate for {model} first")
    out = [("style plate", plate)]
    ref = images(d / "ref")
    if ref:
        out.append(("reference", ref[0]))
    m = meta(p)
    kind = m["chars"][target].get("kind", "character")
    if kind == "scene":         # a key frame is drawn from the sheets of whoever and wherever it names
        text = f"{m['chars'][target]['name']} {m['chars'][target].get('desc', '')}".lower()
        named = []
        for k in m["order"]:
            c = m["chars"][k]
            words = [w for w in re.findall(r"[a-z0-9']+", c["name"].lower()) if len(w) > 2 and w not in ("the", "and", "of")]
            # a person by their first name ("Alex"), a place or a thing by its noun ("workshop", "chip")
            key_word = (words[0] if c.get("kind", "character") == "character" else words[-1]) if words else None
            if k != target and c.get("kind") != "scene" and kept(target_dir(p, k)).get(model) and key_word and (
                    c["name"].lower() in text or re.search(rf"\b{re.escape(key_word)}\b", text)):
                named.append((c.get("kind", "character"), k))
        named.sort(key=lambda x: ("character", "place", "prop").index(x[0]))
        out += [(f"{kind_} sheet: {m['chars'][k]['name']}", kept(target_dir(p, k))[model]) for kind_, k in named]
        return out[:MAX_REFS + 2]
    order = [k for k in m["order"] if m["chars"][k].get("kind", "character") == kind]     # people follow people, places places
    before = [k for k in order[:order.index(target)] if kept(target_dir(p, k)).get(model)]
    for k in dict.fromkeys(before[:1] + before[-1:]):      # the anchor, and the one kept before this one
        out.append(("cast", kept(target_dir(p, k))[model]))
    return out[:MAX_REFS]


def prompt_for(p, target, refs, notes):
    if target == "style":
        text = STYLE_PROMPT
    else:
        c = meta(p)["chars"][target]
        kind = c.get("kind", "character")
        has_ref = any(w == "reference" for w, _ in refs)
        has_cast = any(w == "cast" or w.endswith("sheet") or " sheet: " in w for w, _ in refs)
        if kind == "scene":
            cast = ("Draw every character, place and object exactly as its attached sheet: faces, costumes, "
                    "architecture, materials. " if has_cast else "")
            return SCENE_PROMPT.format(name=c["name"], desc=c.get("desc") or "", ref="The attached reference image shows "
                                       "the intended composition. " if has_ref else "", cast=cast) + (
                "\n\nThe attached images, in order: " + "; ".join(f"{i}. {w}" for i, (w, _) in enumerate(refs, 1))) + (
                f"\n\nNote for this roll: {notes}" if notes else "")
        text = PROMPTS[kind].format(
            name=c["name"], desc=c.get("desc") or "(as in the reference image)",
            ref=f"The attached reference image fixes this {kind}'s look; the description wins where they differ. " if has_ref else "",
            cast=(f"The other attached sheets are this book's {'cast' if kind == 'character' else kind + 's'}: match their style, "
                  "finish and scale, so they share one world. ") if has_cast else "")
    text += "\n\nThe attached images, in order: " + "; ".join(f"{i}. {w}" for i, (w, _) in enumerate(refs, 1)) if refs else ""
    return text + (f"\n\nNote for this roll: {notes}" if notes else "")


def roll(p, target, models, each, notes):
    if not models:
        raise ValueError("pick at least one model")
    each = max(1, min(4, int(each or 1)))
    d = target_dir(p, target)
    plan = [(m, references(p, target, m)) for m in models]        # fails early if a plate is missing
    if target == "style" and not plan[0][1]:
        raise ValueError("add a reference image first")
    with _lock:
        n = len(list((d / "rolls").glob("r*"))) + 1 if (d / "rolls").is_dir() else 1
        folder = d / "rolls" / f"r{n}"
        folder.mkdir(parents=True)
        record = {"round": f"r{n}", "notes": notes or "", "models": models, "each": each, "started": time.time(),
                  "status": "rolling", "candidates": [], "errors": [],
                  "refs": {m: [f"{w}: {rel(p, f)}" for w, f in refs] for m, refs in plan}}      # what each model was shown
        (folder / "roll.json").write_text(json.dumps(record, indent=1))
    key = "" if DRY else core.api_key()
    gen = core.fake if DRY else core.generate

    def one(model, refs, i):
        t0 = time.time()
        try:
            out = gen(model, prompt_for(p, target, refs, notes), [f for _, f in refs] or None,
                      folder / f"cand-{slug(model.split('/')[-1])}-{i}", key)
            add = {"candidates": {"model": model, "file": out.name, "seconds": round(time.time() - t0)}}
        except Exception as e:      # noqa: BLE001 - one candidate failing never stops the roll
            add = {"errors": f"{model}: {str(e)[:300]}"}
        with _lock:
            r = json.loads((folder / "roll.json").read_text())
            for k, v in add.items():
                r[k].append(v)
            (folder / "roll.json").write_text(json.dumps(r, indent=1))

    def work():
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(lambda job: one(*job), [(m, refs, i) for m, refs in plan for i in range(1, each + 1)]))
        with _lock:
            r = json.loads((folder / "roll.json").read_text())
            r["status"], r["seconds"] = "done", round(time.time() - r["started"])
            (folder / "roll.json").write_text(json.dumps(r, indent=1))

    threading.Thread(target=work, daemon=True).start()
    return record


def keep(p, target, round_name, file):
    d = target_dir(p, target)
    src = d / "rolls" / round_name / file
    r = json.loads((d / "rolls" / round_name / "roll.json").read_text()) if src.exists() else None
    cand = next((c for c in (r or {}).get("candidates", []) if c["file"] == file), None)
    if not cand:
        raise ValueError("no such candidate")
    (d / "kept").mkdir(exist_ok=True)
    got = kept_record(d)
    name = f"{slug(cand['model'].split('/')[-1])}{src.suffix}"
    for old in (d / "kept").glob(f"{slug(cand['model'].split('/')[-1])}.*"):
        old.unlink()
    (d / "kept" / name).write_bytes(src.read_bytes())
    got[cand["model"]] = {"file": name, "from": f"{round_name}/{file}"}
    (d / "kept" / "kept.json").write_text(json.dumps(got, indent=1))
    return {"kept": name, "model": cand["model"]}


def save_image(d, stem, data_url):
    head, _, b64 = (data_url or "").partition(",")
    if "image/" not in head or not b64:
        raise ValueError("expected an image")
    ext = "." + head.split("image/")[1].split(";")[0].replace("jpeg", "jpg")
    d.mkdir(parents=True, exist_ok=True)
    n = len(images(d)) + 1 if stem == "ref-n" else None
    out = d / (f"ref-{n}{ext}" if n else f"{stem}{ext}")
    out.write_bytes(base64.b64decode(b64))
    return out


# ---- the page and the API ----------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_json(self, data, code=200):
        body = json.dumps(data).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}") if n else {}

    def route(self, method):
        url = urllib.parse.urlparse(self.path)
        parts = [urllib.parse.unquote(x) for x in url.path.strip("/").split("/") if x]
        data = self.body() if method in ("POST", "PUT") else {}
        if method == "GET" and not parts:
            page = (HERE / "art.html").read_text().replace("%PREFIX%", PREFIX).encode()
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page))); self.end_headers(); self.wfile.write(page)
            return
        if parts[:1] == ["files"] and method == "GET":
            p = project_dir(parts[1])
            f = (p / "/".join(parts[2:])).resolve()
            if p.resolve() not in f.parents or not f.is_file():
                raise FileNotFoundError(url.path)
            body = f.read_bytes()
            self.send_response(200); self.send_header("Content-Type", mimetypes.guess_type(str(f))[0] or "application/octet-stream")
            self.send_header("Cache-Control", "no-store"); self.send_header("Content-Length", str(len(body))); self.end_headers()
            self.wfile.write(body)
            return
        if parts[:2] != ["api", "projects"]:
            raise FileNotFoundError(url.path)
        rest = parts[2:]
        if not rest:
            if method == "GET":
                return self.send_json({"projects": sorted(d.name for d in DATA.iterdir() if (d / "project.json").exists()) if DATA.is_dir() else []})
            p = slug(data.get("name"))
            if meta(p) is None:
                save_meta(p, {"order": [], "chars": {}})
            return self.send_json(state(p))
        p, rest = rest[0], rest[1:]
        m = meta(p)
        if m is None:
            raise FileNotFoundError(p)
        if not rest and method == "GET":
            return self.send_json(state(p))
        if rest == ["style", "refs"] and method == "POST":
            save_image(target_dir(p, "style") / "refs", "ref-n", data.get("data_url"))
        elif rest[:2] == ["style", "refs"] and method == "DELETE" and len(rest) == 3:
            f = target_dir(p, "style") / "refs" / Path(rest[2]).name
            f.unlink(missing_ok=True)
        elif rest == ["characters"] and method == "POST":
            name = (data.get("name") or "").strip()
            key = slug(name)
            if not name or key in m["order"]:
                raise ValueError("a new name, please")
            m["order"].append(key)
            m["chars"][key] = {"name": name, "desc": (data.get("desc") or "").strip(),
                               "kind": data.get("kind") if data.get("kind") in KINDS else "character"}
            save_meta(p, m)
        elif not rest and method == "PUT":
            if "campaign" in data:          # the campaign whose canon the cast is picked from
                m["campaign"] = (data.get("campaign") or "").strip() or None
                save_meta(p, m)
        elif rest[:1] == ["characters"] and len(rest) == 2 and method == "PUT":
            c = m["chars"].get(rest[1]) or {}
            for k in ("name", "desc", "notes"):
                if k in data:
                    c[k] = (data[k] or "").strip()
            save_meta(p, m)
        elif rest[:1] == ["characters"] and len(rest) == 2 and method == "DELETE":
            if rest[1] in m["order"]:
                m["order"].remove(rest[1]); m["chars"].pop(rest[1], None); save_meta(p, m)
        elif rest[:1] == ["characters"] and len(rest) == 3 and rest[2] == "ref" and method == "POST":
            d = target_dir(p, rest[1]) / "ref"
            for old in images(d):
                old.unlink()
            save_image(d, "ref", data.get("data_url"))
        elif rest[-1:] == ["roll"] and method == "POST":
            target = "style" if rest[0] == "style" else rest[1]
            if target == "style" and "notes" in data:
                m["style_notes"] = data.get("notes") or ""; save_meta(p, m)
            roll(p, target, data.get("models") or [], data.get("each"), (data.get("notes") or "").strip())
        elif rest == ["keep"] and method == "POST":
            return self.send_json({**keep(p, data.get("target"), data.get("round"), data.get("file")), **state(p)})
        else:
            raise FileNotFoundError(url.path)
        self.send_json(state(p))

    def handle_any(self, method):
        try:
            self.route(method)
        except FileNotFoundError as e:
            self.send_json({"error": f"not found: {e}"}, 404)
        except (ValueError, KeyError, SystemExit) as e:
            self.send_json({"error": str(e)}, 400)

    def do_GET(self):
        self.handle_any("GET")

    def do_POST(self):
        self.handle_any("POST")

    def do_PUT(self):
        self.handle_any("PUT")

    def do_DELETE(self):
        self.handle_any("DELETE")


if __name__ == "__main__":
    DATA.mkdir(parents=True, exist_ok=True)
    print(f"art department: http://0.0.0.0:{PORT}{PREFIX}  data in {DATA}" + ("  (DRY: no model is called)" if DRY else ""), flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
