# Morgue

Like a newspaper morgue: the clippings archive. Documents we reviewed and don't want
to lose, but that the room does **not** use. Nothing in here reaches an agent.

When something from here is adopted, copy the useful part into `agents/`, `hats/`,
`skills/` or a project's `references/`, and note it below.

## chatgpt_suggestions/ — reviewed 2026-09-16

A lean 7-agent redesign with hats, a Wild Card and a First Reader.

Adopted:
- `hats/*.md` → `hats/` (hat picker on runs)
- `roles/wild-card.md`, `skills/ideation-and-provocation.md`, `project/PROVOCATION_DECK.md` → `roles/wild_card/` (deck drawn in code)
- `roles/first-reader.md` → `roles/first_reader/` (minimal context)
- `skills/storycraft-core.md` → `roles/_shared/storycraft-principles.md`
- `skills/methods-from-masters.md` → `roles/_shared/methods-from-masters.md`
- README "Output discipline" and "Decision rights" → `roles/_shared/house-style.md`
- `project/EVOKE_PROSPERITY.md` → `projects/prosperity/references/evoke-prosperity.md`
- Merged into existing roles: continuity (severity, ledger, critique order),
  editor (canon section, decision log), plotter + character designer
  (story map table, causality, ensemble test), scripter (page job, PAGE CHECK),
  penciller (don'ts, lettering space, accessibility)

Not adopted:
- **Consolidating to 7 agents** (Penciller + Colorist + Letterer → Visual Director;
  Character Designer → Story Architect). The room runs linearly, so there's no
  back-and-forth to save; separate roles keep per-role models and cost data, and the
  Character Designer's visual locks keep generated images consistent. Revisit when
  the Costs view shows which roles don't earn their cost.
- `project/RUN_ASSEMBLY.md` — design notes; the app already assembles context this way.
- The "Read:" sections of the role files — the app decides what each role receives.

## ascii_artist/ — retired 2026-09-17

The ASCII Artist drew whole pages panel by panel with a model. The room draws pages from the Penciller's layout blocks instead, in code and for free, so the role and its guides moved here — with `ascii_art_skill.md` and `ascii_art_bible.md`, the two sources that fed it (moved out of `skills/` on 2026-09-18).
