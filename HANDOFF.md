# Handoff — 2026-09-21

For the next Claude session. Branch `simplify`, pushed to `origin/simplify`. Read this, then
`README.md` (the phase table at the top and "The library" section). Delete this file when it
is no longer useful.

## What the room is now

Five phases, a gate after each: **Intake → Development → Audition → Writing → Execution**
(`agents/phases.json`).

- **Intake** is one agent, the **Script Coordinator** (`agents/script_coordinator/`), the
  Director's assistant. It is the only agent that reads a campaign's `rules/`, `input/`,
  `drafts/` and `references/`. It sorts them into three living files — `characters.md`,
  `world.md`, `story.md` — plus `facts.md` (Continuity Editor only) and `open-items.md`.
  It organizes and proposes; it decides nothing.
- **Development** works in the same three files: Director owns `brief.md` + `world.md`,
  Plotter owns `story.md` (beats, structure and page plot in one file), Character Designer
  owns `characters.md`. There is no `research.md`, `bible.md` or `outline.md` any more.
- Agents know only their craft guides and the prompt the room builds. No agent file names a
  campaign file. Material is named by its real path, `campaigns/<campaign>/<folder>/<file>`.
- A campaign reads only its own folder. The shared `evoke` campaign, Figma support and
  `scripts/` are gone. Underscore folders (`_previous/`, `campaigns/_morgue/`) are never read.
- The pitch is optional material at `input/pitch.md`. Nothing in `output/` steers intake.

## Built today, in order

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
- Phase: **intake**, not yet approved. Rounds so far (gemini-2.5-pro via OpenRouter, about
  $0.25 each):
  - `r01` rewrote the showrunner's files as summaries less than half their size — the reason
    for item 5 above.
  - `r02` kept all four files whole; added about 2 KB to `characters.md` (Alpha the person,
    FIXED from `rules/alpha.md`) and about 5 KB of labelled, cited reference detail to
    `world.md`; wrote nothing for `story.md` or `facts.md`; five open items of its own.
  - `r03` failed on provider errors (two upstream timeouts, one rate limit): one file of
    five, no join. Fixed by item 9, **not yet re-run**.
- So the desk's `open-items.md` is still the Script Coordinator's own five from `r02`. **The
  join has never run against the model**, and the showrunner's 23 items have never reached the
  screen. Nothing is answered; there is no `rules/decisions.md` yet.
- Everything is in git now, by the user's decision: `output/` with every round (files,
  reference copies, model calls, event logs — checked for credentials, none), the two `.docx`
  drafts in `drafts/_previous/`, and `campaigns/_morgue/pratul/`. Only `.env`, `secrets/`,
  `logs/`, `__pycache__` and `.DS_Store` are ignored. Commit round output along with code.

Avalanche is the from-scratch test case: two rules files, nothing else. Never run.

## Known problems / next steps

1. **Run intake again** — the first real test of the blind list, the join, the quality check
   and the missing-files nudge. Watch the join above all: the showrunner's entries are long,
   and a model reshaping a long document is what lost content in `r01`. If it shortens their
   items, do what item 5 did: keep their items word for word in code and let the model only
   add proposals and its own extra items.
2. **Reference use is still thin**, and `facts.md` gets no tagged facts from the references.
   Prompt-only fixes for length failed twice; prefer structure (one call per file, or per
   reference topic) over more adjectives.
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
7. **Name of the role.** The user twice wrote "script supervisor" for the Script Coordinator
   while describing its quality-control job. Asked whether they want the rename; no answer
   yet. It would be a folder rename (`agents/script_coordinator/`) plus role, roster, phase
   and README text.
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
