# Riff: the brainstorming room after the writers' room. Pre-production is done and
# everything here is treated as draft - the next team chats with the material to
# improve a character, sharpen the plot, poke holes. One workspace per campaign,
# files shared in the bucket, chat per browser.
import base64
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response

from store import bucket  # GCS when BUCKET is set, ./data files when not

OPENROUTER = "https://openrouter.ai/api/v1"
CHAT_MODEL = os.getenv("CHAT_MODEL", "openai/gpt-5.6-luna")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "openai/gpt-image-2.5-sunburst")   # what Easel draws with
EASEL_BUCKET = {"avalanche": "evoke-prosperity-easel", "avalanche-2": "evoke-prosperity-easel-2",
                "avengers": "evoke-prosperity-easel-3"}
CAMPS = {"avalanche": "Avalanche", "avalanche-2": "Avalanche 2", "avengers": "Avengers",
         "prosperity": "Prosperity", "worldbuilding": "Worldbuilding"}
TEXT_EXT = (".md", ".txt")
IMG_TYPE = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".webp": "image/webp", ".gif": "image/gif"}
MAX_FILE = 2 * 1024 * 1024

app = FastAPI()
INDEX = (Path(__file__).parent / "index.html").read_text()


def camp_ok(camp):
    if camp not in CAMPS:
        raise HTTPException(404, "no such campaign")


def name_ok(name):
    if not re.fullmatch(r"[\w][\w .()-]{0,80}\.[A-Za-z0-9]{1,5}", name):
        raise HTTPException(400, "give the file a plain name with an extension")
    return name


def ext(name):
    return "." + name.rsplit(".", 1)[-1].lower()


@app.get("/")
def index():
    return HTMLResponse(INDEX)


def _key():
    try:
        return json.loads(bucket().blob("settings.json").download_as_text()).get("key", "")
    except Exception:
        return ""


@app.get("/api/config")
def config():
    return {"configured": bool(_key()), "campaigns": CAMPS}


@app.post("/api/key")
def set_key(d: dict = Body(...)):
    k = (d.get("key") or "").strip()
    if not k:
        raise HTTPException(400, "paste an OpenRouter key")
    bucket().blob("settings.json").upload_from_string(json.dumps({"key": k}))
    return {"ok": True}


@app.get("/api/{camp}/files")
def files(camp: str):
    camp_ok(camp)
    out = []
    for b in bucket().list_blobs(prefix=f"{camp}/files/"):
        name = b.name.split("/", 2)[2]
        out.append({"name": name, "image": ext(name) in IMG_TYPE})
    return sorted(out, key=lambda f: (f["image"], f["name"]))


@app.post("/api/{camp}/file")
def add_file(camp: str, d: dict = Body(...)):
    camp_ok(camp)
    name = name_ok((d.get("name") or "").strip())
    b = bucket().blob(f"{camp}/files/{name}")
    if d.get("image"):
        head, _, b64 = d["image"].partition(",")
        if ext(name) not in IMG_TYPE or not b64:
            raise HTTPException(400, "images must be png, jpg, webp or gif")
        raw = base64.b64decode(b64)
        if len(raw) > MAX_FILE * 4:
            raise HTTPException(400, "image too large")
        b.upload_from_string(raw, content_type=IMG_TYPE[ext(name)])
    else:
        if ext(name) not in TEXT_EXT:
            raise HTTPException(400, "text files must be .md or .txt")
        text = d.get("text") or ""
        if len(text) > MAX_FILE:
            raise HTTPException(400, f"over {MAX_FILE // 1024}KB")
        b.upload_from_string(text, content_type="text/markdown")
    return {"ok": True, "name": name}


@app.get("/api/{camp}/file/{name}")
def get_file(camp: str, name: str):
    camp_ok(camp)
    b = bucket().blob(f"{camp}/files/{name_ok(name)}")
    try:
        if ext(name) in IMG_TYPE:
            return Response(b.download_as_bytes(), media_type=IMG_TYPE[ext(name)],
                            headers={"Cache-Control": "no-cache"})
        return {"name": name, "text": b.download_as_text()}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(404, "no such file")


@app.delete("/api/{camp}/file/{name}")
def del_file(camp: str, name: str):
    camp_ok(camp)
    blob = bucket().blob(f"{camp}/files/{name_ok(name)}")
    try:
        blob.delete()
    except AttributeError:      # local mode: remove the file directly
        blob._p.unlink(missing_ok=True)
        blob._m.unlink(missing_ok=True)
    except Exception:
        pass
    return {"ok": True}


@app.post("/api/{camp}/chat")
def chat(camp: str, d: dict = Body(...)):
    camp_ok(camp)
    key = _key()
    if not key:
        raise HTTPException(400, "no API key set yet - use the API key button")
    msgs = [m for m in (d.get("messages") or [])
            if isinstance(m, dict) and m.get("role") in ("user", "assistant") and m.get("content")][-30:]
    if not msgs:
        raise HTTPException(400, "say something")
    parts = [f"You are the brainstorming partner of the team now working on {CAMPS[camp]}, a "
             "hard-SF graphic novel. The writers' room has finished pre-production; everything "
             "below is DRAFT - raw material to improve, not gospel. Help the team riff: sharpen "
             "characters, fix the plot, find holes, propose better versions. Be concrete and "
             "specific to this material, offer options with trade-offs, keep replies tight, and "
             "when you propose a change say exactly which file and section it would change. "
             "Images in the workspace are listed by name; you cannot see them, so ask what is in "
             "one if it matters. If the material includes refinements.md, those are the changes "
             "the team has ALREADY accepted: treat them as the newest layer of canon, overriding "
             "the draft files where they conflict, and never re-suggest what is already there.\n\n"
             "When your reply proposes anything actionable, END it with a fenced block of the "
             "concrete edits, so the team can apply them with one click:\n"
             "```suggestions\n"
             '[{"file": "characters.md", "title": "at most ten words", '
             '"change": "one to three sentences saying exactly what to change"}]\n'
             "```\n"
             "2 to 6 suggestions, each targeting ONE existing text file from the material by its "
             "exact name. Valid JSON only inside the block. Purely informational replies get no "
             "block."]
    mat, imgs = _material(camp)
    parts += mat
    if imgs:
        parts.append("## Images in the workspace (by name)\n" + "\n".join(f"- {i}" for i in imgs))
    reply = _model(key, [{"role": "system", "content": "\n\n".join(parts)}] + msgs, 4000)
    sugg = []
    m = re.search(r"```suggestions\s*(.*?)```", reply, re.S)
    if m:
        reply = (reply[:m.start()] + reply[m.end():]).strip()
        try:
            raw = json.loads(m.group(1))
            sugg = [{"file": str(s.get("file", ""))[:100], "title": str(s.get("title", ""))[:120],
                     "change": str(s.get("change", ""))[:1200]}
                    for s in raw if isinstance(s, dict) and s.get("file") and s.get("change")][:6]
        except Exception:
            pass
    return {"reply": reply, "suggestions": sugg}


def _material(camp, cap=80000):
    """All text files, with refinements.md LAST under a banner: it is the newest canon and
    beats the drafts wherever they conflict. Buried mid-list, models kept siding with the
    drafts ('oil tycoon' over the accepted rework)."""
    parts, imgs, refin = [], [], None
    for b in bucket().list_blobs(prefix=f"{camp}/files/"):
        name = b.name.split("/", 2)[2]
        if ext(name) in IMG_TYPE:
            imgs.append(name)
        else:
            try:
                text = b.download_as_text()[:cap]
            except Exception:
                continue
            if name == "refinements.md":
                refin = text
            else:
                parts.append(f"## {name} (draft as handed over)\n{text}")
    if refin is not None:
        parts.append(
            "## refinements.md — THE ACCEPTED REFINEMENTS: NEWEST CANON\n"
            "The team accepted these AFTER the drafts above were written, and the drafts have "
            "NOT been updated to reflect them. Wherever a draft and a refinement conflict - a "
            "character's identity, what exists in the world, a plot point - THE REFINEMENT WINS "
            "and the draft version is obsolete. Apply them fully.\n\n" + refin)
    return parts, imgs


def _model(key, messages, max_tokens):
    payload = {"model": CHAT_MODEL, "max_tokens": max_tokens, "messages": messages}
    req = urllib.request.Request(
        f"{OPENROUTER}/chat/completions", data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "HTTP-Referer": "https://github.com/writers-room", "X-Title": "riff"})
    try:
        with urllib.request.urlopen(req, timeout=280) as r:
            result = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise HTTPException(502, f"HTTP {e.code} {e.read()[:300].decode(errors='replace')}")
    except Exception as e:
        raise HTTPException(502, str(e))
    reply = ((result.get("choices") or [{}])[0].get("message") or {}).get("content")
    if not reply:
        raise HTTPException(502, "no reply in the response")
    return reply


@app.post("/api/{camp}/apply")
def apply(camp: str, d: dict = Body(...)):
    """Accept ONE suggestion: the draft files stay as they are (the current state), the
    accepted change is recorded in refinements.md, and future chats build on it."""
    camp_ok(camp)
    name = name_ok(str(d.get("file") or ""))
    title = str(d.get("title") or "")[:120]
    change = str(d.get("change") or "").strip()[:1200]
    if not change:
        raise HTTPException(400, "nothing to accept")
    entry = {"ts": int(time.time()), "file": name, "title": title, "change": change}
    logblob = bucket().blob(f"{camp}/log.jsonl")
    try:
        log = logblob.download_as_text()
    except Exception:
        log = ""
    logblob.upload_from_string(log + json.dumps(entry) + "\n", content_type="application/json")
    # the showrunner's notes: accepted direction on top of the untouched draft
    ref = bucket().blob(f"{camp}/files/refinements.md")
    try:
        text = ref.download_as_text()
    except Exception:
        text = REFIN_HEADER
    when = time.strftime("%Y-%m-%d %H:%M", time.localtime(entry["ts"]))
    text += f"\n## {title or 'Update'} — {name} ({when})\n\n{change}\n"
    ref.upload_from_string(text, content_type="text/markdown")
    return entry


# ---- synthesis: fold the refinements into the drafts, then archive them ----

def _refinements(camp):
    try:
        return bucket().blob(f"{camp}/files/refinements.md").download_as_text()
    except Exception:
        return ""


REFIN_HEADER = ("# Refinements - the showrunner's notes\n\nThe draft files are the current "
                "state; earlier refinement passes are folded in and archived. These are the "
                "changes accepted since the last synthesis; they override the drafts wherever "
                "the two conflict. Newest last.\n")


@app.get("/api/{camp}/pending")
def pending(camp: str):
    """How much refinement is waiting, and which files it targets."""
    camp_ok(camp)
    text = _refinements(camp)
    decisions = len(re.findall(r"(?m)^\*\*", text)) + len(re.findall(r"(?m)^## .+ — .+\(", text))
    targets = set(re.findall(r"(?m)^## ([\w. -]+\.md)\s*$", text))
    targets |= {m for m in re.findall(r"(?m)^## .+ — ([\w. -]+\.md) \(", text)}
    have = {f["name"] for f in files(camp) if not f["image"]}
    targets = sorted((targets & have) - {"refinements.md"})
    if decisions and not targets:
        targets = sorted(have - {"refinements.md", "open-items.md"})
    return {"decisions": decisions, "targets": targets}


@app.post("/api/{camp}/synthesize")
def synthesize(camp: str, d: dict = Body(...)):
    """Fold the refinements into ONE draft file; the client loops per target for feedback.
    The prior version of the file is archived first."""
    camp_ok(camp)
    key = _key()
    if not key:
        raise HTTPException(400, "no API key set yet - use the API key button")
    name = name_ok(str(d.get("file") or ""))
    refin = _refinements(camp)
    if not refin.strip():
        raise HTTPException(400, "no refinements to fold in")
    blob = bucket().blob(f"{camp}/files/{name}")
    try:
        before = blob.download_as_text()
    except Exception:
        raise HTTPException(404, f"no such file: {name}")
    out = _model(key, [
        {"role": "system", "content":
         f"You are updating the canon of {CAMPS[camp]}, a hard-SF graphic novel. The team's "
         "accepted refinements must be folded into the file so it stands alone as current "
         "canon. Rewrite the COMPLETE file: weave in every refinement that concerns it; remove "
         "or rewrite anything a refinement supersedes; keep the file's structure, heading style "
         "and level of detail; keep everything the refinements do not touch; invent nothing. "
         "Return only the file content - no preamble, no code fences."},
        {"role": "user", "content":
         f"The file `{name}`:\n\n{before[:200000]}\n\nTHE ACCEPTED REFINEMENTS (newest canon; "
         f"apply the ones that concern this file):\n\n{refin[:120000]}\n\n"
         "Return the complete updated file."}], 16000)
    out = re.sub(r"^```[a-z]*\n|\n```$", "", out.strip())
    if len(out) < len(before) * 0.4:
        raise HTTPException(502, "the rewrite came back too short - file left untouched")
    ts = int(time.time() * 1000)
    bucket().blob(f"{camp}/archive/{ts}-{name}").upload_from_string(before, content_type="text/markdown")
    blob.upload_from_string(out, content_type="text/markdown")
    return {"file": name, "chars_before": len(before), "chars_after": len(out)}


@app.post("/api/{camp}/synthesize-finish")
def synthesize_finish(camp: str):
    """The refinements are folded in: archive them and start a fresh, empty pass."""
    camp_ok(camp)
    refin = _refinements(camp)
    if not refin.strip():
        return {"ok": True, "archived": False}
    ts = int(time.time() * 1000)
    bucket().blob(f"{camp}/archive/{ts}-refinements.md").upload_from_string(
        refin, content_type="text/markdown")
    bucket().blob(f"{camp}/files/refinements.md").upload_from_string(
        REFIN_HEADER, content_type="text/markdown")
    return {"ok": True, "archived": True}


# ---- the compiled canon: everything in one .md, to copy out or save as a version ----

def _compiled_text(camp):
    parts, imgs = _material(camp, cap=120000)
    head = (f"# {CAMPS[camp]} — compiled canon\n\n"
            f"Everything the {CAMPS[camp]} workspace holds, in one file. Draft files first; if "
            "a refinements section closes the file, it is the newest canon and overrides the "
            "drafts wherever they conflict.\n")
    if imgs:
        head += "\nImages in the workspace (not embedded): " + ", ".join(imgs) + "\n"
    return head + "\n\n" + "\n\n".join(parts) + "\n"


@app.get("/api/{camp}/compile")
def compile_live(camp: str):
    camp_ok(camp)
    return {"text": _compiled_text(camp)}


@app.post("/api/{camp}/compile/save")
def compile_save(camp: str):
    camp_ok(camp)
    ts = int(time.time() * 1000)
    bucket().blob(f"{camp}/compiled/{ts}.md").upload_from_string(
        _compiled_text(camp), content_type="text/markdown")
    return {"ts": ts}


@app.get("/api/{camp}/compiled")
def compiled_list(camp: str):
    camp_ok(camp)
    out = []
    for b in bucket().list_blobs(prefix=f"{camp}/compiled/"):
        try:
            out.append(int(b.name.rsplit("/", 1)[1].split(".")[0]))
        except ValueError:
            pass
    return sorted(out, reverse=True)


@app.get("/api/{camp}/compiled/{ts}")
def compiled_get(camp: str, ts: int):
    camp_ok(camp)
    try:
        return {"ts": ts, "text": bucket().blob(f"{camp}/compiled/{ts}.md").download_as_text()}
    except Exception:
        raise HTTPException(404, "no such version")


# ---- visualizations: infographics and pages from the material + refinements ----

INFO_STYLE = ("Style: clean editorial infographic, deep slate background, glacial ice-blue and "
              "warm amber accents, bold condensed sans-serif labels, subtle grid, high contrast, "
              "2046 hard-sci-fi documentary tone.")
PAGE_STYLE = ("Style: graphic novel page, hard-SF realism, cinematic staging, inked lines over a "
              "cold Antarctic palette. Wordless: no captions, no balloons, no lettering anywhere.")
PROMPT_WRITER = (
    "You write prompts for an image model, from story material. Write ONE image-generation "
    "prompt and nothing else - no preamble, no options, no markdown. Rules: name every text "
    "label the image must render, in double quotes, short (2-6 words) and few (a title plus at "
    "most 10 labels - image models mangle long or numerous text); describe the layout precisely "
    "(what sits where); ground every name, fact and look in the material and never invent; "
    "treat refinements.md as the newest canon, overriding the drafts; at most 220 words; end "
    "with the style line given.")
VIZ = {
    "info": ("The book at a glance", "A single poster-style infographic that captures the whole "
             "book at a glance: the title large at the top; a one-line premise beneath it; the "
             "hero and the antagonist facing each other with their names; the central threat "
             "between or behind them; the settings as small labeled vignettes; and a miniature "
             "story arc along the bottom with the key beats named. A reader should grok the "
             "entire story from this one image."),
    "beats": ("Story beats", "A story-beats infographic titled with the book's title: the hero's "
              "journey drawn as one rising-then-falling arc from left to right with 7 named beat "
              "nodes. Each node is a key moment of THIS story (a 2-4 word name in quotes) placed "
              "at its journey stage (ordinary world, the call, crossing the threshold, trials, "
              "the abyss, transformation, return). Mark the midpoint discovery and the lowest "
              "point visually."),
    "world": ("The world", "A one-page world infographic: the settings as small map vignettes "
              "with their key sites labeled, the institutions and how they connect drawn as a "
              "network with arrows, and the year \"2046\" prominent."),
    "cast": ("The cast", "A cast sheet: the main characters side by side, each with a portrait "
             "matching their visual description in the material, their name, and their role. "
             "Include TJ the robot dog."),
    "settings": ("Key settings", "A key-locations sheet: the 4-6 places the story keeps "
                 "returning to, each as a small scene vignette with its name, arranged in a "
                 "grid."),
}


def _viz_ok(kind):
    if not re.fullmatch(r"[a-z0-9-]{1,30}", kind):
        raise HTTPException(400, "bad kind")


def _image(key, prompt):
    req = urllib.request.Request(
        f"{OPENROUTER}/images", data=json.dumps({"model": IMAGE_MODEL, "prompt": prompt}).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "HTTP-Referer": "https://github.com/writers-room", "X-Title": "riff"})
    try:
        with urllib.request.urlopen(req, timeout=280) as r:
            result = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise HTTPException(502, f"{IMAGE_MODEL}: HTTP {e.code} {e.read()[:300].decode(errors='replace')}")
    except Exception as e:
        raise HTTPException(502, str(e))
    data = (result.get("data") or [{}])[0]
    if not data.get("b64_json"):
        raise HTTPException(502, "no image in the reply")
    return base64.b64decode(data["b64_json"])


@app.post("/api/{camp}/beats")
def story_beats(camp: str):
    """Name the key moments, aligned with the hero's journey, from material + refinements."""
    camp_ok(camp)
    key = _key()
    if not key:
        raise HTTPException(400, "no API key set yet - use the API key button")
    material = "\n\n".join(_material(camp)[0])
    text = _model(key, [
        {"role": "system", "content":
         "From the story material, name the 7 beats of this book as key moments aligned with "
         "the hero's journey. The refinements section at the end is the newest canon: where it "
         "contradicts the drafts, the refinements win. Reply with ONLY a JSON "
         "array of 7 objects, in story order: {\"name\": \"2-4 word beat name\", \"stage\": "
         "\"the journey stage\", \"happens\": \"one sentence of what happens\", \"image\": "
         "\"one sentence: the single image the reader must see\"}."},
        {"role": "user", "content": material}], 3000)
    m = re.search(r"\[.*\]", text, re.S)
    if not m:
        raise HTTPException(502, "no beats in the reply")
    try:
        beats = [{"name": str(b.get("name", ""))[:60], "stage": str(b.get("stage", ""))[:60],
                  "happens": str(b.get("happens", ""))[:300], "image": str(b.get("image", ""))[:300]}
                 for b in json.loads(m.group(0)) if isinstance(b, dict)][:8]
    except Exception:
        raise HTTPException(502, "unparseable beats")
    return {"beats": beats}


@app.post("/api/{camp}/visualize")
def visualize(camp: str, d: dict = Body(...)):
    """One visualization: the chat model writes the image prompt from the material, the image
    model renders it, and the result is saved as a new version of its kind."""
    camp_ok(camp)
    key = _key()
    if not key:
        raise HTTPException(400, "no API key set yet - use the API key button")
    kind = str(d.get("kind") or "")
    if kind == "page":
        b = d.get("beat") or {}
        n = int(d.get("n") or 1)
        title = f"Page {n} · {b.get('name', '?')}"
        spec = (f"One wordless graphic-novel page of 3-6 panels for the beat \"{b.get('name')}\" "
                f"({b.get('stage')}): {b.get('happens')} The page must land this image: "
                f"{b.get('image')} Characters drawn to their visual descriptions in the material.")
        style, kindkey = PAGE_STYLE, f"page-{n:02d}"
    elif kind in VIZ:
        title, spec = VIZ[kind]
        style, kindkey = INFO_STYLE, kind
    else:
        raise HTTPException(400, "unknown kind")
    material = "\n\n".join(_material(camp)[0])
    prompt = _model(key, [
        {"role": "system", "content": PROMPT_WRITER},
        {"role": "user", "content": f"THE MATERIAL:\n{material}\n\nWrite the image prompt for: "
                                    f"{spec}\n\nThe refinements section at the end of the "
                                    "material is the newest canon - where it contradicts the "
                                    "drafts (who a character is, what exists in this world), "
                                    "the refinements win and the draft version must not appear "
                                    f"in the image.\n\nStyle line to end with: {style}"}], 2500).strip()
    png = _image(key, prompt)
    ts = int(time.time() * 1000)
    blob = bucket().blob(f"{camp}/viz/{kindkey}/{ts}.png")
    blob.metadata = {"title": title, "prompt": prompt[:1500]}
    blob.upload_from_string(png, content_type="image/png")
    _mirror_to_easel(camp, png, prompt)
    return {"kind": kindkey, "ts": ts, "title": title}


def _mirror_to_easel(camp, png, prompt):
    """A courtesy copy into the campaign's Easel gallery - same image, same prompt - so the
    team can see and iterate there. Never fails the visualization."""
    if not os.getenv("BUCKET"):
        return
    try:
        import uuid
        from google.cloud import storage
        blob = storage.Client().bucket(EASEL_BUCKET[camp]).blob(
            f"img/{int(time.time() * 1000)}-{uuid.uuid4().hex[:6]}.png")
        blob.metadata = {"model": IMAGE_MODEL, "prompt": prompt[:800]}
        blob.upload_from_string(png, content_type="image/png")
    except Exception:
        pass


@app.get("/api/{camp}/viz")
def viz_list(camp: str):
    camp_ok(camp)
    kinds = {}
    for b in bucket().list_blobs(prefix=f"{camp}/viz/"):
        _, _, kind, fname = b.name.split("/", 3)
        ts = int(fname.split(".")[0])
        m = b.metadata or {}
        k = kinds.setdefault(kind, {"kind": kind, "title": m.get("title", kind), "versions": []})
        k["versions"].append(ts)
        k["title"] = m.get("title", k["title"])
    for k in kinds.values():
        k["versions"].sort(reverse=True)
    return sorted(kinds.values(), key=lambda k: k["kind"])


@app.get("/api/{camp}/viz/{kind}/{ts}")
def viz_image(camp: str, kind: str, ts: int):
    camp_ok(camp)
    _viz_ok(kind)
    b = bucket().blob(f"{camp}/viz/{kind}/{ts}.png")
    try:
        data = b.download_as_bytes()
    except Exception:
        raise HTTPException(404, "no such visualization")
    return Response(data, media_type="image/png",
                    headers={"Cache-Control": "public, max-age=31536000, immutable",
                             "X-Prompt": ""})


@app.get("/api/{camp}/viz/{kind}/{ts}/meta")
def viz_meta(camp: str, kind: str, ts: int):
    camp_ok(camp)
    _viz_ok(kind)
    b = bucket().blob(f"{camp}/viz/{kind}/{ts}.png")
    for blob in bucket().list_blobs(prefix=f"{camp}/viz/{kind}/{ts}.png"):
        return {"title": (blob.metadata or {}).get("title", kind),
                "prompt": (blob.metadata or {}).get("prompt", "")}
    raise HTTPException(404, "no such visualization")


@app.get("/api/{camp}/log")
def get_log(camp: str):
    camp_ok(camp)
    try:
        lines = bucket().blob(f"{camp}/log.jsonl").download_as_text().strip().splitlines()
    except Exception:
        return []
    return [json.loads(ln) for ln in lines[-100:]][::-1]
