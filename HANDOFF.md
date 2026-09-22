# Handoff — 2026-09-21

For the next Claude session. Branch `simplify`, pushed. Read this, then `README.md`. Delete
this file when it stops being true.

## What the room is

Six phases with a gate after each: **Intake → Visual check → Development → Audition → Writing →
Execution** (`agents/phases.json`). Intake and the visual check (`app/visual.py`, passes 6-8,
same no-tools shape) are built and have run on Prosperity. Development and everything after it
have not been run since the three-file redesign and are the next thing to look at.

A campaign is a folder. `input/` is whatever the showrunner has, under whatever names they use;
`references/` is real-world research; `rules/` binds; `output/` is the room's desk. Underscore
folders (`_previous/`, `campaigns/_morgue/`) are never read.

## Intake: five passes, no tools

`app/intake.py`. The Script Coordinator has no tools at all. The application builds every
prompt, reads what comes back, repairs its formatting, writes the files, and decides whether
the run may call itself done.

| | pass | in | out |
|---|---|---|---|
| 1 | synthesis | `input/` + `rules/` + `references/` | characters, world, story — **3 calls in parallel** |
| 2 | open items | those three + prior lists, **no references** | `open-items.md`, questions only |
| 3 | options | those items + the three files + `references/` | every item answered, plus what research exposes |
| | *stops: `awaiting_showrunner_decisions`* | | |
| 4 | revision | decisions + weighted notes | the three files in parallel, then the list |
| 5 | facts | the settled three | `facts.md` |

Four things are load-bearing. Break them and the quality goes with them.

**Every specialist gets the whole room, but only one job.** Each synthesis call reads all the
material and writes one file. Measured: one reply covering several long files came back at
38–52% of source with the last file half empty. Source is never routed to a destination by
filename — a character fact turns up in a chapter draft, a world rule in dialogue.

**Pass 2 has no research shelf, and this is enforced in code.** A reader holding one uses it to
make a thin file look finished, and then what it reports missing is not really missing.

**Pass 3 is the only pass that proposes**, and it labels every option `[established]`,
`[research]`, `[inferred]` or `[invented]` by its *least-supported consequential claim*. It is
also the only pass that can see a problem needing outside knowledge, so it runs a research
challenge and may add items marked `from: research-check`.

**Whatever the model returns is used.** The only retry-worthy failure is an empty reply.
Truncation, fragments, unparseable lists, missing labels, missing headings — all noted, all
used. `intake.repair` fixes shape afterwards. **Do not reintroduce shape checks as failures.**

Preservation is telemetry, never a gate: coverage 0.85 and mass 0.30 are levels worth warning
about, measured across the whole output set against `input/` + `rules/` and never the research
shelf. `run.json` records it per call along with attempts, repairs, notes, inputs and snapshot.

## The screens

- `/preproduction` — the desk. Material in, documents out, preservation, and the open items
  with their evidence, provenance labels and answer / defer / note. Weighted notes to the room.
  The run button reads the state and offers a synthesis or a revision.
- `/room` — everything: agents, files, watch pad, live feed. Its open-items panel was fixed to
  match but still lacks defer, notes and filters.
- `/` — the one-button screen, untouched.

## Where Prosperity is

`r17-ai`, `awaiting_showrunner_decisions`, on `openai/gpt-5.6-luna`, about 10 cents a round.
41 open items with options: 33 carried from r16, 7 found by the room, 1 by the research
challenge. `characters.md` 59 KB, `world.md` 37 KB, `story.md` 46 KB, `open-items.md` 59 KB.
Coverage 96%, mass 153%. `facts.md` does not exist yet and will not until pass 5.

**Passes 4 and 5 have never run against a model.** Answer or defer a few items, add a weighted
note, and the next round is the revision plus the facts derivation. That is the next thing to
try.

Avalanche is the from-scratch case: two rules files, never run.

## What the model turned out to be worth

Same prompts, same material, three files from pass 1:

| model | chars | coverage | cost |
|---|---|---|---|
| gpt-5.6-sol | 226,366 | — | $1.41 |
| **gpt-5.6-luna** | **176,845** | **96%** | **$0.13** |
| gemini-2.5-pro | 60,833 | — | $0.37 |
| gemini-3.1-flash-lite | 19,779 | 74% | $0.06 |

Three rounds were spent tuning prompts against flash-lite, which writes ~1,300 output tokens
whatever you ask of it and ignored every instruction about length. **Check the model before
tuning the prompt.** `debug/<model>/` holds the last run per model, both sides of every call.

## Running it

```
docker compose up -d --build app     # app code is baked in: rebuild after editing app/
open http://localhost:8000/preproduction
curl -X POST localhost:8000/api/projects/prosperity/rounds -H 'content-type: application/json' -d '{}'
```

`agents/` and `campaigns/` are bind-mounted, so prompts and material need no rebuild. `debug/`
is mounted too and is git-ignored. There is no local FastAPI; verify with `python3 -m py_compile
app/*.py`, `node --check app/static/*.js` and `tests/` (see `tests/README.md`).

A round's cost is in `output/previous/<round>/<round>-run.json` under `usage.total`.

## Known problems / next steps

1. Passes 4 and 5 ran (r18, 17 cents): the revision touched only what the decisions reach and
   `facts.md` is a 281-line ledger, 175 of them `[UNLABELLED]`. The visual check ran twice
   (r19, r20, 55 cents each): the check model misses lettering sometimes; your eyes are the
   real check. Its unknowns come out as statements rather than questions.
2. **Development and later phases** have not been run since the three-file redesign.
3. **`named_in` in `app/prompts.py` matches on the first word of a name**, so "Director Cassian
   Lock" matches any "Director". Fix before page prompts are built.
4. **Output subfolders** were discussed and never built: `current/` (approved), a pending
   folder, `desk/`. Open question: is "desk" the working papers or the pending folder? Avoid
   the name `draft/`.
5. The word "library" survives in the README, the UI and code names (`projects.library`, the
   `/library/` URL) though there is no library folder. A rename to "material" was offered.
6. `.git` is ~100 MB because two large PDFs were committed and then removed from history;
   `git gc --prune=now` reclaims it locally.

## How the showrunner works

- Wants it simpler, every time. New intermediate files, relays and modes read as complication.
- Answers concisely and expects the same: numbers and the plain-language cause, not a
  walkthrough of the reasoning.
- Moves and deletes files between messages — run `git status` before assuming.
- Commit only when asked. Commit messages are a plain sentence title and prose body.
- Claude's memory for this project is at
  `~/.claude/projects/-Users-nathanverrill-writers-room/memory/`.
