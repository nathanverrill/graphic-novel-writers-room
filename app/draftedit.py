"""The Draft Editor: the showrunner's drafts, brought into line with the canon, then grown to size.

In edit mode (draft_mode "edit") the book is the showrunner's drafts. After development settles
the canon, the Draft Editor goes through each chapter of draft.md in two stages.

**The canon pass.** Against the brief, characters.md, world.md, story.md, facts.md, the
showrunner's rules and the voice tuning from Voices, it

    edits      only what the canon contradicts - a scene, a name, an age, a fact, a rule - and
               dialogue that breaks how the canon says these people talk: the dialogue and slang
               rules in rules/, each character's Voice, the voice tuning. Everything else comes
               back word for word, in the draft's own form.
    lists      every change: where, what it was, what it is now, and the canon it follows.
    flags      what in the story no longer fits the canon and cannot be fixed by a small edit.
               It is not rewritten: the showrunner decides.
    counts     the pages the chapter fills when drawn (below).

**The expansion** (expand_pages > 0). The pages are shared out where the drafts are thinnest
against the page plot in story.md, and each chapter grows by its share: new beats between the
showrunner's beats - a payoff the canon sets up, a canon character with no moment, a transition
the draft jumps, a breather after a reveal - steered by the showrunner's note. Nothing of theirs
is changed, moved or cut; every addition is marked [NEW] and listed with why it is there.

**Pages are counted for an image model, not by comic convention.** Each page is drawn in one
generation, from the character and location sheets, and a page drifts when it carries too much:
so at most max_panels panels a page and max_characters named characters a panel, one location
a page where the story allows. The count the chapters come to becomes the book's page count, so
the script and the layouts are made to it.

One call per chapter per stage, side by side. A reply that has lost material is asked for once
more, then refused: the chapter stays as it was.

    draft-edited.md    the canon pass: the chapters, edited, in the draft's own form
    draft-final.md     the book: the edited chapters, expanded; the script is made from this
    draft-changes.md   per chapter: the changes, the additions, what does not fit, the pages;
                       and which characters in the book still need a sheet
"""
import concurrent.futures
import os
import re
import threading
from pathlib import Path

from . import llm, projects, review, voices
from .usage import CallLogger

EDITED, FINAL, CHANGES = "draft-edited.md", "draft-final.md", "draft-changes.md"
CANON = ("brief.md", "characters.md", "world.md", "story.md", "facts.md")
SHORTEST = 0.8          # of the chapter as it went in: shorter than this, the edit lost material
KEPT_WHOLE = 0.9        # of the edited chapter's paragraphs an expansion must still carry, word for word
TRIES = 3
WORKERS = 6
OUTPUT_TOKENS = 16000
EDIT_MARKS = ("<<<CHAPTER>>>", "<<<CHANGES>>>", "<<<DOES NOT FIT>>>", "<<<PAGES>>>")
GROW_MARKS = ("<<<CHAPTER>>>", "<<<ADDED>>>", "<<<PAGES>>>")
SHEETS_DIR = Path(os.getenv("SHEETS_CHARACTERS") or Path(__file__).resolve().parent.parent / "sheets" / "characters")
TITLES = {"director", "dr", "dr.", "doctor", "mr", "mrs", "ms", "the", "captain", "old", "young"}


def drawability(slug):
    st = review.settings(slug)
    panels, people = int(st.get("max_panels") or 4), int(st.get("max_characters") or 3)
    return (f"Pages are drawn by an image model, one page per generation, from each character's and "
            f"location's sheet, and a page drifts when it carries too much. So: at most {panels} panels "
            f"a page; at most {people} named characters in one panel; one location a page where the "
            f"story allows (every new location needs its own sheet); no crowd that must be recognisable; "
            f"a big moment gets a splash (one panel, the whole page). Count pages this way, not by comic "
            f"convention.")


SYSTEM = """You are the Draft Editor in a graphic-novel writers' room. The showrunner wrote these
drafts; the room has since settled the canon. Your job is to bring one chapter of the draft into
line with the canon, and nothing more.

You change two things, and only these:

1. What the canon contradicts or has settled differently: a scene, a beat, a name, an age, a
   number, a place, a rule of the world, who knows what when.
2. Dialogue that does not sound the way the canon says these people talk. Every quoted line is
   checked against the showrunner's dialogue rules in rules/ (slang, vocabulary, the language of
   each city and class, words that must never leak from the author into a character's mouth),
   against that character's Voice in characters.md, and against any voice tuning the showrunner
   gave from talking with them. A line that breaks them is re-said in the character's own words
   and slang: the same meaning, the same beat, about the same length, as few words changed as
   the rules need. A line that already fits is not touched, however you might have written it.

- Everything else comes back exactly as it is: the same form, headings, order, wording, narration
  and emphasis. Do not improve, tighten, restructure, summarize or add. Do not write script,
  panels, new scenes or new lines of dialogue.
- Where the story itself no longer fits the canon - a scene depends on something the canon ruled
  out, and no small edit can fix it - do NOT rewrite it. Leave it as it is and flag it.
- Then count the pages this chapter fills when drawn, under the drawability rules you are given.

Reply in exactly four parts, with these markers on lines of their own:

<<<CHAPTER>>>
the whole chapter, edited
<<<CHANGES>>>
- **Where** (section or scene): was "..." -> now "..." - why, citing the canon file or rule (e.g. characters.md, Bi11bot; rules/vocabulary.md, Keel slang)
(or "- none" if nothing needed changing)
<<<DOES NOT FIT>>>
- **Where**: what does not fit, which canon it conflicts with, and the choices the showrunner has
(or "- none")
<<<PAGES>>>
one whole number: the pages this chapter fills"""

GROW = """You are the Draft Editor in a graphic-novel writers' room. The showrunner's chapter below is
already in line with the canon. Your job now is to grow it by about {pages} page(s), and to
change nothing that is there.

- Every word of the chapter stays, in its order: every heading, paragraph, beat and quoted line.
  You only insert.
- Insert new beats between the showrunner's beats, where the chapter is thin: a payoff the canon
  sets up that has no scene, a canon character who is in the story but has no moment, a
  transition the draft jumps over, a breather after a big reveal, a beat that makes a choice
  land. Take what the canon already holds; the showrunner's note, if there is one, steers what.
- No new subplots, no named characters the canon does not have, nothing that contradicts the
  canon or gets ahead of the story. New dialogue follows the dialogue rules and each character's
  Voice exactly as the showrunner's own lines do.
- Write each addition in the draft's own form and register, and mark it: a line reading
  `[NEW {chapter}.1]` (then .2, .3 ...) before it, and `[/NEW]` after it.
- Size the additions to the pages asked for, counted under the drawability rules you are given.

Reply in exactly three parts, with these markers on lines of their own:

<<<CHAPTER>>>
the whole chapter, with the additions marked
<<<ADDED>>>
- **[NEW {chapter}.1]** after "...": what it adds, why (the gap it fills or the setup it pays off), about how many pages
<<<PAGES>>>
one whole number: the pages the whole chapter now fills"""


def chapters(draft):
    """[(name, text)] from draft.md: one "## chapter-01-draft.md" section per draft file."""
    parts = re.split(r"^## (\S+\.md)\s*$", draft or "", flags=re.M)
    return [(parts[i], parts[i + 1].strip()) for i in range(1, len(parts) - 1, 2)]


def split(reply, marks):
    """The parts between the markers, in order, or None when a marker is missing."""
    if not all(m in (reply or "") for m in marks):
        return None
    out, rest = [], reply.split(marks[0], 1)[1]
    for m in marks[1:]:
        part, rest = rest.split(m, 1)
        out.append(part.strip())
    out.append(rest.strip())
    return out


def parse(reply):
    """The canon pass: (chapter, changes, does_not_fit, pages), or None."""
    got = split(reply, EDIT_MARKS)
    return got and (got[0], got[1] or "- none", got[2] or "- none", number(got[3]))


def number(text):
    m = re.search(r"\d+", text or "")
    return int(m.group()) if m else None


def paragraphs(text):
    return [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text or "") if p.strip()]


def kept_whole(before, after):
    """How much of the chapter an expansion still carries, paragraph by paragraph, word for word."""
    old = paragraphs(before)
    new = re.sub(r"\s+", " ", after or "")
    return sum(1 for p in old if p in new) / len(old) if old else 1.0


def planned(slug, n):
    """Pages story.md's page plot gives each chapter, in order: "### Chapter 1" and its Page lines."""
    text = projects.read_artifact(slug, "story.md") or ""
    counts = []
    for block in re.split(r"^#{2,3}\s+Chapter\b", text, flags=re.M | re.I)[1:]:
        pages = re.findall(r"^\s*\**Page\s+\d+", block.split("\n## ", 1)[0], re.M | re.I)
        if pages:
            counts.append(len(pages))
    return counts if len(counts) == n else [None] * n


def share(total, estimates, plan):
    """The expansion's pages, chapter by chapter: first where a chapter falls short of its planned
    pages, then evenly. Whole pages, adding up to the total."""
    if total <= 0:
        return [0] * len(estimates)
    gaps = [max(0, (p or 0) - (e or 0)) for e, p in zip(estimates, plan)]
    weights = gaps if sum(gaps) else [1] * len(estimates)
    raw = [total * w / sum(weights) for w in weights]
    out = [int(r) for r in raw]
    for i in sorted(range(len(raw)), key=lambda i: raw[i] - out[i], reverse=True)[:total - sum(out)]:
        out[i] += 1
    return out


def needs_sheets(slug, text):
    """Characters of the canon who appear in the book and have no sheet yet."""
    missing = []
    for c in voices.characters(slug):
        words = [w for w in re.findall(r"[\w'-]+", c["name"]) if w.lower() not in TITLES]
        if not words or not re.search(rf"\b{re.escape(words[0])}\b", text, re.I):
            continue
        d = SHEETS_DIR / c["key"]
        has = d.is_dir() and (any(d.glob("lock.*")) or ((d / "set").is_dir() and any((d / "set").iterdir())))
        if not has:
            missing.append(c["name"].title() if c["name"].isupper() else c["name"])
    return missing


class DraftEdit:
    """One round's draft edit. Same shape as Agent from the room's side: .run(note), .log.totals."""

    def __init__(self, role, version, emit, should_stop=lambda: False):
        self.role, self.version, self.slug = role, version, version.slug
        self.cfg = role.config()
        self.emit = emit
        self.should_stop = should_stop
        self.log = CallLogger(version, role.id, emit)
        self._lock = threading.Lock()

    def canon(self):
        parts = []
        for name in CANON:
            body = projects.read_artifact(self.slug, name) or ""
            if body.strip():
                parts.append(f"# {name}\n\n{body}")
        rules = projects.campaign_dir(self.slug) / projects.RULES
        for f in sorted(rules.glob("*.md")) if rules.is_dir() else []:
            parts.append(f"# rules/{f.name} - the showrunner's, binding\n\n{f.read_text()}")
        for name, body in voices.all_tuning_md(self.slug):      # from talking with the characters
            parts.append(f"# voices/{name} - the showrunner's voice tuning\n\n{body}")
        parts.append(f"# Drawability - how pages are counted\n\n{drawability(self.slug)}")
        return "\n\n".join(parts)

    def ask(self, system, marks, name, user):
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        for attempt in range(1, TRIES + 1):
            if self.should_stop():
                raise RuntimeError("stopped")
            self.emit("thinking", step=name, attempt=attempt, model=self.cfg.model, input_chars=len(user))
            try:
                reply = llm.text_of(llm.chat(self.cfg, messages, log=self.log, max_tokens=OUTPUT_TOKENS))
            except llm.LLMError as e:
                self.emit("warn", text=f"{name}, attempt {attempt}: the request failed ({e.status}): {str(e)[:160]}")
                continue
            got = split(reply, marks)
            if got:
                return got
            self.emit("warn", text=f"{name}, attempt {attempt}: the reply was not in its {len(marks)} parts; asking again.")
        raise RuntimeError(f"{name}: no usable reply after {TRIES} attempts")

    def edit(self, name, text, canon, note):
        """The canon pass on one chapter: (edited, changes, does_not_fit, pages)."""
        self.emit("message", text=f"Editing {name} against the canon.")

        def once(again):
            user = "\n\n".join(filter(None, [
                "# The canon\n\n" + canon,
                f"# Note from the showrunner\n\n{note}" if note else "",
                f"# The chapter to edit: {name}\n\n{text}",
                ("# Again, whole\nYour last reply was far shorter than the chapter. Return the ENTIRE "
                 "chapter, every section and line, word for word except where the canon changes it.") if again else ""]))
            got = self.ask(SYSTEM, EDIT_MARKS, name, user)
            return got[0], got[1] or "- none", got[2] or "- none", number(got[3])

        edited, changes, misfit, pages = once(False)
        if len(edited) < SHORTEST * len(text):
            self.emit("warn", text=f"{name} came back at {len(edited) / len(text):.0%} of the chapter; asking once more for all of it.")
            edited, changes, misfit, pages = once(True)
            if len(edited) < SHORTEST * len(text):
                self.emit("warn", text=f"{name} was short again; it stays as you wrote it.")
                return text, "- none: the edit came back short twice, so the chapter is unchanged.", misfit, pages
        return edited, changes, misfit, pages

    def grow(self, i, name, text, pages, canon, note):
        """The expansion of one chapter by `pages`: (chapter, added, pages)."""
        self.emit("message", text=f"Growing {name} by {pages} page(s).")
        system = GROW.format(pages=pages, chapter=i + 1)

        def once(again):
            user = "\n\n".join(filter(None, [
                "# The canon\n\n" + canon,
                f"# The showrunner's note on the expansion\n\n{note}" if note else "",
                f"# The chapter to grow by about {pages} page(s): {name}\n\n{text}",
                ("# Again, whole\nYour last reply dropped or changed the showrunner's text. Every "
                 "paragraph of the chapter must come back word for word; only insert.") if again else ""]))
            got = self.ask(system, GROW_MARKS, name, user)
            return got[0], got[1] or "- none", number(got[2])

        grown, added, total = once(False)
        if kept_whole(text, grown) < KEPT_WHOLE:
            self.emit("warn", text=f"{name}: the expansion kept only {kept_whole(text, grown):.0%} of the chapter word for word; asking again.")
            grown, added, total = once(True)
            if kept_whole(text, grown) < KEPT_WHOLE:
                self.emit("warn", text=f"{name}: the expansion changed the chapter again; it stays as edited, not grown.")
                return text, "- none: the expansion changed the showrunner's text twice, so the chapter was not grown.", None
        return grown, added, total

    def run(self, note=None):
        parts = chapters(projects.read_artifact(self.slug, projects.DRAFT) or "")
        if not parts:
            raise RuntimeError("there is no draft to edit: draft.md has no chapters")
        canon = self.canon()
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
            edits = list(pool.map(lambda nt: self.edit(nt[0], nt[1], canon, note), parts))

        want = int(review.settings(self.slug).get("expand_pages") or 0)
        before = [e[3] or 0 for e in edits]
        plan = planned(self.slug, len(parts))
        shares = share(want, before, plan)
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
            grows = list(pool.map(
                lambda i: self.grow(i, parts[i][0], edits[i][0], shares[i], canon, note) if shares[i]
                else (edits[i][0], "- none", before[i]), range(len(parts))))
        after = [g[2] if g[2] is not None else before[i] for i, g in enumerate(grows)]

        edited = ["# The showrunner's draft, edited to the canon", "",
                  "Changed only where the canon required it; every change is in draft-changes.md.", ""]
        final = ["# The book: the showrunner's draft, edited to the canon" + (" and expanded" if want else ""), "",
                 "What the script is made from. Additions are marked [NEW]; every change and addition is in draft-changes.md.", ""]
        report = ["# What the Draft Editor changed, added, and found that does not fit", ""]
        changed = added_n = misfits = 0
        rows = []
        for i, (n, _) in enumerate(parts):
            text, changes, misfit, _ = edits[i]
            grown, added, _ = grows[i]
            edited += [f"## {n}", "", text, ""]
            final += [f"## {n}", "", grown, ""]
            report += [f"## {n}", "", "### Changed", "", changes, "", "### Added", "", added, "",
                       "### Does not fit the canon", "", misfit, ""]
            changed += count(changes)
            added_n += count(added)
            misfits += count(misfit)
            rows.append(f"| {n} | {plan[i] if plan[i] is not None else '-'} | {before[i]} | +{shares[i]} | {after[i]} |")
        pages = sum(after)
        book = "\n".join(final)
        missing = needs_sheets(self.slug, book)
        head = ["## Pages", "", drawability(self.slug), "",
                "| chapter | page plot | as drafted | added | now |", "|---|---|---|---|---|", *rows,
                f"| **the book** | {sum(p or 0 for p in plan) or '-'} | {sum(before)} | +{sum(shares)} | **{pages}** |", "",
                f"The book is set to {pages} pages: the script and the layouts are made to it.", "",
                "## Sheets still needed", "",
                ("Every character in the book with no sheet yet - draw them in Sheets before the pages: "
                 + ", ".join(missing) + ".") if missing else "Every character in the book has a sheet.", ""]
        report[2:2] = head
        for name, body in ((EDITED, "\n".join(edited)), (FINAL, book), (CHANGES, "\n".join(report))):
            self.version.write(name, body)
            self.emit("artifact", name=name)
        if pages:
            review.save_settings(self.slug, pages=pages)
        summary = (f"Edited {len(parts)} chapters to the canon: {changed} change(s), {misfits} place(s) that do not "
                   f"fit" + (f"; grew them by {added_n} addition(s)" if want else "") +
                   f". The book is {pages} pages. " + (f"Still to sheet: {', '.join(missing)}. " if missing else "")
                   + "See draft-changes.md.")
        self.version.append_log(self.role.title, summary)
        return summary


def count(listing):
    return 0 if re.match(r"-\s*\**none", listing or "", re.I) else len(re.findall(r"^\s*-\s", listing, re.M))
