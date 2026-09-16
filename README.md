# Writers' Room

A web-based, agentic writers' room for graphic novels whose product is **ASCII pages**.
Give it a directional draft script and a page count; the room writes until the pages are
ready, you review every page (👎 re-roll · 🔥 love it · ✏️ approve with changes, editing the
ASCII in place), and the room revises from your verdicts, edits and diffs — round after
round, each saved in full. Every role is guided by its own markdown, images and Figma files
and runs on its own provider, model and settings; every model call is logged with its tokens
and dollar cost.

The art room — which will take these ASCII pages and the brief, with its own taste — is a
separate, later room. Its roles (Image Thumbnailer, Colorist) are marked `"room": "art"` and
are hidden here.

| Order | Role | Writes | Notes |
|---|---|---|---|
| 1 | Editor-in-Chief | `brief.md` | owns canon and the decision log |
| 2 | Plotter | `outline.md` | |
| 3 | Wild Card | `provocations.md` | off by default; proposes, never decides |
| 4 | Character Designer | `bible.md` | draws character sheets |
| 5 | Scripter | `script.md` | |
| 6 | Penciller | `layouts.md` (+ `thumbnails.md`) | layout blocks drive the ASCII page previews |
| 7 | ASCII Artist | `thumbnails-drawn.md` | draws each page in ASCII — the pages you review |
| 8 | Letterer | `lettering.md` | optional; reads the thumbnails |
| 9 | Continuity Editor | `notes.md` | ends with `BLOCKERS:` / `FIX:` lines the gate reads |
| 10 | First Reader | `first-read.md` | off by default; cold read of the pages, reactions only |

The Editor-in-Chief also keeps `taste-writers.md`: what you love and hate, learned from your
reviews, which every writer reads. Everything is labeled canon, observation, proposal, risk
or decision needed (see `roles/_shared/house-style.md`).

## Writing rounds and review

1. **New project** — title, page count (e.g. 7), an optional pitch, and an optional draft
   script (high level, directional; saved as `references/draft-script.md`).
2. **Write round** — the room runs Editor → Plotter → Character Designer → Scripter →
   Penciller → ASCII Artist → Continuity Editor, then checks the **readiness gate**:
   exactly the right pages, zero layout issues, zero continuity blockers, and locked pages
   matched. If it fails, only the roles that can fix it run again (up to **Fix passes**,
   default 2). Readiness is measured, not the model's opinion.
3. **Review** — step through the pages (‹ › or the chips). Each page needs one verdict:

   | | Verdict | What happens |
   |---|---|---|
   | 👎 | **Re-roll** | the next round rewrites the page, keeping what flows in and out of it |
   | 🔥 | **Love it** | locked — script section, layout and ASCII never change again |
   | ✏️ | **Approve with changes** | only once you've **edited the page or commented**; your page is locked and the room brings script and layout into line with it |

   The page is editable right there (see *Editing a preview in place*). Your verdicts,
   comments and edits are saved as you go.
4. **Send to the room** (when anything isn't 🔥) or **Finalize** (when nothing is 👎) —
   both need every page decided. Sending saves your review as a human round and starts a
   revision round that works only from it: the Editor updates the brief and the taste file,
   the Scripter and Penciller fix the flagged pages, the ASCII Artist redraws only pages
   whose layout changed, and the gate checks that ✏️ pages now match yours
   (`min_text_match` / `min_layout_match` in `round-settings.json`).

Locks are enforced in code: whatever an agent writes, locked pages are put back.

### The text rule

Letters, digits and `. , ! ? ' " - : ;` appear **only as text** (dialogue, captions, sound
effects, signs); art uses every other character. So a page splits into a text layer and an
art layer, and a diff is a clean dialogue diff plus an art diff. The renderer follows the
rule (panel borders `_ |`, balloons `_ ~ ( ) / \`, captions `+ = |`, figures filled with
`% # @ & $` — the legend says who is who), and text characters in model-drawn art are swapped
for art characters automatically. Your edits are diffed the same way: text changes are
listed word for word, art changes as before/after crops by panel.

## Rounds and file names

Every round is a complete folder, and every file name carries the project and round, so a
file means the same thing wherever it ends up:

```
projects/<slug>/rounds/
  <slug>-r01-ai/        the room's pages
    <slug>-r01-ai-script.md, -layouts.md, -brief.md, -taste-writers.md …   book files
    <slug>-r01-ai-p03-ascii.txt      the page you review
    <slug>-r01-ai-p03-render.txt     the layout render
    <slug>-r01-ai-p03-script.md      the page's script section
    <slug>-r01-ai-p03-layout.json    the page's layout block
    <slug>-r01-ai-run.json, -events.jsonl, -calls.jsonl, calls/<slug>-r01-ai-call-0007-….json
  <slug>-r02-human/     your review
    <slug>-r02-human-review.json / -review.md          verdicts, comments, instructions
    <slug>-r02-human-p02-ascii.txt / -p02-ai-ascii.txt your page and the AI page it came from
    <slug>-r02-human-p02-diff.md                       text and art diff
  <slug>-r03-ai/        the revision
  <slug>-r04-final/     the approved book, plus <slug>-r04-final-book-ascii.txt
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

**Configuration** — `roles/`, `hats/`, `references/` and `pricing.json` — is mounted from this
folder, so you edit it in place.

**Project data** — `projects/` (every round, page, review and call log) and `logs/` — lives in
**SeaweedFS**, an S3-compatible object store whose storage is the `seaweedfs-data` Docker
volume. The app works on a copy inside its container: on start it pulls everything from the
bucket, then pushes changes (including deletions) every `S3_SYNC_SECONDS` (2 s) and once more
on shutdown. Recreating or rebuilding the app container loses nothing; so does
`docker compose down`. **`docker compose down -v` deletes the volume, and all project data
with it.**

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

## ASCII page previews

Page previews are ASCII art at **print scale**: one character cell is one letter of
lettering. At `LETTERING_PT=7.5` a cell is ~0.057" wide and one lettering line (0.125")
tall, so a 6.625" x 10.25" page (`PAGE_TRIM`) is 116 x 82 cells, and a balloon in the
preview is the size it will be on the page. The UI draws cells at that same 2.18:1
ratio, so pages show in their true proportions.

Three methods, compared side by side under **Page previews**:

1. **Layout render** (always) — the Penciller writes a ```` ```layout ```` JSON block per
   page (format: `roles/penciller/layout-format.md`). Every save of `layouts.md` — by the
   Penciller or by you in the editor — redraws `thumbnails.md`: panel borders, gutters,
   bleeds, horizon lines, balloons/whispers/thoughts/shouts with tails pointing at the
   speaker, captions, figlet sound effects, figure silhouettes. The renderer reports
   overlapping lettering, copy that doesn't fit, over-wordy panels, reading-order conflicts,
   lettering over faces, tiny panels and left/right page mistakes back to the Penciller.
2. **Model-drawn** — the ASCII Artist gets each page's skeleton and draws the art into it,
   one call per page. Borders and lettering are laid back on top, so the model can't damage
   them; size mismatches and overwritten cells are noted under the page.
3. **Image → ASCII** — the Image Thumbnailer asks the image model for a rough sketch of each
   panel (description + the bible's look for each character), saves it, and converts it at
   the panel's exact size: stroke direction picks `- / | \`, darkness picks from ` .:-=+*#%@`.

**Light and dark.** Any cell can be shown inverted (light on dark), for night scenes,
silhouettes, flashbacks or emphasis. Inversion is a separate mask stored after each page as a
```` ```invert ```` block (`#` = inverted) and saved with page files as `-pNN-invert.txt`.
The Penciller sets it per panel or item (`"invert": true`; balloons stay light on dark
panels unless inverted themselves), the ASCII Artist may send its own mask, and you can
paint it in the editor with the **invert brush** or **⌘I** on a selection. Review diffs
report inversion changes, and locks keep them.

Methods 2 and 3 are separate roles, so the Costs view shows what each costs. Pages are
written as they finish, so previews fill in live.

### Editing a preview in place

Each preview is plain markdown — `thumbnails.md`, `thumbnails-drawn.md`,
`thumbnails-image.md` — with one ```` ```text ```` block per page, then the panel legend and
issues. Click **Edit** on any preview to change it on a fixed grid (the page never reflows):

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

Saved pages are marked `— edited` in their heading and are **kept** whenever previews are
regenerated: the Penciller saving `layouts.md` doesn't overwrite them, and the ASCII Artist
and Image Thumbnailer skip them (no model call). If the page's layout changes afterwards,
the page gets a warning. **Revert** drops the mark — the layout render redraws immediately,
the other two on their next run. Past rounds are read-only.

## Morgue

`morgue/` keeps reviewed documents we don't use but don't want to lose, with a README noting
what was adopted from each and why the rest wasn't. Nothing in it reaches an agent.

## Reference material

Put your source material — a script, lore, series bible, style notes — in `.md` files in:

```
references/                     shared by every project
projects/<slug>/references/     this project only (a file with the same name wins)
```

Any number of files works, including none. Every agent gets them as canon, and the Files
pane lists them (read-only). With references in place the pitch is optional. Each round
keeps a copy of the references its run used, and `run.json` records a hash of each.

How references reach an agent is set by `references` in its `agent.json` (default from `REFERENCES_MODE`):

- `"full"` — pasted into the prompt. Every step of the agent's loop resends them, so big files cost more.
- `"list"` — only the names are sent, and the agent reads what it needs with `read_artifact("references/<name>")`. Cheaper, but the agent has to choose to read them.

## Guiding the agents

Everything an agent knows comes from its folder:

```
roles/
  roles.json              order, title, mission, reads, outputs
  _shared/                given to every role
  <role>/
    *.md                  guides — all are read, alphabetically
    images/               reference images (png, jpg, webp, gif)
    figma.txt             Figma URLs, one per line (needs FIGMA_TOKEN)
    figma/*.json          Figma REST API exports, for offline use
    agent.json            provider, model and tuned defaults (committed; no keys)
```

- **Add a guide:** drop a `.md` file in the role's folder.
- **Skills:** long craft skills live in `skills/`, which agents never read directly. `tools/split_skill.py` copies each role only the parts it needs: the storycraft skill becomes `roles/<role>/storycraft.md` (the shared core goes to `roles/_shared/`), and the ASCII art skill and the drawing chapters of the ASCII Art Bible become the ASCII Artist's `ascii-art-skill.md` and `ascii-technique.md`, headed by the page rules that override them. Edit a skill or a map in the script, then run `python tools/split_skill.py`. (`references/` is for story material only: everything in it goes to every agent.)
- **Add references:** drop images in `images/`. They're sent to the model, so use a vision-capable model or set `SEND_IMAGES=false`.
- **Add Figma:** paste a design file, FigJam board, frame or section URL into `figma.txt` (needs `FIGMA_TOKEN` in `.env`). The agent gets a text summary (frames, sections, text, stickies, palette hex values) plus PNG renders of up to 4 frames or sections.
- **Add or change a role:** edit `roles/roles.json` and create the matching folder.
  `"selected": false` leaves a role unticked by default. `"context": "minimal"` gives a role
  only its own folder, the pitch and its `reads` — no shared guides, references or tools to
  browse the room (the First Reader uses this).
- **Random entry:** a role with `deck.txt` (one prompt per line) gets 3 cards drawn by code
  each run, plus a word from `words.txt` and a random heading from the outline or script
  as a target. The draw shows in the live feed.

## Hats

`hats/` holds de Bono's six thinking modes (blue process, white evidence, black risk,
yellow value, red reaction, green possibility). Pick one in the hat menu next to **Run**
and it's added to every selected role for that run; the round records which hat was used.
Hats are modes, not jobs: e.g. run the Continuity Editor in the yellow hat to find what's
worth keeping.

## Per-agent settings

Click **⚙ Model** on an agent's card. Up front: **provider** (OpenAI, OpenRouter, Anthropic,
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

**Each agent's `roles/<id>/agent.json` is committed** and holds its provider, model and
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
| ASCII Artist | 0.4 | 16,000 | one ~9,500-character page per call; keeps the grid intact |
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
| `references` | `"full"` or `"list"` — see Reference material. |
| `generate_images`, `image_*` | Image generation (art room). With no `image_base_url`, images use the chat provider and key (or `IMAGE_BASE_URL` / `IMAGE_API_KEY` if set). |

A bad `agent.json` is flagged on the card and blocks runs that include that role.

## Rounds, runs and images

- Every run is a round — **Run selected roles only** too — starting from the current working copy (including your manual edits) and recording every write. A stopped or failed run still leaves a complete round.
- Images (art-room roles, or chat replies that include images) are saved with round-prefixed names in `images/`, so nothing is overwritten.
- Pick a round from the **Files** dropdown to browse its files, replay its feed, see its model calls, or **Restore** its book files into the working copy.

## Call logs and costs

Every model call — chat and image, successful or failed — is recorded three ways:

```
rounds/<slug>-r03-ai/calls/<slug>-r03-ai-call-0007-scripter-chat.json   full request + response
rounds/<slug>-r03-ai/<slug>-r03-ai-calls.jsonl                           one summary line per call
logs/usage.jsonl                                               the same lines, across all projects
```

A summary line has: project, round (`version`), role, kind (`chat`/`image`), provider host, model,
input / cached / image / output / reasoning tokens, `cost_usd`, `cost_source`, duration,
HTTP status, error, and the path to the full log.

- **Cost** comes from the provider when it reports one (`usage.cost`, which OpenRouter returns). Otherwise it's worked out from `pricing.json` (USD per 1M tokens, or `per_image`). A model found in neither is logged as `unpriced` and flagged in the UI. **Check `pricing.json` against your providers' current prices**; the file reloads automatically when you change it.
- **Images** inside requests and responses (base64) are saved once to `calls/blobs/` and replaced by `<blob:calls/blobs/…>`, so logs stay readable. API keys are never logged.
- **In the UI:** each call shows its tokens and cost in the live feed, and role cards show what their last run cost. The **Costs** section breaks spending down by role, by provider/model, by role × provider/model, and by chat vs image, for this project, a selected round, or all projects. A round's **Model calls** button lists its calls, with links to the full JSON.
- **Your own analysis:** `logs/usage.jsonl` loads straight into pandas: `pd.read_json("logs/usage.jsonl", lines=True)`.
- **Totals:** each round's `run.json` has a `usage` block with totals per role.

## How an agent works

`app/agent.py` is a plain loop:

1. The system prompt is the role's mission plus its guides and Figma summaries.
2. The first message is the pitch, the upstream files listed in `reads`, any previous draft, your note, and the images.
3. The model calls tools — `list_artifacts`, `read_artifact`, `write_artifact` (its own outputs only), `generate_image` (if enabled) and `finish` — until it calls `finish` or stops calling tools.
4. The handoff note is appended to `room-log.md`.

If the endpoint rejects tool calling, the agent retries as a plain chat and saves the reply as its deliverable.

## Limits

- One run per project at a time.
- With the object store, up to `S3_SYNC_SECONDS` of writes can be lost if the app container is killed without a clean stop.
- Live runs are tracked in memory: restarting the server during a run ends it. The run's round keeps everything written up to that point, but its status stays `running`.
