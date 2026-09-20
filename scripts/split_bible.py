"""Split the Evoke Prosperity campaign bible into a general bible and one file per chapter.

    python scripts/split_bible.py [references/sources/EVOKE_PROSPERITY_CAMPAIGN_BIBLE.md]

Writes, next to the other references:

    references/EVOKE_PROSPERITY_BIBLE.md        everything that isn't chapter-specific
    references/EVOKE_PROSPERITY_CHAPTER_<n>.md  per chapter: its row of the six-chapter canon,
                                                its Prosperity Principle, its character
                                                interaction map, its script revision flags

The interaction maps (Part II-B) and revision flags (section 22) move to the chapter
files; the overview tables and the principles list stay in the bible as well.
The source stays in references/sources/, which agents don't read. Rerun after
updating it.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "campaigns" / "prosperity" / "novel" / "drafts" / "v00" / "_rough" / "EVOKE_PROSPERITY_CAMPAIGN_BIBLE.md"
OUT = ROOT / "campaigns" / "prosperity" / "chapters"
BIBLE = "EVOKE_PROSPERITY_BIBLE.md"
CHAPTER = "EVOKE_PROSPERITY_CHAPTER_{n}.md"

HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


def plain(text):
    return re.sub(r"[*\\]", "", text).strip()


def block_end(lines, start, stop):
    """Index where the block starting at `start` ends: the first line after it matching `stop`."""
    for i in range(start + 1, len(lines)):
        if stop(lines[i]):
            return i
    return len(lines)


def trim(chunk):
    while chunk and chunk[-1].strip() in ("", "---"):
        chunk = chunk[:-1]
    while chunk and not chunk[0].strip():
        chunk = chunk[1:]
    return chunk


def top_section(lines, title_re):
    """(start, end) of the level-1 section whose title matches."""
    for i, l in enumerate(lines):
        m = HEADING.match(l)
        if m and len(m.group(1)) == 1 and re.search(title_re, plain(m.group(2)), re.I):
            return i, block_end(lines, i, lambda x: bool(re.match(r"^#\s", x)))
    return None


def subsections(lines, start, end, pattern):
    """{chapter: (start, end)} for "### Chapter N..." headings inside lines[start:end]."""
    found = {}
    marks = [i for i in range(start + 1, end) if re.match(r"^#{2,3}\s", lines[i])]
    for k, i in enumerate(marks):
        m = re.match(pattern, plain(HEADING.match(lines[i]).group(2)), re.I)
        if m:
            nxt = marks[k + 1] if k + 1 < len(marks) else end
            found[int(m.group(1))] = (i, nxt)
    return found


def main(source):
    lines = source.read_text().split("\n")
    chapters = {}          # n -> {"title", "map", "flags", "principle", "canon"}
    remove = []            # (start, end, replacement lines)

    # Part II-B: "CHAPTER N — TITLE" sections (level 1 or 2), each until the next CHAPTER or PART heading
    starts = [(i, HEADING.match(l)) for i, l in enumerate(lines) if HEADING.match(l)]
    is_chapter = lambda l: bool(HEADING.match(l) and re.match(r"CHAPTER \d+\s*—", plain(HEADING.match(l).group(2))))
    is_part_or_chapter = lambda l: bool(HEADING.match(l) and len(HEADING.match(l).group(1)) <= 2 and
                                        re.match(r"(CHAPTER \d+\s*—|PART\b)", plain(HEADING.match(l).group(2))))
    first_map = None
    for i, m in starts:
        if len(m.group(1)) <= 2 and is_chapter(lines[i]):
            n, title = re.match(r"CHAPTER (\d+)\s*—\s*(.+)", plain(m.group(2))).groups()
            end = block_end(lines, i, is_part_or_chapter)
            chapters.setdefault(int(n), {})["title"] = title.title()
            chapters[int(n)]["map"] = trim(lines[i + 1:end])
            first_map = first_map if first_map is not None else i
            remove.append((i, end, None))

    # section 22: script revision flags per chapter
    s22 = top_section(lines, r"^22\.\s*SCRIPT REVISION FLAGS")
    if s22:
        subs = subsections(lines, *s22, r"^Chapter (\d+)\s*$")
        if subs:   # a closing note after the last chapter belongs to the whole section
            last = max(subs)
            a, b = subs[last]
            closing = next((i for i in range(a + 1, b) if lines[i].startswith("These flags")), b)
            subs[last] = (a, closing)
        for n, (a, b) in subs.items():
            chapters.setdefault(n, {})["flags"] = trim(lines[a + 1:b])
            remove.append((a, b, None))
        if subs:
            first = min(a for a, _ in subs.values())
            remove.append((first, first, ["The flags for each chapter are in its chapter file "
                                          f"({CHAPTER.format(n='<n>')}).", ""]))

    # section 20: principles (copied, not moved)
    s20 = top_section(lines, r"^20\.\s*PROSPERITY PRINCIPLES")
    if s20:
        for n, (a, b) in subsections(lines, *s20, r"^Chapter (\d+)\s*—").items():
            chapters.setdefault(n, {})["principle"] = (plain(HEADING.match(lines[a]).group(2)).split("—", 1)[-1].strip(),
                                                       trim(lines[a + 1:b]))

    # section 19: the six-chapter canon table (one row per chapter, copied)
    s19 = top_section(lines, r"^19\.\s*SIX-CHAPTER CANON")
    if s19:
        rows = [l for l in lines[s19[0]:s19[1]] if l.startswith("|")]
        header = [plain(c) for c in rows[0].strip("|").split("|")] if rows else []
        for row in rows[2:]:
            cells = [plain(c) for c in row.strip("|").split("|")]
            m = re.match(r"(\d+)", cells[0])
            if m:
                chapters.setdefault(int(m.group(1)), {})["canon"] = list(zip(header[1:], cells[1:]))

    if first_map is not None:
        names = ", ".join(CHAPTER.format(n=n) for n in sorted(chapters))
        remove.append((first_map, first_map, [f"The chapter-by-chapter interaction maps are in the chapter files: {names}.", ""]))

    # the bible: the source minus the moved blocks (applied bottom-up)
    out = list(lines)
    for a, b, repl in sorted(remove, key=lambda r: (r[0], r[1]), reverse=True):
        out[a:b] = repl if repl is not None else []
    bible = ["<!-- generated by scripts/split_bible.py from references/sources/"
             f"{source.name}; edit the source and rerun -->", ""] + out
    (OUT / BIBLE).write_text(re.sub(r"\n{4,}", "\n\n\n", "\n".join(bible)).rstrip() + "\n")
    print(f"references/{BIBLE}: {len(bible)} lines")

    for n in sorted(chapters):
        c = chapters[n]
        doc = ["<!-- generated by scripts/split_bible.py from references/sources/"
               f"{source.name}; edit the source and rerun -->", "",
               f"# Evoke Prosperity — Chapter {n}: {c.get('title', '')}".rstrip(": "), "",
               f"Chapter-specific canon. The general canon (world, characters, voices, rules) is in {BIBLE}.", ""]
        if c.get("canon"):
            doc += ["## At a glance", ""] + [f"- **{k}:** {v}" for k, v in c["canon"]] + [""]
        if c.get("principle"):
            name, body = c["principle"]
            doc += [f"## Prosperity Principle — {name}", ""] + body + [""]
        if c.get("map"):
            doc += ["## Character interaction map", ""] + c["map"] + [""]
        if c.get("flags"):
            doc += ["## Script revision flags", ""] + c["flags"] + [""]
        path = OUT / CHAPTER.format(n=n)
        path.write_text("\n".join(doc).rstrip() + "\n")
        print(f"references/{path.name}: {len(doc)} lines")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else SOURCE)
