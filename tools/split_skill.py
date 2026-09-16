"""Turn the long skills in skills/ into per-role guides, so each agent reads only
the parts it needs.

    python tools/split_skill.py

- skills/story_to_visual_translation_skill.md -> roles/<role>/storycraft.md (MAP below).
  Parts are the "# PART <roman>" headings; sections are the numbered "## N." headings.
- skills/ascii_art_skill.md -> roles/ascii_artist/ascii-art-skill.md, with the page rules
  that override it.
- skills/ascii_art_bible.md -> roles/ascii_artist/ascii-technique.md: only the drawing
  chapters (BIBLE_CHAPTERS). History, glossary and the gallery of other artists' work
  stay out of prompts.

Rerun after editing a skill or a map.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "skills" / "story_to_visual_translation_skill.md"
OUT_NAME = "storycraft.md"

# role folder -> (focus, parts, extra sections)
MAP = {
    "_shared": ("the medium and its core rules, for every role",
                ["INTRO", "I", "XXIX", "XXX", "XXXV"], []),
    "editor": ("pipeline, audience, format and concept development",
               ["II", "IX"], [90, 116]),
    "plotter": ("ideation, story mapping, structure, page budget and page turns",
                ["III", "IV", "V", "VI", "IX", "X"], [95, 96, 111, 116]),
    "character_designer": ("characters whose personality drives the plot",
                           ["VII"], [61, 112]),
    "scripter": ("scripting, narration, balloons, sound effects and rhythm",
                 ["VIII", "XI", "XII", "XXV", "XXVII"], [91, 92, 97, 102, 108, 114]),
    "penciller": ("spreads, storyboards, panels, camera, staging, backgrounds, action and print",
                  ["X", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI",
                   "XXII", "XXIII", "XXVI", "XXVIII"],
                  [93, 98, 99, 100, 101, 103, 104, 105, 107, 109, 113, 115, 117]),
    "colorist": ("color, tone and atmosphere", ["XXIV"], [70, 71]),
    "letterer": ("balloons, reading order, word density and sound effects",
                 ["XII", "XVI", "XVII", "XXV"], [33, 34, 106]),
    "continuity": ("critique, failure modes and preflight checks",
                   ["XXXII", "XXXIV"], [94]),
}


def parse(lines):
    """Returns ({part: (start, end)}, {section_number: (start, end)}) as line index ranges."""
    part_starts, sec_starts = [], []
    for i, line in enumerate(lines):
        m = re.match(r"^# PART ([IVXL]+) ", line)
        if m:
            part_starts.append((m.group(1), i))
        m = re.match(r"^## (\d+)\. ", line)
        if m:
            sec_starts.append((int(m.group(1)), i))

    parts = {"INTRO": (next(i for i, l in enumerate(lines) if l.startswith("# ")), part_starts[0][1])}
    for n, (name, start) in enumerate(part_starts):
        end = part_starts[n + 1][1] if n + 1 < len(part_starts) else len(lines)
        parts[name] = (start, end)

    boundaries = sorted([s for _, s in part_starts] + [s for _, s in sec_starts] + [len(lines)])
    sections = {num: (start, next(b for b in boundaries if b > start)) for num, start in sec_starts}
    return parts, sections


ASCII_SKILL = ROOT / "skills" / "ascii_art_skill.md"
ASCII_BIBLE = ROOT / "skills" / "ascii_art_bible.md"
BIBLE_CHAPTERS = [4, 7, 8, 9, 13]   # canvas, working method, lines and curves, shading, composition
ARTIST_DIR = ROOT / "roles" / "ascii_artist"

PAGE_RULES = """# ASCII art skill — and the page rules that override it

This is a general ASCII art skill. Drawing comic pages in this room, these rules win
wherever the skill says otherwise:

- **Canvas.** The page is a fixed 116 x 82 grid (one cell = one lettered letter). Ignore the
  skill's 72-column limit; return exactly the skeleton's size.
- **Text characters are for text only.** Letters, digits and `. , ! ? ' " - : ;` appear only
  in lettering. Where the skill draws with them, substitute: `.` and `,` -> `_` or `` ` ``;
  `'` -> `` ` ``; `-` -> `=` or `~`; `:` `;` `!` -> `|`; `o` `O` `0` -> `@` or `*`;
  `v` `V` -> `^`; letters used as texture -> `#` `%` `&` `@` `$`. Eyes are `*` or `@`.
- **Fonts.** Pages render in one known monospace font, so `^ ~ * #` are safe and useful —
  ignore the skill's warning about them.
- **No signatures or credits** on pages, and draw original work only.
- Emoticons, banners, Unicode and animation sections don't apply to pages.

---

"""


def split_ascii():
    skill = ASCII_SKILL.read_text().split("\n")
    if skill and skill[0].startswith("name:"):   # the skill's metadata line
        skill = skill[1:]
    out = ARTIST_DIR / "ascii-art-skill.md"
    out.write_text(HEADER.format(source=ASCII_SKILL.name) + PAGE_RULES + "\n".join(skill).strip() + "\n")
    print(f"{out.relative_to(ROOT)}: {out.stat().st_size // 1000} KB")

    lines = ASCII_BIBLE.read_text().split("\n")
    starts = [(int(m.group(1)), i) for i, l in enumerate(lines) if (m := re.match(r"^## Chapter (\d+):", l))]
    bounds = sorted([i for _, i in starts] + [i for i, l in enumerate(lines) if l.startswith("# ")] + [len(lines)])
    chunks = []
    for n, start in starts:
        if n in BIBLE_CHAPTERS:
            end = next(b for b in bounds if b > start)
            chunks.append("\n".join(lines[start:end]).strip())
    out = ARTIST_DIR / "ascii-technique.md"
    out.write_text(HEADER.format(source=ASCII_BIBLE.name)
                   + "# ASCII technique (from the ASCII Art Bible)\n\n"
                   + "The page rules in ascii-art-skill.md override anything here.\n\n"
                   + "\n\n".join(chunks) + "\n")
    print(f"{out.relative_to(ROOT)}: {out.stat().st_size // 1000} KB")


HEADER = "<!-- generated by tools/split_skill.py from skills/{source}; edit the source and rerun -->\n\n"


def main():
    lines = SOURCE.read_text().splitlines()
    parts, sections = parse(lines)
    for role, (focus, part_names, extra) in MAP.items():
        covered = [parts[p] for p in part_names]
        chunks = [lines[a:b] for a, b in covered]
        for num in extra:
            a, b = sections[num]
            if not any(pa <= a < pb for pa, pb in covered):  # skip if its part is already in
                chunks.append(lines[a:b])
        body = "\n".join("\n".join(c).strip() + "\n" for c in chunks)
        header = HEADER.format(source=SOURCE.name) + f"# Storycraft: {focus}\n\n"
        out = ROOT / "roles" / role / OUT_NAME
        out.write_text(header + body)
        print(f"{out.relative_to(ROOT)}: {len(body) // 1000} KB")


if __name__ == "__main__":
    main()
    split_ascii()
