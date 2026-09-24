import base64
import dataclasses
import io
import json
import mimetypes
import re
import threading
import time
import zipfile
from contextlib import asynccontextmanager
from pathlib import Path

import urllib.error
import urllib.request

import anyio
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import intake, keys, lettering, llm, magic, mcp, notes, objectstore, openitems, phases, projects, prompts, review, room, rules, search, thumbnails, usage
from .config import AGENTS_DIR, AgentConfig, env
from .agents import IMAGE_TYPES, SHARED, assets, get_role, load_roles, load_tools

room_mcp = mcp.build()          # the same tools the agents call, for clients outside the room


def index_in_background(slug=None):
    """Keep the search index current without making anyone wait for it."""
    def work():
        try:
            search.index(slug)
        except Exception as e:      # search is optional; the room works without it
            print(f"search index skipped: {type(e).__name__}: {str(e)[:200]}")
    threading.Thread(target=work, daemon=True).start()


@asynccontextmanager
async def lifespan(_app):
    objectstore.start()      # no-op unless S3_ENDPOINT is set
    for slug in projects.list_projects():     # a campaign laid out the old way gets its two desks
        if projects.migrate(slug):
            print(f"{slug}: output/ is now production/, and preproduction/ holds intake's files", flush=True)
        for rid in projects.close_stale_rounds(slug):
            print(f"{slug}: round {rid} was running when the app last stopped; marked interrupted", flush=True)
        if magic.close_stale(slug):
            print(f"{slug}: production was running when the app last stopped; marked failed, resumable", flush=True)
    index_in_background()
    threading.Thread(target=search.watch, args=(0.5, lambda msg: print(f"search: {msg}")),
                     daemon=True).start()   # a file changes, its passages are reindexed
    async with room_mcp.session_manager.run():
        yield
    objectstore.shutdown()


app = FastAPI(title="Graphic Novel Writers' Room", lifespan=lifespan)
STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")
app.mount("/mcp", room_mcp.streamable_http_app(streamable_http_path="/"))   # POST http://host/mcp


def not_found(fn, *args, **kw):
    try:
        return fn(*args, **kw)
    except (FileNotFoundError, KeyError) as e:
        raise HTTPException(404, f"not found: {e}")
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/")
def landing():
    """Three doors: pre-production, production, sheets."""
    return FileResponse(STATIC / "landing.html")


@app.get("/quick")
def home():
    """One button, on a phone: start the book, watch it, see the lettered pages."""
    return FileResponse(STATIC / "home.html")


# ---- sheets: its own container, reached through this port --------------------------------

SHEETS_URL = (env("SHEETS_URL") or "http://sheets:8001").rstrip("/")


@app.api_route("/sheets", methods=["GET"])
@app.api_route("/sheets/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def sheets_proxy(request: Request, path: str = ""):
    """Hand the request to the sheets container and hand its answer back, as is. The sheets
    page is told its prefix (PREFIX=/sheets in docker-compose.yml), so its links come back
    pointing here."""
    url = f"{SHEETS_URL}/{path}" + (f"?{request.url.query}" if request.url.query else "")
    body = await request.body()
    headers = {k: v for k, v in request.headers.items() if k.lower() in ("content-type", "accept")}
    req = urllib.request.Request(url, data=body if body else None, headers=headers, method=request.method)

    def call():
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.status, dict(r.headers), r.read()
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers), e.read()
        except (urllib.error.URLError, OSError) as e:
            return 502, {"Content-Type": "text/plain"}, f"sheets is not running: {e}".encode()
    status, hdrs, data = await anyio.to_thread.run_sync(call)
    keep = {k: v for k, v in hdrs.items() if k.lower() in ("content-type", "content-disposition", "cache-control")}
    return Response(content=data, status_code=status, headers=keep)


@app.get("/preproduction")
def preproduction():
    """The pre-production desk: the material, the three working documents, and the gate.

    Intake stops for the showrunner between pass 3 and pass 4, and this is where that waiting
    happens - the open items, their options and where each one came from, what you answer,
    defer or say about the book. The one-button screen and the full room are untouched."""
    return FileResponse(STATIC / "preproduction.html")


@app.get("/production")
def production():
    """The production room: what will happen, one button, the log, then the finished work.

    The room takes every gate itself (app/magic.py) and stops twice: at page 1, and at the
    end. The showrunner's part is notes, and stepping back if a note reaches further."""
    return FileResponse(STATIC / "production.html")


@app.get("/room")
def index():
    """The whole room: every writer, every file, every round."""
    return FileResponse(STATIC / "index.html")


@app.get("/api/config")
def config():
    """The .env defaults, as a role with no agent.json would see them."""
    d = AgentConfig().resolve().public()
    d["storage"] = objectstore.describe()
    return d


# ---- agents -----------------------------------------------------------------

@app.get("/api/agents")
def roles():
    return {"roles": [r.to_dict() for r in load_roles()], "shared": assets(SHARED),
            "phases": phases.load(), "tools": sorted(load_tools())}


def _role_folder(role_id):
    if role_id != SHARED and role_id not in {r.shares for r in load_roles()}:
        not_found(get_role, role_id)
    return AGENTS_DIR / role_id


@app.get("/api/agents/{role_id}/guides/{name}", response_class=PlainTextResponse)
def role_guide(role_id: str, name: str):
    if name not in assets(role_id)["guides"]:
        raise HTTPException(404)
    return (_role_folder(role_id) / name).read_text()


@app.get("/api/agents/{role_id}/images/{name}")
def role_image(role_id: str, name: str):
    if name not in assets(role_id)["images"]:
        raise HTTPException(404)
    path = _role_folder(role_id) / "images" / name
    return FileResponse(path, media_type=IMAGE_TYPES.get(path.suffix.lower()) or mimetypes.guess_type(path)[0])


class SettingsChange(BaseModel):
    changes: dict


class ApplyProvider(BaseModel):
    roles: list[str]


@app.get("/api/keys")
def saved_keys():
    """Providers with a saved key, and which agents use each (never the keys)."""
    roles = load_roles()
    used = {}
    for r in roles:
        try:
            used.setdefault(r.config().base_url, []).append(r.id)
        except ValueError:
            pass
    return {"providers": [{"base_url": u, "used_by": used.get(u, [])} for u in keys.providers()]}


@app.put("/api/agents/{role_id}/settings")
def save_role_settings(role_id: str, body: SettingsChange):
    role = not_found(get_role, role_id)
    return not_found(role.save_settings, body.changes)


@app.get("/api/agents/{role_id}/models")
def role_models(role_id: str, image: bool = False):
    role = not_found(get_role, role_id)
    cfg = not_found(role.config)
    if image:
        cfg = dataclasses.replace(cfg, base_url=cfg.image_base_url, api_key=cfg.image_api_key)
    try:
        return {"models": llm.list_models(cfg), "base_url": cfg.base_url}
    except llm.LLMError as e:
        raise HTTPException(400, f"couldn't list models from {cfg.base_url}: {str(e)[:300]}")


@app.post("/api/agents/{role_id}/test")
def test_role(role_id: str):
    """One tiny chat request with the role's settings (not logged to any project)."""
    role = not_found(get_role, role_id)
    cfg = dataclasses.replace(not_found(role.config), max_tokens=64, extra={})
    start = time.time()
    try:
        reply = llm.chat(cfg, [{"role": "user", "content": "Reply with the single word OK."}])
    except llm.LLMError as e:
        return {"ok": False, "error": str(e)[:400], "base_url": cfg.base_url, "model": cfg.model}
    return {"ok": True, "reply": llm.text_of(reply)[:200], "ms": round((time.time() - start) * 1000),
            "base_url": cfg.base_url, "model": cfg.model}


@app.post("/api/agents/{role_id}/apply-provider")
def apply_provider(role_id: str, body: ApplyProvider):
    """Copy this role's provider, key and model to other roles."""
    source = not_found(get_role, role_id)
    raw = source.raw_config()
    changes = {k: raw.get(k) for k in ("base_url", "api_key_env", "model")}   # keys are per provider already
    done = []
    for rid in body.roles:
        if rid == role_id:
            continue
        not_found(get_role, rid).save_settings(changes)
        done.append(rid)
    return {"updated": done}


# ---- projects --------------------------------------------------------------

class NewProject(BaseModel):
    title: str
    pitch: str = ""
    pages: int | None = None
    draft: str | None = None


class ArtifactBody(BaseModel):
    content: str


class RunRequest(BaseModel):
    roles: list[str]
    note: str | None = None


@app.get("/api/projects")
def list_projects():
    return {"projects": projects.list_projects()}


@app.post("/api/projects")
def create_project(body: NewProject):
    try:
        if body.pages is not None and not 1 <= body.pages <= 200:
            raise HTTPException(400, "pages must be between 1 and 200")
        return {"slug": projects.create_project(body.title, body.pitch, body.pages, body.draft)}
    except FileExistsError:
        raise HTTPException(409, "a project with that name already exists")


def _desk(desk):
    if desk not in projects.DESKS:
        raise HTTPException(400, f"desk must be one of {', '.join(projects.DESKS)}")
    return desk


@app.get("/api/projects/{slug}")
def get_project(slug: str, desk: str = projects.PROD):
    """The project as one desk sees it: `desk=preproduction` for intake's files and rounds."""
    artifacts = not_found(projects.list_artifacts, slug, desk=_desk(desk))
    run = room.active_run(slug)
    return {"slug": slug, "desk": desk, "artifacts": artifacts, "images": projects.list_images(slug),
            "references": projects.list_references(slug),
            "versions": projects.list_versions(slug, desk),
            "active_run": run.id if run else None,
            "active_version": run.version.id if run else None,
            "settings": review.settings(slug),
            "magic": magic.state(slug),
            **phases.state(slug),
            "library": projects.library(slug),
            "output": f"production/{slug}"}


@app.post("/api/projects/{slug}/export")
def export_project(slug: str):
    pages, book = prompts.build(slug)
    return {"folder": not_found(projects.export_output, slug, pages, book, "working-copy",
                                review.text_layers(slug))}


@app.get("/api/projects/{slug}/images/{name}")
def get_image(slug: str, name: str):
    return FileResponse(not_found(projects.image_path, slug, name))


@app.get("/api/projects/{slug}/artifacts/{name}", response_class=PlainTextResponse)
def get_artifact(slug: str, name: str, desk: str = projects.PROD):
    content = not_found(projects.read_artifact, slug, name, desk=_desk(desk))
    if content is None:
        raise HTTPException(404)
    return content


@app.put("/api/projects/{slug}/artifacts/{name}")
def put_artifact(slug: str, name: str, body: ArtifactBody, desk: str = projects.PROD):
    not_found(projects.write_artifact, slug, name, body.content, desk=_desk(desk))
    if name == "layouts.md":  # hand edits to layouts redraw the preview too
        md, _, feedback = thumbnails.render_layouts(body.content, projects.read_artifact(slug, "thumbnails.md"))
        projects.write_artifact(slug, "thumbnails.md", md)
        return {"ok": True, "thumbnail_issues": feedback}
    return {"ok": True}


PREVIEW_FILES = {"layout": "thumbnails.md"}     # the page sketch, drawn in code from layouts.md


@app.get("/api/projects/{slug}/prompts")
def page_prompts(slug: str, version: str | None = None):
    """The room's deliverable: one image-model prompt per page. Live from the working copy,
    or as a round saved them."""
    if version is None:
        pages, book = not_found(prompts.build, slug)
    else:
        book = not_found(projects.read_artifact, slug, "page-prompts.md", version) or ""
        pre = projects.prefix(slug, version)
        folder = not_found(projects._folder, slug, version)
        pages = {int(p.name[len(pre) + 1:].split("-")[0]): p.read_text()
                 for p in folder.glob(f"{pre}p*-prompt.md")}
    return {"pages": pages, "book": book}


@app.get("/api/projects/{slug}/packet.zip")
def packet_zip(slug: str, version: str | None = None):
    """Everything to take to the image model, in one download: the book packet, one file per
    page, each page's print-scale sketch, and the lettering layers for later."""
    not_found(projects.project_dir, slug)
    pages, book = not_found(prompts.build, slug, version)
    if not pages:
        raise HTTPException(404, "no pages yet - run production first")
    sketches = prompts.context(slug, version).get("sketches") or {}
    letters = review.text_layers(slug, version)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{slug}/00-book.md", book)
        z.writestr(f"{slug}/00-read-me-first.md", prompts.book_packet(slug, version))
        for name in ("script.md", "layouts.md", "brief.md", "characters.md", "world.md"):   # the instructions behind the packets
            text = projects.read_artifact(slug, name, version)
            if text:
                z.writestr(f"{slug}/source/{name}", text)
        for n in sorted(pages):
            z.writestr(f"{slug}/pages/p{n:02d}.md", pages[n])
            if n in sketches:
                z.writestr(f"{slug}/sketches/p{n:02d}.txt", sketches[n])
            if n in letters:
                z.writestr(f"{slug}/letters/p{n:02d}.svg", letters[n])
    buf.seek(0)
    name = f"{slug}-packets{'-' + version if version else ''}.zip"
    return StreamingResponse(buf, media_type="application/zip",
                             headers={"Content-Disposition": f'attachment; filename="{name}"'})


class LetteredPage(BaseModel):
    data_url: str


@app.post("/api/projects/{slug}/lettering/{page}/lettered")
def put_lettered_page(slug: str, page: int, body: LetteredPage):
    """The finished page: art with the lettering flattened onto it, as the browser drew it."""
    head, _, b64 = body.data_url.partition(",")
    if not b64 or "image/png" not in head:
        raise HTTPException(400, "expected a PNG data URL")
    path = not_found(projects.save_lettered_page, slug, page, base64.b64decode(b64))
    return {"lettered": path}


@app.get("/api/projects/{slug}/previews")
def previews(slug: str, version: str | None = None):
    """ASCII page previews from each method, keyed by method then page number."""
    out = {}
    for method, name in PREVIEW_FILES.items():
        md = not_found(projects.read_artifact, slug, name, version)
        out[method] = thumbnails.parse_thumbnails(md) if md else {}
    g = thumbnails.geometry()
    pages = sorted({p for m in out.values() for p in m})
    return {"methods": out, "pages": pages, "cols": g.cols, "rows": g.rows, "pt": g.pt}


class PreviewEdit(BaseModel):
    art: str
    invert: str | None = None


def _preview_file(slug, method):
    name = PREVIEW_FILES.get(method)
    if not name:
        raise HTTPException(404, f"no preview method {method!r}")
    md = not_found(projects.read_artifact, slug, name)
    if md is None:
        raise HTTPException(404, f"{name} doesn't exist yet")
    return name, md


FENCE = "`" * 3


@app.put("/api/projects/{slug}/previews/{method}/{page}")
def edit_preview(slug: str, method: str, page: int, body: PreviewEdit):
    """Save a hand-edited page. It is kept when previews are regenerated."""
    name, md = _preview_file(slug, method)
    grid, _ = thumbnails.text_to_grid(body.art.replace(FENCE, "'" * 3), thumbnails.geometry())
    art = "\n".join("".join(r) for r in grid)
    invert = None if body.invert is None else thumbnails.mask_text(thumbnails.text_to_mask(body.invert, thumbnails.geometry()))
    new = not_found(thumbnails.replace_page, md, page, art, True, invert)
    projects.write_artifact(slug, name, new)
    return {"ok": True}


@app.delete("/api/projects/{slug}/previews/{method}/{page}")
def revert_preview(slug: str, method: str, page: int):
    """Drop the hand-edited mark. The layout render redraws at once; the others on their next run."""
    name, md = _preview_file(slug, method)
    new = not_found(thumbnails.replace_page, md, page, None, False)
    if method == "layout":
        layouts = projects.read_artifact(slug, "layouts.md") or ""
        new, _, _ = thumbnails.render_layouts(layouts, new)
    projects.write_artifact(slug, name, new)
    return {"ok": True}


@app.get("/api/projects/{slug}/library/{name:path}", response_class=PlainTextResponse)
def get_reference(slug: str, name: str):
    content = not_found(projects.read_reference, slug, name)
    if content is None:
        raise HTTPException(404)
    return content


# ---- versions --------------------------------------------------------------

@app.get("/api/projects/{slug}/versions/{version}")
def get_version(slug: str, version: str, desk: str = projects.PROD):
    meta = not_found(projects.version_meta, slug, version, _desk(desk))
    return {**meta, "artifacts": projects.list_artifacts(slug, version, desk),
            "image_files": projects.list_images(slug, version),
            "reference_files": projects.list_references(slug, version)}


@app.get("/api/projects/{slug}/versions/{version}/library/{name:path}", response_class=PlainTextResponse)
def get_version_reference(slug: str, version: str, name: str):
    content = not_found(projects.read_reference, slug, name, version)
    if content is None:
        raise HTTPException(404)
    return content


def _calls_dir(slug, version):
    return not_found(projects._folder, slug, version) / "calls"


@app.get("/api/projects/{slug}/versions/{version}/calls")
def list_calls(slug: str, version: str):
    path = not_found(projects.round_path, slug, version, "calls.jsonl")
    rows = [json.loads(l) for l in path.read_text().splitlines() if l] if path.exists() else []
    return {"calls": rows, "report": usage.report(rows)}


@app.get("/api/projects/{slug}/versions/{version}/calls/{name}")
def get_call(slug: str, version: str, name: str):
    if not re.fullmatch(r"[a-z0-9-]+-call-\d{4}-[a-z0-9-]+\.json", name):
        raise HTTPException(400)
    path = _calls_dir(slug, version) / name
    if not path.exists():
        raise HTTPException(404)
    return FileResponse(path, media_type="application/json")


@app.get("/api/projects/{slug}/versions/{version}/calls/blobs/{name}")
def get_call_blob(slug: str, version: str, name: str):
    if not re.fullmatch(r"[0-9a-f]{20}\.(png|jpg|webp|gif|bin)", name):
        raise HTTPException(400)
    path = _calls_dir(slug, version) / "blobs" / name
    if not path.exists():
        raise HTTPException(404)
    return FileResponse(path)



@app.get("/api/projects/{slug}/versions/{version}/artifacts/{name}", response_class=PlainTextResponse)
def get_version_artifact(slug: str, version: str, name: str, desk: str = projects.PROD):
    content = not_found(projects.read_artifact, slug, name, version, _desk(desk))
    if content is None:
        raise HTTPException(404)
    return content


@app.get("/api/projects/{slug}/versions/{version}/images/{name}")
def get_version_image(slug: str, version: str, name: str):
    return FileResponse(not_found(projects.image_path, slug, name, version))


@app.get("/api/projects/{slug}/versions/{version}/events")
def get_version_events(slug: str, version: str, desk: str = projects.PROD):
    return {"events": not_found(projects.version_events, slug, version, _desk(desk))}


@app.post("/api/projects/{slug}/versions/{version}/restore")
def restore_version(slug: str, version: str):
    if room.active_run(slug):
        raise HTTPException(409, "wait for the current run to finish")
    not_found(projects.restore_version, slug, version)
    return {"ok": True}


@app.get("/api/projects/{slug}/versions/{version}/files")
def list_round_files(slug: str, version: str):
    folder = not_found(projects._folder, slug, version)
    return {"files": sorted(p.name for p in folder.iterdir() if p.is_file())}


@app.get("/api/projects/{slug}/versions/{version}/files/{name}", response_class=PlainTextResponse)
def get_round_file(slug: str, version: str, name: str):
    pre = projects.prefix(slug, version)
    if not name.startswith(pre):
        raise HTTPException(404)
    content = not_found(projects.read_round_file, slug, version, name[len(pre):])
    if content is None:
        raise HTTPException(404)
    return content


@app.get("/api/projects/{slug}/pages/{page}")
def get_page_view(slug: str, page: int, version: str | None = None):
    """The page as the screen shows it: the panel map, and each panel's description and dialog."""
    spec = lettering.page_spec(slug, page, version)
    if not spec:
        raise HTTPException(404, f"no layout for page {page}")
    return {**prompts.page_view(spec), "kept": review.kept(slug).get(page)}


@app.post("/api/projects/{slug}/pages/{page}/keep")
def keep_page(slug: str, page: int):
    """Keep the page as it stands — the room leaves it alone from here, mid-round included."""
    try:
        return {"kept": not_found(review.keep_page, slug, page, "kept by the showrunner")["round"]}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.delete("/api/projects/{slug}/pages/{page}/keep")
def release_page(slug: str, page: int):
    not_found(review.release_page, slug, page)
    return {"kept": None}


# ---- lettering: the text layer over art drawn without text -----------------------

class LetteringEdit(BaseModel):
    changes: dict[str, dict]


class PageArt(BaseModel):
    data_url: str


def _lettering(slug, page, version=None):
    spec = lettering.page_spec(slug, page, version)
    if not spec:
        raise HTTPException(404, f"no layout for page {page}")
    ctx = prompts.context(slug, version)
    return {"page": page, "items": lettering.items(spec), "svg": lettering.svg(spec, ctx),
            "spots": list(lettering.ANCHORS),
            "art": projects.page_art(slug, page), "lettered": projects.lettered_page(slug, page), "mode": ctx.get("lettering", "layer"),
            "size": lettering.page_size()}


@app.get("/api/projects/{slug}/lettering/{page}")
def get_lettering(slug: str, page: int, version: str | None = None):
    return _lettering(slug, page, version)


@app.put("/api/projects/{slug}/lettering/{page}")
def put_lettering(slug: str, page: int, edit: LetteringEdit):
    try:
        lettering.set_items(slug, page, edit.changes)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return _lettering(slug, page)


@app.delete("/api/projects/{slug}/lettering/{page}/items/{index}")
def delete_lettering_item(slug: str, page: int, index: int):
    """Drop one balloon, caption or sound effect from the page."""
    try:
        lettering.delete_item(slug, page, index)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return _lettering(slug, page)


@app.post("/api/projects/{slug}/lettering/{page}/art")
def put_page_art(slug: str, page: int, art: PageArt):
    """The page's art with no lettering on it, as a data: URL from the file picker."""
    head, _, b64 = art.data_url.partition(",")
    if not b64 or "image/" not in head:
        raise HTTPException(400, "expected an image data URL")
    ext = head.split("image/")[1].split(";")[0].replace("jpeg", "jpg")
    if ext not in ("png", "jpg", "webp", "gif"):
        raise HTTPException(400, f"unsupported image type {ext!r}")
    path = projects.save_page_art(slug, page, base64.b64decode(b64), ext)
    return {"art": path}


# ---- standing rules: what the room must always or never do ---------------------

class NewRule(BaseModel):
    text: str
    kind: str = "always"


@app.get("/api/projects/{slug}/rules")
def get_rules(slug: str):
    return {"rules": not_found(rules.all, slug)}


@app.post("/api/projects/{slug}/rules")
def add_rule(slug: str, body: NewRule):
    try:
        return {"rules": rules.add(slug, body.text, body.kind)}
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.delete("/api/projects/{slug}/rules/{rule_id}")
def drop_rule(slug: str, rule_id: int):
    return {"rules": not_found(rules.drop, slug, rule_id)}


# ---- showrunner notes ----------------------------------------------------------

class Note(BaseModel):
    text: str
    page: int | None = None


@app.get("/api/projects/{slug}/notes")
def get_notes(slug: str):
    return {"pending": notes.pending(slug), "all": notes._all(slug)}


@app.post("/api/projects/{slug}/notes")
def add_note(slug: str, note: Note):
    try:
        return notes.add(slug, note.text, note.page)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.delete("/api/projects/{slug}/notes/{note_id}")
def drop_note(slug: str, note_id: int):
    notes.drop(slug, note_id)
    return {"ok": True}


@app.post("/api/projects/{slug}/notes/synthesize")
def synthesize_notes(slug: str):
    """One model call that turns the jotted notes into organized feedback."""
    try:
        return notes.synthesize(slug)
    except (ValueError, llm.LLMError) as e:
        raise HTTPException(400, str(e))


# ---- writing rounds and review -------------------------------------------------

class RoundSettings(BaseModel):
    pages: int | None = None
    chapter: int | None = None
    lettering: str | None = None   # "art" (the model letters it) or "layer" (we do)
    max_passes: int | None = None
    auto_rounds: int | None = None  # keep going without a review for this many more rounds
    execution_rounds: int | None = None   # production: rounds of pages before the book is taken as is
    references: list[str] | None = None   # library files to use; ["*"] = all
    use_references_during_synthesis: bool | None = None   # let intake's pass 1 read references/
    draft_mode: str | None = None   # "improve" or "edit": how production treats the showrunner's draft


class RoundRequest(BaseModel):
    note: str | None = None
    phase: str | None = None   # run this phase rather than the one the book is in (the desk: intake)
    mode: str | None = None    # intake only: "synthesis" or "revision"; default is chosen


class PageReview(BaseModel):
    kept: bool | None = None       # the page is done and locked; everything else is feedback
    comment: str | None = None
    art: str | None = None
    invert: str | None = None


class Submit(BaseModel):
    action: str
    comment: str | None = None


def _idle(slug):
    if room.active_run(slug):
        raise HTTPException(409, "the room is working — wait for the round to finish")


@app.put("/api/projects/{slug}/settings")
def update_settings(slug: str, body: RoundSettings):
    not_found(projects.project_dir, slug)
    if body.max_passes is not None and not 0 <= body.max_passes <= 10:
        raise HTTPException(400, "max_passes must be 0-10")
    if body.auto_rounds is not None and not 0 <= body.auto_rounds <= 20:
        raise HTTPException(400, "auto_rounds must be 0-20")
    if body.execution_rounds is not None and not 1 <= body.execution_rounds <= 10:
        raise HTTPException(400, "execution_rounds must be 1-10")
    if body.draft_mode not in (None, "improve", "edit"):
        raise HTTPException(400, "draft_mode must be improve or edit")
    if body.references not in (None, ["*"]):
        known = {f["name"] for f in projects.library(slug)}
        unknown = [r for r in body.references if r not in known]
        if unknown:
            raise HTTPException(400, f"not in the library: {', '.join(unknown)}")
    return review.save_settings(slug, **body.model_dump())


@app.post("/api/projects/{slug}/rounds")
def start_round(slug: str, body: RoundRequest):
    not_found(projects.project_dir, slug)
    if body.mode is not None and body.mode not in (intake.SYNTHESIS, intake.REVISION, "integration"):
        raise HTTPException(400, f"mode must be {intake.SYNTHESIS!r} or {intake.REVISION!r}")
    try:
        run = room.start_round(slug, (body.note or "").strip() or None, body.mode, body.phase)
    except RuntimeError as e:
        raise HTTPException(409, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"run_id": run.id, "version": run.version.id, "kind": run.plan["kind"]}


# ---- phases: where the book is, and the gate out of each one ----------------

class PhaseMove(BaseModel):
    action: str                    # "approve", "approve_preproduction", "pick" (with writer) or "go" (with phase)
    writer: str | None = None
    phase: str | None = None
    confirm: str | None = None     # approve_preproduction: the word typed to confirm


@app.post("/api/projects/{slug}/phase")
def move_phase(slug: str, body: PhaseMove):
    not_found(projects.project_dir, slug)
    _idle(slug)
    try:
        if body.action == "approve":
            return phases.approve(slug)
        if body.action == "approve_preproduction":
            return phases.approve_preproduction(slug, body.confirm)
        if body.action == "pick":
            return phases.pick(slug, body.writer)
        if body.action == "go":
            return phases.go_to(slug, body.phase)
    except ValueError as e:
        raise HTTPException(400, str(e))
    raise HTTPException(400, "action must be approve, approve_preproduction, pick or go")


# ---- open items: what intake could not settle, and your answers ---------------

class OpenItemAnswer(BaseModel):
    answer: str | None = None      # your answer; empty takes it back and leaves the item open
    feedback: str | None = None    # a note about this item that is not an answer to it
    defer: str | None = None       # leave it open on purpose; the text is why


class Feedback(BaseModel):
    feedback: str | None = None    # about the book, not about one item; empty clears it


@app.get("/api/projects/{slug}/open-items")
def open_items(slug: str):
    not_found(projects.project_dir, slug)
    return {**openitems.state(slug), "readiness": phases.readiness(slug)}


@app.post("/api/projects/{slug}/open-items/{n}")
def answer_open_item(slug: str, n: int, body: OpenItemAnswer):
    """Answer item n, leave a note about it, defer it — or any combination."""
    not_found(projects.project_dir, slug)
    try:
        state = openitems.state(slug)
        for field, value in (("feedback", body.feedback), ("defer", body.defer)):
            if value is not None:
                state = openitems.note_on(slug, n, field, value)
        if body.answer is not None:
            state = openitems.answer(slug, n, body.answer)
        return state
    except ValueError as e:
        raise HTTPException(404, str(e))


@app.post("/api/projects/{slug}/open-items-feedback")
def open_items_feedback(slug: str, body: Feedback):
    """The showrunner's general note about the book: a rule for the next integration."""
    not_found(projects.project_dir, slug)
    return openitems.set_feedback(slug, body.feedback)


@app.get("/api/projects/{slug}/review")
def review_state(slug: str):
    not_found(projects.project_dir, slug)
    st = review.state(slug)
    if room.active_run(slug):
        st["open"] = False
    return st


@app.put("/api/projects/{slug}/review/pages/{page}")
def review_page(slug: str, page: int, body: PageReview):
    _idle(slug)
    return not_found(review.save_page, slug, page, body.kept, body.comment, body.art, body.invert)


@app.put("/api/projects/{slug}/review/comment")
def review_comment(slug: str, body: Submit):
    not_found(review.save_comment, slug, body.comment or "")
    return {"ok": True}


@app.post("/api/projects/{slug}/review/submit")
def review_submit(slug: str, body: Submit):
    _idle(slug)
    rid = not_found(review.submit, slug, body.action, body.comment)
    out = {"round": rid}
    if body.action == "send":
        run = room.start_round(slug)
        out.update(run_id=run.id, version=run.version.id)
    return out


# ---- search: hybrid over everything the room can read -----------------------

@app.get("/api/search")
def search_room(q: str, scope: str | None = None, kind: str | None = None,
                mode: str = "hybrid", limit: int = 10):
    try:
        return {"hits": search.search(q, limit=min(limit, 50), scope=scope, kind=kind, mode=mode)}
    except Exception as e:
        raise HTTPException(503, f"search unavailable: {type(e).__name__}: {str(e)[:200]}")


@app.get("/api/search/health")
def search_health():
    return search.health()


@app.post("/api/search/index")
def search_index(project: str | None = None):
    try:
        return search.index(project)
    except Exception as e:
        raise HTTPException(503, f"indexing failed: {type(e).__name__}: {str(e)[:200]}")


# ---- costs -----------------------------------------------------------------

@app.get("/api/usage")
def usage_report(project: str | None = None, version: str | None = None):
    """Cost and tokens from logs/usage.jsonl, grouped by role, model and kind."""
    rows = usage.read_ledger(project, version)
    return {"report": usage.report(rows), "pricing_models": sorted(usage.pricing())}


# ---- runs ------------------------------------------------------------------

@app.post("/api/projects/{slug}/runs")
def start_run(slug: str, body: RunRequest):
    not_found(projects.project_dir, slug)
    try:
        run = room.start(slug, body.roles, (body.note or "").strip() or None)
    except RuntimeError as e:
        raise HTTPException(409, str(e))
    except KeyError as e:
        raise HTTPException(400, f"unknown role: {e}")
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"run_id": run.id, "version": run.version.id}


def _get_run(run_id):
    run = room.RUNS.get(run_id)
    if not run:
        raise HTTPException(404, "no such run")
    return run


# ---- production, run all the way ------------------------------------------------

class MagicStart(BaseModel):
    step: str = "development"    # where to (re-)enter the chain
    until: str = "layouts"       # where to stop: page1, layouts (the default) or final
    note: str | None = None      # carried into the first round


@app.get("/api/projects/{slug}/magic")
def magic_state(slug: str):
    not_found(projects.project_dir, slug)
    return {**magic.state(slug), "plan": magic.plan(slug), "pages": review.settings(slug)["pages"],
            "drafts": magic.drafts(slug)}


@app.post("/api/projects/{slug}/magic")
def magic_start(slug: str, body: MagicStart):
    not_found(projects.project_dir, slug)
    try:
        return magic.start(slug, body.step, (body.note or "").strip() or None, body.until)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except RuntimeError as e:
        raise HTTPException(409, str(e))


@app.post("/api/projects/{slug}/magic/stop")
def magic_stop(slug: str):
    not_found(projects.project_dir, slug)
    return magic.stop(slug)


@app.post("/api/runs/{run_id}/stop")
def stop_run(run_id: str):
    run = _get_run(run_id)
    run.stop_requested = True
    with run.cond:                 # a paused run is waiting: wake it so it can stop
        run.cond.notify_all()
    return {"ok": True}


@app.post("/api/runs/{run_id}/pause")
def pause_run(run_id: str):
    """Hold the round as soon as the agent at work finishes — not mid-task."""
    run = _get_run(run_id)
    run.pause_requested = True
    return {"ok": True, "paused": run.paused}


@app.post("/api/runs/{run_id}/resume")
def resume_run(run_id: str):
    """Carry on, with whatever settings and notes changed while it was held."""
    run = _get_run(run_id)
    run.pause_requested = False
    with run.cond:
        run.cond.notify_all()
    return {"ok": True}


@app.get("/api/runs/{run_id}/events")
def run_events(run_id: str, after: int = 0):
    run = _get_run(run_id)

    def stream():
        pos = after
        while True:
            events, done = run.wait(pos)
            for ev in events:
                yield f"data: {json.dumps(ev)}\n\n"
            pos += len(events)
            if done and pos >= len(run.events):
                yield "event: end\ndata: {}\n\n"
                return
            if not events:
                yield ": keepalive\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache"})
