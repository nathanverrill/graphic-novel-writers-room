"""Intake: five passes, no tools, and the room owns every file.

    pass 1  synthesis    input/ + rules/ (+ references/)  -> characters, world, story
                         THREE CALLS IN PARALLEL, one per file
    pass 2  open items   those three, no references       -> open-items.md
    pass 3  options      those items + references         -> open-items.md with options
            -- the run stops: awaiting_showrunner_decisions --
    pass 4  revision     decisions + weighted notes       -> the three files, in parallel
                                                          -> then open-items.md
    pass 5  facts        the revised three                -> facts.md

**Every specialist gets the whole room, but only one job.** Each synthesis call reads all of
the showrunner's material and writes one file. That is not an optimization, it is the whole
design: character detail turns up in a chapter draft, a world rule turns up in dialogue, a
story beat turns up in a character note, so routing source files to destinations by their names
would lose exactly the material intake exists to find. Read broadly, write narrowly.

It is also what makes the output usable. Asked for several long files in one reply, a model
spends its budget on the first and compresses the rest - measured on Prosperity at 38-52% of
source, with the last file half empty. One call per file gives each its own output allowance.

The three calls are independent views of one snapshot. They may read an ambiguity differently -
characters.md saying Leona chose exile while story.md says she was forced out - and that is
fine. Pass 2 exists to catch exactly that. There is no hidden reconciliation step in pass 1.

The model's job is meaning; this module's job is everything else: what goes into each prompt,
what comes back, whether it is usable, what gets written, what gets retried and whether the run
may call itself done.
"""
import concurrent.futures
import hashlib
import json
import re
import shutil
import threading

from . import llm, openitems, projects, review, rules as rules_mod
from .config import DEBUG_DIR
from .agent import Stopped
from .agents import gather_context
from .usage import CallLogger

CORE = ("characters.md", "world.md", "story.md")
FACTS = "facts.md"
ITEMS = openitems.ITEMS

SYNTHESIS, OPEN_ITEMS, OPTIONS = "synthesis", "open items", "options"
REVISION, FACTS_PASS = "revision", "facts"

PASS_GUIDE = {SYNTHESIS: "synthesis.md", OPEN_ITEMS: "open-items.md", OPTIONS: "options.md",
              REVISION: "revision.md", FACTS_PASS: "facts.md"}
DEST_GUIDE = {"characters.md": "synthesis-characters.md",
              "world.md": "synthesis-world.md",
              "story.md": "synthesis-story.md"}
ROLE_GUIDES = set(PASS_GUIDE.values()) | set(DEST_GUIDE.values())

SYNTHESIZING, IDENTIFYING, GENERATING = "synthesizing", "identifying_open_items", "generating_options"
AWAITING = "awaiting_showrunner_decisions"
REVISING, DERIVING = "revising", "deriving_facts"
READY, FAILED = "ready_for_review", "failed"

TRIES = 3               # attempts at one call before that call fails
WORKERS = 3             # calls in flight at once
OUTPUT_TOKENS = 64000   # each file's own allowance, set near the model ceiling: a file that
                        # runs long should run long, not come back cut off
SOFT_INPUT_CHARS = 700_000      # ~175k tokens: a ceiling well under any 1M window, because a
                                # model's advertised context is not its good working range
MIN_CHARS = 200         # below this it is noted as a fragment - and still used

# Preservation telemetry. Measured across the whole output set, never file by file, and
# against the showrunner's own material and the rules - never the research shelf, which is
# there to improve the thinking rather than to be reproduced.
#
# These are DIAGNOSTICS, not gates. They are recorded in run.json, shown in the feed, and used
# to compare models and prompts or to tell the showrunner a synthesis is worth a look. They
# never discard a reply and never rerun a pass: a model is not a deterministic function, and
# what it wrote is what the room has. The only retry-worthy failure is an empty reply.
MATURE_CHARS = 8000
MIN_COVERAGE = 0.85     # below this, say so in the feed and run.json - and keep the output
MIN_MASS = 0.30         # likewise: a mark to notice, not a floor to enforce
TERM_HITS = 2

LABELS = ("established", "research", "inferred", "invented")
FENCE = re.compile(r"\A```[a-z]*\n(.*)\n```\Z", re.S)
STRAY = re.compile(r"^<<<(?:FILE:[^>]*|END FILE)>>>\s*$", re.M)
PREAMBLE = re.compile(r"\A\s*(here is|here's|sure|certainly|okay|of course|i have|below is|"
                      r"i've)\b[^\n]*\n+(?=#)", re.I)

COMMON = {
    "The", "This", "That", "These", "Those", "There", "Then", "They", "Their", "Them", "When",
    "What", "Where", "Which", "While", "With", "Without", "Would", "Could", "Should", "But",
    "And", "For", "Not", "Now", "One", "Two", "Three", "Its", "It", "His", "Her", "She", "He",
    "You", "Your", "Our", "All", "Any", "Each", "Every", "Some", "Most", "More", "Much", "Many",
    "Because", "Before", "After", "Above", "Below", "Open", "Note", "Notes", "From", "Into",
    "Only", "Also", "Both", "Even", "Here", "How", "Why", "Who", "Yes", "Nothing", "Something",
    "Everything", "Anything", "Nobody", "Someone", "Everyone", "Chapter", "Page", "Pages",
    "Part", "Section", "Characters", "World", "Story", "Facts", "Look", "Voice", "Relationships",
    "Habits", "Drafts", "Rules", "Input", "References", "If", "In", "On", "At", "As", "Is",
    "Are", "Was", "Were", "Been", "Being", "Have", "Has", "Had", "Do", "Does", "Did", "Can",
    "May", "Might", "Must", "Will", "Shall", "So", "Or", "Nor", "Yet", "Still", "Just", "Very",
}


def debug_folder(model):
    """debug/<model>/ - one folder per model, so runs can be compared side by side."""
    return DEBUG_DIR / re.sub(r"[^a-z0-9.]+", "-", (model or "unknown").lower()).strip("-")


def start_debug(slug, round_id, model):
    """Empty this model's debug folder for a fresh run.

    Every prompt the room sends and every raw reply the provider returns, on disk, in the
    order they happened. The round's own calls/ folder holds the same thing in one file per
    call; this is the flat, readable version for looking at a run by hand. Each model gets its
    own folder, so a comparison run does not wipe the one before it."""
    DEBUG_DIR_MODEL = debug_folder(model)
    try:
        # Empty it, never remove it: debug/ is a bind mount in the container and rmtree on a
        # mount point fails with "device or resource busy", which would quietly disable the dump.
        DEBUG_DIR_MODEL.mkdir(parents=True, exist_ok=True)
        for child in DEBUG_DIR_MODEL.iterdir():
            shutil.rmtree(child) if child.is_dir() else child.unlink()
        for sub in ("sent", "received"):
            (DEBUG_DIR_MODEL / sub).mkdir(parents=True, exist_ok=True)
        (DEBUG_DIR_MODEL / "README.txt").write_text(
            f"Intake debug dump\n"
            f"campaign: {slug}\nround:    {round_id}\nmodel:    {model}\n"
            f"written:  {projects.now()}\n\n"
            f"sent/      one file per model call: the system prompt, then the user message.\n"
            f"received/  the provider's full JSON response for that call.\n"
            f"index.json what was asked for, what came back, and how big.\n\n"
            f"Cleared at the start of the next run on this model; other models are untouched.\n")
        return True
    except Exception as e:
        print(f"intake: debug dump disabled ({type(e).__name__}: {e})", flush=True)
        return False


class IntakeError(Exception):
    """A pass failed. The run stops here - it does not go on and it does not report done."""


# ---- reading what came back -------------------------------------------------

def clean(text):
    """One file's markdown, as the model returned it.

    Every call writes exactly one file, so there is no envelope to parse: the reply is the
    document. This strips what a model adds anyway - a code fence, a stray file marker, a line
    of "Here is the..." before the first heading - and nothing else."""
    text = (text or "").strip()
    m = FENCE.match(text)
    if m:
        text = m.group(1).strip()
    text = STRAY.sub("", text).strip()
    return PREAMBLE.sub("", text).strip()


TOPIC_WORDS = {"open", "overview", "what", "characters", "people", "cast", "notes", "sources",
               "summary", "contents", "feedback"}


def repair(name, content):
    """Put the document into the shape the room needs, and say what was changed.

    Formatting is the room's job, not a reason to throw a reply away. A model that wrote a good
    characters file and forgot the `## Characters` wrapper has done the work; discarding it and
    asking again costs money, loses that work and usually comes back worse. So shape is fixed
    here, after the reply, and only genuinely unusable content is retried."""
    fixed, done = content.strip(), []
    if not fixed:
        return "", []        # nothing to shape; an empty reply must stay empty
    if not re.match(r"^#\s+\S", fixed):
        title = name[:-3].replace("-", " ").title()
        fixed = f"# {title}\n\n{fixed}"
        done.append(f"added a '# {title}' title")

    if name == "characters.md" and not re.search(r"^##\s+Characters\s*$", fixed, flags=re.M):
        # names may have come back at ## level, or under some other wrapper heading
        if not re.search(r"^###\s+\S", fixed, flags=re.M):
            def demote(m):
                head = m.group(1).strip()
                first = head.split()[0].lower().strip(":") if head.split() else ""
                return m.group(0) if first in TOPIC_WORDS else f"### {head}"
            before = fixed
            fixed = re.sub(r"^##\s+(\S.*)$", demote, fixed, flags=re.M)
            if fixed != before:
                done.append("moved character headings from ## to ###")
        m = re.search(r"^###\s+\S", fixed, flags=re.M)
        if m:
            fixed = fixed[:m.start()] + "## Characters\n\n" + fixed[m.start():]
            done.append("added the '## Characters' section heading")

    if name == ITEMS:
        before = fixed
        # field lines the screen cannot read, in any of the ways a model bolds them:
        #   - **file:** x   - **file**: x   **file:** x   - _file_: x
        fixed = re.sub(r"^\s*[-*]?\s*[*_]{1,2}\s*([A-Za-z]{2,})\s*:?\s*[*_]{1,2}\s*:?\s*",
                       r"- \1: ", fixed, flags=re.M)
        if fixed != before:
            done.append("rewrote bolded field lines as '- field: value'")
        heads = re.findall(r"^##\s+(\S.*)$", fixed, flags=re.M)
        unnumbered = [h for h in heads if not re.match(r"\d+[.)]", h.strip())
                      and h.strip().rstrip(":").lower() not in openitems.FEEDBACK_HEADS]
        if unnumbered and len(unnumbered) == len(heads):
            n = [0]
            def number(m):
                head = m.group(1).strip()
                if head.rstrip(":").lower() in openitems.FEEDBACK_HEADS:
                    return m.group(0)
                n[0] += 1
                return f"## {n[0]}. {head}"
            fixed = re.sub(r"^##\s+(\S.*)$", number, fixed, flags=re.M)
            done.append(f"numbered {n[0]} unnumbered items")
    return fixed.strip(), done


def shape_notes(name, content):
    """Shape worth mentioning but not worth fixing or failing over."""
    heads = re.findall(r"^(#{1,6})\s+\S", content, flags=re.M)
    out = []
    if name == "world.md" and len([h for h in heads if h == "##"]) < 3:
        out.append("fewer than three '##' topic sections")
    if name == "story.md" and len([h for h in heads if h == "##"]) < 2:
        out.append("fewer than two '##' sections")
    if name == FACTS and not re.search(r"^\s*[-*]\s*\[", content, flags=re.M):
        out.append("no '- [T] ...' fact lines; it reads as prose")
    if name == "characters.md" and not re.search(r"^###\s+\S", content, flags=re.M):
        out.append("not one '### NAME' heading: no character is written up")
    return out


def items_problems(text, need_options):
    """Thinness in an open-items list, item by item. All of it is a note, none of it fails a
    call: a missing label is a thing to fix or ask about, not a thing to pay for twice."""
    problems, notes_ = [], []
    for item in openitems.parse(text):
        where = f"item {item['n']}"
        if not item["why"]:
            notes_.append(f"{where} has no '- why:' line")
        if not need_options:
            continue
        if not item["options"]:
            problems.append(f"{where} has no lettered options, which is this pass's whole job")
            continue
        for o in item["options"]:
            if not any(f"[{l}]" in o["text"].lower() for l in LABELS):
                problems.append(f"{where}, option {o['id']}: no source label - every option "
                                f"needs one of [{']/['.join(LABELS)}]")
        if not item["suggested"]:
            notes_.append(f"{where} has no '- suggested:' line")
    return problems, notes_


def validate(name, content, truncated=False, want_items=True, need_options=False):
    """(problems, notes) for one call's reply.

    A **problem** means there is nothing to use, and only then is the call worth making again:
    the request failed, or the reply came back empty. That is the whole list.

    Everything else is a **note**. A model is a model, not a deterministic function: it will
    sometimes hand back a short file, an items list the parser cannot read, an option without
    its source label, a file that ran to the token ceiling. None of that is a reason to spend
    another call and throw the work away. What it wrote is what the room has, and shaping it is
    the room's job, after the fact - see repair() and shape_notes()."""
    if not content.strip():
        return ["nothing came back"], []
    notes_ = []
    if truncated:
        notes_.append("ran to the token ceiling, so the end may be missing")
    if re.search(r"^\s*(#+\s*)?(i'm sorry|i am sorry|i cannot|i can't|as an ai|unfortunately, i)",
                 content, flags=re.I):
        notes_.append("reads like a refusal rather than a document")
    if len(content.strip()) < MIN_CHARS:
        notes_.append(f"only {len(content.strip())} characters")
    notes_ += shape_notes(name, content)
    if name == ITEMS:
        if want_items and not openitems.parse(content):
            notes_.append("no numbered items could be read out of it")
        else:
            _p, n = items_problems(content, need_options)
            notes_ += _p + n
    return [], notes_


# ---- the preservation guard -------------------------------------------------

def terms(text):
    """The distinctive words and numbers in a piece of text: names, places, coined terms,
    quantities. Deliberately crude - it counts what a summary drops, it does not parse English."""
    found = re.findall(r"\b[A-Z][A-Za-z'\-]{2,}\b", text or "")
    found += re.findall(r"\b\d[\d.,]{1,}\b", text or "")
    return [t for t in found if t not in COMMON]


# Formatting and labelling vocabulary: real words that go missing for uninteresting reasons.
# A dropped "Caption" or "Speculation" says nothing about lost story material; a dropped name
# or number might. Sorting them apart makes the telemetry worth reading.
CRAFT_WORDS = {
    "Caption", "Captions", "Panel", "Panels", "Close-up", "Wide", "Insert", "Splash", "Beat",
    "Dialogue", "Balloon", "Gutter", "Spread", "Text-first", "Visual-only", "Chapters",
    "Label", "Labels", "Educated", "Speculation", "Truth", "License", "Licence", "Thorne",
    "Thorne's", "Tyson", "Cut", "Guess", "Source", "Sources", "Established", "Proposal",
    "Research", "Inferred", "Invented", "Working", "Draft", "Scene", "Sequence", "Act",
}


def classify(term):
    """Which kind of thing went missing. Observational only - no category fails anything."""
    if re.match(r"^\d", term):
        return "numbers"
    if term in CRAFT_WORDS or term.rstrip("'s") in CRAFT_WORDS:
        return "craft vocabulary"
    if term.isupper() and len(term) > 2:
        return "on-screen text"          # DETECTED, LOCKED: readouts, signage, UI
    if term.endswith("'s") or term.endswith("'s"):
        return "named entities"
    return "names and terms"


def preservation(sources, outputs):
    """Did the pass keep the material, or summarize it away?

    Measured across the whole output set, so moving a thing between files, merging two accounts
    of it or restructuring a file completely costs nothing. Returns None when there is too
    little source material to judge."""
    source_text = "\n".join(sources.values())
    if len(source_text) < MATURE_CHARS:
        return None
    output_text = "\n".join(outputs.values())
    counts = {}
    for t in terms(source_text):
        counts[t] = counts.get(t, 0) + 1
    distinctive = {t for t, n in counts.items() if n >= TERM_HITS}
    low = output_text.lower()
    missing = sorted(t for t in distinctive if t.lower() not in low)
    coverage = 1.0 if not distinctive else 1 - len(missing) / len(distinctive)
    by_kind = {}
    for t in missing:
        by_kind.setdefault(classify(t), []).append(t)
    # coverage of everything except the craft/labelling vocabulary, which is the number that
    # actually says whether story material survived
    substantive = {t for t in distinctive if classify(t) != "craft vocabulary"}
    lost_sub = [t for t in missing if classify(t) != "craft vocabulary"]
    return {"source_chars": len(source_text), "output_chars": len(output_text),
            "mass": round(len(output_text) / len(source_text), 3),
            "terms": len(distinctive), "missing": len(missing),
            "coverage": round(coverage, 3),
            "substantive_terms": len(substantive),
            "substantive_coverage": round(1 - len(lost_sub) / len(substantive), 3) if substantive else 1.0,
            "dropped_by_kind": {k: sorted(v)[:40] for k, v in sorted(by_kind.items())},
            "dropped_counts": {k: len(v) for k, v in sorted(by_kind.items())},
            "dropped": missing[:60]}


def preservation_warnings(measure):
    """What the telemetry is worth saying out loud. Warnings only - nothing here fails a pass
    or costs another call."""
    if not measure:
        return []
    problems = []
    if measure["coverage"] < MIN_COVERAGE:
        problems.append(
            f"material was lost: {measure['missing']} of {measure['terms']} distinctive names, "
            f"terms and numbers in the source appear nowhere in the three files "
            f"({measure['coverage']:.0%} kept, {MIN_COVERAGE:.0%} is the level worth a look; "
            f"{measure['substantive_coverage']:.0%} once craft vocabulary is set aside). "
            + " · ".join(f"{k}: {', '.join(v[:8])}"
                         for k, v in measure["dropped_by_kind"].items()))
    if measure["mass"] < MIN_MASS:
        short = int(measure["source_chars"] * MIN_MASS) - measure["output_chars"]
        problems.append(
            f"the files together are {measure['output_chars']:,} characters against "
            f"{measure['source_chars']:,} of source ({measure['mass']:.0%}, under the "
            f"{MIN_MASS:.0%} mark by about {short:,} characters). Worth reading before you "
            f"approve it.")
    return problems


# ---- what the showrunner has said -------------------------------------------

WEIGHTS = ("HIGH", "MEDIUM", "LOW")
WEIGHT_RE = re.compile(r"^\s*[-*]?\s*\[(HIGH|MEDIUM|LOW)\]\s*(.+)$", re.I)


def weighted(text):
    """Showrunner notes, split into [HIGH] / [MEDIUM] / [LOW]. Unmarked is MEDIUM: they wrote
    it, so it matters, but it does not outrank one they marked HIGH."""
    out = []
    for block in re.split(r"\n\s*\n|\n(?=\s*[-*]?\s*\[(?:HIGH|MEDIUM|LOW)\])", text or "", flags=re.I):
        block = (block or "").strip()
        if not block:
            continue
        m = WEIGHT_RE.match(block.replace("\n", " "))
        out.append({"weight": m.group(1).upper(), "text": m.group(2).strip()} if m
                   else {"weight": "MEDIUM", "text": block})
    return out


def resolved(slug):
    """Open items the showrunner has settled but the files do not yet reflect."""
    return [i for i in openitems.state(slug)["items"] if i.get("answer")]


def notes(slug):
    """The showrunner talking about the book rather than answering a question."""
    st = openitems.state(slug)
    general = weighted(st["feedback"])
    per_item = [{**w, "n": i["n"], "question": i["question"]}
                for i in st["items"] if i["feedback"] for w in weighted(i["feedback"])]
    return {"general": general, "items": per_item, "any": bool(general or per_item)}


def deferred(slug):
    """Items the showrunner has chosen to leave open for now."""
    return [i for i in openitems.state(slug)["items"] if i["status"] == openitems.DEFERRED]


def pending(slug):
    """Everything waiting to be carried into the files: answers and notes both."""
    answers, said = resolved(slug), notes(slug)
    return {"decisions": answers, "notes": said, "deferred": deferred(slug),
            "any": bool(answers or said["any"])}


class Intake:
    """One intake round. Same shape as Agent from the room's side: .run(note) and .log.totals."""

    def __init__(self, role, version, emit, should_stop=lambda: False, mode=None):
        self.role = role
        self.cfg = role.config()
        self.version = version
        self.slug = version.slug
        self._emit = emit
        self._lock = threading.Lock()       # calls run in parallel; the feed is one list
        self.should_stop = should_stop
        self.settings = review.settings(self.slug)
        self.mode = self.clean_mode(mode) or self.pick_mode()
        self.awaiting = False
        self.run_status = None
        self.edited_before_run = []
        self.log = CallLogger(version, role.id, self.emit)
        self.calls = []
        self.dumped = []
        self.debug_dir = debug_folder(self.cfg.model)
        self.debugging = start_debug(self.slug, version.id, self.cfg.model)

    def emit(self, type, **data):
        with self._lock:
            self._emit(type, **data)

    def dump(self, label, attempt, destination, messages, response, status, error):
        """One call, both sides, on disk under debug/. Never breaks a run."""
        if not self.debugging:
            return
        stem = f"{label}-{destination[:-3]}" + (f"-attempt{attempt}" if attempt > 1 else "")
        try:
            sent = "\n".join(
                [f"# SENT  {label} -> {destination}   attempt {attempt}",
                 f"# model {self.cfg.model}  temperature {self.cfg.temperature}  "
                 f"max_tokens {OUTPUT_TOKENS}",
                 f"# {sum(len(m['content']) for m in messages):,} characters in {len(messages)} messages",
                 "", "=" * 78, "SYSTEM", "=" * 78, "", messages[0]["content"],
                 "", "=" * 78, "USER", "=" * 78, ""] + [m["content"] for m in messages[1:]])
            (self.debug_dir / "sent" / f"{stem}.txt").write_text(sent)
            body = response if isinstance(response, (dict, list)) else {"raw": str(response)}
            (self.debug_dir / "received" / f"{stem}.json").write_text(
                json.dumps({"call": label, "destination": destination, "attempt": attempt,
                            "http_status": status, "error": str(error) if error else None,
                            "response": body}, indent=2, ensure_ascii=False))
            with self._lock:
                self.dumped.append({"call": label, "destination": destination, "attempt": attempt,
                                    "sent": f"sent/{stem}.txt", "received": f"received/{stem}.json",
                                    "input_chars": sum(len(m["content"]) for m in messages),
                                    "http_status": status})
        except Exception as e:
            self.emit("warn", text=f"Couldn't write the debug dump for {label}: {e}")

    @staticmethod
    def clean_mode(mode):
        """"integration" was this pass's name before it grew revision notes."""
        return REVISION if mode == "integration" else mode

    def pick_mode(self):
        if pending(self.slug)["any"] and all(projects.read_artifact(self.slug, n) for n in CORE):
            return REVISION
        return SYNTHESIS

    @property
    def use_references_in_synthesis(self):
        """On by default: have an idea, gather the research that makes it richer, let intake use
        both. A mature project turns it off for a consolidation run."""
        return bool(self.settings.get("use_references_during_synthesis"))

    # ---- the material ----------------------------------------------------

    def material(self, kinds, skip=()):
        out = []
        for name, path in projects.reference_files(self.slug).items():
            kind = projects.reference_kind(path)
            if name in skip or kind not in kinds:
                continue
            out.append((kind, name, path.read_text(errors="replace")))
        return sorted(out, key=lambda r: (list(kinds).index(r[0]), r[1]))

    def reserved(self):
        """input/open-items.md is the showrunner's question list, not synthesis material: it
        goes to pass 2, which reconciles it, and nowhere else."""
        return f"{self.slug}/{projects.INPUT}/{ITEMS}"

    def synthesis_kinds(self):
        kinds = [projects.RULES, projects.INPUT, projects.DRAFTS]
        if self.use_references_in_synthesis:
            kinds.append(projects.REFERENCES)
        return kinds

    def sources(self, kinds=None):
        kinds = self.synthesis_kinds() if kinds is None else kinds
        return {name: body for _, name, body in self.material(kinds, skip={self.reserved()})}

    def guarded(self):
        """What the guard measures against: the showrunner's own material and the rules, never
        the research shelf. Research improves the thinking; most of a good shelf should rightly
        leave no trace, and measuring against it would demand the files transcribe it."""
        return self.sources([projects.RULES, projects.INPUT, projects.DRAFTS])

    def snapshot(self, files):
        """A fingerprint of exactly what the parallel calls were given, so a set of outputs can
        never be half from one state of the material and half from another."""
        h = hashlib.sha256()
        for name in sorted(files):
            h.update(name.encode())
            h.update(hashlib.sha256(files[name].encode()).digest())
        return h.hexdigest()[:16]

    # ---- prompts ---------------------------------------------------------

    def guides(self, pass_name):
        """The role's shared guides plus this pass's. A destination guide is not here: it goes
        at the end of the user message, so the whole prefix is identical across parallel calls
        and a provider that caches prefixes can reuse it."""
        keep = PASS_GUIDE[pass_name]
        got, _images = gather_context(self.role, lambda m: self.emit("warn", text=m))
        return [(label, text) for label, text in got
                if label.rpartition("/")[2] not in ROLE_GUIDES - {keep}]

    def guide_text(self, filename):
        path = self.role.dir / filename
        return path.read_text() if path.exists() else ""

    def system_prompt(self, pass_name):
        return "\n\n".join([
            f"You are the {self.role.title} in a graphic novel writers' room.",
            self.role.mission,
            "# Your guides",
            *[f"## {label}\n\n{text}" for label, text in self.guides(pass_name)],
            "# How to answer\n"
            "You have no tools. Return the complete markdown of the one artifact you are asked "
            "for. Write it as long as the material deserves - there is room, and a file that "
            "runs long should run long. Do not stop early to be tidy, do not summarize to fit, "
            "and do not add commentary about what you did. The room takes what you write, "
            "tidies the formatting if it needs to, and saves it.",
        ])

    def payload(self, note):
        """The shared source payload - identical for every parallel call in a synthesis, both
        so each specialist sees the whole room and so the prefix can be cached."""
        text = []
        groups = [
            (projects.RULES, "# The showrunner's rules - binding\n"
                             "True in the book, and the book must not contradict it. It outranks "
                             "everything below."),
            (projects.INPUT, "# The showrunner's material\n"
                             "Everything they have put in, under their own names: brainstorms, "
                             "pitches, fragments, notes, outlines, rough chapters, earlier "
                             "working documents. Nothing about a filename tells you what is "
                             "inside - read each one and treat it as what it is. A draft shows "
                             "what happens, how people behave and how they talk; it is evidence, "
                             "not canon. Where a document labels material T, EG, S, L or Cut, "
                             "keep those labels."),
            (projects.DRAFTS, "# Drafts - what has been written so far\n"
                              "Evidence of the story, the people and their voices. Idea drafts, "
                              "not the book."),
            (projects.REFERENCES, "# Research and reference material - creative input, not canon\n"
                                  "Real-world research the showrunner gathered to make the book "
                                  "richer. Use it selectively, to ground a technology, deepen an "
                                  "institution, reveal a real constraint, enrich someone's "
                                  "circumstances, add lived-world specificity or find the "
                                  "conflict already in a situation. Do not transcribe it, and do "
                                  "not bolt it onto something the showrunner has already "
                                  "developed thoroughly. Anything you build on it is a "
                                  "**Research-informed proposal**, cited, never stated as "
                                  "something the book has settled."),
        ]
        for kind, heading in groups:
            if kind == projects.REFERENCES and not self.use_references_in_synthesis:
                text.append("# Research is NOT in this pass\n"
                            "The references/ shelf is held back for this run. Do not invent "
                            "real-world detail in its place.")
                continue
            chosen = self.material([kind], skip={self.reserved()})
            if not chosen:
                continue
            text.append(heading)
            text += [f"## campaigns/{name}\n\n{body}" for _, name, body in chosen]
        for name in self.role.reads:
            body = projects.read_artifact(self.slug, name)
            if body:
                text += [f"# {name} (from the room)", body]
        if note:
            text += ["# Note from the showrunner - address this first", note]
        return "\n\n".join(text)

    def synthesis_message(self, target, shared):
        """Shared payload first, then this call's one job. The tail is all that differs."""
        others = " and ".join(n for n in CORE if n != target)
        tail = [f"# Your job: write {target}", self.guide_text(DEST_GUIDE[target]),
                f"Everything above is the whole project. Read all of it, then write **{target}** "
                f"and only that. What belongs in {others} is being written by its own call, from "
                f"this same material - leave it, and do not worry that you saw it first. Return "
                f"the complete markdown of {target}, nothing else."]
        return f"Project: {self.slug}\n\n" + shared + "\n\n" + "\n\n".join(t for t in tail if t)

    # ---- passes 2, 3, 5 --------------------------------------------------

    def open_items_message(self, written, note):
        text = [f"Project: {self.slug}",
                "# Your job in this pass\n"
                f"Say what the three files below leave unresolved, and write {ITEMS}: one item "
                "per question, numbered. You are finding the gaps, not filling them - no "
                "answers, no options, and no research. The next pass does that.\n\n"
                "The three files were written independently from the same material, so they may "
                "read an ambiguity differently. Where they disagree, that is an open item, and "
                "finding it is the point of this pass. An item has to matter to the writing or "
                "to continuity: do not raise a question just because more detail could exist."]
        text.append("# The files this run just produced - the current state of the project")
        text += [f"## {name}\n\n{body}" for name, body in written.items()]
        # Two different things, kept apart on purpose.
        #
        # The showrunner's own open-items document is a SOURCE, like rules/ or input/: their
        # questions, in their words, about the project. It is not a synthesis artifact and it
        # is not the room's own work. It gets its own top-level section, named by its real
        # path, and pass 2 reconciles the three new files against that exact list.
        #
        # The desk's open-items.md is the room's previous list, plus whatever the showrunner
        # has since edited into it. Also prior items, also must survive - but a different kind
        # of document, so it is delimited separately and labelled as what it is.
        theirs = projects.read_reference(self.slug, self.reserved())
        if theirs:
            text.append(f"# Existing showrunner open items\n\n"
                        f"Source: {projects.INPUT}/{ITEMS}\n\n"
                        f"This is the showrunner's own list, in their words. Reconcile the three "
                        f"files above against **this exact list**, item by item. Every one of "
                        f"these questions is either in your output or removed because an explicit "
                        f"decision, a binding rule or the material now directly settles it.\n\n"
                        f"{theirs}")
        ours = projects.read_artifact(self.slug, ITEMS)
        if ours and ours.strip():
            text.append(f"# The room's current open-items list\n\n"
                        f"Source: {ITEMS}, as the last round left it and the showrunner may "
                        f"since have edited it.\n\n"
                        f"Prior items too: same rules, same obligation to account for each one.\n\n"
                        f"{ours}")
        if theirs or ours:
            text.append("# How to reconcile a prior item\n"
                        "For each one decide: **still unresolved** (keep it, in their words, with "
                        "their proposed solution); **resolved** by an explicit decision, a binding "
                        "rule or material that now directly settles it (remove it); **partly "
                        "resolved** (rewrite it around what is still uncertain); a **duplicate** of "
                        "something you found (merge, keeping their concern and their wording); or "
                        "**contradicted** by the new synthesis (keep it - the disagreement is "
                        "evidence).\n\n"
                        "**A prior item does not disappear because the new synthesis forgot it, "
                        "and a synthesis file stating one version confidently does not resolve "
                        "anything** - very often it has simply carried the problematic version "
                        "forward, which is exactly why the item exists. A broader question is not "
                        "the same item as a specific one: replacing a concern about a particular "
                        "thing with a general question about its category drops the original. "
                        "Account for every one of them.")
        settled = self.material([projects.RULES])
        if settled:
            text.append("# The showrunner's rules - settled, so nothing here is an open item")
            text += [f"## campaigns/{name}\n\n{body}" for _, name, body in settled]
        if note:
            text += ["# Note from the showrunner", note]
        return "\n\n".join(text)

    def options_message(self, items, note):
        text = [f"Project: {self.slug}",
                "# Your job in this pass\n"
                "Here are the open items you just wrote, and the research shelf. Two jobs.\n\n"
                "**Answer the list.** Give every item one to three complete options and the one "
                "you would pick. Keep every item, its question in the words it already has, its "
                "evidence and its numbering. Nothing gets silently resolved or dropped.\n\n"
                "**Challenge the project against the research.** You are the first pass to see "
                "the shelf. The pass before you found everything the project's own documents "
                "could show; what it could not find is anything that only appears when the "
                "project is held against the real world - geology, geography, law, economics, "
                "infrastructure, physics, how an institution really behaves. Where the research "
                "materially challenges or constrains something the project proposes, append a "
                "new item with `- from: research-check` and give it options too. Three documents "
                "agreeing with each other is not evidence that they are right about the world. "
                "Do not raise a question merely because the shelf holds more detail than the "
                "book needs.\n\n"
                "Every option carries a label saying where it comes from - [established], "
                "[research], [inferred] or [invented] - and its source. Use the weakest label "
                "that is accurate."]
        text.append(f"# The open items, as you wrote them\n\n{items}")
        text.append("# The three files, so an option fits the project you have")
        text += [f"## {name}\n\n{body}" for name, body in self.desk().items()]
        shelf = self.material([projects.REFERENCES])
        if shelf:
            text.append("# Research and reference material - a source for options, never canon")
            text += [f"## campaigns/{name}\n\n{body}" for _, name, body in shelf]
        settled = self.material([projects.RULES])
        if settled:
            text.append("# The showrunner's rules - an option may not contradict these")
            text += [f"## campaigns/{name}\n\n{body}" for _, name, body in settled]
        if note:
            text += ["# Note from the showrunner", note]
        return "\n\n".join(text)

    def facts_message(self, note):
        text = [f"Project: {self.slug}",
                "# Your job in this pass\n"
                f"The project is settled for now. Derive **{FACTS}**: the continuity ledger of "
                "what it currently establishes, read out of the three files below. A fact "
                "belongs here when a later page could contradict it. Keep out personality, "
                "voice, sample dialogue, stylistic observation, anything still unresolved, and "
                "research that has not become part of the project."]
        text.append("# The project as it stands")
        text += [f"## {name}\n\n{body}" for name, body in self.desk().items()]
        settled = self.material([projects.RULES])
        if settled:
            text.append("# The showrunner's rules - some settle a fact, many do not")
            text += [f"## campaigns/{name}\n\n{body}" for _, name, body in settled]
        answers = resolved(self.slug)
        if answers:
            text.append("# The showrunner's decisions - each settles something")
            text += [f"- {a['question']} -> {a['answer']}" for a in answers]
        if note:
            text += ["# Note from the showrunner", note]
        return "\n\n".join(text)

    # ---- pass 4 ----------------------------------------------------------

    def research_needed(self, work):
        text = " ".join([a["answer"] for a in work["decisions"]]
                        + [n["text"] for n in work["notes"]["general"] + work["notes"]["items"]]).lower()
        # the screen strips the [research] label from an accepted option, and an option cites
        # its source by bare filename, so the shelf's own filenames count too
        shelf = [name.rpartition("/")[2].lower() for name in self.sources([projects.REFERENCES])]
        return ("[research]" in text or f"{projects.REFERENCES}/" in text
                or any(name in text for name in shelf))

    def decisions_block(self, work):
        answers, said, held = work["decisions"], work["notes"], work["deferred"]
        text = []
        if answers:
            text.append("# The decisions - each is settled, and the book must not contradict it\n"
                        "These say what is TRUE. They outrank every option you proposed.")
            for a in answers:
                text.append(f"## {a['n']}. {a['question']}\n"
                            f"- file: {a['file'] or '(not stated)'}\n"
                            f"- the showrunner's answer: {a['answer']}")
        if said["any"]:
            text.append(
                "# The showrunner's notes - rules for this revision\n"
                "These do not answer a question; they say how the book should read, and they "
                "have the authority of a rule while you work. They are NOT written into rules/ "
                "and they are not licence to rewrite what they do not reach.\n\n"
                "**[HIGH]** must materially shape all the revision work it touches. "
                "**[MEDIUM]** should shape the relevant material unless something with more "
                "authority says otherwise. **[LOW]** is a preference: use it where it improves "
                "the work, never at the cost of an unrelated change.\n\n"
                "Where a note and a decision pull against each other, the decision says what is "
                "true and the note says how it reads. Honour both by writing the fact they "
                "decided in the register they asked for. Where they cannot both hold, follow the "
                "decision, leave the item open and say in its `why` what you could not reconcile.")
            for w in WEIGHTS:
                text += [f"- [{w}] {n['text']}" for n in said["general"] if n["weight"] == w]
                text += [f"- [{w}] (about item {n['n']}, {n['question']}) {n['text']}"
                         for n in said["items"] if n["weight"] == w]
        if held:
            text.append("# Deferred - left open on purpose\n"
                        "Each stays on the list exactly as it is, with its options and its defer "
                        "line. Do not answer one, do not drop one, do not let one hold up the rest.")
            text += [f"- {d['n']}. {d['question']}" + (f" ({d['defer']})" if d["defer"] else "")
                     for d in held]
        return text

    def revision_payload(self, work, note):
        """The shared half of pass 4: the decisions, the notes, the current state, the rules."""
        text = self.decisions_block(work)
        text.append("# The project as it stands")
        text += [f"## {name}\n\n{body}" for name, body in self.desk().items()]
        text.append(f"## {ITEMS}\n\n" + (projects.read_artifact(self.slug, ITEMS) or ""))
        settled = self.material([projects.RULES])
        if settled:
            text.append("# The showrunner's rules")
            text += [f"## campaigns/{name}\n\n{body}" for _, name, body in settled]
        if self.research_needed(work):
            shelf = self.material([projects.REFERENCES])
            if shelf:
                text.append("# Research and reference material\n"
                            "Here because a decision above rests on it. Use it for that decision "
                            "and nothing else.")
                text += [f"## campaigns/{name}\n\n{body}" for _, name, body in shelf]
        if note:
            text += ["# Note from the showrunner", note]
        return "\n\n".join(text)

    def revision_message(self, target, shared):
        if target == ITEMS:
            job = (f"# Your job: write {ITEMS}\n"
                   "Return the revised open-items list: only what is still open. An answered "
                   "item leaves the list. A deferred item stays exactly as it is, keeping its "
                   "defer line. An item you could not carry in stays, with a line in `why` "
                   "saying what was unclear. A genuinely new conflict that the revision exposed "
                   "may be added - only that kind. Renumber from 1, and leave any `## Feedback` "
                   "block at the end of the file exactly as it is.")
        else:
            job = (f"# Your job: write the revised {target}\n"
                   f"Return **{target}**, whole. It comes back changed only where a decision or "
                   "a note reaches it; everything else returns word for word. Follow each "
                   "decision through the file - a settled age is also a line further down, and a "
                   "contradiction the decision resolves comes out. This is a controlled "
                   "revision: no unrelated invention, no tidying, no restructuring. The other "
                   "files are above for context and are written by their own calls.")
        return f"Project: {self.slug}\n\n" + shared + "\n\n" + job

    # ---- running one call ------------------------------------------------

    def call(self, label, pass_name, destination, user, snapshot="",
             want_items=True, need_options=False, inputs=None):
        """One model call, writing one file. Retries itself; never advances the pipeline."""
        system = self.system_prompt(pass_name)
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        size = len(system) + len(user)
        record = {"call": label, "pass": pass_name, "destination": destination,
                  "model": self.cfg.model, "snapshot": snapshot,
                  "input_chars": size, "input_tokens_est": size // 4,
                  "inputs": sorted(inputs or []),
                  "references_included": bool(inputs) and any(
                      projects.REFERENCES in i.split("/") for i in inputs),
                  "attempts": 0, "status": "failed", "problems": [],
                  "repairs": [], "notes": []}
        with self._lock:
            self.calls.append(record)
        if size > SOFT_INPUT_CHARS:
            self.emit("warn", text=f"Pass {label}: {size:,} characters in, over the "
                                   f"{SOFT_INPUT_CHARS:,} soft ceiling - quality may suffer.")
        seen, best = [], None
        self.emit("message", text=f"Pass {label} ({pass_name}) -> {destination}: {size:,} characters in.")
        for attempt in range(1, TRIES + 1):
            if self.should_stop():
                raise Stopped()
            record["attempts"] = attempt
            self.emit("thinking", step=label, attempt=attempt, pass_name=pass_name,
                      destination=destination, model=self.cfg.model, input_chars=size)
            fixes, notes_ = [], []
            seen_raw = {}

            def watch(kind, url, request, response, st, duration, error=None):
                seen_raw.update(response=response, status=st, error=error)
                return self.log(kind, url, request, response, st, duration, error)

            try:
                reply = llm.chat(self.cfg, messages, log=watch, max_tokens=OUTPUT_TOKENS)
            except llm.LLMError as e:
                content, problems = "", [f"the request failed ({e.status}): {str(e)[:200]}"]
            else:
                content = clean(llm.text_of(reply))
                content, fixes = repair(destination, content)
                problems, notes_ = validate(destination, content,
                                            reply.get("finish_reason") == "length",
                                            want_items, need_options)
            self.dump(label, attempt, destination, messages, seen_raw.get("response"),
                      seen_raw.get("status"), seen_raw.get("error"))
            if best is None or len(content) > len(best[0]):
                best = (content, problems)
            if not problems:
                record.update(status="ok", problems=[], repairs=fixes, notes=notes_,
                              output_chars=len(content))
                for f in fixes:
                    self.emit("message", text=f"Pass {label} ({destination}): {f}.")
                for n in notes_:
                    self.emit("warn", text=f"Pass {label} ({destination}): {n} - used anyway.")
                return content
            record["problems"] = problems
            record["repairs"] = fixes
            record["notes"] = notes_
            for p in problems:
                self.emit("warn", text=f"Pass {label} ({destination}), attempt {attempt}: {p}")
            seen += [p for p in problems if p not in seen]
            if attempt < TRIES:
                earlier = [p for p in seen if p not in problems]
                messages = messages[:2] + [{"role": "user", "content":
                    f"Your last reply could not be used as {destination}:\n- " + "\n- ".join(problems)
                    + ("\n\nAnd from your earlier attempt(s), still to avoid:\n- "
                       + "\n- ".join(earlier) if earlier else "")
                    + f"\n\nAnswer again. Return the complete markdown of {destination}."}]
        # The pass fails, but the model's work is not thrown away: the fullest reply is kept
        # in the round folder so it can be read, diffed or salvaged by hand.
        if best and best[0]:
            kept = f"{destination[:-3]}-rejected.md"
            try:
                self.version.write_file(kept, best[0])
                record["rejected_kept_as"] = kept
                self.emit("warn", text=f"Pass {label}: kept the fullest reply "
                                       f"({len(best[0]):,} chars) as {kept} in this round.")
            except Exception as e:
                self.emit("warn", text=f"Couldn't keep the rejected reply: {e}")
        raise IntakeError(f"pass {label} ({destination}) failed {TRIES} times: "
                          + "; ".join(record["problems"]))

    def parallel(self, stage, targets, build, snapshot, inputs, measure_against=None):
        """A pass of focused calls run at once, then preservation telemetry over the set.

        Each call validates and retries on its own, and only an empty reply is worth another
        call. The telemetry is recorded and warned about; it never discards a reply and never
        reruns the pass. What the model wrote is what the room has."""
        written, failures = {}, []
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
            futures = {}
            for i, name in enumerate(targets):
                label = f"{stage}{chr(ord('A') + i)}"
                futures[pool.submit(
                    self.call, label, GUIDES_PASS[stage], name, build(name),
                    snapshot, name == ITEMS, False, inputs)] = name
            for fut in concurrent.futures.as_completed(futures):
                name = futures[fut]
                try:
                    written[name] = fut.result()
                except Exception as e:
                    failures.append(f"{name}: {e}")
        if failures:
            raise IntakeError(f"pass {stage} could not be completed - " + "; ".join(failures))
        if measure_against is not None:
            measure = preservation(measure_against, {k: v for k, v in written.items() if k in CORE})
            with self._lock:
                for rec in self.calls[-len(targets):]:
                    rec["preservation"] = measure
            for w in preservation_warnings(measure):
                self.emit("warn", text=f"Pass {stage} preservation: {w}")
            if measure:
                self.emit("message", text=(
                    f"Pass {stage} preservation: {measure['coverage']:.0%} of "
                    f"{measure['terms']} distinctive terms kept, mass {measure['mass']:.0%}. "
                    f"Diagnostics only - the output is kept either way."))
        return written

    # ---- the run ---------------------------------------------------------

    def write(self, name, content):
        """The room writes the file, never the model."""
        content, restored = review.enforce_locks(self.slug, name, content)
        content, kept = rules_mod.enforce_rules(self.slug, name, content)
        self.version.write(name, content.rstrip() + "\n")
        self.emit("artifact", name=name)
        if restored:
            self.emit("warn", text=f"{name}: kept the showrunner's locked page(s) "
                                   + ", ".join(map(str, restored)))
        if kept:
            self.emit("warn", text=f"{name}: the showrunner's standing rules were put back at the end")
        return content

    def desk(self, names=CORE):
        return {n: projects.read_artifact(self.slug, n) or "" for n in names}

    def expected(self):
        return CORE + (ITEMS,) if self.mode == SYNTHESIS else CORE + (ITEMS, FACTS)

    def human_modified(self):
        past = projects.list_versions(self.slug)
        last = next((v["id"] for v in past if v["id"] != self.version.id), None)
        if not last:
            return []
        out = []
        for name in CORE + (ITEMS, FACTS):
            now = projects.read_artifact(self.slug, name)
            try:
                then = projects.read_artifact(self.slug, name, last)
            except FileNotFoundError:
                then = None
            if now and then is not None and now != then:
                out.append(name)
        return out

    def write_index(self):
        """debug/index.json: the run at a glance, and where to find each call's two files."""
        if not self.debugging:
            return
        try:
            (self.debug_dir / "index.json").write_text(json.dumps({
                "campaign": self.slug, "round": self.version.id, "mode": self.mode,
                "model": self.cfg.model, "status": self.run_status,
                "use_references_during_synthesis": self.use_references_in_synthesis,
                "calls": self.calls, "files": self.dumped}, indent=2, ensure_ascii=False))
        except Exception as e:
            self.emit("warn", text=f"Couldn't write {self.debug_dir.name}/index.json: {e}")

    def record(self, before, extra=None):
        done = [n for n in self.expected() if n in self.version.meta["files_written"]]
        self.version.update(intake={
            "mode": self.mode,
            "status": self.run_status,
            "use_references_during_synthesis": self.use_references_in_synthesis,
            "calls": self.calls,
            "generated_this_run": done,
            "carried_forward": sorted(before - set(done)),
            "human_modified": self.edited_before_run,
            "failed": [n for n in self.expected() if n not in done],
            **(extra or {})})
        self.write_index()
        return done

    def run(self, note=None):
        refs = projects.reference_files(self.slug)
        self.emit("context", minimal=False,
                  guides=sorted({l for p in PASS_GUIDE for l, _ in self.guides(p)}),
                  images=[], references=list(refs), references_mode="full",
                  reference_chars=sum(p.stat().st_size for p in refs.values()),
                  model=self.cfg.model, temperature=self.cfg.temperature, image_model=None)
        before = {p.name for p in projects.project_dir(self.slug).glob("*.md")}
        self.edited_before_run = self.human_modified()
        if self.debugging:
            self.emit("message", text=f"Writing every prompt and raw reply to "
                                      f"debug/{self.debug_dir.name}/.")
        try:
            return (self.revise(before, note) if self.mode == REVISION
                    else self.synthesize(before, note))
        except Exception:
            self.run_status = self.run_status or FAILED
            self.record(before)
            raise

    def synthesize(self, before, note):
        """Pass 1 in parallel, then 2 and 3, then stop for the showrunner."""
        self.run_status = SYNTHESIZING
        src = self.sources()
        snap = self.snapshot(src)
        shared = self.payload(note)
        self.emit("message", text=f"Pass 1: {len(CORE)} calls in parallel on snapshot {snap} "
                                  f"({len(src)} source files, {len(shared):,} shared characters).")
        written = self.parallel("1", CORE, lambda n: self.synthesis_message(n, shared),
                                snap, list(src), self.guarded())
        for name in CORE:
            self.write(name, written[name])

        self.run_status = IDENTIFYING
        items = self.call("2", OPEN_ITEMS, ITEMS, self.open_items_message(self.desk(), note),
                          snap, inputs=list(CORE) + [self.reserved()]
                                       + list(self.sources([projects.RULES])))
        self.write(ITEMS, items)

        self.run_status = GENERATING
        final = self.call("3", OPTIONS, ITEMS, self.options_message(items, note), snap,
                          need_options=True,
                          inputs=list(CORE) + [ITEMS]
                                 + list(self.sources([projects.REFERENCES, projects.RULES])))
        self.write(ITEMS, final)

        self.run_status = AWAITING
        done = self.record(before, {"snapshot": snap})
        self.awaiting = True
        st = openitems.state(self.slug)
        summary = (f"Intake: {len(done)} files from 3 passes "
                   f"({sum(c['attempts'] for c in self.calls)} model requests). "
                   f"{len(st['items'])} open items, each with options. Waiting on you: answer, "
                   f"defer or leave each one, add any notes, then run intake again. "
                   f"{FACTS} is derived after that.")
        self.version.append_log(self.role.title, summary)
        return summary

    def revise(self, before, note):
        """Pass 4 in parallel, then pass 5."""
        work = pending(self.slug)
        if not work["any"]:
            raise IntakeError("nothing to revise: no open item has been answered and no notes "
                              "have been left")
        said = work["notes"]
        self.emit("message", text=(
            f"Revising with {len(work['decisions'])} decision(s), "
            f"{len(said['general']) + len(said['items'])} note(s), "
            f"{len(work['deferred'])} deferred."))
        inputs = list(CORE) + [ITEMS] + list(self.sources([projects.RULES]))
        if self.research_needed(work):
            inputs += list(self.sources([projects.REFERENCES]))
        current = self.desk()
        snap = self.snapshot({**current, ITEMS: projects.read_artifact(self.slug, ITEMS) or ""})

        self.run_status = REVISING
        shared = self.revision_payload(work, note)
        written = self.parallel("4", CORE, lambda n: self.revision_message(n, shared),
                                snap, inputs, current)
        for name in CORE:
            self.write(name, written[name])
        # the list last, so it is reconciled against the revised files
        listed = self.call("4D", REVISION, ITEMS,
                           self.revision_message(ITEMS, self.revision_payload(work, note)),
                           snap, want_items=False, inputs=inputs)
        self.write(ITEMS, listed)

        self.run_status = DERIVING
        facts = self.call("5", FACTS_PASS, FACTS, self.facts_message(note), snap,
                          inputs=list(CORE) + list(self.sources([projects.RULES])))
        self.write(FACTS, facts)

        self.run_status = READY
        done = self.record(before, {
            "snapshot": snap,
            "decisions_integrated": [a["n"] for a in work["decisions"]],
            "notes_applied": [f"[{n['weight']}] {n['text'][:80]}"
                              for n in said["general"] + said["items"]],
            "deferred": [d["n"] for d in work["deferred"]]})
        after = openitems.state(self.slug)
        summary = (f"Revised {len(done)} files from 2 passes "
                   f"({sum(c['attempts'] for c in self.calls)} model requests): "
                   f"{len(work['decisions'])} decision(s) and "
                   f"{len(said['general']) + len(said['items'])} note(s) carried in, "
                   f"{FACTS} derived. {after['unresolved']} item(s) still open, "
                   f"{after['deferred']} deferred.")
        self.version.append_log(self.role.title, summary)
        return summary


GUIDES_PASS = {"1": SYNTHESIS, "4": REVISION}
