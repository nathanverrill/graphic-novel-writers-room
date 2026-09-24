"""Two desks: intake writes to preproduction/, production starts from a copy, and never the
other way round. Also the one-time migration from the old single output/ desk."""
import json, pathlib, tempfile

tmp = pathlib.Path(tempfile.mkdtemp()) / "campaigns"
tmp.mkdir(parents=True)
from app import config; config.CAMPAIGNS_DIR = tmp
from app import projects, review
projects.CAMPAIGNS_DIR = tmp

slug = projects.create_project("Two Desks", "a pitch")
c = tmp / slug
assert (c / "preproduction").is_dir() and (c / "production").is_dir() and not (c / "output").exists()

# 1. intake writes to its own desk, through a round and through a hand edit
v = projects.Round(slug, desk=projects.PRE, run_id="t")
v.write("story.md", "# Story\n\nintake's reading\n")
projects.write_artifact(slug, "open-items.md", "## 1. Q?\n", desk=projects.PRE)
assert (c / "preproduction" / "story.md").read_text().startswith("# Story")
assert not (c / "production" / "story.md").exists(), "intake must never write to production/"
assert v.dir.parent == c / "preproduction" / "previous", "intake's rounds live on intake's desk"
assert projects.list_versions(slug) == [] and len(projects.list_versions(slug, projects.PRE)) == 1
print("1. intake writes only to preproduction/: ok")

# 2. production starts from a copy; rewriting it leaves intake's alone
assert sorted(projects.seed_production(slug)) == ["open-items.md", "story.md"]
projects.write_artifact(slug, "story.md", "# Story\n\nthe Plotter's rewrite\n")
assert "intake's reading" in projects.read_artifact(slug, "story.md", desk=projects.PRE)
assert "Plotter" in projects.read_artifact(slug, "story.md")
r = projects.Round(slug, run_id="p")
assert r.dir.parent == c / "production" / "previous" and r.id == "r01-ai", "production numbers its own rounds"
print("2. production is a copy, and its rounds are its own: ok")

# 3. neither desk is library material
assert not any(projects.never_read(pathlib.Path(x)) is False for x in ("x/preproduction/a.md", "x/production/a.md", "x/output/a.md"))
assert projects.never_read(pathlib.Path("x/input/a.md")) is False
print("3. never_read skips both desks: ok")

# 4. migration: an old campaign with one output/ desk and an intake round on record
old = tmp / "oldbook"
for sub in ("rules", "input", "output", "output/previous/oldbook-r03-ai"): (old / sub).mkdir(parents=True)
(old / "output" / "story.md").write_text("# rewritten by production\n")
rd = old / "output" / "previous" / "oldbook-r03-ai"
(rd / "oldbook-r03-ai-run.json").write_text(json.dumps({"id": "r03-ai", "kind": "ai", "intake": {"mode": "synthesis"}}))
(rd / "oldbook-r03-ai-story.md").write_text("# as intake left it\n")
assert projects.migrate("oldbook") is True
assert not (old / "output").exists() and (old / "production" / "story.md").read_text().startswith("# rewritten")
assert (old / "preproduction" / "story.md").read_text() == "# as intake left it\n"
assert projects.migrate("oldbook") is False, "runs once"
print("4. migration renames output/ and seeds preproduction/ from the last intake round: ok")

# 5. the desk a phase works on
assert projects.desk_for("intake") == projects.PRE and projects.desk_for("development") == projects.PROD
print("5. desk_for: ok")

# 6. drafts come onto the production desk as draft.md, and go when they go
(c / "drafts").mkdir(exist_ok=True)
(c / "drafts" / "chapter-02.md").write_text("# Two\n\nlater\n")
(c / "drafts" / "chapter-01.md").write_text("# One\n\nfirst\n")
assert "draft.md" in projects.seed_production(slug)
d = projects.read_artifact(slug, "draft.md")
assert d.index("chapter-01.md") < d.index("chapter-02.md") and "first" in d and "later" in d
from app import phases
assert "draft.md" in (phases.note(slug, phases.get("writing")) or "")
assert "draft.md" not in (phases.note(slug, phases.get("execution")) or "")
for p in (c / "drafts").glob("*.md"): p.unlink()
projects.seed_production(slug)
assert projects.read_artifact(slug, "draft.md") is None
print("6. drafts seed production as draft.md, in order, and the phases brief the room on it: ok")

# 7. approve for production: only with every item answered or deferred, folded in, and facts written
from app import openitems as _oi
aslug = projects.create_project("Approve Book", "a pitch")
r = phases.readiness(aslug)
assert not r["ready"] and "facts.md" in r["why"], r
projects.write_artifact(aslug, "facts.md", "- a fact", desk=projects.PRE)
projects.write_artifact(aslug, _oi.ITEMS, "## 1. Who is the woman?\n- why: it matters\n- A: Mera\n", desk=projects.PRE)
r = phases.readiness(aslug)
assert not r["ready"] and "1 open item" in r["why"], r
try:
    phases.approve_preproduction(aslug, "evoke"); raise AssertionError("approved with an open item")
except ValueError:
    pass
projects.write_artifact(aslug, _oi.ITEMS, "## 1. Who is the woman?\n- why: it matters\n- defer: later\n", desk=projects.PRE)
review.save_settings(aslug, magic={"status": "failed", "step": "development", "log": [{"t": 0, "text": "old"}]})
assert phases.readiness(aslug)["ready"]
try:
    phases.approve_preproduction(aslug, "yes"); raise AssertionError("approved without the word")
except ValueError:
    pass
st = phases.approve_preproduction(aslug, " Evoke ")
s = review.settings(aslug)
assert st["phase"] == "development" and s["approved"]["at"] and s["magic"]["status"] == "idle"
assert [l["text"] for l in s["magic"]["log"]] and "old" not in s["magic"]["log"][0]["text"]
print("7. approve for production waits for every item, then starts production clean: ok")

# 8. the second update of the canon takes the room's recommendation for what is left unanswered
from app import intake as _in
rslug = projects.create_project("Recs Book", "a pitch")
projects.write_artifact(rslug, _oi.ITEMS, "## 1. Who is the woman?\n- why: it matters\n- A: Mera\n- B: Ada\n- suggested: B\n"
                        "## 2. How old is he?\n- why: it matters\n- A: nine\n- defer: later\n", desk=projects.PRE)
real = projects.list_versions
try:
    projects.list_versions = lambda slug, desk=projects.PROD: [{"id": "r02-ai", "status": "awaiting_showrunner_decisions", "intake": {"mode": "synthesis"}}]
    assert _oi.revisions(rslug) == 0 and _oi.recommended(rslug) == [], "the first update is the showrunner's alone"
    projects.list_versions = lambda slug, desk=projects.PROD: [
        {"id": "r03-ai", "status": "ready_for_review", "intake": {"mode": "revision"}},
        {"id": "r02-ai", "status": "awaiting_showrunner_decisions", "intake": {"mode": "synthesis"}}]
    assert _oi.revisions(rslug) == 1
    recs = _oi.recommended(rslug)
    assert [r["n"] for r in recs] == [1] and recs[0]["answer"].startswith("Ada (the room's recommendation, option B")
    work = _in.pending(rslug)
    assert work["any"] and [d["n"] for d in work["decisions"]] == [1] and [d["n"] for d in work["deferred"]] == [2]
    r = phases.readiness(rslug)
    assert r["will_recommend"] == 1 and "Update canon again" in r["why"], r
finally:
    projects.list_versions = real
print("8. the second update takes the room's recommendation; deferred items stay put: ok")
