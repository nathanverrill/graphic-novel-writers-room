"""Standing rules — what the showrunner always wants, or never wants.

A jotted note is for one round: the room reads it, acts on it, and it's spent. A rule is
permanent, and it reaches the room two ways from the one list in rules.json:

- `rules/showrunner-rules.md` in the campaign, beside decisions.md. Everything in rules/ is
  binding source material for intake on every pass, so a rule holds for a synthesis from
  scratch as much as for a revision, and it survives starting pre-production over.
- The Director's `taste-writers.md`, the file every writer reads before it starts, in a block
  the room doesn't own:

      <!-- showrunner rules -->
      ## The showrunner's standing rules
      ...
      <!-- end showrunner rules -->

  The Director rewrites that file every round, so the block is put back on every save
  (enforce_rules, beside review.enforce_locks) and the rules survive whatever it wrote.
"""
import json
import re
import time

from . import projects

FILE = "rules.json"
RULES_FILE = "showrunner-rules.md"    # in the campaign's rules/, read by intake
TASTE = "taste-writers.md"
START = "<!-- showrunner rules -->"
END = "<!-- end showrunner rules -->"
BLOCK_RE = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
KINDS = ("always", "never", "note")


def _path(slug):
    return projects.project_dir(slug) / FILE


def all(slug):
    path = _path(slug)
    return json.loads(path.read_text()) if path.exists() else []


def _save(slug, rules):
    _path(slug).write_text(json.dumps(rules, indent=2))
    write_rules_file(slug, rules)
    write_taste(slug)
    return rules


def add(slug, text, kind="always"):
    text = " ".join(str(text).split())
    if not text:
        raise ValueError("a rule needs some words")
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {', '.join(KINDS)}")
    rules = all(slug)
    rules.append({"id": max((r["id"] for r in rules), default=0) + 1,
                  "kind": kind, "text": text, "t": time.time()})
    return _save(slug, rules)


def drop(slug, rule_id):
    return _save(slug, [r for r in all(slug) if r["id"] != rule_id])


def markdown(rules):
    if not rules:
        return ""
    lines = [START, "## The showrunner's standing rules", "",
             "These hold for every round, on every page. They outrank anything else in this file. "
             "If one of them and a note pull in different directions, follow the rule and say so "
             "in your handoff note.", ""]
    for r in rules:
        label = {"always": "Always", "never": "Never", "note": "Remember"}[r["kind"]]
        lines.append(f"- **{label}:** {r['text']}")
    return "\n".join(lines + ["", END]) + "\n"


def rules_file(rules):
    """rules/showrunner-rules.md: the same list as intake reads it - binding, like a decision."""
    lines = ["# The showrunner's standing rules", "",
             "These bind the book. A name, a fact or a prohibition here holds in every file, on "
             "every page, and outranks anything in the material that says otherwise.", ""]
    for r in rules:
        label = {"always": "Always", "never": "Never", "note": "Remember"}[r["kind"]]
        lines.append(f"- **{label}:** {r['text']}")
    return "\n".join(lines) + "\n"


def write_rules_file(slug, rules):
    path = projects.campaign_dir(slug) / projects.RULES / RULES_FILE
    if rules:
        path.parent.mkdir(exist_ok=True)
        path.write_text(rules_file(rules))
    elif path.exists():
        path.unlink()


def enforce_rules(slug, name, content):
    """Put the showrunner's rules back into taste-writers.md, whatever the Director saved."""
    if name != TASTE:
        return content, False
    block = markdown(all(slug))
    had = BLOCK_RE.search(content or "")
    if had and had.group(0).strip() == block.strip():
        return content, False
    if had:
        return (content[:had.start()] + block + content[had.end():]), True
    if not block:
        return content, False
    return (content or "").rstrip() + "\n\n" + block, True


def write_taste(slug):
    """Update the working copy now, so a rule counts before the next round starts."""
    current = projects.read_artifact(slug, TASTE)
    if current is None:
        current = "# What the showrunner loves and hates\n"
    new, changed = enforce_rules(slug, TASTE, current)
    if changed:
        projects.write_artifact(slug, TASTE, new)
    return new
