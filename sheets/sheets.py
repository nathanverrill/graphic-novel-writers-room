#!/usr/bin/env python3
"""sheets.py - build a LoRA training set for one character or one place, a step at a time.

You lock one view by hand. Every other image is made FROM it: each step asks two or three
image models for a change ("turn to three-quarter view"), you pick the best candidate on a
contact sheet, and the pick is the parent of the next step. What you kept, with its caption,
is the training set; lineage.jsonl says which model won which kind of change.

A subject, a character or a place, is a folder:

    sheets/ada/
      kind.txt          "place" for a place; absent or "character" for a character
      description.txt   the subject's look, pasted in (the room's visual lock, or your words)
      notes.txt         optional: anything more for every step ("always the burn scar on the left hand")
      style.txt         optional: how it is drawn; otherwise the brief's visual direction
      lock.png          the approved starting view (front, neutral, plain background)
      reference.png     optional: an image to roll the lock FROM - a screenshot, a photo, a game
                        scene - keeping what is where, redrawn in the book's style
      steps.txt         optional; otherwise sheets/steps.txt (a place: steps-place.txt), one step per line:
                        name | instruction | parent     (parent: a step name, or "lock"; default: the last pick)
      runs/             every candidate, per step, with the contact sheet you chose from
      set/              the picks: NN-name.png and NN-name.txt (the caption), ready to train on
      lineage.jsonl     one line per candidate: step, model, prompt, parent, picked or not

Run:   python3 sheets/sheets.py ada
       python3 sheets/sheets.py ada --models google/gemini-3.1-flash-image,openai/gpt-image-2 --each 2
       python3 sheets/sheets.py ada --step face-angry        # redo one step
       python3 sheets/sheets.py ada --dry                    # no model: fakes candidates, to see the flow

Key: OPENROUTER_API_KEY, or the OpenRouter key saved by the room in secrets/keys.json.
Only the standard library. The contact sheet is an HTML file opened in your browser; you
answer in the terminal: a number to keep, r to redo the step, s to skip it, q to stop.
"""
import argparse
import base64
import concurrent.futures
import http.client
import json
import mimetypes
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
OPENROUTER = "https://openrouter.ai/api/v1"
DEFAULT_MODELS = ["google/gemini-3.1-flash-image", "openai/gpt-image-2", "openai/gpt-image-2.5-flare", "openai/gpt-image-2.5-sunburst",
                  "microsoft/mai-image-2.6-flash"]
# Never offered, whatever OpenRouter lists: a trailing "/" or "-" is a prefix. Design and vector
# models, previews of models that have shipped, and generations a newer model here replaces.
# Everything left takes at least three reference images, so a lock from a reference with the
# style plate (two images) works on all of them.
EXCLUDED = ["recraft/", "inclusionai/", "sourceful/", "krea/",
            "qwen/", "bytedance/", "bytedance-seed/", "x-ai/", "google/gemini-3-pro-image",   # the showrunner's call
            "google/gemini-3.1-flash-image-preview", "google/gemini-3-pro-image-preview", "google/gemini-2.5-flash-image",
            "openai/gpt-image-1", "openai/gpt-image-1-mini", "openai/gpt-5-image", "openai/gpt-5-image-mini",
            "microsoft/mai-image-2.5", "microsoft/mai-image-2.5-pro",
            "black-forest-labs/flux.2-klein-4b"]


def excluded(model):
    return any(model.startswith(x) if x.endswith(("/", "-")) else model == x for x in EXCLUDED)
TIMEOUT = 300
SECRETS = HERE.parent / "secrets" / "keys.json"     # where the room saves provider keys


# ---- the key -----------------------------------------------------------------------------

def api_key():
    key = os.getenv("OPENROUTER_API_KEY")
    if key:
        return key
    saved = SECRETS
    if saved.exists():
        try:
            key = json.loads(saved.read_text()).get(OPENROUTER)
        except ValueError:
            key = None
        if key:
            return key
    sys.exit("No OpenRouter key: set OPENROUTER_API_KEY, or save one in the room (secrets/keys.json).")


# ---- the character folder ------------------------------------------------------------------

def read_steps(path):
    """name | instruction | parent  -> [(name, instruction, parent or None)]; # lines are comments."""
    out = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 2:
            sys.exit(f"{path.name}: a step is `name | instruction | parent`, got: {raw}")
        name = re.sub(r"[^a-z0-9]+", "-", parts[0].lower()).strip("-")
        out.append((name, parts[1], parts[2] if len(parts) > 2 and parts[2] else None))
    return out


class Character:
    def __init__(self, folder, trigger=None, need_lock=True):
        self.dir = Path(folder)
        self.name = self.dir.name
        if not self.dir.is_dir():
            sys.exit(f"no folder {self.dir}: make it, with description.txt and lock.png")
        desc = self.dir / "description.txt"
        if not desc.exists():
            sys.exit(f"{self.dir}/description.txt is missing: paste the character's look there")
        self.description = " ".join(desc.read_text().split())
        kind = self.dir / "kind.txt"
        self.kind = "place" if kind.exists() and kind.read_text().strip() == "place" else "character"
        notes = self.dir / "notes.txt"
        self.notes = " ".join(notes.read_text().split()) if notes.exists() else ""
        style = self.dir / "style.txt"
        self.style = " ".join(style.read_text().split()) if style.exists() else ""
        locks = [p for p in self.dir.glob("lock.*") if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
        if not locks and need_lock:
            sys.exit(f"{self.dir}/lock.png is missing: the approved starting view")
        self.lock = locks[0] if locks else None
        refs = [p for p in self.dir.glob("reference.*") if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
        self.reference = refs[0] if refs else None
        steps = self.dir / "steps.txt"
        self.steps = read_steps(steps if steps.exists() else HERE / ("steps-place.txt" if self.kind == "place" else "steps.txt"))
        self.trigger = trigger or f"{re.sub(r'[^a-z]', '', self.name.lower())[:6]}{'plc' if self.kind == 'place' else 'chr'}"
        (self.dir / "runs").mkdir(exist_ok=True)
        (self.dir / "set").mkdir(exist_ok=True)

    def pick_of(self, step_name):
        """The image kept for a step (or the lock)."""
        if step_name in (None, "lock"):
            return self.lock
        found = sorted((self.dir / "set").glob(f"*-{step_name}.png")) + sorted((self.dir / "set").glob(f"*-{step_name}.jpg"))
        return found[0] if found else None

    def log(self, **record):
        with (self.dir / "lineage.jsonl").open("a") as f:
            f.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%S"), **record}) + "\n")


# ---- the models ------------------------------------------------------------------------------

def data_url(path):
    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def refs_of(parent):
    """The reference images for one call: none, one, or a list (a lock with the style plate)."""
    return [] if parent is None else list(parent) if isinstance(parent, (list, tuple)) else [parent]


def generate(model, prompt, parent, out_stem, key):
    """One image from one model, given the parent image as a reference (or none, for the
    first roll of a lock; or a list, the style plate last). Returns the path."""
    payload = {"model": model, "prompt": prompt}
    if refs_of(parent):
        payload["input_references"] = [{"type": "image_url", "image_url": {"url": data_url(r)}} for r in refs_of(parent)]
    req = urllib.request.Request(f"{OPENROUTER}/images", data=json.dumps(payload).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                          "HTTP-Referer": "https://github.com/writers-room", "X-Title": "sheets"})
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                result = json.loads(r.read())
            break
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"{model}: HTTP {e.code} {e.read()[:300].decode(errors='replace')}")
        except (http.client.RemoteDisconnected, ConnectionResetError):
            # a provider under load (Qwen's, with several calls at once) can hang up after ~180s
            # instead of answering: once more, and then it is that candidate's failure
            if attempt == 2:
                raise RuntimeError(f"{model}: the provider closed the connection twice without answering")
    data = (result.get("data") or [{}])[0]
    if not data.get("b64_json"):
        raise RuntimeError(f"{model}: no image in the reply: {json.dumps(result)[:300]}")
    ext = {"image/jpeg": ".jpg", "image/webp": ".webp"}.get(data.get("media_type"), ".png")
    out = out_stem.parent / (out_stem.name + ext)     # not with_suffix: a model name can hold a dot
    out.write_bytes(base64.b64decode(data["b64_json"]))
    return out


BLANK_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAEAAAABgCAIAAABxbFPeAAAAJklEQVR4nO3BMQEAAADCoPVPbQwfoAAAAAAAAAAAAAAAAAAAAIC3AS5gAAFpm5W4AAAAAElFTkSuQmCC")


def fake(model, prompt, parent, out_stem, key):
    """--dry: the parent copied (or a blank), so the flow can be walked without spending."""
    time.sleep(float(os.getenv("SHEETS_DRY_SECONDS") or 0.2))
    parent = (refs_of(parent) or [None])[0]
    out = out_stem.parent / (out_stem.name + (parent.suffix if parent is not None else ".png"))
    if parent is not None:
        shutil.copyfile(parent, out)
    else:
        out.write_bytes(BLANK_PNG)
    return out


# What the lock shows, and who may be in frame, by kind.
VIEW = {"character": ("Full-length front view, standing, neutral pose, arms at the sides, looking at the camera, "
                      "even daylight, plain light background."),
        "place": "A wide establishing view at eye level, the whole place readable in one frame, nobody in frame."}
FRAME = {"character": "One character, nobody else in frame.",
         "place": "Nobody in frame unless the change asks for people."}
NO_TEXT = "No text, letters, labels or watermarks anywhere."


def prompt_for(char, instruction, notes=None, from_pick=False):
    """A step's prompt. From the step's parent: make the change. From a pick of a previous roll
    of the same step: the change is mostly there, fix what the notes say."""
    if from_pick:
        change = (f"This image is an attempt at: {instruction}. Keep it, and fix only this: "
                  f"{notes or 'bring it closer to the description'}.")
    else:
        change = f"Change only this: {instruction}." + (f" Also: {notes}." if notes else "")
    return (f"Edit the reference image. Keep this exact {char.kind}: {char.description} "
            + (f"Also: {char.notes} " if char.notes else "")
            + f"{change} Same drawing style, same line and colour as the reference. "
            f"{FRAME[char.kind]} {NO_TEXT}")


PLATE = ("Draw it in exactly the rendering of the {which} reference image: its line weight, palette, lighting, "
         "texture and level of detail. Take nothing else from that image: not its subject, face, body, clothes, "
         "pose, props, composition or background.")


def lock_prompt(char, style, notes=None, from_pick=False, plate=False):
    """The lock: the first roll from words alone; later rolls edit the closest pick with notes."""
    view, frame = VIEW[char.kind], FRAME[char.kind]
    style = char.style or style
    if from_pick:
        return (f"Edit the reference image. Keep this exact {char.kind}: {char.description} "
                + (f"Also: {char.notes} " if char.notes else "")
                + f"Change this and nothing else: {notes or 'bring it closer to the description'}. "
                + f"{view} Same drawing style as the reference. {frame} {NO_TEXT}")
    return (f"Style: {(style or 'clean comic line art with flat colour').rstrip('.')}. "
            + (PLATE.format(which="attached") + " " if plate else "")
            + (f"{char.notes.rstrip('.')}. " if char.notes else "")
            + (f"Notes: {notes} " if notes else "")
            + f"Draw this {char.kind}: {char.description} {view} {frame} {NO_TEXT}")


HARD_SF = ("Hard science fiction on the 80/15/5 rule: 80% of what is in frame is today's real technology, "
           "materials, infrastructure and wear carried forward; 15% is a straight-line development of it that "
           "has become ordinary and looks used; 5% at most is new. Nothing fantastical: no impossible structures, "
           "no holograms, no glowing seams, nothing floating; every building, machine and vehicle could be built "
           "with what exists")
PHOTO = ("Photographic realism: as if photographed on location with a full-frame camera, physically "
         "accurate materials, weathering and light, true perspective, subtle film grain. Not a cartoon, "
         "not cel-shaded, not flat colour, not painterly, not stylised")


def reference_prompt(char, style, notes=None, plate=False):
    """The lock from a reference image: the reference says what is where; everything else -
    materials, light, line, colour - comes from the style, the notes and the description.
    The style leads, because that is what the models weigh most."""
    style = (char.style or style or PHOTO).rstrip(".")
    return (f"{style}. " + (PLATE.format(which="second") + " " if plate else "")
            + (f"{char.notes.rstrip('.')}. " if char.notes else "") + (f"{notes.rstrip('.')}. " if notes else "")
            + f"Use the {'first ' if plate else ''}reference image only for what is where: the same terrain and geography, the same "
            "buildings and structures in the same places at the same sizes, the same viewpoint and framing. "
            "Nothing of the reference's medium survives: no blocks, voxels, cubes, pixel textures, game "
            "rendering or screenshot artefacts; real materials, real proportions, natural light. "
            f"This {char.kind}: {char.description} {FRAME[char.kind]} {NO_TEXT}")


# ---- the contact sheet ----------------------------------------------------------------------

def contact_sheet(char, step, instruction, parent, cands, errors):
    cells = "".join(
        f'<figure><img src="{p.name}"><figcaption><b>{i}</b> {m}</figcaption></figure>'
        for i, (m, p) in enumerate(cands, 1))
    errs = "".join(f"<li>{e}</li>" for e in errors)
    html = f"""<!doctype html><meta charset="utf-8"><title>{char.name}: {step}</title>
<style>body{{font:14px system-ui;margin:1rem;background:#1b1b1b;color:#eee}}h1{{font-size:1.1rem}}
.row{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1rem}}
figure{{margin:0;background:#2a2a2a;padding:.5rem;border-radius:6px}}img{{width:100%;border-radius:4px}}
figcaption{{margin-top:.4rem;color:#bbb}}b{{color:#fff;font-size:1.3rem;margin-right:.4rem}}
.parent img{{max-width:300px}} ul{{color:#f88}}</style>
<h1>{char.name} · step <em>{step}</em>: {instruction}</h1>
<div class="parent"><small>parent</small><br><img src="{os.path.relpath(parent, cands[0][1].parent) if cands else ''}"></div>
<p>Pick the number in the terminal. Same face, same clothes, same proportions as the parent?</p>
<div class="row">{cells}</div>{f'<ul>{errs}</ul>' if errs else ''}"""
    path = (cands[0][1].parent if cands else char.dir / "runs" / step) / "contact.html"
    path.write_text(html)
    return path


# ---- the loop --------------------------------------------------------------------------------

def make_candidates(char, n, step, instruction, parent, models, each, gen, key, say=print, folder=None, prompt=None,
                    on_candidate=None, variants=None):
    """One step's candidates, from every model at once. Returns (folder, [(model, path)], [errors]).
    on_candidate(model, path, seconds, variant) is called as each one lands, so a page can show it.
    variants [(name, prompt, parent)] rolls every model once per variant - a lock "plain" and
    "styled", side by side; without them, one variant from `prompt` and `parent`."""
    folder = folder or char.dir / "runs" / f"{n:02d}-{step}"
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("cand-*"):
        old.unlink()
    variants = variants or [(None, prompt or prompt_for(char, instruction), parent)]
    jobs = [(m, k, v) for v in variants for m in models for k in range(1, each + 1)]
    cands, errors, labels = [], [], {}
    stem = lambda m, k, v: folder / (f"cand-{re.sub(r'[^a-z0-9]+', '-', m.split('/')[-1].lower())}-{k}" + (f"-{v[0]}" if v[0] else ""))
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        futs = {pool.submit(gen, m, v[1], v[2], stem(m, k, v), key): (m, k, v) for m, k, v in jobs}
        started = time.time()
        for fut in concurrent.futures.as_completed(futs):
            m, k, (variant, prompt, parent) = futs[fut]
            parent = (refs_of(parent) or [None])[0]
            took = round(time.time() - started, 1)
            try:
                path = fut.result()
                cands.append((m, path))
                labels[path.name] = variant
                say(f"     ✓ {m} #{k}{f' {variant}' if variant else ''} in {took:g}s")
                char.log(step=step, model=m, prompt=prompt, parent=parent.name if parent else None, candidate=path.name,
                         picked=False, seconds=took, **({"variant": variant} if variant else {}))
                if on_candidate:
                    on_candidate(m, path, took, variant)
            except Exception as e:      # noqa: BLE001 - one model failing is not the step failing
                errors.append(f"{m} #{k}: {str(e)[:300]}")
                say(f"     ✗ {m} #{k}: {str(e)[:160]}")
                char.log(step=step, model=m, error=str(e)[:200], seconds=took)
    cands.sort(key=lambda c: c[1].name)
    (folder / "step.json").write_text(json.dumps({"step": step, "n": n, "instruction": instruction, "parent": parent.name if parent else None,
                                                  "candidates": [{"model": m, "file": p.name, "variant": labels[p.name]} for m, p in cands],
                                                  "errors": errors}, indent=1))
    return folder, cands, errors


def keep(char, n, step, instruction, parent, model, path):
    """The pick: into set/ with its caption. Returns the kept path."""
    kept = char.dir / "set" / f"{n:02d}-{step}{path.suffix}"
    for old in (char.dir / "set").glob(f"{n:02d}-{step}.*"):
        old.unlink()
    shutil.copyfile(path, kept)
    (char.dir / "set" / f"{n:02d}-{step}.txt").write_text(f"{char.trigger}, {instruction}\n")
    char.log(step=step, model=model, parent=parent.name, candidate=path.name, picked=True, kept=kept.name)
    return kept


def run_step(char, n, step, instruction, parent_name, models, each, gen, key, open_browser):
    parent = char.pick_of(parent_name) if parent_name else char.last_pick
    if parent is None:
        print(f"  {step}: its parent {parent_name!r} has no pick yet - skipped")
        return None
    print(f"\n[{n:02d}] {step}: {instruction}\n     from {parent.name} · {len(models) * each} candidates from {len(models)} models…")
    folder, cands, errors = make_candidates(char, n, step, instruction, parent, models, each, gen, key)
    if not cands:
        print("     nothing came back; skipping this step")
        return None
    sheet = contact_sheet(char, step, instruction, parent, cands, errors)
    if open_browser:
        webbrowser.open(sheet.as_uri())
    print(f"     contact sheet: {sheet}")
    while True:
        ans = input(f"     keep 1-{len(cands)}, r redo, s skip, q quit: ").strip().lower()
        if ans == "q":
            sys.exit(0)
        if ans == "s":
            return None
        if ans == "r":
            return "redo"
        if ans.isdigit() and 1 <= int(ans) <= len(cands):
            m, p = cands[int(ans) - 1]
            kept = keep(char, n, step, instruction, parent, m, p)
            print(f"     kept {kept.name} ({m})")
            return kept


def main():
    ap = argparse.ArgumentParser(description="Build a LoRA training set for one character, step by step.")
    ap.add_argument("character", help="folder under sheets/, e.g. ada (a place: put `place` in its kind.txt)")
    ap.add_argument("--models", default=",".join(DEFAULT_MODELS), help="comma-separated OpenRouter image models")
    ap.add_argument("--each", type=int, default=2, help="candidates per model per step")
    ap.add_argument("--step", help="run only this step (redo it)")
    ap.add_argument("--trigger", help="the caption's trigger word (default: from the folder name)")
    ap.add_argument("--dry", action="store_true", help="no model: copies the parent, to walk the flow")
    ap.add_argument("--no-open", action="store_true", help="do not open the contact sheet in a browser")
    args = ap.parse_args()

    char = Character(HERE / args.character if not Path(args.character).is_dir() else args.character, args.trigger)
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    gen, key = (fake, "") if args.dry else (generate, api_key())
    char.last_pick = char.lock
    print(f"{char.name}: {len(char.steps)} steps, trigger word {char.trigger!r}, models {', '.join(models)}"
          + (" (dry run)" if args.dry else ""))
    for n, (step, instruction, parent_name) in enumerate(char.steps, 1):
        if args.step and step != args.step:
            have = char.pick_of(step)
            if have:
                char.last_pick = have
            continue
        if not args.step and char.pick_of(step):
            print(f"[{n:02d}] {step}: already kept, skipping (use --step {step} to redo)")
            char.last_pick = char.pick_of(step)
            continue
        while True:
            result = run_step(char, n, step, instruction, parent_name, models, args.each, gen, key, not args.no_open)
            if result != "redo":
                break
        if isinstance(result, Path):
            char.last_pick = result
    kept = sorted(p for p in (char.dir / "set").iterdir() if p.suffix != ".txt")
    print(f"\n{char.name}: {len(kept)} images in {char.dir / 'set'}, captions beside them. "
          f"That folder is the training set; lineage.jsonl says which model won each step.")


if __name__ == "__main__":
    main()
