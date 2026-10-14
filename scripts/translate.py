#!/usr/bin/env python3
"""translate.py - letter the drawn book in another language, offline, at no cost.

    python3 scripts/translate.py export prosperity lines.csv
    python3 scripts/translate.py apply prosperity lines-es.csv ~/Desktop/prosperity-es

export writes every word on the pages - balloons, captions, sound effects - from the production
desk's layouts.md to a spreadsheet, one line per row, with an empty "translation" column. Fill
that column by hand, with a translator, or with any tool you like.

apply draws the lettering layer again with the translated lines over the art already drawn
(renders/<model>/art) and writes one lettered PNG per page to the folder you name. A row left
blank keeps the original line. Nothing in the campaign changes: layouts.md, the art and the
English lettered pages stay as they are.

No model is called and nothing leaves the machine. Run it with the room's Python (it needs the
same cairo and Pillow the renderer uses), or inside the container:

    docker compose exec app python scripts/translate.py apply prosperity /app/lines-es.csv /app/out-es
"""
import argparse
import copy
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import prompts, render  # noqa: E402

FIELDS = ["page", "panel", "item", "type", "speaker", "text", "translation"]


def export(slug, out):
    rows = 0
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        for spec in render.book(slug):
            for i, item in enumerate(spec.get("items") or []):
                if not str(item.get("text", "")).strip():
                    continue
                w.writerow({"page": spec["page"], "panel": item.get("panel", ""), "item": i,
                            "type": item.get("type", ""), "speaker": item.get("speaker", ""),
                            "text": item["text"], "translation": ""})
                rows += 1
    print(f"{rows} lines from {slug} -> {out}")


def apply(slug, sheet, out, tag):
    lines = {}
    with open(sheet, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if (r.get("translation") or "").strip():
                lines[(int(r["page"]), int(r["item"]))] = r["translation"].strip()
    art_dir = render.folder(slug, tag, "art")
    out = Path(out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    ctx = prompts.context(slug)
    done = skipped = used = 0
    for spec in render.book(slug):
        art = art_dir / f"p{spec['page']:02d}.png"
        if not art.is_file():
            skipped += 1
            continue
        spec = copy.deepcopy(spec)
        for i, item in enumerate(spec.get("items") or []):
            if (spec["page"], i) in lines:
                item["text"] = lines[(spec["page"], i)]
                used += 1
        (out / f"p{spec['page']:02d}.png").write_bytes(render.letter(art.read_bytes(), spec, ctx))
        done += 1
    print(f"{done} pages lettered with {used} translated lines -> {out}"
          + (f" ({skipped} pages have no art yet)" if skipped else ""))
    stale = len(lines) - used
    if stale:
        print(f"{stale} translated lines matched no item: the layouts changed since the export - export again")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export", help="write every line on the pages to a CSV")
    e.add_argument("slug"); e.add_argument("csv")
    a = sub.add_parser("apply", help="letter the drawn art with the CSV's translations")
    a.add_argument("slug"); a.add_argument("csv"); a.add_argument("out")
    a.add_argument("--model", default="sunburst", help="whose art to letter (renders/<model>/art)")
    args = p.parse_args()
    if args.cmd == "export":
        export(args.slug, args.csv)
    else:
        apply(args.slug, args.csv, args.out, args.model)


if __name__ == "__main__":
    main()
