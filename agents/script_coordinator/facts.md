# Pass 5: facts

The project is settled for now. `characters.md`, `world.md` and `story.md` carry the
showrunner's decisions, and what is still open is on the open-items list. Your last job is to
read those three files and write `facts.md`: the continuity ledger of what the project
currently establishes.

This is the only pass that writes this file, and it comes last on purpose. A ledger written
while the project was still moving would be a list of things that turned out not to be true.

## Who reads it and why

The Continuity Editor reads it beside the book, line by line, to catch what a page gets wrong.
The Director reads it when deciding what belongs in a formal bible. Nobody writes *from* it —
the writing comes from the three files. So every line has to be checkable on its own, without
reading the line above it and without opening another file.

## What a fact is

A fact belongs here when a later page could contradict it:

- an age, a date, a point in the chronology, how long ago something happened;
- who is related to whom, who works for whom, who knows whom;
- where something is, how far it is from something else;
- who owns what, who controls what;
- a quantity, a price, a measurement, a capacity;
- what an institution does and what it is called;
- how a system, a device or a process works — and what it cannot do;
- an event that definitely happened;
- an outcome that is locked;
- what someone or something is capable of, and the limits on it.

## What is not a fact

These belong in the three files, and putting them here makes the ledger unusable:

- personality, temperament, what someone is like;
- voice, how someone talks, sample dialogue;
- emotional tendencies and tells;
- appearance, except where a specific detail is checkable (a missing finger, yes; "weathered
  and tired", no);
- stylistic observation of any kind;
- anything still unresolved — that is the open-items list, not this;
- real-world research that has not become part of the project.

## Not a mirror of the rules

`rules/` constrains how the book is made. `facts.md` constrains what the book may contradict.
Some rules settle a fact. Most do not.

```
Rule: Keep the science grounded.
facts.md: nothing — it shapes the writing, it settles nothing in the world.

Rule: EVOKE is not a formal organization.
facts.md: - EVOKE is not a formal organization. (rules/<file>)
```

If a rule tells a writer how to work, it produces no line. If it tells them what is true, it
produces one.

## The shape

A flat list under headings by topic — a character, a place, a system, the timeline, money,
technology. Not prose. One fact per line:

```
## Ana Rey

- [T] Ana Rey is 61. (characters.md)
- [FIXED] Ana Rey runs the Keel pump station. (rules/decisions.md)

## The Keel pumps

- [T] The pumps draw from 400 m. (world.md)
- [EG] Every pump in Keel is imported. (world.md)
- [CONFLICT] story.md has the station failing in chapter 2; world.md has it running
  throughout. (story.md / world.md)
```

Each line carries:

- **the tag** — the project's own label where it has one (**T** truth, **EG** educated guess,
  **S** speculation, **L** licence), **FIXED** for anything a rule or a decision settles,
  **CONFLICT** where two files still disagree, **UNLABELLED** for a bare fact from a file that
  grades its material elsewhere;
- **the fact**, in one sentence;
- **the source**, in parentheses: which of the three files it came from, or the rules file.

## Length

Be thorough. This file can be longer than any of the three it comes from, and usually should
be: it is every checkable statement they make, pulled out and listed. A fact that is in one of
the three files belongs here too.

Where two files still disagree about something and the showrunner has not settled it, the
`[CONFLICT]` line is the useful thing — do not pick a side, and do not leave it out.

## What to return

Only the complete markdown of this one file. No preamble, no commentary, no code fence,
no file markers, no other artifact.
