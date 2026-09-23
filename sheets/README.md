# Sheets: a LoRA training set, one character at a time

Standalone. Nothing here touches the room; it reads a folder you fill by hand and writes
images and captions beside it. Two ways in: a page, or the command line.

## The page

```
docker compose up -d sheets        # http://localhost:8001
```

Its own container, its own port. Pick the campaign, choose a character from its
`characters.md` (production's copy, or intake's), and **Start this character**: the description
is filled from the file. Add notes that go into every prompt ("always the burn scar"), upload
the lock image, save, and **Run** each step. The candidates appear in the page; click the one
to keep. What you keep lands in `sheets/characters/<name>/set/` on your disk. The campaigns
folder is mounted read only; the OpenRouter key comes from the room's `secrets/keys.json`.

## The command line

1. Make a folder: `sheets/ada/`.
2. Drop in `description.txt` (paste the character's look, from `characters.md` or your own words)
   and `lock.png` (the one view you approved: front, neutral, plain background).
3. Optionally copy `steps.txt` in and edit it. Each line is `name | what to change | parent`.
4. Run it:

```
python3 sheets/sheets.py ada
```

Each step sends the parent image and the instruction to two or three image models at once
(OpenRouter; the key from `OPENROUTER_API_KEY` or the room's `secrets/keys.json`). A contact
sheet opens in your browser; you type the number to keep in the terminal, `r` to redo the
step, `s` to skip, `q` to stop. Run it again later and it carries on from the first step
without a pick. `--step face-angry` redoes one step.

`sheets/ada/set/` is the training set: `NN-step.png` and `NN-step.txt` (the caption, starting
with the trigger word). `lineage.jsonl` records every candidate, which model made it, from
which parent, and which was kept - so after one character you know which model to trust for
faces, poses and light.

Defaults: `--models google/gemini-3.1-flash-image,openai/gpt-image-2,black-forest-labs/flux.2-pro`
(all take a reference image on OpenRouter; `qwen/qwen-image-3` and `bytedance-seed/seedream-5-0-pro` are good fourth picks),
`--each 2` (six candidates a step). `--dry` walks the flow with no model and no cost.
