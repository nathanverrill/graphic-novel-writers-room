import time
"""Strict QA of lettered pages + automatic fixes. PAGES env, LAYOUTS env.
Art problems (anatomy, impossible poses, wrong character, wrong gaze) -> redraw art with the problems named, then re-letter.
Lettering problems (tail on the wrong speaker, invented/missing/misspelled text, cover a face) -> re-letter with the fixes named."""
import sys, os, re, json, time, base64, io
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[3]))
from app import artcheck, projects, prompts, render, usage
SLUG="prosperity-book"; TAG="sunburst"; key=render.api_key(); C=projects.campaign_dir(SLUG); R=C/"renders"/TAG
specs={d["page"]:d for d in (json.loads(m.group(1)) for m in re.finditer(r"```layout\n(.*?)\n```",open(os.environ["LAYOUTS"]).read(),re.S))}
WHO = {"ALEX":"Alex: young man, 18, messy black wavy hair, brown work jacket (in the 2070 prologue: about 45, grey temples, stubble)",
 "ADA":"Ada: young woman, shoulder-length tousled RED hair, olive field jacket", "BI11BOT":"Bi11bot: small round-headed blue-and-yellow robot with a red scarf",
 "GRANDMOTHER":"Grandmother: elderly woman, curly grey hair pinned up, red woven shawl", "ADRIAN":"Adrian: lean man, curly black hair greying, long coat and tie (often a blue hologram)",
 "DAUGHTER":"Alex's daughter: girl about 9, long curly dark-brown hair, orange jacket", "TOMAS":"Tomas: older miner with a grey moustache and helmet",
 "SUPERVISOR":"the supervisor: bearded man with folded arms", "GUARD":"the checkpoint guard", "BOUNCER":"the bouncer: bald man in a doorway"}
QA = """You are the final quality editor of a graphic novel page. Be strict: the page must read with no AI mistakes.
Check and report every MAJOR problem only:
ART: a hand on the wrong side (a right hand on a left arm), two right or two left hands on one person, extra/missing/fused fingers you can clearly count, extra or missing limbs;
an impossible or precarious pose or physics (sitting balanced on top of a thin railing, floating, a body passing through an object);
a character drawn wrong for who they are (see WHO), the same character twice in a panel, a character looking away from whom they are clearly talking to.
STAGING: a speaker facing away from the person they talk to; a character looking at someone awkwardly or at the wrong thing; an object a character looks at (photo, screen, paper) facing the reader instead of the character; a body part placed awkwardly by another character's face; two characters who should face each other not doing so; a sudden change of lighting, place or mood between adjacent panels of one continuous moment; a character walking away from someone they are with when the script has them together.
LETTERING: every balloon's tail must point at the character who SPEAKS that line per the SCRIPT (use WHO to identify them); flag every tail on the wrong person;
any text not in the script (invented captions, titles, place names); any script line missing; any misspelling; ANY balloon or caption covering any part of a face.
Answer JSON only: {"art": [{"panel": n, "what": "..."}], "lettering": [{"panel": n, "what": "...", "line": "exact line", "should_point_to": "NAME"}]}"""
def url(b): return "data:image/png;base64,"+base64.b64encode(b).decode()
def qa(n, lines):
    who="\n".join(v for k,v in WHO.items() if k in lines)
    content=[{"type":"text","text":QA+"\n\nWHO:\n"+who+"\n\nSCRIPT (speaker: line):\n"+lines},{"type":"text","text":"THE LETTERED PAGE:"},
             {"type":"image_url","image_url":{"url":url((R/"lettered-model"/f"p{n:02d}.png").read_bytes())}}]
    text,cost=artcheck._ask(content,key,artcheck.MODEL); a=artcheck._json(text) or {}
    return a.get("art") or [], a.get("lettering") or [], cost or 0
def lines_of(spec):
    return "\n".join(f'- Panel {i["panel"]}, {i["type"]}'+(f' (spoken by {i["speaker"]})' if i.get("speaker") else "")+f': "{i["text"]}"' for i in spec.get("items",[]) if i.get("text"))
def letter(n, spec, fixes=""):
    lines=lines_of(spec); who="\n".join(v for k,v in WHO.items() if k in lines)
    LP=("Letter this comic page. The first attached image is the finished art: keep every line of it EXACTLY the same. Add only the lettering below, designed into the panels "
        "like the attached lettering reference: small, wide, clean white speech balloons with short tails and thin outlines, in calm space beside the speaker, never over a face or hand; "
        "captions as small cream boxes in panel corners; place-and-time captions as small yellow boxes top-left; sound effects as warm hand-lettered caps by their source. "
        "EVERY TAIL POINTS AT THE CHARACTER WHO SPEAKS THAT LINE - identify them by WHO below. Use exactly these words, spelled and punctuated exactly, in UPPERCASE comic lettering. ADD NO OTHER TEXT.\n\nWHO:\n"+who+"\n\nLINES:\n"+lines+fixes)
    refs=[("the finished art: keep it exactly",R/"art"/f"p{n:02d}.png"),("lettering reference",C/"style/lettering-reference.png")]
    art,rep,cost=artcheck.draw_checked(lambda t,r: render.generate(render.MODELS[TAG],t,r,key),LP,refs,key,script=lines,lettered=True)
    (R/"lettered-model"/f"p{n:02d}.png").write_bytes(art); return cost
def redraw(n, spec, problems):
    sys.argv=["x"]; os.environ["PAGES"]=str(n)
    import importlib.util
    note=("THE LAST DRAWING OF THIS PAGE HAD THESE MISTAKES - draw it fresh and fix them, keeping everything else:\n"+"\n".join(f"- panel {p.get('panel')}: {p.get('what')}" for p in problems)
          +"\nEvery person has one left hand on the left arm and one right hand on the right arm, five fingers each. Nobody sits balanced on a railing: they sit on solid ledges, steps or crates, or lean on the rail.")
    ctx={**prompts.context(SLUG),"slug":SLUG,"lettering":"layer"}
    refs=render.references(SLUG,TAG,spec,ctx)+[("the previous drawing of this page: keep its composition except the mistakes",R/"art"/f"p{n:02d}.png")]
    if n<=4:
        refs.append(("ALEX'S DAUGHTER: exactly this lock",C/"style/locks/alex-daughter-sunburst/lock.png")); refs.append(("ALEX at 45",C/"style/locks/alex-2070-sunburst/lock.png"))
    if n>=11: refs.append(("Adrian's watch",C/"style/props/adrian-watch.png"))
    if n==6: refs.append(("the Keel pump",C/"style/props/pump-repair.png"))
    STYLE=("ART STYLE: inked graphic-novel realism exactly like the character locks and plate. Draw NO lettering; leave calm space for balloons and leave signs and screens blank.\n\n")
    art,rep,cost=artcheck.draw_checked(lambda t,r: render.generate(render.MODELS[TAG],t,r,key),STYLE+note+"\n\n"+render.prompt_for(spec,ctx,refs),refs,key,lettered=False)
    (R/"art"/f"p{n:02d}.png").write_bytes(art); return cost
def run_page(n):
    spec=specs[n]; total=0; log=[]
    for rnd in range(3):
        lines=lines_of(spec)
        art_p, let_p, c = qa(n, lines); total+=c
        log.append((len(art_p),len(let_p)))
        if not art_p and not let_p: break
        if rnd==2: break
        if art_p:
            total+=redraw(n,spec,art_p)
            total+=letter(n,spec)
        else:
            fixes="\n\nFIX THESE MISTAKES FROM THE LAST LETTERING:\n"+"\n".join(f"- panel {p.get('panel')}: {p.get('what')}"+(f" - the line \"{p.get('line')}\" is spoken by {p.get('should_point_to')}: its tail must point at them" if p.get('should_point_to') else "") for p in let_p)
            total+=letter(n,spec,fixes)
    usage.ledger(SLUG,"renderer","qa",artcheck.MODEL,total,None,page=n)
    print(n, round(total,3), log, [p.get("what","")[:70] for p in (art_p+let_p)][:3], flush=True)

for n in [int(x) for x in os.environ["PAGES"].split(",") if x]:
    for attempt in range(3):
        try: run_page(n); break
        except Exception as e:
            print(n, "ERROR", type(e).__name__, str(e)[:80], flush=True); time.sleep(20)
