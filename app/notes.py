"""Showrunner notes — the running commentary you jot while the room works.

Notes are yours, not the room's: half-thoughts, tangents, "oh yeah, and…". They pile up in
the campaign's production/showrunner-notes.json until something uses them, then they're marked used
(nothing is ever deleted unless you drop it):

    the next round      start_round folds pending notes into the room's brief
    a review            submit() adds them to review.md and saves them in the round folder
    Tidy into feedback  one model call that turns the pile into organized feedback you can edit

Each note keeps when it was written, which page you were looking at, and which round was
running, so late thoughts can be told from early ones.
"""
import json
import time

from . import llm, projects, usage
from .agents import load_roles

FILE = "showrunner-notes.json"
SYNTHESIS_ROLE = "director"
PROMPT = """You are the showrunner's assistant on a graphic novel. Below are notes the showrunner
jotted down while the room worked — a raw stream, out of order, some half-finished, some
contradicting each other, some about pages, some about the whole book.

Turn them into feedback the room can act on:

- Group them by theme, and put the biggest thing first.
- Keep the showrunner's own words and intent. Don't invent notes, don't soften them, don't
  add craft advice of your own.
- Where two notes disagree, say so instead of picking one.
- Note which page a note is about when it says.
- End with a short "Later thoughts win" line only if a later note overrides an earlier one.

Markdown, no preamble, no more than 400 words."""


def _path(slug):
    return projects.project_dir(slug) / FILE


def _all(slug):
    p = _path(slug)
    return json.loads(p.read_text()) if p.exists() else []


def _save(slug, notes):
    _path(slug).write_text(json.dumps(notes, indent=2))


def add(slug, text, page=None):
    text = (text or "").strip()
    if not text:
        raise ValueError("a note needs some text")
    notes = _all(slug)
    rounds = projects.list_versions(slug)
    note = {"id": max([n["id"] for n in notes], default=0) + 1, "t": time.time(), "text": text,
            "page": page, "round": rounds[0]["id"] if rounds else None, "used_in": None}
    notes.append(note)
    _save(slug, notes)
    return note


def pending(slug):
    return [n for n in _all(slug) if not n["used_in"]]


def drop(slug, note_id):
    _save(slug, [n for n in _all(slug) if n["id"] != note_id])


def mark_used(slug, ids, where):
    notes = _all(slug)
    for n in notes:
        if n["id"] in ids:
            n["used_in"] = where
    _save(slug, notes)


def markdown(notes, heading="Showrunner's notes, jotted while the room worked"):
    """The raw pile, oldest first, with the time and page each was written at."""
    if not notes:
        return ""
    lines = [f"## {heading}", "",
             "These are off-the-cuff thoughts, not orders. Weigh them, take what serves the book, "
             "and say in your handoff note what you did with the rest.", ""]
    for n in sorted(notes, key=lambda n: n["t"]):
        when = time.strftime("%H:%M", time.localtime(n["t"]))
        where = f", page {n['page']}" if n.get("page") else ""
        lines.append(f"- _{when}{where}_ — {n['text']}")
    return "\n".join(lines) + "\n"


def take(slug, where):
    """Pending notes as markdown, marked used by `where` (a round id). '' when there are none."""
    notes = pending(slug)
    if not notes:
        return ""
    mark_used(slug, [n["id"] for n in notes], where)
    return markdown(notes)


def synthesize(slug):
    """One model call: the pending notes turned into organized feedback. Doesn't mark them used —
    the text comes back for you to edit, and the notes are spent when a round or review takes them."""
    notes = pending(slug)
    if not notes:
        raise ValueError("no notes to tidy up yet")
    role = next((r for r in load_roles() if r.id == SYNTHESIS_ROLE), None)
    if role is None:
        raise ValueError(f"no {SYNTHESIS_ROLE} role to do the tidying")
    cfg = role.config()
    log = usage.LedgerLogger(slug, "showrunner_notes")
    reply = llm.chat(cfg, [{"role": "system", "content": PROMPT},
                           {"role": "user", "content": markdown(notes, "Notes")}], log=log)
    return {"text": (reply.get("content") or "").strip(), "notes": len(notes), "model": cfg.model,
            "cost_usd": log.totals["cost_usd"]}
