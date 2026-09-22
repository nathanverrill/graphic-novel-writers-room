"""Parallel five-pass intake against a fake provider, on a throwaway campaign."""
import pathlib, shutil, tempfile, threading, time

tmp = pathlib.Path(tempfile.mkdtemp()) / "campaigns"
tmp.mkdir(parents=True)
from app import config; config.CAMPAIGNS_DIR = tmp
from app import projects, intake, llm, openitems, review, usage
projects.CAMPAIGNS_DIR = tmp; usage.ROOT = tmp.parent

slug = "testbook"; c = tmp / slug
for sub in ("rules", "input", "references", "preproduction", "production"): (c / sub).mkdir(parents=True)

NAMES = ["Ana Rey", "Tomas Reed", "Keel", "Halyard", "Grandmother Phantum", "Cassian Lock"]
def source(title, n):
    out = [f"# {title}", ""]
    for i in range(n):
        who = NAMES[i % len(NAMES)]
        out.append(f"- [T] {who} works the {400+i} m pump at Keel station {i}, imported. (source)")
        out.append(f"  {who} is {40+i} years old and carries a brass {i} gauge.")
    return "\n".join(out) + "\n"

# nothing is named characters.md / world.md / story.md
(c / "rules" / "hard.md").write_text(source("Rules", 30))
(c / "input" / "brainstorm.md").write_text(source("Brainstorm", 50))
(c / "input" / "rough-chapter-1.md").write_text(source("Rough chapter", 40))
(c / "input" / "pitch.txt").write_text(source("Pitch", 20))
(c / "input" / "notes-from-showrunner.md").write_text(source("Notes", 30))
(c / "references" / "pumps.md").write_text(source("Pump research", 40))
(c / "input" / "open-items.md").write_text("## 1. How old is Ana Rey?\n- why: the art needs it\n")

SRC = "\n".join((c / p).read_text() for p in
                ("rules/hard.md", "input/brainstorm.md", "input/rough-chapter-1.md",
                 "input/pitch.txt", "input/notes-from-showrunner.md"))
HEADS = {"characters.md": "# Characters\n\n## Characters\n\n### ANA REY\n",
         "world.md": "# World\n\n## Places\n\n## Money\n\n## Tech\n",
         "story.md": "# Story\n\n## Premise\n\n## Story So Far\n"}

def body(name, keep=1.0):
    lines = SRC.split("\n"); lines = lines[:int(len(lines) * keep)]
    third = max(1, len(lines) // 3)
    i = list(intake.CORE).index(name)
    return HEADS[name] + "\n".join(lines[i*third:(i+1)*third])

BARE = ("## 1. How old is Ana Rey?\n- file: characters.md\n- evidence: no age given\n"
        "- why: the art needs a face and a body\n- from: both\n\n"
        "## 2. How deep are the Keel pumps?\n- file: world.md\n- evidence: world.md says 400 m once\n"
        "- why: a panel shows the shaft\n- from: script coordinator\n")
OPTS = ("## 1. How old is Ana Rey?\n- file: characters.md\n- evidence: no age given\n"
        "- why: the art needs a face and a body\n- from: both\n"
        "- A: She is 61. [established] (rules/hard.md)\n- B: She is 44. [invented]\n- suggested: A\n\n"
        "## 2. How deep are the Keel pumps?\n- file: world.md\n- evidence: world.md says 400 m once\n"
        "- why: a panel shows the shaft\n- from: script coordinator\n"
        "- A: 400 m. [research] (references/pumps.md)\n- suggested: A\n")
LEFT = ("## 1. How deep are the Keel pumps?\n- file: world.md\n- evidence: says 400 m once\n"
        "- why: a panel shows the shaft\n- from: script coordinator\n"
        "- A: 400 m. [research] (references/pumps.md)\n- suggested: A\n- defer: not until chapter 3\n")
FACTSFILE = "# Facts\n\n## Ana Rey\n\n- [FIXED] Ana Rey is 61. (rules/decisions.md)\n" + source("more", 40)

SENT, LOCK, CONCURRENT, PEAK = [], threading.Lock(), [0], [0]
REPLY = {}          # destination -> markdown, set per scenario
KEEP = [1.0]        # how much of the source each core file carries

def dest_of(tail):
    if "Derive **facts.md**" in tail: return intake.FACTS
    if "You are finding the gaps" in tail: return "pass2"
    if "Here are the open items you just wrote" in tail: return "pass3"
    for n in intake.CORE:
        if f"# Your job: write {n}" in tail or f"# Your job: write the revised {n}" in tail:
            return n
    if "# Your job: write open-items.md" in tail: return "pass4items"
    return "?"

def fake_chat(cfg, messages, tools=None, log=None, max_tokens=None):
    assert tools is None, "intake must not offer tools"
    assert max_tokens == intake.OUTPUT_TOKENS, f"per-call budget missing: {max_tokens}"
    with LOCK:
        SENT.append(messages); CONCURRENT[0] += 1; PEAK[0] = max(PEAK[0], CONCURRENT[0])
    time.sleep(0.05)
    with LOCK:
        CONCURRENT[0] -= 1
    d = dest_of(messages[-1]["content"])
    text = REPLY.get(d, body(d, KEEP[0]) if d in intake.CORE else "")
    return {"role": "assistant", "content": text, "finish_reason": "stop"}
llm.chat = fake_chat

from app.agents import load_roles
role = [r for r in load_roles() if r.id == "script_coordinator"][0]

def run(replies, keep=1.0, mode=None, note=None):
    SENT.clear(); PEAK[0] = 0; KEEP[0] = keep
    REPLY.clear(); REPLY.update(replies)
    v = projects.Round(slug, desk=projects.PRE, run_id="test")
    a = intake.Intake(role, v, lambda t, **d: None, mode=mode)
    try: return a, v, a.run(note), None
    except Exception as e: return a, v, None, e

SYNTH = {"pass2": BARE, "pass3": OPTS}

# ---- 1. passes 1-3, pass 1 in parallel ----------------------------------
a, v, note, err = run(SYNTH)
assert err is None, err
ik = v.meta["intake"]
print("1. synthesis:", note[:58])
print("   calls:", [(x["call"], x["destination"], x["status"]) for x in ik["calls"]])
print("   peak calls in flight:", PEAK[0], "(3 = parallel)")
print("   generated:", ik["generated_this_run"], "| facts held back:", intake.FACTS not in ik["generated_this_run"])
print("   status:", ik["status"], "| snapshot:", ik["snapshot"])
pres = [x["preservation"] for x in ik["calls"] if x.get("preservation")][0]
print("   preservation:", {k: pres[k] for k in ("coverage", "mass")})

# ---- 2. one snapshot, identical shared prefix ---------------------------
snaps = {x["snapshot"] for x in ik["calls"][:3]}
print("\n2. all three pass-1 calls on one snapshot:", len(snaps) == 1, snaps)
sys3 = {SENT[i][0]["content"] for i in range(3)}
print("   system prompt identical across them (cacheable):", len(sys3) == 1)
cut = min(len(SENT[i][1]["content"].split("# Your job: write ")[0]) for i in range(3))
prefixes = {SENT[i][1]["content"][:cut] for i in range(3)}
print(f"   user payload prefix identical ({cut:,} chars, cacheable):", len(prefixes) == 1)
tails = [SENT[i][1]["content"].split("# Your job: write ")[1][:14] for i in range(3)]
print("   only the tail differs:", sorted(t.split("\n")[0] for t in tails))

# ---- 3. every call read the whole room ----------------------------------
print("\n3. each pass-1 call saw all the material:",
      all(all(f in SENT[i][1]["content"] for f in
              ("brainstorm.md", "rough-chapter-1.md", "pitch.txt", "notes-from-showrunner.md"))
          for i in range(3)))
print("   destination guide only in its own call:",
      sum("character-bearing material only" in SENT[i][1]["content"] for i in range(3)) == 1)
print("   references in pass 1:", "references/pumps.md" in SENT[0][1]["content"])

# ---- 4. plain markdown, no envelope -------------------------------------
print("\n4. no envelope demanded:", "<<<FILE:" not in SENT[0][0]["content"])
print("   a model that adds one anyway is cleaned:",
      intake.clean("```markdown\n<<<FILE:x.md>>>\n# Title\n\nbody\n<<<END FILE>>>\n```") == "# Title\n\nbody")
print("   a preamble line is stripped:",
      intake.clean("Here is the document you asked for:\n\n# Title\n\nbody") == "# Title\n\nbody")

# ---- 5. formatting is repaired, not refused -----------------------------
print("\n5. formatting is fixed after the reply, never retried:")
raw = "# Cast\n\n## Ana Rey\n\n" + "Tall, grey coat. " * 20 + "\n\n## Open\n\nNo ages.\n"
fixed, changes = intake.repair("characters.md", raw)
probs, shape = intake.validate("characters.md", fixed)
print("   names at ## with no wrapper ->", changes)
print("   problems after repair:", probs, "| kept:", "## Characters" in fixed)
raw = "## How old is Ana?\n- **file:** characters.md\n- **why:** " + "art needs it " * 20
fixed, changes = intake.repair(intake.ITEMS, raw)
print("   bolded fields, no numbers ->", changes)
print("   parses:", [(i["n"], i["file"]) for i in openitems.parse(fixed)])
for n, doc, why in [("world.md", "# W\n\n## Only one\n\n" + "text " * 80, "one topic"),
                    ("story.md", "# S\n\n## Only one\n\n" + "text " * 80, "one section"),
                    ("facts.md", "# F\n\n## T\n\n" + "prose " * 80, "no fact lines")]:
    p_, n_ = intake.validate(n, doc)
    print(f"   {n:<14} {why:<14} problems: {p_} | noted: {n_}")
print("\n   nothing shape-related fails a call any more:")
for n, doc, why in [("world.md", "I'm sorry, I cannot.", "a refusal"),
                    ("world.md", "# W\n\ntiny", "a fragment"),
                    (intake.ITEMS, "rambling prose, no items", "unparseable items"),
                    (intake.ITEMS, "## 1. Q?\n- file: w.md\n- A: unlabelled\n", "option, no label")]:
    p_, n_ = intake.validate(n, doc, need_options=True)
    print(f"      {why:<20} problems: {p_} ({len(n_)} notes)")
print("   the only failure is an empty reply:", intake.validate("world.md", "")[0])
print("   truncation is a note:", intake.validate("world.md", "# W\n\n## A\n\n## B\n\n## C\n\n"+"x"*300, truncated=True)[1])

# ---- 6. one failing call does not rerun its siblings --------------------
a, v, note, err = run({**SYNTH, "world.md": ""})
calls = v.meta["intake"]["calls"]
print("\n6. world.md comes back empty (the only real failure):", type(err).__name__)
print("   attempts per destination:", {x["destination"]: x["attempts"] for x in calls})
print("   characters and story tried once each:",
      all(x["attempts"] == 1 for x in calls if x["destination"] in ("characters.md", "story.md")))
print("   nothing written to the desk:", v.meta["files_written"] == [])
bad = [x for x in calls if x["destination"] == "world.md"][0]
print("   nothing to keep from an empty reply:", bad.get("rejected_kept_as"))

# ---- 6c. a refusal-shaped or thin reply is still used ------------------
a, v, note, err = run({**SYNTH, "world.md": "# World\n\n## One\n\n" + "sparse. " * 40})
wc = [x for x in v.meta["intake"]["calls"] if x["destination"] == "world.md"][0]
print("\n6c. a thin world.md, one section:")
print("   attempts:", wc["attempts"], "| status:", wc["status"], "| notes:", wc["notes"])
print("   used anyway:", "world.md" in v.meta["files_written"])

# ---- 6b. a badly shaped but real reply is kept and fixed ---------------
messy = ("# Cast\n\n## Ana Rey\n\n" + "Tall, grey coat, brass gauge. " * 30
         + "\n\n## Tomas Reed\n\n" + "Quiet, from Halyard. " * 30)
a, v, note, err = run({**SYNTH, "characters.md": messy})
ch = [x for x in v.meta["intake"]["calls"] if x["destination"] == "characters.md"][0]
print("\n6b. a characters file with no '## Characters' wrapper:")
print("   attempts:", ch["attempts"], "| status:", ch["status"], "| repairs:", ch["repairs"])
print("   written to the desk:", "characters.md" in v.meta["files_written"])
print("   wrapper present on disk:",
      "## Characters" in (projects.read_artifact(slug, "characters.md") or ""))

# ---- 7. preservation is telemetry, never a gate -------------------------
a, v, note, err = run(SYNTH, keep=0.12)
calls = v.meta["intake"]["calls"]
pres = [x["preservation"] for x in calls if x.get("preservation")][0]
print("\n7. a badly thinned set:", "error" if err else "completed")
print("   measured:", {k: pres[k] for k in ("coverage", "substantive_coverage", "mass")},
      "| warnings:", len(intake.preservation_warnings(pres)))
print("   dropped by kind:", pres["dropped_counts"])
print("   one round only, no rerun:", len([x for x in calls if x["call"] == "1A"]) == 1)
print("   the thin output was kept:", sorted(v.meta["intake"]["generated_this_run"]))
print("   run reached the gate anyway:", v.meta["intake"]["status"])

# ---- 8. the human gate, then pass 4 in parallel + pass 5 ----------------
a, v, note, err = run(SYNTH)
openitems.answer(slug, 1, "She is 61. Lock it.")
openitems.note_on(slug, 2, "defer", "not until chapter 3")
openitems.set_feedback(slug, "[HIGH] Keep Ana morally ambiguous.\n\n[LOW] More humour for Tomas.")
print("\n8. mode now:", intake.Intake(role, v, lambda *x, **k: None).mode)
a, v, note, err = run({"pass4items": LEFT, intake.FACTS: FACTSFILE})
assert err is None, err
ik = v.meta["intake"]
print("  ", note[:70])
print("   calls:", [x["call"] for x in ik["calls"]], "| peak in flight:", PEAK[0])
print("   status:", ik["status"], "| generated:", ik["generated_this_run"])
print("   notes:", ik["notes_applied"], "| deferred:", ik["deferred"])
p4 = SENT[0][1]["content"]
print("   pass 4 carried: decision", "She is 61. Lock it." in p4,
      "| [HIGH]", "[HIGH] Keep Ana morally ambiguous." in p4,
      "| deferral", "not until chapter 3" in p4, "| no shelf", "Pump research" not in p4)

# ---- 9. soft input ceiling ----------------------------------------------
print("\n9. soft input ceiling:", f"{intake.SOFT_INPUT_CHARS:,} chars",
      "| per-call output budget:", f"{intake.OUTPUT_TOKENS:,} tokens")

# ---- 10. telemetry categories are observational only --------------------
print("\n10. dropped-term categories:")
for t in ["2003", "Caption", "Speculation", "DETECTED", "Astrophage", "Lock's"]:
    print(f"    {t:<12} -> {intake.classify(t)}")
m = intake.preservation({"a": "Astrophage " * 3 + "Caption " * 3 + "x" * 9000},
                        {"b": "nothing relevant here at all"})
print("    craft vocabulary separated:", m["dropped_counts"])
print("    substantive coverage reported:", "substantive_coverage" in m)
print("    no category is a gate:", intake.preservation_warnings(m) and "warnings only")

shutil.rmtree(tmp.parent)
print("\nall checks ran")
