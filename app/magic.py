"""Production, run all the way: the room takes every gate, the showrunner sees finished work.

The phases (app/phases.py) each stop for the showrunner. This runs them back to back and
takes the decisions itself, in an order with one deliberate pause:

    development   Director, Plotter, Character Designer, Continuity
    audition      Writer A and Writer B; the First Reader's reaction picks the writer
    page1         execution on page 1 only, from the audition pages already in script.md
                  -> STOP: the showrunner sees the first page and says "about right" or not
    writing       the picked writer writes the whole book
    execution     layout and lettering, round after round, until the readiness gate passes
    final         the book is finalized

The pause at page 1 is the point: the cheapest place to find out the book looks wrong.
Everything after it is the standard the showrunner accepted, applied to the rest.

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

from . import llm, notes as notes_mod, phases, projects, review, room
from .agents import load_roles

STEPS = ("development", "audition", "page1", "writing", "execution", "final")
PHASE_OF = {"development": "development", "audition": "audition", "page1": "execution",
            "writing": "writing", "execution": "execution", "final": "execution"}
TITLES = {"development": "Development", "audition": "Audition", "page1": "Page 1",
          "writing": "Writing", "execution": "Pages", "final": "Final"}
STOPS = {"page1": "page1", "final": "final"}    # a chain ends here and waits for the showrunner
MAX_EXECUTION_ROUNDS = 4                        # rounds of layout+lettering before the book is taken as is

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
            note = {"development": _development, "audition": _audition, "page1": _page1,
                    "writing": _writing, "execution": _execution, "final": _final}[step](slug, note)
            if step == until:
                break
            i += 1
        if until == "page1":
            _set(slug, status="page1", finished=projects.now())
            _log(slug, "Page 1 is ready. Have a look: is this about right?")
        else:
            _set(slug, status="done", finished=projects.now())
            _log(slug, "The book is done.")
    except Halted:
        _set(slug, status="stopped", finished=projects.now())
        _log(slug, "Stopped.")
    except Exception as e:      # noqa: BLE001 - whatever failed, the chain must say so and end
        _set(slug, status="failed", error=f"{type(e).__name__}: {e}"[:400], finished=projects.now())
        _log(slug, f"Failed at {TITLES.get(step, step).lower()}: {type(e).__name__}: {str(e)[:200]}")


def _round(slug, phase_id, note=None, scope=0):
    """One round of a phase, waited for. Returns the run; raises if it failed or was stopped."""
    phases.go_to(slug, phase_id)
    review.save_settings(slug, scope=scope)
    run = room.start_round(slug, note)
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


PICK_RE = re.compile(r"(version|writer)\s*([ab])\b", re.I)


def _audition(slug, note):
    _round(slug, "audition", note)
    rnd = review.latest_round(slug)["id"]
    reaction = projects.read_artifact(slug, "first-read.md") or ""
    writer, why = pick_from_first_read(reaction)
    if not writer:
        writer, why = ask_reader(slug, reaction)
    if not writer:
        writer, why = "writer_a", "The First Reader gave no verdict, so Writer A goes forward."
    phases.pick(slug, writer)
    _choice(slug, "audition", f"Picked {'Writer A' if writer == 'writer_a' else 'Writer B'}.", why, rnd)
    _log(slug, f"Audition: picked {'Writer A' if writer == 'writer_a' else 'Writer B'} - {why}")
    return None


def pick_from_first_read(text):
    """The First Reader's last section says which one they would keep reading."""
    m = re.search(r"#+\s*Which one I would keep reading.*?\n(.*?)(?=\n#+\s|\Z)", text, re.S | re.I)
    if not m:
        return None, None
    body = m.group(1).strip()
    found = [x.group(2).upper() for x in PICK_RE.finditer(body)]
    if not found or len(set(found)) > 1 and found[0] != found[-1]:
        return None, None
    letter = found[-1]
    why = " ".join(body.split())[:240]
    return ("writer_a" if letter == "A" else "writer_b"), why


def ask_reader(slug, reaction):
    """A one-line question to the First Reader's own model, when the write-up did not say plainly."""
    role = next((r for r in load_roles() if r.id == "first_reader"), None)
    if role is None or not reaction.strip():
        return None, None
    try:
        reply = llm.chat(role.config(), [
            {"role": "system", "content": "Answer with one letter, A or B, then one sentence."},
            {"role": "user", "content": "This is a reader's report on two versions of the same pages. "
                                        "Which version would they keep reading?\n\n" + reaction[:12000]}],
            max_tokens=80)
        text = llm.text_of(reply).strip()
        m = re.match(r"\W*([AB])\b(.*)", text, re.S | re.I)
        if m:
            return ("writer_a" if m.group(1).upper() == "A" else "writer_b"), (m.group(2).strip() or text)[:240]
    except Exception:       # noqa: BLE001 - a failed tie-break is not a failed audition
        pass
    return None, None


def _page1(slug, note):
    _round(slug, "execution", note, scope=1)
    return None


def _writing(slug, note):
    review.save_settings(slug, scope=0)
    _round(slug, "writing", note)
    _choice(slug, "writing", "Approved the script as written.", "The whole book, in the picked writer's voice.",
            review.latest_round(slug)["id"])
    return None


def _execution(slug, note):
    """Layout and lettering until the readiness gate passes, or the round budget is spent."""
    review.save_settings(slug, scope=0)
    for n in range(1, MAX_EXECUTION_ROUNDS + 1):
        run = _round(slug, "execution", note if n == 1 else None)
        gate = run.version.meta.get("gate") or {}
        if gate.get("ready"):
            _log(slug, f"Pages: ready after round {n} of layout and lettering.")
            return None
        reasons = "; ".join(gate.get("reasons") or [])[:200]
        if n == MAX_EXECUTION_ROUNDS:
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
    out = []
    for step in STEPS:
        phase = phases.get(PHASE_OF[step])
        ids = [st["writer"] or "writer_a" if a == phases.WRITER else a for a in phase["agents"]]
        who = [roles[i] for i in ids if i in roles] if step != "final" else []   # finalizing is no round
        est = room.estimates(who)
        does = {"page1": "Lay out and letter page 1 only, from the audition pages already in the script.",
                "final": "The book is finalized as the last round left it, as a -final round."}.get(step, phase["does"])
        out.append({"step": step, "title": TITLES[step], "phase": phase["id"], "does": does,
                    "agents": [{"id": r.id, "title": r.title, "model": r.config().public().get("model")} for r in who],
                    "seconds": sum(est.values()), "stop": step in STOPS,
                    "note": {"page1": "You judge the look before the rest is made.",
                             "execution": f"Up to {MAX_EXECUTION_ROUNDS} rounds, until the pages pass the readiness check."}.get(step)})
    return out
