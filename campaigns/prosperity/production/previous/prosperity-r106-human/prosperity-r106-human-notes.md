# notes.md

## Verdict

**Needs a pass.** The execution package is not complete because `layouts.md` does not contain page blocks for Pages 11–43, despite the brief requiring all 64 pages. Three continuity blockers remain: the Page 45–47 access-tool handoff contradicts itself, Ada’s route to Leona is not causally established, and the exact debt reduction on Page 63 is not supported by visible work or payments. The page 63 lettering overload is a separate production issue that must be corrected before lettering.

## Findings by severity

### Blocker

#### 1. Pages 11–43 are missing from the layout artifact

- **Location:** `layouts.md`, between the Page 10 and Page 44 entries.
- **Observation:** The file states that Pages 11–43 “retain the approved four-panel layouts,” but does not provide those layout blocks or their `items` arrays. The brief requires page-specific production packets for Pages 1–64.
- **Problem:** The image model has no complete page-level staging or lettering-clearance instructions for Pages 11–43. The book cannot pass execution readiness or be assembled into complete page prompts from this artifact.
- **Smallest repair direction:** **Layout Agent:** restore the approved layout blocks for every page from Page 11 through Page 43, including each page’s panel descriptions, clear lettering areas and complete `items` arrays. Do not alter the approved story or pagination.
- **Role:** layout.

#### 2. Page 47 contradicts the Page 45 access-tool handoff

- **Location:** `script.md`, Page 45 Panel 4; `script.md`, Page 47 Panel 4; `layouts.md`, Pages 45 and 47.
- **Observation:** Page 45 shows Ada catching the access tool thrown across the barrier by Alex. Page 47’s script/layout instead describes Ada using a tool “Lina slipped into her hand.”
- **Problem:** The reader cannot tell who possessed the tool or how Ada obtained it. This tool is the mechanism of Ada’s escape route, so the action chain is broken.
- **Smallest repair direction:** **Writer:** retain the visible Page 45 throw and remove the Lina handoff from Page 47. **Layout Agent:** make Pages 47–48 consistently show Ada using the tool she caught from Alex.
- **Role:** writer, layout.

#### 3. Ada’s route to Leona is not established

- **Location:** `script.md`, Pages 47–49; `layouts.md`, Pages 47–48.
- **Observation:** Page 48 currently implies that Lina’s route or route mark leads Ada to the pale civic apartment where Leona lives. No prior page establishes that Lina knows Leona’s location or gave Ada this route.
- **Problem:** Ada’s independent decision to reach Leona depends on information she has not plausibly received. The Lina Vey/Leona Veyra similarity also creates an unintended relationship question.
- **Smallest repair direction:** **Writer:** make Ada use her own previously established route knowledge from Pages 14/21, with no Lina–Leona connection. **Layout Agent:** remove Lina-associated route language and show Ada applying her own marked route to the service passage and apartment.
- **Role:** writer, layout.

#### 4. The Page 63 debt reduction is numerically unearned

- **Location:** `script.md`, Page 63 Panels 3–4; `layouts.md`, Page 63.
- **Observation:** The book moves from Alex’s 418,607-credit debt on Page 12 to 402,110 credits on Page 63. The ending shows a personal medicine repayment and a months-later repair shop, but no sufficiently legible accumulation of payments supporting the exact 16,497-credit reduction.
- **Problem:** Canon requires the reduction to be supported by visible work and payments. The current ending makes the number appear arbitrary and risks implying that the 45-credit personal loan accounts for the much larger reduction.
- **Smallest repair direction:** **Writer:** show a compact, legible accumulated work/payment record or remove any unsupported intermediate exact figure while retaining the canon-approved 402,110-credit balance. Keep Tomas’s paid medicine loan distinct from Alex’s still-active household debt. **Letterer:** do not letter an unsupported 16,497-credit total.
- **Role:** writer, letterer.

### Minor

#### 5. Page 63 Panel 3 is overcrowded

- **Location:** `script.md`, Page 63 Panel 3; `layouts.md`, Page 63 Panel 3; `thumbnails.md`, Page 63.
- **Observation:** The panel combines the medicine-payment receipt, an accumulated payment ledger, two dialogue balloons and multiple labels. The panel’s dialogue alone is approximately 26 words, above the project’s roughly 25-word guidance.
- **Problem:** The personal repayment, the accumulated work evidence and the dialogue compete for the panel’s limited visual and lettering space.
- **Smallest repair direction:** **Layout Agent / Letterer:** reserve clear space for the receipt and two short balloons, and move or simplify the accumulated payment record after the Writer resolves the debt evidence. Keep the medicine repayment visually distinct from the larger debt balance.
- **Role:** layout, letterer.

## Plausibility ledger

- **64-page format — BLOCKED IN ARTIFACT:** The script covers Pages 1–64, but `layouts.md` does not supply layout blocks for Pages 11–43.
- **Four-panel maximum — HOLDS WHERE LAYOUTS ARE PRESENT:** Supplied layout blocks use four panels; Pages 11–43 cannot be verified until their blocks are restored.
- **Access-tool continuity — CONFLICT:** Page 45 shows Alex throwing the tool to Ada; Page 47 attributes it to Lina. The Page 45 handoff must control.
- **Ada’s Oasis route — UNDER-SUPPORTED:** No approved prior fact establishes Lina as the source of Leona’s location. Use Ada’s own planted route instead.
- **Debt reduction — UNDER-SUPPORTED:** The final 402,110-credit balance is canon, but the visible payment trail does not yet support the exact reduction.
- **Page 63 lettering load — PRODUCTION RISK:** Panel 3 combines too many lettering elements for its available area.
- **No train crossing — HOLDS:** The Keel-to-Halyard crossing uses the broad conduit.
- **Alex’s mother — HOLDS:** No new information about her is introduced.
- **House names — HOLDS IN CURRENT SCRIPT:** The script uses only Caldera, Vector and Orbital; stale alternatives remain in `world.md` but are outside this execution repair pass.

## Continuity ledger

| Thread | Earlier state | Later state | Assessment |
|---|---|---|---|
| Layout coverage | Pages 1–10 and 44–64 have visible layout blocks | Pages 11–43 are only described as retained | Missing production artifact; restore those pages |
| Access tool | Alex throws it to Ada on Page 45 | Ada uses it on Pages 47–48, but Page 47 attributes it to Lina | Contradiction; unify to Alex-to-Ada handoff |
| Ada’s route | Ada has practical route knowledge planted in Keel | Page 48 attributes the Oasis route to Lina | Unsupported attribution; use Ada’s own route |
| Alex’s debt | 418,607 credits at transfer, Page 12 | 402,110 credits, Page 63 | Canonical endpoints hold; payment trail remains insufficient |
| Tomas’s medicine loan | 45 credits, ten-credit weekly terms, Page 15 | Paid receipt, Page 63 | Personal repayment holds; keep separate from household debt reduction |
| Page 63 Panel 3 | Receipt, ledger and dialogue share one panel | Overloaded lettering area | Layout/lettering correction required |

## Questions for the Director

1. Confirm that the approved repair is to restore the missing Pages 11–43 layout blocks without changing their approved content.
2. Confirm that Ada’s Page 47–48 route should use her own earlier route knowledge and remove Lina from that causal chain.
3. Confirm whether the Writer should establish the 16,497-credit reduction through a compact cumulative payment record or omit that unsupported intermediate number while retaining the fixed 402,110-credit balance.

BLOCKERS: 4
FIX: writer, layout, letterer