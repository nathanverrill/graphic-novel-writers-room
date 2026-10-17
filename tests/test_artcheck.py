"""The art check, with no model called: _ask is replaced by canned answers.

Runs with plain python3 from the repo root (PYTHONPATH=.)."""
import io, json
from PIL import Image
from app import artcheck

buf = io.BytesIO(); Image.new("RGB", (1024, 1536), "white").save(buf, "PNG"); ART = buf.getvalue()
answers, asked = [], []
def fake(content, key, model):
    asked.append((model, content)); return answers.pop(0), 0.01
artcheck._ask = fake

# 1. a lettering problem is major as reported; a hands claim the blind close-up doesn't see goes minor
answers[:] = [json.dumps({"problems": [
    {"panel": 1, "kind": "lettering", "severity": "major", "what": "AEE for AGE", "box": [10, 10, 20, 20]},
    {"panel": 2, "kind": "hands", "severity": "major", "what": "six fingers", "box": [100, 100, 200, 200]}]}),
    json.dumps({"mistakes": []})]
r = artcheck.check(ART, "script", [], "k")
assert not r["pass"] and r["problems"][1]["severity"] == "minor" and r["problems"][1]["unconfirmed"], r
assert asked[1][0] == artcheck.CONFIRM_MODEL and "six fingers" not in json.dumps(asked[1][1]), "the confirmation is blind"

# 2. a hands claim the close-up confirms stays major; with nothing else wrong the page fails on it
asked.clear()
answers[:] = [json.dumps({"problems": [{"panel": 2, "kind": "hands", "severity": "major", "what": "x", "box": [100, 100, 200, 200]}]}),
              json.dumps({"mistakes": ["a sixth finger on the left hand"]})]
assert not artcheck.check(ART, "s", [], "k")["pass"]

# 3. a clean page passes; an unreadable answer passes but says so; unlettered art is told it is art only
answers[:] = ['{"problems": []}']
assert artcheck.check(ART, "s", [], "k")["pass"]
answers[:] = ["I think it looks fine"]
r = artcheck.check(ART, "s", [], "k"); assert r["pass"] and r["error"] == "unreadable answer"
asked.clear(); answers[:] = ['{"problems": []}']
artcheck.check(ART, "s", [], "k", lettered=False)
assert "ART ONLY" in asked[0][1][0]["text"]

# 4. crop: padded by its own size, enlarged; no box or a backwards one, no crop
c = Image.open(io.BytesIO(artcheck.crop(ART, [100, 100, 150, 150])))
assert max(c.size) == 768
assert artcheck.crop(ART, None) is None and artcheck.crop(ART, [50, 50, 10, 10]) is None

# 5. draw_checked: redraws with the problems named, stops at a pass, keeps the fewest majors
drawn = []
def gen(prompt, refs):
    drawn.append(prompt); return ART, 0.2
answers[:] = [json.dumps({"problems": [{"panel": 1, "kind": "lettering", "severity": "major", "what": "TAVEL"}]}), '{"problems": []}']
art, rep, cost = artcheck.draw_checked(gen, "PAGE", [], "k")
assert len(drawn) == 2 and "TAVEL" in drawn[1] and "FAILED THE ART CHECK" in drawn[1] and rep["pass"], drawn
assert len(rep["attempts"]) == 2 and round(cost, 2) == 0.42
drawn.clear()
bad = json.dumps({"problems": [{"panel": 1, "kind": "lettering", "severity": "major", "what": "x"}]})
answers[:] = [bad, bad, bad]
art, rep, cost = artcheck.draw_checked(gen, "PAGE", [], "k")
assert len(drawn) == artcheck.TRIES and not rep["pass"]
print("artcheck ok")
