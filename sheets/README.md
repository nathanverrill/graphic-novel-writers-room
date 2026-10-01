# Sheets: a LoRA training set, one character or one place at a time

Standalone. Nothing here touches the room; it reads a folder you fill by hand and writes
images and captions beside it. Two ways in: a page, or the command line.

## The page

```
docker compose up -d               # http://localhost:8000/sheets
```

Its own container, reached through the room's port (the app proxies `/sheets` to it; on its
own, `python3 sheets/server.py` serves it at http://localhost:8001). Pick the campaign, choose a
character from its `characters.md` or a place from its `world.md` (production's copy, or
intake's), and **Start**: the description is filled from the file. The places offered are the
sections of `world.md` under a heading that reads like a place (setting, geography, location,
city, texture...), each carrying its subsections; if no heading does, every section is offered.
Edit the description before the first roll if it says more than the place looks like.

The third group in the chooser is **scenes, from the story**: `story.md`'s page plot (its
numbered lines) and, in intake's richer copy, the `###` sections under each chapter, in story
order. Starting one makes a place whose description is the beat and, under it, the `world.md`
text of every place the beat names - so "p7 · Journey to Halyard" starts from what happens
and what Halyard looks like. The hidden workshop and the abandoned mine are in the story and
not the world, so their description is the beat alone until you add to it. Setup on the left (description, notes for every prompt, the steps, the models)
folds away once it is right.

**Left: captured.** The lock, big, and one tile per step - green when kept. Click a tile to
open that step.

**Right: the workspace.** The same for the lock and for every step: **Roll** (six candidates
from three models), click the closest, say what is off, **Roll again from the pick**, until
one is right, then **Keep** (or **Lock**). Kept steps say so and point to the next. Every roll
is kept under `runs/<stage>/rN/`; what you keep lands in `sheets/characters/<name>/set/`
with a caption. The campaigns folder is mounted read only; the OpenRouter key comes from
the room's `secrets/keys.json`.

## A lock from a reference image

Setup has **Roll the lock from a reference image…** beside the lock upload. A reference (a
screenshot, a photo, a game scene - a Minecraft build of the town, say) is saved as
`reference.png` and never kept itself. The lock's first roll then builds on it with a prompt
that takes only what is where from it - terrain, buildings, viewpoint - and redraws the rest
from the **Style** in Setup (empty: the brief's visual direction; the **Photo-real** button
fills in a photographic one) and your note ("not a game scene:
photo-real graphic novel, weathered concrete and steel, dusk"). Pick the closest, note, roll
again from the pick, and Lock as usual. **Start over** on the lock goes back to the reference.

## The book's style plate

A text-only lock follows the words, and the words are too loose to keep twenty characters
looking like one book. Once one lock is exactly right, **Use as the book's style** on it copies
it to `characters/_style/plate.*`. From then on, every fresh lock (the first roll, or Start
over) can be rolled **text only**, **with the style plate**, or both side by side: the plate
goes along as a reference for line, palette, light and texture, and the prompt forbids taking
its subject, face, clothes, pose or background. Models copy content from a reference as
readily as style, so look for that; the side-by-side is there to show whether the plate helps.
With a reference image, the reference goes first (what is where) and the plate second.
Rolling again from a pick, and every step after the lock, builds on its parent, which already
carries the style, so the plate is not sent there.

Each model chip shows how often that model's candidate was the one kept, over every subject
(`kept/rolled`, from each `lineage.jsonl`); kept rows record `variant` too.

## Places

A place is built the same way. Its lock is one establishing view (wide, eye level, nobody in
frame) instead of a front view, its steps come from `steps-place.txt` - three, all from the
lock: **day**, **night** and **close-detail** - and its prompts keep "this exact place"
rather than "this exact character". When the campaign's `world.md` declares the **80/15/5**
rule, a place starts with the hard-SF line in its notes for every prompt (the **Hard SF
80/15/5** button in Setup adds it to anything else); it goes into every prompt right after the
style. The check before you pick asks about perspective, scale and repeated
textures instead of hands and eyes. The trigger word ends in `plc`. On disk the only
difference is a `kind.txt` holding `place` in the folder, so a character folder is any folder
without one.

## Reset

**Reset…** at the foot of Setup starts the open character or scene over. It asks you to type
`evoke`; the server checks the word too. The reference image, the lock, every roll, every kept image
and the logs move to `previous/<date-time>/` inside the subject's folder; only the
description, notes, style, steps and kind stay, so the next Roll is a first roll again. Nothing
is deleted.

## The command line

1. Make a folder: `sheets/ada/`.
2. Drop in `description.txt` (paste the character's look, from `characters.md` or your own words)
   and `lock.png` (the one view you approved: front, neutral, plain background). For a place,
   add `kind.txt` holding the word `place`, and the lock is an establishing view.
3. Optionally copy `steps.txt` (a place: `steps-place.txt`) in and edit it. Each line is `name | what to change | parent`.
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

Defaults: five models on OpenRouter that take a reference image (Gemini 3.1 Flash Image, GPT Image 2,
GPT Image 2.5 Flare and Sunburst, MAI Image 2.6 Flash), `--each 2` (ten candidates a step). Flux is
offered but not on by default. Qwen, ByteDance (Seedream), xAI (Grok) and Gemini 3 Pro Image are never
offered (`EXCLUDED` in `sheets.py`, and the room's model picker in `app/llm.py`). `--dry` walks the flow with no model and no cost.
