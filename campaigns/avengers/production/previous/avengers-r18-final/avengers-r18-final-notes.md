# notes.md

## Verdict

**Needs a pass.** The execution package is not ready because ten layout blocks fail JSON parsing, preventing the renderer from verifying the affected pages. The layouts file also does not currently provide a complete, renderable set of Pages 1–24, so the consent, evacuation, disclosure, and resolution pages cannot pass the readiness check. The story and approved continuity remain intact; repair the layout packet without changing the locked script or page plan.

## Findings by severity

### Blocker

1. **Location:** `layouts.md`, layout blocks 3, 11, 14, and 18–24; corresponding entries in `thumbnails.md`.  
   **Problem:** The renderer reports `Extra data` JSON parse errors in ten layout blocks:

   - Layout block 3: line 1, column 1332
   - Layout block 11: line 1, column 1312
   - Layout block 14: line 1, column 987
   - Layout block 18: line 1, column 1543
   - Layout block 19: line 1, column 1451
   - Layout block 20: line 1, column 1252
   - Layout block 21: line 1, column 1339
   - Layout block 22: line 1, column 1538
   - Layout block 23: line 1, column 1204
   - Layout block 24: line 1, column 890

   These blocks are not valid JSON objects and cannot be consumed by the layout renderer.  
   **Smallest repair direction:** **Layout Agent:** remove the extra trailing data or malformed characters from each affected block while preserving the existing page number, panel descriptions, lettering items, clear-space instructions, and one-panel Page 24 splash. Regenerate the thumbnails after parsing succeeds. **Letterer:** rerun the lettering preflight against the repaired blocks.  
   **Role:** Layout Agent, Letterer

2. **Location:** `layouts.md`, overall page set.  
   **Problem:** The file currently contains layout blocks only for Pages 1, 2, 4–10, 12, 13, and 15–17. The brief requires exactly Pages 1–24. Pages 3, 11, 14, and 18–24 are absent from the verified layout set; the affected later beats include the TJ consent, Nexus evacuation, public disclosure, Colorado inspection, interim contract, Croft’s choice, and final splash.  
   **Smallest repair direction:** **Layout Agent:** restore valid layout blocks for Pages 3, 11, 14, and 18–24 from the existing `script.md` and layout specifications. Do not add pages, remove pages, or revise the approved story. Regenerate `thumbnails.md` and confirm that exactly 24 pages render.  
   **Role:** Layout Agent

### Major

1. **Location:** Page 18, Panel 4.  
   **Problem:** The panel contains two separate physical TJs and two separate authorizations. If the repaired layout compresses the displays or lettering zones, the reader may misread the panel as one machine granting a combined disclosure.  
   **Smallest repair direction:** **Layout Agent:** preserve a clear physical gap and distinct display areas for Roman’s bonded TJ and Sitara’s TJ. **Letterer:** attach `CONSENT: YES` only to Roman’s TJ and `AUTHORIZED` only to Sitara’s TJ.  
   **Role:** Layout Agent, Letterer

2. **Location:** Pages 19–20.  
   **Problem:** Falcon’s interruption and the later public disclosure depend on attribution and limited scope. A shared exterior view, an unexplained operator, or undifferentiated transfer cards would contradict the approved geography and consent logic.  
   **Smallest repair direction:** **Layout Agent:** keep Page 19 Panels 3–4 inside a clearly labeled authenticated remote-record interface, with no Falcon exterior. Keep Page 20’s Roman TJ, Sitara TJ, and human-record packages visibly separate. **Letterer:** preserve the exact source labels and do not imply full mission-partition synchronization.  
   **Role:** Layout Agent, Letterer

3. **Location:** Page 24, full-page splash.  
   **Problem:** The final splash carries several continuity-critical elements at once: two separate TJs, Sitara’s shared provenance record, Roman’s question, Roman’s TJ response, the monitoring station, and the unresolved public meeting. Poor anchoring could merge the TJs or assign one unit the other’s authorization.  
   **Smallest repair direction:** **Layout Agent:** maintain distinct physical positions for both TJs, the provenance tablet, and the monitoring station, with the public meeting in the background. **Letterer:** anchor `LOCAL MEMORY RETAINED / SHARED RECORD AUTHORIZED` only to Roman’s bonded TJ and `SHARED / NO EXCLUSIVE CLAIM` only to Sitara’s provenance record.  
   **Role:** Layout Agent, Letterer

4. **Location:** Pages 15 and 21.  
   **Problem:** The values `CLARITY INDEX: 41 → 68` and `DOWNSTREAM TAXA: 3 → 11` are used throughout the script and layouts, but `story.md` still identifies them as proposals pending Director approval. The execution packet must not treat unresolved metrics as settled canon.  
   **Smallest repair direction:** **Director:** approve these values or replace them. **Writer, Layout Agent, Letterer:** update every occurrence consistently after that decision.  
   **Role:** Director

### Minor

1. **Location:** Page 18, Panel 1.  
   **Problem:** `CORPORATE ACCESS EVENT / LOCAL ARCHIVE: DELETION / SHUTDOWN REVIEW` is long and competes with Roman’s embodied neural response and the TJ’s local display.  
   **Smallest repair direction:** **Layout Agent:** reserve an isolated caption zone. **Letterer:** keep the corporate notice visually distinct from the TJ’s spoken refusal and Roman’s neural response.  
   **Role:** Layout Agent, Letterer

2. **Location:** Page 20, Panel 4.  
   **Problem:** The inspection request, Antarctic route log, and public custody receipt could read as unrelated paperwork rather than a causal sequence.  
   **Smallest repair direction:** **Layout Agent:** arrange the three windows in clear left-to-right order with separate headers and directional progression. **Letterer:** retain all three exact labels and the closing caption.  
   **Role:** Layout Agent, Letterer

3. **Location:** Page 22, Panel 1.  
   **Problem:** The two contract headings are assigned the same lettering position in the layout specification, creating a likely collision:

   - `UNINCORPORATED INTERIM PARTNERSHIP`
   - `PUBLIC CONTRACTS / INSPECTION REQUIRED`

   **Smallest repair direction:** **Layout Agent:** reserve two separate caption zones within the projection. **Letterer:** stack the headings without overlap.  
   **Role:** Layout Agent, Letterer

4. **Location:** Page 2, Panel 2, as shown in the available thumbnail render.  
   **Problem:** The TJ balloon and `TIK. TIK. TIK.` compete for the same upper/lower-right area, reducing legibility.  
   **Smallest repair direction:** **Letterer:** move the TJ balloon away from the SFX, or shift the SFX lower-right while preserving the action.  
   **Role:** Letterer

5. **Location:** Page 11, Panel 4.  
   **Problem:** The two krill data lines need to remain readable as a single sensor result rather than overlapping or truncating.  
   **Smallest repair direction:** **Letterer:** stack `KRILL REPRODUCTION: FAILED` and `CAUSE CORRELATION: SEA-ICE LOSS` in one clean display area.  
   **Role:** Letterer

## Plausibility ledger

- **[FIXED] Page count:** The book must contain exactly 24 pages. The current layout packet does not yet provide a verified render of all 24.
- **[FIXED] Page sides:** Odd pages are right-hand pages and even pages are left-hand pages. Repaired blocks must preserve the existing assignments.
- **[FIXED] TJ distinction:** Roman’s bonded TJ and Sitara’s TJ are separate physical units. Pages 18, 20, and 24 must preserve separate bodies, displays, and authorizations.
- **[FIXED] Consent sequence:** Roman’s TJ first refuses deletion through the private neural channel, then confirms limited consent through its screen and speaker with Sitara and Nayah witnessing.
- **[FIXED] Disclosure scope:** The release is limited to selected Falcon environmental records, Merritt provenance records, agreed corroborating route and sensor data, Sitara’s separately authorized route/sensor/Falcon-search records, and identified human records. No full mission partition or private neural telemetry is released.
- **[FIXED] Falcon/Nexus geography:** Falcon and Nexus are separate sites. Page 19 must show Falcon only through an authenticated remote feed or record.
- **[FIXED] Falcon interruption:** Authenticated transmission and local inspection control place Falcon on safe hold and make it inspectable. The page must not imply magical remote control, immediate arrest, or a view across the ice.
- **[FIXED] Colorado outcome:** The pilot continues under inspection with measurable benefits and visible costs: recovered feedstock, rejected material, residual solids, emissions monitoring, water use, grid demand, and finite throughput.
- **[UNLABELLED / PROPOSAL in `story.md`] Colorado metric values:** `41 → 68` clarity units and `3 → 11` invertebrate taxa remain pending Director approval.
- **[FIXED] Roman’s consequence:** Public exposure and loss of employment/access are the on-page consequences. No arrest, charges, sentencing, or formal prosecution should appear.
- **[FIXED] Ending state:** Evidence survives, Colorado continues provisionally, Croft relinquishes proprietary control, and ownership, financing, and TJ personhood remain unresolved.
- **[UNLABELLED] Production status:** Ten layout blocks remain invalid until repaired and rerendered.
- **[FIXED] Transport geography:** Falcon and Nexus are connected by a weather-dependent Antarctic route; Colorado is the departure/logistics context, not the physical start of an Antarctic tracked-vehicle journey.

## Continuity ledger

| Element | Current state | Required carry-forward |
|---|---|---|
| Page set | Ten layout blocks fail to parse; the current file does not verify all 24 pages | Render exactly Pages 1–24 after repair |
| Page 3 | Missing from the verified packet | Preserve Falcon challenge-response entry, limited maintenance access, and Nayah’s five-minute safety limit |
| Page 11 | Missing from the verified packet | Preserve the dead krill tank, measurable sea-ice/krill evidence, and costly TJ fabrication |
| Page 14 | Missing from the verified packet | Preserve selected feedstock, rejected material, residual solids, emissions, water, grid demand, and limited throughput |
| Page 18 | Missing from the verified packet | Preserve deletion threat, Roman’s ethical question, witnessed two-stage consent, and explicit disclosure categories |
| Page 19 | Missing from the verified packet | Preserve Nexus evacuation, Orien’s extraction, separate Falcon remote feed, safe hold, and inspection flag |
| Page 20 | Missing from the verified packet | Preserve attributable source packages, separate TJ authorizations, human signatures, and Roman’s employment/access loss |
| Page 21 | Missing from the verified packet | Preserve inspection before continuation, readable metrics, finite wetland capacity, and bounded operation |
| Page 22 | Missing from the verified packet | Preserve the interim public contract, public reading of its terms, disagreement over ownership/financing, and unresolved governance |
| Page 23 | Missing from the verified packet | Preserve Croft’s active refusal to block the pilot without repentance or exoneration |
| Page 24 | Missing from the verified packet | Preserve separate TJs, shared provenance without exclusive claim, local memory retained, unresolved meeting behind them, and limited pilot status |
| Sitara | 26, uninjured, red Antarctic field gear; concealed Merritt copies | Carry her into shared provenance and the no-exclusive-author ending |
| Roman | 22, chemical engineer, medically complicit, bonded to one TJ | Carry him through public exposure and employment/access loss only |
| Nayah | Field commander with a safety veto | Preserve her evacuation order as the controlling Page 19 action |
| Roman’s TJ | Only neural-bonded unit; local archive and consent authority | Keep its records and consent separate from Sitara’s TJ |
| Sitara’s TJ | Separate search/heat-mapping unit with no neural bond | Keep its thermal identifier and independent authorization visible |
| Falcon | Separate illegal exploratory drilling site | Show only through authenticated remote data on Page 19 |
| Nexus | Separate coastal cave laboratory | Preserve fracture, flooding, archive movement, and evacuation |
| Colorado pilot | Real but bounded benefit under inspection | Do not depict universal restoration, unlimited throughput, or fossil-fuel replacement |
| Final state | Evidence survives; pilot continues provisionally; governance contested | Do not imply climate reversal, permanent ownership, or resolved TJ personhood |

## Questions for the Director

1. Should `CLARITY INDEX: 41 → 68` and `DOWNSTREAM TAXA: 3 → 11` be approved as canon, or replaced consistently across Pages 15 and 21?
2. Does the Director approve repairing the ten malformed layout blocks without changing the locked script or page plan?
3. Does the Director approve restoring the missing layout blocks for Pages 3, 11, 14, and 18–24 from the existing script and specifications?
4. Does the Director approve Page 20’s separate-package arrangement, with Roman’s TJ, Sitara’s TJ, and human-held records visibly distinct?
5. Should Page 19’s `DRILL CONTROL: SAFE HOLD` remain an automated/local control-record state with no named operator added?
6. Does the Director approve the Page 24 splash retaining all lower lettering groups, provided each remains anchored to a distinct object?

BLOCKERS: 2
FIX: layout, letterer