# Writers' Room: operations notes (VM, proof, lettering)

What was learned running the Prosperity book on the VM, 2026-11-04 to 11-06.
Read this before changing the VM, the proof or the lettering.

## 1. The VM

| What | Value |
|---|---|
| Site | https://34-123-63-255.sslip.io (signed in) |
| GCP | project `voltaic-quest-502915-u7`, zone `us-central1-a`, instance `writers-room` |
| Repo on the VM | `/home/nathan/writers-room`. The checkout is `prosperity-showrunner` (8a861ae) plus files copied in by hand |
| Book | `campaigns/prosperity-book` (about 10 GB, mostly renders) |
| Containers | `writers-room-app-1` (the app), plus caddy, opensearch, seaweedfs, sheets, art and filebrowser |
| Disk | 49 GB, about 19 GB free (2026-11-06) |

**SSH**:
```sh
gcloud compute ssh writers-room --project voltaic-quest-502915-u7 --zone us-central1-a --command '...'
```
- You arrive as `nathanverrill`, not `nathan`.
- `/home/nathan/backups` is owned by root, so use `sudo` there.

**Inside the app**:
- The app answers on `http://localhost:8000` with no sign-in. Use curl from the VM for the API.
- The app keeps job state in memory, for example `studio.final_state`. A new process started with `docker exec ... python` sees an empty `{}`.
- So read a job's state from the API. For final lettering, that's `GET /api/projects/prosperity-book/proof`, which includes `final`.

**Deploying one file** (the app code is built into the image):
1. Back up first (§6).
2. `gcloud compute scp <file> writers-room:/tmp/`
3. `sudo cp /tmp/<file> app/<path>`, which updates the host copy.
4. `sudo docker cp app/<path> writers-room-app-1:/app/app/<path>`
5. **Python files only:**
   ```sh
   sudo docker compose -f docker-compose.yml -f deploy/gcp/caddy.yml restart app
   ```
   Static files (HTML, JS, CSS) need no restart.

Before copying, compare the VM's copy with the commit you last deployed (`md5sum`), so a change made only on the VM isn't overwritten. Before restarting, check nobody is saving work: look for `POST` or `PUT` in `sudo docker logs --since 15m writers-room-app-1`.

**Running a script inside the app**:
```sh
sudo docker compose -f docker-compose.yml -f deploy/gcp/caddy.yml exec -T app python - < script.py
```

## 2. Where a page's data lives

| File | What it is |
|---|---|
| `production/layouts.md` | **Each page's words, speakers, bubble positions and tails.** `lettering.write_spec` writes it and **puts the file's old modification time back**, so its timestamp says nothing about recent edits |
| `production/thumbnails.md` | The ASCII sketches drawn from the layouts. Rewritten on every edit |
| `production/script.md` | The **candidate script**, rebuilt from the layouts after each proof edit (`proof.write_candidate`). It is *not* Bob's draft |
| `drafts/0N-*.md` | **Bob's drafts. Never changed.** Chapter 3 is "The Price of Ownership" |
| `production/chapters.json` | Chapters by page: Prologue 1–4, Ch1 5–16, Ch2 17–35, Ch3 36–59, Ch4 60–78 |
| `production/proof.json` | Approved, locked pages, each with a snapshot of its approved layout |

**Renders** are in `renders/sunburst/`:

| Folder | Contents |
|---|---|
| `art/` | Art with no words |
| `lettered/` | The room's overlay lettering over the art. It costs nothing to rebuild |
| `overlay/` | The overlay layer on its own |
| `lettered-model/` | Pages Sunburst lettered whole |
| `previous/<YYYYMMDD-HHMMSS-mmm>[-label]/` | Copies kept before each redraw or lettering. Folder names **must start with the timestamp** |

- **Which version a reader sees**: the Studio shows the newest lettering made after the art was drawn, by file time (`studio._shown`). A newer overlay therefore hides an older Sunburst page without deleting it.
- **Pages missing a layout**: as of 2026-11-06, `layouts.md` has pages 1–61 only. Pages 62–78 still have old art and lettering but no layout, so they can't be proofed or lettered until they're laid out.

## 3. The proof, then the final lettering

The order, cheapest first:
1. **The Lettering page**, `/letter?p=prosperity-book#<page>`.
   - Check the art with the bubbles off. Pin notes on it and redraw it: about $0.40 a page.
   - Then edit the words, the speakers, and where the bubbles and tails go: free. Each edit rebuilds the overlay and the candidate script.
2. **Approve & lock.** A locked page can't be changed by anything: an editor, the page chat, a layout run or a bring back. Click the button again to unlock.
3. **Final lettering** with Sunburst runs on **locked pages only**:
   ```sh
   curl -s -X POST -H 'Content-Type: application/json' -d '{"pages":[60,61]}' \
     http://localhost:8000/api/projects/prosperity-book/proof/final
   ```
   The Lettering page has a Final lettering dialog that does the same.

**Final lettering facts** (from `logs/usage.jsonl`, `kind: page-letter`):
- **Cost**: $0.27 a page on the first try, up to about $0.89 after 3 tries. The average is **$0.74 a page**: chapter 3 cost $17.71 for 24 pages.
- **Each try takes about 100–130 s.** Sunburst redraws the whole page, then a second model checks it, and it tries again up to 3 times.
- **Pass rate is about 1 in 3.** Chapter 3 passed 8 of 24 (39, 40, 44, 51, 52, 55, 56, 57), and 60–61 both failed. A page that fails the check is still lettered, so look at it by eye.
- **8 pages at a time** (`FINAL_WORKERS`, default 8 in git; the VM ran 4 as of 2026-11-06). 15 pages took 19 minutes; one at a time it would have been about 75.
- **Busy errors** (429, or OpenRouter's in-flight budget) wait 60 s, then 180 s, then try again.
- **Out of credits** (402 with `openrouter_credits`, "Insufficient credits") stops the run, and the pages not started say so. That happened on 2026-11-06: pages 45–59 failed within seconds before the fix.
- **OpenRouter's limits**: OpenRouter publishes no cap for paid models on requests at the same time. The real limit is the credit balance, so keep it well above the cost of a run.
- **Where to watch progress**:
  - `logs/usage.jsonl`: one line per lettered page, with `tries` and `check_pass`
  - the render status file, `status.json` under `renders/`: each page's `state`, `stage` and `error`
  - `GET .../proof`, then `final`

**Seeing and downloading pages**:

| What | Link |
|---|---|
| Studio, where each page shows its newest lettering | `/studio?p=prosperity-book` |
| One page | `/api/studio/prosperity-book/page/p60.png?kind=lettered-model` (or `kind=lettered`, `kind=art`) |
| Whole book, overlay lettering (no Sunburst) | `/api/projects/prosperity-book/render/sunburst/lettered.zip` (78 pages, 214 MB) |
| A page range as the Studio shows it | `/api/studio/prosperity-book/pages.zip?first=36&last=59&name=chapter-3` |

## 4. Rolling back

- **Bring back** in the Studio steps back one saved copy at a time, using the newest folder in `previous/` that holds that page's art. Copies are made only before an art redraw or a final lettering. **Edits to words and bubbles make no copy**, so bring back can't undo them.
- For edits you mean to undo, take a **checkpoint** first. The one made for chapter 4 is `/home/nathan/backups/20261106-ch4-checkpoint/`, with these contents:

| File | Contents |
|---|---|
| `production/` | `layouts.md`, `script.md`, `proof.json`, `characters.md` and `chapters.json` at 07:19 UTC |
| `renders/` | Art, lettered and overlay images for pages 60–78 |
| `ch4-pages.json` | Each page's layout as JSON |
| `before-today/.../layouts.md` | The layouts from before the 2026-11-06 edits |
| `restore-ch4.sh` and `restore_60_61.py` | The one-step restore of pages 60–61. `DRY=1 sudo -E sh restore-ch4.sh` only reports; `sudo sh restore-ch4.sh` restores |
| `sunburst-60-61/` | Copies of the Sunburst-lettered pages 60–61 |

**What the restore does**, in order:
1. Keeps the edited layouts, and copies of the overlay and Sunburst pages, in `previous/<time>-edited-60-61/`.
2. Unlocks the pages.
3. Writes back the old layout blocks.
4. Rebuilds the overlay and the candidate script.
5. Leaves the Sunburst file where it is. The rebuilt overlay is newer, so the Studio shows the original, but the Sunburst link still downloads the lettered version.

To restore other pages, copy the script and change `PAGES` and the source layouts file.

## 5. Known problems (not fixed)

- **Search on the VM doesn't work.**
  - `OPENSEARCH_URL` inside the app is `http://localhost:9200`; it should be `http://opensearch:9200`. It's probably set in the VM's `.env`.
  - There's no Ollama on the VM for the meaning-based search.
  - The log fills with `search: reindex failed: ... Connection refused`.
  - Nothing else depends on search.
- **The VM's code doesn't match git.** The VM checkout is `prosperity-showrunner` plus copied files. Its live code is `proof-approval` (b1046ea), apart from `letter.html`'s page-number-in-the-URL change, which is deployed but not committed.
- **`proof-approval` is merged into `prosperity-showrunner`** (2026-11-06) and pushed; its worktree is under `/private/tmp/...`, so it can be wiped. Use the main checkout.
- **Page 37, panel 2**: "Anything not worth having" still has no tail drawn by Sunburst.
- **The proof's QA findings for 36–59 were never applied** (tails pointing at the wrong figure, reading order, covered faces). Bob's punctuation changes on p39 and p44 were flagged, not changed.

## 6. Backups on the VM (`/home/nathan/backups`)

| Folder | Taken before |
|---|---|
| `20261105-before-bringback-fix/` | The bring-back folder-order fix |
| `20261105-2000-before-proof-deploy/` | The proof deploy: app code, the app inside the container, and a full tar of the book |
| `letter.html.before-hash` | The page-number-in-the-URL change |
| `20261106-before-parallel-lettering/` | The parallel lettering: app code, the app inside the container, the book's `production/` and `drafts/`, and status files (15 MB) |
| `20261106-ch4-checkpoint/` | Tonight's chapter 4 edits (§4) |

A full tar of the book is about 10 GB. Back up `production/` and `drafts/` (15 MB) unless the art itself is changing.

## 7. How to work on this (lessons)

- **Look at the live state before asking or acting.**
  - Who is editing what: `PUT /lettering/<n>` in the logs.
  - Which pages are locked: `proof.json`.
  - What is running: `usage.jsonl`, the status file, and `final`.

  Once, a question about which version to letter was rejected because the answer was already on the VM: the user had re-edited and locked the pages.
- **Back up before every VM change, and deploy only on a go-ahead.** No restart without one.
- **The cheap proof comes before Sunburst.** No Sunburst lettering until the words, the speakers and the tails are approved.
- **Never change Bob's words without an OK.** Edits go to the candidate script, and the drafts stay as they are.
- **Check each lettered page by eye.** The check fails often, and a failed check isn't always a bad page.
- **Report times in Central and money in dollars.** Usage logs are in UTC.
