# Wild Card (retired)

Made the story less inevitable: deliberate provocations and non-obvious leaps tied to specific
beats, into `provocations.md`, which the Director kept under "Proposals under consideration"
and the Plotter could adopt. It proposed; it never decided. Ran at 1.1 temperature, and drew
cards and a word from its own `deck.txt` and `words.txt` on every run (`random_entry`).

Retired on 2026-09-20 in favor of divergence where it costs something: two Scripters writing
the same pages from the same brief, outline and bible, with the Director picking canon. A
provocation is an idea about a scene; a scene is the only thing that shows whether the idea
works. It was also `"selected": false` and absent from `FIRST_ROUND`, so the room's only
divergent voice was the one you had to remember to switch on — and it read `outline.md` and
`script.md`, which don't exist on a first round.

To bring it back: move this folder to `agents/wild_card`, add it to `agents/agents.json`
(`"selected": false`, reads `brief.md`, `outline.md`, `script.md`, `taste-writers.md`, output
`provocations.md`), and put `provocations.md` back in the Director's and Plotter's `reads`.
Its deck did not come here: `deck.txt` and `words.txt` moved to `agents/_shared/`, where the
`provoke` tool draws from them, so any writer can ask for a provocation instead of one agent
being dealt three whether it wanted them or not.
