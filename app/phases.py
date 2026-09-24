"""The room works in six phases, and you stand at the gate between each:

    intake        the Script Coordinator sorts your material  you approve its reading
    development   Director, Plotter, Character Designer     you approve the story
    drafts        edit mode only: the Draft Editor          you approve your drafts, edited to the canon
    audition      Writer A and Writer B, the same pages     you pick the voice
    writing       the writer you picked, the whole script   you approve the words
    execution     Layout Agent, page packets                you review the pages, then draw them
    lettering     Letterer, over the art you drew           you download the lettered pages

agents/phases.json is the whole definition: who runs in each phase and in what order, and what
to read before you decide. A campaign remembers where it is in round-settings.json ("phase",
and "writer" once you have picked one). Nothing moves on by itself: a phase can be run as often
as you like, and only approve() or pick() takes the book to the next one. go_to() takes it
anywhere, which is how a book goes back to an earlier phase.

A phase never reruns the ones before it. That is the point of having them: a lettering problem
reruns the Letterer, not the writer.

"parallel" in a phase names groups of its agents that run at the same time (see room.py).
"""
import json
import time
from dataclasses import replace
from datetime import datetime

from . import draftedit, openitems, projects, review, voices
from .agents import load_roles
from .config import AGENTS_DIR

WRITER = "writer"       # in phases.json: whichever writer the showrunner picked


def load():
    return json.loads((AGENTS_DIR / "phases.json").read_text())


def get(phase_id):
    for p in load():
        if p["id"] == phase_id:
            return p
    raise ValueError(f"no phase named {phase_id!r}")


def current(slug):
    return get(review.settings(slug)["phase"])


def roles(slug, phase):
    """The agents that run in this phase, in order, writing what this phase has them write."""
    by_id = {r.id: r for r in load_roles()}
    writer = review.settings(slug)["writer"]
    out = []
    for agent_id in phase["agents"]:
        if agent_id == WRITER:
            if not writer:
                raise ValueError("no writer has been picked yet — run the audition and pick one")
            agent_id = writer
        role = by_id[agent_id]
        if agent_id in phase.get("writes", {}):     # the audition: each writer into its own file
            role = replace(role, outputs=[phase["writes"][agent_id]])
        out.append(role)
    return out


DRAFT_NOTE = {
    "development": "draft.md is the showrunner's own draft of the book. It is not finished and it is "
                   "not binding, but it is the book they mean to make: plan around what it does - its "
                   "scenes, its order, its people - and improve on it, rather than planning a "
                   "different book. Where the pre-production files and the draft disagree, the files "
                   "win, and say so in your notes.",
    "audition": "draft.md is the showrunner's own draft. Your audition pages are its opening, rewritten: "
                "keep what it does and the lines that work, bring it into line with the "
                "pre-production files, and raise the craft. The voice is yours; the book is theirs.",
    "writing": "draft.md is the showrunner's own draft of the whole book. Write the book from it, in "
               "the voice of your audition pages: keep its structure, its scenes and the lines that "
               "work; fix what story.md, characters.md, world.md and facts.md contradict; make every "
               "page better than the draft's. Do not start over, and do not drop what it has "
               "unless the files require it.",
}

# draft_mode "edit": the draft is the book, and the room edits it. Improvements, no substantial
# changes. Where this and a role guide disagree about the draft, this wins.
ADDED = ("Where the pre-production files add something the draft does not have - a character, a "
         "look, a rule, a fact - bring it into the draft's existing scenes: give it the moments the "
         "scene has room for, without adding, cutting or moving a scene.")
EDIT_NOTE = {
    "development": "draft.md is the showrunner's own draft, and this book is an EDIT of it: improvements, "
                   "no substantial changes. Director: the brief keeps the draft's story, scenes and "
                   "ending; it decides only what the draft leaves open. Plotter: the draft's scenes, "
                   "in the draft's order, ARE the page plot. Do not build a new version: fit them to "
                   "the page count, fix what contradicts the pre-production files, and fill only real "
                   "gaps. Character Designer: the draft's people as they are, made specific and "
                   "drawable. " + ADDED + " Continuity Editor: a scene the files cut, merged or "
                   "reordered against the draft is a Blocker unless the files require it.",
    "audition": "draft.md is the showrunner's own draft, and this book is an EDIT of it. Your audition "
                "pages are the draft's opening, edited: every scene and beat kept, the draft's lines "
                "word for word unless a line is broken, the craft raised only where it is. " + ADDED,
    "drafts": "draft.md is the showrunner's own draft. Edit it to the canon, chapter by chapter: change "
              "only what the canon contradicts, keep everything else word for word, and flag what no "
              "longer fits rather than rewriting it.",
    "writing": "draft-final.md is the book: the showrunner's draft, edited to the canon and expanded, "
               "and approved. Script it, and do nothing else: break it into pages and panels, one page "
               "after another in its order, with panel descriptions an artist can draw and a balloon for "
               "each of its lines, word for word. No new beats, no new dialogue, nothing cut, nothing "
               "moved; [NEW] marks are the editor's and are not printed. Where there is no draft-final.md, "
               "script draft.md the same way. End each page's PAGE CHECK with `CHANGED: none`, or what "
               "you had to change to draw it and why. Continuity Editor: check script.md against "
               "draft-final.md. A dropped, merged or reordered beat, a line not word for word, or "
               "anything added that the draft does not have is a Blocker.",
}


def editing(slug):
    """The book is an edit of the showrunner's draft: draft_mode "edit", and a draft to edit."""
    return (review.settings(slug).get("draft_mode") == "edit"
            and bool(projects.read_artifact(slug, projects.DRAFT)))


EDIT_WRITER = "writer_a"      # the writer an edit goes to when nobody has auditioned


def start_edit(slug):
    """An edit has no audition: the writer already picked, or Writer A, starts script.md empty."""
    writer = review.settings(slug)["writer"] or EDIT_WRITER
    projects.write_artifact(slug, "script.md", "")
    review.save_settings(slug, writer=writer)
    return go_to(slug, "writing")


def note(slug, phase):
    """What the agents are told about the phase they are running in."""
    parts = []
    if phase["id"] == "audition":
        n = phase["pages"]
        parts.append(f"This is the audition. Write pages 1-{n} only, in full, into your audition file. "
                     "The other writer is writing the same pages and you cannot see their work.")
    if phase["id"] == "writing" and not editing(slug):
        parts.append("The showrunner picked you in the audition. script.md holds your audition pages: "
                     "keep their voice, and write the whole book.")
    if phase["id"] in ("audition", "writing", "execution"):
        parts.append("Drawability: " + draftedit.drawability(slug) + " Every page you make keeps to it.")
    if phase["id"] == "execution":
        parts.append("The pages are drawn from your layouts by an image model, with NO text on them: "
                     "the lettering is added afterwards as a layer, from the items in each layout block. "
                     "So every balloon, caption and sound effect must be in the layout block with the "
                     "exact words, and each panel's description must say where the clear space for them is.")
    if phase["id"] == "lettering":
        have = [n for n in range(1, 400) if projects.page_art(slug, n)]
        parts.append("The showrunner has drawn the pages from the packets and uploaded the art "
                     + (f"for pages {', '.join(map(str, have))}. " if have else "for no pages yet. ")
                     + "Judge the lettering against the real page where there is one, and against the "
                       "layout sketch where there is not.")
    if editing(slug):
        if phase["id"] in EDIT_NOTE:
            parts.append(EDIT_NOTE[phase["id"]])
    elif phase["id"] in DRAFT_NOTE and projects.read_artifact(slug, projects.DRAFT):
        parts.append(DRAFT_NOTE[phase["id"]])
    return "\n\n".join(parts) or None


def state(slug):
    st = review.settings(slug)
    return {"phase": st["phase"], "writer": st["writer"], "phases": load()}


def go_to(slug, phase_id):
    get(phase_id)
    review.save_settings(slug, phase=phase_id)
    return state(slug)


def approve(slug):
    """The showrunner approves the phase's work: on to the next phase.

    Leaving intake copies its five files onto the production desk: that is the reading the
    book is made from, and intake's own copy stays as approved whatever production does."""
    phase = current(slug)
    if phase["gate"] != "approve":
        raise ValueError(f"{phase['title']} is not closed by approving it")
    if phase["id"] == "intake":
        projects.seed_production(slug)
    if phase["id"] == "development":    # an edit goes to the draft edit; anything else skips it
        return go_to(slug, "drafts" if editing(slug) else "audition")
    if phase["id"] == "drafts":
        return start_edit(slug)         # an edit has no audition
    ids = [p["id"] for p in load()]
    if phase["id"] == ids[-1]:          # the last phase: approving it closes the book where it is
        return state(slug)
    return go_to(slug, ids[ids.index(phase["id"]) + 1])


def readiness(slug):
    """Whether pre-production can be approved for production, and if not, what is left.

    Every open item answered or deferred; intake finished, facts.md and all; and nothing in
    rules/ or on the open-items list changed since the last intake round - an answer or a rule the room has not
    folded into the files would never reach production, which does not read rules/."""
    items = openitems.state(slug)
    rounds = projects.list_versions(slug, desk=projects.PRE)
    latest = rounds[0] if rounds else None
    rules = [f for f in (projects.campaign_dir(slug) / projects.RULES).glob("*") if f.is_file()]
    changed = max((f.stat().st_mtime for f in rules), default=0)     # decisions.md is one of them
    listed = projects.project_dir(slug, projects.PRE) / openitems.ITEMS   # defers and item notes go here
    stamp = lambda k: datetime.fromisoformat(latest[k]).timestamp() if latest and latest.get(k) else 0
    changed = max(changed, voices.changed_at(slug))      # the dialog simulator's tuning waits for the canon too
    unfolded = bool(latest) and (changed > stamp("started")
                                 or (listed.exists() and listed.stat().st_mtime > stamp("finished") + 2))
    why = None
    if items["unresolved"]:
        n, recs = items["unresolved"], len(openitems.recommended(slug))
        why = f"{n} open item{'s' if n > 1 else ''} still unanswered: answer or defer {'them' if n > 1 else 'it'}" + (
            ", or Update canon again and the room takes its recommendation." if recs == n else ".")
    elif latest and latest.get("status") in ("running", "stopped", "error", "interrupted"):
        why = "The last intake round did not finish. Press Update canon."
    elif not projects.read_artifact(slug, "facts.md", desk=projects.PRE):
        why = "Intake has not finished: facts.md is written after the canon is updated. Press Update canon."
    elif unfolded:
        why = "Your answers or rules changed since the canon was last updated. Press Update canon so it carries them."
    return {"ready": why is None, "why": why, "round": latest and latest["id"],
            "unfolded": unfolded,       # answers, defers, notes or rules the canon does not carry yet
            "updates": openitems.revisions(slug),      # times the canon was updated since synthesis
            "will_recommend": len(openitems.recommended(slug)),
            "approved": review.settings(slug).get("approved")}


CONFIRM_WORD = "evoke"      # typed to approve pre-production, as the sheets page's reset is


def approve_preproduction(slug, confirm=None):
    """The showrunner approves pre-production for production.

    Intake's files are copied onto the production desk, the book goes to development, and the
    Produce chain starts clean: whatever an earlier production did is in its rounds, not on
    the page the showrunner opens next."""
    if (confirm or "").strip().lower() != CONFIRM_WORD:
        raise ValueError(f"type {CONFIRM_WORD} to confirm")
    ready = readiness(slug)
    if not ready["ready"]:
        raise ValueError(ready["why"])
    projects.seed_production(slug)
    approved = {"at": projects.now(), "t": time.time(), "round": ready["round"]}   # at: the server's clock, as rounds have it
    review.save_settings(slug, phase="development", approved=approved,
                         magic={"status": "idle", "choices": [], "log": [{
                             "t": time.time(),
                             "text": f"Pre-production approved (intake round {ready['round']}). "
                                     "Production starts from its files."}]})
    return state(slug)


def pick(slug, writer):
    """The showrunner picks a writer: their audition pages become the start of script.md."""
    phase = get("audition")
    if writer not in phase["writes"]:
        raise ValueError(f"{writer!r} did not audition")
    pages = projects.read_artifact(slug, phase["writes"][writer])
    if not pages:
        raise ValueError(f"{writer} has not written an audition yet")
    projects.write_artifact(slug, "script.md", pages)
    review.save_settings(slug, writer=writer)
    return go_to(slug, "writing")
