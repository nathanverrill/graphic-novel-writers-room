"""The Pass 2 / Pass 3 prompt contract: the rules the showrunner asked for are actually in
the text the model receives. These check prompts, never model output - nothing here is a
retry gate."""
import pathlib, re, sys, tempfile

tmp = pathlib.Path(tempfile.mkdtemp()) / "campaigns"; tmp.mkdir(parents=True)
from app import config; config.CAMPAIGNS_DIR = tmp
from app import projects, intake
projects.CAMPAIGNS_DIR = tmp

slug = "t"; c = tmp / slug
for sub in ("rules", "input", "references", "output"): (c / sub).mkdir(parents=True)
(c / "rules" / "r.md").write_text("# Rules\n\nThe book is hard SF.\n")
(c / "input" / "notes.md").write_text("# Notes\n\nKeel is a mine. Ana Rey works there.\n")
(c / "references" / "mining.md").write_text("# Mining research\n\nOpen-pit versus underground.\n")
(c / "input" / intake.ITEMS).write_text(
    "## 1. What kind of mine is Keel?\n- file: world.md\n"
    "- why: Keel cannot plausibly be open-pit given the underground working the drafts show\n")
for n in intake.CORE:
    projects.write_artifact(slug, n, f"# {n}\n\n## A\n\n## B\n\n## C\n\ntext\n")
projects.write_artifact(slug, intake.ITEMS,
    "# Open Items\n\n## 1. Who is the TRACK observer?\n- file: characters.md\n"
    "- evidence: an unseen woman chooses TRACK\n- why: the reveal depends on it\n- from: showrunner\n")

class V:
    slug = slug; id = "dry"; prefix = "t-"; meta = {"run_id": "dry"}
    def next_call_number(self): return 0

from app.agents import load_roles
role = [r for r in load_roles() if r.id == "script_coordinator"][0]
a = intake.Intake(role, V(), lambda *x, **k: None, mode=intake.SYNTHESIS)

p2_sys = a.system_prompt(intake.OPEN_ITEMS)
p2_user = a.open_items_message(a.desk(), None)
p3_sys = a.system_prompt(intake.OPTIONS)
p3_user = a.options_message("## 1. Q?\n- file: world.md\n- why: x\n", None)

fails = []
def check(n, where, text, needle, label):
    ok = (needle.lower() in text.lower()) if isinstance(needle, str) else bool(needle.search(text))
    print(f"  {n}. {label:<62} {'ok' if ok else 'MISSING'}  [{where}]")
    if not ok: fails.append(label)

print("Pass 2 — the prompt requires:")
check(1, "p2 guide", p2_sys, "must not disappear because the new synthesis forgot",
      "prior items survive unless genuinely resolved")
check(1, "p2 input", p2_user, "does not disappear because the new synthesis forgot",
      "  ...and the same rule reaches the user message")
check(2, "p2 guide", p2_sys, "reconcile", "prior items are reconciled with newly discovered ones")
check(2, "p2 input", p2_user, "How to reconcile a prior item", "  ...with the reconciliation rules")
check(3, "p2 guide", p2_sys, "stating one interpretation confidently does not resolve",
      "a confident synthesis does not resolve an item")
check(3, "p2 guide", p2_sys, "open-pit lithium mine", "  ...with the Keel worked example")
check(0, "p2 guide", p2_sys, "still unresolved", "the five dispositions are spelled out")
check(0, "p2 guide", p2_sys, "partially resolved", "  ...including partially resolved")
check(0, "p2 input", p2_user, "Who is the TRACK observer", "the desk's prior list is in the prompt")
check(0, "p2 input", p2_user, "# Existing showrunner open items", "the showrunner source has its own section")
check(0, "p2 input", p2_user, f"Source: input/{intake.ITEMS}", "  ...named by its real path")
check(0, "p2 input", p2_user, "What kind of mine is Keel", "  ...with their list in it")
check(0, "p2 input", p2_user, "# The room's current open-items list", "the desk list is delimited separately")
check(0, "p2 input", p2_user, "a broader question is not the same item as a specific one",
      "a broader question does not replace a specific one")
print(f"  0. {'pass 2 gets NO research shelf':<62} "
      f"{'ok' if 'references/' not in p2_user else 'LEAK'}  [p2 input]")
if "references/" in p2_user: fails.append("pass 2 research leak")
check(0, "p2 guide", p2_sys, "do not create trivia", "trivia is discouraged with examples")

print("\nPass 3 — the prompt requires:")
check(4, "p3 guide", p3_sys, "only** when authoritative material already answers",
      "[established] needs direct authoritative support")
check(4, "p3 guide", p3_sys, "the answer seems obvious", "  ...with the list of bad reasons")
check(5, "p3 guide", p3_sys, "label by the least-supported consequential claim",
      "least-supported consequential claim sets the label")
check(5, "p3 guide", p3_sys, "Tomaso", "  ...with the Tomas/Tomaso example")
check(6, "p3 guide", p3_sys, "cannot be answered `[established]`",
      "an unestablished question cannot get an [established] answer")
check(6, "p3 guide", p3_sys, "Adrian transferred", "  ...with the Adrian transfer example")
check(7, "p3 guide", p3_sys, "Synthesis files are not authority",
      "synthesis files cannot launder their own inference")
check(7, "p3 guide", p3_sys, "working name", "  ...and working names are not established names")
check(0, "p3 guide", p3_sys, "suggestion", "a suggestion does not strengthen a label")
check(0, "p3 guide", p3_sys, "explicit decision", "only an explicit showrunner decision is established")
check(0, "p3 input", p3_user, "references/", "pass 3 DOES get the research shelf")
check(8, "p3 guide", p3_sys, "does not make your application of that framework",
      "an established framework does not establish its application")
check(9, "p3 guide", p3_sys, "The research challenge", "pass 3 runs a research challenge")
check(9, "p3 guide", p3_sys, "from: research-check", "  ...and marks what it finds from: research-check")
check(9, "p3 guide", p3_sys, "fictional geology that conflicts with real geology",
      "  ...with the kinds of problem to look for")
check(9, "p3 input", p3_user, "from: research-check", "  ...and the user message says so too")
check(10, "p3 guide", p3_sys, "Would ignoring this create a meaningful plausibility",
      "a materiality test gates a research-found item")
check(10, "p3 guide", p3_sys, "merely because the research contains more\ndetail",
      "  ...detail alone is not a reason")
check(11, "p3 guide", p3_sys, "Internal consistency is not plausibility",
      "internal agreement is not evidence of being right")
print()
print("  the old restriction is gone:",
      "Do not add new items" not in p3_sys and "not reopening it" not in p3_user)
if "Do not add new items" in p3_sys: fails.append("pass 3 still forbidden from adding items")
check(8, "p3 guide", p3_sys, "is the thing I am proposing established, or is the thing it rests on",
      "  ...with the test question")

print("\nNo new gates:")
probs, notes = intake.validate(intake.ITEMS, "## 1. Q?\n- file: w.md\n- A: unlabelled option\n" + "x"*300,
                               need_options=True)
print(f"  an unlabelled option still does not fail a call: {probs == []}  (notes: {len(notes)})")
if probs: fails.append("unlabelled option became a failure")

import shutil; shutil.rmtree(tmp.parent)
print(f"\n{'ALL PROMPT CONTRACTS PRESENT' if not fails else 'MISSING: ' + '; '.join(fails)}")
sys.exit(1 if fails else 0)
