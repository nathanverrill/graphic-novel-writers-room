# Morgue

Like a newspaper morgue: the clippings archive. Documents we reviewed and don't want
to lose, but that the room does **not** use. It is here for people, so an old draft can be
found again — and nothing in here reaches an agent, because the leading underscore on
`_morgue/` is what the room skips: in the library listing, in what a round carries into a
prompt, and in what an agent can ask for by name.

When something from here is adopted, copy the useful part into `agents/`, `agents/skills/`,
`agents/hats/`, or a campaign's `canon/` or `input/`, and note it below.

## chatgpt_suggestions/ — reviewed 2026-09-16

A lean 7-agent redesign with hats, a Wild Card and a First Reader.

Adopted:
- `hats/*.md` → `agents/hats/` (hat picker on runs)
- `roles/wild-card.md`, `skills/ideation-and-provocation.md`, `project/PROVOCATION_DECK.md` → `agents/wild_card/` (deck drawn in code)
- `roles/first-reader.md` → `agents/first_reader/` (minimal context)
- `skills/storycraft-core.md` → `agents/_shared/storycraft-principles.md`
- `skills/methods-from-masters.md` → `agents/_shared/methods-from-masters.md`
- README "Output discipline" and "Decision rights" → `agents/_shared/house-style.md`
- `project/EVOKE_PROSPERITY.md` → `campaigns/prosperity/` (the campaign's own material,
  now `canon/` and `input/`)
- Merged into existing agents: continuity (severity, ledger, critique order),
  editor (canon section, decision log), plotter + character designer
  (story map table, causality, ensemble test), scripter (page job, PAGE CHECK),
  penciller (don'ts, lettering space, accessibility)

Not adopted:
- **Consolidating to 7 agents** (Penciller + Colorist + Letterer → Visual Director;
  Character Designer → Story Architect). The room runs linearly, so there's no
  back-and-forth to save; separate agents keep per-agent models and cost data, and the
  Character Designer's visual locks keep generated images consistent. Revisit when
  the Costs view shows which agents don't earn their cost.
- `project/RUN_ASSEMBLY.md` — design notes; the app already assembles context this way.
- The "Read:" sections of the role files — the app decides what each agent receives.

## ascii_artist/ — retired 2026-09-17

The ASCII Artist drew whole pages panel by panel with a model. The room draws pages from the Penciller's layout blocks instead, in code and for free, so the agent and its guides moved here — with `ascii_art_skill.md` and `ascii_art_bible.md`, the two sources that fed it (moved out of the skills folder on 2026-09-18).

## colorist/, image_thumbnailer/ — retired 2026-09-20

The art room's only two agents, retired together; the room is now a plan with nothing in it.
The Colorist wrote a color script no one downstream used, because the page prompt hands color
to the outside image model. The Image Thumbnailer paid an image call per panel for a sketch
the room draws from the layout blocks in code. Each folder's README says how to bring it back.

## wild_card/ — retired 2026-09-20

The room's divergent voice, replaced by divergence that commits: two Scripters on the same
outline, one Director picking canon. Its provocations were a document about the story rather
than a version of it, and it was off by default — see the folder's README.
