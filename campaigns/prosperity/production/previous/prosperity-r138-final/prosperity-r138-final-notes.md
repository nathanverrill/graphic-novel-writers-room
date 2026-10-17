# notes.md

## Verdict

**Needs a pass.** The packet is close, but one fixed causal contradiction remains: Page 11 visually activates Bi11bot before the watch does so on Page 12. The remaining defects are execution-level lettering collisions, unsupported placement values and density warnings; repair those without changing the approved story or lettering copy.

## Findings by severity

### Blocker

#### 1. Page 11, Panel 4: Bi11bot appears active before the watch activation

- **Location:** `script.md`, Page 11, Panel 4; `draft-final.md`, Chapter 1 Page 7, Panel 4; `layouts.md`, Page 11, Panel 4.
- **Problem:** The description includes a “faint amber pulse beneath the cloth,” contradicting the fixed causal chain in which Adrian’s watch wakes Bi11bot when Alex closes the clasp on Page 12, Panel 3. The Page 11 thumbnail also risks an activation cue before the intended reveal.
- **Smallest repair direction:** **Writer**, remove the pulse and specify complete dormancy: dark optics, dark chest seam and only ordinary reflected workshop light. **Layout Agent**, carry that dormant state into the Page 11 layout description. Do not add an activation cue to the lettering layer.

### Major

#### 2. Page 1, Panel 3: invalid caption position

- **Location:** `layouts.md`, Page 1, Panel 3; showrunner review: `SMALL MAKERS AND THE HOU...` at `middle-right`.
- **Problem:** `middle-right` is not a supported placement value and falls back to `middle`, putting the caption into the central image area rather than its intended artifact zone.
- **Smallest repair direction:** **Layout Agent**, replace `middle-right` with a supported explicit zone matching the upper-right artifact area. Keep the exact approved clipping text.

#### 3. Page 1, Panel 3: future clippings collide

- **Location:** `layouts.md`, Page 1, Panel 3; thumbnail report: `KEEL WATER CO-OP` overlaps `40TH INDEPENDENT`.
- **Problem:** The approved evidence of the future cannot be read cleanly, weakening the prologue’s setup of independent licensing and the Keel co-op.
- **Smallest repair direction:** **Layout Agent**, preserve three separated artifact zones and move the `KEEL WATER CO-OP RENEWS ITS PHANTUM LICENSE` item fully into the lower-left zone, clear of the `40TH INDEPENDENT SHOP LICENSES PHANTUM PURIFIER` item. **Letterer**, verify both captions remain readable.

#### 4. Page 5, Panel 1: invalid caption position

- **Location:** `layouts.md`, Page 5, Panel 1; showrunner review: `What if everyone you've...` at `middle-left`.
- **Problem:** `middle-left` is unsupported and falls back to `middle`, risking collision with the central geography and the other thematic captions.
- **Smallest repair direction:** **Layout Agent**, replace it with a supported explicit zone, preferably the reserved center-left area. Keep it separate from the spine and city labels.

#### 5. Page 5, Panel 1: thematic captions are dense

- **Location:** `layouts.md`, Page 5, Panel 1; review reports the caption set at approximately 27 words.
- **Problem:** The full-page establishing image must communicate three cities, the spine, access gates and unequal infrastructure; dense captioning competes with that visual work.
- **Smallest repair direction:** **Layout Agent**, use the already reserved five caption zones and keep each question visually isolated from infrastructure. Do not alter approved wording unless the Director authorizes a copy change.

#### 6. Page 6, Panel 4: repair-status captions collide

- **Location:** `layouts.md`, Page 6, Panel 4; thumbnail report.
- **Problem:** `UNAUTHORIZED REPAIR — REVIEW REQUIRED`, `ROUTINE MAINTENANCE` and `NEW PART ADDED — DESIGN CREDIT: SITE 6` overlap, obscuring the sequence from flagged repair to supervisor reclassification to lost attribution.
- **Smallest repair direction:** **Layout Agent**, preserve three vertically separated terminal rows: unauthorized alert at top, routine-maintenance reclassification in the middle and Site 6 credit at bottom. **Letterer**, confirm each row is fully readable.

#### 7. Page 6, Panel 4: supervisor balloon collides with the credit record

- **Location:** `layouts.md`, Page 6, Panel 4; thumbnail report.
- **Problem:** The supervisor’s `...Works.` balloon overlaps `NEW PART ADDED — DESIGN CREDIT: SITE 6`, obscuring the supervisor’s decision and its consequence.
- **Smallest repair direction:** **Letterer**, move the balloon into the reserved lower-right area without covering any terminal row or consequential object.

#### 8. Page 6, Panel 2: debt-transfer panel is over-dense

- **Location:** `layouts.md`, Page 6, Panel 2; review reports approximately 48 words.
- **Problem:** The checkpoint must make the essential facts—`418,607 CREDITS`, `28.7 YEARS` and `TRAVEL STATUS: RESTRICTED`—immediately legible, but the display, balloons, caption and SFX compete in one panel.
- **Smallest repair direction:** **Layout Agent**, maintain one dominant vertical display block, separate the guard and Alex balloons from the display and reserve a distinct scanner zone for `BEEP`. Do not change the canon values or remove required debt information.

#### 9. Page 7, Panel 4: Alex and Ada’s balloons overlap

- **Location:** `layouts.md`, Page 7, Panel 4; thumbnail report.
- **Problem:** Ada’s birthday line and Alex’s reply overlap, obscuring the exchange and weakening the brief warm beat before the ownership grievance.
- **Smallest repair direction:** **Letterer**, place Ada’s balloon upper-left and Alex’s upper-right, with separate tails and both faces and mugs unobstructed.

#### 10. Page 7, Panel 6: opposing-dreams dialogue is over-dense

- **Location:** `layouts.md`, Page 7, Panel 6; review reports approximately 28 words.
- **Problem:** Four dialogue beats compete with the visual contrast between Alex looking toward Oasis and Ada looking toward Keel.
- **Smallest repair direction:** **Layout Agent**, preserve the existing four balloon sequence with a clear reading path: Alex, Ada, Alex, Ada. Keep the balloons in the reserved upper-left, lower-right, middle-left and lower-left zones without covering the eyelines. If the density still fails at lettering, **Writer** should redistribute the existing lines across adjacent panels rather than introduce new material.

#### 11. Page 16, Panel 5: closing caption and chapter marker collide

- **Location:** `layouts.md`, Page 16, Panel 5; thumbnail report.
- **Problem:** The retrospective caption overlaps `LETTERING: END OF CHAPTER ONE`, making the final observation and chapter marker compete at the page’s closing beat.
- **Smallest repair direction:** **Layout Agent**, retain separate lower-left and lower-right zones with a substantial gap between them. **Letterer**, place the retrospective caption lower-left and the chapter marker lower-right, away from the amber point and Mera’s reflection.

### Minor

#### 12. Dormant watch state should remain explicit in production copy

- **Location:** `layouts.md`, Page 11, Panel 4; `thumbnails.md`, Page 11, Panel 4.
- **Problem:** The watch’s object label is present, but the dormant state could drift during image generation unless the face-down position and dark display are repeated in the final page prompt.
- **Smallest repair direction:** **Layout Agent**, specify that the watch lies face down beside the covered robot, its display dark, with no amber reflection or pulse until Page 12, Panel 3.

## Plausibility ledger

| Invention or claim | Status | Assessment |
|---|---|---|
| Adrian’s watch wakes Bi11bot | FIXED | Contradicted by the amber pulse specified on Page 11, Panel 4. Remove the pulse and preserve complete dormancy until Page 12, Panel 3. |
| Bi11bot activates when Alex closes the watch clasp | FIXED | Holds in the Page 12 script and layout if Page 11 is corrected. |
| The future wall shows independent shops, competition and a Keel co-op | FIXED | The approved clipping copy is present. Its current problem is lettering placement and collision, not canon. |
| Chapter 1 Legacy Protocol activity sends only an alert and source location | FIXED | Holds across Pages 15–16. No authentication or authority transfer is shown. |
| Mera sees only `SOURCE: KEEL SECTOR` and chooses `TRACK` | FIXED | Holds on Page 16. Preserve the limited source information. |
| Alex’s checkpoint displays 418,607 credits, 28.7 years and restricted travel | Established project material | Correct, but Page 6 density threatens first-pass readability. |
| Alex’s bracket receives Site 6 credit rather than Alex’s name | Established project material | Correct, but Page 6, Panel 4 collisions obscure the causal sequence. |
| Page 5 establishes the three cities and shared infrastructure spine | Established project material | Holds conceptually. Caption placement must not obscure the geography. |
| Page packet covers exactly Pages 1–16 | FIXED | Satisfied in the current packet. |

## Continuity ledger

| Thread | Current state | Where it changes or is at risk |
|---|---|---|
| Bi11bot activation | Watch clasp is the sole activation cause | Page 11, Panel 4 incorrectly suggests an earlier pulse; Page 12, Panel 3 correctly activates him |
| Adrian’s watch | Face down and dark beside dormant Bi11bot, then worn on Alex’s left wrist | Page 11 must remain fully dark; Page 12, Panel 3 activates it |
| Bi11bot design | Industrial blue and chipped mustard body, scarf, warm amber eyes, right-eye ring and white `Bi11` chest mark | Page 12 preserves the design; Page 11 must show the same body dormant |
| Prologue future evidence | Three approved clippings establish independent licensing and the Keel co-op | Page 1, Panel 3 has an invalid placement and caption collision |
| Alex’s debt | 418,607 credits, 28.7-year clearance and restricted travel | Page 6, Panel 2 is lettering-dense but canonically consistent |
| Alex’s bracket | Works but receives Site 6 credit | Page 6, Panels 1 and 4; collisions obscure the payoff |
| Alex and Ada | Close practical friends, not romantic | Page 7 balloon repair must preserve the non-romantic warmth |
| Legacy Protocol | Map identifies three artifacts; Chapter 1 transmits only an alert and source | Pages 15–16 remain within the fixed boundary |
| Mera | Recognizes Adrian’s protocol, sees only Keel sector and chooses TRACK | Page 16 remains consistent |
| Page numbering | Execution packet uses book Pages 1–16 | No current numbering blocker; retain book-level numbering in all handoff references |

## Questions for the Director

1. Confirm that the Page 11 amber pulse is removed entirely, leaving only ordinary reflected workshop light.
2. Confirm that the Page 5 thematic captions retain their approved wording despite the density warning.
3. Confirm whether Page 7, Panel 6 should remain four balloons in one panel after the lettering pass or be redistributed without changing dialogue.

BLOCKERS: 1
FIX: writer, layout
