# Writers' Room

A web-based, agentic writers' room for graphic novels. Its product is **page prompts**:
for every page, a complete markdown brief you paste into an image model (outside the room)
to draw the finished page. Drawing the pages is not this application's job.

The room works in **five phases**, and you stand at the gate between each. Nothing moves on
by itself:

| | Phase | Who runs, in order | What you get | Your gate |
|---|---|---|---|---|
| 1 | **Intake** | Script Coordinator | `characters.md`, `world.md`, `story.md`, `open-items.md`, then `facts.md` | **Answer the open items** — approve an option, edit it, defer it, or leave it — add weighted notes if you have any, run intake again to fold them in, then **Approve** |
| 2 | **Development** | Director → Plotter → Character Designer → Continuity Editor | `brief.md`, and the same `world.md`, `story.md`, `characters.md`, built up; `notes.md` | **Approve**: is this the right story, told by these people? |
| 3 | **Audition** | Writer A → Writer B → First Reader | `audition-a.md`, `audition-b.md` (the same opening pages, twice), `first-read.md` | **Pick**: whose book do you want to read? |
| 4 | **Writing** | the writer you picked → Continuity Editor | `script.md`, `notes.md` | **Approve**: are these the words? |
| 5 | **Execution** | Layout Agent → Letterer → Continuity Editor | `layouts.md`, `lettering.md`, the page sketches, and the **page prompts** | **Review** the pages: keep, note, send back, or finalize |

Three rules make this work, and they are the whole design:

- **A phase never reruns the ones before it.** A lettering problem reruns the Letterer, not the
  writer. Not happy with a phase? Add a note and run it again; each agent revises its own last draft.
- **The first four gates are your judgment; the last one is measured.** Execution checks itself
  — right page count, no layout issues, no continuity blockers — and reruns its own agents until
  it passes (up to **Fix passes**), before it asks you anything.
- **You can always go back.** Click any phase to take the book there. Nothing is deleted.

The definition is one small file, `agents/phases.json`: who runs in each phase, in what order,
and what to read before you decide. The code that runs it is `app/phases.py` and `app/room.py`.

## The agents

Ten agents. Each is a folder with a `role.md` (the job and its deliverable), a `craft.md` (how
to do that job well) and an `agent.json` (its model and settings).

| Agent | Phase | Writes | What it is for |
|---|---|---|---|
| Script Coordinator | intake | `characters.md`, `world.md`, `story.md`, `open-items.md`, `facts.md` | the Director's assistant and the only reader of what you put in, whatever you named it: organizes it into the three files the room works from, lists what is still undecided, offers options, carries your decisions back in, and derives the fact list for the Continuity Editor. A five-pass pipeline, not a tool loop (`app/intake.py`) |
| Director | development | `brief.md`, `world.md`, `taste-writers.md` | owns the vision, the canon, the decision log and the visual direction; settles what the world leaves open |
| Plotter | development | `story.md` | what happens, in what order, on which page — never the dialogue |
| Character Designer | development | `characters.md` | a visual lock per character, pasted word for word into every page prompt |
| Writer A | audition, writing | `script.md` | the writer who trusts the picture: spare, image-led |
| Writer B | audition, writing | `script.md` | the writer who trusts the voices: dialogue-led |
| First Reader | audition | `first-read.md` | reads both auditions cold — the pages, nothing else — and reports reactions. Never picks |
| Layout Agent | execution | `layouts.md` (+ `thumbnails.md`, drawn in code) | the shape of each page; its layout blocks are the source of the page prompts and the sketch |
| Letterer | execution | `lettering.md` | checks balloon order, placement and word count; the Layout Agent reads it on a fix pass |
| Continuity Editor | closes 1, 3 and 4 | `notes.md` | finds what is broken; ends with the `BLOCKERS:` / `FIX:` lines the execution gate reads |

**The two writers** are the room's one deliberate act of divergence. They share a job and a
craft (`agents/_writers/role.md` and `craft.md`) and differ in voice (`agents/writer_a/voice.md`,
`agents/writer_b/voice.md`) and settings — give them different models if you can. The audition
is blind: neither can read the other's pages. When you pick, the winner's audition pages become
the start of `script.md` and that writer writes the rest.

The Director also keeps `taste-writers.md`: what you actually said and changed in your
reviews, plus your standing rules, which every writer reads. Everything is labeled canon, observation, proposal, risk
or decision needed (see `agents/_shared/house-style.md`).

Everything the room can read — a campaign's rules, everything in its input, the craft skills,
each project's own files — is searchable, hybrid, keywords and meaning at once, and reindexed
a second or two after you save a file. The same tools the agents call are served over MCP, so a
chat client or an editor can work on a book without the screen.

## Two screens

**`/` is one button.** It runs the phase the Prosperity book is in — **Start intake**,
then **Run audition**, and so on: a line for each agent in that phase with the one at work
spinning, and under it the gate — the question, and **Approve** or **Pick Writer A / Pick
Writer B**. After execution it shows the lettered pages. Built for a phone, nothing to set.

**`/room` is everything else** — every writer, every file, every round — and the rest of this
document is about that screen. The two link to each other: the footer on `/`, the title on
`/room`.

## The room's screen

Campaigns on the left; the book in the middle; what the room is doing on the right.

| Where | What |
|---|---|
| Middle, **Pages** tab | page 1 building itself as the room writes (panel boxes and numbers, with each panel's description and dialog beside it), the layout sketch to edit, and the page prompts — the deliverable, so it opens here |
| Middle, **Lettering** tab | the text layer over your uploaded art (only once there are pages) |
| Middle, **The room** tab | the agents, on which model, and this round's settings: lettering, chapter, pages, fix passes, references |
| Middle, under the tabs | **Stats** — what the room has spent, by project, round or agent |
| Right, watch pad | progress, the agents and what each is doing, your notes while you watch, and the live feed |
| Far right, **Files** | the room's markdown files and their previews, references, images and past rounds |

**Run *phase*** sits above the tabs with the five phases, the gate and the showrunner note, so
it's there whichever tab you're on; in execution, when a review is waiting, **Review ↓** appears
next to it. Changing the previewed page opens
that page's prompt below it.

### Watching a page get made

The **Pages** tab opens on one page and watches it being built. Before you run a phase
it's an empty frame at trim proportions, with a card waiting for its **Description** and
**Dialog**. Then the room writes, and the page takes a step each time a writer's file lands —
not token by token; a file at a time, in step with the live feed:

| When | What appears |
|---|---|
| `story.md` — the Plotter | the page's beat, above the frame |
| `script.md` — the writer | one card per panel, marked *from the script*, with its description and dialog |
| `layouts.md` — the Layout Agent | the panel boxes appear in the frame, numbered; the cards become the real panels — shot and angle, where they sit, who stands where and how big, and every balloon, caption and sound effect with its exact position |
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
- **Characters** — the visual lock in `characters.md` for everyone on the page, word for word.
- **Layout** — a box diagram of the page, panels drawn to scale where they sit, then rows
  and panels with their share of the page, bleeds.
- **Panels** — shot and angle, the Layout Agent's scene description, light, who stands where
  and how big, and every balloon, caption and sound effect in reading order, exactly as lettered.
- **Rules**, and the page's script for reference.

They're **assembled in code**, not written by a model: free, always in step with the room's
files, and the character descriptions never get paraphrased. In the app, **Page prompts** has
a **Copy** button per page and **Copy all pages**; the review screen shows the prompt for the
page you're reviewing. Each round also saves `-pNN-prompt.md` per page, and the final round
saves `book-prompts.md`. So the prompts are only as good as the brief's visual direction, the
visual locks in `characters.md` and the Layout Agent's panel descriptions — that's where to push the room.

## Rounds and review

1. **New project** — title, page count (e.g. 7), an optional pitch (saved as `input/pitch.md`), and an optional draft
   script (high level, directional; saved as `drafts/draft-script.md`). It starts in intake.
2. **Run *phase*** — runs the phase the book is in, then stops for you. Read what the gate lists,
   and approve, pick, or add a note and run it again. **Pause** holds a round between two agents.
   In execution the room also checks the **readiness gate**: exactly the right pages, zero
   layout issues, zero continuity blockers, and locked pages matched. If it fails, only the
   execution agents that can fix it run again (up to **Fix passes**, default 2). Readiness is
   measured, not the model's opinion. A blocker that belongs to an earlier phase stops the
   passes: sending the book back is your call. The page prompts are written at the end.
   **Auto rounds** reruns execution without waiting for your review.
3. **Review** — step through the pages (‹ › or the chips). Each page shows its layout sketch
   (editable in place) and its prompt. A page is one of two things:

   | | What happens |
   |---|---|
   | **Kept** | done: script section, layout and sketch are locked and never change again |
   | **Open** | the room can work on it. Edit the sketch or write a note and it works from that; an edited page is locked as your version and the room brings script and layout into line with it. Say nothing and the room carries on with the page as it sees fit |

   Nothing has to be decided: keep what's finished, say what you want on the rest. Your
   notes and edits are saved as you go.
4. **Send to the room** or **Finalize**. Sending saves your review as a human round and runs
   execution again, working only from it: the Layout Agent and Letterer work the open pages, and
   the gate checks that the pages you redrew now match yours (`min_text_match` / `min_layout_match` in `round-settings.json`).

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
campaigns/<slug>/output/previous/
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

Rounds are numbered in one sequence. The desk (`campaigns/<slug>/output/*.md`) is the live copy
the agents read and write; `locks.json`, `review-draft.json` and `round-settings.json` sit beside
it, and every finished round is kept under `output/previous/`.

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

`docker compose up -d` brings up three services: the **app**, **SeaweedFS** for the room's data,
and **OpenSearch** for the search index. Ollama stays on your machine — the app reaches it at
`host.docker.internal:11434`.

**Configuration** — `agents/` (with its skills and tools), `campaigns/` and
`pricing.json` — is mounted from this folder, so you edit it in place, and a saved file is
reindexed about a second later.

**The work is `campaigns/`, bind-mounted from this folder** — the room reads `rules/` and
`input/` and writes `output/`, all as plain files on your disk, so you can open them in an
editor and git keeps their history. Rebuilding or recreating the container loses nothing,
because nothing the room made lives inside it.

Only the usage ledger (`logs/usage.jsonl`) goes to **SeaweedFS**, the S3-compatible store whose
storage is the `seaweedfs-data` volume. `docker compose down -v` deletes that volume and the
cost history with it; the search index in `opensearch-data` is rebuilt from the files, so losing
that one costs only the time to re-embed.

```sh
# bucket status, from inside the app
docker compose exec app python -m app.objectstore status
```

The S3 API is published on `127.0.0.1:8333` for backup tools (bucket `writers-room`). Change
the credentials with `S3_ACCESS_KEY` / `S3_SECRET_KEY` in `.env` before the first start — both
containers read them. Without Docker, leave `S3_ENDPOINT` unset and the ledger stays a plain
file in `logs/`.

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

The Layout Agent writes a ```` ```layout ```` JSON block per page (format:
`agents/layout/role.md`). Every save of `layouts.md` — by the Layout Agent or by you
in the editor — redraws `thumbnails.md`: panel borders, gutters, bleeds, horizon lines,
balloons/whispers/thoughts/shouts with tails pointing at the speaker, captions, figlet sound
effects and figure placeholders, in code and for free. The renderer reports overlapping
lettering, copy that doesn't fit, over-wordy panels, reading-order conflicts, lettering over
faces, tiny panels and left/right page mistakes back to the Layout Agent.

**Light and dark.** Any cell can be shown inverted (light on dark), for night scenes,
silhouettes, flashbacks or emphasis. Inversion is a separate mask stored after each page as a
```` ```invert ```` block (`#` = inverted) and saved as `-pNN-invert.txt`. The Layout Agent sets
it per panel or item (`"invert": true` — which also tells the image model the panel is dark),
and you can paint it in the editor with the **invert brush** or **⌘I**. Review diffs report
inversion changes, and locks keep them.

(The ASCII Artist, which drew full pages in ASCII, is retired to `campaigns/_morgue/ascii_artist/`.)

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

`campaigns/_morgue/` keeps reviewed documents we don't use but don't want to lose, with a README
noting what was adopted from each and why the rest wasn't. It is there so a person can find an
old document again, and nothing in it reaches an agent — the leading underscore is the rule (see
**The library**).

## Running the room

What the screen gives you while the room works, and the controls that decide what it does.

**Holding the room.** **Pause** stops the round at the next clean break: the writer at work
finishes and hands off, and the round waits there — same version, same place in the order,
nothing torn down. While it's held, change any writer's model, temperature or anything else in
**The room**, and jot notes in the watch pad. **Resume** hands both to the writer about to
start and everyone after it (every agent reads `agent.json` when it starts, so the change is
real, and the feed says what changed: `carrying on — Writer B → temperature 0.15 · your notes
go to the writers still to come`). The notes are marked used by that round and saved with it.
**Stop** still ends the round outright, and works while it's held.

**Auto rounds.** **Auto rounds** in **The room** tab runs execution without you. After each
execution round the room hands the round back to itself — every page open, nothing said about any
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
until something takes them: the next round folds them into the room's brief, and
submitting a review adds them to `review.md`; either way they're saved in that round's folder and
marked used. **Tidy into feedback** is one model call (the Director's model) that groups the pile
by theme and drops the text into your note box to edit before sending — it doesn't spend the
notes. **x** drops a note you've changed your mind about.

**Standing rules.** These are a different thing from the campaign's `rules/` folder: that holds
what is true in the book, while these are how you want the room to work. A jotted note is for
the next round only — the room reads it and it's spent. A rule holds for good. In the watch pad,
say **Always**, **Never** or **Remember** and add it; the rule goes into the Director's
`taste-writers.md`, the file every writer reads before it starts, in a block the room doesn't
own:

```markdown
<!-- showrunner rules -->
## The showrunner's standing rules
- **Always:** open every chapter on a wide establishing shot
- **Never:** put narration captions on a character's face
<!-- end showrunner rules -->
```

The Director rewrites that file every round, so the block is put back on every save and the
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

**Outputs.** The **Pages** tab has the page prompts (Copy / Copy all) and the main story files.
Every finished round, review and finalize also writes `page-prompts.md` and
`pages/pNN-prompt.md` to the campaign's `output/`, beside the script and the layouts that
produced them — overwritten each time, with every earlier round kept under `output/previous/`.
**Save to output folder** does it on demand. There is nothing to fetch: the files are in
`campaigns/<slug>/output/` on your disk.

**Page numbers.** Every page prompt asks for the page number in small light-blue lettering in
the top-left corner (`PAGE 2`). Set **Chapter** in **The room** tab and page 1 reads
`CHAPTER 4 — PAGE 1`.

Intake always pastes the material in full, so `references` and `max_steps` in the Script
Coordinator's `agent.json` do not apply to it — it has no tool loop to step through. What it
does need is `max_tokens` big enough for one whole file per reply; short of that the envelope
comes back truncated and the call is retried.

## The library

**A campaign is the project.** There is no separate `projects/` folder and no separate
`output/` folder: `campaigns/prosperity/` holds the whole of it, and opening that folder is
opening the work. The Script Coordinator reads `rules/`, `input/`, `drafts/` and `references/`, and the room writes `output/`, which is the desk
the agents share — the script, the layouts, the page prompts, the settings, and every finished
round under `output/previous/`.

**The room never reads its own `output/` back as material.** A round that took its own last
script as input would be working from its own echo, and the drift compounds every round, so
`never_read` in `app/projects.py` skips `output/` the way it skips an underscore folder. The
desk still reaches an agent — under its own file names, as the project's own work — which is a
different thing from reference material.

The campaign folders are what the room calls the **library**, and one agent reads it: the
**Script Coordinator**, the Director's assistant and the whole of the intake phase, who goes
through every file the round picked — `rules/`, `input/`, `drafts/` and `references/` — and
sorts it into the three files the room works from:

| File | Holds | Who takes it over in development |
|---|---|---|
| `characters.md` | the people: look, voice, wants, relationships | Character Designer |
| `world.md` | how the world works: places, systems, money, technology | Director |
| `story.md` | what happens: what you are reaching for, the beats so far, then the structure and the page-by-page plot | Plotter |

Every point is cited and keeps its T / EG / S / L label, and each file ends with an **Open**
list: what your material leaves undecided or contradicts itself on. You approve the three
files at the first gate. In development their owners decide what is open and build what is
missing, in the same files — there is no second copy — and the Director's `brief.md` says what
the book is and wins wherever it differs. The Script Coordinator organizes; it decides
nothing. A file reaches it under its real path, `campaigns/<campaign>/<folder>/<file>`.

**Intake is five passes, and the room writes the files.** The Script Coordinator has no tools.
The room builds every prompt, parses the file envelope that comes back, checks it and writes
the files itself.

| | pass | in | out |
|---|---|---|---|
| 1 | **synthesis** | everything in `input/`, `rules/`, `references/` | `characters.md`, `world.md`, `story.md` — **three calls at once** |
| 2 | **open items** | those three, your own open-items list — **no references** | `open-items.md`, questions only |
| 3 | **options** | those items, the three files, `references/` | `open-items.md`, every item answered, plus what the research exposes |
| | *the run stops and waits for you* | | |
| 4 | **revision** | your decisions and notes, the three files | the three files **in parallel**, then what is still open |
| 5 | **facts** | the settled three files | `facts.md` |

**Throw your material in under any names.** There is no file you have to create first.
`input/` is whatever you have — `brainstorm.md`, `rough-chapter-1.md`, `pitch.txt`,
`notes-to-self.md`, an old outline, a half-finished `characters.md`. Intake reads each one and
works out what it holds; making the structure is its job, not something you do before calling
it. Early drafts go in `input/` too — a separate `drafts/` folder still works but is not
needed. `.md` and `.txt` are both read.

**Every specialist gets the whole room, but only one job.** Pass 1 is three calls running at
the same time, one per file, each reading all your material; pass 4 is the same, then the
open-items list. This is measured, not theoretical: asked for several long files in one reply,
the model wrote the first properly and thinned out, delivering 38–52% of the source with the
last file half empty. Each call now has its own output budget.

Reading broadly is the other half of it. A character fact turns up in a chapter draft, a world
rule in a line of dialogue, a story beat in a character note — so nothing is routed by
filename. Every call sees everything and takes what belongs to it.

The three calls are independent views of one snapshot, and they may read an ambiguity
differently — `characters.md` saying Leona chose exile while `story.md` says she was forced
out. That is fine. Pass 2 exists to catch exactly that, and there is no hidden reconciliation
step in pass 1. Each call validates and retries on its own, so a file that came back fine is
never thrown away because a sibling failed.

**One artifact per reply, and formatting is the room's job.** Each call returns the plain
markdown of its file — no envelope, no markers. A code fence, a stray marker or a line of "Here
is the document" gets stripped. Then the room *repairs* the shape rather than rejecting it: a
characters file whose names came back at `##` with no `## Characters` wrapper gets the names
demoted and the wrapper added; bolded field lines in `open-items.md` (`- **file:** x`) are
rewritten so the screen can read them; unnumbered items get numbered; a missing title is added.
Every repair is logged in `run.json` and shown in the feed.

**Whatever the model returns is used.** There is exactly one reason to make a call again: the
reply came back empty. Everything else is written down and carried on with. A short file, an
items list the parser cannot read, an option with no source label, a file that ran to the token
ceiling, something that reads more like a refusal than a document — all of it is noted in
`run.json` and shown in the feed, and all of it is used. A model is a model, not a
deterministic function; spending another call and throwing away what it wrote is the wrong
answer to a formatting problem. Shaping the result is the room's job, afterwards.

Each call gets a 64,000-token output budget, near the model's ceiling, so a file that should
run long runs long instead of coming back cut off.

**`facts.md` comes last, and only after you have decided.** It is a continuity ledger derived
from the settled project — ages, dates, who is related to whom, how a device works, what is
locked — for the Continuity Editor to check pages against. It is never an input to synthesis,
and it is not a mirror of your rules: a rule that shapes how the book is written but settles
nothing about the world produces no line in it.

Pass 1 organizes and enriches; it does not resolve. Pass 2 finds the gaps and is deliberately
the one pass with no research in reach — a reader holding a shelf will use it to make a thin
file look finished, and then what it reports missing is not really missing. Pass 3 is the only
pass that proposes answers.

**Pass 3 also challenges the book against the research.** It is the first pass to see the
shelf, so it is the only one that can catch what the project's own documents never could:
fictional geology that conflicts with real geology, a journey that cannot take that long, a
legal mechanism implausible in the jurisdiction intended, a technology that breaks the hard-SF
rules, an economy that does not work the way the book says. Three documents agreeing with each
other is not evidence they are right about the world. Where research materially challenges
something the project proposes, Pass 3 raises a new item marked `from: research-check` and
gives it options on the spot — not because the shelf holds more detail than the book needs,
but only where ignoring it would cost you plausibility, continuity or credibility.

**The room checks each call:** all the files present, none empty, none truncated, each reading
like the document its name promises, every option in pass 3 carrying a source label. A call
that fails is retried — the same call, with every problem seen so far plus the standing bar —
up to three times, then the run fails. It does not advance and it does not report done.

**The files are working source documents, not summaries.** The room writes the book from them
and never sees your sources again, so a page-by-page draft stays page-by-page: beats,
decisions, consequences, reveals, dialogue worth keeping, on-screen text, numbers, objects,
specific actions and the causal link between one beat and the next. Duplication collapses;
detail does not. Reducing a detailed chapter to a synopsis is the one failure the synthesis
guides warn about hardest.

**Preservation is telemetry, not a gate.** Passes 1 and 4 are measured against what they were
given — what share of the distinctive names, terms and numbers survived, and the rough mass
ratio — across the whole set rather than file by file, and against your own material and rules,
never the research shelf. Dropped terms are sorted into numbers, names and terms, on-screen
text and craft vocabulary, so you can tell a lost measurement from a lost formatting word; a
second coverage figure ignores the craft vocabulary entirely. Below 85% coverage or 30% mass it
says so, in the feed and in `run.json`. It never discards a reply and never re-runs a pass, and
none of the categories is a failure condition. The numbers are there to compare models and
prompts, and to tell you a synthesis is worth reading closely before you approve it.

**The guard never measures research.** It compares against `input/` and `rules/` only. The
shelf is there to make the book better and most of it should rightly leave no trace; measuring
against it would demand the files transcribe your research.

**Research is part of the creative loop.** Have the idea, find the real-world material that
makes it richer, stranger or more specific, put it in `references/`, and intake uses it twice —
in pass 1 while it shapes the project, and in pass 3 to ground the options. So
`use_references_during_synthesis` defaults to **on**. What research may not do is become canon
by being plausible: a point from the shelf is cited and marked as real-world reporting, and
anything built on it is written as a proposal and raised as an open item. Set the flag to
`false` for a consolidation run.

**Open items: the room proposes, you decide.** Passes 2 and 3 write `open-items.md`: every gap
and contradiction the three files leave, numbered, each with

**Open items are reconciled, never restarted.** Pass 2 works from two independent sources: the
questions it finds in the new synthesis, and every open item that already existed — the list on
the desk from the last round, with whatever you edited into it, plus an `input/open-items.md`
if you keep one. For each prior item it decides: still unresolved (kept, in your words, with
your proposed solution), resolved by an explicit decision or a binding rule or material that
now directly settles it (removed), partly resolved (rewritten around what is still uncertain),
a duplicate (merged, keeping your wording), or contradicted by the synthesis (kept — the
disagreement is evidence). What comes back is one reconciled list, each item marked `from:`
showrunner, script coordinator or both.

**A question does not disappear because the synthesis forgot it.** A working document stating
one version confidently settles nothing — very often it has just carried the problematic
version forward, which is why you raised the item. Pass 2 is told this explicitly, with a
worked example.

**Every option says where it comes from.** Pass 3 labels each one **[established]** in your own
material, **[research]** from the shelf, **[inferred]** from the four files, or **[invented]**,
with its source — so a plausible suggestion never reads as something the book already settled.
A pass 3 reply with an unlabelled option is rejected and asked again.

**Three things you can do with an item.** **Answer** it — on either screen, which writes it to
`rules/decisions.md`, or with a `- decision:` line in `output/open-items.md`. **Defer** it with
a `- defer: <why>` line, which leaves it open on purpose and holds nothing up; pass 4 must not
quietly answer it. Or leave it alone.

**Notes carry weight.** Not everything you want to say answers a question: "Adrian should stay
morally ambiguous", "Oasis should feel more desirable and less sterile", "give Bi11bot slightly
more humour". Write those in a `## Feedback` block at the end of `open-items.md`, or attach one
to a single item with `- feedback:`. Mark each with **[HIGH]**, **[MEDIUM]** or **[LOW]** — an
unmarked note is MEDIUM:

- **[HIGH]** must materially shape all the revision work it touches.
- **[MEDIUM]** shapes the relevant material unless something with more authority says otherwise.
- **[LOW]** is a preference: used where it improves the work, never at the cost of an unrelated
  change.

Pass 4 is given them with the authority of a rule for that run. Where a note and a decision
pull against each other, the decision says *what is true* and the note says *how it reads*.
Notes are *not* written into `rules/` — promoting one to a permanent rule is yours to do.

**Pass 4 and 5.** **Run intake again** and the round is a revision: each answer goes into the
file it belongs to, stated as settled and cited, followed through every other file it touches;
your notes shape how all of it reads; deferred items stay put; and `open-items.md` comes back
holding only what is still open. It is a controlled revision, not another synthesis — nothing
unrelated changes and nothing may fall out. The shelf is absent unless a decision rests on it.
Then pass 5 derives `facts.md` from the settled project.

The round picks its own mode: revision when the three files exist and anything is waiting — an
answer *or* a note — and a fresh synthesis otherwise. Post a round with `{"mode": "synthesis"}`
or `{"mode": "revision"}` to override.

**How a round ends.** Passes 1–3 leave it `awaiting_showrunner_decisions`; a finished pass 5
leaves it `ready_for_review`. Neither is `done`, and `run.json` also records which files this
run generated, which were carried forward, and which **you** edited by hand since the last
round.

**Other mediums.** The pipeline does not care whether the book is a graphic novel, a novel, a
screenplay, a game or an audio drama. What changes is `craft.md` and the expected shape of
`story.md`; `characters.md`, `world.md`, `facts.md` and `open-items.md` stay as they are.

**Under the hood.** All three synthesis calls work from one snapshot of the material, recorded
in `run.json`, so a set of files can never be half from one state and half from another. They
share an identical system prompt and payload prefix — only the last few lines differ — so a
provider that caches prefixes can reuse it. Each call gets its own 30,000-token output budget,
and the room warns if a prompt goes past a soft ceiling well below the model's advertised
window, since an advertised context is not a good working range.

**Two ways a book starts, one path through the room.** From scratch, `drafts/` is empty and
`input/` holds raw notes: the three files come out thin with long Open lists, and development
does most of the building. With chapters already written (Prosperity), they go in `drafts/`:
`story.md` starts as the beats of what exists and `characters.md` as the people the way the
drafts play them, and development is mostly deciding what to keep. Drafts are idea drafts
either way — the room writes its own version.

One folder per campaign, and the same words inside each, so a person opening any folder knows
what they are looking at:

```
campaigns/
  prosperity/
    rules/          what the book must not contradict: hard-sf-rules.md
    input/          anything you want read, any quality: notes, sketches, plans — empty for now
    drafts/         pages or chapters already written: the script draft. Empty when a book starts from scratch
    references/     material to draw on, grouped for your own sake
    output/         the room's desk: script, layouts, page prompts, previous/
  avalanche/        the second campaign: the same folders
  _morgue/          clippings kept for people, so an old document is never lost
```

**One question decides where a file goes: does it bind the book?** `rules/` binds — the bible,
each chapter's own truth, who each character is. (Not to be confused with **the showrunner's
standing rules**, which are how you want the room to work and live in `taste-writers.md`.)
Nothing else in a campaign binds: `input/` for anything you want read at any quality,
`drafts/` for what is already written, `references/` for material to draw on, `output/` for what the room wrote.

**Only `rules/` binds**, so a folder you invent inside a campaign is non-binding by default —
group your material however suits you, and you cannot turn a rough note into canon by filing it
somewhere. `references/` is research about the real world, and part of the creative loop: read in intake's
first pass to enrich the project and in its third to ground the options, never canon until you
approve it. It is otherwise a folder for your own sake, read the same way `input/`
is read.

**The pitch is optional, and it is input.** If you want to say what the book should be, write
`input/pitch.md`; the Script Coordinator reads it with everything else and carries it into the
three files. No agent is handed it separately, and nothing in `output/` steers intake: the
desk starts empty.

`input/` is the heap, and it is meant to be one: a reference document, a prompt that worked,
rough notes, dropped in without deciding anything first. The room reads it, mines it, and is
never bound by it.

**Nothing in the code decides whether a document is worldbuilding or reporting.** A
document says what it is in its own words — its title, its frontmatter, its first line — and the
agent reading it works that out. `triangle-money.md` opens with "Grounded worldbuilding for what
money is like…"; `hard-sf-rules.md` opens with "How a grounded story invents things without lying to the
reader." Those sentences
are the classification, and they are also what a person reads. There is no marker to write:
if you want the hard SF rules to bind the book, the document goes in `rules/`, which is where
Prosperity keeps it. The one folder that does say what a file is is `drafts/`: a draft is read for what
happens in it and how its people talk, and reaches the Script Coordinator under its own heading.

A file is
named by its path, so `prosperity/rules/chapter-04.md` and
`prosperity/drafts/chapter-04.md` are two different things and are read as what they are.
A new campaign is `mkdir -p campaigns/<name>/{rules,input,drafts,references,output}`, which is what **+ New campaign** does.

And a third rule that is only a naming convention: **inside the library — `campaigns/` — a
folder whose name starts with an underscore is not library material.**
The room skips it when it lists the library, when a round carries references into a prompt, and
when an agent asks for a file by name; `never_read` in `app/projects.py` is the whole of it, and
there is no list of special folder names anywhere. Those folders are for people. (An agent's own folder is not library material
either, so the underscore says nothing there: `agents/_shared/` is given to every role.)

**A campaign reads its own folder and never another campaign's.** That is a folder rule, not
a setting: the room only ever walks `campaigns/<the campaign that is running>/`. Material two
books share is copied into each (`hard-sf-rules.md` sits in both campaigns' `rules/`). So Prosperity is not told about emperor penguins because Avalanche exists, a new
campaign cannot reach into the others, and a file you drop into a campaign's `input/` is read
the moment you save it, with nothing to add to a list. It holds for a file asked for by name
too, so an agent cannot read across the boundary either.

**Within that, a campaign picks what it uses** — **References…** in **The room** tab lists both
folders; default: all of them. The summary beside the picker shows how many KB the Script Coordinator
will carry. With references in place the pitch is optional. Each round keeps a copy of the references it used, and `run.json` records
a hash of each.

The campaign's files are the campaign's files: edit them in place. The scripts that once
split a long source document into them were one-off utilities for importing older material,
and they are retired to `campaigns/_morgue/utilities/`.

**What a reference is.** Four kinds, each arriving under its own heading so the Script Coordinator is
told which it is reading:

| Kind | Where it comes from | What the room does with it |
|---|---|---|
| rules | a campaign's `rules/` | must not contradict it; where it conflicts with the room's files, the rules win |
| drafts | a campaign's `drafts/` | what is written so far: the best evidence of the story and the voices, and still an idea draft — it binds nothing, and the room writes its own version |
| input | a campaign's `input/`, or anywhere else in it | your own material, under any names: brainstorms, fragments, notes, rough chapters, old outlines, earlier structured files. It binds the book to nothing and none of it has happened. What each document *is* comes from the document, never from its filename. `.md` and `.txt` |
| references | a campaign's `references/` | research about the real world, gathered to feed the creative work. Pass 1 reads it to enrich the project (unless you turn `use_references_during_synthesis` off) and pass 3 reads it for options labelled **[research]**; passes 2, 4 and 5 never see it. Nothing here becomes canon by being plausible — it becomes canon when you approve it |

`rules/alpha.md` is the case in point for the one question a folder answers: it
arrived as a craft skill, but it is who Alpha is rather than a menu of options, so it sits in
`rules/` and binds the book.

The skills label their material with the vocabulary in
the campaign's `rules/hard-sf-rules.md` — **T** truth, **EG** educated guess, **S** speculation, **L** license,
**Cut** — along with the rules for a license, the license log and the Thorne and Tyson tests.
Writers keep those labels when they use guide material, and the Continuity Editor's
**plausibility ledger** reports unlicensed inventions, licenses that contradict a truth beside
them, and a license used to skip work the characters should have done.

**Only the Script Coordinator reads the library, and the room reads its three files.**
`characters.md`, `world.md` and `story.md` go to the Director, the Plotter, the Character
Designer, the writers, the Layout Agent and the Continuity Editor. (The First Reader reads cold
and the Letterer reads only the pages, so neither gets them.) `facts.md` is the
fact-checker's list — every checkable statement in the material, one per line, tagged with the
material's own label and its source — and the Continuity Editor reads it beside the book. An
agent that asks `read_artifact` for a file under `campaigns/` is refused and pointed at the three files.

## Guiding the agents

Everything an agent knows comes from its folder:

```
agents/
  agents.json             title, mission, reads, outputs
  phases.json             the five phases: who runs in each, in order, and each gate
  tools/                  what an agent can call: one json schema per tool
  _shared/                given to every agent: house-style.md, craft.md, the provocation deck
  _writers/               given to both writers: role.md, craft.md, actual-script-writing.md
  <agent>/
    role.md               the job: what it delivers, in what format
    craft.md              the craft: how to do that job well
    agent.json            provider, model and tuned defaults (committed; no keys)
    images/               reference images (png, jpg, webp, gif)
```

- **Change how an agent works:** edit its `role.md` or `craft.md`. Every `.md` in the folder is
  sent to the model, `role.md` first, so a new guide is a new file.
- **Long craft references** are just more `.md` files in the folder that needs them: the
  Layout Agent carries four (layout, panel picking, set design, emotion), the writers one
  (`actual-script-writing.md`). They are sent after `role.md` and `craft.md`.
- **Add references:** drop images in `images/`. They're sent to the model, so use a vision-capable model or set `SEND_IMAGES=false`.
- **Change what a tool says:** edit its file in `agents/tools/`. The `description` and
  `parameters` are what the model sees, so the wording steers behaviour; `_why` lines are
  comments for the next person. An agent gets every implemented tool unless its `agent.json`
  names a `tools` list, `write_artifact` refuses any file that is not its own output, and
  `generate_image` needs `generate_images: true`. A cold reader (`"context": "minimal"`) gets
  `write_artifact` and `finish` only, so it can neither browse the room nor be provoked.
- **Add or change an agent:** edit `agents/agents.json`, create the matching folder, and name
  it in a phase in `agents/phases.json`. `"context": "minimal"` gives it
  only its own folder and its `reads` — no shared guides, references or tools to
  browse the room (the First Reader uses this).
- **Random entry:** the `provoke` tool deals 3 cards from `agents/_shared/deck.txt` (one move
  per line), a word from `words.txt` and a random heading from the story or script as a
  target. Drawn by code, so it is not an idea the model talked itself into, and pulled rather
  than dealt: a writer asks when the obvious version of a beat is the one it keeps writing, and
  a writer who isn't stuck pays nothing. The draw shows in the live feed.

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
| Director | 0.6 | 6,000 | judgment and consistency; sees reference images |
| Plotter | 0.9 | 8,000 | structure with surprises |
| Character Designer | 0.7 | 8,000 | exact, reusable descriptions; sees reference images |
| Writer A | 0.7 | 16,000 | the spare, image-led voice; the longest output, 600 s timeout |
| Writer B | 1.0 | 16,000 | the dialogue-led voice; same budget. Give the two different models if you can |
| Layout Agent | 0.5 | 16,000 | valid layout JSON for every page |
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
| `references` | Script Coordinator only: `"full"` (the chosen library files go into every call) or `"list"` (names and sizes only, read on demand). |
| `generate_images`, `image_*` | Image generation (art room). With no `image_base_url`, images use the chat provider and key (or `IMAGE_BASE_URL` / `IMAGE_API_KEY` if set). |

A bad `agent.json` is flagged on the card and blocks runs that include that agent.

## Rounds, runs and images

- Every run is a round — **Run selected roles only** too — starting from the current working copy (including your manual edits) and recording every write. A stopped or failed run still leaves a complete round.
- Images (art-room roles, or chat replies that include images) are saved with round-prefixed names in `images/`, so nothing is overwritten.
- Pick a round from the **Files** dropdown to browse its files, replay its feed, see its model calls, or **Restore** its book files into the working copy.

## Search

Everything the room can read is indexed for hybrid search: each campaign's `rules/` and
`input/`, the craft skills, and each campaign's own desk. A scope is the folder a file sits in
(`prosperity/rules`, `prosperity/input`, `skills`) or `project:<slug>` for the desk, so a search
can ask one campaign or one part of it without knowing file names. Deleting a file drops its
passages: `indexed_as` in `app/search.py` rebuilds the key the file was indexed under, because
by then the file is gone and cannot be looked up.

- **Keywords** — BM25 in OpenSearch over the passage, its heading path, and the keywords drawn
  from it. A term that is common in one passage and rare everywhere else is a keyword, so a
  record carries *brine*, *cooperative*, *Evokation* rather than *page* and *the room*.
- **Meaning** — `embeddinggemma`, served by Ollama on your machine. Local, free to re-run.
- **Hybrid** — both at once, normalised and combined by OpenSearch's own pipeline, so
  `balloon tails` and `how does a family here talk about money` both work.

A passage is a markdown section carrying its heading path, so a hit reads
`triangle-money.md › The big truths › Three countries, three money cultures` instead of naming a
22 KB file. Indexing is keyed by content hash — an unchanged passage is never re-embedded — so
the first pass over this library is 763 passages and a few minutes of embedding, while a full
pass with nothing changed walks the same 763 and re-embeds none of them in about half a second.

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
change: **an edit is searchable a second or two after you save it** — 0.16 s for a host save to
reach the container, up to 0.5 s of poll, then chunking the one file, embedding what changed
(0.15 s a passage) and a refresh. The same applies to what an agent writes mid-round, so a page
the Layout Agent has just written is searchable while the round is still going.

One changed file costs one file's work: the passages it lost are dropped, the ones it gained are
embedded, everything else is left alone. Rewriting one passage of a 22 KB file re-embeds that
passage and leaves the other twenty alone.

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
| `list_projects` | the campaigns you can run, by name |
| `list_artifacts` | a project's room files and its reference material |
| `read_artifact` | one file, e.g. `script.md` or `campaigns/prosperity/rules/alpha.md` |
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
`docker compose up -d --build app`, and the browser caches
the app's own JS and CSS (a hard reload picks up a new build).

## Call logs and costs

Every model call — chat and image, successful or failed — is recorded three ways:

```
rounds/<slug>-r03-ai/calls/<slug>-r03-ai-call-0007-writer-a-chat.json   full request + response
rounds/<slug>-r03-ai/<slug>-r03-ai-calls.jsonl                           one summary line per call
logs/usage.jsonl                                               the same lines, across all campaigns
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

1. The system prompt is the agent's mission plus its guides (`role.md`, `craft.md`, the shared ones).
2. The first message is the upstream files listed in `reads`, any previous draft, the phase it is running in, your note, and the images.
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
