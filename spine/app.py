# Spine: the story in seven points, forged at speed. Forge's twin - same shared
# roster with auto-versions in a bucket, same AI ideas through the shared
# OpenRouter key - but the spine is the Seven-Point Story Structure.
import json
import os
import re
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import HTMLResponse

BUCKET = os.getenv("BUCKET", "evoke-prosperity-spine")
OPENROUTER = "https://openrouter.ai/api/v1"
CHAT_MODEL = os.getenv("CHAT_MODEL", "openai/gpt-5.6-luna")
FIELDS = ["world", "change", "pressure", "discovery", "breaks", "choice", "newworld"]
LABELS = {"world": "the starting world - who the hero is and what is wrong or missing",
          "change": "something changes - what forces them into the story",
          "pressure": "pressure builds - what makes this much harder than expected",
          "discovery": "the discovery - what they learn that changes their understanding",
          "breaks": "everything breaks - the moment it looks like they have lost",
          "choice": "the choice - what the hero decides to do differently",
          "newworld": "the new world - what happens because of that choice"}

app = FastAPI()
INDEX = (Path(__file__).parent / "index.html").read_text()
_bucket = None


def bucket():
    global _bucket
    if _bucket is None:
        from google.cloud import storage
        _bucket = storage.Client().bucket(BUCKET)
    return _bucket


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
    return {"configured": bool(_key())}


@app.post("/api/key")
def set_key(d: dict = Body(...)):
    k = (d.get("key") or "").strip()
    if not k:
        raise HTTPException(400, "paste an OpenRouter key")
    bucket().blob("settings.json").upload_from_string(json.dumps({"key": k}))
    return {"ok": True}


@app.post("/api/suggest")
def suggest(d: dict = Body(...)):
    key = _key()
    if not key:
        raise HTTPException(400, "no API key set yet - use the API key button")
    field = d.get("field")
    if field not in FIELDS:
        raise HTTPException(400, "unknown field")
    a = d.get("answers") or {}
    have = "\n".join(f"- {LABELS[f]}: {str(a.get(f)).strip()}" for f in FIELDS
                     if f != field and str(a.get(f) or "").strip()) or "(nothing yet - a blank page)"
    payload = {"model": CHAT_MODEL, "max_tokens": 320, "temperature": 0.9,
               "messages": [
                   {"role": "system", "content":
                    "You help a writers' room break a story at speed on the seven-point structure. "
                    "Given the points locked so far, propose exactly 3 sharply different options for "
                    "the one story point asked for. Each option is a single concise line, at most 15 "
                    "words, concrete and dramatic - no explanation, no numbering, no quotes. Each must "
                    "fit the locked points and contradict none of them. Reply with ONLY a JSON array "
                    "of 3 strings."},
                   {"role": "user", "content":
                    f"The story so far:\n{have}\n\nSuggest 3 options for {LABELS[field]}."}]}
    req = urllib.request.Request(
        f"{OPENROUTER}/chat/completions", data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "HTTP-Referer": "https://github.com/writers-room", "X-Title": "spine"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            result = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise HTTPException(502, f"HTTP {e.code} {e.read()[:300].decode(errors='replace')}")
    except Exception as e:
        raise HTTPException(502, str(e))
    text = ((result.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
    try:
        m = re.search(r"\[.*\]", text, re.S)
        ideas = [str(x).strip() for x in json.loads(m.group(0))][:3]
    except Exception:
        ideas = [re.sub(r"^[\s\d.\-*•\"']+|[\"']+$", "", ln).strip()
                 for ln in text.splitlines() if ln.strip()][:3]
    ideas = [i for i in ideas if i]
    if not ideas:
        raise HTTPException(502, "no usable suggestions in the reply")
    return {"ideas": ideas}


@app.get("/api/stories")
def stories():
    """The rack: one row per story (lineage), all its versions newest first."""
    groups = {}
    try:
        for b in bucket().list_blobs(prefix="story/"):
            sid = b.name.split("/", 1)[1]
            m = b.metadata or {}
            line = m.get("line", sid)
            groups.setdefault(line, []).append(
                {"id": sid, "name": m.get("name", "?"), "done": int(m.get("done", 0))})
    except Exception as e:
        raise HTTPException(502, f"could not list stories: {e}")
    out = []
    for line, vs in groups.items():
        vs.sort(key=lambda v: v["id"], reverse=True)
        out.append({"line": line, "name": vs[0]["name"], "done": vs[0]["done"],
                    "versions": [v["id"] for v in vs]})
    out.sort(key=lambda g: g["versions"][0], reverse=True)
    return out[:200]


@app.post("/api/story")
def save(d: dict = Body(...)):
    """Every save is a new immutable version. Same `line` = same story."""
    a = d.get("answers") or {}
    answers = {f: str(a.get(f, ""))[:2000] for f in FIELDS}
    if not answers["world"].strip():
        raise HTTPException(400, "start with the starting world")
    line = str(d.get("line") or "").strip()
    if not re.fullmatch(r"[\w-]{1,80}", line or "-"):
        line = ""
    sid = f"{int(time.time() * 1000)}-{uuid.uuid4().hex[:6]}"
    line = line or sid
    b = bucket().blob(f"story/{sid}")
    b.metadata = {"name": answers["world"][:60], "line": line,
                  "done": str(sum(1 for f in FIELDS if answers[f].strip()))}
    b.upload_from_string(json.dumps({"line": line, "answers": answers}),
                         content_type="application/json")
    return {"id": sid, "line": line}


@app.get("/api/story/{sid}")
def load(sid: str):
    if not re.fullmatch(r"[\w-]+", sid):
        raise HTTPException(400, "bad id")
    try:
        doc = json.loads(bucket().blob(f"story/{sid}").download_as_text())
    except Exception:
        raise HTTPException(404, "no such story")
    if "answers" not in doc:
        doc = {"line": sid, "answers": doc}
    return doc
