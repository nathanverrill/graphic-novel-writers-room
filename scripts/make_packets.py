#!/usr/bin/env python3
"""make_packets.py - from the material to the page packets with no clicks.

    python3 scripts/make_packets.py prosperity
    python3 scripts/make_packets.py prosperity --model openai/gpt-5.6-luna --fresh --out ~/Desktop

Every default accepted: intake reads the material, the open items are answered with the room's
own suggestions, intake folds them in and is approved, and production runs to the layouts:
every page's map and panels, to look at on the production screen's Pages tab. --to final goes
on through the fix rounds to the packets, downloaded as a zip. Drawing the pages is yours.

--model puts every agent on that model (the provider and key the Script Coordinator uses).
--fresh starts intake over from the material instead of revising what is on the desk.
Standard library only; talks to a running room (--base, default http://localhost:8000)."""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://localhost:8000"


def api(path, body=None, method=None, raw=False):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"content-type": "application/json"},
                                 method=method or ("POST" if body is not None else "GET"))
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.read() if raw else json.load(r)
    except urllib.error.HTTPError as e:
        text = e.read().decode(errors="replace")
        try:
            text = json.loads(text).get("detail", text)
        except ValueError:
            pass
        sys.exit(f"{method or 'POST' if body is not None else 'GET'} {path}: HTTP {e.code}: {text}")


def say(text):
    print(time.strftime("%H:%M:%S"), text, flush=True)


def wait_round(slug, run_id, version, desk):
    """Until the run is done; a line per agent as they start and finish."""
    seen = set()
    while True:
        p = api(f"/api/projects/{slug}")
        done = p.get("active_run") != run_id
        try:
            ev = api(f"/api/projects/{slug}/versions/{version}/events?desk={desk}")
        except SystemExit:
            ev = {}
        for e in ev.get("events", []) if isinstance(ev, dict) else []:
            key = (e.get("i"), e.get("type"))
            if key in seen:
                continue
            seen.add(key)
            if e["type"] == "role_start":
                say(f"    {e.get('title', e.get('role'))} begins")
            elif e["type"] == "role_done":
                say(f"    {e.get('role')} done in {e.get('seconds', '?')}s")
            elif e["type"] in ("error", "warn"):
                say(f"    {e['type']}: {e.get('text', '')[:160]}")
        if done:
            return
        time.sleep(5)


def latest(slug, desk=None):
    p = api(f"/api/projects/{slug}" + (f"?desk={desk}" if desk else ""))
    return (p.get("versions") or [{}])[0]


def set_model(model):
    """Every agent on this model, with the Script Coordinator's provider and key."""
    roles = api("/api/agents")["roles"]
    ids = [r["id"] for r in roles]
    api("/api/agents/script_coordinator/settings", {"changes": {"model": model}}, "PUT")
    api("/api/agents/script_coordinator/apply-provider", {"roles": ids})
    say(f"every agent is on {model}")


def intake(slug, mode):
    r = api(f"/api/projects/{slug}/rounds", {"phase": "intake", "mode": mode})
    say(f"intake {mode or 'as the desk needs'}: round {r['version']}")
    wait_round(slug, r["run_id"], r["version"], "preproduction")
    v = latest(slug, "preproduction")
    if v.get("status") not in ("done", "awaiting_showrunner_decisions", "ready_for_review"):
        sys.exit(f"intake ended with status {v.get('status')!r}: see the pre-production desk")
    return v


def answer_all(slug):
    st = api(f"/api/projects/{slug}/open-items")
    n = 0
    for it in st["items"]:
        if it.get("decision") or it.get("defer"):
            continue
        opt = next((o for o in it["options"] if o["id"] == it.get("suggested")), None) or (it["options"] or [None])[0]
        if not opt:
            continue
        api(f"/api/projects/{slug}/open-items/{it['n']}", {"answer": opt["text"]})
        n += 1
    say(f"answered {n} open items with the room's suggestions")
    return n


def produce(slug, until):
    m = api(f"/api/projects/{slug}/magic")
    if m["status"] == "running" and m["active"]:
        sys.exit("production is already running")
    api(f"/api/projects/{slug}/magic", {"step": "development", "until": until})
    say("production: development → audition → writing → " + ("layouts" if until == "layouts" else "pages → final"))
    seen = 0
    last_run = None
    while True:
        m = api(f"/api/projects/{slug}/magic")
        for line in m["log"][seen:]:
            say(f"  ★ {line['text'][:200]}")
        seen = len(m["log"])
        p = api(f"/api/projects/{slug}")
        if p.get("active_run") and p["active_run"] != last_run:
            last_run = p["active_run"]
        if not m["active"] and m["status"] != "running":
            break
        time.sleep(10)
    if m["status"] not in ("done", "layouts"):
        sys.exit(f"production ended {m['status']}: {m.get('error') or 'see the production screen'}")


def main():
    global BASE
    ap = argparse.ArgumentParser(description="From the material to the page packets, every default accepted.")
    ap.add_argument("slug")
    ap.add_argument("--model", help="put every agent on this model (OpenRouter id, e.g. openai/gpt-5.6-luna)")
    ap.add_argument("--fresh", action="store_true", help="start intake over from the material")
    ap.add_argument("--skip-intake", action="store_true", help="the desk is already approved: just produce")
    ap.add_argument("--to", choices=["layouts", "final"], default="layouts",
                    help="layouts: stop at the page maps and panels (default). final: fix rounds and the packets zip")
    ap.add_argument("--out", default=".", help="where the packets zip goes (--to final)")
    ap.add_argument("--base", default=BASE)
    args = ap.parse_args()
    BASE = args.base.rstrip("/")
    slug = args.slug
    t0 = time.time()
    api(f"/api/projects/{slug}")
    if args.model:
        set_model(args.model)
    if not args.skip_intake:
        p = api(f"/api/projects/{slug}")
        if p.get("active_run"):
            sys.exit("the room is already working on this book")
        intake(slug, "synthesis" if args.fresh else None)
        if answer_all(slug):
            intake(slug, "revision")
        st = api(f"/api/projects/{slug}/open-items")
        if st["unresolved"]:
            say(f"  {st['unresolved']} item(s) still open after the revision - left for the room")
        if api(f"/api/projects/{slug}").get("phase") == "intake":
            api(f"/api/projects/{slug}/phase", {"action": "approve"})
            say("intake approved: production starts from its files")
    produce(slug, args.to)
    p = api(f"/api/projects/{slug}/prompts")
    if args.to == "layouts":
        say(f"done in {round((time.time() - t0) / 60)} min: {len(p['pages'])} pages laid out. "
            f"Look at them on {BASE}/production?p={slug}&tab=pages, then Make the pages (or run again with --to final).")
        return
    out = Path(args.out).expanduser() / f"{slug}-packets.zip"
    out.write_bytes(api(f"/api/projects/{slug}/packet.zip", raw=True))
    say(f"done in {round((time.time() - t0) / 60)} min: {len(p['pages'])} page packets → {out}")
    say("the book packet, the sheets, the script and the source files are inside; draw from those")


if __name__ == "__main__":
    main()
