# Run Assembly

A model call should be assembled from only the context needed for that run.

## Base

1. System safety/tooling instructions.
2. `project/EVOKE_PROSPERITY.md`
3. `roles/<active-role>.md`
4. Required `skills/*.md`
5. Optional `hats/<hat>.md`
6. Relevant current artifact excerpt(s)
7. Editor-in-Chief / user note for this run

## Suggested skill mapping

| Role | Required skills |
|---|---|
| Editor-in-Chief | storycraft-core, story-architecture, continuity-and-critique |
| Story Architect | storycraft-core, story-architecture, methods-from-masters |
| Wild Card | ideation-and-provocation, methods-from-masters, storycraft-core |
| Scripter | storycraft-core, scriptwriting |
| Visual Director | storycraft-core, visual-storytelling, methods-from-masters |
| Continuity Editor | storycraft-core, continuity-and-critique + artifact-specific skill |
| First Reader | none; keep context deliberately minimal |

## Important

Do not give First Reader internal notes unless the test is specifically about whether a revision fixed a known issue.

Do not give Wild Card authority language such as "improve the story." Ask it to produce provocations. Selection belongs elsewhere.

Do not attach every skill to every run.

## Random-entry pseudocode

```python
cards = random.sample(provocation_deck, 3)
word = random.choice(random_word_list)
target = random.choice(story_beats_or_pages)

wild_card_context = {
    "cards": cards,
    "random_word": word,
    "random_target": target,
}
```

Randomness should come from code rather than relying only on model temperature.
