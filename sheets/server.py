#!/usr/bin/env python3
"""The sheets page: sheets.py behind one small web page, in its own container.

    python3 sheets/server.py            # http://localhost:8001

Same folders as the command line (sheets/<character>/...), so the two can be mixed. The page
can also read markdown from the campaigns folder - a character's section of characters.md,
say - to fill in the description. Standard library only; one thread per request, and the
generation of a step runs in a thread of its own while the page polls."""
import base64
import json
import mimetypes
import os
import re
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sheets as core                                  # noqa: E402
if os.getenv("SECRETS_FILE"):
    core.SECRETS = Path(os.getenv("SECRETS_FILE"))

ROOT = Path(os.getenv("SHEETS_DIR") or core.HERE).resolve()            # where the characters live
MD_ROOTS = [Path(p).resolve() for p in (os.getenv("MD_DIRS") or str(core.HERE.parent / "campaigns")).split(":") if p]
PORT = int(os.getenv("PORT") or 8001)
DRY = bool(os.getenv("SHEETS_DRY"))

_running = {}          # (character, step) -> {"status": "running"|"done"|"failed", "errors": [...]}
_lock = threading.Lock()


# ---- helpers ------------------------------------------------------------------------------------

def character(name):
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,40}", name or ""):
        raise ValueError("a character is a short lowercase folder name")
    return ROOT / name


def load(name, need=True):
    d = character(name)
    if not d.is_dir():
        if need:
            raise FileNotFoundError(name)
        return None
    if not (d / "description.txt").exists() or not list(d.glob("lock.*")):
        return None          # made, not ready
    return core.Character(d)


def stage_file(d, stage_id):
    return d / "runs" / stage_id / "stage.json"


def stage_state(d, stage_id):
    f = stage_file(d, stage_id)
    return json.loads(f.read_text()) if f.exists() else {"rounds": [], "pick": None}


def save_stage(d, stage_id, st):
    f = stage_file(d, stage_id)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(st, indent=1))


def style_text():
    """The book's visual direction, if a brief is in reach: the first campaign's brief.md."""
    for root in MD_ROOTS:
        for b in sorted(root.glob("*/production/brief.md")) if root.is_dir() else []:
            m = re.search(r"^#+\s*.*(visual|style|look).*\n(.*?)(?=^#|\Z)", b.read_text(), re.S | re.M | re.I)
            if m:
                return " ".join(m.group(2).split())[:600]
    return None


def stages(char):
    """[(id, n, title, instruction, parent_name)] - the lock, then the steps."""
    out = [("00-lock", 0, "lock", "the approved starting view: full-length front, neutral, plain background", None)]
    for n, (step, instruction, parent) in enumerate(char.steps, 1):
        out.append((f"{n:02d}-{step}", n, step, instruction, parent))
    return out


def kept_for(char, stage_id, title):
    if stage_id == "00-lock":
        return char.lock
    return char.pick_of(title)


def parent_for(char, stage_id, n, parent_name):
    """The image a stage builds on: the pick of one of its own rolls if there is one (roll
    again), else the named step's keep, else the nearest earlier keep, else the lock."""
    st = stage_state(char.dir, stage_id)
    pick = st.get("pick")
    if pick:
        p = char.dir / "runs" / stage_id / pick["round"] / pick["file"]
        if p.exists():
            return p, True
    if stage_id == "00-lock":
        return None, False
    if parent_name:
        return char.pick_of(parent_name), False
    parent = char.lock
    for sid, k, title, _, _ in stages(char):
        if 0 < k < n and char.pick_of(title):
            parent = char.pick_of(title)
    return parent, False


def roll(name, stage_id, notes, models, each):
    d = character(name)
    if not (d / "description.txt").exists():
        raise ValueError("write the description first")
    char = core.Character(d, need_lock=False)
    found = next((x for x in stages(char) if x[0] == stage_id), None)
    if not found:
        raise ValueError(f"no stage {stage_id}")
    _, n, title, instruction, parent_name = found
    parent, from_pick = parent_for(char, stage_id, n, parent_name)
    if stage_id != "00-lock" and parent is None:
        raise ValueError("this step's parent has nothing kept yet - lock first, or keep the step it builds on")
    if stage_id == "00-lock":
        prompt = core.lock_prompt(char, style_text(), notes, from_pick=from_pick)
    else:
        prompt = core.prompt_for(char, instruction, notes, from_pick=from_pick)
    st = stage_state(d, stage_id)
    k = len(st["rounds"]) + 1
    folder = d / "runs" / stage_id / f"r{k}"
    key = "" if DRY else core.api_key()
    gen = core.fake if DRY else core.generate
    with _lock:
        if _running.get((name, stage_id), {}).get("status") == "running":
            raise ValueError("that stage is already rolling")
        _running[(name, stage_id)] = {"status": "running", "errors": []}
    st["rounds"].append({"round": f"r{k}", "notes": notes or "", "from_pick": from_pick,
                         "parent": parent.name if parent else None, "candidates": [], "errors": []})
    save_stage(d, stage_id, st)

    def work():
        try:
            _, cands, errors = core.make_candidates(char, n, title, instruction, parent, models, each, gen, key,
                                                    say=lambda m: None, folder=folder, prompt=prompt)
            st2 = stage_state(d, stage_id)
            st2["rounds"][-1].update(candidates=[{"model": m, "file": p.name} for m, p in cands], errors=errors)
            save_stage(d, stage_id, st2)
            _running[(name, stage_id)] = {"status": "done" if cands else "failed", "errors": errors}
        except Exception as e:      # noqa: BLE001
            st2 = stage_state(d, stage_id)
            st2["rounds"][-1]["errors"] = [str(e)[:300]]
            save_stage(d, stage_id, st2)
            _running[(name, stage_id)] = {"status": "failed", "errors": [str(e)[:300]]}
    threading.Thread(target=work, daemon=True).start()


def pick(name, stage_id, round_name, file):
    d = character(name)
    if not (d / "runs" / stage_id / round_name / file).exists():
        raise ValueError("no such candidate")
    st = stage_state(d, stage_id)
    st["pick"] = {"round": round_name, "file": file}
    save_stage(d, stage_id, st)


def keep(name, stage_id):
    """The pick becomes the lock, or the step's kept image with its caption."""
    d = character(name)
    char = core.Character(d, need_lock=False)
    st = stage_state(d, stage_id)
    if not st.get("pick"):
        raise ValueError("pick the closest candidate first")
    src = d / "runs" / stage_id / st["pick"]["round"] / st["pick"]["file"]
    if stage_id == "00-lock":
        for old in d.glob("lock.*"):
            old.unlink()
        dst = d / f"lock{src.suffix}"
        dst.write_bytes(src.read_bytes())
        char.log(step="lock", model=None, parent=None, candidate=str(src.relative_to(d)), picked=True, kept=dst.name)
        return dst.name
    _, n, title, instruction, _ = next(x for x in stages(char) if x[0] == stage_id)
    rnd = next(r for r in st["rounds"] if r["round"] == st["pick"]["round"])
    model = next((c["model"] for c in rnd["candidates"] if c["file"] == src.name), None)
    parent = Path(rnd["parent"] or "lock")
    return core.keep(char, n, title, instruction, parent, model, src).name


def status(name):
    """Everything the page shows for one character."""
    d = character(name)
    desc = (d / "description.txt").read_text() if (d / "description.txt").exists() else ""
    notes = (d / "notes.txt").read_text() if (d / "notes.txt").exists() else ""
    steps_file = d / "steps.txt"
    steps_text = steps_file.read_text() if steps_file.exists() else (core.HERE / "steps.txt").read_text()
    char = core.Character(d, need_lock=False) if desc.strip() else None
    out = {"name": name, "description": desc, "notes": notes, "steps_text": steps_text,
           "lock": char.lock.name if char and char.lock else None,
           "lock_v": int(char.lock.stat().st_mtime) if char and char.lock else 0,
           "trigger": char.trigger if char else None, "stages": [], "set": []}
    if not char:
        return out
    for sid, n, title, instruction, parent_name in stages(char):
        st = stage_state(d, sid)
        live = _running.get((name, sid), {})
        kept = kept_for(char, sid, title)
        rounds = [dict(r, candidates=[dict(c, url=f"/files/{name}/runs/{sid}/{r['round']}/{c['file']}") for c in r["candidates"]])
                  for r in st["rounds"]]
        out["stages"].append({"id": sid, "n": n, "title": title, "instruction": instruction, "parent": parent_name,
                              "kept": f"/files/{name}/{kept.relative_to(d)}?v={int(kept.stat().st_mtime)}" if kept else None,
                              "rounds": rounds, "pick": st.get("pick"), "running": live.get("status") == "running"})
    for p in sorted((d / "set").iterdir()) if (d / "set").is_dir() else []:
        if p.suffix != ".txt":
            cap = p.with_suffix(".txt")
            out["set"].append({"file": p.name, "url": f"/files/{name}/set/{p.name}", "caption": cap.read_text().strip() if cap.exists() else ""})
    return out


def campaigns():
    """The campaign folders under the markdown roots that have a characters.md."""
    out = []
    for root in MD_ROOTS:
        for d in sorted(root.iterdir()) if root.is_dir() else []:
            if d.is_dir() and not d.name.startswith(("_", ".")) and characters_file(d):
                out.append(d.name)
    return out


def characters_file(d):
    """production/characters.md if the room has been there, else intake's copy, else the root."""
    for rel in ("production/characters.md", "preproduction/characters.md", "characters.md"):
        if (d / rel).exists():
            return d / rel
    return None


def cast(campaign):
    """[(name, look)] from the campaign's characters.md: each character heading and its section."""
    d = next((r / campaign for r in MD_ROOTS if (r / campaign).is_dir()), None)
    f = characters_file(d) if d else None
    if not f:
        raise FileNotFoundError(f"{campaign} has no characters.md")
    text = f.read_text()
    people = re.compile(r"\bcharacters?\b|\bcast\b|\bensemble\b", re.I)
    out, name, body, inside, top = [], None, [], False, None
    def close():
        if name:
            look = "\n".join(body).strip()
            if look:
                out.append({"name": name, "look": look})
    for line in text.split("\n"):
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if not m:
            if name is not None:
                body.append(line)
            continue
        depth, head = len(m.group(1)), m.group(2).strip().rstrip("*").strip()
        if depth == 1:
            close(); name, body = None, []
            top = head; inside = bool(people.search(head))
        elif depth == 2:
            close(); name, body = None, []
            if people.search(head):
                inside = True
            elif inside and top and people.search(top) and 1 <= len(head.split()) <= 4:
                name = head          # "# Characters" then "## Ada"
            else:
                inside = False
        elif depth == 3 and inside and 1 <= len(head.split()) <= 4:
            close(); name, body = head, []
        elif name is not None:
            body.append(line)        # a deeper heading inside the character's own section
    close()
    return {"campaign": campaign, "file": str(f.relative_to(f.parents[2])), "characters": out}


def md_files():
    out = []
    for root in MD_ROOTS:
        if not root.is_dir():
            continue
        for p in sorted(root.rglob("*.md")):
            rel = p.relative_to(root)
            if any(part.startswith(("_", ".")) or part == "previous" for part in rel.parts):
                continue
            out.append(f"{root.name}/{rel}")
    return out


def md_read(path):
    root_name, _, rel = path.partition("/")
    root = next((r for r in MD_ROOTS if r.name == root_name), None)
    if root is None:
        raise FileNotFoundError(path)
    p = (root / rel).resolve()
    if root not in p.parents or p.suffix != ".md" or not p.exists():
        raise FileNotFoundError(path)
    text = p.read_text()
    sections, cur = [], None
    for line in text.split("\n"):
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            cur = {"heading": m.group(2).strip().rstrip("*").strip(), "depth": len(m.group(1)), "body": []}
            sections.append(cur)
        elif cur is not None:
            cur["body"].append(line)
    for s in sections:
        s["body"] = "\n".join(s["body"]).strip()
    return {"path": path, "text": text, "sections": [s for s in sections if s["body"]]}


# ---- the page ---------------------------------------------------------------------------------------

PAGE = r"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sheets</title>
<style>
:root{--bg:#171717;--panel:#222;--line:#3a3a3a;--ink:#eee;--muted:#9a9a9a;--go:#2563eb;--ok:#22c55e;--bad:#ef4444}
body{margin:0;font:14px/1.45 system-ui,sans-serif;background:var(--bg);color:var(--ink)}
header{display:flex;gap:.8rem;align-items:center;padding:.6rem 1rem;border-bottom:1px solid var(--line);flex-wrap:wrap}
header h1{font-size:1rem;margin:0 .4rem 0 0}header select,header button{font:inherit;padding:.3rem .5rem;background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:4px}
main{display:grid;grid-template-columns:minmax(16rem,22rem) 1fr;gap:1rem;padding:1rem}
@media(max-width:60rem){main{grid-template-columns:1fr}}
.card{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:.8rem;margin-bottom:1rem}
.card h2{font-size:.8rem;margin:0 0 .5rem;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
textarea,input[type=text]{width:100%;box-sizing:border-box;font:inherit;font-size:.82rem;background:var(--bg);color:var(--ink);border:1px solid var(--line);border-radius:4px;padding:.4rem}
textarea.mono{font-family:ui-monospace,monospace;min-height:10rem}
button{font:inherit;padding:.35rem .7rem;border:1px solid var(--line);border-radius:4px;background:var(--panel);color:var(--ink);cursor:pointer}
button.go{background:var(--go);border-color:var(--go)}button.ok{background:var(--ok);border-color:var(--ok);color:#111}button:disabled{opacity:.45;cursor:default}
.hint{color:var(--muted);font-size:.78rem}.row{display:flex;gap:.5rem;align-items:center;flex-wrap:wrap;margin:.4rem 0}
.err{color:var(--bad);font-size:.76rem}.good{color:var(--ok)}
details summary{cursor:pointer;color:var(--muted);font-size:.8rem;margin:.2rem 0}
/* captured: the lock big, the kept steps small */
.captured .lock img{width:100%;border-radius:4px;border:1px solid var(--line)}
.captured .lock .empty{border:1px dashed var(--line);border-radius:4px;padding:1.4rem .8rem;text-align:center;color:var(--muted);font-size:.8rem}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(88px,1fr));gap:.4rem;margin-top:.6rem}
.grid figure{margin:0;cursor:pointer}.grid img{width:100%;border-radius:3px;border:2px solid transparent;display:block}
.grid figure.now img{border-color:var(--go)}.grid figure.kept img{border-color:var(--ok)}
.grid figcaption{font-size:.64rem;color:var(--muted);margin-top:.15rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.grid .todo{aspect-ratio:2/3;border:1px dashed var(--line);border-radius:3px;display:grid;place-items:center;color:var(--muted);font-size:.7rem}
/* the workspace */
.strip{display:flex;gap:.3rem;flex-wrap:wrap;margin-bottom:.6rem}
.strip button{font-size:.72rem;padding:.15rem .5rem;font-family:ui-monospace,monospace}
.strip button.kept{border-color:var(--ok)}.strip button.now{background:var(--go);border-color:var(--go)}
.stage-head{display:flex;gap:1rem;align-items:flex-start;margin-bottom:.6rem}
.stage-head img{width:96px;border-radius:4px;border:1px solid var(--line)}
.stage-head h3{margin:0 0 .2rem;font-size:1rem}.stage-head h3 b{font-family:ui-monospace,monospace;color:var(--muted);font-weight:500;margin-right:.4rem}
.roll{border:1px solid var(--line);border-radius:6px;padding:.5rem .7rem;margin-bottom:.6rem}
.roll.now{border-color:var(--go)}.roll .who{font-size:.76rem;color:var(--muted)}
.cands{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:.6rem;margin-top:.5rem}
.cands figure{margin:0;background:var(--bg);padding:.3rem;border-radius:4px;cursor:pointer;border:2px solid transparent}
.cands figure:hover{border-color:var(--go)}.cands figure.pick{border-color:var(--ok)}
.cands img{width:100%;border-radius:3px;display:block}.cands figcaption{font-size:.68rem;color:var(--muted);margin-top:.2rem}
.acts{position:sticky;bottom:0;background:var(--panel);padding:.6rem 0 0;border-top:1px solid var(--line);margin-top:.6rem}
.working{display:inline-block;width:.5rem;height:.5rem;border-radius:50%;background:var(--go);animation:pulse 1.2s infinite;margin-right:.4rem}
@keyframes pulse{50%{opacity:.2}}
dialog{background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:6px;width:min(720px,92vw);max-height:80vh}
dialog .sec{padding:.4rem .5rem;border-bottom:1px solid var(--line);cursor:pointer}dialog .sec:hover{background:var(--bg)}
dialog .sec small{color:var(--muted);display:block;white-space:pre-wrap;max-height:4.5em;overflow:hidden}
</style>
<header><h1>Sheets</h1>
  <label class="hint">campaign <select id="camp"></select></label>
  <label class="hint">character <select id="cast"><option value="">choose…</option></select></label>
  <button id="make" class="go">Start</button>
  <span class="hint">· open</span><select id="who"></select>
  <span class="hint" id="top-hint"></span></header>
<main>
<aside>
  <div class="card captured"><h2>Captured</h2>
    <div class="lock" id="lock-box"></div>
    <div class="grid" id="kept-grid"></div>
    <p class="hint" id="set-hint" style="margin:.5rem 0 0"></p></div>
  <div class="card"><details id="setup"><summary>Setup: description, notes, steps, models</summary>
    <h2 style="margin-top:.6rem">Description</h2>
    <textarea id="desc" rows="7" placeholder="The character's look, from characters.md - or paste your own."></textarea>
    <div class="row"><button id="from-md">From a .md file…</button></div>
    <h2 style="margin-top:.8rem">Notes for every prompt</h2>
    <textarea id="notes" rows="2" placeholder="'always the burn scar on the left hand', 'never a hat'"></textarea>
    <h2 style="margin-top:.8rem">Steps</h2>
    <textarea id="steps" class="mono" spellcheck="false"></textarea>
    <p class="hint" style="margin:.3rem 0 0"><code>name | what to change | parent</code> per line. Parent: a step name or <code>lock</code>; empty builds on the previous keep.</p>
    <h2 style="margin-top:.8rem">Models</h2>
    <input id="models" type="text"><div class="row"><label class="hint">candidates per model <input id="each" type="number" min="1" max="4" value="2" style="width:3rem"></label></div>
    <div class="row"><button class="go" id="save">Save setup</button><span class="hint" id="said"></span></div>
    <div class="row"><label><input type="file" id="lock-file" accept="image/*" hidden><button onclick="document.getElementById('lock-file').click()">Upload a lock image instead</button></label></div>
  </details></div>
</aside>
<section>
  <div class="card"><div class="strip" id="strip"></div><div id="work"></div></div>
</section>
</main>
<dialog id="md"><div class="row"><select id="md-file" style="flex:1"></select><button onclick="document.getElementById('md').close()">close</button></div>
  <p class="hint">Click a section to use it as the description.</p><div id="md-secs"></div></dialog>
<script>
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const DEFAULT_MODELS = %MODELS%;
let who = null, st = null, poll = null, castData = null, current = null, lastDrawn = "", notesDraft = {};
async function api(path, opts = {}) {
  const r = await fetch(path, { method: opts.method || "GET", headers: { "content-type": "application/json" }, body: opts.body ? JSON.stringify(opts.body) : undefined });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.error || r.statusText);
  return d;
}
/* ---- who ---- */
async function listWho() {
  const { characters } = await api("/api/characters");
  $("#who").innerHTML = `<option value="">${characters.length ? "started…" : "(none yet)"}</option>` + characters.map((c) => `<option ${c === who ? "selected" : ""}>${esc(c)}</option>`).join("");
  if (!who && characters.length) { who = characters[0]; $("#who").value = who; }
}
async function listCampaigns() {
  const { campaigns } = await api("/api/campaigns");
  $("#camp").innerHTML = campaigns.map((c) => `<option ${c === localStorage.getItem("sheets-camp") ? "selected" : ""}>${esc(c)}</option>`).join("") || `<option value="">(no campaign with a characters.md)</option>`;
  await listCast();
}
async function listCast() {
  const camp = $("#camp").value; castData = null;
  $("#cast").innerHTML = `<option value="">choose…</option>`;
  if (!camp) return;
  localStorage.setItem("sheets-camp", camp);
  try {
    castData = await api(`/api/campaigns/${encodeURIComponent(camp)}`);
    $("#cast").innerHTML = `<option value="">choose…</option>` + castData.characters.map((c, i) => `<option value="${i}">${esc(c.name)}</option>`).join("");
  } catch (err) { $("#top-hint").textContent = err.message; }
}
$("#camp").onchange = listCast;
$("#make").onclick = async () => {
  const c = castData?.characters[+$("#cast").value];
  if (!c) { $("#top-hint").textContent = "choose a character first"; return; }
  const name = c.name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40);
  try {
    await api("/api/characters", { method: "POST", body: { name } });
    await api(`/api/characters/${name}`, { method: "PUT", body: { description: `${c.name}: ${c.look}` } });
    who = name; current = null; lastDrawn = ""; await listWho(); await load(true);
    $("#top-hint").textContent = `${c.name}: description filled from ${castData.file}.`;
  } catch (err) { $("#top-hint").textContent = err.message; }
};
$("#who").onchange = async () => { if ($("#who").value) { who = $("#who").value; current = null; lastDrawn = ""; await load(true); } };

/* ---- load: redraw only when something changed, so nothing blinks ---- */
async function load(force) {
  if (!who) { $("#work").innerHTML = `<p class="hint">Choose a campaign and a character, then Start.</p>`; return; }
  st = await api(`/api/characters/${who}`);
  const key = JSON.stringify([st.stages, st.set, st.lock, st.lock_v, current]);
  if (force || key !== lastDrawn) { lastDrawn = key; draw(); }
  if (force) {
    $("#desc").value = st.description; $("#notes").value = st.notes || ""; $("#steps").value = st.steps_text;
    if (!$("#models").value) $("#models").value = localStorage.getItem("sheets-models") || DEFAULT_MODELS;
  }
  $("#top-hint").textContent = st.trigger ? `${who} · trigger word ${st.trigger}` : "";
  const busy = st.stages.some((s) => s.running);
  if (busy && !poll) poll = setInterval(load, 2500);
  if (!busy && poll) { clearInterval(poll); poll = null; }
}
function draw() {
  if (!st.stages.length) { $("#work").innerHTML = `<p class="hint">Open Setup on the left and write the description first.</p>`; $("#strip").innerHTML = ""; return; }
  if (!current || !st.stages.find((s) => s.id === current)) current = (st.stages.find((s) => !s.kept) || st.stages[st.stages.length - 1]).id;
  drawCaptured(); drawStrip(); drawStage();
}
/* ---- left: what is captured ---- */
function drawCaptured() {
  const lock = st.stages[0];
  $("#lock-box").innerHTML = lock.kept ? `<img src="${lock.kept}" title="the lock">` : `<div class="empty">no lock yet - roll it on the right</div>`;
  $("#kept-grid").innerHTML = st.stages.slice(1).map((s) => `<figure data-go="${esc(s.id)}" class="${s.kept ? "kept" : ""} ${s.id === current ? "now" : ""}">
    ${s.kept ? `<img src="${s.kept}">` : `<div class="todo">${s.n}</div>`}<figcaption title="${esc(s.title)}">${esc(s.title)}</figcaption></figure>`).join("");
  const done = st.stages.slice(1).filter((s) => s.kept).length;
  $("#set-hint").textContent = `${done} of ${st.stages.length - 1} steps kept${done ? ` · sheets/characters/${who}/set/` : ""}`;
}
$("#kept-grid").onclick = (e) => { const f = e.target.closest("figure[data-go]"); if (f) { current = f.dataset.go; lastDrawn = ""; draw(); } };
$("#lock-box").onclick = () => { current = "00-lock"; lastDrawn = ""; draw(); };
/* ---- right: the workspace ---- */
function drawStrip() {
  $("#strip").innerHTML = st.stages.map((s) => `<button data-go="${esc(s.id)}" class="${s.kept ? "kept" : ""} ${s.id === current ? "now" : ""}">${s.n === 0 ? "lock" : String(s.n).padStart(2, "0")}${s.running ? " …" : ""}</button>`).join("");
}
$("#strip").onclick = (e) => { const b = e.target.closest("button[data-go]"); if (b) { current = b.dataset.go; lastDrawn = ""; draw(); } };
function drawStage() {
  const s = st.stages.find((x) => x.id === current);
  const isLock = s.n === 0, rounds = s.rounds || [], pick = s.pick;
  const next = st.stages.find((x) => x.n > s.n && !x.kept);
  const prev = st.stages.find((x) => x.id === current) && st.stages[st.stages.indexOf(s) - 1];
  const parentImg = isLock ? null : (s.parent ? st.stages.find((x) => x.title === s.parent)?.kept : (st.stages.slice(0, st.stages.indexOf(s)).reverse().find((x) => x.kept)?.kept));
  const can = isLock || parentImg;
  $("#work").innerHTML = `
    <div class="stage-head">
      ${parentImg ? `<img src="${parentImg}" title="builds on this">` : s.kept && isLock ? `<img src="${s.kept}" title="the lock">` : ""}
      <div><h3><b>${isLock ? "lock" : String(s.n).padStart(2, "0")}</b>${esc(isLock ? "The lock" : s.title)}</h3>
        <div class="hint">${esc(s.instruction)}${!isLock ? ` · builds on ${esc(s.parent || "the previous keep")}` : ""}</div>
        ${s.kept ? `<div class="good" style="margin-top:.3rem">✓ kept${isLock ? " as the lock" : ""}. ${next ? `Next: <a href="#" id="go-next">${esc(next.n === 0 ? "lock" : next.title)}</a>.` : "Every step is kept."} Or roll again below to replace it.</div>` : ""}
        ${!can ? `<div class="err" style="margin-top:.3rem">Nothing to build on yet: ${s.parent ? `keep <b>${esc(s.parent)}</b> first` : "lock first"}.</div>` : ""}
      </div></div>
    ${rounds.map((r, i) => `<div class="roll ${i === rounds.length - 1 ? "now" : ""}">
      <div class="who"><b>roll ${i + 1}</b> ${r.from_pick ? "from your pick" : isLock ? "from the description" : "from the parent"}${r.notes ? ` · “${esc(r.notes)}”` : ""}${i === rounds.length - 1 && s.running ? ` <span class="working"></span>working…` : ""}</div>
      ${(r.errors || []).length ? `<div class="err">${r.errors.map(esc).join("<br>")}</div>` : ""}
      ${r.candidates.length ? `<div class="cands">${r.candidates.map((c) => `<figure data-round="${esc(r.round)}" data-file="${esc(c.file)}" class="${pick && pick.round === r.round && pick.file === c.file ? "pick" : ""}"><img src="${c.url}"><figcaption>${esc(c.model)}</figcaption></figure>`).join("")}</div>` : ""}
    </div>`).join("")}
    ${!rounds.length && can ? `<p class="hint">Roll: ${$("#models").value.split(",").filter(Boolean).length || 3} models, ${+$("#each").value || 2} each. Then click the closest, say what is off, and roll again from it until one is right.</p>` : ""}
    <div class="acts">
      <textarea id="stage-notes" rows="2" placeholder="${rounds.length ? "What is off in the closest one? Then roll again from it." : "Anything for this first roll (optional)."}">${esc(notesDraft[current] || "")}</textarea>
      <div class="row">
        <button class="go" id="roll" ${s.running || !can ? "disabled" : ""}>${rounds.length ? (pick ? "Roll again from the pick" : "Roll again") : "Roll"}</button>
        <button class="ok" id="keep" ${pick && !s.running ? "" : "disabled"}>${isLock ? "Lock this one" : "Keep this one"}</button>
        <span class="hint">${s.running ? "working…" : pick ? `closest: ${esc(pick.file)}` : rounds.length ? "click the closest candidate" : ""}</span>
      </div></div>`;
  $("#stage-notes").oninput = (e) => { notesDraft[current] = e.target.value; };
  $("#go-next")?.addEventListener("click", (e) => { e.preventDefault(); current = next.id; lastDrawn = ""; draw(); });
  $("#roll").onclick = async () => {
    try {
      await api(`/api/characters/${who}`, { method: "PUT", body: { description: $("#desc").value, notes: $("#notes").value } });
      await api(`/api/characters/${who}/stages/${current}/roll`, { method: "POST", body: { notes: $("#stage-notes").value, models: $("#models").value.split(",").map((m) => m.trim()).filter(Boolean), each: +$("#each").value || 2 } });
      notesDraft[current] = ""; await load(true);
    } catch (err) { $("#said").textContent = err.message; $("#top-hint").textContent = err.message; }
  };
  $("#keep").onclick = async () => {
    try {
      await api(`/api/characters/${who}/stages/${current}/keep`, { method: "POST", body: {} });
      const nxt = st.stages.find((x) => x.n > s.n && !x.kept);
      await load(true);
      if (nxt) { current = nxt.id; lastDrawn = ""; draw(); }
    } catch (err) { $("#top-hint").textContent = err.message; }
  };
}
$("#work").addEventListener("click", async (e) => {
  const fig = e.target.closest("figure[data-round]"); if (!fig) return;
  try { await api(`/api/characters/${who}/stages/${current}/pick`, { method: "POST", body: { round: fig.dataset.round, file: fig.dataset.file } }); await load(true); }
  catch (err) { $("#top-hint").textContent = err.message; }
});
/* ---- setup ---- */
$("#save").onclick = async () => {
  try {
    localStorage.setItem("sheets-models", $("#models").value);
    await api(`/api/characters/${who}`, { method: "PUT", body: { description: $("#desc").value, notes: $("#notes").value, steps_text: $("#steps").value } });
    $("#said").textContent = "saved"; lastDrawn = ""; await load(true);
  } catch (err) { $("#said").textContent = err.message; }
};
$("#lock-file").onchange = async (e) => {
  const f = e.target.files[0]; if (!f) return;
  const data_url = await new Promise((res) => { const r = new FileReader(); r.onload = () => res(r.result); r.readAsDataURL(f); });
  try { await api(`/api/characters/${who}/lock`, { method: "POST", body: { data_url } }); lastDrawn = ""; await load(true); }
  catch (err) { $("#said").textContent = err.message; }
};
$("#from-md").onclick = async () => {
  const { files } = await api("/api/md");
  $("#md-file").innerHTML = files.map((f) => `<option>${esc(f)}</option>`).join("") || "<option value=''>(no .md files found)</option>";
  $("#md").showModal(); showMd();
};
$("#md-file").onchange = showMd;
async function showMd() {
  const path = $("#md-file").value; if (!path) return;
  const d = await api(`/api/md?path=${encodeURIComponent(path)}`);
  $("#md-secs").innerHTML = d.sections.map((s, i) => `<div class="sec" data-i="${i}"><b>${"#".repeat(s.depth)} ${esc(s.heading)}</b><small>${esc(s.body.slice(0, 300))}</small></div>`).join("");
  $("#md-secs").onclick = (e) => { const el = e.target.closest(".sec"); if (!el) return; const s = d.sections[+el.dataset.i]; $("#desc").value = `${s.heading}: ${s.body}`; $("#md").close(); };
}
(async () => { await listCampaigns(); await listWho(); await load(true); if (st && !st.description) $("#setup").open = true; })();
</script></html>"""


# ---- the server -------------------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):   # quieter: the page polls
        if "GET /api/characters/" not in (args[0] if args else "") and "/files/" not in (args[0] if args else ""):
            super().log_message(fmt, *args)

    def send_json(self, data, code=200):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}") if n else {}

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(url.query)
        try:
            if url.path == "/":
                page = PAGE.replace("%MODELS%", json.dumps(",".join(core.DEFAULT_MODELS))).encode()
                self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(page))); self.end_headers(); self.wfile.write(page)
            elif url.path == "/api/characters":
                self.send_json({"characters": sorted(p.name for p in ROOT.iterdir() if p.is_dir() and re.fullmatch(r"[a-z0-9][a-z0-9_-]*", p.name))})
            elif url.path.startswith("/api/characters/"):
                self.send_json(status(url.path.split("/")[3]))
            elif url.path == "/api/md":
                self.send_json(md_read(q["path"][0]) if "path" in q else {"files": md_files()})
            elif url.path == "/api/campaigns":
                self.send_json({"campaigns": campaigns()})
            elif url.path.startswith("/api/campaigns/"):
                self.send_json(cast(urllib.parse.unquote(url.path.split("/")[3])))
            elif url.path.startswith("/files/"):
                rel = urllib.parse.unquote(url.path[len("/files/"):])
                p = (ROOT / rel).resolve()
                if ROOT not in p.parents or not p.is_file():
                    raise FileNotFoundError(rel)
                data = p.read_bytes()
                self.send_response(200); self.send_header("Content-Type", mimetypes.guess_type(str(p))[0] or "application/octet-stream")
                self.send_header("Content-Length", str(len(data))); self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(data)
            else:
                self.send_json({"error": "not found"}, 404)
        except FileNotFoundError as e:
            self.send_json({"error": f"not found: {e}"}, 404)
        except (ValueError, KeyError) as e:
            self.send_json({"error": str(e)}, 400)

    def do_POST(self):
        parts = self.path.split("?")[0].split("/")
        try:
            data = self.body()
            if self.path == "/api/characters":
                d = character(data.get("name", ""))
                d.mkdir(exist_ok=True)
                self.send_json({"ok": True, "name": d.name})
            elif len(parts) == 5 and parts[4] == "lock":
                head, _, b64 = data.get("data_url", "").partition(",")
                if "image/" not in head or not b64:
                    raise ValueError("expected an image")
                ext = head.split("image/")[1].split(";")[0].replace("jpeg", "jpg")
                d = character(parts[3])
                for old in d.glob("lock.*"):
                    old.unlink()
                (d / f"lock.{ext}").write_bytes(base64.b64decode(b64))
                self.send_json({"ok": True})
            elif len(parts) == 7 and parts[4] == "stages" and parts[6] == "roll":
                roll(parts[3], parts[5], (data.get("notes") or "").strip(), data.get("models") or core.DEFAULT_MODELS, int(data.get("each") or 2))
                self.send_json({"ok": True})
            elif len(parts) == 7 and parts[4] == "stages" and parts[6] == "pick":
                pick(parts[3], parts[5], data.get("round", ""), data.get("file", ""))
                self.send_json({"ok": True})
            elif len(parts) == 7 and parts[4] == "stages" and parts[6] == "keep":
                self.send_json({"kept": keep(parts[3], parts[5])})
            else:
                self.send_json({"error": "not found"}, 404)
        except FileNotFoundError as e:
            self.send_json({"error": f"not found: {e}"}, 404)
        except (ValueError, KeyError, SystemExit) as e:
            self.send_json({"error": str(e)}, 400)

    def do_PUT(self):
        parts = self.path.split("/")
        try:
            data = self.body()
            if len(parts) == 4 and parts[2] == "characters":
                d = character(parts[3])
                if not d.is_dir():
                    raise FileNotFoundError(parts[3])
                if "description" in data:
                    (d / "description.txt").write_text(data["description"].strip() + "\n")
                if "notes" in data:
                    (d / "notes.txt").write_text(data["notes"].strip() + "\n")
                if "steps_text" in data:
                    (d / "steps.txt").write_text(data["steps_text"].rstrip() + "\n")
                    core.read_steps(d / "steps.txt")     # complains now rather than at run time
                self.send_json({"ok": True})
            else:
                self.send_json({"error": "not found"}, 404)
        except FileNotFoundError as e:
            self.send_json({"error": f"not found: {e}"}, 404)
        except (ValueError, SystemExit) as e:
            self.send_json({"error": str(e)}, 400)


if __name__ == "__main__":
    ROOT.mkdir(parents=True, exist_ok=True)
    print(f"sheets: http://0.0.0.0:{PORT}  characters in {ROOT}  markdown from {', '.join(map(str, MD_ROOTS))}"
          + ("  (DRY: no model is called)" if DRY else ""), flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
