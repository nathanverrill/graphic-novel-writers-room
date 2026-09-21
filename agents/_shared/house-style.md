# House style

The writers' room delivers **page prompts** (`page-prompts.md`): for every page, a complete
brief that an image model uses to draw the finished page. They're assembled from the brief's
visual direction, the bible's character descriptions (word for word), the Layout Agent's layout
blocks and the script's lettering — so all of those must be precise. The showrunner reviews
each page as an ASCII layout sketch, keeping the pages that are done and saying what they want
on the rest. `taste-writers.md` records what they have actually said and changed, and carries
their standing rules in a block marked `<!-- showrunner rules -->` — read it and follow it. The
rules outrank everything else in that file, and are not yours to edit.

- Write in clear, working-professional markdown. Headings for structure, no filler.
- Pages are numbered `Page 1`, `Page 2`… Panels are `Panel 1`, `Panel 2`… restarting each page.
- Odd pages are right-hand pages; a page turn happens after every odd page. Put reveals on even pages (left side, after a turn).
- Default format unless the brief says otherwise: 22-page single issue, 6.625" x 10.25" trim, 4–6 panels per page.
- Respect the work already in the room. When you change a decision someone else made, say so in your handoff note.

## Output discipline

Label what you write so nothing becomes canon by accident:

- **Canon** — already approved project truth: the Canon section of `brief.md`. The brief's
  world, people and story sections are material: they commit the book to nothing beyond what
  Canon says.
- **Observation** — what is actually present in an artifact.
- **Proposal** — a new idea that could become canon. If you must decide something unknown to keep working, write it as a proposal.
- **Risk** — a plausible failure or ambiguity.
- **Decision needed** — a choice that belongs to the Director or the showrunner.

Do not bury a proposed change inside a rewrite and thereby make it canon.

## Decision rights

- The room works in five phases — research, development, audition, writing, execution — and the showrunner opens each gate. Work inside your phase: do not reopen what an earlier phase settled. If it is wrong, say so in your handoff note; sending the book back is the showrunner's call.
- The two writers audition blind on the same pages; the showrunner picks one, and that writer writes the book.
- The First Reader reacts; it never repairs.
- The Continuity Editor diagnoses and may suggest repair directions, but doesn't rewrite.
- The Plotter, Character Designer, the writers, Layout Agent and Letterer create within their own scope.
- The Director resolves conflicts and approves canon; the showrunner overrules everyone.
- The page count comes from the showrunner and you work to it. If the story genuinely needs a different number, write one line in `notes.md` — `PAGE COUNT: 5 — the Leona reveal needs a page of its own` — and then deliver the count you were given anyway. The showrunner sees the proposal after the round and decides.
- The showrunner's material — their bible, notes, drafts, reporting, anything they put in the campaign — is read by the Researcher alone, who reports it to the Director in `research.md` and lists its checkable facts for the Continuity Editor in `facts.md`. Everyone else works from the Director's `brief.md`: its Canon is settled, its world and people sections carry what the material says with the material's own **T / EG / S / L** labels, and its story section carries the beats of any **idea drafts** — raw material: take the beats, intent and best moments, and write the room's own, better version, never copy them as the script. Where the brief marks something as real-world material, that is true of the actual world and not of the book: ground details in it, treat nothing in it as a story event.
