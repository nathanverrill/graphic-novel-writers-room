# Sheets: a LoRA training set, one character at a time

Standalone. Nothing here touches the room; it reads a folder you fill by hand and writes
images and captions beside it. Two ways in: a page, or the command line.

## The page

```
docker compose up -d               # http://localhost:8000/sheets
```

Its own container, reached through the room's port (the app proxies `/sheets` to it; on its
own, `python3 sheets/server.py` serves it at http://localhost:8001). Pick the campaign, choose a character from its
`characters.md` (production's copy, or intake's), and **Start**: the description is filled
from the file. Setup on the left (description, notes for every prompt, the steps, the models)
folds away once it is right.

**Left: captured.** The lock, big, and one tile per step - green when kept. Click a tile to
open that step.

**Right: the workspace.** The same for the lock and for every step: **Roll** (six candidates
from three models), click the closest, say what is off, **Roll again from the pick**, until
one is right, then **Keep** (or **Lock**). Kept steps say so and point to the next. Every roll
is kept under `runs/<stage>/rN/`; what you keep lands in `sheets/characters/<name>/set/`
with a caption. The campaigns folder is mounted read only; the OpenRouter key comes from
the room's `secrets/keys.json`.

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

Defaults: nine models on OpenRouter that take a reference image (Gemini 3.1 Flash and 3 Pro Image, GPT Image 2, Flux 2 Pro and Max, Qwen Image 3, Seedream 5 Pro, Recraft v4.1 and v4.1 Pro)
(all take a reference image on OpenRouter; `qwen/qwen-image-3` and `bytedance-seed/seedream-5-0-pro` are good fourth picks),
`--each 2` (six candidates a step). `--dry` walks the flow with no model and no cost.
