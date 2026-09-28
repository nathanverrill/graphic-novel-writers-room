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
             "one if it matters.\n\n"
             "When your reply proposes anything actionable, END it with a fenced block of the "
             "concrete edits, so the team can apply them with one click:\n"
             "```suggestions\n"
             '[{"file": "characters.md", "title": "at most ten words", '
             '"change": "one to three sentences saying exactly what to change"}]\n'
             "```\n"
             "2 to 6 suggestions, each targeting ONE existing text file from the material by its "
             "exact name. Valid JSON only inside the block. Purely informational replies get no "
             "block."]
    imgs = []
    for b in bucket().list_blobs(prefix=f"{camp}/files/"):
        name = b.name.split("/", 2)[2]
        if ext(name) in IMG_TYPE:
            imgs.append(name)
        else:
            try:
                parts.append(f"## {name}\n{b.download_as_text()[:80000]}")
            except Exception:
                pass
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
    """Apply ONE accepted suggestion to its file; the client loops for feedback per item."""
    camp_ok(camp)
    key = _key()
    if not key:
        raise HTTPException(400, "no API key set yet - use the API key button")
    name = name_ok(str(d.get("file") or ""))
    title = str(d.get("title") or "")[:120]
    change = str(d.get("change") or "").strip()[:1200]
    if ext(name) not in TEXT_EXT or not change:
        raise HTTPException(400, "a change and a text file to change")
    blob = bucket().blob(f"{camp}/files/{name}")
    try:
        before = blob.download_as_text()
    except Exception:
        raise HTTPException(404, f"no such file: {name}")
    out = _model(key, [
        {"role": "system", "content":
         f"You are the keeper of the draft files of {CAMPS[camp]}, a hard-SF graphic novel. "
         "Apply exactly one requested change to one file. Return the COMPLETE updated file and "
         "nothing else - no preamble, no code fences. Preserve everything the change does not "
         "touch; keep the file's format and heading structure; weave the change in cleanly "
         "wherever the file addresses that topic (it may touch several sections)."},
        {"role": "user", "content":
         f"The file `{name}`:\n\n{before[:200000]}\n\nThe change to apply:\n{title}: {change}\n\n"
         "Return the complete updated file."}], 16000)
    out = re.sub(r"^```[a-z]*\n|\n```$", "", out.strip())
    if len(out) < len(before) * 0.4:
        raise HTTPException(502, "the rewrite came back too short - file left untouched")
    blob.upload_from_string(out, content_type="text/markdown")
    entry = {"ts": int(time.time()), "file": name, "title": title, "change": change,
             "chars_before": len(before), "chars_after": len(out)}
    logblob = bucket().blob(f"{camp}/log.jsonl")
    try:
        log = logblob.download_as_text()
    except Exception:
        log = ""
    logblob.upload_from_string(log + json.dumps(entry) + "\n", content_type="application/json")
    return entry


@app.get("/api/{camp}/log")
def get_log(camp: str):
    camp_ok(camp)
    try:
        lines = bucket().blob(f"{camp}/log.jsonl").download_as_text().strip().splitlines()
    except Exception:
        return []
    return [json.loads(ln) for ln in lines[-100:]][::-1]
