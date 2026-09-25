"""Fast and awesome: agents side by side, the Letterer last, the page packets.

Runs with plain python3 from the repo root (PYTHONPATH=.) and touches nothing outside a
temp directory. No model is called: the pieces under test are the room's own code."""
import json, pathlib, tempfile

tmp = pathlib.Path(tempfile.mkdtemp()) / "campaigns"
tmp.mkdir(parents=True)
from app import config; config.CAMPAIGNS_DIR = tmp
from app import projects, review, phases, room, magic, lettering, prompts, thumbnails
from app.agents import load_roles
projects.CAMPAIGNS_DIR = tmp

slug = projects.create_project("Fast Book", "a pitch")

# 1. the phases: the Letterer is out of execution and has a phase of its own, last
ids = [p["id"] for p in phases.load()]
assert ids == ["intake", "development", "drafts", "audition", "writing", "execution", "lettering"], ids
assert phases.get("execution")["agents"] == ["layout", "continuity"]
assert phases.get("lettering")["agents"] == ["letterer"]
assert phases.get("development")["parallel"] == [["plotter", "character_designer"]]
assert phases.get("audition")["parallel"] == [["writer_a", "writer_b"]]
phases.go_to(slug, "lettering")
assert phases.approve(slug)["phase"] == "lettering", "approving the last phase keeps the book there"
phases.go_to(slug, "intake")
print("1. seven phases, the Letterer last, two parallel groups: ok")

# 2. the runner groups agents that run side by side, and keeps the order otherwise
dev = phases.roles(slug, phases.get("development"))
run = room.Run(slug, dev, None, {"kind": "development", "max_passes": 0, "all": dev,
                                 "parallel": phases.get("development")["parallel"]})
steps = [[r.id for r in b] for b in run.steps(dev)]
assert steps == [["director"], ["plotter", "character_designer"], ["continuity"]], steps
aud = phases.roles(slug, phases.get("audition"))
run2 = room.Run(slug, aud, None, {"kind": "audition", "max_passes": 0, "all": aud,
                                  "parallel": phases.get("audition")["parallel"]})
assert [[r.id for r in b] for b in run2.steps(aud)] == [["writer_a", "writer_b"], ["first_reader"]]
# a fix pass with only one of a pair runs it alone
assert [[r.id for r in b] for b in run.steps([dev[1], dev[3]])] == [["plotter"], ["continuity"]]
for r in (run, run2):
    r.version.update(status="done", finished=projects.now())
print("2. the runner batches the pairs and keeps everyone else in order: ok")

# 3. the audition pick reads the First Reader's report; no second call
w, why = magic.pick_from_first_read("### Pulled me forward\n\nstuff\n\n### Which one I would keep reading, and the moment that decided it\n\nVersion B. The pump line.\n\n### Aftertaste\n")
assert w == "writer_b" and "pump" in why
w, why = magic.pick_from_first_read("no headings, but I would go on with writer A here.")
assert w == "writer_a"
assert magic.pick_from_first_read("") == (None, None)
assert not hasattr(magic, "ask_reader")
print("3. the pick comes from the report alone: ok")

# 4. the chain skips the page 1 proof unless asked for, and rounds of pages are a setting
assert "page1" in magic.STEPS and magic.STOPS["page1"] == "page1"
assert magic.max_execution_rounds(slug) == 2
review.save_settings(slug, execution_rounds=5)
assert magic.max_execution_rounds(slug) == 5
src = pathlib.Path("app/magic.py").read_text()
assert 'if step == "page1" and until != "page1"' in src
print("4. no page 1 stop on Produce; page rounds are a setting: ok")

# 4b. the layouts stop: the Layout Agent alone, no fix passes
assert magic.STOPS["layouts"] == "layouts" and "layouts" in magic.STEPS
assert 'if step == "layouts" and until != "layouts"' in src
run_l = room.Run(slug, phases.roles(slug, phases.get("execution")), None,
                 {"kind": "execution", "max_passes": 0, "all": [], "parallel": []})
run_l.version.update(status="done", finished=projects.now())
only = [r.id for r in phases.roles(slug, phases.get("execution")) if r.id in ("layout",)]
assert only == ["layout"]
assert any(p["step"] == "layouts" and [a["id"] for a in p["agents"]] == ["layout"] for p in magic.plan(slug))
print("4b. the layouts stop runs the Layout Agent alone: ok")

# 4c. edit mode: the draft is the book; no audition, and the notes say edit, not rewrite
eslug = projects.create_project("Edit Book", "a pitch", draft="PAGE 1. Bi11bot opens the door.")
assert not phases.editing(eslug)
projects.seed_production(eslug)
assert "improve on it" in phases.note(eslug, phases.get("development"))
review.save_settings(eslug, draft_mode="edit")
assert phases.editing(eslug)
assert any(p["step"] == "audition" for p in magic.plan(slug))
assert not any(p["step"] == "audition" for p in magic.plan(eslug))
assert any(p["step"] == "drafts" for p in magic.plan(eslug)) and not any(p["step"] == "drafts" for p in magic.plan(slug))
dn = phases.note(eslug, phases.get("development"))
assert "EDIT" in dn and "improve on it" not in dn
wn = phases.note(eslug, phases.get("writing"))
assert "CHANGED:" in wn and "audition pages" not in wn
phases.go_to(eslug, "development")
assert phases.approve(eslug)["phase"] == "drafts", "an edit goes to the draft edit"
assert phases.approve(eslug)["phase"] == "writing", "and from there to the writing, no audition"
assert review.settings(eslug)["writer"] == "writer_a"
assert "draft.md" in next(r for r in load_roles() if r.id == "continuity").reads
print("4c. edit mode skips the audition and tells the room to edit: ok")

# 4d. edit mode's page 1 proof writes the script first, and the writing step does not write it twice
calls = []
real_round = magic._round
magic._round = lambda slug, phase_id, note=None, scope=0, only=None: calls.append((phase_id, scope))
try:
    projects.write_artifact(eslug, "script.md", "")
    review.save_settings(eslug, magic={})
    magic._page1(eslug, None)
    assert calls == [("writing", 0), ("execution", 1)], calls
    projects.write_artifact(eslug, "script.md", "## Page 1\n\nBi11bot opens the door.")
    calls.clear(); magic._writing(eslug, None)
    assert calls == [], "the script was written twice"
    calls.clear(); magic._writing(eslug, None)
    assert calls == [("writing", 0)], "the flag is spent after one skip"
finally:
    magic._round = real_round
print("4d. edit mode writes the script before the page 1 proof, once: ok")

# 4e. the Draft Editor: the canon pass, then the expansion, pages counted and set
from app import draftedit
draft = "# The showrunner's draft\n\n## chapter-01-draft.md\n\n# Chapter 1\n\nAlex: \"One day... I'm leaving.\"\n\n## chapter-02-draft.md\n\n# Chapter 2\n\nBi11bot wakes.\n"
assert [n for n, _ in draftedit.chapters(draft)] == ["chapter-01-draft.md", "chapter-02-draft.md"]
assert draftedit.parse("<<<CHAPTER>>>\nx\n<<<CHANGES>>>\n- none\n<<<DOES NOT FIT>>>\n- none\n<<<PAGES>>>\n12") == ("x", "- none", "- none", 12)
assert draftedit.parse("just prose") is None
assert draftedit.share(5, [10, 16], [16, 16]) == [5, 0], "pages go where a chapter falls short of its plan"
assert draftedit.share(3, [16, 16], [16, 16]) == [2, 1] and sum(draftedit.share(7, [1, 2, 3], [None] * 3)) == 7
assert draftedit.kept_whole("a b\n\nc d", "a b\n\n[NEW 1.1]\nnew\n[/NEW]\n\nc d") == 1.0
assert draftedit.kept_whole("a b\n\nc d", "a b changed") == 0.5
projects.write_artifact(eslug, "draft.md", draft)
projects.write_artifact(eslug, "story.md", "## 3. Page plot\n\n### Chapter 1\n\n**Page 1:** a\n**Page 2:** b\n\n### Chapter 2\n\n**Page 3:** c\n")
assert draftedit.planned(eslug, 2) == [2, 1]
review.save_settings(eslug, expand_pages=2, pages=None)
ch1 = "# Chapter 1\n\nAlex: \"One day... I'm leaving.\""
replies = {
    ("edit", "chapter-01-draft.md"): f"<<<CHAPTER>>>\n{ch1}\n<<<CHANGES>>>\n- none\n<<<DOES NOT FIT>>>\n- none\n<<<PAGES>>>\n1",
    ("edit", "chapter-02-draft.md"): "<<<CHAPTER>>>\nshort\n<<<CHANGES>>>\n- **Scene**: x\n<<<DOES NOT FIT>>>\n- **Scene**: the mine is sealed\n<<<PAGES>>>\n1",
    ("grow", "chapter-01-draft.md"): f"<<<CHAPTER>>>\n{ch1}\n\n[NEW 1.1]\nTJ rolls in.\n[/NEW]\n<<<ADDED>>>\n- **[NEW 1.1]** TJ's first moment\n<<<PAGES>>>\n2",
    ("grow", "chapter-02-draft.md"): "<<<CHAPTER>>>\nsomething else entirely\n<<<ADDED>>>\n- **[NEW 2.1]** x\n<<<PAGES>>>\n3"}
def fake(cfg, messages, log=None, max_tokens=None):
    stage = "grow" if "grow it by" in messages[0]["content"] else "edit"
    return {"content": next(v for (st, k), v in replies.items() if st == stage and k in messages[-1]["content"])}
real_chat = draftedit.llm.chat
draftedit.llm.chat = fake
try:
    ed_role = next(r for r in load_roles() if r.id == "draft_editor")
    ed_run = room.Run(eslug, [ed_role], None, {"kind": "drafts", "max_passes": 0, "all": [ed_role], "parallel": []})
    note = draftedit.DraftEdit(ed_role, ed_run.version, lambda *a, **k: None).run()
    ed_run.version.update(status="done", finished=projects.now())
finally:
    draftedit.llm.chat = real_chat
edited, final, changes = (projects.read_artifact(eslug, n) for n in ("draft-edited.md", "draft-final.md", "draft-changes.md"))
assert "Bi11bot wakes." in edited and "short" not in edited, "a short canon pass keeps the chapter as written"
assert "[NEW 1.1]" in final and "I'm leaving." in final, "chapter 1 grew, its own text intact"
assert "something else entirely" not in final and "Bi11bot wakes." in final, "an expansion that changed the text is refused"
assert "the mine is sealed" in changes and "| **the book** |" in changes
assert review.settings(eslug)["pages"] == 3, "the book's page count is what the chapters come to"
assert "Drawability" in phases.note(eslug, phases.get("writing")) and "draft-final.md" in phases.note(eslug, phases.get("writing"))
print("4e. the Draft Editor: canon pass, expansion that only inserts, pages counted for drawing: ok")

# 4f. the proof can be any page: chapters mapped from the outline, the gate asks for that page only
pslug = projects.create_project("Proof Book", "a pitch")
projects.write_artifact(pslug, "story.md", "## Story So Far\n\n### Chapter 1 — One\n\n#### Page 1 — a\n\n#### Pages 2–3 — b\n\n"
                        "### Chapter 2 — Two\n\n#### Page 1 — c\n\n#### Page 2 — d\n\n### Chapter 3 — Three\n\n#### A scene\n")
assert magic.chapter_pages(pslug) == [{"chapter": 1, "title": "Chapter 1 — One", "first": 1, "pages": 3},
                                      {"chapter": 2, "title": "Chapter 2 — Two", "first": 4, "pages": 2}], magic.chapter_pages(pslug)
projects.write_artifact(pslug, "story.md", "## 3. Page plot\n\n### Chapter 1\n\n**Page 1:** a\n**Page 2:** b\n\n### Chapter 2\n\n**Page 3:** c\n")
assert [(c["first"], c["pages"]) for c in magic.chapter_pages(pslug)] == [(1, 2), (3, 1)], "book-wide numbering is kept"
assert review.proof_page(pslug) == 1
review.save_settings(pslug, scope=1, proof_page=3, pages=None)
projects.write_artifact(pslug, "layouts.md", "## Page 1\n")
g = review.gate(pslug, {})
assert any("proof of page 3 only" in r for r in g["reasons"]), g["reasons"]
assert room.magic_chapter_of(pslug, 3) == " (chapter 2, its page 1)"
review.save_settings(pslug, scope=0)
print("4f. the proof is any page: chapters mapped, the gate asks for that page: ok")

# 4g. key pages: found by chapter and page, their words checked in the script, their look sent along
from app import keypages
kslug = projects.create_project("Key Book", "a pitch")
kd = keypages.folder(kslug); kd.mkdir(parents=True, exist_ok=True)
(kd / "ch01-p02.md").write_text("# Chapter 1 — Page 2: DEBT\n\n## Dialogue / On-Page Text\n\n- SUPERVISOR: That's not the approved repair.\n"
                                "- ALEX: Then don't approve it.\n- Caption: Seventeen.\n\n## Layout\n\nFour tiers.\n")
(kd / "ch01-p02.jpg").write_bytes(b"\xff\xd8fake")
(kd / "notes.txt").write_text("ignored")
ks = keypages.pages(kslug)
assert [(k["book"], len(k["lines"]), k["layout"]) for k in ks] == [(2, 3, "Four tiers.")], ks
assert ks[0]["lines"][0] == ("SUPERVISOR", "That's not the approved repair.") and ks[0]["lines"][2] == (None, "Caption: Seventeen.")
assert keypages.check(kslug, "## Page 1\n\nx\n") == ["page 2 is a key page and is missing from the script"]
script = "## Page 2\n\nSUPERVISOR: That’s not the approved repair.\nALEX: Then don't approve it!\nCAPTION: Seventeen.\n## Page 3\n"
assert keypages.check(kslug, script) == [], keypages.check(kslug, script)
assert len(keypages.check(kslug, script.replace("approve it", "sign it"))) == 1
review.save_settings(kslug, phase="writing")
projects.write_artifact(kslug, "script.md", "## Page 2\n\nnothing\n")
g = review.gate(kslug, {"writer_a": "Writer A", "continuity": "Continuity Editor"})
assert "writer_a" in g["fix"] and any("key-page" in r for r in g["reasons"]), g
assert "Then don't approve it." in phases.note(kslug, phases.get("writing"))
assert keypages.images(kslug)[0][0].startswith("key page 2")
(kd / "notes.md").write_text("# What the key pages do not lock\n\n- **Bi11bot is off-model.** Take the style,\n  not his design.\n")
assert keypages.exceptions(kslug) == "Bi11bot is off-model. Take the style, not his design.", keypages.exceptions(kslug)
assert "not his design" in keypages.images(kslug)[0][0] and "not his design" in phases.note(kslug, phases.get("writing"))
print("4g. key pages: mapped, their words held in the script, their look sent along, the canon winning where noted: ok")

# 5. a chain or a round that died with the process is closed at startup
review.save_settings(slug, magic={"status": "running", "step": "execution", "log": []})
assert magic.close_stale(slug) is True and magic.state(slug)["status"] == "failed"
assert magic.close_stale(slug) is False
v = projects.Round(slug, run_id="x")           # status "running", never finished
assert v.id in projects.close_stale_rounds(slug)
assert json.loads(v.path("run.json").read_text())["status"] == "interrupted"
print("5. stale runs are marked at startup: ok")

# 6. the Letterer's moves land in layouts.md; words never change; locked pages stay
layout = {"page": 1, "side": "right",
          "tiers": [{"h": 1, "panels": [{"w": 1, "shot": "wide", "description": "ADA at the pump yard. Sky above her, clear."}]},
                    {"h": 1, "panels": [{"w": 1, "shot": "close", "description": "The gauge needle."}]}],
          "items": [{"panel": 1, "type": "figure", "label": "Ada", "at": "bottom-left", "size": 60},
                    {"panel": 1, "type": "balloon", "speaker": "ADA", "text": "The pump says it's lying.", "at": "bottom-right"},
                    {"panel": 2, "type": "caption", "text": "Later.", "at": "top-left"}]}
md = "## Page 1 (right) — 2 panels\n\n```layout\n" + json.dumps(layout) + "\n```\n"
projects.write_artifact(slug, "layouts.md", md)
drawn, _, _ = thumbnails.render_layouts(md, None)
projects.write_artifact(slug, "thumbnails.md", drawn)
notes = ("# Lettering\n\n## Page 1\n\nreads fine.\n\n```moves\n{\"page\": 1, \"moves\": ["
         "{\"item\": 1, \"at\": \"top-right\"}, {\"item\": 2, \"x\": 70, \"y\": 15}, "
         "{\"item\": 0, \"at\": \"top\"}, {\"item\": 9, \"at\": \"top\"}, {\"item\": 1, \"at\": \"nowhere\"}]}\n```\n")
assert [p for p, _ in lettering.moves_in(notes)] == [1]
done = lettering.apply_moves(slug, notes)
assert done == [(1, 1, "top-right"), (1, 2, "70,15")], done
spec = lettering.page_spec(slug, 1)
assert spec["items"][1]["at"] == "top-right" and spec["items"][1]["text"] == "The pump says it's lying."
assert spec["items"][2]["x"] == 70 and "at" not in spec["items"][2]
assert spec["items"][0]["at"] == "bottom-left", "a figure never moves"
assert lettering.apply_moves(slug, notes, locked={1}) == []
print("6. the Letterer's moves: applied to balloons and captions only, never a locked page: ok")

# 7. the packet: no text, the print-scale sketch, a checklist, a book packet in front
projects.write_artifact(slug, "characters.md", "# Characters\n\n## Ada\n\n**Look:** red hair, grey coveralls, a burn scar on the left hand.\n")
projects.write_artifact(slug, "brief.md", "# Brief\n\n## Visual direction\n\nClean line, flat colour, hard desert light.\n")
projects.write_artifact(slug, "script.md", "## Page 1\n\nPanel 1. ADA: The pump says it's lying.\n")
projects.write_artifact(slug, "world.md", "# World\n\n## Setting\n\n### The pump yard\n\nA fenced yard of rusted pumps under hard light.\n\n"
                                          "### Travel and access\n\nroads.\n\n## History\n\n### The Water Wars\n\nlong ago.\n")
pages, book = prompts.build(slug)
assert prompts.location_entries(projects.read_artifact(slug, "world.md")) == [("The pump yard", "A fenced yard of rusted pumps under hard light.")]
assert "**Reference images to attach**" in pages[1] and "the character sheet (ADA)" in pages[1] and "the location sheet (THE PUMP YARD)" in pages[1]
assert "## Location sheet — draw this next" in book and "THE PUMP YARD" in book
p1 = pages[1]
for must in ("NO TEXT anywhere", "**Layout sketch at print scale**", "**Before you keep this image, check:**",
             "- [ ] 2 panels", "- [ ] ADA:", "Clear, uncluttered space at: panel 1 top right; panel 2 ",
             "No letters, numbers, balloons", "red hair, grey coveralls", "_Copy everything under this heading"):
    assert must in p1, must
assert "professional comic lettering" not in p1
assert "PAGE 1\"" not in p1, "no page number in layer mode"
head = book.split("\n---\n\n", 1)[0]
for must in ("## How to use these packets", "## Rules for every page", "## Character sheet — draw this first",
             "## The pages at a glance", "| 1 | 2 | ADA |"):
    assert must in head, must
assert prompts.book_packet(slug) == head
review.save_settings(slug, lettering="art")
pages, _ = prompts.build(slug)
assert "professional comic lettering" in pages[1] and "check:" not in pages[1], "art mode letters the page and has no checklist"
print("7. the page packet and the book packet: ok")

# 8. the export writes the packets and the layers where the zip reads them
review.save_settings(slug, lettering="layer")
letters = review.text_layers(slug)
assert 1 in letters and letters[1].startswith("<svg")
print("8. lettering layers for the zip: ok")


# 9. agents in a group really run at the same time, and the round survives them
import threading, time
from app import agent as agent_mod
seen, gate = [], threading.Barrier(2, timeout=5)      # both must be inside run() at once, or it times out

class Stub:
    def __init__(self, role, version, emit, should_stop=lambda: False, *a):
        self.role, self.emit, self.log = role, emit, type("L", (), {"totals": {}})()
    def run(self, note=None):
        seen.append(self.role.id)
        if self.role.id in ("plotter", "character_designer"):
            gate.wait()             # each waits for the other: only true if they run at once
        time.sleep(0.05)
        self.emit("artifact", name=self.role.outputs[0])
        return f"{self.role.id} done"

real = agent_mod.Agent
agent_mod.Agent = Stub
try:
    dev = phases.roles(slug, phases.get("development"))
    run3 = room.Run(slug, dev, None, {"kind": "development", "max_passes": 0, "all": dev,
                                      "parallel": phases.get("development")["parallel"]})
    run3.run_roles(dev, None)
finally:
    agent_mod.Agent = real
    run3.version.update(status="done", finished=projects.now())
assert seen[0] == "director" and set(seen[1:3]) == {"plotter", "character_designer"} and seen[3] == "continuity", seen
kinds = [e["type"] for e in run3.events]
assert kinds.count("role_start") == 4 and kinds.count("role_done") == 4 and "parallel" in kinds
assert all(e.get("seconds") is not None for e in run3.events if e["type"] == "role_done")
print("9. a parallel group runs side by side (the barrier proves it) and the events are whole: ok")
print("\nall checks ran")
