"""Riff, in the room: brainstorm the draft with a model that has read it, then take its ideas
into the files one section at a time.

It works on one desk's three working files - story.md, characters.md, world.md - with the
campaign's rules/ as the limits it must keep, and the last structure checks as what is weak.
It is the step between intake drafting the files and approving them for production: the
sprint tool Riff (riff/) brought inside, writing to the same files the room reads.

    chat(slug, desk, messages)         -> {reply, suggestions, cost}
        every reply that proposes something ends with suggestions: one file, one section, one
        change each
    propose(slug, desk, suggestion)    -> the section as it is, and as the model would rewrite it
    accept(...)                        -> written through storydesk's section edit (hash-checked),
                                          and logged in riff-log.md on the desk

The material is sent as one cached prefix (Anthropic prompt caching through OpenRouter), so a
conversation pays for the files once, not on every message.
"""
import json
import re
import time
import urllib.error
import urllib.request

from . import artcheck, projects, render, storydesk

MODEL = "anthropic/claude-opus-5.5"
URL = "https://openrouter.ai/api/v1/chat/completions"
TIMEOUT = 300
LOG = "riff-log.md"
_last_usage = {}         # the last call's usage, for checking the cache
CAP = 120_000            # characters per file, a ceiling no working file reaches today

SYSTEM = """You are the brainstorming partner of the showrunner of {title}, a graphic novel. The Script
Coordinator has drafted the working files from the showrunner's material; they are DRAFT, to be improved
before the room writes the book from them. Help the showrunner riff: sharpen characters, fix the plot,
find holes, strengthen weak structure, propose better versions.

Be concrete and specific to this material. Offer options with trade-offs. Keep replies tight: short
paragraphs, plain words. The rules files are binding: never propose anything they forbid.

When your reply proposes anything the showrunner could take into the files, END it with a fenced block
of concrete edits, one per section, so each can be applied with one click:

```suggestions
[{{"file": "story.md", "section": "<the exact heading text of the section to change>", "new": false,
  "title": "<at most ten words: what this edit does>",
  "change": "<one to four sentences saying exactly what to change in that section>"}}]
```

- "file" is one of story.md, characters.md, world.md.
- "section" is a heading copied exactly from that file, without the # marks. To add a NEW section, set
  "new": true and make "section" the exact heading it should follow.
- Two to six suggestions. Valid JSON only inside the block. A purely informational reply gets no block.
"""


def _ask(messages, key, max_tokens=4000):
    body = {"model": MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                          "HTTP-Referer": "https://github.com/writers-room", "X-Title": "riff"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} {e.read()[:300].decode(errors='replace')}")
    except (urllib.error.URLError, TimeoutError) as e:
        raise RuntimeError(f"no answer: {e}")
    _last_usage.clear(); _last_usage.update(data.get("usage") or {})
    text = (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""
    if not text:
        raise RuntimeError(f"no reply: {json.dumps(data)[:300]}")
    return text, (data.get("usage") or {}).get("cost") or 0


def _key():
    key = render.api_key()
    if not key:
        raise ValueError("no OpenRouter key - add one on the room's screen")
    return key


def _rules(slug):
    d = projects.campaign_dir(slug) / "rules"
    return [(p.name, p.read_text()[:CAP]) for p in sorted(d.glob("*.md"))] if d.is_dir() else []


def _structure_notes(slug, desk):
    out = []
    for fw, f in storydesk.FRAMEWORKS.items():
        p = projects.project_dir(slug, desk) / f"structure-{fw}.json"
        if not p.exists():
            continue
        r = json.loads(p.read_text())
        names = {i: n for i, n, _ in f["stages"]}
        weak = [s for s in r.get("stages", []) if s.get("rating") in ("thin", "missing")]
        out.append(f"### {f['title']}: {r.get('score')}/100\n\n{r.get('summary', '')}\n\n" + "\n".join(
            f"- {names.get(s.get('id'), s.get('id'))} ({s.get('rating')}): {s.get('note', '')} "
            f"Suggested: {s.get('suggestion', '')}" for s in weak))
    return out


def material(slug, desk):
    """The cached prefix: the rules, the three files, and the last structure checks."""
    parts = ["# THE RULES (binding)"] + [f"## rules/{n}\n\n{t}" for n, t in _rules(slug)]
    parts.append("# THE WORKING FILES (draft, to improve)")
    for name in storydesk.EDITABLE:
        text = storydesk._read(slug, name, desk)
        parts.append(f"## {name}\n\n{text[:CAP] if text else '(not written yet)'}")
    notes = _structure_notes(slug, desk)
    if notes:
        parts.append("# THE LAST STRUCTURE CHECKS (where the outline is weak)\n\n" + "\n\n".join(notes))
    return "\n\n".join(parts)


def _system(slug, desk, role):
    """The material first and marked for caching, the role after it: the chat and the rewrites
    share one cached prefix, so only the first call in a while pays for the whole draft."""
    return [{"type": "text", "text": material(slug, desk), "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": role}]


def _title(slug):
    head = storydesk._read(slug, "story.md", projects.PRE).splitlines()[:1] or [slug]
    return re.sub(r"^#\s*|\s*[—-]\s*Story\s*$", "", head[0]).strip() or slug


def chat(slug, desk, messages):
    key = _key()
    msgs = [{"role": m["role"], "content": str(m["content"])[:20000]} for m in (messages or [])
            if isinstance(m, dict) and m.get("role") in ("user", "assistant") and m.get("content")][-30:]
    if not msgs or msgs[-1]["role"] != "user":
        raise ValueError("say something")
    system = _system(slug, desk, SYSTEM.format(title=_title(slug)))
    reply, cost = _ask([{"role": "system", "content": system}] + msgs, key)
    suggestions = []
    m = re.search(r"```suggestions\s*(.*?)```", reply, re.S)
    if m:
        reply = (reply[:m.start()] + reply[m.end():]).strip()
        try:
            raw = json.loads(m.group(1))
            suggestions = [{"file": str(s.get("file", "")), "section": str(s.get("section", ""))[:200],
                            "new": bool(s.get("new")), "title": str(s.get("title", ""))[:120],
                            "change": str(s.get("change", ""))[:1500]}
                           for s in raw if isinstance(s, dict) and s.get("file") in storydesk.EDITABLE and s.get("change")][:6]
        except (json.JSONDecodeError, TypeError):
            pass
    for s in suggestions:
        s["found"] = _find(slug, desk, s["file"], s["section"]) is not None
    return {"reply": reply, "suggestions": suggestions, "cost": cost}


def _find(slug, desk, name, heading):
    """The index of the section whose heading is `heading`: exact, then ignoring case and
    punctuation, then the one heading that contains it."""
    sections = storydesk.parse(storydesk._read(slug, name, desk))
    norm = lambda t: re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()
    want = norm(heading.lstrip("#").strip())
    if not want:
        return None
    for test in (lambda t: t == heading.lstrip("#").strip(), lambda t: norm(t) == want):
        hits = [i for i, s in enumerate(sections) if s["level"] and test(s["title"])]
        if hits:
            return hits[0]
    hits = [i for i, s in enumerate(sections) if s["level"] and want in norm(s["title"])]
    return hits[0] if len(hits) == 1 else None


REWRITE = """You edit one section of {file}, a working file of a graphic novel, to carry out one accepted change.

Rules for the edit:
- Change only what the change asks for, and what it makes untrue. Keep everything else word for word:
  the section's form, its markdown, its source citations in backticks, its level of detail and its voice.
- Never contradict the rules files or the rest of the working files.
- {mode}

Reply with ONLY a JSON object: {{"title": "<the section heading, without # marks>", "body": "<the full section text, markdown>"}}

=== THE CHANGE ===
{change}

=== {what} ===
{section}
"""


def propose(slug, desk, file, section, change, new=False):
    """The section as it is and as it would be with the change: nothing is written yet."""
    key = _key()
    name = storydesk._file(file)
    out = storydesk.outline(slug, desk, name)
    i = _find(slug, desk, name, section)
    if i is None:
        raise ValueError(f'no heading "{section}" in {name} - edit it by hand, or ask Riff to name the section exactly')
    s = out["sections"][i]
    if new:
        mode = ("Write a NEW section to follow the one below, in the same form and at the same heading level. "
                "The section below is only there to show the form and where it goes; do not repeat it.")
        what = "THE SECTION THE NEW ONE FOLLOWS"
    else:
        mode = "Return the whole section rewritten, including the parts that do not change."
        what = "THE SECTION AS IT IS"
    system = _system(slug, desk, "You keep a graphic novel's working files consistent.")
    text, cost = _ask([{"role": "system", "content": system},
                       {"role": "user", "content": REWRITE.format(file=name, mode=mode, what=what, change=change,
                                                                  section=f"{'#' * s['level']} {s['title']}\n\n{s['body']}")}],
                      key, max_tokens=8000)
    data = artcheck._json(text)
    if not data or "body" not in data:
        raise RuntimeError("the rewrite could not be read - try again")
    title = storydesk._clean_title(str(data.get("title") or s["title"]).lstrip("#").strip())
    body = str(data["body"]).strip("\n")
    body = re.sub(rf"^#{{1,6}}\s+{re.escape(title)}\s*\n+", "", body)      # a heading repeated in the body
    if not new and len(body) < len(s["body"]) * 0.3 and len(s["body"]) > 400:
        raise RuntimeError("the rewrite came back far shorter than the section - left as it was; try again")
    return {"file": name, "hash": out["hash"], "i": i, "new": new, "level": s["level"],
            "before": {"title": s["title"], "body": s["body"]} if not new else None,
            "after": {"title": title, "body": body}, "anchor": s["title"], "cost": cost}


def accept(slug, desk, file, file_hash, i, title, body, new=False, level=3, why=""):
    """Write the proposed section through the hash-checked section edit, and log it."""
    name = storydesk._file(file)
    if new:
        out = storydesk.add_section(slug, desk, file_hash, i, level, title, body, name)
    else:
        out = storydesk.update_section(slug, desk, file_hash, i, title, body, name)
    log = projects.project_dir(slug, desk) / LOG
    head = "" if log.exists() else "# Riff log\n\nEvery change taken from Riff into the working files, newest last.\n"
    with log.open("a") as f:
        f.write(f"{head}\n## {time.strftime('%Y-%m-%d %H:%M')} — {name}: {'new section ' if new else ''}{title}\n\n{why.strip()}\n")
    return out
