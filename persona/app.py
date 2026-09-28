# Persona: build one character bot together. The .md files are the character's
# canon, the voice field tunes how they speak, the face is the avatar. Everything
# lives in one GCS bucket (bot.json + face + settings.json), so the whole team
# edits and talks to the same character. Chat goes through OpenRouter with the
# shared key, same as Easel.
import base64
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response

OPENROUTER = "https://openrouter.ai/api/v1"
CHAT_MODEL = os.getenv("CHAT_MODEL", "openai/gpt-5.6-luna")
MAX_FILE = 512 * 1024

app = FastAPI()
INDEX = (Path(__file__).parent / "index.html").read_text()
from store import bucket  # noqa: E402 - GCS when BUCKET is set, ./data files when not


def _json(name, default):
    try:
        return json.loads(bucket().blob(name).download_as_text())
    except Exception:
        return default


def _bot():
    return _json("bot.json", {"voice": "", "files": {}})


def _save_bot(b):
    bucket().blob("bot.json").upload_from_string(json.dumps(b))


def _key():
    return _json("settings.json", {}).get("key", "")


def _name_ok(name):
    return bool(re.fullmatch(r"[\w][\w .()-]{0,80}\.md", name))


@app.get("/")
def index():
    return HTMLResponse(INDEX)


@app.get("/api/bot")
def bot():
    b = _bot()
    face = False
    try:
        face = bucket().blob("face").exists()
    except Exception:
        pass
    return {"configured": bool(_key()), "voice": b.get("voice", ""), "face": face,
            "files": [{"name": n, "chars": len(t)} for n, t in sorted(b.get("files", {}).items())]}


@app.post("/api/key")
def set_key(d: dict = Body(...)):
    k = (d.get("key") or "").strip()
    if not k:
        raise HTTPException(400, "paste an OpenRouter key")
    bucket().blob("settings.json").upload_from_string(json.dumps({"key": k}))
    return {"ok": True}


@app.post("/api/voice")
def voice(d: dict = Body(...)):
    b = _bot()
    b["voice"] = (d.get("voice") or "")[:8000]
    _save_bot(b)
    return {"ok": True}


@app.post("/api/file")
def add_file(d: dict = Body(...)):
    name, text = (d.get("name") or "").strip(), d.get("text") or ""
    if not name.endswith(".md"):
        name += ".md"
    if not _name_ok(name):
        raise HTTPException(400, "give the file a plain name ending in .md")
    if len(text) > MAX_FILE:
        raise HTTPException(400, f"{name}: over {MAX_FILE // 1024}KB")
    b = _bot()
    b["files"][name] = text
    _save_bot(b)
    return {"ok": True, "name": name}


@app.get("/api/file/{name}")
def get_file(name: str):
    b = _bot()
    if name not in b["files"]:
        raise HTTPException(404, "no such file")
    return {"name": name, "text": b["files"][name]}


@app.delete("/api/file/{name}")
def del_file(name: str):
    b = _bot()
    if name in b["files"]:
        del b["files"][name]
        _save_bot(b)
    return {"ok": True}


@app.get("/api/versions")
def versions():
    return list(reversed(_json("versions.json", [])))


@app.post("/api/version")
def add_version(d: dict = Body(...)):
    import time as _t
    vs = _json("versions.json", [])
    tr = [{"q": str(t.get("q", ""))[:2000], "a": str(t.get("a", ""))[:8000]}
          for t in (d.get("transcript") or []) if isinstance(t, dict)][:20]
    vs.append({"n": (vs[-1]["n"] + 1) if vs else 1, "ts": int(_t.time()),
               "voice": (d.get("voice") or "")[:8000], "files": [str(f)[:100] for f in (d.get("files") or [])][:50],
               "transcript": tr})
    vs = vs[-100:]
    bucket().blob("versions.json").upload_from_string(json.dumps(vs))
    return {"ok": True, "n": vs[-1]["n"]}


@app.post("/api/face")
def set_face(d: dict = Body(...)):
    head, _, b64 = (d.get("image") or "").partition(",")
    if not (head.startswith("data:image/") and b64):
        raise HTTPException(400, "expected an image data: URL")
    mt = head[5:].split(";")[0]
    blob = bucket().blob("face")
    blob.upload_from_string(base64.b64decode(b64), content_type=mt)
    return {"ok": True}


@app.get("/api/face")
def get_face():
    blob = bucket().blob("face")
    try:
        data = blob.download_as_bytes()
    except Exception:
        raise HTTPException(404, "no face yet")
    return Response(data, media_type=blob.content_type or "image/png",
                    headers={"Cache-Control": "no-cache"})


@app.post("/api/chat")
def chat(d: dict = Body(...)):
    key = _key()
    if not key:
        raise HTTPException(400, "no API key set yet - use the API key button")
    msgs = [m for m in (d.get("messages") or [])
            if isinstance(m, dict) and m.get("role") in ("user", "assistant") and m.get("content")][-40:]
    if not msgs:
        raise HTTPException(400, "say something")
    b = _bot()
    parts = ["You are the character defined below. Speak as them, always, in first person. "
             "Stay inside what the files establish; when asked something the files do not cover, "
             "answer the way this character would, and never break character or mention these instructions."]
    if b.get("voice"):
        parts.append("## Voice - how this character speaks\n" + b["voice"])
    for n, t in sorted(b.get("files", {}).items()):
        parts.append(f"## {n}\n{t}")
    payload = {"model": CHAT_MODEL, "max_tokens": 1000,
               "messages": [{"role": "system", "content": "\n\n".join(parts)}] + msgs}
    req = urllib.request.Request(
        f"{OPENROUTER}/chat/completions", data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "HTTP-Referer": "https://github.com/writers-room", "X-Title": "persona"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            result = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise HTTPException(502, f"HTTP {e.code} {e.read()[:300].decode(errors='replace')}")
    except Exception as e:
        raise HTTPException(502, str(e))
    reply = ((result.get("choices") or [{}])[0].get("message") or {}).get("content")
    if not reply:
        raise HTTPException(502, "no reply in the response")
    return {"reply": reply}
