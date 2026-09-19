"""Rebuild the standalone character references in references/ from every document in the room.

    python scripts/gather_character.py            # all of them
    python scripts/gather_character.py ADA        # one

Each file gathers, in this order: the "at a glance" table (authored by hand in
scripts/character_glance.json — edit it there, not in the generated file), the character's
visual lock from the newest project bible, their canon sheet from the campaign bible verbatim,
the bible's relationship sections, every distinct line the scripts have given them, and a list
of where it all came from.

Sources walked: references/, agents/, morgue/, and every project's files and rounds — the
container's copy when the app is running, otherwise projects/ on disk. A passage repeated across
twenty round snapshots is written once.

These files are gathered, not authored: new canon belongs in the bible, and a rerun overwrites.
"""
import collections
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app.search import chunks                                       # noqa: E402

BIBLE = ROOT / "references" / "EVOKE_PROSPERITY_BIBLE.md"
GLANCE = ROOT / "scripts" / "character_glance.json"
NAMES = {"ALEX PHANTUM": "ALEX", "ADA VEYRA": "ADA", "BI11BOT": "BI11BOT", "MERA VALE": "MERA",
         "ADRIAN PHANTUM": "ADRIAN", "LEONA VEYRA": "LEONA"}


def projects_dir():
    """The container's project data when the app is up, else what is on disk."""
    tmp = pathlib.Path("/tmp/projects-snapshot")
    done = subprocess.run(["docker", "cp", "writers-room-app-1:/app/projects", str(tmp)],
                          capture_output=True)
    return tmp if done.returncode == 0 else ROOT / "projects"


def bible_parts():
    """({character: sheet}, [(pair title, body)]) from the campaign bible."""
    lines = BIBLE.read_text().split("\n")
    heads = [(i, re.sub(r"[*\\#]", "", l).strip()) for i, l in enumerate(lines)
             if re.match(r"^# \*\*", l)]
    sheets, pairs = collections.defaultdict(list), []
    for j, (i, title) in enumerate(heads):
        end = heads[j + 1][0] if j + 1 < len(heads) else len(lines)
        body = "\n".join(lines[i:end]).strip()
        name = title.split(".", 1)[1].strip() if re.match(r"^\d+\.", title) else title
        if name in NAMES:
            sheets[NAMES[name]].append(body)
        elif "↔" in name:
            pairs.append((name, body))
    return {k: "\n\n".join(v) for k, v in sheets.items()}, pairs


def passages(aliases, sources):
    """Distinct passages that mention the character, with the file each came from."""
    seen, out = set(), []
    for path in sources:
        try:
            text = path.read_text(errors="replace")
        except Exception:
            continue
        for part in chunks(text, min_chars=200, max_chars=2500):
            body = part["text"].strip()
            if len(body) < 60 or not any(re.search(rf"\b{re.escape(a)}\b", body) for a in aliases):
                continue
            key = re.sub(r"\s+", " ", body.lower())
            if key not in seen:
                seen.add(key)
                out.append({"file": str(path), "text": body})
    return out


def project_entry(aliases, pdir):
    """Their entry in each project bible, newest first — the visual lock artists are given."""
    out = []
    for p in sorted(pdir.rglob("*bible.md"), key=lambda x: x.stat().st_mtime, reverse=True):
        for block in re.split(r"\n(?=#{2,4}\s)", p.read_text(errors="replace")):
            head = block.split("\n", 1)[0]
            if any(re.search(rf"\b{re.escape(a)}\b", head, re.I) for a in aliases):
                out.append((p.parent.name, block.strip()))
                break
    return out


def spoken(aliases, rows, limit=24):
    """Distinct lines the scripts give them, and where each was written."""
    speaker = "|".join(re.escape(a.upper()) for a in aliases)
    # a speaker cue only: the name, an optional parenthetical, a colon. Not "ALEX ARC:", not
    # "ALEX and Ada freeze as the drone says:", and not the bible's "Bi11bot:\n\ndry redirection."
    # — those are description and craft notes, not lines anyone says.
    cue = rf"^\**({speaker})\**\s*(?:\([^)]{{0,40}}\))?\s*:\**\s*(.+)$"
    seen, out = set(), []
    for row in rows:
        for line in row["text"].split("\n"):
            m = re.match(cue, line.strip(), re.I)
            if not m:
                continue
            said = re.sub(r"\*+", "", m.group(m.lastindex))
            said = re.sub(r"&nbsp;|\s+", " ", said).strip()
            key = re.sub(r"\W+", " ", said.lower())[:60]
            arc_note = "→" in said or "->" in said          # "Escape → Plan → Discovery": an arc, not a line
            empty = not re.search(r"[A-Za-z]{2}", said.replace("&nbsp;", ""))
            label = len(said.split()) < 3 and said.endswith(".") and said.islower()
            if len(said) > 3 and not arc_note and not empty and not label and key not in seen:
                seen.add(key)
                out.append((said, row["file"].split("/")[-1]))
    return out[:limit]


def render(key, g, sheet, pairs, rows, pdir):
    name = g["title"].split()[0]
    entries = project_entry(g["aliases"], pdir)
    lines = spoken(g["aliases"], rows)
    files = collections.Counter(r["file"] for r in rows).most_common()
    out = [f"""---
name: {g['file'].removesuffix('.md').lower().replace('_', '-')}
description: {g['description']}
---

# {g['title']}

*Standalone character reference, gathered from the campaign bible, the chapter canon, every
project bible, the script drafts, the rounds and the morgue. The canon sheet below is the
campaign bible's own words; everything after it says where it came from.*

## At a glance

| | |
|---|---|
| **In one line** | {g['line']} |
| **Age** | {g['age']} |
| **Wants** | {g['want']} |
| **Needs** | {g['need']} |
| **Wound** | {g['wound']} |
| **Tell** | {g['tell']} |
| **Voice** | {g['voice']} |
| **Palette** | {g['palette']} |
"""]
    if entries:
        newest, block = entries[0]
        out.append(f"\n## Visual lock — what an artist is given\n\nFrom the working bible in "
                   f"**{newest}**, pasted verbatim into every page prompt this character appears "
                   f"on:\n\n{block}\n")
        if len(entries) > 1:
            out.append(f"\n*{len(entries) - 1} earlier versions of this entry exist in other "
                       "project bibles; they agree on the silhouette and differ in wording.*\n")
    if sheet:
        out.append("\n## Canon sheet\n\nFrom `EVOKE_PROSPERITY_BIBLE.md`, verbatim.\n\n"
                   + re.sub(r"^# ", "### ", sheet, flags=re.M).replace("\n## ", "\n#### ") + "\n")
    else:
        out.append("\n## Canon sheet\n\n" + g.get("no_canon", "**None.** No entry in the campaign "
                   "bible: the room invented this character while writing.") + "\n")
    mine = [(t, b) for t, b in pairs if re.search(rf"\b{key.split('_')[0]}\b", t, re.I)]
    if mine:
        out.append("\n## Relationships, from the bible\n")
        for _title, body in mine:
            out.append("\n" + re.sub(r"^# ", "### ", body, flags=re.M).replace("\n## ", "\n#### "))
    if lines:
        out.append(f"\n\n## Lines the scripts have given {name}\n\nDeduplicated across every draft "
                   "and round; the source is the file it was written in.\n")
        out += [f"\n- “{said}” — *{src}*" for said, src in lines]
    out.append(f"\n\n## Where this came from\n\n{len(files)} files mention {name}. The ones that "
               "say most about them:\n")
    out += [f"\n- `{p.replace(str(pdir), 'projects')}` — {n} passage{'s' if n > 1 else ''}"
            for p, n in files[:14]]
    out.append("\n\n*Gathered by `scripts/gather_character.py`; rerun it after a round. New canon "
               "belongs in the bible, not here — a rerun overwrites this file.*\n")
    return "\n".join(out)


def main(only=None):
    glance = json.loads(GLANCE.read_text())
    sheets, pairs = bible_parts()
    pdir = projects_dir()
    mine = {g["file"] for g in glance.values()}       # never read what this script wrote
    sources = [p for p in ROOT.rglob("*.md")
               if not any(x in {".git", ".venv", "output", "projects"} for x in p.parts)
               and p.name not in mine]
    sources += list(pdir.rglob("*.md"))
    for key, g in glance.items():
        if only and key != only.upper():
            continue
        rows = passages(g["aliases"], sources)
        (ROOT / "references" / g["file"]).write_text(render(key, g, sheets.get(key, ""), pairs,
                                                            rows, pdir))
        print(f"{g['file']:22} {len(rows):4} passages · {len({r['file'] for r in rows})} files")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
