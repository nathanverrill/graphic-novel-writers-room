"""Production, run all the way: the room takes every gate, the showrunner sees finished work.

The phases (app/phases.py) each stop for the showrunner. This runs them back to back and
takes the decisions itself:

    development   Director, then Plotter and Character Designer side by side, then Continuity
    audition      Writer A and Writer B side by side; the First Reader's reaction picks the writer
    page1         the proof: execution on one page only (page 1, or proof_page), from the script
                  -> only when asked for (until="page1"): a cheap look at the book before the rest
    writing       the picked writer writes the whole book
    layouts       one pass of the Layout Agent alone: the page maps and panel definitions
                  -> the default stop: look at the pages before the long part
    execution     layouts, round after round, until the readiness gate passes; then the packets
    final         the book is finalized: the page packets are the deliverable

"Produce" runs development to the layouts stop. "Make the pages" runs on to final. The page 1 proof is there for a
showrunner who wants to see the look first; a chain running to final skips it, because the
whole book's pages are made right after the writing anyway.

Lettering is not in the chain. It comes after the pages are drawn from the packets, as its own
phase, over the uploaded art (phases.json, "lettering").

Every choice the room makes for the showrunner is written down (choices), with the round it
was made in, so it can be seen and stepped back to. Stepping back is start(slug, step, note):
the chain is re-entered at that step, with the note, and runs on from there. Nothing before
the step is rerun.

State lives in round-settings.json under "magic", so it survives a restart of the app and the
production page can read it with the rest of the project.
"""
import re
import threading
import time

from . import notes as notes_mod, phases, projects, review, room
from .agents import load_roles

STEPS = ("development", "drafts", "audition", "page1", "writing", "layouts", "execution", "final")
PHASE_OF = {"development": "development", "drafts": "drafts", "audition": "audition", "page1": "execution",
            "writing": "writing", "layouts": "execution", "execution": "execution", "final": "execution"}
TITLES = {"development": "Development", "drafts": "Draft edit", "audition": "Audition", "page1": "Proof page",
          "writing": "Writing", "layouts": "Layouts", "execution": "Pages", "final": "Final"}
STOPS = {"drafts": "drafts", "page1": "page1", "layouts": "layouts", "final": "final"}    # a chain ends here and waits for the showrunner

def chapter_pages(slug):
    """[{chapter, title, first, pages}]: where each chapter starts in the book, for the proof picker.

    An edit of the drafts counts its own chapters (the pages table in draft-changes.md); otherwise
    the page plot in story.md numbers every page under its chapter heading."""
    if phases.editing(slug):
        rows = re.findall(r"^\|\s*(chapter-(\d+)[^|]*?)\s*\|[^|]*\|[^|]*\|[^|]*\|\s*\**(\d+)\**\s*\|\s*$",
                          projects.read_artifact(slug, "draft-changes.md") or "", re.M)
        if rows:
            out, first = [], 1
            for name, n, pages in rows:
                out.append({"chapter": int(n), "title": name, "first": first, "pages": int(pages)})
                first += int(pages)
            return out
    # the Plotter writes pages either through the whole book ("**Page 33:**") or within each
    # chapter ("#### Page 1", "Pages 5-6"); a chapter whose pages start again at 1 is the second kind
    text = projects.read_artifact(slug, "story.md") or ""
    out, after = [], 0
    for m in re.finditer(r"^#{2,3}\s+Chapter\s+(\d+)\b[^\n]*\n(.*?)(?=^#{2,3}\s|\Z)", text, re.M | re.S | re.I):
        nums = []
        for a, b in re.findall(r"^\s*(?:#{1,6}\s*|\*\*)?Pages?\s+(\d+)(?:\s*[\u2013\u2014-]\s*(\d+))?", m.group(2), re.M | re.I):
            nums += [int(a), int(b or a)]
        if not nums:
            continue
        low, high = min(nums), max(nums)
        first = low if low > after else after + 1
        title = m.group(0).split("\n", 1)[0].lstrip("# ").strip()
        out.append({"chapter": int(m.group(1)), "title": title, "first": first, "pages": high - low + 1})
        after = first + high - low
    return out


def max_execution_rounds(slug):
    """Rounds of pages before the book is taken as it is (the execution_rounds setting)."""
    return max(1, int(review.settings(slug).get("execution_rounds") or 2))

_threads = {}
_lock = threading.Lock()


# ---- state -------------------------------------------------------------------------

def state(slug):
    st = review.settings(slug).get("magic") or {}
    return {"status": st.get("status", "idle"),      # idle | running | page1 | done | stopped | failed
            "step": st.get("step"), "until": st.get("until"),
            "choices": st.get("choices", []), "log": st.get("log", []),
            "error": st.get("error"), "started": st.get("started"), "finished": st.get("finished"),
            "active": bool(_threads.get(slug) and _threads[slug].is_alive())}


def _set(slug, **changes):
    with _lock:
        st = review.settings(slug).get("magic") or {}
        st.update(changes)
        review.save_settings(slug, magic=st)
    return st


def _log(slug, text):
    with _lock:
        st = review.settings(slug).get("magic") or {}
        st.setdefault("log", []).append({"t": time.time(), "text": text})
        st["log"] = st["log"][-200:]
        review.save_settings(slug, magic=st)


def _choice(slug, step, what, why, rnd):
    with _lock:
        st = review.settings(slug).get("magic") or {}
        st.setdefault("choices", []).append({"t": time.time(), "step": step, "what": what, "why": why, "round": rnd})
        review.save_settings(slug, magic=st)


class Halted(Exception):
    pass


def close_stale(slug):
    """At startup: a chain the record says is running cannot be - the process it ran in is
    gone. Say so, rather than showing "working" forever."""
    st = review.settings(slug).get("magic") or {}
    if st.get("status") == "running" and not state(slug)["active"]:
        _set(slug, status="failed", finished=projects.now(),
             error="The app restarted while the room was working. Resume picks up at that step.")
        _log(slug, f"The app restarted during {TITLES.get(st.get('step'), st.get('step') or 'the run')}. Resume to go on.")
        return True
    return False


# ---- the chain ------------------------------------------------------------------------

def start(slug, step="development", note=None, until="final"):
    """Run the chain from `step` to `until` (a stop: page1 or final) in a thread."""
    if step not in STEPS or until not in STOPS:
        raise ValueError(f"step must be one of {', '.join(STEPS)} and until one of {', '.join(STOPS)}")
    if STEPS.index(until) < STEPS.index(step):
        raise ValueError(f"{until} comes before {step}")
    if room.active_run(slug) or state(slug)["active"]:
        raise RuntimeError("the room is already working on this project")
    if not (projects.read_artifact(slug, "story.md", desk=projects.PRE) or "").strip():
        raise ValueError("there is no story.md yet - run pre-production first")
    _set(slug, status="running", step=step, until=until, error=None, stop=False,
         started=projects.now(), finished=None)
    if step == "development":
        _set(slug, choices=[], log=[])
    if STEPS.index(step) <= STEPS.index("page1"):
        _set(slug, written_for_page1=False)     # a chain that reaches page 1 again writes again
    _log(slug, f"Production starts at {TITLES[step]}, running to {TITLES[until].lower()}."
               + (f" With your note: {note[:120]}" if note else ""))
    t = threading.Thread(target=_run, args=(slug, step, until, note), daemon=True)
    _threads[slug] = t
    t.start()
    return state(slug)


def stop(slug):
    _set(slug, stop=True)
    run = room.active_run(slug)
    if run:
        run.stop_requested = True
        with run.cond:
            run.cond.notify_all()
    return state(slug)


def _stopping(slug):
    return bool((review.settings(slug).get("magic") or {}).get("stop"))


def _run(slug, step, until, note):
    try:
        i = STEPS.index(step)
        while True:
            step = STEPS[i]
            _set(slug, step=step)
            if _stopping(slug):
                raise Halted()
            if step == "drafts" and not phases.editing(slug):
                i += 1                  # only an edit of the showrunner's drafts has a draft edit
                continue
            if step == "page1" and until != "page1":
                i += 1                  # no proof asked for: straight on to the writing
                continue
            if step == "layouts" and until != "layouts":
                i += 1                  # not stopping there: the pages step lays out and fixes
                continue
            note = {"development": _development, "drafts": _drafts, "audition": _audition, "page1": _page1,
                    "writing": _writing, "layouts": _layouts, "execution": _execution, "final": _final}[step](slug, note)
            if step == until or step == "drafts":     # an edit always stops at the edited drafts
                break
            i += 1
        if step == "drafts":
            _set(slug, status="drafts", finished=projects.now())
            _log(slug, "Your drafts are edited to the canon: every change and everything that does not fit "
                       "is in draft-changes.md. Read them, then script them - or stop here.")
        elif until == "page1":
            _set(slug, status="page1", finished=projects.now())
            _log(slug, f"The proof, page {review.proof_page(slug)}, is ready. Have a look: is this about right?")
        elif until == "layouts":
            _set(slug, status="layouts", finished=projects.now())
            _log(slug, "The layouts are drawn: every page's map and panels. Look them over, then Make the pages.")
        else:
            _set(slug, status="done", finished=projects.now())
            _log(slug, "The book is done. The page packets are ready to paste into an image model; "
                       "upload the art it draws and run the lettering.")
    except Halted:
        _set(slug, status="stopped", finished=projects.now())
        _log(slug, "Stopped.")
    except Exception as e:      # noqa: BLE001 - whatever failed, the chain must say so and end
        _set(slug, status="failed", error=f"{type(e).__name__}: {e}"[:400], finished=projects.now())
        _log(slug, f"Failed at {TITLES.get(step, step).lower()}: {type(e).__name__}: {str(e)[:200]}")


def _round(slug, phase_id, note=None, scope=0, only=None):
    """One round of a phase, waited for. Returns the run; raises if it failed or was stopped."""
    phases.go_to(slug, phase_id)
    review.save_settings(slug, scope=scope)
    run = room.start_round(slug, note, only=only)
    _set(slug, run=run.id, round=run.version.id)
    _log(slug, f"Round {run.version.id}: {phases.get(phase_id)['title'].lower()}, "
               f"{', '.join(r.title for r in run.roles)}.")
    with run.cond:
        run.cond.wait_for(lambda: run.done)
    status = run.version.meta.get("status")
    if status == "stopped":
        raise Halted()
    if status not in ("done", "awaiting_showrunner_decisions", "ready_for_review"):
        raise RuntimeError(f"round {run.version.id} ended with status {status!r}")
    return run


def _development(slug, note):
    seeded = projects.seed_production(slug)
    _log(slug, f"Production starts from intake's files: {', '.join(seeded) or 'none found'}.")
    _round(slug, "development", note)
    _choice(slug, "development", "Approved the development files as written.",
            "The brief, story and people go forward as the Director's room left them.",
            review.latest_round(slug)["id"])
    return None


TITLE_OF = {"writer_a": "Writer A", "writer_b": "Writer B"}
def _drafts(slug, note):
    """Edit mode: the Draft Editor brings the showrunner's drafts into line with the canon."""
    _round(slug, "drafts", note)
    return None


PICK_RE = re.compile(r"(version|writer)\s*([ab])\b", re.I)


def _audition(slug, note):
    if phases.editing(slug):        # an edit of the draft has one voice already: the draft's
        phases.start_edit(slug)
        writer = review.settings(slug)["writer"]
        _choice(slug, "audition", f"No audition: {TITLE_OF.get(writer, writer)} edits the draft.",
                "The book is an edit of the showrunner's draft (draft_mode \"edit\").",
                (review.latest_round(slug) or {}).get("id"))
        return note                 # the note was for the writers: it goes on to the writing
    _round(slug, "audition", note)
    rnd = review.latest_round(slug)["id"]
    reaction = projects.read_artifact(slug, "first-read.md") or ""
    writer, why = pick_from_first_read(reaction)
    if not writer:
        writer, why = "writer_a", "The First Reader gave no plain verdict, so Writer A goes forward."
    phases.pick(slug, writer)
    _choice(slug, "audition", f"Picked {'Writer A' if writer == 'writer_a' else 'Writer B'}.", why, rnd)
    _log(slug, f"Audition: picked {'Writer A' if writer == 'writer_a' else 'Writer B'} - {why}")
    return None


def pick_from_first_read(text):
    """The First Reader's "which one I would keep reading" section names a version. No second
    model call: the section is read, and if it does not say plainly, the last version named
    anywhere in the report counts."""
    m = re.search(r"#+\s*Which one I would keep reading.*?\n(.*?)(?=\n#+\s|\Z)", text, re.S | re.I)
    body = m.group(1).strip() if m else ""
    found = [x.group(2).upper() for x in PICK_RE.finditer(body)]
    if found and (len(set(found)) == 1 or found[0] == found[-1]):
        letter = found[-1]
        return ("writer_a" if letter == "A" else "writer_b"), " ".join(body.split())[:240]
    tail = [x.group(2).upper() for x in PICK_RE.finditer(text or "")]
    if tail:
        return ("writer_a" if tail[-1] == "A" else "writer_b"), "The report did not conclude plainly; the last version it named."
    return None, None




def _page1(slug, note):
    """The proof page is laid out from the script. After an audition the script holds its first pages; an
    edit of the draft has no audition, so the writer edits the draft into the script first."""
    if phases.editing(slug) and not (projects.read_artifact(slug, "script.md") or "").strip():
        _log(slug, "No audition in an edit: the writer scripts the drafts first, for the proof page to be laid out from.")
        note = _writing(slug, note)
        _set(slug, written_for_page1=True)
    _round(slug, "execution", note, scope=1)
    return None


def _writing(slug, note):
    review.save_settings(slug, scope=0)
    st = review.settings(slug).get("magic") or {}
    if st.get("written_for_page1") and not note and (projects.read_artifact(slug, "script.md") or "").strip():
        _set(slug, written_for_page1=False)     # written for the page 1 proof already: not twice
        _log(slug, "The script was written for the proof; going on from it.")
        return note
    _round(slug, "writing", note)
    _choice(slug, "writing", "Approved the script as written.", "The whole book, in the picked writer's voice.",
            (review.latest_round(slug) or {}).get("id"))
    return None


def _layouts(slug, note):
    """The Layout Agent alone, once: no continuity, no fix passes. The quick look."""
    review.save_settings(slug, scope=0)
    _round(slug, "execution", note, only=["layout"])
    return None


def _execution(slug, note):
    """Layouts until the readiness gate passes, or the round budget is spent."""
    review.save_settings(slug, scope=0)
    most = max_execution_rounds(slug)
    for n in range(1, most + 1):
        run = _round(slug, "execution", note if n == 1 else None)
        gate = run.version.meta.get("gate") or {}
        if gate.get("ready"):
            _log(slug, f"Pages: ready after round {n} of layouts.")
            return None
        reasons = "; ".join(gate.get("reasons") or [])[:200]
        if n == most:
            _choice(slug, "execution", f"Took the pages after {n} rounds, not fully ready.",
                    reasons or "The readiness gate still had reasons.", run.version.id)
            _log(slug, f"Pages: not fully ready after {n} rounds - taking them as they are ({reasons}).")
            return None
        _log(slug, f"Pages: round {n} not ready ({reasons}); sending it back for another.")
        review.submit(slug, "send")     # an empty review: every page open, nothing said
    return None


def _final(slug, note):
    st = review.state(slug)
    if not st["open"]:
        raise RuntimeError("there is no finished round to finalize")
    rnd = review.submit(slug, "finalize")
    _choice(slug, "final", "Finalized the book.", "Every page as the last round left it.", rnd)
    _log(slug, f"Finalized as {rnd}.")
    return None


# ---- what the page shows before it begins -----------------------------------------------------

def drafts(slug):
    """The showrunner's drafts/ files, which production starts from when there are any."""
    d = projects.campaign_dir(slug) / projects.DRAFTS
    return sorted(p.name for p in d.glob("*.md")) if d.is_dir() else []


def plan(slug):
    """The chain as it will run: each step, who works in it, on which model, and how long it took last time."""
    roles = {r.id: r for r in load_roles()}
    st = review.settings(slug)
    edit = st.get("draft_mode") == "edit" and bool(drafts(slug))
    out = []
    for step in STEPS:
        if step == "audition" and edit:
            continue                # an edit has no audition (see _audition)
        if step == "drafts" and not edit:
            continue                # only an edit has a draft edit
        phase = phases.get(PHASE_OF[step])
        ids = [st["writer"] or "writer_a" if a == phases.WRITER else a for a in phase["agents"]]
        if step == "layouts":
            ids = ["layout"]
        who = [roles[i] for i in ids if i in roles] if step != "final" else []   # finalizing is no round
        est = room.estimates(who)
        does = {"page1": f"Lay out one page only, page {review.proof_page(slug)}, from the script: a proof of the look.",
                "layouts": "One pass of the Layout Agent alone: every page's map and its panels, to look at before the long part.",
                "final": "The book is finalized as the last round left it, and the page packets are ready to download."}.get(step, phase["does"])
        groups = [set(g) for g in phase.get("parallel") or []]
        seconds = 0                     # agents side by side count once, as the longest of them
        for g in groups:
            seconds += max([est.get(i, 0) for i in g] or [0])
        seconds += sum(v for i, v in est.items() if not any(i in g for g in groups))
        out.append({"step": step, "title": TITLES[step], "phase": phase["id"], "does": does,
                    "agents": [{"id": r.id, "title": r.title, "model": r.config().public().get("model"),
                                "parallel": any(r.id in g for g in groups)} for r in who],
                    "seconds": seconds, "stop": step in STOPS, "optional": step == "page1",
                    "note": {"page1": "Only if you ask for a proof first.",
                             "drafts": "An edit stops here: read what changed, then script it - or stop.",
                             "layouts": "Produce stops here. Make the pages goes on.",
                             "execution": f"Up to {max_execution_rounds(slug)} rounds, until the pages pass the readiness check."}.get(step)})
    letterer = roles.get("letterer")
    if letterer:                    # not in the chain: after the art comes back
        out.append({"step": "lettering", "title": "Lettering", "phase": "lettering", "after": True,
                    "does": "You draw the pages from the packets and upload the art. The Letterer checks every "
                            "balloon against the real page, and the room draws the words over the art.",
                    "agents": [{"id": "letterer", "title": letterer.title,
                                "model": letterer.config().public().get("model"), "parallel": False}],
                    "seconds": room.estimates([letterer]).get("letterer", 0), "stop": False, "optional": False,
                    "note": "Runs from the Lettering tab, page by page as the art comes in."})
    return out
