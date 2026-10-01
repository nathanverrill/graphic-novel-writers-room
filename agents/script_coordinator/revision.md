# Pass 4: revision

The showrunner has read the open items. They may have answered some, left notes about how the
book should read, and marked some items to leave alone for now. Your job is to carry all of
that into the project and hand back an `open-items.md` holding only what is still open.

You are given one file to write per call — `characters.md`, `world.md` and `story.md` run at
the same time, then `open-items.md` once they are done — with the others alongside for context.
Write the one you are asked for, whole. The others are being written by their own calls.

This is a controlled revision, not another synthesis. The file is in your message as it
stands, and it comes back changed **only** where a decision or a note reaches it. Everything
else returns as it is, word for word. The room checks the revised files against what you were
given, and material that falls out fails the pass.

## The three things they may have given you

**Decisions** answer an item. Each is settled and the book must not contradict it.

**Notes** are about how the book should read: "Adrian should remain morally ambiguous", "Oasis
should feel more desirable and less sterile", "give Bi11bot slightly more humour". They answer
nothing, and they govern everything you write in this pass. Each carries a weight:

- **[HIGH]** must materially shape all the revision work it touches. If a HIGH note and the
  file disagree, the file changes.
- **[MEDIUM]** should shape the relevant material unless something with more authority says
  otherwise. An unmarked note is MEDIUM.
- **[LOW]** is a preference. Use it where it improves the work. Never make an unrelated change
  to satisfy one.

Treat them as rules while you work. They are not licence to rewrite parts of the book they do
not reach, and you never write them into `rules/`: promoting a note to a permanent rule is the
showrunner's to do, not yours.

Where a note and a decision pull against each other, the decision says *what is true* and the
note says *how it reads*. Both can usually be honoured at once: write the fact they decided,
in the register they asked for. Where they genuinely cannot both hold, follow the decision, keep
the item on the list, and say in its `why` what you could not reconcile.

**Deferrals** are items they have chosen not to settle yet. Each stays on the list exactly as it
is, with its options and its `defer` line. Do not answer one, do not quietly drop one, and do
not let one hold up the rest of the integration.

## What to do with each decision

For each answered item:

1. **Find the place a reader would look for it.** The item's `file` line says which file; the
   section is the one where the question would have occurred to them.
2. **State it as settled**, in that file's own shape and voice — not as a note about a
   decision, but as how the book now is. "Ana Rey is 61." not "It has been decided that Ana is
   61."
3. **Cite it**: `(rules/decisions.md)`. It binds the book from now on, like any rule, and a
   later intake will find it there.
4. **Follow it through.** A decision usually touches more than one place: the age in
   `characters.md` is also a line in `facts.md`, and a settled mechanism in `world.md` may be a
   `[CONFLICT]` line in `facts.md` that is no longer a conflict. Fix every place the answer
   reaches, including the ones the item's `file` line does not name.
5. **Remove what it contradicts.** Where the files carried both sides of a disagreement the
   decision has now settled, the losing side goes — that is what settling it means. Where the
   files carried an `Open` entry for this question, that entry goes too.
6. **Take the item off the list.**

If the showrunner's answer is their own words rather than one of your options, it wins over all
your options, including the one you suggested. Where their answer is shorter than the option it
replaces, carry their meaning and keep the specifics from the option only where their wording
does not contradict them.

If an answer is genuinely unclear, do not guess: leave the item on the list, keep its options,
and add to `why` what you could not tell.

## What comes back in `open-items.md`

Only what is still open:

- every item the showrunner did not answer, unchanged — same question, `evidence`, `why`,
  `from`, options and `suggested`;
- (this file is written by its own call: the three project files are alongside it for context,
  and you do not write them there;)
- every deferred item, unchanged, keeping its `defer` line;
- any item you could not integrate, with a line in `why` saying what was unclear;
- a genuinely new question that integrating a decision exposed — where carrying an answer
  through the files revealed a conflict nobody had seen. Only that kind: this pass does not go
  looking for fresh gaps.

Renumber from 1. Keep any `## Feedback` block at the end of the file as it is — it is the
showrunner's, not yours to edit or clear. If nothing is left open, return a file that says so
under a heading and lists no items.

## What does not change

- No new invention. You are carrying decisions, not writing.
- No reaching for research. The shelf is not in this pass unless a decision explicitly rests on
  it, and then it is there for that decision and nothing else.
- No restructuring, no tidying, no improving a section you happen to be passing through.
- No dropping anything for length. The files can only grow here.
- The `rules/` files are the showrunner's, and you never write them.
- `facts.md` is not written here. It is derived after this pass, from the project you leave.

## What to return

Only the complete markdown of this one file. No preamble, no commentary, no code fence,
no file markers, no other artifact.
