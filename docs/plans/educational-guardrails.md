# Plan: educational guardrails

Status: **proposed, not built** (2026-10-14). Nothing here is in the code yet.

## The goal

Keep profanity, slurs, hate speech, harassment and sexual content off the page of a book read by
students, without flattening the story. Prosperity's readers are 15 to 18, in an educational
program, reading it as homework (`campaigns/prosperity/rules/reader.md`).

The guard protects **what a reader sees**: the words that get lettered, translations, and the
tools a student or partner might talk to. It does not filter the room's own critics.

## What to check, and what not to

| Check | Where it is made | Why |
|---|---|---|
| The script | `script.md`, by the writers (`app/agent.py` via `llm.chat`) | the source of every line |
| The lettered words | `items[].text` in the `layout` blocks of `layouts.md` | exactly what is printed |
| Translations | `scripts/translate.py apply` | new words that no agent wrote |
| Riff replies and accepted edits | `app/riff.py` (direct OpenRouter call) | writes into the working files |
| Voices chats | `app/voices.py` (`llm.chat`) | a character talking live |

**Do not filter** the First Reader, the cold readers or the Analyst. Their job is to quote a
problem line so the showrunner sees it ("what might offend, and whom" is in the Analyst's role),
and a filter would hide exactly what they are flagging. Intake and the Story desk's structure and
lock checks also produce nothing a reader sees.

## Three layers, cheapest first

### 1. Tell the agents (free)

Add `rules/audience.md` to each campaign: the age band, the program, and the rules, for example:

- No profanity, including mild ("damn", "hell") unless the campaign allows it.
- No slurs or hate speech, from anyone, villains included.
- No sexual content; romance stays at what a school library shelves.
- Villains may be cruel, threatening and wrong in what they say and do, but never with slurs,
  profanity or degrading a group of people.

Every agent already reads the campaign's `rules/`, so this needs no code and stops most problems
at the source. Riff gets it too, through `riff.material()`.

### 2. A word list (free, offline, deterministic)

`app/guard.py` with `scan(text) -> [hits]`:

- A list of profanity and slurs in `agents/_shared/guard-words.txt` (committed), plus a per-campaign
  `rules/guard-allow.txt` for words the showrunner allows, and `rules/guard-block.txt` for more.
- Whole-word, case-insensitive matching, with common obfuscations (`f*ck`, `sh1t`, spaced letters).
- Runs in milliseconds, with no network, so it can run on every save and inside `translate.py`.

Moderation models often miss mild profanity, so the list covers what they let through.

### 3. A moderation model (context: hate, harassment, sexual content)

A word list cannot judge context ("you people" in a threat). For that, one model call per checked
text:

- **OpenAI moderation** (`omni-moderation-latest`): free, returns category scores. Needs an OpenAI
  key, not the OpenRouter one.
- **Llama Guard** on OpenRouter (`meta-llama/llama-guard-4-12b` or current): a fraction of a cent
  per check, uses the key the room already has.

Pick one in `.env` (`GUARD_MODEL`), with `off` as an option for local and mock runs.

## What happens on a hit

The same pattern as the art check (`app/artcheck.py`):

1. **Rewrite.** The flagged lines go back to the agent that wrote them, named, with the rule they
   broke. The agent rewrites only those lines. Up to two tries.
2. **Stop at the gate.** Anything still flagged is listed at the next checkpoint (in the phase's
   gate panel and in `notes.md`), and the phase cannot be approved until each line is fixed or
   explicitly allowed by the showrunner.
3. **Log it.** Every hit and its outcome goes to `guard-log.md` on the desk, like `riff-log.md`.

The showrunner can always override a hit (a false positive, a line the book needs), and the
override is logged with who and why.

## Where it goes in the code

- `app/guard.py`: `scan()` (word list), `moderate()` (model), `check(text, campaign) -> report`.
- `app/agent.py`: after a writer, Layout Agent, Letterer or Press Check writes `script.md` or
  `layouts.md`, run `check()` on the new lines only and feed hits back as a revision note.
- `app/phases.py`: the writing, execution, lettering and press-check gates refuse `approve()` while
  unresolved hits remain, the way the execution gate reads `BLOCKERS:` today.
- `app/riff.py`: check `chat()` replies and `propose()` rewrites before they are shown.
- `app/voices.py`: check each character line before it is shown.
- `scripts/translate.py`: `scan()` every translated line on `apply` and list hits (never block;
  the translator fixes the CSV).
- Images: add an "inappropriate content" kind to the art check's list. The image provider's own
  moderation already applies.

## Build order

1. `rules/audience.md` for Prosperity. No code; check the next script against it.
2. `app/guard.py` with the word list, wired into `translate.py` and the press-check gate.
3. The rewrite loop in `app/agent.py` for the writers and the Layout Agent.
4. The moderation model, behind `GUARD_MODEL`.
5. Riff and Voices.
6. The gate panel UI and `guard-log.md`.

Steps 1 and 2 are small and cover the last point before print. Each later step is independent.

## Cost

- Word list: $0.
- OpenAI moderation: $0. Llama Guard: well under $0.01 per check, so cents per book.
- Rewrites: only when a line is flagged, at the writer's normal per-call cost.

## Decisions for the showrunner

- **Age band and language:** does mild language ("damn", "hell") count for this program?
- **Villains:** confirm villains may be cruel on the page as long as there are no slurs, profanity
  or degrading a group. A blanket filter flattens antagonists.
- **Who can override a hit**, and whether overrides need a reason.
- **Moderation provider:** OpenAI's free endpoint (a second key) or Llama Guard on the existing
  OpenRouter key.
