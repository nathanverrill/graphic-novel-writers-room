"""The visual check against a fake provider: briefs, parallel images, checks, review, unknowns."""
import io, pathlib, struct, tempfile, threading, time, zlib

tmp = pathlib.Path(tempfile.mkdtemp()) / "campaigns"
tmp.mkdir(parents=True)
from app import config; config.CAMPAIGNS_DIR = tmp
from app import projects, intake, llm, openitems, usage, visual
from app.agents import get_role
projects.CAMPAIGNS_DIR = tmp; usage.ROOT = tmp.parent

slug = "testbook"; c = tmp / slug
for sub in ("rules", "input", "output"): (c / sub).mkdir(parents=True)
(c / "rules" / "hard.md").write_text("# Rules\n\n- [T] Keel is a copper mine at 3,800 m.\n")
(c / "input" / "notes.md").write_text("# Notes\n\nAna Rey, 61, runs the pumps.\n")
for n, t in (("characters.md", "# Characters\n\n## Characters\n\n### Ana Rey\n\n61, grey braid, brass gauge on a lanyard.\n"),
             ("world.md", "# World\n\n## Keel\n\nAn exhausted copper pit at 3,800 m; pumps below.\n"),
             ("story.md", "# Story\n\n## Premise\n\nAna keeps the water moving.\n"),
             ("facts.md", "# Facts\n\n- [FIXED] Keel is at 3,800 m. (rules/decisions.md)\n"),
             ("open-items.md", "# Open items\n\n## 1. Colour of the pumps?\n- why: art\n- defer: later\n\n## Feedback\n\nkeep it cold\n")):
    (c / "output" / n).write_text(t)

BRIEFS = """# Visual briefs

## 1. world-basin: The basin at dawn
- kind: world
- subject: The three cities seen from above the pit rim.
- required: Keel's open copper pit at 3,800 m, terraced; thin air, hard light.
  Halyard's plateau in the middle distance.
- allowed: time of day, cloud.
- prohibited: neon, skyscrapers, any signage.
- unknown: Is Oasis visible from Keel's rim, or over the horizon?
- unknown: Colour of the pumps?

## 2. character-ana: Ana Rey at the pump head
- kind: character
- subject: Ana Rey, full figure, at a pump head.
- required: 61, grey braid, brass gauge on a lanyard.
- prohibited: lettering.

## 3. scene-pumps: Ana at work below
- kind: scene
- subject: Ana in the pump gallery under Keel.
- required: brass gauge; wet rock.
"""

def png():
    raw = b"".join(b"\x00" + b"\x80\x80\x80" * 4 for _ in range(4))
    def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 4, 4, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))

LOCK, CONC, PEAK, IMG_PROMPTS, CHECKS = threading.Lock(), [0], [0], [], []

def fake_chat(cfg, messages, tools=None, log=None, max_tokens=None):
    user = messages[-1]["content"]
    if isinstance(user, list):                      # pass 8: text + image
        assert any(p.get("type") == "image_url" for p in user), "the check must see the image"
        text = next(p["text"] for p in user if p.get("type") == "text")
        CHECKS.append(text)
        if "character-ana" in text:
            return {"content": "verdict: revise\nfound:\n- a name badge on her jacket, upper left\n- she looks 40", "finish_reason": "stop"}
        return {"content": "verdict: pass\nfound:\n- nothing", "finish_reason": "stop"}
    assert "Derive" not in user
    assert "references" not in user.lower().split("# the project as it stands")[0], "no research shelf"
    assert "## characters.md" in user and "## facts.md" in user
    assert "Ana Rey, 61, runs the pumps" not in user, "input/ is not a source for briefs"
    return {"content": BRIEFS, "finish_reason": "stop"}

def fake_image(cfg, prompt, size=None, log=None):
    with LOCK:
        IMG_PROMPTS.append(prompt); CONC[0] += 1; PEAK[0] = max(PEAK[0], CONC[0])
    time.sleep(0.1)
    with LOCK:
        CONC[0] -= 1
    return png()

llm.chat, llm.generate_image = fake_chat, fake_image
events = []
role = get_role("script_coordinator")
cfg = role.config(); cfg.image_model = "fake/image"      # whatever this machine has set
role.config = lambda: cfg

def run(mode=None):
    v = projects.Version(slug, roles=["script_coordinator"], configs={})
    return visual.Visual(role, v, lambda t, **d: events.append((t, d)), mode=mode).run()

print("parse:", [(b["n"], b["slug"], b["kind"], len(b["unknown"])) for b in visual.parse(BRIEFS)])
b1 = visual.parse(BRIEFS)[0]
assert b1["required"].startswith("Keel's open copper pit") and "Halyard" in b1["required"], "a field runs on"
assert b1["unknown"] == ["Is Oasis visible from Keel's rim, or over the horizon?", "Colour of the pumps?"]

summary = run()
print(summary)
st = visual.state(slug)
assert len(st["briefs"]) == 3 and all(b["image"] for b in st["briefs"]), st
print("images rendered in parallel: peak", PEAK[0], "of", len(IMG_PROMPTS))
assert PEAK[0] >= 2
assert all(p.startswith("A photographic concept reference with NO TEXT") for p in IMG_PROMPTS), "no-text comes first"
assert "Must be shown, exactly as written: Keel's open copper pit" in IMG_PROMPTS[0] or any("Keel's open copper pit" in p for p in IMG_PROMPTS)
ana = next(b for b in st["briefs"] if b["slug"] == "character-ana")
assert ana["verdict"] == "revise" and len(ana["found"]) == 2, ana
assert next(b for b in st["briefs"] if b["slug"] == "world-basin")["verdict"] == "pass"
items = openitems.state(slug)
qs = [i["question"] for i in items["items"]]
print("open items now:", qs)
assert "Is Oasis visible from Keel's rim, or over the horizon?" in qs, "an unknown becomes an open item"
assert qs.count("Colour of the pumps?") == 1, "an unknown already on the list is not added twice"
assert items["feedback"] == "keep it cold", "the Feedback block survives"
assert next(i for i in items["items"] if "Oasis" in i["question"])["from"] == "visual-brief"
files = (c / "output" / "visual-briefs.md").read_text()
assert "- image: images/" in files and "- verdict: revise" in files and "- found: a name badge" in files

# the showrunner's review
visual.review(slug, 2, "back", "older, and no badge")
visual.review(slug, 1, "kept")
st = visual.state(slug)
assert st["kept"] == 1 and st["back"] == 1 and st["unreviewed"] == 1
text = (c / "output" / "visual-briefs.md").read_text()
assert "- note: older, and no badge" in text and "- status: back" in text
assert "- required: 61, grey braid" in text, "the brief itself is untouched"

# the next round renders only what was sent back, with the note in the prompt
IMG_PROMPTS.clear(); CHECKS.clear()
run()
print("regenerated:", len(IMG_PROMPTS), "image(s)")
assert len(IMG_PROMPTS) == 1 and "The showrunner adds: older, and no badge" in IMG_PROMPTS[0]
st = visual.state(slug)
ana = next(b for b in st["briefs"] if b["slug"] == "character-ana")
assert ana["status"] == "" and ana["image"], "sent back -> rendered again -> unreviewed"
assert next(b for b in st["briefs"] if b["slug"] == "world-basin")["status"] == "kept"

# nothing to do
try:
    run(); raise SystemExit("should have refused")
except intake.IntakeError as e:
    print("refused when nothing is sent back:", str(e)[:40])

# mode briefs rewrites the set and renders everything
IMG_PROMPTS.clear()
run("briefs")
assert len(IMG_PROMPTS) == 3

print("\nALL VISUAL CHECKS PASSED")
