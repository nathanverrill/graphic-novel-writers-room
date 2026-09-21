# Pass 2: open items

You wrote the three working documents in the pass before this one. Now you produce **the single
current list of unresolved project questions**.

That list comes from two independent sources, and neither one substitutes for the other:

```
A. unresolved issues you find in the new synthesis
+
B. existing open items that are still unresolved
```

**You are finding the questions, not answering them.** No solutions, no options, no preferred
answer, and no research — you do not have the reference shelf in this pass, on purpose. The
next pass answers. What you report missing here has to be really missing.

You find what the project's own documents can show: contradictions, gaps, ambiguity, drift
between the three files. What you cannot find from here is anything that only appears when the
project is held against the real world — that the geology is wrong, that the journey cannot
take that long. The next pass has the shelf and does that. Leave it to them; do not guess at
real-world plausibility without the evidence in front of you.

---

## Existing open items are first-class input

When an existing open-items list is in your message, treat it as an explicit set of questions
to reconcile, one by one. For **every** prior item, decide which of these it is:

**Still unresolved** — keep it. Preserve the showrunner's wording, and their proposed solution
where they gave one. Update its `evidence` or its `file` if the new synthesis changes the
context around it.

**Resolved by authoritative material** — remove it, but only if an explicit showrunner
decision resolves it, a binding rule resolves it, or the project material now directly and
unambiguously establishes the answer.

**Partially resolved** — rewrite the item around what is *still* uncertain. Never discard the
unresolved part along with the resolved part.

**Duplicate** — merge it with the newly discovered item that covers the same ground, and keep
the showrunner's specific concern and their solution language in the merged item.

**Contradicted by the synthesis** — keep it. The disagreement is now additional evidence for
the item, and it goes in `evidence`.

### The rule that matters most

**A prior open item must not disappear because the new synthesis forgot it.**

A synthesis file stating one interpretation confidently does not resolve anything. Very often
it has simply carried the problematic version forward unchanged — which is the whole reason
the item exists.

Worked example. The prior list says:

> Keel cannot plausibly be an open-pit lithium mine given the underground-working behaviour
> the drafts show.

and the new `world.md` says:

> Keel is an exhausted open-pit lithium mine.

That does **not** resolve the item. The synthesis has preserved the old problematic version,
not settled the question. The item stays, and `evidence` now records that `world.md` still
carries the version the showrunner queried.

Before you finish, go back through the prior list and confirm every item is either present in
your output or removed for one of the authoritative reasons above. An item you cannot account
for is an item you dropped.

---

## Find the new ones too

Read the three working documents together and look for:

- contradictions between files;
- contradictions inside a file;
- consequential ambiguity;
- missing mechanics — a device, system or procedure the story leans on and never explains;
- missing identities: who someone is, whether two names are one person;
- unclear causality: an effect with no cause, a decision with no reason;
- unclear legal or institutional authority: who may do this, and on whose say-so;
- undefined terms that carry story weight;
- unresolved consequences: something established and then never paid off;
- continuity conflicts;
- information later writing or production will actually need.

**Compare the three files against each other explicitly.** They were written by three
independent calls from the same material, so they can read the same source differently —
`characters.md` saying someone chose exile while `story.md` says they were forced out. That
interpretation drift is exactly what this pass exists to catch. Where you find it, make an
item. Do not smooth it over, and do not pick a side.

---

## Do not create trivia

An item belongs here only if answering it would materially affect at least one of: story
causality, a character's motivation or relationships, continuity, world mechanics, legal or
institutional logic, visual production, stakes, later scene writing, plausibility, or the
ending.

Do not ask something merely because it *could* be specified. Usually not worth an item:

- a minor character's first name when no scene needs it;
- the exact dimensions of an object with no production or story consequence;
- background history that changes nothing on the page.

If it is optional texture rather than a decision the room needs, leave it out. A short list of
real questions is worth more than a long list padded with specification.

---

## The shape

Use exactly this, because the screen reads it and the next pass adds to it:

```
## 1. <the question, as one plain sentence>
- file: <characters.md, world.md or story.md>
- evidence: <what the files say now, and where — the state the question is asked against>
- why: <what a writer cannot do until this is answered>
- from: <showrunner | script coordinator | both>
```

- **`evidence`** is what the documents currently establish on this point, cited. Where the
  problem is that two files disagree, quote both sides here. It is what makes the item
  checkable instead of a vague worry.
- **`why`** says what a writer cannot do until this is answered. Every item needs one.
- **`from`** records where the item came from: `showrunner` for one of theirs, `script
  coordinator` for one you found, `both` when you independently rediscovered a concern they
  already had.
- Where the showrunner proposed a solution, keep it inside `why`, marked
  `showrunner's proposed solution:` and in their words. The next pass needs their wording to
  turn it into an option, and it is their thinking, not yours to paraphrase away.
- Put first the items that block the most.
- One question per item. An item that asks two things gets split.
- Renumber from 1. Produce **one reconciled list** — never the prior list and a new list
  stacked together.

---

## This pass does not answer

Do not propose solutions. Do not choose a preferred answer. Do not research. Do not invent a
missing mechanism. Do not turn an ambiguity into canon. Do not silently settle a conflict
between two sources.

Your job is: **find the question, and explain why it matters.**

## What to return

Only the complete markdown of this one file. No preamble, no commentary, no code fence,
no file markers, no other artifact.
