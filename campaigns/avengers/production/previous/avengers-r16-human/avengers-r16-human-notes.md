# notes.md

## Verdict

**Needs a pass.** The execution round is not ready because six specified layout blocks fail JSON parsing, leaving the required 24-page layout set unavailable to the renderer. The story and approved continuity otherwise hold, but the malformed blocks and their unverified lettering zones must be repaired before page packets can be produced.

## Findings by severity

### Blocker

1. **Location:** `layouts.md`, the six repaired layout blocks for Pages 3, 18, 19, 20, 21, and 24; corresponding entries in `thumbnails.md`.  
   **Problem:** Each block returns an `Extra data` JSON parse error. The renderer therefore sees `pages: []` rather than the required Pages 1–24, and no page packet can be generated for these six pages.  
   **Smallest repair direction:** **Layout Agent:** make each affected block one valid JSON object containing exactly its page number, side, tiers, and items. Preserve the existing panel descriptions, page assignments, lettering text, and clear-space instructions. Regenerate `thumbnails.md` and confirm that exactly Pages 1–24 are recognized. **Letterer:** recheck the lettering zones after successful parsing.  
   **Fix:** layout, letterer

### Major

1. **Location:** Page 18, Panel 4, `layouts.md`.  
   **Problem:** Two separate TJs authorize two separate data packages. If the repaired panel compresses the displays or captions, the reader may read this as one machine granting one combined consent.  
   **Smallest repair direction:** **Layout Agent:** keep Roman’s bonded TJ and Sitara’s TJ physically distinct, with separate display areas. **Letterer:** attach `CONSENT: YES` only to Roman’s bonded TJ and `AUTHORIZED` only to Sitara’s TJ.  
   **Fix:** layout, letterer

2. **Location:** Page 19, Panels 3–4, `layouts.md`.  
   **Problem:** Falcon must be represented only through an authenticated remote operational record. A live exterior view, a shared Antarctic landscape, or an unexplained operator would contradict the fixed Falcon/Nexus geography and the approved mechanism of interruption.  
   **Smallest repair direction:** **Layout Agent:** place both panels unmistakably within Roman’s field-tablet or authenticated remote-record interface. Do not show Falcon as visible from Nexus and do not add an operator. **Letterer:** retain `FALCON — AUTHENTICATED REMOTE RECORD FEED`, `DRILL CONTROL: SAFE HOLD`, `LOCAL RECORD: FLAGGED`, and `INSPECTION REQUIRED`.  
   **Fix:** layout, letterer

3. **Location:** Page 20, Panel 1, `layouts.md`.  
   **Problem:** The disclosure includes Roman’s TJ records, Sitara’s TJ records, and human-held records. Without clear attribution, the transfer may read as a single TJ authorizing everything or as full mission-partition synchronization.  
   **Smallest repair direction:** **Layout Agent:** preserve separate source-package cards with visible gaps. **Letterer:** label Roman’s TJ package, Sitara’s TJ package, and human records as separate sources; do not use language implying a full archive transfer.  
   **Fix:** layout, letterer

4. **Location:** Page 24, Panel 1, `layouts.md`.  
   **Problem:** The final splash must simultaneously show two separate TJs, the shared provenance record, Roman’s question, the bonded TJ’s response, and the limited pilot status. The current density risks merging devices or attaching text to the wrong object.  
   **Smallest repair direction:** **Layout Agent:** maintain distinct positions for Sitara’s TJ, Roman’s bonded TJ, the provenance tablet, and the monitoring station. **Letterer:** anchor each status line to its correct object; keep `LOCAL MEMORY RETAINED / SHARED RECORD AUTHORIZED` exclusive to Roman’s bonded TJ.  
   **Fix:** layout, letterer

5. **Location:** Page 15, script; Page 21, Panel 3, `layouts.md`.  
   **Problem:** `CLARITY INDEX: 41 → 68` and `DOWNSTREAM TAXA: 3 → 11` are treated as final lettering, but `story.md` identifies these fictional values as proposals pending Director approval. This is a canon-status problem rather than a layout preference.  
   **Smallest repair direction:** **Director:** approve these exact fictional metrics or replace them. Once decided, update every occurrence consistently in the script, layouts, packets, and lettering.  
   **Fix:** director

### Minor

1. **Location:** Page 18, Panel 1, `layouts.md`.  
   **Problem:** `CORPORATE ACCESS EVENT / LOCAL ARCHIVE: DELETION / SHUTDOWN REVIEW` is long for a panel that must also communicate Roman’s embodied neural response and the bonded TJ’s local state.  
   **Smallest repair direction:** **Layout Agent:** reserve a dedicated caption zone away from Roman and the TJ. **Letterer:** keep the corporate access notice visually separate from the neural communication.  
   **Fix:** layout, letterer

2. **Location:** Page 20, Panel 4, `layouts.md`.  
   **Problem:** The three windows—inspection request, Antarctic route log, and public custody receipt—could read as unrelated paperwork rather than a causal sequence after disclosure.  
   **Smallest repair direction:** **Layout Agent:** give each window a distinct header and clear left-to-right progression. **Letterer:** preserve the three labels and closing caption without allowing the caption to substitute for the visual sequence.  
   **Fix:** layout, letterer

3. **Location:** `thumbnails.md`, Page 2, Panel 2.  
   **Problem:** The TJ balloon overlaps `TIK. TIK. TIK.`, making both the machine report and the SFX less legible.  
   **Smallest repair direction:** **Letterer:** move the TJ balloon to the upper-left or shift the SFX to the lower-right, preserving the action and panel composition.  
   **Fix:** letterer

4. **Location:** `thumbnails.md`, Page 11, Panel 4.  
   **Problem:** The captions `KRILL REPRODUCTION: FAILED` and `CAUSE CORRELATION: SEA-ICE LOSS` overlap and are truncated in the render. The ecological evidence cannot be read cleanly.  
   **Smallest repair direction:** **Letterer:** stack the two lines in one dedicated display area or use two non-overlapping data labels.  
   **Fix:** letterer

5. **Location:** `thumbnails.md`, Page 14, Panel 4.  
   **Problem:** The four monitoring labels overlap and truncate one another, weakening the required visible costs of the Colorado process.  
   **Smallest repair direction:** **Letterer:** place the four metrics in a single readable vertical monitoring block or distribute them across distinct areas of the wall.  
   **Fix:** letterer

6. **Location:** `thumbnails.md`, Page 23, Panel 3.  
   **Problem:** The two Croft authorization lines overlap and truncate: `CSG WILL NOT BLOCK THE INTERIM PUBLIC CONTRACT` and `CSG WITHDRAWS EXCLUSIVE OPERATING FRAME`. The page-turn action is not reliably readable.  
   **Smallest repair direction:** **Letterer:** stack the two document lines with enough separation, preserving both exact statements.  
   **Fix:** letterer

## Plausibility ledger

- **[FIXED] Page count:** The book must contain exactly 24 pages. Current renderer output reports `pages: []` because the six affected layout blocks do not parse.
- **[FIXED] Page sides:** Pages 3, 19, and 21 are right-hand pages; Pages 18, 20, and 24 are left-hand pages. The repaired blocks must preserve these sides.
- **[FIXED] TJ distinction:** Roman’s bonded TJ and Sitara’s TJ are separate physical units. Pages 18, 20, and 24 must preserve separate bodies, displays, and authorizations.
- **[FIXED] Consent sequence:** Roman’s TJ first refuses deletion through the private neural channel, then confirms limited consent through its screen and speaker with Sitara and Nayah witnessing.
- **[FIXED] Disclosure scope:** The release is limited to selected Falcon environmental records, Merritt provenance records, agreed corroborating route and sensor data, Sitara’s separately authorized route/sensor/Falcon-search records, and identified human records. No full mission partition or private neural telemetry is released.
- **[FIXED] Falcon/Nexus geography:** Falcon and Nexus are separate sites. Page 19 must show Falcon only through an authenticated remote feed or record.
- **[FIXED] Falcon interruption:** Authenticated transmission and local inspection control place Falcon on safe hold and make it inspectable. The page must not imply magical remote control, bodily control, immediate arrest, or a view across the ice.
- **[FIXED] Colorado outcome:** The pilot continues under inspection with measurable benefits and visible costs: recovered feedstock, rejected material, residual solids, emissions monitoring, water use, grid demand, and finite throughput.
- **[UNLABELLED / PROPOSAL in `story.md`] Colorado metric values:** `41 → 68` clarity units and `3 → 11` invertebrate taxa remain pending Director approval.
- **[FIXED] Roman’s consequence:** Public exposure and loss of employment/access are the on-page consequences. No arrest, charges, sentencing, or formal prosecution should appear.
- **[FIXED] Ending state:** Evidence survives, Colorado continues provisionally, Croft relinquishes proprietary control, and ownership, financing, and TJ personhood remain unresolved.
- **[UNLABELLED] Production status:** The six malformed blocks remain unverified until repaired and rerendered.

## Continuity ledger

| Element | Current state | Required carry-forward |
|---|---|---|
| Page set | Six layout blocks fail to parse; renderer reports no recognized pages | Recognize exactly Pages 1–24 after repair |
| Page 3 | Unavailable to execution | Preserve Falcon challenge-response entry, limited maintenance access, and Nayah’s five-minute safety limit |
| Page 18 | Unavailable to execution | Preserve deletion threat, Roman’s ethical question, witnessed two-stage consent, and explicit disclosure categories |
| Page 19 | Unavailable to execution | Preserve Nexus evacuation, Orien’s extraction, separate Falcon remote feed, safe hold, and inspection flag |
| Page 20 | Unavailable to execution | Preserve attributable source packages, separate TJ authorizations, human signatures, and Roman’s employment/access loss |
| Page 21 | Unavailable to execution | Preserve inspection before continuation, readable metrics, finite wetland capacity, and bounded operation |
| Page 24 | Unavailable to execution | Preserve separate TJs, shared provenance without exclusive claim, local memory retained, unresolved meeting behind them, and limited pilot status |
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
2. Does the Director approve repairing exactly Pages 3, 18, 19, 20, 21, and 24 without reopening the other layouts?
3. Does the Director approve Page 20’s separate-package arrangement, with Roman’s TJ, Sitara’s TJ, and human-held records visibly distinct?
4. Should Page 19’s `DRILL CONTROL: SAFE HOLD` remain an automated/local control-record state with no named operator added?
5. Does the Director approve the Page 24 splash retaining all lower lettering groups, provided each remains anchored to a distinct object?

BLOCKERS: 1
FIX: layout, letterer