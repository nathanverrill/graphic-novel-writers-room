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

from . import llm, projects, review, rules, search, thumbnails
from . import agents as agents_mod
from .agents import gather_context, random_entry
from .usage import CallLogger

REF_PREFIX = "library/"    # the agents' name for the library: campaigns/ and
                           # agents/skills/ under one prefix, library/<its path>


IMPLEMENTED = ("list_artifacts", "read_artifact", "search", "provoke", "write_artifact", "generate_image", "finish")
MINIMAL = ("write_artifact", "finish")     # a cold reader cannot browse the room


def repair_calls(calls, warn=lambda msg: None):
    """Make a model's tool calls valid before they are run or sent back.

    Some models emit two calls glued into one `arguments` string —
    `{"name": "script.md"}{"name": "layouts.md"}` — which is what the model meant to be two
    reads. A provider that validates the transcript rejects the whole next request over it, so
    the malformed call must not be kept in the history: each object becomes its own call, with
    its own id, and anything that still will not parse becomes an empty argument object for the
    tool itself to complain about."""
    out = []
    for call in calls:
        raw = (call.get("function") or {}).get("arguments") or "{}"
        objects, rest, decoder = [], raw.strip(), json.JSONDecoder()
        while rest:
            try:
                obj, end = decoder.raw_decode(rest)
            except json.JSONDecodeError:
                break
            objects.append(obj)
            rest = rest[end:].strip()
        if not objects or rest:
            warn(f"{call['function']['name']}: arguments were not valid JSON; "
                 f"sent back as an empty call")
            objects = objects or [{}]
        if len(objects) > 1:
            warn(f"{call['function']['name']}: {len(objects)} calls arrived glued together; "
                 "split into separate calls")
        for i, obj in enumerate(objects):
            out.append({**call,
                        "id": call["id"] if i == 0 else f"{call['id']}-{i + 1}",
                        "function": {**call["function"], "arguments": json.dumps(obj)}})
    return out


def tools_for(role, cfg, emit=None):
    """The tools this agent may call, from agents/tools/*.json.

    Its agent.json can name a `tools` list; otherwise it gets everything implemented here,
    minus generate_image unless it is set up for images. A schema with no implementation is
    skipped with a warning rather than offered to the model."""
    available = agents_mod.load_tools()
    for name in sorted(set(available) - set(IMPLEMENTED)):
        available.pop(name)
        if emit:
            emit("warn", text=f"agents/tools/{name}.json has no implementation; skipped")
    order = [n for n in IMPLEMENTED if n in available]      # a sensible order, not the file order
    wanted = MINIMAL if role.minimal else (order if cfg.tools is None else cfg.tools)   # [] = no tools: plain chat
    if not cfg.can_generate_images:
        wanted = [n for n in wanted if n != "generate_image"]
    return [available[n] for n in wanted if n in available]



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
        self.tools = tools_for(role, self.cfg, emit)
        self.log = CallLogger(version, role.id, emit)

    # ---- prompt building -------------------------------------------------

    def system_prompt(self, guides, figma_text, use_tools):
        r = self.role
        parts = [
            f"You are the {r.title} in a graphic novel writers' room.",
            r.mission,
            "# Your guides",
            *[f"## {label}\n\n{text}" for label, text in guides],
        ]
        if figma_text:
            parts += ["# Figma references", *figma_text]
        if use_tools and self.role.minimal:
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

    def shortlist(self, refs):
        """The library files this writer reads, if its settings name any.

        A shortlist entry is campaign-relative — "rules/bible.md" means this campaign's bible,
        whichever campaign is running — so one line-up of agents works for every book. Entries
        that name a campaign outright ("evoke/rules/alpha.md") are taken as written, which is
        how the shared material is picked.

        If a shortlist names nothing this campaign has, the writer gets everything in scope
        rather than nothing. A stale shortlist should cost a writer its focus, never its
        material."""
        if self.cfg.reference_files is None:
            return refs
        wanted = {n if "/" in n and n.split("/", 1)[0] in (self.slug, projects.SHARED, "skills")
                  else f"{self.slug}/{n}"
                  for n in self.cfg.reference_files}
        kept = {n: p for n, p in refs.items() if n in wanted}
        return kept or refs

    def task_message(self, note, images):
        r = self.role
        pitch = projects.read_artifact(self.slug, "pitch.md") or "(no pitch yet)"
        text = [f"Project: {self.slug}", "# Pitch", pitch]

        refs = {} if r.minimal else projects.reference_files(self.slug)
        refs = self.shortlist(refs)
        kinds = {n: projects.reference_kind(p) for n, p in refs.items()}
        groups = [
            ("rules", "# The showrunner's rules for this book\n"
                      "This is true in the book and the book must not contradict it. Where it "
                      "conflicts with the room's own files, it wins unless the showrunner's note "
                      "says otherwise."),
            ("input", "# Material the showrunner put in — it does NOT bind the book\n"
                      "Anything they wanted you to read: invented background, real-world "
                      "reporting, an earlier draft, notes, a document about how to work. Each one "
                      "says what it is — read it and treat it accordingly. None of it binds the "
                      "book and none of it has happened: mine it for what serves the page, write "
                      "the room's own version, and where it conflicts with the rules, the rules "
                      "win. Where a document labels material T, EG, S, L or Cut, keep those "
                      "labels when you use it."),
            ("guide", "# Craft guides from the room — they do NOT bind the book\n"
                      "How to do the work. They commit the book to nothing and describe no "
                      "events: take what serves the page and ignore the rest."),
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
            if target.startswith("audition-") and target not in self.role.outputs + self.role.reads:
                return "That is the other writer's audition. It is blind: write your own pages."
            try:
                if target.startswith(REF_PREFIX):
                    content = projects.read_reference(self.slug, target[len(REF_PREFIX):])
                else:
                    content = projects.read_artifact(self.slug, target)
            except ValueError as e:
                return str(e)
            return content if content is not None else f"No file named {args.get('name')!r}."
        if name == "search":
            scope = args.get("scope")
            if scope == "project":
                scope = f"project:{self.slug}"
            try:
                hits = search.search(args.get("query", ""), limit=int(args.get("limit") or 6),
                                     scope=scope or None, kind=args.get("kind") or None)
            except Exception as e:      # the index is optional: say so, do not fail the turn
                return f"Search is unavailable ({type(e).__name__}). Use list_artifacts and read_artifact."
            self.emit("tool", name="search", args={"query": args.get("query", "")[:80], "hits": len(hits)})
            return search.as_text(hits)
        if name == "provoke":
            sparks = random_entry(story_targets(self.slug), int(args.get("cards") or 3))
            if not sparks:
                return "The deck is empty (agents/_shared/deck.txt)."
            self.emit("random_entry", **sparks)
            out = ["Cards:"] + [f"- {c}" for c in sparks["cards"]]
            if sparks["word"]:
                out.append(f"Unrelated word: {sparks['word']}")
            if sparks["target"]:
                out.append(f"Target: {sparks['target']}")
            out.append("None of this is canon. Use what strengthens the page and say what you used.")
            return "\n".join(out)
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
        """Every save of layouts.md redraws thumbnails.md; problems go back to the Layout Agent."""
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
                "flag copy-length problems for the Letterer in your handoff note:\n- "
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

    def run(self, note=None):
        guides, figma_text, images = gather_context(self.role, lambda m: self.emit("warn", text=m))
        if not self.cfg.send_images:
            images = []
        refs = self.shortlist({} if self.role.minimal else projects.reference_files(self.slug))
        self.emit("context", minimal=self.role.minimal, guides=[g for g, _ in guides], images=[i for i, _, _ in images],
                  references=list(refs), references_mode=self.cfg.references,
                  reference_chars=sum(p.stat().st_size for p in refs.values()),
                  figma=len(figma_text), model=self.cfg.model, temperature=self.cfg.temperature,
                  image_model=self.cfg.image_model if self.cfg.can_generate_images else None)
        if self.cfg.generate_images and not self.cfg.image_model:
            self.emit("warn", text="generate_images is on but no image_model is set (agent.json or IMAGE_MODEL).")

        task = self.task_message(note, images)
        if not self.tools:      # "tools": [] in agent.json — for models that write tool calls as text
            return self.run_without_tools(guides, figma_text, task)
        messages = [{"role": "system", "content": self.system_prompt(guides, figma_text, True)}, task]

        nudged = False
        for step in range(1, self.cfg.max_steps + 1):
            if self.should_stop():
                raise Stopped()
            self.emit("thinking", step=step)
            try:
                reply = llm.chat(self.cfg, messages, tools=self.tools, log=self.log)
            except llm.LLMError as e:
                if e.status == 400 and step == 1:
                    self.emit("warn", text=f"Endpoint rejected tool calling; retrying as plain chat. ({e})")
                    return self.run_without_tools(guides, figma_text, task)
                raise

            self.keep_reply_images(reply)
            text = llm.text_of(reply)
            calls = repair_calls(reply.get("tool_calls") or [],
                                 lambda msg: self.emit("warn", text=msg))
            # send back only what every server accepts
            kept = {"role": "assistant", "content": text or None}
            if calls:
                kept["tool_calls"] = calls
            messages.append(kept)
            if text:
                self.emit("message", text=text)

            if not calls:
                if not self.written and not nudged:     # it talked about the work instead of doing it
                    nudged = True
                    self.emit("warn", text="No tool call and nothing written — asking once for the deliverable.")
                    messages.append({"role": "user", "content":
                                     f"You have not written {self.role.outputs[0]} yet. Do not describe what you will do "
                                     "and do not write a tool call as text: call write_artifact now, with the complete "
                                     "file as its content, then call finish."})
                    continue
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

    def run_without_tools(self, guides, figma_text, task):
        messages = [{"role": "system", "content": self.system_prompt(guides, figma_text, False)}, task]
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
