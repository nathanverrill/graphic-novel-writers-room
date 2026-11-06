"""prosperity-book pages from a given layouts file: art (no lettering) -> SVG overlay + layer -> image-model lettering. PAGES env; LAYOUTS env."""
import sys, os, re, json, io, time, concurrent.futures as cf
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[3]))
from app import artcheck, projects, prompts, render, lettering, usage
from PIL import Image
SLUG = "prosperity-book"; TAG = "sunburst"; key = render.api_key()
C = projects.campaign_dir(SLUG); R = C / "renders" / TAG
for k in ("art", "lettered", "lettered-model", "overlay"): (R / k).mkdir(parents=True, exist_ok=True)
specs = {d["page"]: d for d in (json.loads(m.group(1)) for m in re.finditer(r"```layout\n(.*?)\n```", open(os.environ["LAYOUTS"]).read(), re.S))}
PAGES = [int(x) for x in os.environ["PAGES"].split(",")]
ctx = {**prompts.context(SLUG), "slug": SLUG, "lettering": "layer"}
L = C / "style" / "locks"; PR = C / "style" / "props"
plate = C / "style/plate.png"; oasis = C / "style/oasis-reference.png"; letref = C / "style/lettering-reference.png"
older = L / "alex-2070-sunburst/lock.png"; young = L / "alex-phantum-sunburst/lock.png"; girl = L / "alex-daughter-sunburst/lock.png"
watch = PR / "adrian-watch.png"; pump = PR / "pump-repair.png"
STYLE = ("ART STYLE: inked graphic-novel realism exactly like the character locks and plate: bold confident black ink contours, hatching in the shadows, "
         "matte painterly colour, gritty hand-made texture. Clear eyelines: characters look at whoever or whatever they react to. Exactly five fingers on every hand. "
         "Draw NO lettering: no balloons, captions or readable text; leave calm space where balloons will go, and leave signs, screens and headline bands blank.\n\n")
FUTURE = ("2070 (overrides anything below): Alex is about 45, exactly as the ALEX in 2070 lock: grey at the temples, stubble, brown work jacket, no backpack; "
          "his daughter matches her lock on every panel. Homes and city built the way Oasis was in 2043 (the attached Oasis), never present-day suburbia. "
          "Only a final Keel 2043 panel, if there is one, shows Alex at eighteen, rust and charcoal.\n\n")
HOUSES = ("THE CHARTER HOUSES, whenever they appear: HELION's insignia, uniforms, signs and light are deep amber-orange; AQUALIS's cool jade-teal; ASTRA's pale steel-violet.\n\n")
NOTES = {}
NOTES.update(json.loads(os.environ.get("NOTES", "{}")))
LNOTES = json.loads(os.environ.get("LNOTES", "{}"))
def refs_for(n, spec):
    base = render.references(SLUG, TAG, spec, ctx)
    if n <= 4:
        base = [((("ALEX at eighteen: only the final Keel 2043 panel", p) if n == 4 else ("ALEX in 2070, about 45: draw him exactly as this lock", older))
                 if "alex-phantum-sunburst" in str(p) else (l, p)) for l, p in base]
        if not any(p == older for _, p in base): base.append(("ALEX in 2070, about 45: draw him exactly as this lock", older))
        base = [(l, p) for l, p in base if "ada-veyra" not in str(p) and "alex-daughter" not in str(p)]
        base.append(("ALEX'S DAUGHTER, about 9: draw her EXACTLY as this lock on every panel - long curly dark-brown hair, brown eyes, orange H2O jacket, teal planet T-shirt. She is NOT Ada: never red hair, never an olive jacket", girl))
        base.append(("the Oasis: the 2070 homes and cities are built in this architecture", oasis))
    if os.environ.get("EARLIER") and (R.parent / os.environ["EARLIER"] / f"art-p{n:02d}.png").exists():
        base.append(("the earlier version of this page: keep everything the notes do not change", R.parent / os.environ["EARLIER"] / f"art-p{n:02d}.png"))
    if n >= 11: base.append(("Adrian's watch: draw it exactly like this whenever it appears", watch))
    if n == 6: base.append(("the Keel pump Alex repairs: draw this exact unit", pump))
    return base
def lines_of(spec):
    return "\n".join(f'- Panel {i["panel"]}, {i["type"]}' + (f' ({i["speaker"]})' if i.get("speaker") else "") + f': "{i["text"]}"'
                     for i in spec.get("items", []) if i.get("text"))
def one(n):
    spec = specs[n]; refs = refs_for(n, spec); t0 = time.time()
    pre = STYLE + artcheck.ALWAYS.split("- Lettering")[0] + "\n" + (FUTURE if n <= 4 else "") + (HOUSES if n >= 36 else "") + (NOTES.get(str(n), "") + "\n\n" if str(n) in NOTES else "")
    art, rep, cost = artcheck.draw_checked(lambda t, r: render.generate(render.MODELS[TAG], t, r, key), pre + render.prompt_for(spec, ctx, refs), refs, key, lettered=False)
    (R / "art" / f"p{n:02d}.png").write_bytes(art)
    usage.ledger(SLUG, "renderer", "page", render.MODELS[TAG], cost, time.time() - t0, page=n, tries=len(rep["attempts"]), check_pass=rep["pass"])
    im = Image.open(io.BytesIO(art)); rects = lettering.detect_rects(spec, art)
    (R / "overlay" / f"p{n:02d}.svg").write_text(lettering.svg(spec, {**ctx, "page_label": False, "page_size": (1000, round(1000 * im.height / im.width))}, rects))
    (R / "lettered" / f"p{n:02d}.png").write_bytes(render.letter(art, spec, ctx))
    lines = lines_of(spec); lcost = 0; lrep = {"pass": True, "attempts": [], "problems": []}
    if lines:
        LP = ("Letter this comic page. The first attached image is the finished art: keep every line of it EXACTLY the same, change nothing in the drawing. "
              "Add only the lettering below, designed into the panels like the attached lettering reference: small, wide, clean white speech balloons with short tails and thin outlines, "
              "in calm space beside the speaker, tail pointing at the speaker's mouth, never over a face, hand or the key object, read in order top-left to bottom-right; "
              "captions as small cream boxes with dark text in panel corners; place-and-time captions as small yellow boxes top-left; screen and sign text drawn onto the screen or sign in the art; "
              "sound effects as warm hand-lettered caps in the scene's light, next to their source. Use exactly these words, spelled and punctuated exactly, uppercase comic lettering. ADD NO OTHER TEXT: no captions, titles, place names, dates or words that are not in this list:\n" + lines + ("\n\nPLACEMENT: " + LNOTES[str(n)] if str(n) in LNOTES else ""))
        lrefs = [("the finished art: keep it exactly, add only the lettering", R / "art" / f"p{n:02d}.png"), ("lettering reference: balloon, caption and sound-effect style", letref)]
        t1 = time.time()
        lart, lrep, lcost = artcheck.draw_checked(lambda t, r: render.generate(render.MODELS[TAG], t, r, key), LP, lrefs, key, script=lines, lettered=True)
        (R / "lettered-model" / f"p{n:02d}.png").write_bytes(lart)
        usage.ledger(SLUG, "renderer", "letter", render.MODELS[TAG], lcost, time.time() - t1, page=n, tries=len(lrep["attempts"]), check_pass=lrep["pass"])
    else:
        (R / "lettered-model" / f"p{n:02d}.png").write_bytes(art)
    return n, round(cost + lcost, 3), rep["pass"], lrep["pass"], [p.get("what", "")[:80] for p in rep["problems"] + lrep["problems"]][:4]
def safe(n):
    try: return one(n)
    except Exception as e: return n, "FAILED", repr(e)[:200]
with cf.ThreadPoolExecutor(int(os.environ.get("WORKERS", "4"))) as ex:
    for r in ex.map(safe, PAGES): print(*r, flush=True)
