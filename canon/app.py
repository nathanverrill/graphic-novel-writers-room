# Canon: the story and the research side by side, and the checks that make it
# canon. Two shelves of .md files in one shared bucket; a check run reads them
# all and marks each canon rule pass / thin / fail, with receipts. Every run is
# kept, so the room can watch the canon converge.
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import HTMLResponse

OPENROUTER = "https://openrouter.ai/api/v1"
CHAT_MODEL = os.getenv("CHAT_MODEL", "openai/gpt-5.6-luna")
MAX_FILE = 512 * 1024
CATS = ("story", "research")
CHECKS = [
    ("year", "Set in 2046"),
    ("settings", "Antarctica, the Himalayas, and Colorado are all present"),
    ("wtv", "A waste-to-value organization in Antarctica aids conservation in Colorado"),
    ("tj", "TJ the robot dog is in the cast"),
    ("messages", "Secret messages are being sent from Antarctica"),
    ("hardsf", "Hard sci-fi holds: the 80/15/5 mix, inventions with rules, no cheats"),
    ("agree", "Story and research agree: claims backed or licensed, no contradictions"),
]

app = FastAPI()
INDEX = (Path(__file__).parent / "index.html").read_text()
from store import bucket  # noqa: E402 - GCS when BUCKET is set, ./data files when not


def _json(name, default):
    try:
        return json.loads(bucket().blob(name).download_as_text())
    except Exception:
        return default


def _canon():
    c = _json("canon.json", {})
    return {"story": c.get("story", {}), "research": c.get("research", {})}


def _save_canon(c):
    bucket().blob("canon.json").upload_from_string(json.dumps(c))


def _key():
    return _json("settings.json", {}).get("key", "")


def _name_ok(name):
    return bool(re.fullmatch(r"[\w][\w .()-]{0,80}\.md", name))


@app.get("/")
def index():
    return HTMLResponse(INDEX)


@app.get("/api/canon")
def canon():
    c = _canon()
    runs = sorted(_json("runs.json", []), key=lambda r: r["ts"], reverse=True)
    return {"configured": bool(_key()),
            "story": [{"name": n, "chars": len(t)} for n, t in sorted(c["story"].items())],
            "research": [{"name": n, "chars": len(t)} for n, t in sorted(c["research"].items())],
            "checks": [{"id": i, "text": t} for i, t in CHECKS],
            "runs": runs[:30]}


@app.post("/api/key")
def set_key(d: dict = Body(...)):
    k = (d.get("key") or "").strip()
    if not k:
        raise HTTPException(400, "paste an OpenRouter key")
    bucket().blob("settings.json").upload_from_string(json.dumps({"key": k}))
    return {"ok": True}


@app.post("/api/file")
def add_file(d: dict = Body(...)):
    cat = d.get("cat")
    if cat not in CATS:
        raise HTTPException(400, "cat must be story or research")
    name, text = (d.get("name") or "").strip(), d.get("text") or ""
    if not name.endswith(".md"):
        name += ".md"
    if not _name_ok(name):
        raise HTTPException(400, "give the file a plain name ending in .md")
    if len(text) > MAX_FILE:
        raise HTTPException(400, f"{name}: over {MAX_FILE // 1024}KB")
    c = _canon()
    c[cat][name] = text
    _save_canon(c)
    return {"ok": True, "name": name}


@app.get("/api/file/{cat}/{name}")
def get_file(cat: str, name: str):
    c = _canon()
    if cat not in CATS or name not in c[cat]:
        raise HTTPException(404, "no such file")
    return {"cat": cat, "name": name, "text": c[cat][name]}


@app.delete("/api/file/{cat}/{name}")
def del_file(cat: str, name: str):
    c = _canon()
    if cat in CATS and name in c[cat]:
        del c[cat][name]
        _save_canon(c)
    return {"ok": True}


@app.post("/api/check")
def check():
    key = _key()
    if not key:
        raise HTTPException(400, "no API key set yet - use the API key button")
    c = _canon()
    if not c["story"]:
        raise HTTPException(400, "add at least one story file first")
    parts = []
    for cat in CATS:
        parts.append(f"\n==== {cat.upper()} FILES ====")
        if not c[cat]:
            parts.append("(none)")
        for n, t in sorted(c[cat].items()):
            parts.append(f"\n## {n}\n{t[:60000]}")
    material = "\n".join(parts)[:400000]
    rules = "\n".join(f"- id \"{i}\": {t}" for i, t in CHECKS)
    payload = {"model": CHAT_MODEL, "max_tokens": 900, "temperature": 0.2,
               "messages": [
                   {"role": "system", "content":
                    "You are the continuity editor of a writers' room, checking whether the canon "
                    "holds. Judge ONLY from the files given. For each check: verdict \"pass\" when "
                    "the files clearly establish it, \"thin\" when it is gestured at but not "
                    "established, \"fail\" when it is missing or contradicted. The note is at most "
                    "20 words: the evidence (name the file) or exactly what is missing or in "
                    "conflict. Reply with ONLY a JSON array of objects "
                    "{\"id\": ..., \"verdict\": ..., \"note\": ...}, one per check, in order."},
                   {"role": "user", "content":
                    f"THE CHECKS:\n{rules}\n\nTHE FILES:{material}"}]}
    req = urllib.request.Request(
        f"{OPENROUTER}/chat/completions", data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "HTTP-Referer": "https://github.com/writers-room", "X-Title": "canon"})
    try:
        with urllib.request.urlopen(req, timeout=280) as r:
            result = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise HTTPException(502, f"HTTP {e.code} {e.read()[:300].decode(errors='replace')}")
    except Exception as e:
        raise HTTPException(502, str(e))
    text = ((result.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
    m = re.search(r"\[.*\]", text, re.S)
    if not m:
        raise HTTPException(502, "no verdicts in the reply")
    try:
        raw = json.loads(m.group(0))
    except Exception:
        raise HTTPException(502, "unparseable verdicts in the reply")
    by_id = {str(r.get("id")): r for r in raw if isinstance(r, dict)}
    results = []
    for i, t in CHECKS:
        r = by_id.get(i, {})
        v = r.get("verdict") if r.get("verdict") in ("pass", "thin", "fail") else "fail"
        results.append({"id": i, "text": t, "verdict": v, "note": str(r.get("note", ""))[:200]})
    run = {"ts": int(time.time()),
           "files": sorted(c["story"]) + sorted(c["research"]),
           "passes": sum(1 for r in results if r["verdict"] == "pass"),
           "results": results}
    runs = _json("runs.json", [])
    runs.append(run)
    bucket().blob("runs.json").upload_from_string(json.dumps(runs[-100:]))
    return run
