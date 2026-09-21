"""Open items — what your material leaves undecided, and your answers.

At intake the Script Coordinator lists every gap and contradiction it found in `open-items.md`,
each with the answers it can propose and the one it would pick:

    ## 1. Are Tomas and Tomas Reed the same person?
    - file: characters.md
    - why: two men share a name in two cities, and a reader will merge them
    - A: Two people. Rename the Halyard engineer. (input/characters.md treats them as separate)
    - B: One person, who left Keel for Halyard.
    - suggested: A

(and `- from:` — the showrunner, the Script Coordinator, or both — when your own open items,
input/open-items.md, were joined with its list; see Agent.fuse_open_items.)

You approve a proposal, edit it, or leave the item open for the room to decide in development.
An answer is yours, so it does not go on the room's desk: it is written to the campaign's
`rules/decisions.md`, where it binds the book like any other rule and survives every rerun.
The next intake reads it there, states it as FIXED in the file it belongs to, and drops the
item from the list.
"""
import re

from . import projects

ITEMS = "open-items.md"
DECISIONS = "decisions.md"
HEAD = ("# Decisions\n\n"
        "The showrunner's answers to the open items the Script Coordinator raised at intake. "
        "Each one settles its question: the book must not contradict it.\n")


def _decisions_path(slug):
    return projects.campaign_dir(slug) / projects.RULES / DECISIONS


def _key(question):
    return re.sub(r"[^a-z0-9]+", " ", question.lower()).strip()


def parse(text):
    """open-items.md as a list of {n, question, file, why, options: [{id, text}], suggested}."""
    items = []
    for block in re.split(r"^##\s+", text or "", flags=re.M)[1:]:
        lines = block.strip().split("\n")
        m = re.match(r"(\d+)[.)]\s*(.*)", lines[0].strip())
        item = {"n": int(m.group(1)) if m else len(items) + 1,
                "question": (m.group(2) if m else lines[0]).strip(),
                "file": "", "why": "", "from": "", "options": [], "suggested": ""}
        for line in lines[1:]:
            f = re.match(r"^\s*[-*]\s*\**([A-Za-z]+)\**\s*:\s*(.*)", line)
            if not f:
                continue
            label, value = f.group(1), f.group(2).strip()
            if label.lower() in ("file", "why", "from", "suggested"):
                item[label.lower()] = value
            elif len(label) == 1:
                item["options"].append({"id": label.upper(), "text": value})
        item["suggested"] = item["suggested"][:1].upper()
        if not item["suggested"]:       # agents also mark it inline: "- A: ... (suggested; ...)"
            item["suggested"] = next((o["id"] for o in item["options"] if "(suggested" in o["text"].lower()), "")
        items.append(item)
    return items


def decisions(slug):
    """{question key: answer} from rules/decisions.md."""
    path = _decisions_path(slug)
    if not path.exists():
        return {}
    out = {}
    for block in re.split(r"^##\s+", path.read_text(), flags=re.M)[1:]:
        head, _, body = block.partition("\n")
        out[_key(head)] = re.sub(r"\n_\(.*?\)_\s*$", "", body.strip(), flags=re.S).strip()
    return out


def state(slug):
    """The items the last intake raised, each with your answer if you have given one."""
    decided = decisions(slug)
    items = parse(projects.read_artifact(slug, ITEMS))
    for item in items:
        item["answer"] = decided.get(_key(item["question"]))
    return {"items": items, "answered": sum(1 for i in items if i["answer"]),
            "decisions_file": f"{projects.RULES}/{DECISIONS}"}


def answer(slug, n, text):
    """Record your answer to item n — or, with no text, take it back and leave the item open."""
    item = next((i for i in parse(projects.read_artifact(slug, ITEMS)) if i["n"] == n), None)
    if item is None:
        raise ValueError(f"no open item {n}")
    path = _decisions_path(slug)
    blocks = re.split(r"^(?=##\s)", path.read_text(), flags=re.M) if path.exists() else [HEAD]
    blocks = [b for b in blocks[:1] + [b for b in blocks[1:]
              if _key(b.partition("\n")[0].lstrip("# ")) != _key(item["question"])]]
    text = (text or "").strip()
    if text:
        about = f", about {item['file']}" if item["file"] else ""
        blocks.append(f"## {item['question']}\n\n{text}\n\n_(decided {projects.now()[:10]}{about})_\n")
    if len(blocks) == 1 and not text:
        path.unlink(missing_ok=True)      # nothing decided: no empty rules file left behind
    else:
        path.parent.mkdir(exist_ok=True)
        path.write_text("\n".join(b.rstrip("\n") + "\n" for b in blocks))
    return state(slug)
