"""Model-letter existing art again (keep art). PAGES env, LAYOUTS env."""
import sys, os, re, json, time
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[3]))
from app import artcheck, projects, render, usage
SLUG="prosperity-book"; TAG="sunburst"; key=render.api_key(); C=projects.campaign_dir(SLUG); R=C/"renders"/TAG
specs={d["page"]:d for d in (json.loads(m.group(1)) for m in re.finditer(r"```layout\n(.*?)\n```",open(os.environ["LAYOUTS"]).read(),re.S))}
LNOTES=json.loads(os.environ.get("LNOTES","{}"))
for n in [int(x) for x in os.environ["PAGES"].split(",")]:
    spec=specs[n]
    lines="\n".join(f'- Panel {i["panel"]}, {i["type"]}'+(f' ({i["speaker"]})' if i.get("speaker") else "")+f': "{i["text"]}"' for i in spec.get("items",[]) if i.get("text"))
    LP=("Letter this comic page. The first attached image is the finished art: keep every line of it EXACTLY the same, change nothing in the drawing. "
        "Add only the lettering below, designed into the panels like the attached lettering reference: small, wide, clean white speech balloons with short tails and thin outlines, "
        "in calm space beside the speaker, tail pointing at the speaker's mouth, never over a face, hand or the key object; captions as small cream boxes with dark text in panel corners; "
        "place-and-time captions as small yellow boxes top-left. Use exactly these words, spelled and punctuated exactly, uppercase comic lettering. "
        "ADD NO OTHER TEXT: no captions, titles, place names, dates or words that are not in this list.\n"+lines+("\n\nPLACEMENT: "+LNOTES[str(n)] if str(n) in LNOTES else ""))
    refs=[("the finished art: keep it exactly, add only the lettering",R/"art"/f"p{n:02d}.png"),("lettering reference",C/"style/lettering-reference.png")]
    t0=time.time()
    art,rep,cost=artcheck.draw_checked(lambda t,r: render.generate(render.MODELS[TAG],t,r,key),LP,refs,key,script=lines,lettered=True)
    (R/"lettered-model"/f"p{n:02d}.png").write_bytes(art)
    usage.ledger(SLUG,"renderer","letter",render.MODELS[TAG],cost,time.time()-t0,page=n,tries=len(rep["attempts"]),check_pass=rep["pass"])
    print(n,round(cost,3),rep["pass"],[p.get("what","")[:90] for p in rep["problems"]][:3],flush=True)
