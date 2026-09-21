# Handoff — 2026-09-21

For the next Claude session. Branch `simplify`, pushed to `origin/simplify`. Read this, then
`README.md` (the phase table at the top and "The library" section). Delete this file when it
is no longer useful.

## What the room is now

Five phases, a gate after each: **Intake → Development → Audition → Writing → Execution**
(`agents/phases.json`).

- **Intake is a five-pass pipeline, not an agent loop** (`app/intake.py`, 900 lines).
  No tools; the app builds every prompt, parses a file envelope, validates, retries, writes.
  - **Pass 1, synthesis** — `input/` + `rules/` + `references/` -> `characters.md`, `world.md`,
    `story.md`. **Three calls IN PARALLEL** (`Intake.parallel`, ThreadPoolExecutor), each given
    all the material and its own destination guide. `facts.md` is NOT written here. Each call
    validates and retries independently; only the set-level guard reruns the whole pass.
  - **Pass 2, open items** — those three + their own `input/open-items.md` -> `open-items.md`,
    questions only. **No references, enforced in code.**
  - **Pass 3, options** — those items + the three files + `references/` -> options labelled
    [established] / [research] / [inferred] / [invented].
  - Round ends `awaiting_showrunner_decisions`.
  - **Pass 4, revision** — decisions + weighted notes + deferrals -> the three files in
    parallel, then `open-items.md` last so it is reconciled against the revised files.
  - **Pass 5, facts** — the settled three files -> `facts.md`. Round ends `ready_for_review`.
  - **No filename is required.** `projects._material` enumerates every `.md`/`.txt` in the
    campaign; the model works out what each holds. Only `input/open-items.md` is reserved
    (`Intake.reserved`), routed to pass 2. `input/_previous/` and `_`-folders are never read.
  - **Weighted notes** ([HIGH]/[MEDIUM]/[LOW], unmarked = MEDIUM) in a `## Feedback` block or a
    per-item `- feedback:` line. `intake.weighted` parses them; pass 4 gets them as rules for
    that run. Never written to `rules/`.
  - **Preservation is telemetry** (`preservation`, `preservation_warnings`), measuring
    `input/` + `rules/` — never the shelf — across the whole output set. Coverage 0.85 and mass
    0.30 are levels worth a warning, NOT gates: nothing is discarded and no pass is rerun. Off
    below 8 KB of source. `ROUNDS` and the shortfall-feedback plumbing are gone.
  - **Retries** carry every problem seen so far, because told one thing at a time the model
    fixes a heading and comes back shorter.
  - **No envelope.** Every call writes one file, so the reply is the document. `intake.clean`
    strips a fence, a stray `<<<FILE:>>>` marker or a "Here is..." preamble.
  - **Whatever the model returns is used** (showrunner's call, 2026-09-21, emphatic). The ONLY
    thing that fails a call and earns a retry is an empty reply. Truncation, fragments,
    unparseable item lists, options with no source label, refusal-shaped text, missing headings
    — all notes, all used. `validate` returns `(problems, notes)` and `problems` is only ever
    `["nothing came back"]`. Do not reintroduce shape checks as failures.
  - `OUTPUT_TOKENS = 64000` and `agent.json` `max_tokens` 64000, near the model ceiling, so a
    long file is not cut off.
  - **Formatting is repaired, never retried.** `intake.repair`
    adds a missing title, demotes character names from `##` to `###` and inserts the
    `## Characters` wrapper, rewrites bolded field lines (`- **file:** x`) so `openitems.parse`
    can read them, and numbers unnumbered items. `intake.shape_notes` records what it could not
    fix without failing the call. `validate` now returns `(problems, notes)`: only nothing-came-
    back, an apology, a fragment, `finish_reason: length`, an unparseable items list, or a pass
    that did not do its job (pass 3 with unlabelled options) are worth another call.
    `items_problems` demotes missing `why` and `suggested` to notes.
  - **A failed call keeps its work**: the fullest reply is written to the round folder as
    `<name>-rejected.md` before the error is raised, so nothing the model produced is lost.
  - **Per-call output budget** `OUTPUT_TOKENS = 30000` via a new `max_tokens` argument to
    `llm.chat`, so one file never eats another's allowance. `usage.CallLogger` got a lock.
  - **Snapshot** (`Intake.snapshot`) hashes the exact source set; all parallel calls record it,
    so a set of outputs can never be half from one state of the material and half from another.
  - **Caching**: system prompt and payload prefix are byte-identical across the three synthesis
    calls (121,496 chars on Prosperity); only the tail differs.
  - **Soft input ceiling** `SOFT_INPUT_CHARS = 700_000`, warned not enforced.
- **Development** works in the same three files: Director owns `brief.md` + `world.md`,
  Plotter owns `story.md` (beats, structure and page plot in one file), Character Designer
  owns `characters.md`. There is no `research.md`, `bible.md` or `outline.md` any more.
- Agents know only their craft guides and the prompt the room builds. No agent file names a
  campaign file. Material is named by its real path, `campaigns/<campaign>/<folder>/<file>`.
- A campaign reads only its own folder. The shared `evoke` campaign, Figma support and
  `scripts/` are gone. Underscore folders (`_previous/`, `campaigns/_morgue/`) are never read.
- The pitch is optional material at `input/pitch.md`. Nothing in `output/` steers intake.

## Built 2026-09-21 (afternoon): the intake rewrite

Two specs, one after the other: first a tool-free two-call pipeline, then the four-pass shape
below. What changed from the state described further down:

1. **`app/intake.py`** — the whole pipeline (598 lines). `parse_envelope` / `validate` /
   `items_problems` / `preservation` / `Intake.call` (retry the same pass) / `synthesize` /
   `integrate`. `room.run_roles` dispatches to it on `"pipeline": "intake"` in
   `agents/agents.json`; every other role still runs `Agent`.
2. **Kept-whole is gone, by the showrunner's decision, and is not the fallback.**
   `projects.showrunner_file`, `projects.with_additions`, `projects.ADDED` and `Agent.kept` are
   deleted. Pass 1 re-emits the showrunner's four `input/` files whole — the r01 failure shape
   — and the showrunner ruled out going back to additions-only. What guards it instead is
   `intake.preservation`, which is measured, logged in `run.json` and retried against. If the
   guard turns out to be too loose or too tight, tune `MIN_COVERAGE` / `MIN_MASS` /
   `MATURE_CHARS` rather than reinstating additions.
3. **The blind list is gone**; `Agent.held_back` / `Agent.fuse_open_items` deleted. Their
   `open-items.md` is kept out of pass 1 and reconciled in pass 2. Blindness now lives in a
   different place and for a different reason: pass 2 cannot see `references/`.
4. **The quality-check section is gone** — it belonged to the additions mechanism.
5. **`references/` is its own kind** (`projects.REFERENCES`), so research can be held out of
   call 1 and handed only to call 2. It used to read as `input`.
6. **`Agent` lost all its library code**: `library()`, `kept()`, `held_back()`,
   `fuse_open_items()` and the `campaigns/` branches of `read_artifact`. No role has a tool
   loop over the material any more.
7. **Guides split per pass**: `role.md` + `craft.md` go to all four; `synthesis.md`,
   `open-items.md`, `options.md` and `integration.md` each go to their own pass only
   (`intake.GUIDES`). Each pass is told one job.
15. **Pass 3 research challenge** (the eighth spec, 2026-09-21): pass 3 may now ADD items, not
    just answer them. It is the first pass with the shelf, so it is the only one that can catch
    a problem needing outside knowledge — the Keel open-pit-lithium-vs-salar-brine case is the
    worked example in `options.md`. New items are marked `- from: research-check` (or `both`
    where it converges with an existing concern), numbered after the existing list, and given
    options immediately. Gated by a materiality test, not by detail. The old "do not add new
    items" restriction is removed from the guide and from `options_message`.
    Pass 2's guide now says explicitly that real-world plausibility is not its job.
    **Note on the pass 2 payload**: `input/open-items.md` no longer exists and should not be
    restored — the old 23 items were asked against material that has since been replaced. The
    showrunner-authored path is still supported (own section, `Source: input/open-items.md`)
    but the normal lifecycle is that pass 2 writes the list, the showrunner edits it in place,
    and the next run reconciles against the desk copy.
14. **Pass 2 reconciliation + strict provenance** (the seventh spec, 2026-09-21, after r15):
    `open-items.md` rewritten: prior items are first-class input with five named dispositions,
    "a prior item must not disappear because the new synthesis forgot it" with the Keel worked
    example, explicit cross-file drift comparison, a do-not-create-trivia section, and
    showrunner solutions preserved in `why`. `options.md` rewritten: [established] is strict
    with a list of bad reasons, an item that exists *because* X is unestablished cannot be
    answered [established], synthesis files are not authority for their own inference, working
    names are not established names, an established fact does not carry an invented
    explanation, existence and classification are separate claims, suggestions do not change
    provenance, and a seven-question self-check.
    **Code change**: `open_items_message` now supplies the prior list from BOTH
    `input/open-items.md` and the desk's own `open-items.md` — the showrunner removed open
    items from `input/`, so the desk copy is where their edits live.
    **Tests**: `scratchpad/test_prompts.py` asserts all seven required rules are in the text
    the model actually receives. Prompt-content only — no new gates, no shape checks.
13. **Anti-synopsis + provenance tightening** (the sixth spec, 2026-09-21, after reading r10):
    `synthesis-story.md` gained "Drafts: keep them at the granularity they arrived in" — do not
    collapse a page-by-page draft into a chapter synopsis — and all four synthesis guides now
    carry "your output is a working source document, not a summary". `options.md` gained the
    **least-supported consequential claim** rule with three worked bad/better examples, because
    r10 labelled mixed options by their strongest part. Telemetry gained `classify()`,
    `dropped_by_kind`, `dropped_counts` and `substantive_coverage` (coverage ignoring craft
    vocabulary) — observational only, no new gates. On r10's dropped list, 12 of 24 terms were
    craft vocabulary from hard-sf-rules.md rather than story material.
12. **Prompt cleanup + guard-to-telemetry** (the fifth spec, 2026-09-21):
    `synthesis.md` replaced wholesale with the shared contract only — what the pass is,
    authority order, synthesize/do-not-resolve, research discipline, where a thing goes, the
    `## Open` section, citations, what to return. All per-destination schema lives only in
    `synthesis-characters.md` / `-world.md` / `-story.md`. The preservation guard became
    telemetry. Architecture untouched.
9. **New settings and plumbing**: `use_references_during_synthesis` in
   `review.DEFAULT_SETTINGS` and the settings API; `mode` on `POST /api/projects/{slug}/rounds`;
   `Run.mode` / `Run.awaiting` in `room.py`; a `- decision:` line is now parsed by
   `openitems.parse`, so an item can be settled by hand in `output/open-items.md`; the UI shows
   the two new run states in words.
11. **Five passes, per-file calls** (the fourth spec, 2026-09-21): `facts.md` moved to its own
    final pass and out of synthesis; pass 1 split into 1A/1B/1C and pass 4 into 4A-4D;
    `integration.md` renamed `revision.md` and a new `facts.md` guide written; weighted notes;
    no required input filenames and `.txt` support; run states `synthesizing` /
    `identifying_open_items` / `generating_options` / `awaiting_showrunner_decisions` /
    `revising` / `deriving_facts` / `ready_for_review`. `mode` is now "synthesis" or
    "revision"; "integration" still accepted.
10. **Creative-first pass** (the third spec): the references default flipped to true, the guard
    taught to ignore research, human feedback and deferral made first-class, `ready_for_review`,
    `human_modified` and per-pass inputs added. `openitems` gained `note_on`, `set_feedback`,
    `general_feedback` and item `status`; `POST /open-items/{n}` now takes `feedback` and
    `defer` as well as `answer`, and there is a new `POST /open-items-feedback`.
    **The open-items file shape was deliberately left as it is** — `- file:` / `- why:` /
    `- A:` lines rather than the `### Option A` headings the spec sketches — because
    `openitems.parse`, both screens and the answer API all read the line shape, and the spec
    calls its own version "typical structure". An `- evidence:` line was added to carry the
    "current evidence" the spec asks for.
8. `agent.json`: `max_tokens` 32000 -> 60000, because four whole files come back in one reply.
   `max_steps` and `references` no longer apply to this role.

Sizes for Prosperity, references off: 1A/1B/1C ~31k tokens each, pass 2 ~36k, pass 3 ~89k —
~217k tokens over 5 calls for a synthesis round. The guard's floor is now 47,418 chars across
the three files (source 86,215 after alpha.md was moved to `_morgue`).

**Run history, all before the five-pass rewrite — read this before tuning anything:**

| round | attempt 1 | 2 | 3 | outcome |
|---|---|---|---|---|
| r04 | 38% | broke a heading | 32% | failed |
| r05 | 39% | 45% | 44% | failed |
| r06 | 45% | 52% | 45% | failed |

All three failed pass 1 on mass, with coverage passing (0.82-0.87). Diagnosis, in order:
(a) `finish_reason: stop` every time, 12-14k output tokens of a 60,000 budget — never a token
limit, never a masked error; (b) `craft.md` had a Length section saying "write as much as the
material earns **and no more**", left over from the additions-only design — removed, and the
showrunner then removed the length line in `role.md` too; (c) retries saw one problem at a time
and oscillated — fixed; (d) `rules/alpha.md`, a 22 KB craft skill, was inflating the
denominator — the showrunner moved it to `campaigns/_morgue/alpha.md` and added a 5 KB
`input/alpha-notes.md`. **The real cause was the single reply**: r05's per-file breakdown was
characters 92% of its source, world 58%, story 49%, facts 45% — it writes the first file
properly and thins out. That is why pass 1 is now one call per file.

Tested with a fake provider on a throwaway campaign (the script is in the session scratchpad,
not in git): passes 1-3 and their material split, the guide split, pass 2 having no references,
options-without-labels rejected, a bare list accepted at pass 2 and rejected at pass 3, the
preservation guard refusing a 25%-mass summary while passing a fully reorganized set,
`use_references_during_synthesis`, pass 4 end to end including mode auto-detection both ways, a
hand-written `- decision:` line, pass 4 refusing to lose material, and a first pass that never
validates stopping the run. There is still **no round against a real model**.

## Built earlier that day, in order

1. Researcher → Script Coordinator; Research → Intake; three shared files; `drafts/` as its
   own folder kind.
2. Hard-coded file references removed from `agents/`; Figma removed; `evoke` and its scoping
   code removed (`app/projects.py` now has one `_material()` walk).
3. **Open items** (`app/openitems.py`): the Script Coordinator writes `open-items.md` with
   proposals A/B/C and a suggestion; both screens (`/` and `/room`) show them under the intake
   gate; an answer is saved to `campaigns/<slug>/rules/decisions.md`; the next intake run states
   it as FIXED and drops the item. API: `GET/POST /api/projects/{slug}/open-items[/{n}]`.
4. Character lookup for page prompts moved from `app/thumbnails.py` to `app/prompts.py`; it
   accepts `### NAME` under `## Characters` and `## Name` under `# Characters`.
5. **Intake keeps the showrunner's files whole** (`projects.showrunner_file`,
   `projects.with_additions`, `Agent.kept` in `app/agent.py`): if `input/` holds
   `characters.md`, `world.md`, `story.md` or `facts.md`, it goes onto the desk word for word
   and the agent's output is appended under `<!-- added at intake -->` / "Added at intake".
   Code drops any added line already in the showrunner's file, because the agent hands the
   whole file back whatever it is told. The user confirmed this is right: those files are
   improved outside the room, so intake's additions should be minimal.
6. **Blind open items, then a join** (`Agent.held_back`, `Agent.fuse_open_items`): if `input/`
   holds the showrunner's own `open-items.md`, the Script Coordinator cannot see it during its
   pass (left out of the prompt, refused by name), so its list is its own reading. One more
   plain call then gets both lists and writes the joined `open-items.md`: every item of
   theirs in their words and in full, their solutions first, its proposals added, its extra
   items after, each with a `- from:` line (showrunner / script coordinator / both) that both
   screens show. A joined list that does not parse is discarded and its own list stands.
7. **Quality check**: for files the showrunner wrote, the additions carry a "Quality check"
   section — where a writer would stumble, quoted, never rewritten.
8. **Missing files**: an agent that calls finish, or just stops, with outputs unwritten is
   asked once for the rest.
9. **Provider errors inside a 200** (`llm._error_inside`): OpenRouter delivers upstream
   timeouts and rate limits as an empty message with `finish_reason: "error"`. `llm.chat` now
   waits and retries twice, then raises. Before this they read as an agent that said nothing.

## Prosperity right now

- Material: four extraction files in `input/` (the user writes these outside the room and is
  making them richer), ten files in `references/`, `rules/alpha.md`, `rules/hard-sf-rules.md`.
  All draft scripts are in `drafts/_previous/` on purpose — out of reach. Older extraction
  files are in `input/_previous/`.
- Also in `input/`: the showrunner's own `open-items.md` (31 KB, 23 numbered items, each with
  current canon, the problem, solutions and a LOCK / REFINE / CHOOSE / SCRIPT DECISION
  recommendation). The older `facts.md` versions are in `input/_previous/`.
- Phase: **intake**, not yet approved. Rounds so far all predate the rewrite above
  (gemini-2.5-pro via OpenRouter, about $0.25 each):
  - `r01` rewrote the showrunner's files as summaries less than half their size — the reason
    for item 5 above.
  - `r02` kept all four files whole; added about 2 KB to `characters.md` (Alpha the person,
    FIXED from `rules/alpha.md`) and about 5 KB of labelled, cited reference detail to
    `world.md`; wrote nothing for `story.md` or `facts.md`; five open items of its own.
  - `r03` failed on provider errors (two upstream timeouts, one rate limit): one file of
    five, no join. Fixed by item 9, **not yet re-run**.
- So the desk's `open-items.md` is still the Script Coordinator's own five from `r02`, and the
  four files on the desk still carry the old `<!-- added at intake -->` marker from `r02`. The
  next run overwrites all five. The showrunner's 23 items have never reached the screen,
  nothing is answered, and there is no `rules/decisions.md` yet.
- Everything is in git now, by the user's decision: `output/` with every round (files,
  reference copies, model calls, event logs — checked for credentials, none), the two `.docx`
  drafts in `drafts/_previous/`, and `campaigns/_morgue/pratul/`. Only `.env`, `secrets/`,
  `logs/`, `__pycache__` and `.DS_Store` are ignored. Commit round output along with code.

Avalanche is the from-scratch test case: two rules files, nothing else. Never run.

## Known problems / next steps

1. **Run the five-pass intake against the model — it has never been run.** The showrunner
   asked for it to be written and not run. Prosperity has `use_references_during_synthesis`
   false in `campaigns/prosperity/output/round-settings.json`. Watch whether per-file calls
   clear the 47,418-char floor; r05's evidence says `characters.md` alone reached 92% of its
   source when it was written first, so three dedicated calls should.
2. **Older notes on running intake** — nothing above has been tried for real. Watch, in order:
   (a) does pass 1 survive the preservation guard on the first attempt, or does it burn all
   three; (b) does the envelope survive four files in one reply, or truncate at 60000 tokens;
   (c) does pass 2 carry the showrunner's 23 items in their own words; (d) does pass 3 label
   its options honestly, or mark inventions [established]; (e) with research now in pass 1 by
   default, does the synthesis stay the showrunner's book or drift into a literature review —
   watch for reference detail stated as canon instead of raised as a proposal. Fallbacks:
   (b) one pass per file, (c) keep their items verbatim in code, (d) tighten `options.md`,
   (e) set `use_references_during_synthesis` false for Prosperity, which is a consolidation
   project, and leave the default on for new ones.
2. **Reference use**: references now reach pass 3 only, by design. If `facts.md` should carry
   tagged facts from the references, that is another pass, not a bigger pass 1.
3. **`named_in` in `app/prompts.py` matches on the first word of a name**, so "Director
   Cassian Lock" matches any "Director", "Grandmother Phantum" any "Grandmother". Fix before
   page prompts are built.
4. **Output subfolders** were discussed, not built: `current/` (approved; only a gate writes
   it), a pending folder (what the running phase wrote; rerun overwrites only this), `desk/`
   (working papers, settings, `previous/`). Open question to the user: is "desk" the working
   papers, or the same thing as the pending folder? Avoid the name `draft/` — `drafts/` is
   already an input folder.
5. The open-items panel on both screens has been exercised through the API only; nobody has
   looked at it in a browser yet.
6. Development and later phases have not been run since the three-file redesign.
7. **Name of the role — settled 2026-09-21: it stays Script Coordinator.** The user asked and
   confirmed. A script coordinator works off set on the script itself — collecting material,
   tracking versions, keeping the paperwork straight so others can decide and write — which is
   intake's job exactly. A script supervisor works on set, logging continuity take by take;
   that job is already `agents/continuity/`, the only reader of `facts.md`, so the rename would
   have collided with it. Do not reopen.
8. The word "library" survives as a concept in the README, the UI and code names
   (`projects.library`, `"library": true`, the `/library/` URL). The user pointed out there is
   no library folder; agent-facing text no longer uses it. A rename to "material" was offered,
   not requested.

## Running it

```
docker compose up -d --build app      # app code is baked into the image: rebuild after edits
open http://localhost:8000/room       # everything;  http://localhost:8000/ is the one-button screen
curl -X POST localhost:8000/api/projects/prosperity/rounds -H 'content-type: application/json' -d '{}'
```

`agents/` and `campaigns/` are bind-mounted, so role and material edits need no rebuild. There
is no local Python environment with FastAPI or pytest; verify with `python3 -m py_compile
app/*.py`, `node --check app/static/app.js`, direct imports of `app.projects` / `app.agent`,
and the running container. A round's cost is in
`output/previous/<round>/<round>-run.json` under `usage.total`.

## How the user works

- Wants it simpler, every time. New intermediate files, relays and modes read as complication.
- Moves and deletes files themselves between messages — run `git status` before assuming.
- Commit only when asked; commit messages are a plain sentence title and prose body.
- Claude's memory for this project holds the design rules
  (`~/.claude/projects/-Users-ai-graphic-novel-writers-room/memory/`).
