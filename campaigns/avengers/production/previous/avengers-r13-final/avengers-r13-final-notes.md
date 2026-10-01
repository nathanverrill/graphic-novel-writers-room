# notes.md

## Verdict

**Needs a pass.** The execution round is not ready because six layout blocks fail to parse, leaving Pages 3 and 18–21 and 24 out of the recognized 24-page artifact. The missing pages include the consent, disclosure, evacuation, inspection, and final-state beats, so continuity and production cannot be verified until the layout data is repaired and rerendered. The remaining seven issues are local lettering overflows identified by the showrunner.

## Findings by severity

### Blocker

1. **Location: `layouts.md`, layout blocks 3, 18, 19, 20, 21, and 24; recognized page set is `[1, 2, 4–17, 22, 23]`.**  
   Six layout blocks return `Extra data` parse errors. Consequently, Page 3 and Pages 18–21 and 24 are absent from the execution artifact, despite the brief requiring exactly Pages 1–24. This prevents verification of TJ consent, limited disclosure, Nexus evacuation, Falcon’s inspection hold, Colorado’s closing state, and the final shared-stewardship image.  
   **Smallest repair direction:** Layout Agent: repair each affected block into one valid JSON layout object with exactly one layout structure and one `items` array, preserving the approved panel descriptions, lettering, page numbers, sides, and page count. Rerun the readiness check and confirm that Pages 1–24 are recognized. Letterer: rerender and verify the restored pages after parsing succeeds.  
   **Fix:** layout, letterer

### Major

1. **Location: Page 2, Panel 1 — `THRUMM—THRUMM—THRUMM` runs beyond the page/live area.**  
   The SFX may be trimmed and is not safely producible in the full-page splash.  
   **Smallest repair direction:** Layout Agent: move or scale the SFX into the live area, or explicitly mark it as an intentional breakout with sufficient trim safety. Letterer: verify that it remains legible and does not obscure the hatch reveal or dialogue.  
   **Fix:** layout, letterer

2. **Location: Page 4, Panel 2 — Nayah’s balloon, `That is not an ice-core manifest.`, breaks past the live area.**  
   The line may be trimmed, and the balloon currently competes with Sitara’s adjacent response.  
   **Smallest repair direction:** Layout Agent: reserve a wider interior balloon zone or reposition the balloon inward while keeping the two speakers’ reading order clear. Letterer: preserve the complete sentence.  
   **Fix:** layout, letterer

3. **Location: Page 5, Panel 1 — `THRUM—THRUM—THRUM` runs beyond the page/live area.**  
   The SFX may be trimmed and risks colliding with Nayah’s four-minute warning.  
   **Smallest repair direction:** Layout Agent: reduce and reposition the SFX inside the panel, or mark it as a deliberate breakout with safe trim clearance. Letterer: confirm separation from the balloon.  
   **Fix:** layout, letterer

4. **Location: Page 10, Panel 1 — `GROOOAN` runs beyond the splash/live area.**  
   The structural SFX may be trimmed and could interfere with Roman’s command if moved without planning.  
   **Smallest repair direction:** Layout Agent: place or scale the SFX within the live area while preserving the fracture’s impact and Roman/Nayah dialogue zones. Letterer: verify safe placement.  
   **Fix:** layout, letterer

### Minor

1. **Location: Page 2, Panel 1 — duplicate readiness flags for the same `THRUMM—THRUMM—THRUMM` overflow.**  
   The report lists both “runs off the page” and “breaks out past the live area.” These describe one production defect rather than two separate story problems.  
   **Smallest repair direction:** Treat both flags as one SFX-placement correction and clear both readiness errors when the render is rerun.  
   **Fix:** layout, letterer

2. **Location: Page 5, Panel 1 — duplicate readiness flags for the same `THRUM—THRUM—THRUM` overflow.**  
   The report lists both “runs off the page” and “breaks out past the live area.” These should clear together after one placement correction.  
   **Smallest repair direction:** Resolve the single SFX placement issue and rerun the readiness check.  
   **Fix:** layout, letterer

3. **Location: Page 10, Panel 1 — duplicate readiness flags for the same `GROOOAN` overflow.**  
   The report lists both “runs off the page” and “breaks out past the live area.” These should be treated as one placement correction.  
   **Smallest repair direction:** Resolve the single SFX placement issue and rerun the readiness check.  
   **Fix:** layout, letterer

## Plausibility ledger

- **[FIXED] Page count:** The brief requires exactly 24 pages. The current layout artifact recognizes only Pages 1, 2, 4–17, and 22–23. Missing Pages 3, 18–21, and 24 are a production defect.
- **[FIXED] Page sides:** Existing assignments follow the required pattern: odd pages right-hand, even pages left-hand. Preserve these assignments while repairing parse errors.
- **[FIXED] TJ consent and disclosure:** The approved sequence requires Roman’s bonded TJ to refuse erasure privately, then confirm limited consent through its screen and speaker, with Sitara and Nayah witnessing. The affected Page 18 block must retain that two-stage sequence.
- **[FIXED] Disclosure scope:** The public package must remain limited to selected Falcon environmental records, Merritt provenance records, agreed corroborating route/sensor data, Sitara’s separately authorized route/sensor/Falcon-search records, and identified human records. No full mission partition or private neural telemetry may be added while repairing Page 18 or Page 20.
- **[FIXED] Falcon/Nexus geography:** Falcon must appear only through an authenticated remote feed or record. Page 19 must not depict Falcon as physically visible from Nexus.
- **[FIXED] Falcon interruption:** The climax action is authenticated transmission plus local drilling hold/inspection flag. It is not remote bodily control, magical facility shutdown, or a direct view across the ice.
- **[FIXED] Colorado limits and benefits:** Pages 14–15 and 21 use selected feedstock, rejected material, residual solids, water use, grid demand, emissions monitoring, finite throughput, improved clarity, and returning invertebrate taxa. Preserve these elements in the repaired resolution pages.
- **[PROPOSAL / UNLABELLED AS CANON] Colorado metric values:** `CLARITY INDEX: 41 → 68` and `DOWNSTREAM TAXA: 3 → 11` remain proposed fictional measurements in `story.md`, although they are consistently used in the script and layouts. Director approval is still required for final canon lock.
- **[FIXED] Roman’s consequence:** Public exposure and loss of employment/access are the on-page consequences. Do not introduce arrest, charges, sentencing, or a formal legal proceeding in the repaired pages.
- **[UNLABELLED] Layout repair status:** The six malformed blocks remain unverified until they parse and render successfully.

## Continuity ledger

| Element | Current state | Required carry-forward |
|---|---|---|
| Page count | Exactly 24 required; six blocks fail to parse | Restore valid layout blocks for Pages 3, 18–21, and 24 |
| Page 3 | Missing from recognized layout set | Preserve Falcon challenge-response entry and Nayah’s five-minute safety limit |
| Page 18 | Missing from recognized layout set | Preserve corporate deletion threat, Roman’s question, witnessed TJ consent, and explicit limited categories |
| Page 19 | Missing from recognized layout set | Preserve Nexus evacuation, Orien’s extraction, separate Falcon remote feed, and local inspection hold |
| Page 20 | Missing from recognized layout set | Preserve attributable source packages, no-exclusive disclosure, and Roman’s employment/access loss |
| Page 21 | Missing from recognized layout set | Preserve inspection before continuation and visible Colorado benefits/limits |
| Page 24 | Missing from recognized layout set | Preserve separate TJs, shared provenance without exclusive claim, local memory retained, and unresolved governance |
| Sitara | 26, uninjured, red Antarctic gear; concealed Merritt copies | Carry through shared provenance and no-exclusive-author ending |
| Roman | 22, chemical engineer, medically complicit, bonded to one TJ | Carry through public exposure and employment/access loss only |
| Nayah | Field commander with safety veto | Retain authority to order the Nexus evacuation |
| Roman’s TJ | Only neural-bonded unit | Keep its disclosure package distinct from Sitara’s TJ |
| Sitara’s TJ | Separate search/heat-mapping unit with no neural bond | Keep its thermal identifier and separately authorized records |
| Falcon | Separate illegal exploratory drilling site | Show authenticated remote status and local inspection control |
| Nexus | Separate coastal cave laboratory | Preserve fracture, flooding, archive movement, and evacuation |
| Final state | Evidence survives; Colorado continues provisionally; governance remains contested | Do not imply climate reversal, legal closure, permanent ownership, or resolved TJ personhood |

## Questions for the Director

1. Does the Director approve repairing the six malformed layout blocks without changing their approved visual content or page assignments?
2. Does the Director approve the proposed fictional Colorado metrics `41 → 68` and `3 → 11` as final canon?
3. Should the three SFX overflows be moved inside the live area, or should any be intentional breakouts with explicit trim safety?
4. Does the Director approve preserving the exact Page 18 disclosure categories and separate TJ authorizations during the repair?
5. Does the Director approve the Page 19 local inspection acknowledgment as an automated/local console confirmation rather than a newly introduced named operator?

BLOCKERS: 1
FIX: layout, letterer