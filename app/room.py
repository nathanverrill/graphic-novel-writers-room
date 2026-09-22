"""Runs agents one after another in a background thread and records events
so the browser can follow along (see /api/runs/{id}/events).
Every run is an AI round (previous/<slug>-rNN-ai).

A round (start_round) runs the phase the book is in — see phases.py — and then stops for
the showrunner. Execution goes one step further, because its gate is measured rather than
judged: it checks the readiness gate (page count, layout issues, continuity blockers, how
closely locked pages are matched) and reruns only the agents that can fix what's wrong,
up to max_passes times, before handing the pages over for review.

Two things can interrupt that: the showrunner can hold the round between two writers
(hold(), pause/resume) and change settings or leave notes for whoever runs next, and
auto mode (auto_step) can hand a finished round straight back to the room instead of
waiting for a review."""
import threading
import time
import uuid
from dataclasses import replace

from . import agent as agent_mod, intake as intake_mod, visual as visual_mod
from . import notes as notes_mod
from . import phases, projects, review, usage
from .agents import load_roles

MEASURED = "execution"      # the one phase whose gate the room can check for itself


class Run:
    def __init__(self, slug, roles, note, plan=None, mode=None):
        self.id = uuid.uuid4().hex[:12]
        self.slug = slug
        self.roles = roles
        self.mode = mode          # intake: which kind of round this is
        self.awaiting = False     # a runner stopped for the showrunner (intake passes 1-3)
        self.run_status = None    # a runner's own word for how the round ended (see intake.py)
        self.note = note
        self.plan = plan            # set for a phase's round: {"kind": phase id, "max_passes", "all"}
        self.events = []
        self.done = False
        self.stop_requested = False
        self.pause_requested = False
        self.paused = False
        self.last_done = None       # the writer who handed off last, for the pause banner
        self.cond = threading.Condition()
        self.version = projects.Version(
            slug, run_id=self.id, note=note, roles=[r.id for r in roles],
            configs={r.id: r.config().public() for r in (plan["all"] if plan else roles)},
            writing_round=plan and plan["kind"],
        )

    def emit(self, type, **data):
        with self.cond:
            event = {"i": len(self.events), "type": type, "t": time.time(), **data}
            self.events.append(event)
            self.version.log_event(event)
            self.cond.notify_all()

    def wait(self, after, timeout=15):
        """Block until there are events past `after` (or the run ends)."""
        with self.cond:
            self.cond.wait_for(lambda: len(self.events) > after or self.done, timeout)
            return self.events[after:], self.done

    def hold(self, note, next_role):
        """Between two agents: if the showrunner asked to pause, wait here until they resume.

        Nothing is torn down — the round keeps its version and its place in the order. Every
        agent's settings are read from agent.json when it starts, so a model or temperature
        changed while paused applies to whoever runs next; notes jotted while paused are
        handed to them as well. Returns the note the rest of the round should carry."""
        with self.cond:
            if not self.pause_requested or self.stop_requested:
                return note
            self.paused = True
            before = {r.id: r.config().public() for r in (self.plan["all"] if self.plan else self.roles)}
            self.emit("paused", next=next_role.id, title=next_role.title,
                      after=self.last_done and self.last_done.id, after_title=self.last_done and self.last_done.title)
            self.cond.wait_for(lambda: not self.pause_requested or self.stop_requested)
            self.paused = False
        if self.stop_requested:
            raise agent_mod.Stopped()
        roles = self.plan["all"] if self.plan else self.roles
        after = {r.id: r.config().public() for r in roles}
        changed = {r: {k: v for k, v in after[r].items() if before.get(r, {}).get(k) != v}
                   for r in after if after[r] != before.get(r)}
        self.version.update(configs=after)
        jotted = notes_mod.take(self.slug, self.version.id)
        if jotted:                 # keep the notes taken at the start of the round as well
            path = self.version.path("showrunner-notes.md")
            had = path.read_text() if path.exists() else ""
            self.version.write_file("showrunner-notes.md", "\n\n".join(filter(None, [had, jotted])))
        self.emit("resumed", changed=changed, notes=bool(jotted))
        return "\n\n".join(p for p in (note, jotted) if p)

    def run_roles(self, roles, note, pass_n=1):
        for role in roles:
            note = self.hold(note, role)
            role = self.reload(role)
            emit = lambda type, _id=role.id, **d: self.emit(type, role=_id, **d)
            emit("role_start", title=role.title, pass_n=pass_n)
            if self.plan and self.plan["kind"] == "visual":
                a = visual_mod.Visual(role, self.version, emit, lambda: self.stop_requested, self.mode)
            elif role.pipeline == "intake":
                a = intake_mod.Intake(role, self.version, emit, lambda: self.stop_requested, self.mode)
            else:
                a = agent_mod.Agent(role, self.version, emit, lambda: self.stop_requested)
            try:
                done_note = a.run(note)
            finally:
                emit("role_cost", **a.log.totals)
            emit("role_done", note=done_note)
            self.awaiting = self.awaiting or getattr(a, "awaiting", False)
            self.run_status = getattr(a, "run_status", None) or self.run_status
            self.last_done = role

    def reload(self, role):
        """The role as it is on disk now — settings can have changed while the round was paused.
        What the phase has it write (an audition file, say) stays as the phase set it."""
        fresh = {r.id: r for r in load_roles()}.get(role.id, role)
        return replace(fresh, outputs=role.outputs)

    def fix_roles(self, g):
        """Who reruns: only agents of this phase. A blocker that belongs to an earlier phase is
        the showrunner's call, so with nobody here to fix it the passes stop."""
        fixers = {r.id for r in self.plan["all"] if r.id in g["fix"]}
        return [r for r in self.plan["all"] if r.id in fixers or (fixers and r.id == "continuity")]

    def writing_round(self):
        titles = {r.id: r.title for r in self.plan["all"]}
        g = review.gate(self.slug, titles)
        passes = 0
        while not g["ready"] and passes < self.plan["max_passes"]:
            fixers = self.fix_roles(g)
            if not fixers:
                self.emit("warn", text="What's wrong isn't this phase's to fix — it is yours to send back.")
                break
            passes += 1
            self.emit("gate", ready=False, pass_n=passes, reasons=g["reasons"], fix=g["fix"],
                      roles=[r.id for r in fixers])
            note = "\n\n".join(filter(None, [
                self.note,
                f"# Revision pass {passes} of {self.plan['max_passes']} — the round isn't ready yet",
                "Fix only these problems, and touch nothing else:\n- " + "\n- ".join(g["reasons"]),
                "\n\n".join(g["notes"][:40]),
            ]))
            self.run_roles(fixers, note, passes + 1)
            g = review.gate(self.slug, titles)
        summary = {k: g[k] for k in ("ready", "reasons", "blockers", "layout_issues", "pages", "dialed_in")}
        self.version.update(gate=summary, passes=passes)
        self.emit("gate", pass_n=passes, final=True, **{k: g[k] for k in ("ready", "reasons", "fix", "dialed_in")})
        if not g["ready"]:
            self.emit("warn", text=f"Not fully ready after {passes} revision passes — handing it to you anyway.")

    def work(self):
        measured = bool(self.plan) and self.plan["kind"] == MEASURED
        times = estimates(self.roles)
        self.emit("run_start", roles=[r.id for r in self.roles], version=self.version.id,
                  writing_round=self.plan and self.plan["kind"],
                  max_passes=self.plan["max_passes"] if measured else 0,
                  estimates=times, pass_seconds=sum(times.values()) if measured else 0)
        status = "error"
        try:
            self.run_roles(self.roles, self.note)
            if measured:
                self.writing_round()
            pages = review.export_pages(self.slug, self.version)
            self.version.update(pages=pages)
            if measured:
                self.emit("round_ready", version=self.version.id, pages=pages)
            status = self.run_status or "done"
            self.emit("run_done", version=self.version.id, awaiting=self.awaiting)
        except agent_mod.Stopped:
            status = "stopped"
            self.emit("run_stopped", version=self.version.id)
        except Exception as e:
            self.emit("error", text=f"{type(e).__name__}: {e}")
        finally:
            self.version.update(status=status, finished=projects.now())
            self.emit("run_cost", **self.version.meta["usage"]["total"])
            with self.cond:
                self.done = True
                self.cond.notify_all()
        if status == "done" and measured:
            threading.Thread(target=auto_step, args=(self.slug, self), daemon=True).start()


RUNS = {}
DEFAULT_ROLE_SECONDS = 120


def auto_step(slug, run):
    """Auto mode, in execution only: when a round ends, go again without waiting for a review.

    The round that just finished is handed back with nothing said about any page — every page
    open, no notes — which is what an empty review means, and the next round starts from it.
    The loop stops when the gate comes back ready, when the round budget is spent, or when
    the showrunner sets Auto rounds to 0; then the book is finalized. Nothing else changes:
    each writer still runs on its own model and settings."""
    left = int(review.settings(slug).get("auto_rounds") or 0)
    if left <= 0:
        return
    ready = bool((run.version.meta.get("gate") or {}).get("ready"))
    review.save_settings(slug, auto_rounds=max(0, left - 1))
    try:
        if ready or left <= 1:
            review.submit(slug, "finalize")
            review.save_settings(slug, auto_rounds=0)
            return
        review.submit(slug, "send")
        start_round(slug)
    except (ValueError, RuntimeError):
        review.save_settings(slug, auto_rounds=0)     # something is wrong: stop rather than spin


def estimates(roles):
    """{role: seconds} — the median of the role's past runs, with its current model if it has any."""
    past = usage.role_seconds()
    out = {}
    for r in roles:
        model = r.config().model
        runs = past.get((r.id, model)) or [s for (role, _), v in past.items() if role == r.id for s in v]
        out[r.id] = round(sorted(runs)[len(runs) // 2]) if runs else DEFAULT_ROLE_SECONDS
    return out


def active_run(slug):
    for run in RUNS.values():
        if run.slug == slug and not run.done:
            return run
    return None


def _check_configs(roles):
    for r in roles:  # fail before starting if an agent.json is broken
        try:
            r.config()
        except (ValueError, TypeError) as e:
            raise ValueError(f"{r.id}/{e}") from None


def start_round(slug, note=None, mode=None):
    """Run the phase the book is in. It stops for the showrunner when the phase's agents are done."""
    if active_run(slug):
        raise RuntimeError("the room is already working on this project")
    st = review.settings(slug)
    phase = phases.current(slug)
    roles = phases.roles(slug, phase)
    _check_configs(roles)
    parts = [f"The room is in {phase['title'].lower()}: {phase['does']}", phases.note(slug, phase)]
    if st["pages"]:
        parts.append(f"The book is exactly {st['pages']} pages: pages 1-{st['pages']}, no more, no fewer.")
    last = review.latest_round(slug)
    if last and last.get("kind") == "human":
        parts += ["Work from the showrunner's review below. Change only what it asks for; "
                  "locked pages are restored automatically if you touch them.",
                  projects.read_artifact(slug, "review.md") or ""]
    if note:
        parts.append(f"Showrunner's note for this round: {note}")
    jotted = notes_mod.take(slug, "pending")   # the round id isn't known until the Run is made
    if jotted:
        parts.append(jotted)
    plan = {"kind": phase["id"], "max_passes": int(st["max_passes"]), "all": roles}
    run = Run(slug, roles, "\n\n".join(p for p in parts if p), plan, mode)
    if jotted:
        notes_mod.mark_used(slug, [n["id"] for n in notes_mod._all(slug) if n["used_in"] == "pending"], run.version.id)
        run.version.write_file("showrunner-notes.md", jotted)
    RUNS[run.id] = run
    threading.Thread(target=run.work, daemon=True).start()
    return run


def start(slug, role_ids, note=None):
    """Run just these agents, outside the phases — for trying one thing."""
    if active_run(slug):
        raise RuntimeError("the room is already working on this project")
    by_id = {r.id: r for r in load_roles()}
    unknown = [r for r in role_ids if r not in by_id]
    if unknown:
        raise KeyError(", ".join(unknown))
    roles = [by_id[r] for r in role_ids]
    _check_configs(roles)
    run = Run(slug, roles, note)
    RUNS[run.id] = run
    threading.Thread(target=run.work, daemon=True).start()
    return run
