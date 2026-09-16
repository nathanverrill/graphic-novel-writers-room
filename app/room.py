"""Runs roles one after another in a background thread and records events
so the browser can follow along (see /api/runs/{id}/events).
Every run is an AI round (rounds/<slug>-rNN-ai).

A *writing round* (start_round) goes further: the room writes the book, then checks
the readiness gate (page count, layout issues, continuity blockers, how closely
locked pages are matched) and reruns only the roles that can fix what's wrong, up
to max_passes times, before handing the pages to the showrunner for review."""
import threading
import time
import uuid

from . import agent as agent_mod
from . import projects, review
from .roles import list_hats, load_roles

FIRST_ROUND = ["editor", "plotter", "character_designer", "scripter", "penciller", "ascii_artist", "continuity"]
REVISION_ROUND = ["editor", "scripter", "penciller", "ascii_artist", "continuity"]


class Run:
    def __init__(self, slug, roles, note, hat=None, plan=None):
        self.id = uuid.uuid4().hex[:12]
        self.slug = slug
        self.roles = roles
        self.note = note
        self.hat = hat
        self.plan = plan            # set for writing rounds: {"order", "max_passes", "kind"}
        self.events = []
        self.done = False
        self.stop_requested = False
        self.cond = threading.Condition()
        self.version = projects.Version(
            slug, run_id=self.id, note=note, hat=hat, roles=[r.id for r in roles],
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

    def run_roles(self, roles, note, pass_n=1):
        for role in roles:
            emit = lambda type, _id=role.id, **d: self.emit(type, role=_id, **d)
            emit("role_start", title=role.title, pass_n=pass_n)
            a = agent_mod.Agent(role, self.version, emit, lambda: self.stop_requested)
            try:
                done_note = a.run(note, self.hat)
            finally:
                emit("role_cost", **a.log.totals)
            emit("role_done", note=done_note)

    def fix_roles(self, g):
        wanted = set(g["fix"])
        if wanted & {"scripter", "penciller"}:
            wanted.add("ascii_artist")
        wanted.add("continuity")
        return [r for r in self.plan["all"] if r.id in wanted]

    def writing_round(self):
        titles = {r.id: r.title for r in self.plan["all"]}
        g = review.gate(self.slug, titles)
        passes = 0
        while not g["ready"] and passes < self.plan["max_passes"]:
            passes += 1
            self.emit("gate", ready=False, pass_n=passes, reasons=g["reasons"], fix=g["fix"])
            note = "\n\n".join(filter(None, [
                self.note,
                f"# Revision pass {passes} of {self.plan['max_passes']} — the round isn't ready yet",
                "Fix only these problems, and touch nothing else:\n- " + "\n- ".join(g["reasons"]),
                "\n\n".join(g["notes"][:40]),
            ]))
            self.run_roles(self.fix_roles(g), note, passes + 1)
            g = review.gate(self.slug, titles)
        summary = {k: g[k] for k in ("ready", "reasons", "blockers", "layout_issues", "pages", "dialed_in")}
        self.version.update(gate=summary, passes=passes)
        self.emit("gate", pass_n=passes, final=True, **{k: g[k] for k in ("ready", "reasons", "fix", "dialed_in")})
        if not g["ready"]:
            self.emit("warn", text=f"Not fully ready after {passes} revision passes — handing it to you anyway.")

    def work(self):
        self.emit("run_start", roles=[r.id for r in self.roles], version=self.version.id, hat=self.hat,
                  writing_round=self.plan and self.plan["kind"])
        status = "error"
        try:
            self.run_roles(self.roles, self.note)
            if self.plan:
                self.writing_round()
            pages = review.export_pages(self.slug, self.version)
            self.version.update(pages=pages)
            if self.plan:
                self.emit("round_ready", version=self.version.id, pages=pages)
            status = "done"
            self.emit("run_done", version=self.version.id)
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


RUNS = {}


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


def start_round(slug, note=None, hat=None):
    """The whole room, then fix passes until the pages are ready for review."""
    if active_run(slug):
        raise RuntimeError("the room is already working on this project")
    if hat and hat not in list_hats():
        raise ValueError(f"no hat named {hat!r}")
    st = review.settings(slug)
    last = review.latest_round(slug)
    kind = "revision" if last and last.get("kind") == "human" else "first"
    by_id = {r.id: r for r in load_roles()}
    order = [i for i in (REVISION_ROUND if kind == "revision" else FIRST_ROUND)
             if i in by_id and (st["artist"] or i != "ascii_artist")]
    roles = [by_id[i] for i in order]
    _check_configs(roles)
    parts = []
    if st["pages"]:
        parts.append(f"The book is exactly {st['pages']} pages: pages 1-{st['pages']}, no more, no fewer.")
    if kind == "revision":
        parts += ["Work from the showrunner's review below. Change only what it asks for; "
                  "locked pages are restored automatically if you touch them.",
                  projects.read_artifact(slug, "review.md") or ""]
    if note:
        parts.append(f"Showrunner's note for this round: {note}")
    plan = {"kind": kind, "max_passes": int(st["max_passes"]), "all": roles}
    run = Run(slug, roles, "\n\n".join(p for p in parts if p), hat, plan)
    RUNS[run.id] = run
    threading.Thread(target=run.work, daemon=True).start()
    return run


def start(slug, role_ids, note=None, hat=None):
    if active_run(slug):
        raise RuntimeError("the room is already working on this project")
    by_id = {r.id: r for r in load_roles()}
    unknown = [r for r in role_ids if r not in by_id]
    if unknown:
        raise KeyError(", ".join(unknown))
    roles = [by_id[r] for r in role_ids]
    if hat and hat not in list_hats():
        raise ValueError(f"no hat named {hat!r}")
    _check_configs(roles)
    run = Run(slug, roles, note, hat)
    RUNS[run.id] = run
    threading.Thread(target=run.work, daemon=True).start()
    return run
