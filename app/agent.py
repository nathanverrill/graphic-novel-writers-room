"""One agent = one role working on one project.

The loop is deliberately plain:
    1. build a system prompt from the role's guides
    2. send the task (+ reference images)
    3. while the model asks for tools: run them, send results back
    4. stop when the model calls `finish` or stops asking for tools

Each agent uses its own AgentConfig (roles/<id>/agent.json), so roles can run
on different providers, models and temperatures.

If the endpoint does not support tool calling, the agent falls back to a
single request and saves the reply as its deliverable.
"""
import base64
import json
import re

from . import artist, asciitext, llm, projects, review, rules, thumbnails
from .roles import gather_context, random_entry, read_hat
from .usage import CallLogger

REF_PREFIX = "references/"

PREVIEW_HOW = artist.PANEL_HOW

TOOLS = [
    {"type": "function", "function": {
        "name": "list_artifacts",
        "description": "List the room's markdown files and the reference material (names starting with references/).",
        "parameters": {"type": "object", "properties": {}},
    }},
    {"type": "function", "function": {
        "name": "read_artifact",
        "description": "Read one project file, e.g. 'outline.md' or 'references/lore.md'.",
        "parameters": {"type": "object", "properties": {"name": {"type": "string"}},
                       "required": ["name"]},
    }},
    {"type": "function", "function": {
        "name": "write_artifact",
        "description": "Write (overwrite) one of your deliverables with its complete markdown content.",
        "parameters": {"type": "object", "properties": {
            "name": {"type": "string"}, "content": {"type": "string"}},
            "required": ["name", "content"]},
    }},
    {"type": "function", "function": {
        "name": "finish",
        "description": "Call when your deliverables are written. The note is handed to the rest of the room.",
        "parameters": {"type": "object", "properties": {"note": {"type": "string"}},
                       "required": ["note"]},
    }},
]

IMAGE_TOOL = {"type": "function", "function": {
    "name": "generate_image",
    "description": "Generate an image (character sheet, thumbnail, color key...). Returns its path, "
                   "which you can embed in your markdown as ![caption](path).",
    "parameters": {"type": "object", "properties": {
        "name": {"type": "string", "description": "short label, e.g. 'mara-turnaround'"},
        "prompt": {"type": "string", "description": "complete, self-contained image prompt"},
        "size": {"type": "string", "description": "optional, e.g. 1024x1536"},
    }, "required": ["name", "prompt"]},
}}


MINIMAL_TOOLS = [t for t in TOOLS if t["function"]["name"] in ("write_artifact", "finish")]


def story_targets(slug):
    """Headings from the outline and script: the places a random target can point at."""
    found = []
    for name in ("outline.md", "script.md"):
        text = projects.read_artifact(slug, name) or ""
        found += [l.lstrip("#").strip() for l in text.splitlines() if re.match(r"^#{2,3} \S", l)]
    return found


def page_of(message):
    m = re.match(r"page (\d+)", message)
    return int(m.group(1)) if m else None


class Stopped(Exception):
    pass


class Agent:
    def __init__(self, role, version, emit, should_stop=lambda: False):
        self.role = role
        self.cfg = role.config()
        self.version = version  # projects.Version — where this run's output goes
        self.slug = version.slug
        self.emit = emit  # emit(type, **data) -> shows up in the UI
        self.should_stop = should_stop
        self.written = set()
        if role.minimal:  # a cold reader can't browse the room
            self.tools = MINIMAL_TOOLS
        else:
            self.tools = TOOLS + ([IMAGE_TOOL] if self.cfg.can_generate_images else [])
        self.log = CallLogger(version, role.id, emit)

    # ---- prompt building -------------------------------------------------

    def system_prompt(self, guides, figma_text, use_tools, hat=None):
        r = self.role
        parts = [
            f"You are the {r.title} in a graphic novel writers' room.",
            r.mission,
            "# Your guides",
            *[f"## {label}\n\n{text}" for label, text in guides],
        ]
        if figma_text:
            parts += ["# Figma references", *figma_text]
        if hat:
            parts += ["# Thinking mode for this run — wear this hat", read_hat(hat)]
        if r.preview:
            parts.append(PREVIEW_HOW)
        elif use_tools and self.role.minimal:
            parts.append(
                "# How to work\n"
                f"Everything you may read is in the message. Write {r.outputs[0]} in full with "
                "write_artifact, then call finish with a one-line note."
            )
        elif use_tools:
            parts.append(
                "# How to work\n"
                "The room shares a folder of markdown files. Use list_artifacts and read_artifact "
                "to check colleagues' work when you need it. "
                f"Your deliverables: {', '.join(r.outputs)}. Write each one in full with "
                "write_artifact (it overwrites). When they are done, call finish with a short "
                "handoff note for the rest of the room: decisions made, open questions."
            )
            if self.cfg.can_generate_images:
                parts.append(
                    "You can create images with generate_image. Use it for the visuals your role "
                    "is responsible for, write complete prompts (character looks and palette "
                    "verbatim from the room's files), and embed the returned paths in your deliverable."
                )
        else:
            parts.append(
                "# How to work\n"
                f"Reply with the complete markdown content of {r.outputs[0]} and nothing else."
            )
        return "\n\n".join(parts)

    def task_message(self, note, images, sparks=None):
        r = self.role
        pitch = projects.read_artifact(self.slug, "pitch.md") or "(no pitch yet)"
        text = [f"Project: {self.slug}", "# Pitch", pitch]

        refs = {} if r.minimal else projects.reference_files(self.slug)
        kinds = {n: projects.reference_kind(p) for n, p in refs.items()}
        groups = [
            ("canon", "# Reference material from the showrunner — canon\n"
                      "Treat these as canon. Where they conflict with the room's files, "
                      "the references win unless the showrunner's note says otherwise."),
            ("draft", "# Idea drafts from the showrunner — NOT canon, NOT the script to write\n"
                      "These were put together to get ideas on paper. Mine them for story beats, "
                      "intent, moments and lines worth keeping, but write the room's own, better "
                      "version: don't copy their structure, pacing, dialogue or page breakdown. "
                      "Where a draft conflicts with the canon references, the canon wins."),
        ]
        for kind, heading in groups:
            chosen = {n: p for n, p in refs.items() if kinds[n] == kind}
            if not chosen:
                continue
            if self.cfg.references == "full":
                text.append(heading)
                text += [f"## {REF_PREFIX}{n}\n\n{p.read_text()}" for n, p in chosen.items()]
            else:
                text.append(heading + "\nRead what you need with read_artifact:\n"
                            + "\n".join(f"- {REF_PREFIX}{n} ({p.stat().st_size // 1000 or 1} KB)"
                                        for n, p in chosen.items()))

        for name in r.reads:
            content = projects.read_artifact(self.slug, name)
            if content:
                text += [f"# {name} (from the room)", content]
            else:
                text.append(f"# {name}\n(not written yet — work from what you have)")

        existing = [] if r.minimal else [(n, projects.read_artifact(self.slug, n)) for n in r.outputs]
        existing = [(n, c) for n, c in existing if c]
        if existing:
            text.append("# Your previous drafts — revise rather than start over")
            text += [f"## {n}\n{c}" for n, c in existing]

        if sparks:
            spark = ["# Random entry (drawn by code for this run)", "Cards:"]
            spark += [f"- {c}" for c in sparks["cards"]]
            if sparks["word"]:
                spark.append(f"Unrelated word: {sparks['word']}")
            if sparks["target"]:
                spark.append(f"Target: {sparks['target']}")
            text.append("\n".join(spark))

        if note:
            text += ["# Note from the showrunner — address this first", note]

        if images:
            text.append("# Reference images attached: " + ", ".join(l for l, _, _ in images))

        content = [{"type": "text", "text": "\n\n".join(text)}]
        for _, mime, data in images:
            url = f"data:{mime};base64,{base64.b64encode(data).decode()}"
            content.append({"type": "image_url", "image_url": {"url": url}})
        return {"role": "user", "content": content}

    # ---- tools -----------------------------------------------------------

    def run_tool(self, name, args):
        if name not in {t["function"]["name"] for t in self.tools}:
            return f"Tool {name!r} is not available to you."
        if name == "list_artifacts":
            names = [a["name"] for a in projects.list_artifacts(self.slug)]
            names += [REF_PREFIX + n for n in projects.reference_files(self.slug)]
            return json.dumps(names)
        if name == "read_artifact":
            target = args.get("name", "")
            try:
                if target.startswith(REF_PREFIX):
                    content = projects.read_reference(self.slug, target[len(REF_PREFIX):])
                else:
                    content = projects.read_artifact(self.slug, target)
            except ValueError as e:
                return str(e)
            return content if content is not None else f"No file named {args.get('name')!r}."
        if name == "write_artifact":
            target = args.get("name", "")
            if target not in self.role.outputs:
                return f"Refused: you may only write {', '.join(self.role.outputs)}."
            return self.save(target, args.get("content", ""))
        if name == "generate_image" and self.cfg.can_generate_images:
            prompt = args.get("prompt", "")
            if not prompt:
                return "A prompt is required."
            self.emit("image_start", name=args.get("name"), prompt=prompt, model=self.cfg.image_model)
            try:
                data = llm.generate_image(self.cfg, prompt, args.get("size"), log=self.log)
            except llm.LLMError as e:
                self.emit("warn", text=f"Image generation failed: {e}")
                return f"Image generation failed: {e}"
            path = self.save_image(args.get("name") or "image", data)
            return f"Saved {path}. Embed it as ![caption]({path})."
        return f"Unknown tool {name!r}."

    def save(self, name, content):
        content, restored = review.enforce_locks(self.slug, name, content)
        content, kept_rules = rules.enforce_rules(self.slug, name, content)
        self.version.write(name, content)
        self.written.add(name)
        self.emit("artifact", name=name)
        result = f"Saved {name}."
        if kept_rules:
            result += " The showrunner's standing rules were put back at the end; they are theirs, not yours."
        if restored:
            pages = ", ".join(map(str, restored))
            result += f" Page(s) {pages} are locked by the showrunner; your changes to them were discarded."
            self.emit("warn", text=f"{name}: kept locked page(s) {pages}")
        if name == "layouts.md":
            result += self.render_thumbnails(content)
        return result

    def render_thumbnails(self, content):
        """Every save of layouts.md redraws thumbnails.md; problems go back to the Penciller."""
        md, specs, feedback = thumbnails.render_layouts(
            content, projects.read_artifact(self.slug, "thumbnails.md"))
        if not specs and not feedback:
            return " No ```layout blocks found, so no thumbnails were drawn."
        md, _ = review.enforce_locks(self.slug, "thumbnails.md", md)
        kept = {n for n, l in review.locks(self.slug).items() if l.get("kind") == review.KEPT}
        feedback = [f for f in feedback if page_of(f) not in kept]   # nothing to fix on a kept page
        self.version.write("thumbnails.md", md)
        self.emit("artifact", name="thumbnails.md")
        self.emit("thumbnails", pages=len(specs), issues=len(feedback))
        if not feedback:
            return f" Drew {len(specs)} pages into thumbnails.md with no layout issues."
        return (f" Drew {len(specs)} pages into thumbnails.md. Fix what you can and save again; "
                "flag copy-length problems for the Scripter/Letterer in your handoff note:\n- "
                + "\n- ".join(feedback))

    def save_image(self, label, data):
        path = self.version.save_image(self.role.id, label, data)
        self.emit("image", path=path)
        return path

    def keep_reply_images(self, reply):
        """Some chat models return images with their text; always keep them."""
        try:
            found = llm.images_in_message(reply)
        except Exception as e:
            self.emit("warn", text=f"Couldn't save an image from the reply: {e}")
            return
        for data in found:
            self.save_image("reply", data)

    # ---- the loop --------------------------------------------------------

    def run(self, note=None, hat=None):
        guides, figma_text, images = gather_context(self.role, lambda m: self.emit("warn", text=m))
        if not self.cfg.send_images:
            images = []
        refs = {} if self.role.minimal else projects.reference_files(self.slug)
        sparks = random_entry(self.role, story_targets(self.slug))
        if sparks:
            self.emit("random_entry", **sparks)
        self.emit("context", hat=hat, minimal=self.role.minimal, guides=[g for g, _ in guides], images=[i for i, _, _ in images],
                  references=list(refs), references_mode=self.cfg.references,
                  reference_chars=sum(p.stat().st_size for p in refs.values()),
                  figma=len(figma_text), model=self.cfg.model, temperature=self.cfg.temperature,
                  image_model=self.cfg.image_model if self.cfg.can_generate_images else None)
        if self.cfg.generate_images and not self.cfg.image_model:
            self.emit("warn", text="generate_images is on but no image_model is set (agent.json or IMAGE_MODEL).")

        if self.role.preview:
            return self.run_preview(note, hat, guides, figma_text, images)

        task = self.task_message(note, images, sparks)
        messages = [{"role": "system", "content": self.system_prompt(guides, figma_text, True, hat)}, task]

        for step in range(1, self.cfg.max_steps + 1):
            if self.should_stop():
                raise Stopped()
            self.emit("thinking", step=step)
            try:
                reply = llm.chat(self.cfg, messages, tools=self.tools, log=self.log)
            except llm.LLMError as e:
                if e.status == 400 and step == 1:
                    self.emit("warn", text=f"Endpoint rejected tool calling; retrying as plain chat. ({e})")
                    return self.run_without_tools(guides, figma_text, task, hat)
                raise

            self.keep_reply_images(reply)
            text = llm.text_of(reply)
            calls = reply.get("tool_calls") or []
            # send back only what every server accepts
            kept = {"role": "assistant", "content": text or None}
            if calls:
                kept["tool_calls"] = calls
            messages.append(kept)
            if text:
                self.emit("message", text=text)

            if not calls:
                return self.wrap_up(text)

            finished = None
            for call in calls:
                fn = call["function"]["name"]
                try:
                    args = json.loads(call["function"].get("arguments") or "{}")
                except json.JSONDecodeError:
                    args = {}
                self.emit("tool", name=fn, args={k: (v if k != "content" else f"{len(v)} chars")
                                                  for k, v in args.items()})
                if fn == "finish":
                    finished = args.get("note", "")
                    result = "Thanks."
                else:
                    result = self.run_tool(fn, args)
                messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})

            if finished is not None:
                return self.wrap_up(finished)

        self.emit("warn", text=f"Stopped after {self.cfg.max_steps} steps.")
        return self.wrap_up("(ran out of steps)")

    def run_without_tools(self, guides, figma_text, task, hat=None):
        messages = [{"role": "system", "content": self.system_prompt(guides, figma_text, False, hat)}, task]
        reply = llm.chat(self.cfg, messages, log=self.log)
        self.keep_reply_images(reply)
        return self.wrap_up(llm.text_of(reply))

    def wrap_up(self, text):
        """If the model answered in prose without saving, keep the prose as the deliverable."""
        primary = self.role.outputs[0]
        if not self.written and text.strip():
            self.save(primary, text)
            text = f"Delivered {primary}."
        self.version.append_log(self.role.title, text or "(no note)")
        return text

    # ---- ASCII page previews ------------------------------------------------

    def run_preview(self, note, hat, guides, figma_text, images):
        """One page at a time, fresh context per page, written out as each page lands.
        Hand-edited pages are kept and not redrawn."""
        target = self.role.outputs[0]
        specs, errors = thumbnails.parse_layouts(projects.read_artifact(self.slug, "layouts.md"))
        if not specs:
            self.emit("warn", text="layouts.md has no ```layout blocks yet — run the Penciller first.")
            self.version.append_log(self.role.title, "No layouts to preview.")
            return "No layouts to preview."
        geo = thumbnails.geometry()
        script = projects.read_artifact(self.slug, "script.md") or ""
        bible = projects.read_artifact(self.slug, "bible.md") or ""
        before = thumbnails.parse_thumbnails(projects.read_artifact(self.slug, target))
        pages = []
        for i, spec in enumerate(specs):
            if self.should_stop():
                raise Stopped()
            page = thumbnails.render_page(spec, geo)
            current = (thumbnails.parse_thumbnails(projects.read_artifact(self.slug, target)).get(page.number)
                       or before.get(page.number))
            if current and current["edited"]:
                self.emit("warn", text=f"page {page.number} is hand-edited or locked — kept, not redrawn")
                pages.append(thumbnails.keep_edited(current, page.number, spec))
                continue
            if current and current["layout"] == thumbnails.layout_hash(spec):
                pages.append(thumbnails.keep_edited(current, page.number, spec))   # layout unchanged: no redraw
                continue
            self.emit("thinking", step=f"page {page.number}")
            try:
                mask = None
                if self.role.preview == "drawn":
                    art, notes = artist.draw_page(self, page, script, bible, guides, figma_text, note, hat)
                else:
                    art, notes = self.image_page(page, bible, note)
            except llm.LLMError as e:
                art, notes, mask = None, [f"model call failed, showing the layout render: {e}"], None
                self.emit("warn", text=f"page {page.number}: {e}")
            invert = thumbnails.mask_text(thumbnails.compose_invert(page, mask))
            pages.append(thumbnails.page_markdown(page, thumbnails.compose(page, art), notes, spec, invert))
            # keep the pages not reached yet, and any the showrunner hand-edited meanwhile
            later = [thumbnails.keep_edited(before[s["page"]], s["page"]) for s in specs[i + 1:] if s["page"] in before]
            doc = thumbnails.document(self.role.title, pages + later, errors, geo)
            self.save(target, thumbnails.merge_edited(doc, projects.read_artifact(self.slug, target)))
        return self.wrap_up(f"Drew {len(pages)} pages into {target}.")

    def image_page(self, page, bible, note):
        if not self.cfg.image_model:
            return None, ["no image model configured (image_model / IMAGE_MODEL) — showing the layout render"]
        art = [row[:] for row in page.art]
        notes = []
        items = thumbnails.labels_by_panel(page)
        for p in page.panels:
            desc = (p.spec.get("description") or "").strip()
            if not desc:
                notes.append(f"P{p.n}: no description — kept the layout silhouettes")
                continue
            if self.should_stop():
                raise Stopped()
            shot = " ".join(b for b in (p.spec.get("shot"), p.spec.get("angle") and f"{p.spec['angle']} angle") if b)
            prompt = ("Rough black-and-white comic thumbnail sketch, bold simple shapes, strong contrast, "
                      "plain white background, no text, no lettering, no panel border. "
                      + (f"{shot} shot. " if shot else "") + desc + " "
                      + thumbnails.looks_for(bible, items.get(p.n, []))
                      + (f" Note: {note}" if note else ""))
            size = thumbnails.image_size_for(p, page.geo)
            self.emit("image_start", name=f"page {page.number} panel {p.n}", prompt=prompt,
                      model=self.cfg.image_model)
            try:
                data = llm.generate_image(self.cfg, prompt, size, log=self.log)
                self.save_image(f"p{page.number}-panel{p.n}", data)
                w, h = p.size
                x0, y0, _, _ = p.inner
                for j, row in enumerate(thumbnails.image_to_ascii(data, w, h, page.geo)):
                    art[y0 + j][x0:x0 + w] = row
            except Exception as e:  # one bad panel shouldn't lose the page
                notes.append(f"P{p.n}: image failed — {e}")
                self.emit("warn", text=f"page {page.number} panel {p.n}: {e}")
        return art, notes
