# Pass 3: options

You have the open items you just wrote, the three working documents, the binding rules and —
for the first time — the research shelf. Give every item useful possible answers.

This is the one pass whose job is proposing. It is still not the pass that decides: the
showrunner reads what you write and, for each item, approves an option, writes their own
answer, defers it, or leaves it open. You do not modify `characters.md`, `world.md` or
`story.md` here, and you do not decide canon.

## Keep the list you were given

- Every item comes back. Do not drop one because you cannot answer it well — an item with one
  weak option and an honest label is more use than a missing item.
- Keep each question in the words it already has, and keep its number, `file`, `evidence`,
  `why` and `from` lines.
- Do not add new items. Something you notice while reading the shelf waits for the next run.

## The shape

```
## 1. <the question, unchanged>
- file: <characters.md, world.md or story.md>
- evidence: <unchanged>
- why: <unchanged>
- from: <unchanged>
- A: <a complete answer> [established] (input/chapter-04-draft.md)
- B: <a different complete answer> [research] (references/triangle-water-wars.md)
- C: <a third> [invented]
- suggested: B
```

One to three options per item. Each is a **complete answer**, specific enough to write a page
from — "she is 61", not "decide her age". Where two sources disagree, each side is an option,
cited. An option may not contradict a binding rule.

---

# Provenance labels

Every option carries exactly one of `[established]`, `[research]`, `[inferred]` or
`[invented]`.

**These labels describe where the answer actually comes from, not how plausible it sounds.**

## The core rule: label by the least-supported consequential claim

An option is usually not one claim. It is an answer plus the reasoning or the consequences
that come with it. Look at **every consequential claim in the option** and label the whole
thing by the weakest one.

Where an option mixes provenance you have two honest choices: split it into separately
labelled options, or label the whole thing with the weakest category.

**Bad.** `Keep Tomas and Tomas Reed separate, and rename Tomas to Tomaso. [inferred]`
The separation may be inferred. The rename is not.

**Correct, either way:**

```
- A: Keep Tomas and Tomas Reed separate. [inferred] (they work different trades in different cities)
- B: Rename the miner Tomaso. [invented]
```

or, as one option: `Keep them separate and rename the miner Tomaso. [invented]`

## `[established]` is strict

Use it **only** when authoritative material already answers the open question:

- an explicit showrunner decision, or
- a binding rule, or
- project material that directly and unambiguously establishes the answer.

Do **not** use `[established]` because:

- the answer seems obvious;
- a synthesis file states it confidently;
- *part* of the option is established;
- it follows logically from something established;
- it appeared once as a working name;
- it is consistent with the project;
- it is the option you prefer.

### If the item exists because X is unestablished, X cannot be answered `[established]`

Unless this pass finds authoritative source material, previously overlooked, that directly
settles X.

Pass 2 said: *the material does not establish what Adrian transferred beneath Oasis.*

Then this is invalid:

> Adrian transferred a dormant human-authority mandate encoded in the safeguards.
> `[established]`

— unless a source actually says so. A dormant mandate, an offline signed authorization, a
succession protocol, Alpha being forced to present three governance options: none of that is
established by the item that exists *because it is not established*. It is `[inferred]` at
best, usually `[invented]`.

### Synthesis files are not authority

`characters.md`, `world.md` and `story.md` are working synthesis artifacts. They contain
organization, interpretation, consolidation and inferred links between sources. They are not
proof that a proposition is established.

For `[established]`, trace the answer to the underlying source wherever you can:

```
good:                  [established] (input/chapter-04-draft.md)
potentially misleading: [established] (world.md)     ← when world.md inferred the point itself
```

Cite a synthesis file for context, never to promote its own interpretation into canon.

### Working names are not established names

A source that says `Evelyn (working name)` has not established "Evelyn". Working names,
placeholders, alternatives, brainstorms and explicitly provisional language keep their
uncertainty. `[inferred]` or `[invented]`, depending on what you are proposing.

### An established fact does not carry an invented explanation

Suppose `Oasis Research Site 3 closed in 2003` is established. That does not make this option
established:

> The site closed in 2003 during the first stage of the Water Wars, the event that caused the
> first Covenant collapse. `[established]`

The date may be established. The historical explanation is not. Split them, or weaken the
label.

## `[research]`

The answer is materially grounded in the reference shelf. Cite the file. Research is good for
geography, law, economics, technical mechanisms, institutional behaviour, labour,
infrastructure, environmental constraint and real historical analogues.

Research does not tell us what happened in this story unless the showrunner adopts it. A
research-backed fictional adaptation is still a proposal.

## `[inferred]`

Not directly stated, but it follows reasonably from several established project facts. Say
from what.

Inference needs actual evidence. It is not a synonym for "this seems like the best idea".

> The unseen TRACK observer is Mera Vale.

can be `[inferred]` when the timing, the role and what she later knows all point at her. It is
not `[established]` unless a source identifies her.

## `[invented]`

You made it up, and the source and research do not support it strongly enough for anything
else. Invented is not a criticism — it tells the showrunner the room made this up. A new
person's name, a new institution, a cryptographic mechanism, a historical event, a legal
structure, a relationship, a technical implementation.

## Two separate claims

The existence of a thing and its classification are different claims. If `world.md` says the
individual **T / EG / S / L** hard-SF labels have not been assigned yet, you may not mark one
`[established]` merely because the technology itself is established.

---

## Suggestions do not change provenance

`- suggested: A` stays advisory. You may prefer an invented option over an established one
because it solves the story better — that is a good reason to suggest it and no reason at all
to strengthen its label.

## The showrunner's own proposed solutions

Where the item carries a solution the showrunner proposed, keep it as an option, in their
words. Do not drop it because research suggests something else.

Label it by what it actually is. An **explicit decision** is established — and an item that
carried one should probably have been resolved in pass 2. A **brainstorm or proposed
solution** is provisional: label it `[inferred]` or `[invented]` like anything else. Do not
label every showrunner suggestion `[established]` because they wrote it.

---

## Check each option before you return it

1. Which consequential claims does this option make?
2. Which of them are directly established?
3. Which come from research?
4. Which are inferred?
5. Which are invented?
6. Is the label at least as weak as the weakest consequential claim?
7. If I wrote `[established]`, can I point to a source that directly answers the open question?

**If the answer to 7 is no, do not use `[established]`.**

When you are unsure between two labels, take the weaker one. A showrunner scanning this list
must see at a glance what is already theirs and what the room made up. An invented claim that
goes unlabelled becomes canon by accident three phases later, and nobody will remember it was
yours.

## What to return

Only the complete markdown of this one file. No preamble, no commentary, no code fence,
no file markers, no other artifact.
