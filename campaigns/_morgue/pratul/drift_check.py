#!/usr/bin/env python3
"""
drift_check.py  ·  script-authority checker for image generation

PRINCIPLE
    The screenplay is the only source of truth. Anything an image model
    renders that is not in the screenplay is drift. Anything in the
    screenplay that the model did not render is drift. Anything reworded
    is drift. The model's own ideas never win.

This tool knows nothing about any particular story. It reads your
screenplay file, reads what the model says it produced, and diffs them.
All project-specific rules (forbidden phrases, fixed facts, label styles)
live in an optional rules file you supply, not in this code.

COMMANDS
    build     Parse a screenplay markdown file into per-page specs (JSON).
    preflight Check the model's pre-render restatement against the spec.
    render    Check the model's post-render transcription against the spec.
    milestone Summarise a batch of render checks and apply the stop rule.

EXAMPLES
    python drift_check.py build     screenplay.md  -o specs.json
    python drift_check.py preflight specs.json 6 preflight.json  [-r rules.json]
    python drift_check.py render    specs.json 6 render.json -s results/p06.json
    python drift_check.py milestone "results/*.json"

EXIT CODES
    0 PASS · 1 REVIEW or REGEN · 2 usage / parse error

REQUIRES  Python 3.8+ ; PyYAML only if you use a .yaml rules file.
"""

import argparse
import difflib
import glob
import json
import re
import sys
import unicodedata
from pathlib import Path

# ------------------------------------------------------------------ codes

DRIFT = {
    "D1": "OMISSION",           # script line missing from image
    "D2": "NON_SCRIPT_TEXT",    # labels, page numbers, nameplates, notation
    "D3": "ADDITION",           # line in image that is not in script
    "D4": "CAPTION_CREEP",      # caption where script has none
    "D5": "SPEAKER_SWAP",       # right words, wrong character
    "D6": "STRUCTURE",          # panel count differs
    "D7": "MODIFICATION",       # script line present but reworded
    "D8": "BEAT_SUBSTITUTION",  # page does not do what script says it does
    "D9": "RULE_BREAK",         # violates a rule in the user's rules file
}
ALWAYS_REGEN = {"D2", "D4", "D5", "D7", "D8", "D9"}

DEFAULT_RULES = {
    "modification_threshold": 0.55,
    "non_script_patterns": [
        r"^page\s*\d+\b", r"^chapter\b", r"^sheet\b", r"^scene\b",
        r"^panel\s*\d+", r"^\d+(\.\d+)+$", r"^source\b", r"\[[A-Z]+\]",
    ],
    "forbidden_patterns": [],
    "extra_load_bearing": [],
    "stop_after_consecutive_regen": 2,
}


# ------------------------------------------------------------------ text utils

def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    for a, b in (("\u2018", "'"), ("\u2019", "'"), ("\u201c", '"'),
                 ("\u201d", '"'), ("\u2014", "-"), ("\u2013", "-"),
                 ("\u2026", "...")):
        s = s.replace(a, b)
    s = re.sub(r"[*_`]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def loose(s):
    return re.sub(r"[^a-z0-9 ]", "", norm(s).lower())


def sim(a, b):
    return difflib.SequenceMatcher(None, loose(a), loose(b)).ratio()


# ------------------------------------------------------------------ rules

def load_rules(path):
    rules = {k: (list(v) if isinstance(v, list) else v)
             for k, v in DEFAULT_RULES.items()}
    if not path:
        return rules
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if p.suffix in (".yaml", ".yml"):
        try:
            import yaml
        except ImportError:
            sys.exit("PyYAML required for .yaml rules: pip install pyyaml")
        user = yaml.safe_load(text) or {}
    else:
        user = json.loads(text)
    for k, v in user.items():
        if isinstance(v, list) and isinstance(rules.get(k), list):
            rules[k] = rules[k] + v
        else:
            rules[k] = v
    return rules


# ------------------------------------------------------------------ parser
#
# Reads any screenplay in the common markdown convention:
#
#   ## PAGE 6 — Title        ### Sheet 1.6 — Title
#   **Page function:** ...   **Sheet function:** ...
#   ### P3 — ...             **P3.**            Panel 3
#   **SPEAKER [TAG]:** line  SPEAKER: line       **[CAPTION]:** line
#
# Anything it cannot classify is ignored, never guessed.

PAGE_RE = re.compile(r"^#{1,4}\s*(?:page|sheet)\s+([0-9]+(?:\.[0-9]+)?)\b(.*)$", re.I)
FUNC_RE = re.compile(r"^\*{0,2}(?:page|sheet)\s+function\s*:?\s*\*{0,2}\s*:?\s*(.+)$", re.I)
PANEL_RE = re.compile(r"^(?:#{1,5}\s*)?\*{0,2}(?:P|panel\s*)(\d+)\b(?![^\n]*:\*\*\s)", re.I)
LINE_RE = re.compile(
    r"^\*{0,2}\s*(\[?[A-Za-z0-9][A-Za-z0-9 .'\-]*?\]?)\s*"
    r"(\[[^\]]+\])?\s*(?:,[^:]*?)?\s*:\s*\*{0,2}\s*(.+)$")
CAPTION_TAGS = {"CAPTION", "NARRATION", "NARRATOR", "TEXT BOX", "TEXTBOX"}
NON_SPEAKERS = {"PAGE FUNCTION", "SHEET FUNCTION", "LAYOUT", "SFX", "SIGN",
                "VISUAL", "NOTE", "VALUE", "CAMERA", "RENDERED", "MOTION"}


def parse_screenplay(md_text):
    pages, cur, panel, seq = [], None, None, 0
    for raw in md_text.splitlines():
        line = raw.strip()
        if not line or line[0] in ">|":
            continue

        m = PAGE_RE.match(line)
        if m:
            seq += 1
            cur = {"page": seq, "source_label": m.group(1),
                   "title": norm(m.group(2)).strip("— -"),
                   "function": "", "panel_count": 0, "panels": [],
                   "captions": [], "load_bearing": []}
            pages.append(cur)
            panel = None
            continue
        if cur is None:
            continue

        m = FUNC_RE.match(line)
        if m:
            cur["function"] = norm(m.group(1))
            continue

        m = PANEL_RE.match(line)
        if m:
            pid = int(m.group(1))
            panel = {"id": pid, "dialogue": []}
            cur["panels"].append(panel)
            cur["panel_count"] = max(cur["panel_count"], pid)
            continue

        m = LINE_RE.match(line)
        if m and panel is not None:
            speaker = norm(m.group(1)).strip("[]").upper()
            tag = (m.group(2) or "").strip("[]").split(",")[0].strip().upper()
            text = norm(m.group(3))
            # a real speaker tag is short; long "speakers" are stage directions
            if not text or speaker in NON_SPEAKERS or len(speaker) > 30 \
                    or len(speaker.split()) > 4:
                continue
            if speaker in CAPTION_TAGS or tag in CAPTION_TAGS:
                cur["captions"].append(text)
                continue
            panel["dialogue"].append({"speaker": speaker, "tag": tag, "text": text})
    return pages


def specs_from_file(path):
    p = Path(path)
    if p.suffix == ".json":
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else [data]
    return parse_screenplay(p.read_text(encoding="utf-8"))


def pick(specs, page):
    for s in specs:
        if str(s["page"]) == str(page) or str(s.get("source_label")) == str(page):
            return s
    sys.exit(f"page {page} not found in specs")


def spec_lines(spec):
    return [{"panel": p["id"], "speaker": d["speaker"], "text": d["text"]}
            for p in spec.get("panels", []) for d in p.get("dialogue", [])]


# ------------------------------------------------------------------ report

class Report:
    def __init__(self, page, title=""):
        self.page, self.title, self.items = page, title, []

    def add(self, code, panel=None, expected=None, found=None,
            load_bearing=False, note=""):
        self.items.append(dict(code=code, name=DRIFT[code], panel=panel,
                               expected=expected, found=found,
                               load_bearing=load_bearing, note=note))

    @property
    def verdict(self):
        if not self.items:
            return "PASS"
        if any(i["load_bearing"] or i["code"] in ALWAYS_REGEN for i in self.items):
            return "REGEN"
        return "REVIEW"

    def show(self):
        bar = "=" * 70
        print(bar)
        print(f"PAGE {self.page}" + (f" · {self.title}" if self.title else ""))
        print(f"VERDICT: {self.verdict}    issues: {len(self.items)}")
        print(bar)
        for i in self.items:
            lb = "  [LOAD-BEARING]" if i["load_bearing"] else ""
            pn = i["panel"] if i["panel"] is not None else "-"
            print(f"{i['code']} {i['name']:<18} panel {pn}{lb}")
            if i["expected"] is not None:
                print(f"      script: {i['expected']}")
            if i["found"] is not None:
                print(f"      image:  {i['found']}")
            if i["note"]:
                print(f"      note:   {i['note']}")
        print()

    def to_json(self):
        return {"page": self.page, "verdict": self.verdict, "issues": self.items}


# ------------------------------------------------------------------ diff engine

def diff(script_lines, image_lines, rep, rules, load_bearing):
    """Script is authoritative.
       pass 1  exact match      -> ok, or D5 if the speaker differs
       pass 2  fuzzy pairing    -> D7 script line present but reworded
       pass 3  leftovers        -> D1 script line missing / D3 invented line"""
    thr = rules["modification_threshold"]
    lb = {norm(x) for x in load_bearing}
    S = [dict(x) for x in script_lines]
    I = [dict(x) for x in image_lines]

    for s in S[:]:
        for i in I:
            if norm(s["text"]) == norm(i["text"]):
                if s.get("speaker") and i.get("speaker") and \
                        norm(s["speaker"]).upper() != norm(i["speaker"]).upper():
                    rep.add("D5", s.get("panel"), f"{s['speaker']}: {s['text']}",
                            f"{i['speaker']}: {i['text']}", norm(s["text"]) in lb)
                S.remove(s)
                I.remove(i)
                break

    pairs = sorted(((sim(s["text"], i["text"]), si, ii)
                    for si, s in enumerate(S) for ii, i in enumerate(I)), reverse=True)
    used_s, used_i = set(), set()
    for r, si, ii in pairs:
        if r < thr:
            break
        if si in used_s or ii in used_i:
            continue
        rep.add("D7", S[si].get("panel"), S[si]["text"], I[ii]["text"],
                norm(S[si]["text"]) in lb, f"similarity {r:.2f}")
        used_s.add(si)
        used_i.add(ii)

    for si, s in enumerate(S):
        if si not in used_s:
            rep.add("D1", s.get("panel"), s["text"], None, norm(s["text"]) in lb)
    for ii, i in enumerate(I):
        if ii not in used_i:
            rep.add("D3", i.get("panel"), None, i["text"])


def forbidden_scan(texts, rep, rules):
    for panel, t in texts:
        for pat in rules["forbidden_patterns"]:
            if re.search(pat, t, re.I):
                rep.add("D9", panel, f"must not match /{pat}/", t, True)


def is_non_script(text, kind, rules):
    if kind in ("label", "nameplate", "title", "page_number", "notation"):
        return True
    return any(re.search(p, norm(text), re.I) for p in rules["non_script_patterns"])


def load_bearing_for(spec, rules):
    lb = list(spec.get("load_bearing", [])) + list(rules["extra_load_bearing"])
    return [re.sub(r"^\s*[A-Za-z0-9 ]+:\s*", "", x) for x in lb]


# ------------------------------------------------------------------ commands

def cmd_build(a):
    pages = parse_screenplay(Path(a.screenplay).read_text(encoding="utf-8"))
    if not pages:
        sys.exit("No pages found. Headings must look like '## PAGE 1' or '### Sheet 1.1'.")
    out = json.dumps(pages, indent=2, ensure_ascii=False)
    if a.output:
        Path(a.output).write_text(out, encoding="utf-8")
        print(f"wrote {len(pages)} page specs to {a.output}")
    else:
        print(out)
    for p in pages:
        n = sum(len(x["dialogue"]) for x in p["panels"])
        print(f"  page {p['page']:>3}  [{p['source_label']}]  panels {p['panel_count']:>2}  "
              f"lines {n:>2}  captions {len(p['captions'])}  {p['title']}", file=sys.stderr)
    return 0


def cmd_preflight(a):
    rules = load_rules(a.rules)
    spec = pick(specs_from_file(a.specs), a.page)
    pf = json.loads(Path(a.preflight).read_text(encoding="utf-8"))
    rep = Report(spec["page"], spec.get("title", ""))

    if pf.get("panel_count") != spec["panel_count"]:
        rep.add("D6", None, f"{spec['panel_count']} panels", f"{pf.get('panel_count')} panels")

    if not spec["captions"]:
        for c in pf.get("captions", []) or []:
            rep.add("D4", None, "NO CAPTIONS", c)
    else:
        diff([{"panel": None, "text": c} for c in spec["captions"]],
             [{"panel": None, "text": c} for c in pf.get("captions", []) or []], rep, rules, [])

    diff(spec_lines(spec), pf.get("dialogue", []) or [], rep, rules, load_bearing_for(spec, rules))

    for f in pf.get("fit_flags", []) or []:
        if f.get("applied"):
            rep.add("D7", f.get("panel"), "flag only, text unchanged", "model applied its own change")

    forbidden_scan([(d.get("panel"), d.get("text", "")) for d in pf.get("dialogue", []) or []],
                   rep, rules)
    rep.show()
    if rep.verdict != "PASS":
        print(">>> Do NOT send CONFIRMED. Correct and re-run preflight.")
    return 0 if rep.verdict == "PASS" else 1


def cmd_render(a):
    rules = load_rules(a.rules)
    spec = pick(specs_from_file(a.specs), a.page)
    rr = json.loads(Path(a.render).read_text(encoding="utf-8"))
    rep = Report(spec["page"], spec.get("title", ""))

    if rr.get("panels_rendered") is not None and rr["panels_rendered"] != spec["panel_count"]:
        rep.add("D6", None, f"{spec['panel_count']} panels", f"{rr['panels_rendered']} panels")

    balloons, caps = [], []
    for t in rr.get("text_found", []) or []:
        kind = (t.get("kind") or "").lower()
        txt = t.get("text", "")
        if is_non_script(txt, kind, rules):
            rep.add("D2", t.get("panel"), None, txt)
        elif kind in ("caption", "narration", "text_box"):
            caps.append({"panel": t.get("panel"), "text": txt})
        elif kind == "signage":
            continue
        else:
            balloons.append({"panel": t.get("panel"), "speaker": t.get("speaker_guess"), "text": txt})

    if not spec["captions"]:
        for c in caps:
            rep.add("D4", c["panel"], "NO CAPTIONS", c["text"])
    else:
        diff([{"panel": None, "text": c} for c in spec["captions"]], caps, rep, rules, [])

    diff(spec_lines(spec), balloons, rep, rules, load_bearing_for(spec, rules))

    fa = (rr.get("function_achieved") or "").lower()
    if fa in ("no", "partial"):
        rep.add("D8", None, spec.get("function") or "(see script)",
                rr.get("function_evidence"), True, f"model says: {fa}")

    forbidden_scan([(t.get("panel"), t.get("text", "")) for t in rr.get("text_found", []) or []],
                   rep, rules)
    rep.show()
    if a.save:
        Path(a.save).parent.mkdir(parents=True, exist_ok=True)
        Path(a.save).write_text(json.dumps(rep.to_json(), indent=2), encoding="utf-8")
    if rep.verdict == "REGEN":
        print(">>> Regenerate this page before generating the next one.")
    return 0 if rep.verdict == "PASS" else 1


def cmd_milestone(a):
    rules = load_rules(a.rules)
    files = sorted(f for pat in a.results for f in glob.glob(pat))
    if not files:
        sys.exit("no result files")
    rows = sorted((json.loads(Path(f).read_text(encoding="utf-8")) for f in files),
                  key=lambda r: r["page"])
    counts = {k: 0 for k in DRIFT}
    regen = []
    print("=" * 70)
    print(f"{'PAGE':>5}  VERDICT  ISSUES")
    for r in rows:
        for i in r["issues"]:
            counts[i["code"]] += 1
        if r["verdict"] == "REGEN":
            regen.append(r["page"])
        print(f"{r['page']:>5}  {r['verdict']:<7}  {len(r['issues'])}")
    print("-" * 70)
    for k, v in counts.items():
        if v:
            print(f"  {k} {DRIFT[k]:<18} {v}")
    best = streak = 0
    prev = None
    for p in regen:
        streak = streak + 1 if prev is not None and p == prev + 1 else 1
        best, prev = max(best, streak), p
    limit = rules["stop_after_consecutive_regen"]
    print("-" * 70)
    if best >= limit:
        print(f"STOP RULE: {best} consecutive REGEN pages (limit {limit}).")
        print("Open a NEW session. Do not correct inside the drifted one.")
    else:
        print("Stop rule not triggered.")
    print("Hand-verify 3 random pages; model transcriptions under-report.")
    print("=" * 70)
    return 1 if regen else 0


# ------------------------------------------------------------------ cli

def main():
    ap = argparse.ArgumentParser(description="Script-authority drift checker")
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="screenplay.md -> page specs JSON")
    b.add_argument("screenplay")
    b.add_argument("-o", "--output")

    p = sub.add_parser("preflight")
    p.add_argument("specs", help="screenplay .md or specs .json")
    p.add_argument("page")
    p.add_argument("preflight")
    p.add_argument("-r", "--rules")

    r = sub.add_parser("render")
    r.add_argument("specs")
    r.add_argument("page")
    r.add_argument("render")
    r.add_argument("-r", "--rules")
    r.add_argument("-s", "--save", help="write result JSON for milestone")

    m = sub.add_parser("milestone")
    m.add_argument("results", nargs="+")
    m.add_argument("-r", "--rules")

    a = ap.parse_args()
    sys.exit({"build": cmd_build, "preflight": cmd_preflight,
              "render": cmd_render, "milestone": cmd_milestone}[a.cmd](a))


if __name__ == "__main__":
    main()
