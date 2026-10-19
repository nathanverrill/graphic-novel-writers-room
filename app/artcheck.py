"""The art check: a vision model looks at every drawn page for what image models get wrong -
fingers, limbs, faces, clones, garbled text, characters off their locks - before the page is kept.

    check(art, script, refs, key)  ->  {"pass": bool, "problems": [{"panel", "severity", "what"}], "cost"}
    draw_checked(generate, prompt, refs, key)  ->  (art, report, cost): drawn, checked, and redrawn
                                                  with the problems named until it passes or tries run out

A page passes with no "major" problem. Minor problems are recorded, never redrawn for. A major
hands, bodies or faces claim is confirmed on an enlarged crop first; one the close-up doesn't bear
out is kept as minor and marked unconfirmed (small hands are where checkers see ghosts).
"""
import base64
import io
import json
import re
import urllib.error
import urllib.request

MODEL = "meta-llama/llama-4-maverick"    # the art reviewer, the page sent as image bytes (gemini-3.1-pro-preview to 2026-10-15, gemini-4-argon to 10-17, opus-5.5 briefly)
URL = "https://openrouter.ai/api/v1/chat/completions"
TRIES = 3          # the first drawing and two redraws
TIMEOUT = 300

ASK = """You are the art checker for a graphic novel. Image models make the same mistakes again and
again; your job is to catch them on this page before it is printed. Look at every panel closely.

Check, panel by panel:
1. HANDS. Count the fingers on every hand large enough to read: a human hand has a thumb and four
   fingers. Flag extra, missing, fused or boneless fingers, two thumbs, a hand on backwards, a hand
   that melts into an object.
2. BODIES. Extra or missing arms or legs, limbs that come from nowhere, impossible joints, bodies
   merged with each other or with furniture, a head on the wrong way, broken necks, feet sinking into
   floors.
3. FACES. Eyes that don't match or look in two directions, melted or smeared features, extra eyes or
   teeth, a crowd of identical cloned faces, the same named character twice in one panel.
4. CHARACTERS. Compare each named character with their attached reference sheet, if any: wrong
   design, colours, age, hair, costume, or a robot drawn as a different robot.
5. LETTERING. Read every balloon, caption and sign. Flag misspellings, garbled or invented words,
   gibberish signage, lines that are not in the script, script lines that are missing, balloon tails
   pointing at the wrong speaker, balloons that read out of order. Lettering of the panel
   descriptions or stage directions (text meant as instructions) is a major problem.
6. CRAFT. Objects floating or fused, broken perspective that reads as an error, panel borders that
   break or overlap by mistake, a panel that is unreadable mush.
7. SCRIPT. A panel or beat the script asks for that is missing or shows the wrong action.

Severity: "major" only for what a reader would trip over at reading size:
- any misspelled, garbled or invented word in a balloon or caption, or a clearly misspelled sign;
- a balloon tail on the wrong speaker, balloons read in the wrong order, speaker names, stage
  directions or panel descriptions lettered onto the page, a script line missing;
- the wrong person in a role (one character drawn with another's design), a character twice in a
  panel, a character's design clearly changed (different face, hair, costume, colours, robot);
- a real anatomy error you can clearly see; a panel that doesn't read; a story action missing.
Everything else is "minor": a design mirrored left-to-right, a patch or marking on the other side,
lighting, camera angle or prop details that differ from the script, tiny background text. Don't
report style choices. Don't guess about hands too small to read.

Answer with JSON only, no prose around it. "kind" is one of hands, bodies, faces, characters,
lettering, craft, script. "box" is where the problem is, as [ymin, xmin, ymax, xmax] on a 0-1000
scale of the whole page:
{"problems": [{"panel": 1, "kind": "hands", "severity": "major", "what": "Alex's left hand has six fingers", "box": [120, 300, 180, 380]}]}
An empty list when the page is clean."""

# The showrunner's standing checks (2026-10-15): every one is MAJOR when you can see it, on every page.
ALWAYS = """
ALWAYS CHECK, EVERY PAGE - each of these is MAJOR when you can see it:
- Hands: every person has one LEFT hand on the left arm and one RIGHT hand on the right arm (thumb on the correct side). Two right hands, two left hands, or a hand on the wrong arm is major. A pointing arm must end in its own hand. Five fingers on every readable hand.
- Poses and physics: nobody sits or stands balanced on top of a thin railing, floats, or passes through an object. People sit on solid ledges, steps, crates or chairs.
- Eyelines: a speaker faces and looks at the person they are talking to; nobody looks at someone awkwardly, sideways, or at the wrong thing. Two people in conversation face each other.
- Objects a character looks at (a photo, paper, sketch, screen, watch) face THE CHARACTER, not the reader.
- No body part (crotch, elbow, back) beside another character's face; close two-shots are face to face at eye level.
- People who are together in the script stay together: nobody walks away with their back to the person they are with.
- Continuity: lighting, place and mood stay the same across adjacent panels of one continuous moment.
- Setting: each panel is in the place the script says (a scene in a home stays in that home; no stray outdoor or industrial background).
- Tone: the expressions match the script (hard times are not drawn as happy or celebratory).
- Characters match their locks exactly; one character is never drawn with another's design (Alex's daughter is never drawn as Ada).
- Lettering, when there is lettering: every balloon tail points at the character who speaks that line; no balloon or caption covers ANY part of a face; no text that is not in the script (no invented captions, titles or place names); every word spelled and punctuated exactly.
"""

CONFIRM = """This is a close-up from a graphic novel page. Look for drawing mistakes in the {kind} here:
for hands, count the fingers you can clearly see on each hand (a finger hidden by an object or the
angle is not missing; a thumb and four fingers is correct) and look for fused or extra fingers; for
bodies, extra, missing or impossible limbs; for faces, mismatched or melted features. Report only
mistakes you can clearly see, not ones you suspect. Answer with JSON only:
{{"mistakes": ["..."]}}, an empty list when the drawing is correct or too small to judge."""
CONFIRM_MODEL = "anthropic/claude-opus-5.5"   # a second pair of eyes, not the first checker again
ZOOMED = {"hands", "bodies", "faces"}       # small-detail claims are confirmed on a close-up


def _url(data, mime="image/png"):
    return f"data:{mime};base64," + base64.b64encode(data).decode()


def _ask(content, key, model):
    """(text, cost) from one chat call; raises on a network failure."""
    body = {"model": model, "messages": [{"role": "user", "content": content}], "temperature": 0}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                          "HTTP-Referer": "https://github.com/writers-room", "X-Title": "artcheck"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        data = json.loads(r.read())
    return (data.get("choices") or [{}])[0].get("message", {}).get("content") or "", (data.get("usage") or {}).get("cost") or 0


def _json(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    try:
        return json.loads(m.group(0)) if m else None
    except json.JSONDecodeError:
        return None


def crop(art, box, pad=0.35, side=768):
    """The flagged area, padded by a share of its own size and enlarged, as PNG bytes; None
    without a usable box."""
    from PIL import Image
    try:
        y0, x0, y1, x1 = [float(v) / 1000 for v in box]
    except (TypeError, ValueError):
        return None
    im = Image.open(io.BytesIO(art)).convert("RGB")
    w, h = im.size
    px, py = max(0.015, (x1 - x0) * pad), max(0.01, (y1 - y0) * pad)
    x0, y0, x1, y1 = max(0, x0 - px), max(0, y0 - py), min(1, x1 + px), min(1, y1 + py)
    if x1 <= x0 or y1 <= y0:
        return None
    c = im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
    size = (side, max(1, int(side * c.height / c.width))) if c.width >= c.height else (max(1, int(side * c.width / c.height)), side)
    buf = io.BytesIO()
    c.resize(size, Image.LANCZOS).save(buf, "PNG")
    return buf.getvalue()


def confirm(art, problem, key, model=CONFIRM_MODEL):
    """(real, cost): a second, blind look at a hands/bodies/faces claim on an enlarged crop - the
    second model is not told the claim, only what kind of thing to look at."""
    close = crop(art, problem.get("box"))
    if close is None:
        return True, 0
    text, cost = _ask([{"type": "text", "text": CONFIRM.format(kind=problem.get("kind", "drawing"))},
                       {"type": "image_url", "image_url": {"url": _url(close)}}], key, model)
    verdict = _json(text)
    return bool(verdict.get("mistakes")) if verdict else True, cost


UNLETTERED = ("\n\nTHIS PAGE IS ART ONLY: the lettering is added later on its own layer. Don't check for script "
              "lines. Any balloon, caption or lettered dialogue drawn into the art is a major problem; in-world "
              "signs and screens are fine if spelled correctly.")


UNLETTERED_SFX = ("\n\nTHIS PAGE IS ART PLUS SOUND EFFECTS: balloons and captions are added later on their own layer. "
                  "Don't check for script lines. The only lettering drawn into the art should be these sound effects, "
                  "each spelled exactly: {sfx}. A sound effect misspelled, missing or doubled is a major problem; any "
                  "balloon, caption or lettered dialogue drawn into the art is a major problem; in-world signs and "
                  "screens are fine if spelled correctly.")


def check(art, script, refs, key, model=MODEL, lettered=True):
    """lettered: True (the page carries all its lettering), False (art only), or the sound
    effects, as text, when the art carries those and nothing else."""
    ask = ASK + ALWAYS + ("" if lettered is True else UNLETTERED_SFX.format(sfx=lettered) if lettered else UNLETTERED)
    content = [{"type": "text", "text": ask + "\n\n=== THE SCRIPT FOR THIS PAGE ===\n\n" + (script or "(none)")}]
    for label, path in refs or []:
        content += [{"type": "text", "text": f"Reference: {label}"},
                    {"type": "image_url", "image_url": {"url": _url(path.read_bytes())}}]
    content += [{"type": "text", "text": "THE PAGE TO CHECK:"}, {"type": "image_url", "image_url": {"url": _url(art)}}]
    try:
        text, cost = _ask(content, key, model)
    except (urllib.error.URLError, TimeoutError) as e:
        return {"pass": True, "problems": [], "cost": None, "error": f"check did not run: {e}"[:300]}
    answer = _json(text)
    if not answer or not isinstance(answer.get("problems"), list):
        return {"pass": True, "problems": [], "cost": cost, "error": "unreadable answer"}
    problems = answer["problems"]
    for p in problems:
        if p.get("severity") == "major" and p.get("kind") in ZOOMED:
            try:
                real, c = confirm(art, p, key)
            except (urllib.error.URLError, TimeoutError):
                real, c = True, 0
            cost += c
            if not real:
                p["severity"], p["unconfirmed"] = "minor", True
    return {"pass": not any(p.get("severity") == "major" for p in problems), "problems": problems, "cost": cost}


def fix_note(problems):
    return ("\n\nTHE LAST DRAWING OF THIS PAGE FAILED THE ART CHECK. Draw it fresh and avoid these mistakes:\n"
            + "\n".join(f"- panel {p.get('panel', '?')}: {p.get('what')}" for p in problems if p.get("severity") == "major")
            + "\nEvery visible hand has a thumb and four fingers. Every word is spelled exactly as written.")


def draw_checked(generate, prompt, refs, key, script=None, tries=TRIES, lettered=True, stage=None):
    """Draw, check, redraw with the problems named. Keeps the drawing with the fewest major problems.
    stage(name, attempt), if given, hears "drawing" and "checking" as each try moves on."""
    best, total, history = None, 0.0, []
    note = ""
    stage = stage or (lambda name, attempt: None)
    for attempt in range(1, tries + 1):
        stage("drawing", attempt)
        art, cost = generate(prompt + note, refs)
        stage("checking", attempt)
        report = check(art, script or prompt, refs, key, lettered=lettered)
        total += (cost or 0) + (report.get("cost") or 0)
        majors = sum(p.get("severity") == "major" for p in report["problems"])
        history.append({"attempt": attempt, "majors": majors, "problems": report["problems"], "error": report.get("error")})
        if best is None or majors < best[0]:
            best = (majors, art, report)
        if report["pass"]:
            break
        note = fix_note(report["problems"])
    majors, art, report = best
    return art, {**report, "attempts": history}, total
