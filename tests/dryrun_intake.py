"""Build every intake call and stop before the model. Nothing is written to the campaign.

Usage: dryrun_intake.py <slug> <outdir> [synthesis|revision]
"""
import sys, pathlib

from app import intake, openitems, phases, projects, review, notes as notes_mod
from app.agents import load_roles

SLUG = sys.argv[1] if len(sys.argv) > 1 else "prosperity"
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "dryrun-out")
MODE = sys.argv[3] if len(sys.argv) > 3 else None
OUT.mkdir(parents=True, exist_ok=True)

st = review.settings(SLUG)
phase = phases.current(SLUG)
parts = [f"The room is in {phase['title'].lower()}: {phase['does']}", phases.note(SLUG, phase)]
if st["pages"]:
    parts.append(f"The book is exactly {st['pages']} pages: pages 1-{st['pages']}, no more, no fewer.")
jotted = [n for n in notes_mod._all(SLUG) if not n.get("used_in")]
if jotted:
    parts.append("\n\n".join(n.get("text", "") for n in jotted))
note = "\n\n".join(p for p in parts if p)

class DryVersion:
    slug = SLUG; id = "dryrun"; prefix = f"{SLUG}-dryrun-"; meta = {"run_id": "dryrun"}
    def next_call_number(self): return 0

role = [r for r in load_roles() if r.id == "script_coordinator"][0]
a = intake.Intake(role, DryVersion(), lambda *t, **d: None, mode=MODE)
work = intake.pending(SLUG)
items_now = projects.read_artifact(SLUG, intake.ITEMS) or "(open-items.md not written yet)"

calls = []
if a.mode == intake.SYNTHESIS:
    shared = a.payload(note)
    for i, n in enumerate(intake.CORE):
        calls.append((f"1{chr(ord('A')+i)}", intake.SYNTHESIS, n, a.synthesis_message(n, shared)))
    calls.append(("2", intake.OPEN_ITEMS, intake.ITEMS, a.open_items_message(a.desk(), note)))
    calls.append(("3", intake.OPTIONS, intake.ITEMS, a.options_message(items_now, note)))
else:
    shared = a.revision_payload(work, note)
    for i, n in enumerate(intake.CORE + (intake.ITEMS,)):
        calls.append((f"4{chr(ord('A')+i)}", intake.REVISION, n, a.revision_message(n, shared)))
    calls.append(("5", intake.FACTS_PASS, intake.FACTS, a.facts_message(note)))

lines = [f"campaign   {SLUG}", f"phase      {phase['id']}",
         f"role       {role.id} (pipeline: {role.pipeline})",
         f"mode       {a.mode}" + ("  (given)" if MODE else "  (chosen)"),
         f"model      {a.cfg.model}  temp={a.cfg.temperature}  max_tokens={a.cfg.max_tokens}",
         f"references in synthesis: {a.use_references_in_synthesis}",
         f"tools      none - the room writes the files", ""]
total = 0
for label, pass_name, dest, user in calls:
    system = a.system_prompt(pass_name)
    (OUT / f"pass-{label}-system.txt").write_text(system)
    (OUT / f"pass-{label}-task.txt").write_text(user)
    n = len(system) + len(user); total += n
    par = "  (parallel)" if label[0] in "14" and label != "4D" else ""
    lines += [f"pass {label}: {pass_name} -> {dest}{par}",
              f"  guides    {', '.join(l.split('/')[-1] for l, _ in a.guides(pass_name))}"
              + (f" + {intake.DEST_GUIDE[dest]}" if dest in intake.DEST_GUIDE else ""),
              f"  system    {len(system):>9,}",
              f"  task      {len(user):>9,}",
              f"  total     {n:>9,} chars  (~{n // 4:,} tokens)"
              + ("  OVER SOFT CEILING" if n > intake.SOFT_INPUT_CHARS else ""), ""]
lines.append(f"whole round: {total:,} chars in  (~{total // 4:,} tokens), {len(calls)} calls")
lines.append(f"soft input ceiling {intake.SOFT_INPUT_CHARS:,} chars · output budget "
             f"{intake.OUTPUT_TOKENS:,} tokens per call")
if a.mode == intake.SYNTHESIS:
    src = a.sources()
    lines.append(f"snapshot {a.snapshot(src)} over {len(src)} source files; the three synthesis "
                 f"calls share a {len(a.payload(note)):,}-char prefix")

by_kind = {}
for n, p in projects.reference_files(SLUG).items():
    by_kind.setdefault(projects.reference_kind(p), []).append((n, p.stat().st_size))
lines += ["", "material by kind"]
for kind in sorted(by_kind):
    files = sorted(by_kind[kind])
    lines.append(f"  {kind:<11} {len(files):>2} files, {sum(s for _, s in files) // 1000:>4} KB")
    for n, s in files:
        lines.append(f"      {s // 1000 or 1:>4} KB  {n}")

guard = intake.preservation(a.guarded(), a.desk())
lines += ["", "preservation guard (input/ + rules/ vs the three files on the desk now;",
          "                    research is a creative input and is never measured)"]
lines.append(f"  {guard}" if guard else "  not engaged: too little source material")
if guard:
    need = int(guard["source_chars"] * intake.MIN_MASS)
    lines.append(f"  floor {intake.MIN_MASS:.0%} -> the three files need {need:,} chars together")

state = openitems.state(SLUG)
lines += ["", f"held from pass 1: {a.reserved()}",
          f"open items: {state['answered']} answered, {state['deferred']} deferred, "
          f"{state['unresolved']} unresolved",
          f"notes: {len(intake.notes(SLUG)['general'])} general, "
          f"{len(intake.notes(SLUG)['items'])} on items",
          "", "NOT run: any model call, validation, any file write."]
summary = "\n".join(lines)
(OUT / "summary.txt").write_text(summary)
print(summary)
print(f"\nwritten to {OUT.resolve()}/")
