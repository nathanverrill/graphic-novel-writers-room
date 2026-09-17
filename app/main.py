import dataclasses
import json
import mimetypes
import re
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import keys, llm, objectstore, projects, prompts, review, room, thumbnails, usage
from .config import ROLES_DIR, AgentConfig, settings
from .roles import IMAGE_TYPES, SHARED, assets, get_role, list_hats, load_roles

@asynccontextmanager
async def lifespan(_app):
    objectstore.start()      # no-op unless S3_ENDPOINT is set
    yield
    objectstore.shutdown()


app = FastAPI(title="Graphic Novel Writers' Room", lifespan=lifespan)
STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


def not_found(fn, *args):
    try:
        return fn(*args)
    except (FileNotFoundError, KeyError) as e:
        raise HTTPException(404, f"not found: {e}")
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/config")
def config():
    """The .env defaults, as a role with no agent.json would see them."""
    d = AgentConfig().resolve().public()
    d["figma_token_set"] = bool(settings.figma_token)
    d["storage"] = objectstore.describe()
    return d


# ---- roles -----------------------------------------------------------------

@app.get("/api/roles")
def roles():
    return {"roles": [r.to_dict() for r in load_roles()], "shared": assets(SHARED), "hats": list_hats()}


def _role_folder(role_id):
    if role_id != SHARED:
        not_found(get_role, role_id)
    return ROLES_DIR / role_id


@app.get("/api/roles/{role_id}/guides/{name}", response_class=PlainTextResponse)
def role_guide(role_id: str, name: str):
    if name not in assets(role_id)["guides"]:
        raise HTTPException(404)
    return (_role_folder(role_id) / name).read_text()


@app.get("/api/roles/{role_id}/images/{name}")
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


@app.put("/api/roles/{role_id}/settings")
def save_role_settings(role_id: str, body: SettingsChange):
    role = not_found(get_role, role_id)
    return not_found(role.save_settings, body.changes)


@app.get("/api/roles/{role_id}/models")
def role_models(role_id: str, image: bool = False):
    role = not_found(get_role, role_id)
    cfg = not_found(role.config)
    if image:
        cfg = dataclasses.replace(cfg, base_url=cfg.image_base_url, api_key=cfg.image_api_key)
    try:
        return {"models": llm.list_models(cfg), "base_url": cfg.base_url}
    except llm.LLMError as e:
        raise HTTPException(400, f"couldn't list models from {cfg.base_url}: {str(e)[:300]}")


@app.post("/api/roles/{role_id}/test")
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


@app.post("/api/roles/{role_id}/apply-provider")
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
    hat: str | None = None


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


@app.get("/api/projects/{slug}")
def get_project(slug: str):
    artifacts = not_found(projects.list_artifacts, slug)
    run = room.active_run(slug)
    return {"slug": slug, "artifacts": artifacts, "images": projects.list_images(slug),
            "references": projects.list_references(slug),
            "versions": projects.list_versions(slug),
            "active_run": run.id if run else None,
            "active_version": run.version.id if run else None,
            "settings": review.settings(slug),
            "library": projects.library()}


@app.get("/api/projects/{slug}/images/{name}")
def get_image(slug: str, name: str):
    return FileResponse(not_found(projects.image_path, slug, name))


@app.get("/api/projects/{slug}/artifacts/{name}", response_class=PlainTextResponse)
def get_artifact(slug: str, name: str):
    content = not_found(projects.read_artifact, slug, name)
    if content is None:
        raise HTTPException(404)
    return content


@app.put("/api/projects/{slug}/artifacts/{name}")
def put_artifact(slug: str, name: str, body: ArtifactBody):
    not_found(projects.write_artifact, slug, name, body.content)
    if name == "layouts.md":  # hand edits to layouts redraw the preview too
        md, _, feedback = thumbnails.render_layouts(body.content, projects.read_artifact(slug, "thumbnails.md"))
        projects.write_artifact(slug, "thumbnails.md", md)
        return {"ok": True, "thumbnail_issues": feedback}
    return {"ok": True}


PREVIEW_FILES = {"layout": "thumbnails.md", "drawn": "thumbnails-drawn.md", "image": "thumbnails-image.md"}


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


@app.get("/api/projects/{slug}/references/{name}", response_class=PlainTextResponse)
def get_reference(slug: str, name: str):
    content = not_found(projects.read_reference, slug, name)
    if content is None:
        raise HTTPException(404)
    return content


# ---- versions --------------------------------------------------------------

@app.get("/api/projects/{slug}/versions/{version}")
def get_version(slug: str, version: str):
    meta = not_found(projects.version_meta, slug, version)
    return {**meta, "artifacts": projects.list_artifacts(slug, version),
            "image_files": projects.list_images(slug, version),
            "reference_files": projects.list_references(slug, version)}


@app.get("/api/projects/{slug}/versions/{version}/references/{name}", response_class=PlainTextResponse)
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
def get_version_artifact(slug: str, version: str, name: str):
    content = not_found(projects.read_artifact, slug, name, version)
    if content is None:
        raise HTTPException(404)
    return content


@app.get("/api/projects/{slug}/versions/{version}/images/{name}")
def get_version_image(slug: str, version: str, name: str):
    return FileResponse(not_found(projects.image_path, slug, name, version))


@app.get("/api/projects/{slug}/versions/{version}/events")
def get_version_events(slug: str, version: str):
    return {"events": not_found(projects.version_events, slug, version)}


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


# ---- writing rounds and review -------------------------------------------------

class RoundSettings(BaseModel):
    pages: int | None = None
    chapter: int | None = None
    max_passes: int | None = None
    references: list[str] | None = None   # library files to use; ["*"] = all


class RoundRequest(BaseModel):
    note: str | None = None
    hat: str | None = None


class PageReview(BaseModel):
    verdict: str | None = None
    comment: str | None = None
    art: str | None = None
    invert: str | None = None
    clear: bool = False


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
    if body.references not in (None, ["*"]):
        known = {f["name"] for f in projects.library()}
        unknown = [r for r in body.references if r not in known]
        if unknown:
            raise HTTPException(400, f"not in references/: {', '.join(unknown)}")
    return review.save_settings(slug, **body.model_dump())


@app.post("/api/projects/{slug}/rounds")
def start_round(slug: str, body: RoundRequest):
    not_found(projects.project_dir, slug)
    try:
        run = room.start_round(slug, (body.note or "").strip() or None, body.hat or None)
    except RuntimeError as e:
        raise HTTPException(409, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"run_id": run.id, "version": run.version.id, "kind": run.plan["kind"]}


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
    return not_found(review.save_page, slug, page, body.verdict, body.comment, body.art, body.clear, body.invert)


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
        run = room.start(slug, body.roles, (body.note or "").strip() or None, body.hat or None)
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


@app.post("/api/runs/{run_id}/stop")
def stop_run(run_id: str):
    _get_run(run_id).stop_requested = True
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
