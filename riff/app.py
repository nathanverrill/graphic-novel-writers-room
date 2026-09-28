# Riff: the brainstorming room after the writers' room. Pre-production is done and
# everything here is treated as draft - the next team chats with the material to
# improve a character, sharpen the plot, poke holes. One workspace per campaign,
# files shared in the bucket, chat per browser. As simple as possible.
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
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "google/gemini-3.1-flash-image")
CAMPS = {"avalanche": "Avalanche", "avalanche-2": "Avalanche 2", "avengers": "Avengers"}
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
    parts, imgs = [], []
    for b in bucket().list_blobs(prefix=f"{camp}/files/"):
        name = b.name.split("/", 2)[2]
        if ext(name) in IMG_TYPE:
            imgs.append(name)
        else:
            try:
                parts.append(f"## {name}\n{b.download_as_text()[:cap]}")
            except Exception:
                pass
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
        text = ("# Refinements - the showrunner's notes\n\nThe draft files below this one are "
                "the current state as handed over by the writers' room, untouched. These are the "
                "changes the team has accepted since; each names the file it concerns, and they "
                "override the draft where the two conflict. Newest last.\n")
    when = time.strftime("%Y-%m-%d %H:%M", time.localtime(entry["ts"]))
    text += f"\n## {title or 'Update'} — {name} ({when})\n\n{change}\n"
    ref.upload_from_string(text, content_type="text/markdown")
    return entry


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
         "the hero's journey. Treat refinements.md as the newest canon. Reply with ONLY a JSON "
         "array of 7 objects, in story order: {\"name\": \"2-4 word beat name\", \"stage\": "
         "\"the journey stage\", \"happens\": \"one sentence of what happens\", \"image\": "
         "\"one sentence: the single image the reader must see\"}."},
        {"role": "user", "content": material}], 1200)
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
                                    f"{spec}\n\nStyle line to end with: {style}"}], 700).strip()
    png = _image(key, prompt)
    ts = int(time.time() * 1000)
    blob = bucket().blob(f"{camp}/viz/{kindkey}/{ts}.png")
    blob.metadata = {"title": title, "prompt": prompt[:1500]}
    blob.upload_from_string(png, content_type="image/png")
    return {"kind": kindkey, "ts": ts, "title": title}


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
