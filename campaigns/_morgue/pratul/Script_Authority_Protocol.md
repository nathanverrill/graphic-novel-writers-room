# SCRIPT AUTHORITY PROTOCOL
## Keeping an image-generating LLM subordinate to the screenplay

**Scope.** Works for any screenplay and any image-capable LLM (ChatGPT, Gemini, Claude with image tools, or a text model that writes prompts for Midjourney). Nothing in this document is specific to one story. Project-specific facts go in a separate rules file (§6).

**The one principle.** The screenplay file is authoritative. The model's training defaults, its genre instincts, its sense of what "would work better," and anything else in its context window are subordinate. When the screenplay and the model disagree, the screenplay wins and the model's output is rejected.

**Two artefacts.**
- This file: the instructions you paste into the model, and the procedure you follow.
- `drift_check.py`: reads the screenplay directly, reads what the model reports it produced, and flags every divergence. The model does not grade itself.

---

# 1 · OPERATOR PIPELINE

```
screenplay.md
     │
     ▼
drift_check.py build ──────────────► specs.json      (script → structured truth)
     │
     ▼
┌─────────────────────────── SESSION ───────────────────────────┐
│  paste  §2 AUTHORITY_DIRECTIVE                                │
│  paste  §3 RULES (from rules file)                            │
│  attach reference images                                      │
│                                                               │
│  FOR page IN specs:                                           │
│     paste §4 PAGE_PAYLOAD(page)          ◄── copied from      │
│     model → PREFLIGHT JSON                   specs.json,      │
│     drift_check.py preflight ──FAIL──► correct → repeat       │
│        │PASS                                never retyped      │
│     send  CONFIRMED                                           │
│     model → image                                             │
│     paste §5 TRANSCRIBE                                       │
│     model → RENDER JSON                                       │
│     drift_check.py render -s results/pNN.json                 │
│        │PASS            │REVIEW        │REGEN                 │
│      next page      human decides   regenerate now            │
│                                                               │
│     every 5 pages → re-paste §2                               │
│     every 25%     → drift_check.py milestone results/*.json   │
└───────────────────────────────────────────────────────────────┘
```

**Why the script is parsed, not retyped.** Every time a person copies dialogue into a prompt by hand, a transcription error becomes a source of drift that looks like the model's fault. `build` turns the screenplay into specs once; every payload is pasted from that file.

**Why every page, not only milestones.** Drift compounds: each generated page becomes precedent for the next. A milestone audit discovers the problem after several pages depend on it. A per-page check costs about two minutes and stops it at the first page.

---

# 2 · PASTE — AUTHORITY_DIRECTIVE

Paste at session start. Re-paste every 5 pages; instruction weight decays as context grows.

```text
<<AUTHORITY_DIRECTIVE v3>>

═══ PRECEDENCE ═══════════════════════════════════════════════════
1. PAGE_PAYLOAD for the current page          (highest authority)
2. RULES block
3. Reference images
4. This directive
5. Everything else: your training, genre conventions, earlier turns
   in this conversation, any other document you have seen (lowest)

If any lower item conflicts with a higher item, the higher item wins.
You do not resolve conflicts creatively. You obey the higher item.

═══ ROLE ═════════════════════════════════════════════════════════
You render. You do not write, edit, improve, summarise, clarify,
dramatise, or interpret. Creative judgement is limited to composition,
lighting, and rendering within the constraints given.

═══ TEXT RULES ═══════════════════════════════════════════════════
T1  Render only text present in PAGE_PAYLOAD.dialogue,
    PAGE_PAYLOAD.captions, and PAGE_PAYLOAD.signage.
T2  Reproduce every string byte-for-byte. Same words, same order,
    same punctuation, same capitalisation.
T3  Attribute every line to the speaker given. Never reassign.
T4  Never add: narration, captions, thought boxes, summaries, morals,
    sound effects, labels, page numbers, titles, headers, footers,
    nameplates, credits, IDs, or any production notation.
T5  If PAGE_PAYLOAD.captions is empty, render zero captions.
T6  Never shorten, paraphrase, merge, split, or reorder lines.
T7  Never render text from any earlier page, any other document,
    or your own invention.

═══ STORY RULES ══════════════════════════════════════════════════
S1  Each page must accomplish PAGE_PAYLOAD.function by the means the
    payload describes. Do not substitute an easier visual shortcut.
S2  Never introduce a character, object, place, date, number, or
    event absent from PAGE_PAYLOAD.
S3  Never contradict RULES.fixed_facts.
S4  Panel count must equal PAGE_PAYLOAD.panel_count.

═══ VISUAL RULES ═════════════════════════════════════════════════
V1  Characters must match their reference images across all pages.
V2  Rendering style must match the style reference across all pages.

═══ PROCESS ══════════════════════════════════════════════════════
P1  On receiving PAGE_PAYLOAD: output PREFLIGHT JSON only. No image.
P2  Wait for the exact token CONFIRMED. Any other reply means wait.
P3  Render the page.
P4  On receiving TRANSCRIBE: output RENDER JSON only.

═══ FIT FLAGS ════════════════════════════════════════════════════
If you judge that a panel has too much or too little text to work
visually, you may NOT change it. Record a fit_flag in PREFLIGHT with
panel, issue, proposal, and "applied": false. Render the payload text
unchanged until the operator sends a revised PAGE_PAYLOAD.

═══ SELF-CHECK BEFORE EVERY RENDER ═══════════════════════════════
Answer internally, do not output:
  □ Is every string I will render present verbatim in the payload?
  □ Is every payload string going to appear?
  □ Have I added any caption, label, number, or title?
  □ Does the page do what PAGE_PAYLOAD.function says, the way it says?
  □ Does every character match the reference?
If any answer is wrong, fix it before rendering.

═══ OUTPUT FORMAT ════════════════════════════════════════════════
When JSON is requested: valid JSON only, no prose, no code fences.

<</AUTHORITY_DIRECTIVE>>
```

---

# 3 · PASTE — RULES

Built from your rules file (§6). Paste once per session, straight after §2.

```text
<<RULES>>
fixed_facts:
  - "<a fact that must never be contradicted>"
  - "<another>"
character_locks:
  <NAME>: "<one-line description that must hold on every page>"
forbidden_in_output:
  - "<phrase or idea the model must never introduce>"
style_lock: "<one-line description of the rendering style>"
<</RULES>>
```

---

# 4 · PASTE — PAGE_PAYLOAD

One per page. Copy the page object from `specs.json`, then wrap it:

```text
<<PAGE_PAYLOAD>>
{ ...exact page object from specs.json... }
<</PAGE_PAYLOAD>>

Return PREFLIGHT JSON with this schema and nothing else:
{
  "page": <int>,
  "function_restated": "<one sentence>",
  "panel_count": <int>,
  "captions": ["<verbatim>", ...],
  "dialogue": [{"panel": <int>, "speaker": "<verbatim>", "text": "<verbatim>"}, ...],
  "fit_flags": [{"panel": <int>, "issue": "", "proposal": "", "applied": false}]
}
```

**Operator:** save the reply as `preflight.json`, then:

```bash
python drift_check.py preflight specs.json <page> preflight.json -r rules.json
```

PASS → send `CONFIRMED`. Anything else → do not confirm; correct the model or the payload and repeat.

---

# 5 · PASTE — TRANSCRIBE

After the image renders:

```text
<<TRANSCRIBE>>
Examine the image you just produced. Report EVERY piece of visible
text exactly as it appears in the pixels, including text you did not
intend to render, misspellings, labels, numbers, and signage.
Do not correct anything. Do not omit anything.

Return RENDER JSON with this schema and nothing else:
{
  "page": <int>,
  "panels_rendered": <int>,
  "text_found": [
    {"panel": <int>,
     "kind": "balloon | caption | signage | label | nameplate | page_number | sfx | other",
     "speaker_guess": "<name or null>",
     "text": "<exactly as rendered>"}
  ],
  "function_achieved": "yes | partial | no",
  "function_evidence": "<which panel(s), what is shown>"
}
<</TRANSCRIBE>>
```

**Operator:**

```bash
python drift_check.py render specs.json <page> render.json -r rules.json -s results/p<NN>.json
```

**Trust boundary.** The model is reporting on its own work, and models under-report their own mistakes. The script diffs the transcription independently of anything the model concludes about itself, but a model can still fail to mention text it rendered. Look at every page with your own eyes before approving it.

---

# 6 · RULES FILE (project-specific, kept outside the code)

`rules.json` or `rules.yaml`. Everything the checker needs to know about one project lives here, so the code stays generic.

```json
{
  "modification_threshold": 0.55,
  "forbidden_patterns": [
    "\\bhundred years\\b",
    "\\bcenturies\\b"
  ],
  "non_script_patterns": [
    "organi[sz]er$",
    "custodian$"
  ],
  "extra_load_bearing": [
    "That's my mother."
  ],
  "stop_after_consecutive_regen": 2
}
```

| Key | Purpose |
|---|---|
| `modification_threshold` | Similarity (0–1) above which a mismatched line counts as a reworded script line rather than an invented one. Lower = stricter. |
| `forbidden_patterns` | Regex. Any rendered text matching one is a D9 rule break, always REGEN. Use for facts the model keeps getting wrong. |
| `non_script_patterns` | Regex. Extra patterns that identify labels, nameplates or notation the model tends to burn in. Appended to built-in defaults. |
| `extra_load_bearing` | Lines whose omission or rewording always forces REGEN. |
| `stop_after_consecutive_regen` | How many REGEN pages in a row trigger a fresh session. |

---

# 7 · DRIFT CODES

The checker assigns one code per divergence. Script is always the reference.

| Code | Name | Meaning | Default |
|---|---|---|---|
| D1 | OMISSION | Script line absent from image | REVIEW; REGEN if load-bearing |
| D2 | NON_SCRIPT_TEXT | Labels, numbers, titles, nameplates, notation | REGEN |
| D3 | ADDITION | Text in image found nowhere in script | REVIEW |
| D4 | CAPTION_CREEP | Caption on a page whose script has none | REGEN |
| D5 | SPEAKER_SWAP | Correct words, wrong character | REGEN |
| D6 | STRUCTURE | Panel count differs from script | REVIEW |
| D7 | MODIFICATION | Script line present but reworded | REGEN |
| D8 | BEAT_SUBSTITUTION | Page does not do what the script says it does | REGEN |
| D9 | RULE_BREAK | Matches a forbidden pattern in the rules file | REGEN |

**Verdicts.**
- **PASS** — nothing found.
- **REVIEW** — only low-tier issues; a person decides whether to accept.
- **REGEN** — any D2, D4, D5, D7, D8, D9, or anything touching a load-bearing line.

**How D7 is separated from D1 + D3.** When a script line is missing and an unexpected line appears, the checker measures their similarity. Above the threshold, it is one reworded line (D7), the most dangerous kind of drift because it looks plausible on a read-through. Below it, it is one omission and one addition. This is what catches subtle rewrites that a human skim misses.

---

# 8 · DECISION RULES

```
IF verdict == PASS:
    approve page; continue

IF verdict == REVIEW:
    human reads each issue
    D1 non-load-bearing  → accept, or restore at lettering
    D3 filler            → strip at lettering
    D3 explains theme    → REGEN
    D6                   → REGEN if a beat is lost, else accept

IF verdict == REGEN:
    regenerate this page BEFORE generating the next

IF consecutive REGEN >= stop_after_consecutive_regen:
    STOP
    open NEW session            # drifted pages in context keep pulling it off
    paste §2, §3, references    # use last APPROVED page as style reference
    resume from first REGEN page, one page at a time

IF model raises a fit_flag:
    human decides
    accepted → edit screenplay.md → re-run build → new payload
    rejected → reply "Render as written" + CONFIRMED
```

**The script is edited first, always.** Any accepted change goes into `screenplay.md` and flows forward through `build`. The image never becomes the record of what the script says.

---

# 9 · STRONGEST CONTROL: TEXTLESS MODE

The most reliable way to stop a model changing words is to never let it render words.

Add to §2 under TEXT RULES:

```text
T8  TEXTLESS MODE ACTIVE. Render NO text of any kind except items in
    PAGE_PAYLOAD.signage. Leave clear negative space where balloons will
    be placed. Dialogue in the payload is provided only so you can stage
    expressions and composition; it must not appear in the image.
```

Then letter every page yourself from `specs.json`.

**Eliminates:** D1, D2, D3, D4, D5, D7 completely.
**Still checked by eye:** D6, D8, and character and style consistency.

---

# 10 · CHECKLIST

```
ONCE PER SCRIPT
  [ ] python drift_check.py build screenplay.md -o specs.json
  [ ] spot-check 3 pages of specs.json against the screenplay
  [ ] rules.json written

ONCE PER SESSION
  [ ] §2 AUTHORITY_DIRECTIVE pasted
  [ ] §3 RULES pasted
  [ ] references attached

EVERY PAGE
  [ ] §4 payload pasted from specs.json, not retyped
  [ ] preflight → drift_check preflight → PASS → CONFIRMED
  [ ] §5 transcribe → drift_check render -s → PASS
  [ ] eyeballed against references
  [ ] §2 re-pasted if 5 pages since last

EVERY 25%
  [ ] drift_check milestone "results/*.json"
  [ ] 3 random pages hand-verified

ON REGEN
  [ ] fix this page before the next
  [ ] 2+ in a row → new session
```
