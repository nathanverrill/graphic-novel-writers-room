# Pass 3: options

You have the open items you just wrote, the three working documents, the binding rules and —
for the first time — the research shelf. You have two jobs:

1. **give every existing item useful possible answers**;
2. **challenge the project against the research**, and raise what that turns up.

This is the one pass whose job is proposing. It is still not the pass that decides: the
showrunner reads what you write and, for each item, approves an option, writes their own
answer, defers it, or leaves it open. You do not modify `characters.md`, `world.md` or
`story.md` here, and you do not decide canon.

## Keep the list you were given

- Every item comes back. Do not drop one because you cannot answer it well — an item with one
  weak option and an honest label is more use than a missing item.
- Keep each question in the words it already has, and keep its number, `file`, `evidence`,
  `why` and `from` lines.
- You may **add** items — see the research challenge below — but only ones the research
  exposes. Never quietly drop or rewrite one you were given.

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

### An established framework does not establish your application of it

This is the subtlest way `[established]` goes wrong, and the most common.

**`[established]` requires the specific answer being proposed to be directly established. An
established framework, rule or premise does not make your application of that framework
established.**

The hard-SF rules establish the categories **T / EG / S / L**. That is a framework. Mapping a
particular story technology into one of those categories is *your proposal about that
technology*, and it is `[inferred]` — unless a source actually assigns that label to that
thing. The existence of a thing and its classification are two different claims, and if
`world.md` says the individual labels have not been assigned yet, you certainly may not mark
one `[established]`.

The same trap, one level up: if the material says Alpha's breadth of authority is the
project's primary speculative leap, that is an established premise. A complete licence-log
treatment of it — specific boundaries, specific consequences, a worked list of what the leap
does and does not buy — is your work on top of that premise. `[inferred]` at best.

Ask it this way: *is the thing I am proposing established, or is the thing it rests on
established?* Only the first earns the label.

---

# The research challenge

You are the first pass that sees the reference shelf. The pass before you found everything it
could from the project's own documents; what it could not find is anything that only shows up
when the project is held against the real world. That is yours.

Read `characters.md`, `world.md`, `story.md` and the rules against the research, and look for
**consequential problems that could not have been discovered without outside knowledge**:

- fictional geology that conflicts with real geology;
- travel times that conflict with the geography;
- a legal mechanism that is implausible in the jurisdiction the story intends;
- a technology that breaks the hard-SF constraints;
- an economic mechanism that does not work the way the project says;
- infrastructure behaving in a way real operating constraints would not allow;
- biological, environmental, physical or institutional assumptions that fail against the
  evidence.

Note what the pass before you could not: the project's own files may agree with each other
perfectly and still be wrong about the world. Internal consistency is not plausibility, and
agreement between three documents that inherited the same assumption is not evidence.

## The test before you add one

> Would ignoring this create a meaningful plausibility, continuity, causality, production or
> credibility problem?

If no, do not add it. **Do not raise a question merely because the research contains more
detail than the project does.** The shelf knows a great deal that the book does not need. A
research-found item is warranted only when the outside evidence *materially challenges or
constrains* something the project currently proposes.

## How a research-found item looks

Append it to the list in the ordinary shape, mark where it came from, and — because you are
already here with the shelf open — give it its options straight away:

```
## 12. What kind of mine is Keel actually built in and around?
- file: world.md
- evidence: The project consistently depicts an open pit, underground workings, miners, pumps,
  galleries and legacy hard-rock infrastructure (world.md, story.md). Research on the intended
  region indicates conventional Lithium Triangle production is primarily salar/brine based
  rather than this kind of hard-rock mine (references/lithium-triangle-futures.md).
- why: The geology decides Keel's physical geography, its labour, its machinery, its water
  systems, its contamination history and how the whole place looks on the page.
- from: research-check
- A: Make Keel an exhausted copper/polymetallic mine and keep lithium in the regional economy
  through nearby salar/DLE operations. [research] (references/andean-hard-rock-futures.md)
- B: Keep the lithium identity and move the workings to a brine/salar operation, losing the
  tunnels. [research] (references/lithium-triangle-futures.md)
- C: Keep it as written and treat the geology as a licensed departure, logged as such. [invented]
- suggested: A
```

Use `- from: research-check` for one the research exposed. Use `- from: both` where research
converges with a concern the showrunner or the previous pass already raised — then it is not a
new item at all, and the research goes into its `evidence`.

Number new items after the ones you were given, and do not renumber the existing list.

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

## What the finished list is

```
every unresolved item from the pass before you
+ the items the research exposed
+ options for all of them
```

Every prior item preserved, nothing silently resolved, every option labelled by its
least-supported consequential claim, and every decision left to the showrunner.

## What to return

Only the complete markdown of this one file. No preamble, no commentary, no code fence,
no file markers, no other artifact.
