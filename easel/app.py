# Easel's small back half: serve the page, hold the one shared OpenRouter key
# (pasted once, kept in the bucket), draw images with it, and keep every image
# in the bucket so the gallery is everyone's.
import base64
import json
import os
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response

BUCKET = os.getenv("BUCKET", "evoke-prosperity-easel")
OPENROUTER = "https://openrouter.ai/api/v1"
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


@app.post("/api/generate")
def generate(d: dict = Body(...)):
    key = _key()
    if not key:
        raise HTTPException(400, "no API key set yet - use the API key button")
    prompt = (d.get("prompt") or "").strip()
    if not prompt:
        raise HTTPException(400, "empty prompt")
    payload = {"model": d.get("model"), "prompt": prompt}
    refs = [r for r in (d.get("refs") or []) if isinstance(r, str) and r.startswith("data:")][:3]
    if refs:
        payload["input_references"] = [{"type": "image_url", "image_url": {"url": r}} for r in refs]
    req = urllib.request.Request(
        f"{OPENROUTER}/images", data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "HTTP-Referer": "https://github.com/writers-room", "X-Title": "easel"})
    try:
        with urllib.request.urlopen(req, timeout=280) as r:
            result = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise HTTPException(502, f"HTTP {e.code} {e.read()[:300].decode(errors='replace')}")
    except Exception as e:
        raise HTTPException(502, str(e))
    data = (result.get("data") or [{}])[0]
    if not data.get("b64_json"):
        raise HTTPException(502, "no image in the reply")
    return {"image": f"data:{data.get('media_type') or 'image/png'};base64,{data['b64_json']}"}


@app.post("/api/save")
def save(d: dict = Body(...)):
    head, _, b64 = (d.get("image") or "").partition(",")
    if not (head.startswith("data:") and b64):
        raise HTTPException(400, "expected a data: URL")
    mt = head[5:].split(";")[0] or "image/png"
    ext = {"image/jpeg": "jpg", "image/webp": "webp"}.get(mt, "png")
    name = f"img/{int(time.time() * 1000)}-{uuid.uuid4().hex[:6]}.{ext}"
    try:
        b = bucket().blob(name)
        b.metadata = {"model": (d.get("model") or "")[:120], "prompt": (d.get("prompt") or "")[:800]}
        b.upload_from_string(base64.b64decode(b64), content_type=mt)
    except Exception as e:
        raise HTTPException(502, f"could not save to the gallery: {e}")
    return {"id": name.split("/", 1)[1]}


@app.get("/api/gallery")
def gallery():
    try:
        blobs = list(bucket().list_blobs(prefix="img/"))
    except Exception as e:
        raise HTTPException(502, f"could not read the gallery: {e}")
    blobs.sort(key=lambda b: b.name, reverse=True)      # names start with a ms timestamp
    return [{"id": b.name.split("/", 1)[1],
             "model": (b.metadata or {}).get("model", ""),
             "prompt": (b.metadata or {}).get("prompt", "")} for b in blobs[:400]]


@app.get("/api/img/{img_id}")
def img(img_id: str):
    if "/" in img_id or ".." in img_id:
        raise HTTPException(400, "bad id")
    b = bucket().blob(f"img/{img_id}")
    try:
        data = b.download_as_bytes()
    except Exception:
        raise HTTPException(404, "no such image")
    return Response(data, media_type=b.content_type or "image/png",
                    headers={"Cache-Control": "public, max-age=31536000, immutable"})
