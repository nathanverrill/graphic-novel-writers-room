"""What a reader gets: the pages, and nothing the writer said about them.

A script carries two kinds of text. One kind is printed: the art as described, captions,
balloons, screen text, sound effects. The other is the writer talking to the room: what a page
is for, how it is laid out, what the reader should feel, what changed since last round. A cold
reader must see only the first kind, or the report is about the plan instead of the pages. The
customer who read Prosperity's fourth draft had none of the second kind, and neither should
the room's readers."""
import re

from . import projects

# a line that is the writer talking, by its label
_NOTE = re.compile(
    r"^\s*(?:\*\*)?(issue question|page-turn question|reader question|cliffhanger question|turn question|page function|page-turn function|page intent|page check|chapter function|chapter intent|"
    r"central question|prosperity principle|style block|layout|rows? [a-z]\b|reading order|composition|timing|"
    r"lock|changed|intent|function|image prompt|writers.? room draft|draft script)\b", re.I)
# a sentence inside an art description that is aimed at the artist or the room, not the eye
_ASIDE = re.compile(
    r"\b(the reader|readers?\b|easy to miss|second-time|the eye should|should register|should feel|should hurt|"
    r"the point is|without resolving|in post|we can't yet|intended|foreshadow|hint at|"
    r"echoing (?:issue|chapter|page)|callback to)\b", re.I)
# "## Page 4 (left) — Show Alex's competence becoming entrapment": the title after the dash is intent
_PAGE_HEAD = re.compile(r"^(\s*#*\s*PAGE\s+\d+[^\n—:–-]*?)\s*(?:—|–|:|-)\s+.*$", re.I)
_DIALOGUE = re.compile(r"^\s*(?:\*\*)?[A-Z][A-Z0-9 .'\-]{0,24}(?:\s*\([^)]*\))?(?:\*\*)?\s*:")
_PANEL = re.compile(r"^\s*(?:\*\*)?(?:P|Panel)\s*\d+", re.I)
_CHAPTER = re.compile(r"\bchapter\s+(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b", re.I)
_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}


def _issue(m):
    n = m.group(1).lower()
    n = _WORDS.get(n, n)
    return f"Issue {int(n):02d}"


def pages_only(text):
    """The script with the writer's notes stripped: labelled note lines gone, page titles cut
    to the page number, asides to the artist removed from the art, chapters called issues."""
    out, skip = [], False
    for line in (text or "").splitlines():
        if re.match(r"^\s*#*\s*(chapter function|central question|prosperity principle)\b", line, re.I):
            skip = True
        if re.match(r"^\s*#*\s*PAGE\s+\d+", line, re.I):
            skip = False
        if skip or _NOTE.match(line):
            continue
        m = _PAGE_HEAD.match(line)
        if m:
            line = m.group(1).rstrip()
        elif not _DIALOGUE.match(line) and not _PANEL.match(line) and not re.match(r"^\s*#", line):
            label, sep, rest = line.partition(":") if re.match(r"^\s*(?:\*\*)?(image|captions?)\b", line, re.I) else ("", "", line)
            parts = re.split(r"(?<=[.!?])\s+", rest.strip())
            kept = " ".join(p for p in parts if not _ASIDE.search(p))
            if not kept.strip():
                continue
            line = f"{label}:{sep and ' '}{kept}" if sep else kept
        line = _CHAPTER.sub(_issue, line)
        out.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"


READER = "reader.md"       # in the campaign's rules/: who reads this book


def profile(slug):
    """rules/reader.md, if the campaign says who its reader is: the one thing from rules/ a reader gets."""
    path = projects.campaign_dir(slug) / projects.RULES / READER
    return path.read_text() if path.exists() else None
