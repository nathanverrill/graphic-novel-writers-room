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
assert ids == ["intake", "development", "audition", "writing", "execution", "lettering"], ids
assert phases.get("execution")["agents"] == ["layout", "continuity"]
assert phases.get("lettering")["agents"] == ["letterer"]
assert phases.get("development")["parallel"] == [["plotter", "character_designer"]]
assert phases.get("audition")["parallel"] == [["writer_a", "writer_b"]]
phases.go_to(slug, "lettering")
assert phases.approve(slug)["phase"] == "lettering", "approving the last phase keeps the book there"
phases.go_to(slug, "intake")
print("1. six phases, the Letterer last, two parallel groups: ok")

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
dn = phases.note(eslug, phases.get("development"))
assert "EDIT" in dn and "improve on it" not in dn
wn = phases.note(eslug, phases.get("writing"))
assert "CHANGED:" in wn and "audition pages" not in wn
phases.go_to(eslug, "development")
assert phases.approve(eslug) == {**phases.state(eslug), "phase": "writing"}
assert review.settings(eslug)["writer"] == "writer_a"
assert "draft.md" in next(r for r in load_roles() if r.id == "continuity").reads
print("4c. edit mode skips the audition and tells the room to edit: ok")

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
