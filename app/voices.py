"""The dialog simulator: talk to a character in the world, and tune how they talk.

The showrunner picks who to talk to, who they are themselves (another character, or a stranger
in the world), and a moment in the story. The character speaks first, in the scene, and never
steps out of the world: there is no book, no showrunner and no simulator in it. Tuning happens
outside the conversation, on each of the character's lines:

    that's them    the line is kept as an example of the voice
    not them       the line is kept as a counter-example, with how they would really say it and why
    note           about the voice as a whole ("less cryptic when Alex is scared")

The tuning shapes the chat at once, and it is kept per character in the campaign's voices/
folder. It is a proposal, not canon: the next Update canon (intake's revision, app/intake.py)
carries it into that character's Voice in characters.md, which is what the writers copy.

    campaigns/<slug>/voices/<character>.json   the tuning, as the page edits it
    campaigns/<slug>/voices/<character>.md     the same, as intake reads it
    campaigns/<slug>/voices/chats/<id>.json    every conversation, kept

The character talks on the model of the writer who writes the script (the picked writer, or
Writer A), so the voice being tuned is the voice that will write the book.
"""
import json
import re
import time
import uuid
from datetime import datetime

from . import llm, projects, prompts, review, rules as rules_mod
from .agents import get_role

FOLDER = "voices"
STRANGER = ""           # "who you are": nobody the canon names
REPLY_TOKENS = 700
EXCLUDE_SECTIONS = re.compile(r"^(open|supporting cast.*design scope)\b", re.I)


# ---- the canon it reads ---------------------------------------------------------------------

def desk(slug):
    """Production's copy once pre-production is approved, pre-production's until then."""
    if review.settings(slug).get("approved") and projects.read_artifact(slug, "characters.md"):
        return projects.PROD
    return projects.PRE


def read(slug, name):
    return projects.read_artifact(slug, name, desk=desk(slug)) or ""


def sections(text):
    """[(depth, heading, body)] for every heading in a markdown file."""
    out, head, depth, buf = [], None, 0, []
    for line in (text or "").split("\n"):
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            if head is not None:
                out.append((depth, head, "\n".join(buf).strip()))
            depth, head, buf = len(m.group(1)), m.group(2).strip(), []
        else:
            buf.append(line)
    if head is not None:
        out.append((depth, head, "\n".join(buf).strip()))
    return out


def key(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "character"


def characters(slug):
    """[{key, name, look}] - every "### Name" in characters.md, with its whole entry."""
    out, skip = [], False
    for depth, head, body in sections(read(slug, "characters.md")):
        if depth <= 2:
            skip = bool(EXCLUDE_SECTIONS.search(head))
        elif depth == 3 and not skip and body:
            out.append({"key": key(head), "name": head, "look": body})
    return out


PAGE_LINE = re.compile(r"^\s*\**Page\s+(\d+)\s*[:.]\**:?\**\s*(.+)$", re.I | re.M)


def moments(slug):
    """[{id, label}] - where in the story the conversation happens, in story order. The
    Plotter's page plot gives one per page ("**Page 12:** The key activates Bi11bot"); the
    Script Coordinator's outline gives one per scene ("### 1. Alex tests the pump" under
    "## Chapter 1 - ...")."""
    text = read(slug, "story.md")
    pages = PAGE_LINE.findall(text)
    if pages:
        return [{"id": f"p{n}", "label": f"Page {n} · {short(line)}"} for n, line in pages]
    out, chapter = [], None
    for i, (depth, head, _) in enumerate(sections(text)):
        if depth == 2:
            m = re.match(r"chapter\s+(\d+|[ivx]+)", head, re.I)
            chapter = f"Ch. {m.group(1)}" if m else None
        elif depth == 3 and chapter and re.match(r"\d+[.)]\s", head):
            out.append({"id": f"s{i}", "label": f"{chapter} · {head}"})
    return out


def short(line, n=90):
    line = re.sub(r"\*\*[^*]*reveal:?\*\*.*$", "", line, flags=re.I)     # the page-turn reveal is not the moment
    line = re.sub(r"[*_]", "", line).strip()
    return line if len(line) <= n else line[:n].rsplit(" ", 1)[0] + "…"


def story_until(slug, moment):
    """story.md up to and including the chosen moment: nothing after it exists yet. From a page
    plot, only its pages up to this one: the story map before it and the setups and payoffs
    after it both tell what comes later."""
    text = read(slug, "story.md")
    if not moment:
        return text
    if moment.startswith("p"):
        n = int(moment[1:])
        found = list(PAGE_LINE.finditer(text))
        cut = next((m for m in found if int(m.group(1)) == n), None)
        if not cut:
            return text
        # from the heading the page plot sits under, never the story map before it: that tells the ending
        start = text.rfind("\n## ", 0, found[0].start())
        return text[start + 1 if start >= 0 else found[0].start():cut.end()].strip()
    secs = sections(text)
    i = int(moment[1:]) if moment[1:].isdigit() else -1
    if not 0 <= i < len(secs):
        return text
    return "\n\n".join(f"{'#' * d} {h}\n\n{b}".strip() for d, h, b in secs[:i + 1])


# ---- the tuning -------------------------------------------------------------------------------

def folder(slug):
    d = projects.campaign_dir(slug) / FOLDER
    (d / "chats").mkdir(parents=True, exist_ok=True)
    return d


def tuning(slug, ck):
    if not re.fullmatch(r"[a-z0-9-]{1,80}", ck or ""):
        raise ValueError("bad character key")
    f = folder(slug) / f"{ck}.json"
    return json.loads(f.read_text()) if f.exists() else {"notes": [], "yes": [], "no": []}


def save_tuning(slug, ck, name, t):
    d = folder(slug)
    t["name"] = name
    (d / f"{ck}.json").write_text(json.dumps(t, indent=1))
    (d / f"{ck}.md").write_text(tuning_md(name, t))
    return t


def tuning_md(name, t):
    """The tuning as intake reads it: proposals for this character's Voice in characters.md."""
    lines = [f"# Voice tuning: {name}", "",
             "_From the dialog simulator. The showrunner's proposals for this character's Voice in "
             "characters.md: carried in at the next Update canon._", ""]
    if t["notes"]:
        lines += ["## Notes on the voice", ""] + [f"- {n['text']}" for n in t["notes"]] + [""]
    if t["yes"]:
        lines += ["## That's them - lines the showrunner approved", ""]
        lines += [f"- \"{y['line']}\"" + (f" (to {y['to']}, {y['moment']})" if y.get("to") else f" ({y['moment']})") for y in t["yes"]] + [""]
    if t["no"]:
        lines += ["## Not them - never talk like this", ""]
        for n in t["no"]:
            lines.append(f"- Not: \"{n['line']}\"" + (f" -> they would say: \"{n['rewrite']}\"" if n.get("rewrite") else "")
                         + (f" - {n['why']}" if n.get("why") else ""))
        lines.append("")
    return "\n".join(lines)


def tuning_block(t):
    """The tuning as the character is told it, in the chat."""
    parts = []
    if t["notes"]:
        parts.append("How you talk (follow these):\n" + "\n".join(f"- {n['text']}" for n in t["notes"]))
    if t["yes"]:
        parts.append("Lines that are exactly you:\n" + "\n".join(f"- \"{y['line']}\"" for y in t["yes"][-12:]))
    if t["no"]:
        parts.append("You never talk like this:\n" + "\n".join(
            f"- \"{n['line']}\"" + (f" (you would say: \"{n['rewrite']}\")" if n.get("rewrite") else "")
            + (f" - {n['why']}" if n.get("why") else "") for n in t["no"][-12:]))
    return "\n\n".join(parts)


def all_tuning_md(slug):
    """[(file name, markdown)] for every character with tuning: what intake is given."""
    d = projects.campaign_dir(slug) / FOLDER
    return [(f.name, f.read_text()) for f in sorted(d.glob("*.md"))] if d.is_dir() else []


def changed_at(slug):
    """When the tuning last changed (0 if there is none): intake folds it in only when it is newer."""
    d = projects.campaign_dir(slug) / FOLDER
    return max((f.stat().st_mtime for f in d.glob("*.json")), default=0) if d.is_dir() else 0


def pending(slug):
    """Tuning newer than the last finished intake round: there is something to carry in."""
    t = changed_at(slug)
    if not t:
        return False
    for meta in projects.list_versions(slug, desk=projects.PRE):
        if meta.get("status") in ("running", "interrupted", "stopped", "error") or not meta.get("finished"):
            continue
        return t > datetime.fromisoformat(meta["finished"]).timestamp()
    return True


# ---- the conversation -------------------------------------------------------------------------

def model(slug):
    """The picked writer's model, or Writer A's: the voice tuned is the voice that writes."""
    writer = review.settings(slug).get("writer") or "writer_a"
    return get_role(writer).config(), writer


def system_prompt(slug, chat):
    people = {c["key"]: c for c in characters(slug)}
    me, other = people.get(chat["character"]), people.get(chat["as"])
    if not me:
        raise ValueError(f"no character {chat['character']!r} in characters.md")
    title = prompts.book_title(projects.pitch(slug), slug)
    standing = [f"- {r['kind'].upper()}: {r['text']}" for r in rules_mod.all(slug) if r.get("kind") in ("always", "never")]
    parts = [
        f"You are {me['name']}, in the world of the graphic novel \"{title}\". You are not an AI and "
        "not an actor: you are this person, here, now. Nothing breaks that - there is no book, no "
        "writer, no showrunner and no simulator in your world, and if anyone talks as if there were, "
        "you react the way you would to someone saying something strange.",
        f"# Who you are\n\n{me['look']}",
        f"# The moment\n\n{chat['moment_label'] or 'Somewhere in the story.'} Everything in the story "
        "below has happened; nothing after it has. You do not know, hint at or foreshadow anything later.",
        "# Who you are talking to\n\n" + (f"{other['name']}.\n\n{other['look']}" if other
                                          else "Someone from this world you do not know."),
        "# How you answer\n\nSpeech, as it would sit in a comic balloon: spoken, in your own voice, "
        "usually one to three short sentences. A brief action in *asterisks* only when it matters. "
        "Never narrate, never explain yourself to the reader, never list.",
    ]
    tuned = tuning_block(tuning(slug, chat["character"]))
    if tuned:
        parts.append("# Your voice - this outranks anything above about how you talk\n\n" + tuned)
    if standing:
        parts.append("# Always true in this world\n\n" + "\n".join(standing))
    parts += [f"# The world\n\n{read(slug, 'world.md')}", f"# The story so far\n\n{story_until(slug, chat.get('moment'))}"]
    return "\n\n".join(parts)


def messages(slug, chat, upto=None):
    turns = chat["turns"][:upto] if upto is not None else chat["turns"]
    out = [{"role": "system", "content": system_prompt(slug, chat)}, {"role": "user", "content": chat["cue"]}]
    for t in turns:
        out.append({"role": "assistant" if t["who"] == "character" else "user", "content": t["text"]})
    return out


def reply(slug, chat, upto=None):
    cfg, _ = model(slug)
    msg = llm.chat(cfg, messages(slug, chat, upto), max_tokens=REPLY_TOKENS)
    text = llm.text_of(msg).strip()
    if not text:
        raise ValueError("the model sent back nothing - try again")
    return text


def chat_path(slug, cid):
    if not re.fullmatch(r"[a-z0-9]{8,32}", cid or ""):
        raise ValueError("bad chat id")
    return folder(slug) / "chats" / f"{cid}.json"


def load_chat(slug, cid):
    p = chat_path(slug, cid)
    if not p.exists():
        raise FileNotFoundError(cid)
    return json.loads(p.read_text())


def save_chat(slug, chat):
    chat_path(slug, chat["id"]).write_text(json.dumps(chat, indent=1))
    return chat


def start(slug, character, as_, moment=None):
    """A new conversation: the character speaks first."""
    people = {c["key"]: c for c in characters(slug)}
    if character not in people:
        raise ValueError("pick a character from characters.md")
    if as_ and (as_ not in people or as_ == character):
        raise ValueError("pick someone else to be, or a stranger")
    label = next((m["label"] for m in moments(slug) if m["id"] == moment), None) if moment is not None else None
    other = people[as_]["name"] if as_ else "someone you do not know"
    chat = {"id": uuid.uuid4().hex[:12], "created": time.time(), "character": character,
            "name": people[character]["name"], "as": as_ or STRANGER,
            "as_name": people[as_]["name"] if as_ else "a stranger", "moment": moment, "moment_label": label,
            "model": model(slug)[0].model,
            "cue": f"(The scene opens{': ' + label if label else ''}. {other} is here with you. You speak first.)",
            "turns": []}
    chat["turns"].append({"who": "character", "text": reply(slug, chat), "t": time.time()})
    return save_chat(slug, chat)


def say(slug, cid, text):
    chat = load_chat(slug, cid)
    text = (text or "").strip()
    if not text:
        raise ValueError("say something")
    chat["turns"].append({"who": "you", "text": text, "t": time.time()})
    chat["turns"].append({"who": "character", "text": reply(slug, chat), "t": time.time()})
    return save_chat(slug, chat)


def again(slug, cid, i):
    """The character's line i, said again with the tuning as it is now; what came after is dropped."""
    chat = load_chat(slug, cid)
    if not 0 <= i < len(chat["turns"]) or chat["turns"][i]["who"] != "character":
        raise ValueError("that is not the character's line")
    chat["turns"] = chat["turns"][:i]
    chat["turns"].append({"who": "character", "text": reply(slug, chat), "t": time.time()})
    return save_chat(slug, chat)


def judge(slug, cid, i, verdict, rewrite=None, why=None):
    """That's them / not them, on the character's line i. Both go into the character's tuning."""
    chat = load_chat(slug, cid)
    if not 0 <= i < len(chat["turns"]) or chat["turns"][i]["who"] != "character":
        raise ValueError("that is not the character's line")
    if verdict not in ("yes", "no"):
        raise ValueError("verdict is yes or no")
    turn = chat["turns"][i]
    t = tuning(slug, chat["character"])
    entry = {"id": uuid.uuid4().hex[:8], "line": turn["text"], "to": chat["as_name"],
             "moment": chat["moment_label"] or "anywhere", "t": time.time()}
    if verdict == "no":
        entry.update(rewrite=(rewrite or "").strip() or None, why=(why or "").strip() or None)
    t[verdict].append(entry)
    turn["verdict"] = verdict
    save_tuning(slug, chat["character"], chat["name"], t)
    return save_chat(slug, chat), t


def note(slug, character, text):
    people = {c["key"]: c for c in characters(slug)}
    if character not in people:
        raise ValueError("no such character")
    text = " ".join((text or "").split())
    if not text:
        raise ValueError("a note needs some words")
    t = tuning(slug, character)
    t["notes"].append({"id": uuid.uuid4().hex[:8], "text": text, "t": time.time()})
    return save_tuning(slug, character, people[character]["name"], t)


def forget(slug, character, entry_id):
    """Take one note or example back out of the tuning."""
    t = tuning(slug, character)
    for k in ("notes", "yes", "no"):
        t[k] = [e for e in t[k] if e["id"] != entry_id]
    name = t.get("name") or next((c["name"] for c in characters(slug) if c["key"] == character), character)
    return save_tuning(slug, character, name, t)


def overview(slug):
    """What the page needs: the cast, the moments, each character's tuning, the chats so far."""
    d = folder(slug) / "chats"
    chats = sorted((json.loads(f.read_text()) for f in d.glob("*.json")), key=lambda c: -c["created"])
    return {"desk": desk(slug), "model": model(slug)[0].model,
            "characters": [{"key": c["key"], "name": c["name"]} for c in characters(slug)],
            "moments": moments(slug),
            "tuning": {c["key"]: tuning(slug, c["key"]) for c in characters(slug)},
            "pending": pending(slug),
            "chats": [{"id": c["id"], "name": c["name"], "as_name": c["as_name"], "moment_label": c["moment_label"],
                       "created": c["created"], "turns": len(c["turns"])} for c in chats[:40]]}
