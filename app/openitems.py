"""Open items — what your material leaves undecided, and your answers.

In intake's second pass the Script Coordinator lists every gap and contradiction the four files
leave open in `open-items.md`, each with the answers it can propose and the one it would pick:

    ## 1. Are Tomas and Tomas Reed the same person?
    - file: characters.md
    - why: two men share a name in two cities, and a reader will merge them
    - A: Two people. Rename the Halyard engineer. (input/characters.md treats them as separate)
    - B: One person, who left Keel for Halyard.
    - suggested: A

(and `- from:` — the showrunner, the Script Coordinator, or both — when your own open items,
input/open-items.md, were reconciled with its list; see app/intake.py, call 2.)

You approve a proposal, edit it, or leave the item open for the room to decide in development.
An answer is yours, so it does not go on the room's desk: it is written to the campaign's
`rules/decisions.md`, where it binds the book like any other rule and survives every rerun.
You can also settle an item by hand, by writing a `- decision:` line into the item in
`preproduction/open-items.md`. Either way, the next intake run is an integration pass (app/intake.py,
pass 4): it carries each answer into the file it belongs to and leaves only what is still open.
"""
import re

from . import projects

ITEMS = "open-items.md"
DECISIONS = "decisions.md"
FEEDBACK_HEADS = ("feedback", "showrunner feedback", "notes", "showrunner notes")
RESOLVED, DEFERRED, UNRESOLVED = "resolved", "deferred", "unresolved"
FIELDS = ("file", "why", "from", "evidence", "suggested", "decision", "feedback", "defer")
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
        if not m and lines[0].strip().rstrip(":").lower() in FEEDBACK_HEADS:
            continue        # a showrunner's general note, not a question — see general_feedback
        item = {"n": int(m.group(1)) if m else len(items) + 1,
                "question": (m.group(2) if m else lines[0]).strip(),
                **{f: "" for f in FIELDS}, "options": []}
        for line in lines[1:]:
            f = re.match(r"^\s*[-*]\s*\**([A-Za-z]+)\**\s*:\s*(.*)", line)
            if not f:
                continue
            label, value = f.group(1), f.group(2).strip()
            if label.lower() in FIELDS:
                item[label.lower()] = value
            elif len(label) == 1:
                item["options"].append({"id": label.upper(), "text": value})
        item["status"] = (RESOLVED if item["decision"] else
                          DEFERRED if item["defer"] else UNRESOLVED)
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


def general_feedback(text):
    """A `## Feedback` block in open-items.md: the showrunner talking about the book as a
    whole rather than answering one question. Pass 4 treats it as a rule for that run."""
    for block in re.split(r"^##\s+", text or "", flags=re.M)[1:]:
        head, _, body = block.partition("\n")
        if head.strip().rstrip(":").lower() in FEEDBACK_HEADS:
            return body.strip()
    return ""


def state(slug):
    """The items the last intake raised, each with your answer if you have given one.

    An item is resolved when you have answered it — in rules/decisions.md, through the screen,
    or with a `- decision:` line — deferred when you have said to leave it (`- defer:`), and
    unresolved otherwise. `- feedback:` is a note about an item that is not an answer to it."""
    text = projects.read_artifact(slug, ITEMS, desk=projects.PRE)
    decided = decisions(slug)
    items = parse(text)
    for item in items:
        item["answer"] = decided.get(_key(item["question"])) or item["decision"] or None
        if item["answer"]:
            item["status"] = RESOLVED
    return {"items": items,
            "answered": sum(1 for i in items if i["answer"]),
            "deferred": sum(1 for i in items if i["status"] == DEFERRED),
            "unresolved": sum(1 for i in items if i["status"] == UNRESOLVED),
            "feedback": general_feedback(text),
            "decisions_file": f"{projects.RULES}/{DECISIONS}"}


def note_on(slug, n, field, text):
    """Write a `- feedback:` or `- defer:` line onto item n in open-items.md, or clear it.

    These stay in the file rather than going to rules/decisions.md: feedback is about how the
    book should read rather than what is true in it, and a deferral is about this round. Pass 4
    reads both from here."""
    if field not in ("feedback", "defer"):
        raise ValueError(f"no such field {field!r}")
    text = (text or "").strip()
    body = projects.read_artifact(slug, ITEMS, desk=projects.PRE) or ""
    blocks = re.split(r"^(?=##\s)", body, flags=re.M)
    for i, block in enumerate(blocks):
        m = re.match(r"##\s+(\d+)[.)]", block)
        if not m or int(m.group(1)) != n:
            continue
        lines = [l for l in block.rstrip("\n").split("\n")
                 if not re.match(rf"^\s*[-*]\s*\**{field}\**\s*:", l, flags=re.I)]
        if text:
            lines.append(f"- {field}: {text}")
        blocks[i] = "\n".join(lines) + "\n\n"
        projects.write_artifact(slug, ITEMS, "".join(blocks).rstrip("\n") + "\n", desk=projects.PRE)
        return state(slug)
    raise ValueError(f"no open item {n}")


def set_feedback(slug, text):
    """The showrunner's general note about the book, kept in a `## Feedback` block at the end
    of open-items.md. Pass 4 reads it as a rule for that integration."""
    text = (text or "").strip()
    body = projects.read_artifact(slug, ITEMS, desk=projects.PRE) or ""
    blocks = [b for b in re.split(r"^(?=##\s)", body, flags=re.M)
              if b.partition("\n")[0].lstrip("# ").strip().rstrip(":").lower() not in FEEDBACK_HEADS]
    kept = "".join(blocks).rstrip("\n")
    if text:
        kept += f"\n\n## Feedback\n\n{text}"
    projects.write_artifact(slug, ITEMS, kept.lstrip("\n") + "\n", desk=projects.PRE)
    return state(slug)


def answer(slug, n, text):
    """Record your answer to item n — or, with no text, take it back and leave the item open."""
    item = next((i for i in parse(projects.read_artifact(slug, ITEMS, desk=projects.PRE)) if i["n"] == n), None)
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
