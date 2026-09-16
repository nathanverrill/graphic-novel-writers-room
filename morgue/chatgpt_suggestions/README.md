# Graphic Novel Writers' Room

A lean multi-agent room for developing graphic novels without turning every specialty or thinking mode into a separate agent.

## Recommended room: 7 agents

1. **Editor-in-Chief** — owns the process, brief, gates, and final decisions.
2. **Story Architect** — owns plot, character causality, page budget, and story structure.
3. **Wild Card** — creates deliberate provocations and non-obvious alternatives; never decides.
4. **Scripter** — converts the approved story plan into page/panel script.
5. **Visual Director** — owns page storytelling, panel composition, visual continuity, color intent, and lettering feasibility.
6. **Continuity Editor** — checks logic, clarity, contradictions, pacing, and production preflight.
7. **First Reader** — gives cold-reader reactions only; never proposes fixes.

## Why reduce the room?

The former **Character Designer** is folded into Story Architect because character design should change story causality, not become an isolated biography exercise.

The former **Penciller, Colorist, and Letterer** are folded into Visual Director because page composition, value/color hierarchy, reading order, balloon space, and sound effects constrain one another. Keeping them separate can create expensive back-and-forth before art exists.

Their specialist knowledge is preserved in `skills/` so it can be attached to a future dedicated agent when production complexity actually requires one.

## Shared context model

Every run should be assembled from small files instead of one giant master prompt:

- `roles/<role>.md` — what this agent is responsible for.
- `skills/*.md` — reusable craft knowledge.
- `project/EVOKE_PROSPERITY.md` — project-specific truth.
- `hats/<mode>.md` — optional thinking mode for this run.
- Current artifacts — story map, script, pages, notes, etc.
- Showrunner note — the immediate request.

Roles should not silently invent project canon. If something is missing, they may propose it and label it as a proposal.

## Hat system

Hats are **modes**, not jobs. Add at most one hat file to a normal role run.

- Blue — process and framing
- White — facts and observable evidence
- Black — risks and failure modes
- Yellow — strengths and opportunities
- Red — immediate reaction without justification
- Green — alternatives, provocations, and new possibilities

The dedicated First Reader is essentially a disciplined red-hat pass. The Wild Card is a stronger green-hat implementation with random-entry prompts supplied by code.

## Suggested pipeline

`Editor-in-Chief → Story Architect → Wild Card (optional/default at concept stage) → Editor-in-Chief selection → Scripter → Visual Director → Continuity Editor → revision → First Reader → Editor-in-Chief`

The Wild Card should run **after a coherent plan exists but before prose becomes expensive to rewrite**. It can also be invoked on demand for a page range or beat.

The First Reader should see as little internal reasoning as possible. Give it the artifact a normal reader would see, plus the intended audience. Its value comes from reacting cold.

## Decision rights

- Wild Card proposes; never selects.
- First Reader reacts; never repairs.
- Continuity Editor diagnoses; may suggest repair directions but does not rewrite unless explicitly asked.
- Story Architect and Scripter create within their scopes.
- Visual Director makes visual-storytelling decisions within approved story intent.
- Editor-in-Chief resolves conflicts and approves canon.

## Output discipline

Every agent should distinguish:

- **Canon** — already approved project truth.
- **Observation** — what is actually present in the artifact.
- **Proposal** — a new idea that could become canon.
- **Risk** — a plausible failure or ambiguity.
- **Decision needed** — a choice that belongs to the Editor-in-Chief.

Do not bury a proposed change inside a rewrite and thereby make it canon accidentally.
