"""The visual check: text -> image, never image -> canon.

    pass 6  briefs   characters, world, story, facts  -> visual-briefs.md   (one call)
    pass 7  images   one brief                        -> images/<brief>.png (all briefs at once)
    pass 8  check    one image + its brief            -> verdict and found lines in the brief
            -- the run stops: the showrunner keeps, sends back or rejects each --

The four files are the only source. A brief says what MUST appear, what the image model MAY
decide, what MUST NOT appear, and what the files leave UNKNOWN. An unknown is an open item by
another route, so it is appended to open-items.md with `- from: visual-brief`; it is answered
there, carried into the files by intake's revision, and the brief is regenerated. Nothing an
image shows becomes a fact by being shown.

Same shape as intake: no tools, the room builds every prompt, writes every file, and the model
does only the reading and the picturing. Runs as its own phase (agents/phases.json, "visual")
with the Script Coordinator's settings, plus an image model.
"""
import base64
import concurrent.futures
import re

from . import intake, llm, openitems, projects
from .agent import Stopped
from .intake import Intake, IntakeError

BRIEFS = "visual-briefs.md"
KINDS = ("world", "location", "character", "scene")
FIELDS = ("kind", "subject", "required", "allowed", "prohibited", "look", "unknown", "note",
          "image", "verdict", "found", "status")
MULTI = {"unknown", "found"}
KEPT, BACK, REJECTED = "kept", "back", "rejected"
STATUSES = (KEPT, BACK, REJECTED)

BRIEFING, RENDERING, CHECKING = "writing_briefs", "rendering", "checking"
AWAITING = "awaiting_showrunner_review"
WORKERS = 8         # the user asked for the images in parallel; a brief set is 5-8

NO_TEXT = ("A photographic concept reference with NO TEXT ANYWHERE IN THE IMAGE: no place "
           "names, captions, labels, signage, logos, numbers, speech balloons or on-screen "
           "writing, even where a place is named below - the picture identifies things by how "
           "they look, never by a word. Not finished comic art; no panel borders.")
CITATION = re.compile(r"\s*`?\([^()]*\.md[^()]*\)`?")


# ---- the file -----------------------------------------------------------------

def parse(text):
    """visual-briefs.md as a list of briefs.

        ## 1. world-establishing: The basin from above
        - kind: world
        - required: ...            (a field runs on until the next field line)
        - unknown: ...             (may repeat: one line per unknown)
    """
    out = []
    for block in re.split(r"^##\s+", text or "", flags=re.M)[1:]:
        lines = block.strip().split("\n")
        m = re.match(r"(\d+)[.)]\s*([a-z0-9][a-z0-9-]*)\s*:\s*(.*)", lines[0].strip(), flags=re.I)
        if not m:
            continue
        b = {"n": int(m.group(1)), "slug": m.group(2).lower(), "title": m.group(3).strip(),
             **{f: ([] if f in MULTI else "") for f in FIELDS}}
        field = None
        for line in lines[1:]:
            f = re.match(r"^\s*[-*]\s*\**([A-Za-z]+)\**\s*:\s*(.*)", line)
            if f and f.group(1).lower() in FIELDS:
                field, value = f.group(1).lower(), f.group(2).strip()
                if field in MULTI:
                    if value:
                        b[field].append(value)
                else:                           # a repeated field line adds a paragraph
                    b[field] = (b[field] + "\n" + value).strip() if b[field] else value
            elif field and line.strip():        # the field runs on to the next line
                if field not in MULTI:
                    b[field] = (b[field] + "\n" + line.rstrip()).strip()
                elif b[field]:
                    b[field][-1] += " " + line.strip()
                else:
                    b[field].append(line.strip())
        b["kind"] = b["kind"].lower()
        out.append(b)
    return out


def set_lines(text, n, **fields):
    """Rewrite a brief's field lines in place; a value of None removes the field, a list
    writes one line per entry. Everything else in the file is left exactly as it is."""
    blocks = re.split(r"^(?=##\s)", text or "", flags=re.M)
    for i, block in enumerate(blocks):
        m = re.match(r"##\s+(\d+)[.)]", block)
        if not m or int(m.group(1)) != n:
            continue
        lines = block.rstrip("\n").split("\n")
        kept, skip = [], False
        for line in lines:
            f = re.match(r"^\s*[-*]\s*\**([A-Za-z]+)\**\s*:", line)
            if f and f.group(1).lower() in FIELDS:
                skip = f.group(1).lower() in fields
            elif f or not line.strip() or line.startswith("#"):
                skip = False
            if not skip:
                kept.append(line)
        while kept and not kept[-1].strip():
            kept.pop()
        for field, value in fields.items():
            for v in (value if isinstance(value, list) else [value]):
                if v:
                    kept.append(f"- {field}: {str(v).strip()}")
        blocks[i] = "\n".join(kept) + "\n\n"
        return "".join(blocks).rstrip("\n") + "\n"
    raise ValueError(f"no brief {n}")


def state(slug):
    text = projects.read_artifact(slug, BRIEFS) or ""
    briefs = parse(text)
    return {"briefs": briefs, "exists": bool(text.strip()),
            "kept": sum(1 for b in briefs if b["status"] == KEPT),
            "back": sum(1 for b in briefs if b["status"] == BACK),
            "rejected": sum(1 for b in briefs if b["status"] == REJECTED),
            "unreviewed": sum(1 for b in briefs if b["image"] and not b["status"])}


def review(slug, n, status=None, note=None):
    """The showrunner's word on one brief: kept, sent back (with a note the regeneration
    reads), rejected, or cleared. Written into the brief, nowhere else."""
    if status is not None and status not in STATUSES + ("",):
        raise ValueError(f"status must be one of {STATUSES}")
    text = projects.read_artifact(slug, BRIEFS) or ""
    fields = {}
    if status is not None:
        fields["status"] = status
    if note is not None:
        fields["note"] = note.strip()
    projects.write_artifact(slug, BRIEFS, set_lines(text, n, **fields))
    return state(slug)


def unknown_items(briefs, existing):
    """Every unknown a brief raises, as open items, minus those already on the list."""
    have = {openitems._key(i["question"]) for i in existing}
    items, n = [], max([i["n"] for i in existing] + [0])
    for b in briefs:
        for u in b["unknown"]:
            q = u.strip().rstrip(".")
            if not q or openitems._key(q) in have:
                continue
            have.add(openitems._key(q))
            n += 1
            items.append(f"## {n}. {q}\n- file: {BRIEFS}\n"
                         f"- why: the brief for {b['slug']} ({b['title']}) needed it to draw the "
                         f"picture and the files do not say\n- from: visual-brief")
    return items


# ---- the run --------------------------------------------------------------------

class Visual(Intake):
    """One visual-check round. Same shape as Intake from the room's side."""

    def __init__(self, role, version, emit, should_stop=lambda: False, mode=None):
        super().__init__(role, version, emit, should_stop, intake.SYNTHESIS)
        self.mode = "briefs" if mode == "briefs" else "visual"
        if not self.cfg.image_model:
            raise IntakeError("no image model: set image_model in agents/script_coordinator/"
                              "agent.json or IMAGE_MODEL in .env")

    # ---- pass 6 ------------------------------------------------------------

    def briefs_message(self, note):
        text = [f"Project: {self.slug}",
                "# Your job in this pass\n"
                f"Write **{BRIEFS}**: five to eight visual briefs, each for one image that would "
                "let a reader look and say 'yes, that is the world, the people and the scale "
                "these files describe' - or see at once where the files are being misread. "
                "Decide the set from the material: a world-establishing image, the two or three "
                "most important or most distinct locations, the two or three principal "
                "characters, and at least one scene with people in a place at the intended "
                "scale and level of technology.\n\n"
                "The four files below are the only source. Nothing from outside them - no "
                "genre habit, no real place standing in for an invented one, no detail from a "
                "story like this one - may put a story fact into a brief. Where the files do "
                "not say, the brief says so, as an unknown, and gives the image model a free "
                "hand marked as such."]
        text.append("# The project as it stands - the only source")
        text += [f"## {name}\n\n{body}" for name, body in self.desk(intake.CORE + (intake.FACTS,)).items()]
        settled = self.material([projects.RULES])
        if settled:
            text.append("# The showrunner's rules - binding on every image")
            text += [f"## campaigns/{name}\n\n{body}" for _, name, body in settled]
        if note:
            text += ["# Note from the showrunner", note]
        return "\n\n".join(text)

    # ---- pass 7 ------------------------------------------------------------

    def image_prompt(self, b):
        cite = lambda t: CITATION.sub("", t)      # "(world.md; facts.md)" is for the room, not the artist
        parts = [NO_TEXT, cite(b["subject"])]
        if b["required"]:
            parts.append("Must be shown, exactly as written: " + cite(b["required"]))
        if b["allowed"]:
            parts.append("Not established, so your choice: " + cite(b["allowed"]))
        if b["prohibited"]:
            parts.append("Must not appear: " + cite(b["prohibited"]))
        if b["look"]:
            parts.append("The look: " + cite(b["look"]))
        if b["note"]:
            parts.append("The showrunner adds: " + b["note"])
        parts.append("Add nothing that tells a story of its own: no invented symbols, emblems, "
                     "documents or events. Render the description, not an interpretation of it.")
        return "\n\n".join(p.strip() for p in parts if p and p.strip())

    def render_one(self, b):
        if self.should_stop():
            raise Stopped()
        prompt = self.image_prompt(b)
        label = f"7{b['slug']}"
        record = {"call": label, "pass": "images", "destination": f"images/{b['slug']}",
                  "model": self.cfg.image_model, "input_chars": len(prompt),
                  "attempts": 0, "status": "failed", "problems": []}
        with self._lock:
            self.calls.append(record)
        self.emit("message", text=f"Pass 7 -> {b['slug']}: {len(prompt):,} characters to {self.cfg.image_model}.")
        self.emit("image_start", name=b["slug"], prompt=prompt, model=self.cfg.image_model)
        err = None
        for attempt in (1, 2):
            record["attempts"] = attempt
            try:
                data = llm.generate_image(self.cfg, prompt, log=self.log)
                path = self.version.save_image("visual", b["slug"], data)
                record.update(status="ok", output=path)
                self.emit("image", path=path)
                return path
            except llm.LLMError as e:
                err = f"{e.status}: {str(e)[:200]}"
                record["problems"] = [err]
                self.emit("warn", text=f"Pass 7 ({b['slug']}), attempt {attempt}: {err}")
        raise IntakeError(f"{b['slug']}: {err}")

    # ---- pass 8 ------------------------------------------------------------

    def check_message(self, b):
        return "\n\n".join([
            f"Project: {self.slug}",
            "# Your job\n"
            "Here is a brief and the image made from it. Hold the image up against the brief "
            "and say whether it can stand as a reference for this project. A striking image "
            "that contradicts the brief fails; a plain one that matches it passes. Look for: a "
            "required detail missing or wrong; something prohibited present; wrong geography, "
            "technology level, architecture, relative scale or period; a symbol, object or "
            "piece of text the brief did not ask for; the wrong genre; anything that reads as "
            "story information the files do not contain. Any lettering at all - a place name, "
            "a label, a title on a book - is a finding unless the brief required that exact "
            "text. Ignore taste and finish.\n\n"
            "Answer in exactly this shape and nothing else:\n\n"
            "verdict: pass | revise\n"
            "found:\n"
            "- one problem per line, saying what and where in the image; or 'nothing' if none",
            f"# The brief\n\n## {b['n']}. {b['slug']}: {b['title']}\n"
            + "\n".join(f"- {f}: {b[f]}" for f in ("kind", "subject", "required", "allowed", "prohibited", "look") if b[f]),
        ])

    def check_one(self, b, path):
        if self.should_stop():
            raise Stopped()
        data = projects.image_path(self.slug, path.split("/")[-1]).read_bytes()
        mime = "image/png" if data[:4] == b"\x89PNG" else "image/jpeg" if data[:2] == b"\xff\xd8" else "image/webp"
        url = f"data:{mime};base64,{base64.b64encode(data).decode()}"
        text = self.check_message(b)
        messages = [{"role": "system", "content": self.system_prompt(intake.CHECK)},
                    {"role": "user", "content": [{"type": "text", "text": text},
                                                  {"type": "image_url", "image_url": {"url": url}}]}]
        label = f"8{b['slug']}"
        record = {"call": label, "pass": intake.CHECK, "destination": BRIEFS, "model": self.cfg.model,
                  "input_chars": len(text), "attempts": 0, "status": "failed", "problems": []}
        with self._lock:
            self.calls.append(record)
        self.emit("message", text=f"Pass 8 -> {b['slug']}: the image and its brief.")
        reply = ""
        for attempt in (1, 2):
            record["attempts"] = attempt
            try:
                reply = llm.text_of(llm.chat(self.cfg, messages, log=self.log, max_tokens=4000)).strip()
            except llm.LLMError as e:
                record["problems"] = [f"{e.status}: {str(e)[:200]}"]
                self.emit("warn", text=f"Pass 8 ({b['slug']}), attempt {attempt}: {record['problems'][0]}")
                continue
            if reply:
                break
        if not reply:
            raise IntakeError(f"{b['slug']}: the check came back empty")
        m = re.search(r"verdict\s*:\s*\**\s*(pass|revise|fail)", reply, flags=re.I)
        verdict = (m.group(1).lower() if m else "unread").replace("fail", "revise")
        found = [re.sub(r"^\s*[-*]\s*", "", l).strip() for l in reply.split("\n")
                 if re.match(r"^\s*[-*]\s+\S", l)]
        found = [f for f in found if f.lower().rstrip(".") != "nothing"]
        record.update(status="ok", verdict=verdict, found=found)
        self.emit("message", text=f"Pass 8 ({b['slug']}): {verdict}" + (f", {len(found)} found" if found else ""))
        return verdict, found

    # ---- the round ---------------------------------------------------------

    def targets(self, briefs):
        """Which briefs this round renders: all of them after a fresh pass 6; otherwise the
        ones sent back, and any that have no image yet."""
        return [b for b in briefs if not b["image"] or b["status"] == BACK]

    def run(self, note=None):
        refs = projects.reference_files(self.slug)
        self.emit("context", minimal=False, guides=sorted({l for l, _ in self.guides(intake.BRIEFS_PASS)}),
                  images=[], references=[], references_mode="none", reference_chars=0,
                  model=self.cfg.model, temperature=self.cfg.temperature, image_model=self.cfg.image_model)
        before = {p.name for p in projects.project_dir(self.slug).glob("*.md")}
        try:
            return self.check_round(before, note)
        except Exception:
            self.run_status = self.run_status or intake.FAILED
            self.record(before)
            raise

    def expected(self):
        return (BRIEFS,)

    def check_round(self, before, note):
        missing = [n for n in intake.CORE + (intake.FACTS,) if not projects.read_artifact(self.slug, n)]
        if missing:
            raise IntakeError("the visual check reads the settled files, and these are not written "
                              "yet: " + ", ".join(missing))
        text = projects.read_artifact(self.slug, BRIEFS) or ""
        briefs = parse(text)
        if self.mode == "briefs" or not briefs:
            self.run_status = BRIEFING
            text = self.call("6", intake.BRIEFS_PASS, BRIEFS, self.briefs_message(note),
                             inputs=list(intake.CORE) + [intake.FACTS] + list(self.sources([projects.RULES])))
            briefs = parse(text)
            if not briefs:
                raise IntakeError(f"pass 6 wrote {BRIEFS} but no brief could be read out of it")
            self.write(BRIEFS, text)
            self.emit("message", text=f"Pass 6: {len(briefs)} briefs - "
                                      + ", ".join(f"{b['slug']} ({b['kind'] or '?'})" for b in briefs))
            existing = openitems.parse(projects.read_artifact(self.slug, openitems.ITEMS))
            new = unknown_items(briefs, existing)
            if new:
                self.add_open_items(new)
                self.emit("message", text=f"Pass 6: {len(new)} unknown(s) added to {openitems.ITEMS}.")

        todo = self.targets(briefs)
        if not todo:
            raise IntakeError("nothing to render: every brief has an image and none is sent back. "
                              "Send one back, or run with mode 'briefs' to write the set again.")

        self.run_status = RENDERING
        self.emit("message", text=f"Pass 7: {len(todo)} image(s) at once on {self.cfg.image_model}.")
        paths, failures = {}, []
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
            futs = {pool.submit(self.render_one, b): b for b in todo}
            for fut in concurrent.futures.as_completed(futs):
                b = futs[fut]
                try:
                    paths[b["n"]] = fut.result()
                except Stopped:
                    raise
                except Exception as e:
                    failures.append(str(e))
        for b in todo:
            if b["n"] in paths:
                text = set_lines(text, b["n"], image=paths[b["n"]], status="", verdict="", found=[])
        self.write(BRIEFS, text)
        if failures:
            self.emit("warn", text="Pass 7: " + "; ".join(failures))
        if not paths:
            raise IntakeError("pass 7 rendered nothing - " + "; ".join(failures))

        self.run_status = CHECKING
        done = [b for b in todo if b["n"] in paths]
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
            futs = {pool.submit(self.check_one, b, paths[b["n"]]): b for b in done}
            for fut in concurrent.futures.as_completed(futs):
                b = futs[fut]
                try:
                    verdict, found = fut.result()
                except Stopped:
                    raise
                except Exception as e:
                    self.emit("warn", text=f"Pass 8 ({b['slug']}): {e} - the image is kept unchecked.")
                    continue
                text = set_lines(text, b["n"], verdict=verdict, found=found or [])
        self.write(BRIEFS, text)

        self.run_status = AWAITING
        self.awaiting = True
        self.record(before, {"rendered": [b["slug"] for b in done], "failed_images": failures})
        st = state(self.slug)
        revise = sum(1 for b in st["briefs"] if b["verdict"] == "revise")
        summary = (f"Visual check: {len(done)} image(s) rendered from {len(st['briefs'])} briefs, "
                   f"{revise} flagged by the check. Waiting on you: keep, send back or reject each "
                   f"one. Text is canon; an image only shows it.")
        self.version.append_log(self.role.title, summary)
        return summary

    def add_open_items(self, blocks):
        body = projects.read_artifact(self.slug, openitems.ITEMS) or f"# Open items\n"
        parts = re.split(r"^(?=##\s)", body, flags=re.M)
        tail = [p for p in parts if p.partition("\n")[0].lstrip("# ").strip().rstrip(":").lower()
                in openitems.FEEDBACK_HEADS]
        head = [p for p in parts if p not in tail]
        text = "".join(head).rstrip("\n") + "\n\n" + "\n\n".join(blocks) + "\n"
        if tail:
            text += "\n" + "".join(tail)
        self.write(openitems.ITEMS, text.rstrip("\n") + "\n")
