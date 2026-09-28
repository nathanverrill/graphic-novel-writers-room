# Forge: rapid character creation on the hero's journey wheel. No LLM, no key -
# the page does the work; this back half only keeps the finished characters in
# a bucket so the whole team's roster accumulates.
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

OPENROUTER = "https://openrouter.ai/api/v1"
CHAT_MODEL = os.getenv("CHAT_MODEL", "openai/gpt-5.6-luna")
FIELDS = ["name", "why", "incentive", "motive", "weakness", "change", "ret"]
LABELS = {"name": "who they are", "why": "their why - the wound or debt that still shapes them",
          "incentive": "their incentive - what they want badly enough to act",
          "motive": "their motive - what really drives them underneath",
          "weakness": "their weakness - what fails them at the worst moment",
          "change": "the change - what they must become to get through",
          "ret": "the return - what they bring back"}

app = FastAPI()
INDEX = (Path(__file__).parent / "index.html").read_text()
from store import bucket  # noqa: E402 - GCS when BUCKET is set, ./data files when not


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
                     if f != field and str(a.get(f) or "").strip()) or "(nothing yet - they are starting fresh)"
    payload = {"model": CHAT_MODEL, "max_tokens": 300, "temperature": 0.9,
               "messages": [
                   {"role": "system", "content":
                    "You help a writer forge a graphic-novel character at speed. Given what they have "
                    "so far, propose exactly 3 sharply different options for the one field asked for. "
                    "Each option is a single concise line, at most 12 words, concrete and specific - "
                    "no explanation, no numbering, no quotes. They must fit what is already established "
                    "and contradict none of it. Reply with ONLY a JSON array of 3 strings."},
                   {"role": "user", "content":
                    f"The character so far:\n{have}\n\nSuggest 3 options for {LABELS[field]}."}]}
    req = urllib.request.Request(
        f"{OPENROUTER}/chat/completions", data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "HTTP-Referer": "https://github.com/writers-room", "X-Title": "forge"})
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


@app.post("/api/polish")
def polish(d: dict = Body(...)):
    key = _key()
    if not key:
        raise HTTPException(400, "no API key set yet - use the API key button")
    draft_text = str(d.get("conclusion") or "").strip()
    if not draft_text:
        raise HTTPException(400, "nothing to improve yet")
    a = d.get("answers") or {}
    have = "\n".join(f"- {LABELS[f]}: {str(a.get(f)).strip()}" for f in FIELDS
                     if str(a.get(f) or "").strip()) or "(none)"
    payload = {"model": CHAT_MODEL, "max_tokens": 400, "temperature": 0.85,
               "messages": [
                   {"role": "system", "content":
                    "You polish the one-breath summary of a graphic-novel character. Rewrite the "
                    "draft into one tight, vivid paragraph of at most 90 words that keeps every "
                    "established fact and name, sharpens the prose, and lands on a hook. No "
                    "preamble, no quotes, no bullets - reply with only the paragraph."},
                   {"role": "user", "content":
                    f"The established facts:\n{have}\n\nThe draft:\n{draft_text}\n\nRewrite it."}]}
    req = urllib.request.Request(
        f"{OPENROUTER}/chat/completions", data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "HTTP-Referer": "https://github.com/writers-room", "X-Title": "forge"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            result = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise HTTPException(502, f"HTTP {e.code} {e.read()[:300].decode(errors='replace')}")
    except Exception as e:
        raise HTTPException(502, str(e))
    text = (((result.get("choices") or [{}])[0].get("message") or {}).get("content") or "").strip().strip('"')
    if not text:
        raise HTTPException(502, "no rewrite in the reply")
    return {"text": text}


@app.get("/api/characters")
def characters():
    """The roster: one row per character (lineage), all its versions newest first."""
    groups = {}
    try:
        for b in bucket().list_blobs(prefix="char/"):
            cid = b.name.split("/", 1)[1]
            m = b.metadata or {}
            line = m.get("line", cid)
            groups.setdefault(line, []).append(
                {"id": cid, "name": m.get("name", "?"), "done": int(m.get("done", 0))})
    except Exception as e:
        raise HTTPException(502, f"could not list characters: {e}")
    out = []
    for line, vs in groups.items():
        vs.sort(key=lambda v: v["id"], reverse=True)
        out.append({"line": line, "name": vs[0]["name"], "done": vs[0]["done"],
                    "versions": [v["id"] for v in vs]})
    out.sort(key=lambda g: g["versions"][0], reverse=True)
    return out[:200]


@app.post("/api/character")
def save(d: dict = Body(...)):
    """Every save is a new immutable version. Same `line` = same character."""
    a = d.get("answers") or {}
    answers = {f: str(a.get(f, ""))[:2000] for f in FIELDS}
    if not answers["name"].strip():
        raise HTTPException(400, "give them a name first")
    line = str(d.get("line") or "").strip()
    if not re.fullmatch(r"[\w-]{1,80}", line or "-"):
        line = ""
    cid = f"{int(time.time() * 1000)}-{uuid.uuid4().hex[:6]}"
    line = line or cid
    b = bucket().blob(f"char/{cid}")
    b.metadata = {"name": answers["name"][:80], "line": line,
                  "done": str(sum(1 for f in FIELDS if answers[f].strip()))}
    b.upload_from_string(json.dumps({"line": line, "answers": answers,
                                     "conclusion": str(d.get("conclusion") or "")[:4000]}),
                         content_type="application/json")
    return {"id": cid, "line": line}


@app.get("/api/character/{cid}")
def load(cid: str):
    if not re.fullmatch(r"[\w-]+", cid):
        raise HTTPException(400, "bad id")
    try:
        doc = json.loads(bucket().blob(f"char/{cid}").download_as_text())
    except Exception:
        raise HTTPException(404, "no such character")
    if "answers" not in doc:                     # a save from before versioning
        doc = {"line": cid, "answers": doc}
    doc.setdefault("conclusion", "")
    return doc
