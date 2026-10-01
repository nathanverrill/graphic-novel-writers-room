# Earlier runs

Two finished runs from when the room kept its work in `projects/<slug>/` and copied the
deliverables to a top-level `output/<slug>/`. Both folders are gone: a campaign is the project
now, and the room writes `campaigns/<campaign>/output/`.

These are kept because they are real work, not because anything reads them — nothing in
`_morgue/` reaches an agent.

- `evoke-chapter-1/` — page prompts and the story files behind them (script, layouts,
  thumbnails, outline, brief, bible, notes, taste, room log).
- `evoke-chapter-4/` — the same, plus `pages/` with each page's prompt and its lettering SVG.

Inside each, `story/` is what the desk held and `pages/` is what you would have pasted into an
image model. `ROUND.txt` names the round they came from.

To bring one back as a campaign of its own: make `campaigns/<name>/{canon,input,output}`, move
`story/*.md` onto the desk in `output/`, and put anything you want read into `input/`.
