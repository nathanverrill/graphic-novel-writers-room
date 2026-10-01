"""Overnight: two full books, each rendered by two image models, with no one at the desk.

    python3 scripts/overnight.py            # against the running app on localhost:8000

1. Pre-production: wait for the canon update, approve it ("evoke").
2. Run 1, "edited" (campaign prosperity): edit mode, chapter 3 as key pages - development, the
   draft edit, the script from the edited drafts, layouts and fix rounds, packets.
3. Run 2, "room" (campaign prosperity-room, a copy of the approved canon with no key pages):
   improve mode - development, audition, the room's writer, layouts, packets. Runs alongside 1.
4. When both books are laid out and the locks are ready (a flag file, or 45 minutes), render
   every page of both with Gemini 3.1 Flash Image and GPT Image 2.5 Sunburst; failed pages are
   drawn once more.
5. Out: overnight/<date>/<run>/ - four PDFs (each model, art and lettered), the PNGs, the
   locks and style plate used, the script, layouts, change reports, the room's logs and this log.
"""
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "http://localhost:8000"
DAY = datetime.now().strftime("%Y-%m-%d")
OUT = ROOT / "overnight" / DAY
LOG = OUT / "overnight.log"
LOCKS_READY = OUT / "locks-ready"
RUNS = {"prosperity": "1-edited-with-key-pages", "prosperity-room": "2-room-judgment"}
TAGS = ("gemini", "sunburst")


def log(msg):
    OUT.mkdir(parents=True, exist_ok=True)
    line = f"{datetime.now().strftime('%H:%M:%S')}  {msg}"
    print(line, flush=True)
    with LOG.open("a") as f:
        f.write(line + "\n")


def call(method, path, body=None, timeout=120):
    req = urllib.request.Request(API + path, method=method, headers={"content-type": "application/json"},
                                 data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code} {e.read().decode()[:400]}"}
    except (urllib.error.URLError, TimeoutError) as e:
        return {"error": f"unreachable: {e}"}


def wait(what, check, every=20, limit=4 * 3600):
    """Poll until check() returns a truthy value; returns it."""
    t0 = time.time()
    while time.time() - t0 < limit:
        got = check()
        if got:
            return got
        time.sleep(every)
    log(f"gave up waiting for {what} after {limit // 60} minutes")
    return None


# ---- pre-production ----------------------------------------------------------------------------

def preproduction():
    def canon_done():
        p = call("GET", "/api/projects/prosperity")
        return None if p.get("active_run") else True
    wait("the canon update", canon_done)
    ready = call("GET", "/api/projects/prosperity/open-items").get("readiness", {})
    if not ready.get("ready"):
        log(f"pre-production not ready: {ready.get('why')} - running Update canon with a note")
        call("POST", "/api/projects/prosperity/open-items-feedback",
             {"feedback": "[LOW] Carry the rules as they stand, including Adrian's equation in rules/decisions.md."})
        call("POST", "/api/projects/prosperity/rounds", {"phase": "intake"})
        wait("the second canon update", canon_done)
        ready = call("GET", "/api/projects/prosperity/open-items").get("readiness", {})
    r = call("POST", "/api/projects/prosperity/phase", {"action": "approve_preproduction", "confirm": "evoke"})
    log(f"approve pre-production: {r.get('error') or 'approved, phase ' + str(r.get('phase'))}")


def copy_for_room():
    """prosperity-room: the approved canon and drafts, no key pages, no history, improve mode."""
    src, dst = ROOT / "campaigns" / "prosperity", ROOT / "campaigns" / "prosperity-room"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("renders", "previous", "keypages"))
    st = json.loads((dst / "production" / "round-settings.json").read_text())
    st.update(draft_mode="improve", writer=None, phase="development", scope=0, proof_page=None,
              magic={"status": "idle", "choices": [], "log": []})
    (dst / "production" / "round-settings.json").write_text(json.dumps(st, indent=2))
    for f in ("draft-edited.md", "draft-final.md", "draft-changes.md", "script.md", "layouts.md", "thumbnails.md"):
        (dst / "production" / f).unlink(missing_ok=True)
    log("prosperity-room: copied from the approved canon, improve mode, no key pages")


# ---- production ----------------------------------------------------------------------------------

def chain(slug, step, until):
    r = call("POST", f"/api/projects/{slug}/magic", {"step": step, "until": until})
    log(f"{slug}: {step} -> {until}: {r.get('error') or 'started'}")
    def done():
        m = call("GET", f"/api/projects/{slug}/magic")
        return m if m.get("status") not in ("running", None) else None
    m = wait(f"{slug} {step}->{until}", done, limit=5 * 3600)
    if m:
        log(f"{slug}: {step} -> {until} ended {m.get('status')}{': ' + m['error'] if m.get('error') else ''}")
        for line in (m.get("log") or [])[-6:]:
            log(f"    {line.get('text', '')[:200]}")
    return m


def run_edited():
    slug = "prosperity"
    call("PUT", f"/api/projects/{slug}/settings", {"draft_mode": "edit", "expand_pages": 0})
    m = chain(slug, "development", "drafts")
    if m and m.get("status") == "drafts":
        chain(slug, "audition", "final")


def run_room():
    chain("prosperity-room", "development", "final")


# ---- rendering ----------------------------------------------------------------------------------

def render(slug):
    r = call("POST", f"/api/projects/{slug}/render", {"models": list(TAGS)})
    log(f"{slug}: render {r.get('error') or 'started, ' + str(len(r.get('pages', []))) + ' pages'}")
    def done():
        s = call("GET", f"/api/projects/{slug}/render")
        st = s.get("state") or {}
        return s if all(st.get(t, {}).get("state") == "done" for t in TAGS) else None
    s = wait(f"{slug} render", done, every=30, limit=6 * 3600)
    failed = {t: [int(n) for n, p in (s or {}).get("state", {}).get(t, {}).get("pages", {}).items() if p.get("state") == "failed"] for t in TAGS}
    for t, pages in failed.items():
        if pages:
            log(f"{slug}: {t} failed on pages {pages}; drawing them once more")
            call("POST", f"/api/projects/{slug}/render", {"models": [t], "pages": pages, "redo": True})
    if any(failed.values()):
        wait(f"{slug} redraws", done, every=30, limit=2 * 3600)


def pdfs(slug):
    """Each version as a PDF, built in the app's container (it has Pillow)."""
    code = f"""
from pathlib import Path
from PIL import Image
base = Path('/app/campaigns/{slug}/renders')
for tag in {list(TAGS)!r}:
    for kind in ('art', 'lettered'):
        files = sorted((base / tag / kind).glob('p*.png'))
        if not files:
            continue
        pages = []
        for f in files:
            im = Image.open(f).convert('RGB')
            im.thumbnail((1400, 2100))
            pages.append(im)
        out = base / f'{slug}-{{tag}}-{{kind}}.pdf'
        pages[0].save(out, save_all=True, append_images=pages[1:], resolution=150, quality=85)
        print(out.name, len(pages))
"""
    r = subprocess.run(["docker", "compose", "exec", "-T", "app", "python", "-c", code], cwd=ROOT, capture_output=True, text=True)
    log(f"{slug}: PDFs {r.stdout.strip().replace(chr(10), ', ') or r.stderr.strip()[-300:]}")


def collect(slug):
    """Everything to look at and to diagnose from, in one folder per run."""
    out = OUT / RUNS[slug]
    camp = ROOT / "campaigns" / slug
    renders = camp / "renders"
    for tag in TAGS:
        for kind in ("art", "lettered"):
            src = renders / tag / kind
            if src.is_dir():
                shutil.copytree(src, out / "png" / f"{tag}-{kind}", dirs_exist_ok=True)
    for pdf in renders.glob("*.pdf"):
        shutil.copy2(pdf, out / pdf.name)
    (out / "logs").mkdir(parents=True, exist_ok=True)
    if (renders / "status.json").exists():
        shutil.copy2(renders / "status.json", out / "logs" / "render-status.json")
    for f in ("brief.md", "story.md", "characters.md", "world.md", "draft.md", "draft-edited.md", "draft-final.md",
              "draft-changes.md", "script.md", "layouts.md", "notes.md", "room-log.md", "page-prompts.md", "round-settings.json"):
        if (camp / "production" / f).exists():
            (out / "book").mkdir(parents=True, exist_ok=True)
            shutil.copy2(camp / "production" / f, out / "book" / f)
    if (camp / "keypages").is_dir():
        shutil.copytree(camp / "keypages", out / "keypages", dirs_exist_ok=True)
    sheets = ROOT / "sheets" / "characters"
    for tag in TAGS:
        for d in sorted(sheets.glob(f"*-{tag}")):
            for lock in d.glob("lock.*"):
                (out / "locks" / tag).mkdir(parents=True, exist_ok=True)
                shutil.copy2(lock, out / "locks" / tag / f"{d.name}{lock.suffix}")
    for plate in (sheets / "_style").glob("plate.*"):
        (out / "locks").mkdir(parents=True, exist_ok=True)
        shutil.copy2(plate, out / "locks" / f"style-plate{plate.suffix}")
    rounds = camp / "production" / "previous"
    if rounds.is_dir():
        for r in sorted(rounds.iterdir())[-12:]:           # the night's rounds: events, calls, what was written
            shutil.copytree(r, out / "logs" / "rounds" / r.name, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("images"))
    log(f"{slug}: collected into {out.relative_to(ROOT)}")


def index():
    lines = [f"# Overnight {DAY}", "",
             "Two books, each drawn by Gemini 3.1 Flash Image and GPT Image 2.5 Sunburst, as art and lettered.", ""]
    for slug, name in RUNS.items():
        d = OUT / name
        lines += [f"## {name}", "", f"campaign `{slug}`", ""]
        lines += [f"- `{p.name}`" for p in sorted(d.glob("*.pdf"))] or ["- (no PDFs - see overnight.log)"]
        st = d / "logs" / "render-status.json"
        if st.exists():
            s = json.loads(st.read_text())
            for tag, m in s.get("models", {}).items():
                ps = m.get("pages", {}).values()
                done = sum(1 for p in ps if p.get("state") == "done")
                cost = sum(p.get("cost") or 0 for p in ps)
                lines.append(f"- {tag}: {done} pages drawn, {sum(1 for p in ps if p.get('state') == 'failed')} failed, ${cost:.2f}")
        lines += ["", "Also here: `png/` (every page), `locks/` (the locks and style plate used), `book/` (brief, script, "
                  "layouts, change reports, room log), `logs/` (render status, the night's rounds).", ""]
    (OUT / "README.md").write_text("\n".join(lines))


def main():
    log("overnight: start")
    preproduction()
    copy_for_room()
    import threading
    runs = [threading.Thread(target=run_edited), threading.Thread(target=run_room)]
    for t in runs:
        t.start()
    for t in runs:
        t.join()
    log("both books laid out; waiting for the locks (flag file, or 45 minutes)")
    wait("the locks", lambda: LOCKS_READY.exists(), every=30, limit=45 * 60)
    renders = [threading.Thread(target=render, args=(s,)) for s in RUNS]
    for t in renders:
        t.start()
    for t in renders:
        t.join()
    for slug in RUNS:
        pdfs(slug)
        collect(slug)
    shutil.copy2(Path(__file__), OUT / "overnight.py")
    index()
    log("overnight: done - open overnight/" + DAY + "/README.md")


if __name__ == "__main__":
    main()
