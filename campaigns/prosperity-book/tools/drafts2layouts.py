"""Bob's drafts -> layouts.md, deterministically: one layout page per draft page, one panel per P-label,
every dialogue line / caption / screen / SFX as a lettering item, word for word."""
import re, json, sys
from pathlib import Path
C = Path(__file__).resolve().parents[1]
FILES = ["00-prologue.md", "01-chapter-01.md", "02-chapter-02.md", "03-chapter-03.md"]
if len(sys.argv) > 2: FILES = sys.argv[2].split(",")
OUT = Path(sys.argv[1])
START = int(sys.argv[3]) if len(sys.argv) > 3 else 1
DIA = re.compile(r"^([A-Z][A-Z0-9 \-'’.]+?)\s*(\*?\(([^)]*)\)\*?)?\s*:\s*(.+)$")
TAG = re.compile(r"^\*([^*]+?):\*\s*(.*)$")          # *Caption:* text, *Screen:* text, *SFX:* text
SCREENISH = ("screen", "wristband", "display", "readout", "gauge", "scanner", "terminal", "note", "band", "message",
             "cost sheet", "countdown", "ad slogan", "screen text", "reply", "screen (flashing briefly)")
PLACE = re.compile(r"^[A-Z0-9 ,.'’—\-…]+$")
def kind_of(tag, text):
    t = tag.lower()
    if t.startswith("sfx"): return "sfx"
    if t.startswith("lettering"): return "caption"
    if t.startswith("caption"):
        if "older alex" in t: return "caption"
        return "location" if PLACE.match(text) and len(text) < 48 else "caption"
    if any(t.startswith(s) for s in SCREENISH): return "screen"
    return "caption"
def shot(label):
    m = re.search(r"\(([^)]*)\)", label); return (m.group(1) if m else "").lower()
pages = []
for f in FILES:
    t = re.sub(r"<!--.*?-->", "", (C / "drafts" / f).read_text(), flags=re.S)
    for block in re.split(r"(?m)^## (?:PAGE|Page) ", t)[1:]:
        head, _, body = block.partition("\n")
        title = re.sub(r"^[^:–\-]*[:–\-]\s*", "", head).strip()
        parts = re.split(r"(?m)^(?=\*\*(?:P\d+|Panel \d+|Hook inset|Image|Captions)\b)", body)
        pre, chunks = parts[0], parts[1:]
        if not chunks: chunks = [body]
        panels, items, pending_screen = [], [], None
        cmap = {}
        for ci, ch in enumerate(chunks, 1):
            lines = [l.strip() for l in ch.strip().splitlines() if l.strip()]
            label = re.sub(r"\*", "", lines[0]) if lines else ""
            desc = []
            # a label line may carry its description inline: "**P1: Click (small).** Close on ..."
            m = re.match(r"^\*\*([^*]+)\*\*\s*(.*)$", lines[0]) if lines else None
            if m and m.group(2): desc.append(m.group(2))
            for l in lines[1:]:
                l2 = l.rstrip()
                tm = TAG.match(l2); dm = DIA.match(re.sub(r"\*", "", l2)) if not l2.startswith("*") else None
                if l2.startswith("*Image:*"):
                    desc.append(re.sub(r"^\*Image:\*\s*", "", l2)); pending_screen = None
                elif tm:
                    tag, txt = tm.group(1).strip(), re.sub(r"\*", "", tm.group(2)).strip()
                    k = kind_of(tag, txt)
                    if not txt:   # "*Screen text:*" then plain lines follow
                        items.append({"panel": ci, "type": k, "text": ""}); pending_screen = items[-1]
                    else:
                        items.append({"panel": ci, "type": k, "text": txt}); pending_screen = None
                elif dm:
                    spk, mod, txt = dm.group(1).strip(), (dm.group(3) or "").lower(), dm.group(4).strip()
                    k = "whisper" if any(w in mod for w in ("whisper", "quiet", "under his breath", "small", "almost to herself")) else "balloon"
                    if "shout" in mod: k = "shout"
                    items.append({"panel": ci, "type": k, "speaker": spk, "text": re.sub(r"\*", "", txt)}); pending_screen = None
                elif re.match(r"^\*?\(.*\)\*?$", l2):
                    desc.append(re.sub(r"[*()]", "", l2))
                elif pending_screen is not None and re.sub(r"[*\\]", "", l2).strip():
                    pending_screen["text"] = (pending_screen["text"] + " / " if pending_screen["text"] else "") + re.sub(r"[*\\]", "", l2).strip()
                elif l2.startswith("* ") or l2.startswith("- "):
                    li = re.sub(r"^[*\-]\s*", "", l2); tm2 = re.match(r"^([^:]+):\s*(.+)$", re.sub(r"\*", "", li))
                    if tm2 and label.lower().startswith("captions"):
                        items.append({"panel": max(1, ci - 1), "type": "location" if "date" in tm2.group(1).lower() or "label" in tm2.group(1).lower() else "caption", "text": tm2.group(2).strip()})
                    else: desc.append(re.sub(r"\*", "", li))
                else:
                    if "display" in l2.lower() and "banner" in l2.lower():
                        items.append({"panel": ci, "type": "screen", "text": re.sub(r"[*]", "", l2.split("reading", 1)[-1]).strip()}); pending_screen = items[-1]
                    else: desc.append(re.sub(r"\*", "", l2))
            if label.lower().startswith("captions"): continue
            if not desc and not any(i["panel"] == ci for i in items): continue
            panels.append({"label": label, "description": " ".join(desc).strip(), "shot": shot(label)}); cmap[ci] = len(panels)
        if not panels: panels = [{"label": "", "description": re.sub(r"\*", "", pre).strip(), "shot": "splash"}]
        if pre.strip() and panels and len(chunks) > 1 and not pre.strip().startswith("*"):
            panels[0]["description"] = re.sub(r"\*", "", pre.strip()) + " " + panels[0]["description"]
        # tiers: dominant/wide/splash panels get their own tier; others pair up
        tiers, row = [], []
        for p in panels:
            big = any(w in p["shot"] for w in ("dominant", "splash", "establishing", "full")) or len(panels) <= 2
            wide = "wide" in p["shot"] or "strip" in p["shot"]
            if big or wide:
                if row: tiers.append({"h": 2, "panels": row}); row = []
                tiers.append({"h": 3 if big else 2, "panels": [p]})
            else:
                row.append(p)
                if len(row) == 2: tiers.append({"h": 2, "panels": row}); row = []
        if row: tiers.append({"h": 2, "panels": row})
        renum = {}; k = 0
        for ti in tiers:
            for p in ti["panels"]:
                k += 1; renum[id(p)] = k
                p.update({"w": 1, "angle": "eye", "horizon": 45})
        order = [id(p) for p in panels]
        for it in items:
            if 1 <= it["panel"] <= len(chunks):
                pass
        for it in items:
            c = it["panel"]
            while c > 0 and c not in cmap: c -= 1
            it["panel"] = cmap.get(c, 1)
        pages.append({"title": title, "tiers": tiers, "items": [i for i in items if i.get("text")], "nchunks": len(chunks)})
out = ["# Prosperity — Layouts (from Bob's drafts, word for word)\n"]
for n, pg in enumerate(pages, START):
    # items reference chunk numbers; map chunk order to panel order (panels kept in chunk order)
    spec = {"page": n, "side": "right" if n % 2 else "left", "tiers": pg["tiers"], "items": pg["items"]}
    out.append(f"## Page {n} — {pg['title']}\n\n```layout\n{json.dumps(spec, ensure_ascii=False)}\n```\n")
OUT.write_text("\n".join(out))
print(len(pages), "pages")
