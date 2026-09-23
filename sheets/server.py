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


def lock_state(d):
    f = d / "lock-rounds.json"
    return json.loads(f.read_text()) if f.exists() else {"rounds": [], "pick": None}


def save_lock_state(d, st):
    (d / "lock-rounds.json").write_text(json.dumps(st, indent=1))


def style_text():
    """The book's visual direction, if a brief is in reach: the first campaign's brief.md."""
    for root in MD_ROOTS:
        for b in sorted(root.glob("*/production/brief.md")) if root.is_dir() else []:
            m = re.search(r"^#+\s*.*(visual|style|look).*\n(.*?)(?=^#|\Z)", b.read_text(), re.S | re.M | re.I)
            if m:
                return " ".join(m.group(2).split())[:600]
    return None


def lock_roll(name, notes, models, each):
    """A round of lock candidates: from words alone the first time, then edits of the pick."""
    d = character(name)
    if not (d / "description.txt").exists():
        raise ValueError("write the description first")
    char = core.Character(d, need_lock=False)
    st = lock_state(d)
    pick = st.get("pick")
    parent = (d / "runs" / pick["round"] / pick["file"]) if pick else None
    if pick and not parent.exists():
        parent = None
    r = len(st["rounds"]) + 1
    step = f"lock-r{r}"
    prompt = core.lock_prompt(char, style_text(), notes, from_pick=parent is not None)
    key = "" if DRY else core.api_key()
    gen = core.fake if DRY else core.generate
    with _lock:
        if _running.get((name, "lock"), {}).get("status") == "running":
            raise ValueError("a lock round is already running")
        _running[(name, "lock")] = {"status": "running", "errors": []}
    st["rounds"].append({"round": f"00-{step}", "notes": notes or "", "parent": parent.name if parent else None, "candidates": [], "errors": []})
    save_lock_state(d, st)

    def work():
        try:
            folder, cands, errors = core.make_candidates(char, 0, step, prompt, parent, models, each, gen, key, say=lambda m: None)
            st2 = lock_state(d)
            st2["rounds"][-1].update(candidates=[{"model": m, "file": p.name} for m, p in cands], errors=errors)
            save_lock_state(d, st2)
            _running[(name, "lock")] = {"status": "done" if cands else "failed", "errors": errors}
        except Exception as e:      # noqa: BLE001
            _running[(name, "lock")] = {"status": "failed", "errors": [str(e)[:300]]}
    threading.Thread(target=work, daemon=True).start()


def lock_pick(name, round_name, file):
    d = character(name)
    st = lock_state(d)
    if not (d / "runs" / round_name / file).exists():
        raise ValueError("no such candidate")
    st["pick"] = {"round": round_name, "file": file}
    save_lock_state(d, st)


def lock_accept(name):
    """The pick becomes lock.png: the starting view every step builds from."""
    d = character(name)
    st = lock_state(d)
    if not st.get("pick"):
        raise ValueError("pick the closest candidate first")
    src = d / "runs" / st["pick"]["round"] / st["pick"]["file"]
    for old in d.glob("lock.*"):
        old.unlink()
    dst = d / f"lock{src.suffix}"
    dst.write_bytes(src.read_bytes())
    core.Character(d).log(step="lock", model=None, parent=None, candidate=str(src.relative_to(d)), picked=True, kept=dst.name)
    return dst.name


def status(name):
    """Everything the page shows for one character."""
    d = character(name)
    desc = (d / "description.txt").read_text() if (d / "description.txt").exists() else ""
    notes = (d / "notes.txt").read_text() if (d / "notes.txt").exists() else ""
    steps_file = d / "steps.txt"
    steps_text = steps_file.read_text() if steps_file.exists() else (core.HERE / "steps.txt").read_text()
    lock = next((p.name for p in d.glob("lock.*")), None)
    char = load(name, need=False)
    lk = lock_state(d)
    live = _running.get((name, "lock"), {})
    out = {"name": name, "description": desc, "notes": notes, "steps_text": steps_text, "lock": lock, "ready": bool(char),
           "trigger": char.trigger if char else None, "steps": [], "kept": [],
           "lock_rounds": [dict(r, candidates=[dict(c, url=f"/files/{name}/runs/{r['round']}/{c['file']}") for c in r["candidates"]])
                           for r in lk["rounds"]],
           "lock_pick": lk.get("pick"), "lock_running": live.get("status") == "running",
           "lock_errors": live.get("errors") or []}
    steps = core.read_steps(steps_file if steps_file.exists() else core.HERE / "steps.txt")
    for n, (step, instruction, parent) in enumerate(steps, 1):
        folder = d / "runs" / f"{n:02d}-{step}"
        run = json.loads((folder / "step.json").read_text()) if (folder / "step.json").exists() else None
        kept = next((p.name for p in (d / "set").glob(f"{n:02d}-{step}.*") if p.suffix != ".txt"), None) if (d / "set").is_dir() else None
        live = _running.get((name, step), {})
        out["steps"].append({"n": n, "step": step, "instruction": instruction, "parent": parent or "previous pick",
                             "kept": kept, "running": live.get("status") == "running",
                             "failed": live.get("status") == "failed", "errors": (run or {}).get("errors") or live.get("errors") or [],
                             "candidates": [dict(c, url=f"/files/{name}/runs/{folder.name}/{c['file']}") for c in (run or {}).get("candidates", [])]})
    if (d / "set").is_dir():
        for p in sorted(d / "set" for _ in [0])[0].iterdir():
            if p.suffix != ".txt":
                cap = p.with_suffix(".txt")
                out["kept"].append({"file": p.name, "url": f"/files/{name}/set/{p.name}",
                                    "caption": cap.read_text().strip() if cap.exists() else ""})
    return out


def run_in_thread(name, step_name, models, each):
    char = load(name)
    if not char:
        raise ValueError("needs description.txt and lock.png first")
    steps = {s: (n, i, p) for n, (s, i, p) in enumerate(char.steps, 1)}
    if step_name not in steps:
        raise ValueError(f"no step {step_name!r}")
    n, instruction, parent_name = steps[step_name]
    # the parent: the named step's pick, or the nearest earlier pick, or the lock
    if parent_name:
        parent = char.pick_of(parent_name)
        if parent is None:
            raise ValueError(f"step {parent_name!r} has no pick yet")
    else:
        parent = char.lock
        for s, (k, _, _) in steps.items():
            if k < n and char.pick_of(s):
                parent = char.pick_of(s)
    key = "" if DRY else core.api_key()
    gen = core.fake if DRY else core.generate
    with _lock:
        if _running.get((name, step_name), {}).get("status") == "running":
            raise ValueError("that step is already running")
        _running[(name, step_name)] = {"status": "running", "errors": []}

    def work():
        try:
            _, cands, errors = core.make_candidates(char, n, step_name, instruction, parent, models, each, gen, key, say=lambda m: None)
            _running[(name, step_name)] = {"status": "done" if cands else "failed", "errors": errors}
        except Exception as e:      # noqa: BLE001
            _running[(name, step_name)] = {"status": "failed", "errors": [str(e)[:300]]}
    threading.Thread(target=work, daemon=True).start()


def keep(name, step_name, file):
    char = load(name)
    steps = {s: (n, i, p) for n, (s, i, p) in enumerate(char.steps, 1)}
    n, instruction, _ = steps[step_name]
    folder = char.dir / "runs" / f"{n:02d}-{step_name}"
    run = json.loads((folder / "step.json").read_text())
    cand = next((c for c in run["candidates"] if c["file"] == file), None)
    if not cand:
        raise ValueError("no such candidate")
    parent = Path(run["parent"])
    kept = core.keep(char, n, step_name, instruction, parent, cand["model"], folder / file)
    return kept.name


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
header{display:flex;gap:1rem;align-items:center;padding:.7rem 1rem;border-bottom:1px solid var(--line)}
header h1{font-size:1rem;margin:0}header select,header input,header button{font:inherit;padding:.3rem .5rem;background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:4px}
main{display:grid;grid-template-columns:minmax(18rem,26rem) 1fr;gap:1rem;padding:1rem}
@media(max-width:60rem){main{grid-template-columns:1fr}}
.card{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:.8rem;margin-bottom:1rem}
.card h2{font-size:.85rem;margin:0 0 .5rem;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
textarea,input[type=text]{width:100%;box-sizing:border-box;font:inherit;font-size:.82rem;background:var(--bg);color:var(--ink);border:1px solid var(--line);border-radius:4px;padding:.4rem}
textarea.mono{font-family:ui-monospace,monospace;min-height:12rem}
button{font:inherit;padding:.35rem .7rem;border:1px solid var(--line);border-radius:4px;background:var(--panel);color:var(--ink);cursor:pointer}
button.go{background:var(--go);border-color:var(--go)}button:disabled{opacity:.5;cursor:default}
.hint{color:var(--muted);font-size:.78rem}.row{display:flex;gap:.5rem;align-items:center;flex-wrap:wrap;margin:.4rem 0}
.lock img{max-width:100%;border-radius:4px;border:1px solid var(--line)}
.step{border:1px solid var(--line);border-radius:6px;padding:.6rem .8rem;margin-bottom:.6rem}
.step.kept{border-color:var(--ok)}.step.now{border-color:var(--go)}.step b{font-family:ui-monospace,monospace}
.cands{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:.6rem;margin-top:.6rem}
.cands figure{margin:0;background:var(--bg);padding:.3rem;border-radius:4px;cursor:pointer;border:2px solid transparent}
.cands figure:hover{border-color:var(--go)}.cands figure.kept{border-color:var(--ok)}
.cands img{width:100%;border-radius:3px}.cands figcaption{font-size:.7rem;color:var(--muted);margin-top:.2rem;word-break:break-all}
.set{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:.4rem}.set img{width:100%;border-radius:3px}
.err{color:var(--bad);font-size:.76rem}.ok{color:var(--ok)}
dialog{background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:6px;width:min(720px,92vw);max-height:80vh}
dialog .sec{padding:.4rem .5rem;border-bottom:1px solid var(--line);cursor:pointer}dialog .sec:hover{background:var(--bg)}
dialog .sec small{color:var(--muted);display:block;white-space:pre-wrap;max-height:4.5em;overflow:hidden}
</style>
<header><h1>Sheets</h1>
  <label class="hint">campaign <select id="camp"></select></label>
  <label class="hint">character <select id="cast"><option value="">choose…</option></select></label>
  <button id="make" class="go">Start this character</button>
  <span class="hint">· or open</span><select id="who"></select>
  <span class="hint" id="top-hint">A LoRA training set, one character at a time.</span></header>
<main>
<aside>
  <div class="card"><h2>Description</h2>
    <textarea id="desc" rows="8" placeholder="The character's look, from characters.md - or paste your own."></textarea>
    <div class="row"><button id="from-md">From another .md file…</button><span class="hint">world.md, a reference, anything under campaigns/</span></div></div>
  <div class="card"><h2>Notes</h2>
    <textarea id="notes" rows="3" placeholder="Anything more for every step: 'always the burn scar on the left hand', 'never a hat'."></textarea>
    <p class="hint" style="margin:.3rem 0 0">Goes into every prompt after the description.</p></div>
  <div class="card lock"><h2>Lock: the approved starting view</h2>
    <div id="lock-img"></div>
    <div class="row"><label><input type="file" id="lock-file" accept="image/*" hidden><button onclick="document.getElementById('lock-file').click()">Upload one instead</button></label>
      <span class="hint">or build it on the right: roll, pick the closest, note what is off, roll again, lock.</span></div></div>
  <div class="card"><h2>Steps</h2>
    <textarea id="steps" class="mono" spellcheck="false"></textarea>
    <p class="hint" style="margin:.3rem 0 0">One per line: <code>name | what to change | parent</code>. Parent is a step name or <code>lock</code>; leave it out to build on the previous pick.</p></div>
  <div class="card"><h2>Models</h2>
    <input id="models" type="text"><div class="row"><span class="hint">comma-separated OpenRouter image models ·</span><label class="hint">each <input id="each" type="number" min="1" max="4" value="2" style="width:3rem"></label></div>
    <div class="row"><button class="go" id="save">Save</button><span class="hint" id="said"></span></div></div>
</aside>
<section>
  <div class="card" id="lock-card"><h2>Lock it first</h2><div id="lock-view"></div></div>
  <div class="card"><h2>Then the steps</h2><div id="steps-view"></div></div>
  <div class="card"><h2>The set so far</h2><div class="set" id="set"></div><p class="hint" id="set-hint"></p></div>
</section>
</main>
<dialog id="md"><div class="row"><select id="md-file" style="flex:1"></select><button onclick="document.getElementById('md').close()">close</button></div>
  <p class="hint">Click a section to use it as the description.</p><div id="md-secs"></div></dialog>
<script>
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const DEFAULT_MODELS = %MODELS%;
let who = null, st = null, poll = null, castData = null;
async function api(path, opts = {}) {
  const r = await fetch(path, { method: opts.method || "GET", headers: { "content-type": "application/json" }, body: opts.body ? JSON.stringify(opts.body) : undefined });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.error || r.statusText);
  return d;
}
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
    $("#top-hint").textContent = `${castData.characters.length} characters in ${castData.file}`;
  } catch (err) { $("#top-hint").textContent = err.message; }
}
$("#camp").onchange = listCast;
async function load() {
  if (!who) { $("#steps-view").innerHTML = `<p class="hint">Make a character to begin.</p>`; return; }
  st = await api(`/api/characters/${who}`);
  if (document.activeElement !== $("#desc")) $("#desc").value = st.description;
  if (document.activeElement !== $("#notes")) $("#notes").value = st.notes || "";
  if (document.activeElement !== $("#steps")) $("#steps").value = st.steps_text;
  if (!$("#models").value) $("#models").value = localStorage.getItem("sheets-models") || DEFAULT_MODELS;
  $("#lock-img").innerHTML = st.lock ? `<img src="/files/${who}/${esc(st.lock)}?t=${Date.now()}">` : `<p class="hint">No lock yet. Generate the front view elsewhere, approve it by eye, upload it here.</p>`;
  $("#top-hint").textContent = st.ready ? `trigger word: ${st.trigger}` : "needs a description and a lock image";
  renderLock(); renderSteps(); renderSet();
  const busy = st.steps.some((s) => s.running) || st.lock_running;
  if (busy && !poll) poll = setInterval(load, 2500);
  if (!busy && poll) { clearInterval(poll); poll = null; }
}
function renderLock() {
  const rounds = st.lock_rounds || [], pick = st.lock_pick;
  const last = rounds[rounds.length - 1];
  const notesBox = `<textarea id="lock-notes" rows="2" placeholder="${rounds.length ? "What is off in the closest one? 'hair shorter', 'coveralls not a jacket', 'older'." : "Anything for this first roll (optional)."}"></textarea>`;
  $("#lock-view").innerHTML = `
    ${st.lock ? `<p class="ok">Locked: ${esc(st.lock)}. Roll again to replace it, or go on to the steps.</p>` : ""}
    ${rounds.map((r, i) => `<div class="step ${i === rounds.length - 1 ? "now" : ""}">
      <div class="row" style="justify-content:space-between"><span><b>roll ${i + 1}</b> ${r.parent ? `<span class="hint">edited from ${esc(r.parent)}</span>` : `<span class="hint">from the description</span>`}${r.notes ? ` · ${esc(r.notes)}` : ""}</span>
        ${i === rounds.length - 1 && st.lock_running ? `<span class="hint">working…</span>` : ""}</div>
      ${(r.errors || []).length ? `<div class="err">${r.errors.map(esc).join("<br>")}</div>` : ""}
      ${r.candidates.length ? `<div class="cands">${r.candidates.map((c) => `<figure data-lock-round="${esc(r.round)}" data-file="${esc(c.file)}" class="${pick && pick.round === r.round && pick.file === c.file ? "kept" : ""}"><img src="${c.url}"><figcaption>${esc(c.model)}</figcaption></figure>`).join("")}</div>` : ""}
    </div>`).join("")}
    ${st.lock_errors.length && !last ? `<div class="err">${st.lock_errors.map(esc).join("<br>")}</div>` : ""}
    <div class="row">${notesBox}</div>
    <div class="row">
      <button class="go" id="lock-roll" ${st.lock_running || !st.description ? "disabled" : ""}>${rounds.length ? (pick ? "Roll again from the pick" : "Roll again") : "Roll the first candidates"}</button>
      <button id="lock-accept" ${pick && !st.lock_running ? "" : "disabled"}>Lock this one →</button>
      <span class="hint">${pick ? `closest so far: ${esc(pick.file)} (${esc(pick.round)})` : rounds.length ? "click the closest candidate" : "six candidates from three models, from the description alone"}</span>
    </div>`;
  $("#lock-roll").onclick = async () => {
    try {
      await api(`/api/characters/${who}`, { method: "PUT", body: { description: $("#desc").value, notes: $("#notes").value } });
      await api(`/api/characters/${who}/lock/roll`, { method: "POST", body: { notes: $("#lock-notes").value, models: $("#models").value.split(",").map((m) => m.trim()).filter(Boolean), each: +$("#each").value || 2 } });
      await load();
    } catch (err) { $("#said").textContent = err.message; }
  };
  $("#lock-accept").onclick = async () => {
    try { await api(`/api/characters/${who}/lock/accept`, { method: "POST", body: {} }); await load(); }
    catch (err) { $("#said").textContent = err.message; }
  };
}
$("#lock-view").addEventListener("click", async (e) => {
  const fig = e.target.closest("figure[data-lock-round]"); if (!fig) return;
  try { await api(`/api/characters/${who}/lock/pick`, { method: "POST", body: { round: fig.dataset.lockRound, file: fig.dataset.file } }); await load(); }
  catch (err) { $("#said").textContent = err.message; }
});
function renderSteps() {
  const next = st.steps.find((s) => !s.kept);
  $("#steps-view").innerHTML = st.steps.map((s) => `
    <div class="step ${s.kept ? "kept" : ""} ${s === next ? "now" : ""}">
      <div class="row" style="justify-content:space-between"><span><b>${String(s.n).padStart(2, "0")} ${esc(s.step)}</b> · ${esc(s.instruction)} <span class="hint">from ${esc(s.parent)}</span></span>
        <span>${s.kept ? `<span class="ok">kept ${esc(s.kept)}</span> ` : ""}<button data-run="${esc(s.step)}" ${s.running || !st.ready ? "disabled" : ""}>${s.running ? "working…" : s.candidates.length ? "Again" : "Run"}</button></span></div>
      ${s.errors.length ? `<div class="err">${s.errors.map(esc).join("<br>")}</div>` : ""}
      ${s.candidates.length ? `<div class="cands">${s.candidates.map((c) => `<figure data-keep="${esc(s.step)}" data-file="${esc(c.file)}" class="${s.kept && s.kept.replace(/\.[^.]+$/, "") === s.kept?.replace(/\.[^.]+$/, "") && c.picked ? "kept" : ""}"><img src="${c.url}?t=${Date.now()}"><figcaption>${esc(c.model)}</figcaption></figure>`).join("")}</div>
        <p class="hint" style="margin:.3rem 0 0">Click the one to keep: same face, same clothes, same proportions as the parent.</p>` : ""}
    </div>`).join("");
}
function renderSet() {
  $("#set").innerHTML = st.kept.map((k) => `<figure style="margin:0"><img src="${k.url}" title="${esc(k.caption)}"><figcaption class="hint" style="font-size:.66rem">${esc(k.file)}</figcaption></figure>`).join("");
  $("#set-hint").textContent = st.kept.length ? `${st.kept.length} images with captions in sheets/${who}/set/. That folder is the training set.` : "Nothing kept yet.";
}
$("#steps-view").addEventListener("click", async (e) => {
  const run = e.target.closest("button[data-run]"), fig = e.target.closest("figure[data-keep]");
  try {
    if (run) {
      run.disabled = true; run.textContent = "working…";
      await api(`/api/characters/${who}/steps/${run.dataset.run}/run`, { method: "POST", body: { models: $("#models").value.split(",").map((m) => m.trim()).filter(Boolean), each: +$("#each").value || 2 } });
      await load();
    } else if (fig) {
      await api(`/api/characters/${who}/steps/${fig.dataset.keep}/keep`, { method: "POST", body: { file: fig.dataset.file } });
      await load();
    }
  } catch (err) { $("#said").textContent = err.message; await load(); }
});
$("#save").onclick = async () => {
  try {
    localStorage.setItem("sheets-models", $("#models").value);
    await api(`/api/characters/${who}`, { method: "PUT", body: { description: $("#desc").value, notes: $("#notes").value, steps_text: $("#steps").value } });
    $("#said").textContent = "saved"; await load();
  } catch (err) { $("#said").textContent = err.message; }
};
$("#lock-file").onchange = async (e) => {
  const f = e.target.files[0]; if (!f) return;
  const data_url = await new Promise((res) => { const r = new FileReader(); r.onload = () => res(r.result); r.readAsDataURL(f); });
  try { await api(`/api/characters/${who}/lock`, { method: "POST", body: { data_url } }); await load(); }
  catch (err) { $("#said").textContent = err.message; }
};
$("#make").onclick = async () => {
  const c = castData?.characters[+$("#cast").value];
  if (!c) { $("#top-hint").textContent = "choose a character first"; return; }
  const name = c.name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40);
  try {
    await api("/api/characters", { method: "POST", body: { name } });
    await api(`/api/characters/${name}`, { method: "PUT", body: { description: `${c.name}: ${c.look}` } });
    who = name; await listWho(); await load();
    $("#top-hint").textContent = `${c.name}: description filled from ${castData.file}. Upload the lock, then run the steps.`;
  } catch (err) { $("#top-hint").textContent = err.message; }
};
$("#who").onchange = async () => { if ($("#who").value) { who = $("#who").value; await load(); } };
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
(async () => { await listCampaigns(); await listWho(); await load(); })();
</script></html>"""


# ---- the server -------------------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):   # quieter
        if "/api/characters/" not in (args[0] if args else ""):
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
            elif len(parts) == 6 and parts[4] == "lock" and parts[5] == "roll":
                lock_roll(parts[3], (data.get("notes") or "").strip(), data.get("models") or core.DEFAULT_MODELS, int(data.get("each") or 2))
                self.send_json({"ok": True})
            elif len(parts) == 6 and parts[4] == "lock" and parts[5] == "pick":
                lock_pick(parts[3], data.get("round", ""), data.get("file", ""))
                self.send_json({"ok": True})
            elif len(parts) == 6 and parts[4] == "lock" and parts[5] == "accept":
                self.send_json({"lock": lock_accept(parts[3])})
            elif len(parts) == 7 and parts[4] == "steps" and parts[6] == "run":
                run_in_thread(parts[3], parts[5], data.get("models") or core.DEFAULT_MODELS, int(data.get("each") or 2))
                self.send_json({"ok": True})
            elif len(parts) == 7 and parts[4] == "steps" and parts[6] == "keep":
                self.send_json({"kept": keep(parts[3], parts[5], data.get("file", ""))})
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
