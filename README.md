# Writers' Room

A web-based, agentic writers' room for graphic novels. Its product is **page prompts**:
for every page, a complete markdown brief you paste into an image model (outside the room)
to draw the finished page. Give it a directional draft script and a page count; the room
writes until the pages are ready, you review every page as a layout sketch — keep the ones
that are done, say what you want on the rest — and the room revises from your notes, edits
and diffs — round after round, each saved in full. Every agent is guided by its own markdown,
images and Figma files and runs on its own provider, model and settings; every model call is
logged with its tokens and dollar cost.

Everything the room can read — the canon, the idea drafts, the craft and worldbuilding skills,
each project's own files — is searchable, hybrid, keywords and meaning at once, and reindexed
about a second after you save a file. The same tools the agents call are served over MCP, so a
chat client or an editor can work on a book without the screen.

The art room — which will draw pages itself, with its own taste — is a separate, later room.
Its agents (Image Thumbnailer, Colorist) are marked `"room": "art"` and are hidden here.

A writing round runs six of them, in this order. The other three are there when you want them,
and run only if you tick them and press **Run selected roles only**.

| In a round | Agent | Writes | Notes |
|---|---|---|---|
| 1 | Editor-in-Chief | `brief.md` | owns canon, the decision log and the visual direction |
| 2 | Plotter | `outline.md` | |
| 3 | Character Designer | `bible.md` | a visual lock per character, pasted into every prompt |
| 4 | Scripter | `script.md` | |
| 5 | Penciller | `layouts.md` (+ `thumbnails.md`) | layout blocks: the source of the page prompts and the sketch |
| 6 | Continuity Editor | `notes.md` | ends with `BLOCKERS:` / `FIX:` lines the gate reads |
| — | Wild Card | `provocations.md` | proposes, never decides |
| — | Letterer | `lettering.md` | balloon order and placement, for the text layer |
| — | First Reader | `first-read.md` | cold read, reactions only, sees nothing but the script and sketch |

A revision round — the one that runs after your review — is Editor-in-Chief, Scripter,
Penciller, Continuity Editor.

The Editor-in-Chief also keeps `taste-writers.md`: what you actually said and changed in your
reviews, plus your standing rules, which every writer reads. Everything is labeled canon, observation, proposal, risk
or decision needed (see `agents/_shared/house-style.md`).

## The screen

Projects on the left; the book in the middle; what the room is doing on the right.

| Where | What |
|---|---|
| Middle, **Pages** tab | page 1 building itself as the room writes (panel boxes and numbers, with each panel's description and dialog beside it), the layout sketch to edit, and the page prompts — the deliverable, so it opens here |
| Middle, **Lettering** tab | the text layer over your uploaded art (only once there are pages) |
| Middle, **The room** tab | who writes, on which model, and this round's settings: lettering, chapter, pages, fix passes, references |
| Middle, under the tabs | **Stats** — what the room has spent, by project, round or agent |
| Right, watch pad | progress, the agents and what each is doing, your notes while you watch, and the live feed |
| Far right, **Files** | the room's markdown files and their previews, references, images and past rounds |

**Write round** sits above the tabs with the showrunner note, so it's there whichever tab you're
on; when a review is waiting, **Review ↓** appears next to it. Changing the previewed page opens
that page's prompt below it.

### Watching a page get made

The **Pages** tab opens on one page and watches it being built. Before you press **Write round**
it's an empty frame at trim proportions, with a card waiting for its **Description** and
**Dialog**. Then the room writes, and the page takes a step each time a writer's file lands —
not token by token; a file at a time, in step with the live feed:

| When | What appears |
|---|---|
| `outline.md` — the Plotter | the page's beat, above the frame |
| `script.md` — the Scripter | one card per panel, marked *from the script*, with its description and dialog |
| `layouts.md` — the Penciller | the panel boxes appear in the frame, numbered; the cards become the real panels — shot and angle, where they sit, who stands where and how big, and every balloon, caption and sound effect with its exact position |
| `notes.md` — the Continuity Editor | that page's flags, under the cards |

The boxes are the tier and panel fractions themselves, nothing else — so any layout the format
can describe draws correctly: a nine-panel grid, one splash, a wide tier over two narrow ones
(`3*` bleeds off the page edge). Click a number to jump to that panel; hovering a card lights up
its box. The map stays put while you scroll the panels.

The room always writes the whole book. This screen follows **page 1** — one page is enough to
form a focused opinion before the rest arrives (`BUILD_PAGE` in `app/static/app.js`). The
remaining pages are all there in **Layout sketch** below (the drawn page with lettering in
place, which is what you edit and review) and in the page prompts, each with its own page picker.

## Page prompts — the deliverable

`page-prompts.md` (in the project, and in every round) has one section per page. Each is
self-contained, so you can paste a single page into an image model:

- **Format** — trim (`PAGE_TRIM`), portrait, left or right page, how many panels.
- **Style** — the brief's visual direction, the same on every page.
- **Characters** — the bible's visual lock for everyone on the page, word for word.
- **Layout** — a box diagram of the page, panels drawn to scale where they sit, then rows
  and panels with their share of the page, bleeds.
- **Panels** — shot and angle, the Penciller's scene description, light, who stands where
  and how big, and every balloon, caption and sound effect in reading order, exactly as lettered.
- **Rules**, and the page's script for reference.

They're **assembled in code**, not written by a model: free, always in step with the room's
files, and the character descriptions never get paraphrased. In the app, **Page prompts** has
a **Copy** button per page and **Copy all pages**; the review screen shows the prompt for the
page you're reviewing. Each round also saves `-pNN-prompt.md` per page, and the final round
saves `book-prompts.md`. So the prompts are only as good as the brief's visual direction, the
bible's visual locks and the Penciller's panel descriptions — that's where to push the room.

## Writing rounds and review

1. **New project** — title, page count (e.g. 7), an optional pitch, and an optional draft
   script (high level, directional; saved as `references/draft-script.md`).
2. **Write round** — the room runs Editor → Plotter → Character Designer → Scripter →
   Penciller → Continuity Editor, then checks the **readiness gate**: exactly the right
   pages, zero layout issues, zero continuity blockers, and locked pages matched. If it
   fails, only the roles that can fix it run again (up to **Fix passes**, default 2).
   Readiness is measured, not the model's opinion. The page prompts are written at the end.
   **Pause** holds the round between two writers; **Auto rounds** runs the next one without
   waiting for you.
3. **Review** — step through the pages (‹ › or the chips). Each page shows its layout sketch
   (editable in place) and its prompt. A page is one of two things:

   | | What happens |
   |---|---|
   | **Kept** | done: script section, layout and sketch are locked and never change again |
   | **Open** | the room can work on it. Edit the sketch or write a note and it works from that; an edited page is locked as your version and the room brings script and layout into line with it. Say nothing and the room carries on with the page as it sees fit |

   Nothing has to be decided: keep what's finished, say what you want on the rest. Your
   notes and edits are saved as you go.
4. **Send to the room** or **Finalize**. Sending saves your review as a human round and starts a
   revision round that works only from it: the Editor updates the brief and the taste file,
   the Scripter and Penciller work the open pages, and the gate checks that the pages you
   redrew now match yours (`min_text_match` / `min_layout_match` in `round-settings.json`).

Locks are enforced in code: whatever an agent writes, locked pages are put back.

### The text rule (sketches)

In the layout sketch, letters, digits and `. , ! ? ' " - : ;` appear **only as text**
(dialogue, captions, sound effects, signs); drawing uses every other character (panel borders
`_ |`, balloons `_ ~ ( ) / \`, captions `+ = |`, figures filled with `% # @ & $` — the legend
says who is who). So your sketch edits diff cleanly: text changes word for word, art changes
as before/after crops by panel.

## Rounds and file names

Every round is a complete folder, and every file name carries the project and round, so a
file means the same thing wherever it ends up:

```
projects/<slug>/rounds/
  <slug>-r01-ai/        the room's work
    <slug>-r01-ai-page-prompts.md, -script.md, -layouts.md, -brief.md, -taste-writers.md …
    <slug>-r01-ai-p03-prompt.md      the page's prompt for the image model
    <slug>-r01-ai-p03-ascii.txt      the page's layout sketch
    <slug>-r01-ai-p03-script.md      the page's script section
    <slug>-r01-ai-p03-layout.json    the page's layout block
    <slug>-r01-ai-run.json, -events.jsonl, -calls.jsonl, calls/<slug>-r01-ai-call-0007-….json
  <slug>-r02-human/     your review
    <slug>-r02-human-review.json / -review.md          what you kept, notes, instructions
    <slug>-r02-human-p02-ascii.txt / -p02-ai-ascii.txt your sketch and the room's
    <slug>-r02-human-p02-diff.md                       text and art diff
  <slug>-r03-ai/        the revision
  <slug>-r04-final/     the approved book: <slug>-r04-final-book-prompts.md, per-page prompts
```

Rounds are numbered in one sequence. The working copy (`projects/<slug>/*.md`) is the live
desk the agents read; `locks.json`, `review-draft.json` and `round-settings.json` sit beside it.
Projects from before rounds keep their old `versions/` folder, which the app no longer shows.

## Run it

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env        # set OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL
.venv/bin/uvicorn app.main:app --reload
```

Open http://localhost:8000.

Search is optional and needs two more things: OpenSearch (`docker compose up -d opensearch`, or
the whole stack) and Ollama on your machine with `ollama pull embeddinggemma`. Without them the
room runs exactly as before.

To try it with no key and no bill, use the mock endpoint (it fakes chat, images and token usage;
`MOCK_REPORT_COST=1` imitates a provider that reports its own cost):

```sh
.venv/bin/python tests/mock_openai.py &
OPENAI_BASE_URL=http://localhost:8765/v1 OPENAI_MODEL=gpt-4o IMAGE_MODEL=gpt-image-1 .venv/bin/uvicorn app.main:app
```

## Docker

```sh
cp .env.example .env              # your provider settings
docker compose up -d --build      # http://localhost:8000
```

`docker compose up -d` brings up three services: the **app**, **SeaweedFS** for project data,
and **OpenSearch** for the search index. Ollama stays on your machine — the app reaches it at
`host.docker.internal:11434`.

**Configuration** — `agents/` (with its skills and tools), `hats/`, `references/` and
`pricing.json` — is mounted from this folder, so you edit it in place, and a saved file is
reindexed about a second later.

**Project data** — `projects/` (every round, page, review and call log) and `logs/` — lives in
**SeaweedFS**, an S3-compatible object store whose storage is the `seaweedfs-data` Docker
volume. The app works on a copy inside its container: on start it pulls everything from the
bucket, then pushes changes (including deletions) every `S3_SYNC_SECONDS` (2 s) and once more
on shutdown. Recreating or rebuilding the app container loses nothing; so does
`docker compose down`. **`docker compose down -v` deletes the volumes, and all project data
with them** — the search index in `opensearch-data` is rebuilt from the files, so losing that
one costs only the time to re-embed.

```sh
# bring an existing project folder in (it syncs up within seconds)
docker compose cp projects/my-book app:/app/projects/my-book
# take a copy out
docker compose cp app:/app/projects ./backup-projects
# bucket status, from inside the app
docker compose exec app python -m app.objectstore status
```

The S3 API is published on `127.0.0.1:8333` for backup tools (bucket `writers-room`). Change
the credentials with `S3_ACCESS_KEY` / `S3_SECRET_KEY` in `.env` before the first start —
both containers read them. Any S3-compatible store works the same way: point `S3_ENDPOINT`
at it. Without Docker, leave `S3_ENDPOINT` unset and data stays as plain files in `projects/`
and `logs/`.

To use a model server running on your machine (Ollama, LM Studio), use
`http://host.docker.internal:11434/v1` as the base URL, not `localhost`.

To use the fake provider, set `OPENAI_BASE_URL=http://mock:8765/v1` in `.env` and run
`docker compose --profile mock up -d`.

After changing `.env`, run `docker compose up -d` again to apply it.

## Layout sketch

The sketch is ASCII art at **print scale**: one character cell is one letter of lettering. At
`LETTERING_PT=7.5` a cell is ~0.057" wide and one lettering line (0.125") tall, so a
6.625" x 10.25" page (`PAGE_TRIM`) is 116 x 82 cells, and a balloon in the sketch is the size
it will be on the page. The UI draws cells at that same 2.18:1 ratio, so pages show in their
true proportions.

The Penciller writes a ```` ```layout ```` JSON block per page (format:
`agents/penciller/layout-format.md`). Every save of `layouts.md` — by the Penciller or by you
in the editor — redraws `thumbnails.md`: panel borders, gutters, bleeds, horizon lines,
balloons/whispers/thoughts/shouts with tails pointing at the speaker, captions, figlet sound
effects and figure placeholders, in code and for free. The renderer reports overlapping
lettering, copy that doesn't fit, over-wordy panels, reading-order conflicts, lettering over
faces, tiny panels and left/right page mistakes back to the Penciller.

**Light and dark.** Any cell can be shown inverted (light on dark), for night scenes,
silhouettes, flashbacks or emphasis. Inversion is a separate mask stored after each page as a
```` ```invert ```` block (`#` = inverted) and saved as `-pNN-invert.txt`. The Penciller sets
it per panel or item (`"invert": true` — which also tells the image model the panel is dark),
and you can paint it in the editor with the **invert brush** or **⌘I**. Review diffs report
inversion changes, and locks keep them.

(The ASCII Artist, which drew full pages in ASCII, is retired to `morgue/ascii_artist/`.)

### Editing the sketch in place

The sketch is plain markdown (`thumbnails.md`): one ```` ```text ```` block per page, then the
panel legend and issues. Click **Edit** (or edit on the review screen) to change it on a fixed
grid — the page never reflows:

| | |
|---|---|
| type | overwrite the cell under the cursor |
| click, arrows, Enter | move (Enter returns to the column you started typing in) |
| drag | select a rectangle; typing fills it, Delete clears it |
| ⌘/Ctrl C, X, V | copy, cut and paste rectangular blocks |
| ⌘/Ctrl Z, ⇧⌘Z | undo, redo |
| ⌘/Ctrl I | invert the selection or cell (light on dark) |
| invert brush | tick it and drag to paint inversion on (or off, starting from an inverted cell) |
| paint | tick **paint** and drag to stamp the brush character |

Saved pages are marked `— edited` and are **kept** when the sketch is redrawn; if the page's
layout changes afterwards, the page gets a warning. **Revert** drops the mark and redraws.
Past rounds are read-only.

## Morgue

`morgue/` keeps reviewed documents we don't use but don't want to lose, with a README noting
what was adopted from each and why the rest wasn't. Nothing in it reaches an agent.

## Running the room

What the screen gives you while the room works, and the controls that decide what it does.

**Holding the room.** **Pause** stops the round at the next clean break: the writer at work
finishes and hands off, and the round waits there — same version, same place in the order,
nothing torn down. While it's held, change any writer's model, temperature or anything else in
**The room**, and jot notes in the watch pad. **Resume** hands both to the writer about to
start and everyone after it (every agent reads `agent.json` when it starts, so the change is
real, and the feed says what changed: `carrying on — Scripter → temperature 0.15 · your notes
go to the writers still to come`). The notes are marked used by that round and saved with it.
**Stop** still ends the round outright, and works while it's held.

**Auto rounds.** **Auto rounds** in **The room** tab runs the book without you. After each
writing round the room hands the round back to itself — every page open, nothing said about any
of them — and starts the next one, counting down as it goes. It stops and finalizes the book
when the readiness gate comes back ready, or when the count runs out. The header shows how many
rounds are left and **Stop auto** ends it after the current round; **Pause**, **Stop** and
**Keep this page** all still work while it runs, and each writer still runs on its own model and
settings.

What the gate measures is structure — page count, layout issues, continuity blockers, locked
pages matched — not whether the book is any good. A run that finishes clean is a draft nobody
has read yet.

**Page count.** You own it: set **Pages** in **The room** tab, or use − / + in the review. The room
can propose a different count by writing one line in `notes.md` —
`PAGE COUNT: 5 — the Leona reveal needs a page of its own` — which shows up in the review as a
suggestion with a button to accept it. Nothing changes the count without you.

**Keeping a page.** Above the panel map, **Keep this page** marks the page as it stands —
the same lock the review writes when you keep a page, but you can set it while the room is working
(pause first if you want to stop it mid-round). From then on the page's script section, layout
block and sketch are put back into whatever an agent saves, the writer is told its changes to
that page were discarded, and the readiness gate stops reporting layout issues for it. Click
again to release it.

**Your notes.** The watch pad on the right has a box to jot thoughts while you watch — half-formed
ones welcome (⌘⏎ adds one). Each note keeps its time and the page you were on. They sit there
until something takes them: the next **Write round** folds them into the room's brief, and
submitting a review adds them to `review.md`; either way they're saved in that round's folder and
marked used. **Tidy into feedback** is one model call (the Editor's model) that groups the pile
by theme and drops the text into your note box to edit before sending — it doesn't spend the
notes. **x** drops a note you've changed your mind about.

**Standing rules.** A jotted note is for the next round only — the room reads it and it's
spent. A rule holds for good. In the watch pad, say **Always**, **Never** or **Remember** and
add it; the rule goes into the Editor-in-Chief's `taste-writers.md`, the file every writer
reads before it starts, in a block the room doesn't own:

```markdown
<!-- showrunner rules -->
## The showrunner's standing rules
- **Always:** open every chapter on a wide establishing shot
- **Never:** put narration captions on a character's face
<!-- end showrunner rules -->
```

The Editor rewrites that file every round, so the block is put back on every save and the
writer is told the rules are yours, not its. **Make a rule** on a jotted note moves its words
into the rule box — pick always, never or remember, add it, and the note is spent. **x** drops
a rule, which also takes it out of the taste file.

**Who is working.** The watch pad lists every writer with a dot — idle, working, done, error —
the step the working one is on, and what it spent last run, so you can see what the room is doing
from any tab without opening **The room**. Under it, the live feed; **Expand** opens it across
the window to read properly, **Close the feed** or Escape puts it back.

**Progress.** Above the live feed in the watch pad, a bar shows the pass and step (e.g. "Pass 1 of up to 3 ·
step 2 of 6: Plotter"), time elapsed, roughly how long is left (the median of each agent's past
real runs from `logs/usage.jsonl`, 2 minutes for an agent with no history), and how long the room
has been waiting on the model, highlighted after 3 minutes.

**Lettering as its own layer.** Set **Lettering** in **The room** tab to *separate layer* and the
page prompts ask the image model for finished art with **no text at all**, keeping the balloon
areas uncluttered. The room then draws the lettering itself, from the layout's items, as a
transparent SVG over the art — so the words are exactly what you typed, and changing a line never
touches the art. The **Lettering** tab is side by side: the page on the left (your uploaded art
with the text layer over it), every balloon, caption and sound effect on the right. Edit the words
or move a balloon to one of nine spots in its panel, and the layer redraws; **x** on a balloon,
caption or sound effect deletes it (after a confirmation). Every change is written back to
`layouts.md` and redraws the layout sketch, so the next round and the page prompts say the same
thing. **Upload art**
attaches the page's art, **Download text layer** saves the SVG, and each round and export writes
`pNN-letters.svg` next to the prompts. Balloons that would overlap are nudged apart automatically.

**Outputs.** The **Pages** tab has the page prompts (Copy / Copy all) and the main story files. Every finished round, review and finalize also writes them to
`output/<project>/` in this folder (`page-prompts.md`, `pages/pNN-prompt.md`, `story/*.md`;
overwritten each time — every version stays in the project's rounds). **Save to output folder**
does it on demand.

**Page numbers.** Every page prompt asks for the page number in small light-blue lettering in
the top-left corner (`PAGE 2`). Set **Chapter** in **The room** tab and page 1 reads
`CHAPTER 4 — PAGE 1`.

How references reach an agent is set by `references` in its `agent.json` (default from `REFERENCES_MODE`):

- `"full"` — pasted into the prompt. Every step of the agent's loop resends them, so big files cost more.
- `"list"` — only the names are sent, and the agent reads what it needs with `read_artifact("references/<name>")`. Cheaper, but the agent has to choose to read them.

## Reference material and skills

The room reads two shared folders. They differ in what the material *is*, and the agents are
told which they are reading:

```
agents/skills/                  craft skills the agents load — always read as guides
agents/skills/sources/          long skills split into per-agent guides (never read whole)
references/                     the book's own material: canon, and idea drafts to mine
references/sources/             originals that tools split up (agents never read these)
projects/<slug>/references/     this project only (a file with the same name wins)
```

So `references/` answers *what is true in this book* — the bible, the chapter canon, Alpha, the
draft script — and `agents/skills/` answers *how to do the work and what is plausible* — layout, emotion,
script writing, the hard-SF rules, the lithium triangle, the Social Innovators' Framework.

**A project picks which library files it uses** — **References…** in **The room** tab lists both
folders; default: all of them. A writer can narrow that further with its own shortlist (below), and the summary
beside the picker shows how many KB the selection is. With references in place the pitch is
optional. Each round keeps a copy of the references it used, and `run.json` records a hash of
each.

Long documents can be split so a project takes only what it needs:

- `python scripts/split_bible.py` — `references/sources/EVOKE_PROSPERITY_CAMPAIGN_BIBLE.md` into
  `EVOKE_PROSPERITY_BIBLE.md` (general canon) and `EVOKE_PROSPERITY_CHAPTER_<n>.md` (each
  chapter's canon row, principle, character interaction map and script revision flags).
- `python scripts/split_script.py` — `references/sources/SCRIPT_DRAFT_AUG_23.md` into
  `SCRIPT_DRAFT_AUG_23_CHAPTER_<n>.md`, each marked as an idea draft.

Rerun them after updating a source.

**What a reference is.** Three kinds, and the room is told which it is reading:

| Kind | Where it comes from | What the room does with it |
|---|---|---|
| canon | `references/`, or `<!-- reference: canon -->` | must not contradict it; where it conflicts with the room's files, the reference wins |
| draft | `<!-- reference: draft -->` near the top | ideas on paper: mine it for beats and intent, write the room's own version |
| guide | anything in `agents/skills/`, or `<!-- reference: guide -->` | craft and worldbuilding guidance: commits the book to nothing, describes no events, take what serves the page |

A marker wins over the folder, so a skill that carries the book's own canon — a character, a
place, the story's one license — says `<!-- reference: canon -->` and is read as canon.
`references/ALPHA.md` is the case in point: it arrived as a skill, but it is who Alpha is, not a
menu of options, so it lives with the canon.

The skills label their material with the vocabulary in
`agents/skills/hard-sf-rules.md` — **T** truth, **EG** educated guess, **S** speculation, **L** license,
**Cut** — along with the rules for a license, the license log and the Thorne and Tyson tests.
Writers keep those labels when they use guide material, and the Continuity Editor's
**plausibility ledger** reports unlicensed inventions, licenses that contradict a truth beside
them, and a license used to skip work the characters should have done.

**Library files per writer.** The **References…** picker chooses what a *round* uses. A writer
also carries its own shortlist: in its model settings, **Library files for this writer**, which
lists the references and the skills together. What each one reads now:

| Writer | Reads in full |
|---|---|
| Editor-in-Chief | the bible, Alpha, `hard-sf-rules` |
| Plotter | chapter canon, Alpha, `hard-sf-rules`, `lithium-triangle-futures`, `triangle-water-wars`, `social-innovators-framework` |
| Character Designer | the bible, Alpha, `hard-sf-rules` |
| Scripter | chapter canon, Alpha, `hard-sf-rules`, `actual-script-writing` |
| Penciller | Alpha, `hard-sf-rules`, `graphic-novel-layout`, `comic-layout-picker`, `near-future-set-design`, `emotion` |
| Continuity Editor | the bible, Alpha, `hard-sf-rules` |
| Wild Card, Letterer, First Reader | names only — they read what they want on demand |

That puts every writer between 97 and 116 KB a call, out of a library that is now 31 files and
622 KB — 16 guides, 9 canon files, 6 idea drafts. Anything left off a shortlist is still one
`read_artifact` away: the chapter canon for the Editor, everyday life and money for the
Scripter, the science guide for the Plotter.

Selecting none in that list means the writer reads whatever the round picked. The project's own
`references/` folder is always read, whatever the shortlist says.

## Guiding the agents

Everything an agent knows comes from its folder:

```
agents/
  agents.json             order, title, mission, reads, outputs
  skills/                 craft skills, loaded by name in an agent's shortlist
  tools/                  what an agent can call: one json schema per tool
  _shared/                given to every agent
  <agent>/
    *.md                  guides — all are read, alphabetically
    images/               reference images (png, jpg, webp, gif)
    figma.txt             Figma URLs, one per line (needs FIGMA_TOKEN)
    figma/*.json          Figma REST API exports, for offline use
    agent.json            provider, model and tuned defaults (committed; no keys)
```

- **Add a guide:** drop a `.md` file in the agent's folder.
- **Skills:** the craft skills in `agents/skills/` reach an agent as library files, chosen by its shortlist. A long skill can instead be split into per-agent guides: `scripts/split_skill.py` copies each agent only the parts of the storycraft skill it needs, as `agents/<agent>/storycraft.md` (the shared core goes to `agents/_shared/`). Edit `agents/skills/sources/story_to_visual_translation_skill.md` or the map in the script, then run `python scripts/split_skill.py`.
- **Add references:** drop images in `images/`. They're sent to the model, so use a vision-capable model or set `SEND_IMAGES=false`.
- **Add Figma:** paste a design file, FigJam board, frame or section URL into `figma.txt` (needs `FIGMA_TOKEN` in `.env`). The agent gets a text summary (frames, sections, text, stickies, palette hex values) plus PNG renders of up to 4 frames or sections.
- **Change what a tool says:** edit its file in `agents/tools/`. The `description` and
  `parameters` are what the model sees, so the wording steers behaviour; `_why` lines are
  comments for the next person. An agent gets every implemented tool unless its `agent.json`
  names a `tools` list, `write_artifact` refuses any file that is not its own output, and
  `generate_image` needs `generate_images: true`. A cold reader (`"context": "minimal"`) gets
  `write_artifact` and `finish` only.
- **Add or change an agent:** edit `agents/agents.json` and create the matching folder.
  `"selected": false` leaves an agent unticked by default. `"context": "minimal"` gives it
  only its own folder, the pitch and its `reads` — no shared guides, references or tools to
  browse the room (the First Reader uses this).
- **Random entry:** an agent with `deck.txt` (one prompt per line) gets 3 cards drawn by code
  each run, plus a word from `words.txt` and a random heading from the outline or script
  as a target. The draw shows in the live feed.

## Hats

`hats/` holds de Bono's six thinking modes (blue process, white evidence, black risk,
yellow value, red reaction, green possibility). Pick one in the hat menu next to **Run**
and it's added to every selected agent for that run; the round records which hat was used.
Hats are modes, not jobs: e.g. run the Continuity Editor in the yellow hat to find what's
worth keeping.

## Per-agent settings

Click **Model** on an agent's card. Up front: **provider** (OpenAI, OpenRouter, Anthropic,
Gemini, Groq, Together, Mistral, DeepSeek, Ollama, LM Studio, or a custom URL), **API key**
and **model** — with **Load models** (the provider's own list), **Test connection**, and
**Use this provider & model for all agents**. **Show advanced** reveals everything else.

**Keys are saved per provider**, in `secrets/keys.json` (git-ignored, owner-only, mounted into
the container). One OpenRouter key serves every agent — and every model — on OpenRouter, and a
key can never follow an agent to a different host. Keys are never shown again, logged, or
written to `agent.json` / `run.json`. Only agents on the default provider fall back to
`OPENAI_API_KEY` from `.env`. For a different key on one agent, set **Key from env var
instead** in the advanced settings. The app listens on `127.0.0.1` only, because anyone who
can reach it can use your keys.

**Each agent's `agents/<id>/agent.json` is committed** and holds its provider, model and
**tuned defaults for that kind of agent** — no keys. Its `_why` note (shown in the advanced
view) explains them:

| Agent | Temp | Max tokens | Why |
|---|---|---|---|
| Editor-in-Chief | 0.6 | 6,000 | judgment and consistency; sees reference images |
| Plotter | 0.9 | 8,000 | structure with surprises |
| Wild Card | 1.1 | 4,000 | divergent leaps; references on demand; few steps |
| Character Designer | 0.7 | 8,000 | exact, reusable descriptions; sees reference images |
| Scripter | 0.85 | 16,000 | voice and dialogue; the longest output, 600 s timeout |
| Penciller | 0.5 | 16,000 | valid layout JSON for every page |
| Letterer | 0.2 | 8,000 | literal and careful |
| Continuity Editor | 0.1 | 10,000 | catches everything; exact `BLOCKERS` line |
| First Reader | 0.7 | 3,000 | natural reactions, minimal context |

Blank or `null` fields use the `.env` defaults; keys starting with `_` are comments. When the
UI changes a setting, the change shows up in `git diff`.

| Field | Meaning |
|---|---|
| `base_url`, `model` | Provider and model (usually set in the UI). |
| `api_key_env` | Optional: the **name** of an env var holding this agent's key, instead of the provider's saved key. |
| `temperature`, `max_tokens` | Sent with every chat request. Models that reject them (e.g. reasoning models) are handled: `temperature` is dropped and `max_tokens` becomes `max_completion_tokens`, remembered per model. |
| `extra` | Merged into the chat request body (`top_p`, `reasoning_effort`, …). |
| `max_steps`, `timeout`, `send_images` | Loop length, request timeout in seconds, and whether reference images are sent. |
| `tools` | Which tools from `agents/tools/` this agent may call — `list_artifacts`, `read_artifact`, `search`, `write_artifact`, `generate_image`, `finish`. Empty means all it can use. |
| `references` | `"full"` (the chosen library files go into every call) or `"list"` (names and sizes only, read on demand). |
| `reference_files` | This writer's own shortlist of library files, set in **Library files for this writer**. Empty means whatever the round picked. |
| `generate_images`, `image_*` | Image generation (art room). With no `image_base_url`, images use the chat provider and key (or `IMAGE_BASE_URL` / `IMAGE_API_KEY` if set). |

A bad `agent.json` is flagged on the card and blocks runs that include that agent.

## Rounds, runs and images

- Every run is a round — **Run selected roles only** too — starting from the current working copy (including your manual edits) and recording every write. A stopped or failed run still leaves a complete round.
- Images (art-room roles, or chat replies that include images) are saved with round-prefixed names in `images/`, so nothing is overwritten.
- Pick a round from the **Files** dropdown to browse its files, replay its feed, see its model calls, or **Restore** its book files into the working copy.

## Search

Everything the room can read is indexed for hybrid search: the campaign's canon and drafts, the
craft and worldbuilding skills, and each project's own files.

- **Keywords** — BM25 in OpenSearch over the passage, its heading path, and the keywords drawn
  from it. A term that is common in one passage and rare everywhere else is a keyword, so a
  record carries *brine*, *cooperative*, *Evokation* rather than *page* and *the room*.
- **Meaning** — `embeddinggemma`, served by Ollama on your machine. Local, free to re-run.
- **Hybrid** — both at once, normalised and combined by OpenSearch's own pipeline, so
  `balloon tails` and `how does a family here talk about money` both work.

A passage is a markdown section carrying its heading path, so a hit reads
`triangle-money.md › The big truths › Three countries, three money cultures` instead of naming a
22 KB file. Indexing is keyed by content hash — an unchanged passage is never re-embedded — so
the first pass over this library is 642 passages in about four minutes, and a pass with nothing
changed is 0.3 s.

The index lives in the `opensearch-data` Docker volume and is published on
`127.0.0.1:9200`, so you can query it yourself:

```sh
curl -s 'localhost:9200/writers-room/_count'
curl -s localhost:8000/api/search/health          # what is up, and how much is indexed
curl -s 'localhost:8000/api/search?q=water+permits&scope=skills&mode=keywords'
```

**Who searches.** The **Files** pane has the search box — pick hybrid, keywords or meaning, and
a scope, and click a hit to open that file, whether or not this round carries it. The agents have it as a tool (`agents/tools/search.json`),
so a writer can reach the whole library without carrying it. MCP clients get `search_room` and
`reindex`.

**Staying current.** The app watches every file the index covers and reindexes the ones that
change: **an edit is searchable in about a second** — 0.16 s for a host save to reach the
container, up to 0.5 s of poll, 0.3 s to embed the changed passage and refresh. The same applies
to what an agent writes mid-round, so a page the Penciller has just written is searchable while
the round is still going.

One changed file costs one file's work: the passages it lost are dropped, the ones it gained are
embedded, everything else is left alone. Re-chunking a 37 KB file with nothing changed takes
0.32 s and re-embeds nothing.

It polls (twice a second, a few dozen `stat` calls) rather than using an OS file watcher,
because the app runs in the container while you edit on the host: macOS bind mounts do not
forward inotify events, so a watcher would see what the agents write and stay silent for
everything you save. Running the app natively instead makes an OS watcher the better choice —
only the trigger would change.

**Running it.** `docker compose up -d` starts OpenSearch beside the app, which indexes on start
and watches from then on. Ollama runs on your machine with `ollama pull embeddinggemma`.
Without either, the room works as before: the box says search is off, and the agents' tool tells
them to fall back to `list_artifacts` and `read_artifact`.

## The room's tools, over MCP

The six tools an agent calls are defined in `agents/tools/`. The room also serves them over
MCP, so a chat client, an editor or another agent can work on a book without going through the
screen:

```sh
claude mcp add --transport http writers-room http://localhost:8000/mcp/
```

| Tool | What it does |
|---|---|
| `list_projects` | the room's projects by name |
| `list_artifacts` | a project's room files and its reference material |
| `read_artifact` | one file, e.g. `script.md` or `references/ALPHA.md` |
| `write_artifact` | overwrite one room file with complete markdown |
| `search_room` | hybrid search over the library, the skills and a project's files |
| `reindex` | rebuild the index from disk; unchanged passages are not re-embedded |
| `page_prompts` | the deliverable: every page's prompt, or one page's |

Outside a round there is no agent, so every tool takes the project it acts on and
`write_artifact` is not restricted to one agent's outputs. The guards are the same either way,
and in the same code: pages you have kept are put back, your standing rules are restored, and
saving `layouts.md` redraws the sketch. `finish` is not served — it ends an agent's turn, which
means nothing from outside.

## Always the file on disk

Nothing about an agent is cached between turns. Every time an agent takes the floor it reads
its guides, its `agent.json`, the tool files in `agents/tools/`, and whichever library files it
carries, straight from disk — so editing a `.md` while a round is running changes what the next
writer sees, and pausing the round to edit one is a real way to work. The same goes for the
tools served over MCP: their descriptions are re-read before a client is shown them.

The exceptions are not markdown: code under `app/` is baked into the Docker image and needs
`docker compose up -d --build app`, Figma pulls are cached per process, and the browser caches
the app's own JS and CSS (a hard reload picks up a new build).

## Call logs and costs

Every model call — chat and image, successful or failed — is recorded three ways:

```
rounds/<slug>-r03-ai/calls/<slug>-r03-ai-call-0007-scripter-chat.json   full request + response
rounds/<slug>-r03-ai/<slug>-r03-ai-calls.jsonl                           one summary line per call
logs/usage.jsonl                                               the same lines, across all projects
```

A summary line has: project, round (`version`), agent, kind (`chat`/`image`), provider host, model,
input / cached / image / output / reasoning tokens, `cost_usd`, `cost_source`, duration,
HTTP status, error, and the path to the full log.

- **Cost** comes from the provider when it reports one (`usage.cost`, which OpenRouter returns). Otherwise it's worked out from `pricing.json` (USD per 1M tokens, or `per_image`). A model found in neither is logged as `unpriced` and flagged in the UI. **Check `pricing.json` against your providers' current prices**; the file reloads automatically when you change it.
- **Images** inside requests and responses (base64) are saved once to `calls/blobs/` and replaced by `<blob:calls/blobs/…>`, so logs stay readable. API keys are never logged.
- **In the UI:** each call shows its tokens and cost in the live feed, and agent cards show what their last run cost. The **Costs** section breaks spending down by role, by provider/model, by role × provider/model, and by chat vs image, for this project, a selected round, or all projects. A round's **Model calls** button lists its calls, with links to the full JSON.
- **Your own analysis:** `logs/usage.jsonl` loads straight into pandas: `pd.read_json("logs/usage.jsonl", lines=True)`.
- **Totals:** each round's `run.json` has a `usage` block with totals per agent.

## How an agent works

`app/agent.py` is a plain loop:

1. The system prompt is the agent's mission plus its guides and Figma summaries.
2. The first message is the pitch, the upstream files listed in `reads`, any previous draft, your note, and the images.
3. The model calls tools — the ones in `agents/tools/` this agent carries: `list_artifacts`, `read_artifact`, `search`, `write_artifact` (its own outputs only), `generate_image` (if enabled) and `finish` — until it calls `finish` or stops calling tools.
4. The handoff note is appended to `room-log.md`.

If the endpoint rejects tool calling, the agent retries as a plain chat and saves the reply as its deliverable.

Tool calls are repaired before they run. Some models glue two calls into one `arguments`
string — `{"name": "script.md"}{"name": "layouts.md"}` — and a provider that validates the
transcript then rejects every later request in that turn, which used to kill the round. Each
object becomes its own call, anything that still will not parse becomes an empty call for the
tool to complain about, and the feed says which happened.

## Limits

- One run per project at a time.
- Search is optional: without OpenSearch or Ollama the room works, and the agents' `search` tool
  tells them to fall back to `list_artifacts` and `read_artifact`.
- The MCP endpoint and the API have no authentication. Both are bound to `127.0.0.1`; anything
  that can reach them can read and write your books.
- With the object store, up to `S3_SYNC_SECONDS` of writes can be lost if the app container is killed without a clean stop.
- Live runs are tracked in memory: restarting the server during a run ends it. The run's round keeps everything written up to that point, but its status stays `running`.
