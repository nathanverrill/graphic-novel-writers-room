"""The room works in six phases, and you stand at the gate between each:

    intake        the Script Coordinator sorts your material  you approve its reading
    development   Director, Plotter, Character Designer     you approve the story
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
from dataclasses import replace

from . import projects, review
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


def note(slug, phase):
    """What the agents are told about the phase they are running in."""
    parts = []
    if phase["id"] == "audition":
        n = phase["pages"]
        parts.append(f"This is the audition. Write pages 1-{n} only, in full, into your audition file. "
                     "The other writer is writing the same pages and you cannot see their work.")
    if phase["id"] == "writing":
        parts.append("The showrunner picked you in the audition. script.md holds your audition pages: "
                     "keep their voice, and write the whole book.")
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
    if phase["id"] in DRAFT_NOTE and projects.read_artifact(slug, projects.DRAFT):
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
    ids = [p["id"] for p in load()]
    if phase["id"] == ids[-1]:          # the last phase: approving it closes the book where it is
        return state(slug)
    return go_to(slug, ids[ids.index(phase["id"]) + 1])


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
