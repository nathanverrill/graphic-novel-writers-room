#!/usr/bin/env python3
"""sheets.py - build a LoRA training set for one character, one step at a time.

You lock one view by hand. Every other image is made FROM it: each step asks two or three
image models for a change ("turn to three-quarter view"), you pick the best candidate on a
contact sheet, and the pick is the parent of the next step. What you kept, with its caption,
is the training set; lineage.jsonl says which model won which kind of change.

A character is a folder:

    sheets/ada/
      description.txt   the character's look, pasted in (the room's visual lock, or your words)
      lock.png          the approved starting view (front, neutral, plain background)
      steps.txt         optional; otherwise sheets/steps.txt, one step per line:
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
DEFAULT_MODELS = ["google/gemini-3.1-flash-image", "openai/gpt-image-2", "black-forest-labs/flux.2-pro"]
TIMEOUT = 300


# ---- the key -----------------------------------------------------------------------------

def api_key():
    key = os.getenv("OPENROUTER_API_KEY")
    if key:
        return key
    saved = HERE.parent / "secrets" / "keys.json"
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
    def __init__(self, folder, trigger=None):
        self.dir = Path(folder)
        self.name = self.dir.name
        if not self.dir.is_dir():
            sys.exit(f"no folder {self.dir}: make it, with description.txt and lock.png")
        desc = self.dir / "description.txt"
        if not desc.exists():
            sys.exit(f"{self.dir}/description.txt is missing: paste the character's look there")
        self.description = " ".join(desc.read_text().split())
        locks = [p for p in self.dir.glob("lock.*") if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
        if not locks:
            sys.exit(f"{self.dir}/lock.png is missing: the approved starting view")
        self.lock = locks[0]
        steps = self.dir / "steps.txt"
        self.steps = read_steps(steps if steps.exists() else HERE / "steps.txt")
        self.trigger = trigger or f"{re.sub(r'[^a-z]', '', self.name.lower())[:6]}chr"
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


def generate(model, prompt, parent, out_stem, key):
    """One image from one model, given the parent image as a reference. Returns the path."""
    payload = {"model": model, "prompt": prompt,
               "input_references": [{"type": "image_url", "image_url": {"url": data_url(parent)}}]}
    req = urllib.request.Request(f"{OPENROUTER}/images", data=json.dumps(payload).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                          "HTTP-Referer": "https://github.com/writers-room", "X-Title": "sheets"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            result = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{model}: HTTP {e.code} {e.read()[:300].decode(errors='replace')}")
    data = (result.get("data") or [{}])[0]
    if not data.get("b64_json"):
        raise RuntimeError(f"{model}: no image in the reply: {json.dumps(result)[:300]}")
    ext = {"image/jpeg": ".jpg", "image/webp": ".webp"}.get(data.get("media_type"), ".png")
    out = out_stem.parent / (out_stem.name + ext)     # not with_suffix: a model name can hold a dot
    out.write_bytes(base64.b64decode(data["b64_json"]))
    return out


def fake(model, prompt, parent, out_stem, key):
    """--dry: the parent copied, so the flow can be walked without spending."""
    time.sleep(0.2)
    out = out_stem.parent / (out_stem.name + parent.suffix)
    shutil.copyfile(parent, out)
    return out


def prompt_for(char, instruction):
    return (f"Edit the reference image. Keep this exact character: {char.description} "
            f"Change only this: {instruction}. Same drawing style, same line and colour as the reference. "
            f"One character, nobody else in frame. No text, letters, labels or watermarks anywhere.")


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

def run_step(char, n, step, instruction, parent_name, models, each, gen, key, open_browser):
    parent = char.pick_of(parent_name) if parent_name else char.last_pick
    if parent is None:
        print(f"  {step}: its parent {parent_name!r} has no pick yet - skipped")
        return None
    folder = char.dir / "runs" / f"{n:02d}-{step}"
    folder.mkdir(parents=True, exist_ok=True)
    prompt = prompt_for(char, instruction)
    jobs = [(m, k) for m in models for k in range(1, each + 1)]
    print(f"\n[{n:02d}] {step}: {instruction}\n     from {parent.name} · {len(jobs)} candidates from {len(models)} models…")
    cands, errors = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        futs = {pool.submit(gen, m, prompt, parent, folder / f"cand-{re.sub(r'[^a-z0-9]+', '-', m.split('/')[-1].lower())}-{k}", key): (m, k) for m, k in jobs}
        for fut in concurrent.futures.as_completed(futs):
            m, k = futs[fut]
            try:
                path = fut.result()
                cands.append((m, path))
                print(f"     ✓ {m} #{k}")
            except Exception as e:      # noqa: BLE001 - one model failing is not the step failing
                errors.append(str(e))
                print(f"     ✗ {m} #{k}: {str(e)[:160]}")
    cands.sort(key=lambda c: c[1].name)
    for m, p in cands:
        char.log(step=step, model=m, prompt=prompt, parent=parent.name, candidate=p.name, picked=False)
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
            keep = char.dir / "set" / f"{n:02d}-{step}{p.suffix}"
            for old in (char.dir / "set").glob(f"{n:02d}-{step}.*"):
                old.unlink()
            shutil.copyfile(p, keep)
            (char.dir / "set" / f"{n:02d}-{step}.txt").write_text(f"{char.trigger}, {instruction}\n")
            char.log(step=step, model=m, parent=parent.name, candidate=p.name, picked=True, kept=keep.name)
            print(f"     kept {keep.name} ({m})")
            return keep


def main():
    ap = argparse.ArgumentParser(description="Build a LoRA training set for one character, step by step.")
    ap.add_argument("character", help="folder under sheets/, e.g. ada")
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
