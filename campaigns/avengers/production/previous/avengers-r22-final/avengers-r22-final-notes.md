# notes.md

## Verdict

**Needs a pass.** The execution package is not ready because eleven layout blocks fail JSON parsing, preventing reliable rendering of the affected pages. The thumbnail output therefore omits Pages 3, 11, 12, 14, and 18–24 from review, so the complete 24-page book has not passed the readiness check. The existing rendered pages show one local lettering collision on Page 2 that must be corrected after layout repair.

## Findings by severity

### Blocker

1. **Location:** `layouts.md`, layout blocks 3, 11, 12, 14, and 18–24; renderer errors listed in `thumbnails.md`.  
   **Problem:** Eleven layout blocks fail with `Extra data` errors, so their panel geometry, clear-space instructions, and lettering items are not reliably consumable by the renderer.  
   **Smallest repair direction:** Remove only the duplicated or trailing data that makes each affected JSON block invalid. Preserve the approved panel descriptions, panel counts, lettering text, and page numbers.  
   **Role:** Layout Agent

2. **Location:** `layouts.md` page registry and regenerated `thumbnails.md`.  
   **Problem:** The renderable thumbnail set contains only Pages 1, 2, 4–10, 13, and 15–17. Pages 3, 11, 12, 14, and 18–24 are absent from the reviewable output, so the required 24-page execution package has not been verified.  
   **Smallest repair direction:** Repair the malformed blocks, render exactly Pages 1–24 in order, and regenerate `thumbnails.md`. Do not add, remove, or renumber pages.  
   **Role:** Layout Agent

### Major

1. **Location:** Page 3, Panels 2–4; currently unavailable because of the parser failure.  
   **Problem:** The Falcon credential must open only the hatch and a local maintenance interface. A rendered page must not imply unrestricted facility, archive, or system access through Sitara’s TJ.  
   **Smallest repair direction:** Preserve the sealed challenge-response module beside the communications core, the handspan hatch opening, the local-interface limitation, and Nayah’s five-minute safety limit.  
   **Role:** Layout Agent

2. **Location:** Page 11, Panels 3–4; currently unavailable because of the parser failure.  
   **Problem:** TJ fabrication could read as a magical full-system repair rather than a small, power-costly replacement.  
   **Smallest repair direction:** Show only the conductive bridge, visible battery loss, and qualified sensor readout. Do not depict arbitrary tool manufacture or complete archive recovery.  
   **Role:** Layout Agent

3. **Location:** Page 12, Panels 1–4; currently unavailable because of the parser failure.  
   **Problem:** The midpoint must show the two incomplete records aligning without implying full TJ synchronization or merged mission partitions.  
   **Smallest repair direction:** Preserve the physical separation of the records and TJs, with `SELECTED SYNC ONLY` and `FULL PARTITIONS UNAVAILABLE` in distinct, legible display zones.  
   **Role:** Layout Agent

4. **Location:** Page 14, Panels 1–4; currently unavailable because of the parser failure.  
   **Problem:** The Colorado application must visibly contain both measurable benefit and material cost. An indistinct industrial montage could lose rejected feedstock, recovered feedstock, residual solids, emissions monitoring, water use, grid demand, and limited throughput.  
   **Smallest repair direction:** Keep accepted PET/polyolefin and rejected material visibly separate, and reserve distinct lettering-safe areas for feedstock output, residual solids, emissions, water use, grid demand, and throughput.  
   **Role:** Layout Agent

5. **Location:** Page 18, Panel 4; currently unavailable because of the parser failure.  
   **Problem:** Roman’s bonded TJ and Sitara’s TJ authorize different records. A merged display could falsely imply that one unit authorizes the other’s data or that either releases a full partition.  
   **Smallest repair direction:** Preserve a clear physical gap and separate displays. Roman’s TJ should show its limited disclosure and consent; Sitara’s TJ should show only its independently authorized route, sensor, and Falcon-search records.  
   **Role:** Layout Agent

6. **Location:** Page 19, Panels 3–4; currently unavailable because of the parser failure.  
   **Problem:** Falcon must appear only through an authenticated remote record, not as a shared landscape or unexplained live view. `SAFE HOLD` must indicate interruption pending inspection, not destruction or permanent shutdown.  
   **Smallest repair direction:** Show only the clearly labeled Falcon authenticated remote feed and retain `DRILL CONTROL: SAFE HOLD`, `LOCAL RECORD: FLAGGED`, and `INSPECTION REQUIRED`.  
   **Role:** Layout Agent

7. **Location:** Page 20, Panels 1–4; currently unavailable because of the parser failure.  
   **Problem:** The disclosure package requires readable source attribution. A dense or merged interface could obscure which TJ or human authorized each category and imply full synchronization.  
   **Smallest repair direction:** Use distinct package areas for Roman’s TJ, Sitara’s TJ, Sitara’s Merritt copies, and the human chemical/Orien records. Keep full partitions, private neural telemetry, and unrelated TJ data visibly excluded.  
   **Role:** Layout Agent

8. **Location:** Page 21, Panels 1–4; currently unavailable because of the parser failure.  
   **Problem:** The inspection must visibly precede continuation of the Colorado pilot, while the measurable benefit and finite limits remain readable.  
   **Smallest repair direction:** Preserve the inspection of rejected feedstock, residual solids, emissions, wetland capacity, clarity, invertebrate counts, grid demand, and throughput before showing the line continuing.  
   **Role:** Layout Agent

9. **Location:** Page 22, Panels 1–4; currently unavailable because of the parser failure.  
   **Problem:** The interim public contract must be read aloud while ownership, financing, and long-term governance remain open. A crowded projection or meeting scene could falsely suggest that permanent governance has been settled.  
   **Smallest repair direction:** Keep the two interim-contract headings legible, preserve the distinct disagreements, and show `OWNERSHIP — OPEN`, `FINANCING — OPEN`, and `LONG-TERM GOVERNANCE — OPEN` as separate terms.  
   **Role:** Layout Agent

10. **Location:** Page 23, Panels 1–4; currently unavailable because of the parser failure.  
    **Problem:** Croft’s authorization could be read as repentance, total intellectual-property surrender, or legal exoneration.  
    **Smallest repair direction:** Keep the document narrowly limited to refusing to block the interim public contract and withdrawing CSG’s exclusive operating frame. Preserve the treatment schedule and Croft’s non-apologetic posture.  
    **Role:** Layout Agent

11. **Location:** Page 24, full-page splash; currently unavailable because of the parser failure.  
    **Problem:** The final image contains two separate TJs, Sitara’s provenance status, Roman’s consent question, Roman’s TJ’s response, pilot limits, and the unresolved public meeting. Without strict anchoring, the closing agency statement may attach to the wrong unit or become unreadable.  
    **Smallest repair direction:** Keep both TJs small-dog scale and physically separate. Anchor `SHARED / NO EXCLUSIVE CLAIM` to Sitara’s tablet and `LOCAL MEMORY RETAINED / SHARED RECORD AUTHORIZED` to Roman’s bonded TJ only. Reserve independent lettering zones for each item.  
    **Role:** Layout Agent

### Minor

1. **Location:** `thumbnails.md`, Page 2, Panel 3.  
   **Problem:** Nayah’s `Sitara!` balloon overlaps the `KRAK—` SFX.  
   **Smallest repair direction:** Move the SFX toward the fracture edge or move the balloon into the reserved upper corner without changing the words or art.  
   **Role:** Letterer

2. **Location:** Page 11, Panel 4; verify after parser repair.  
   **Problem:** The krill display must read as qualified evidence, not definitive proof of a single cause.  
   **Smallest repair direction:** Retain wording equivalent to `CAUSE INDICATION: SEA-ICE LOSS` and keep the sensor context visible.  
   **Role:** Layout Agent

3. **Location:** Page 20, Panel 1; verify after parser repair.  
   **Problem:** The four disclosure packages contain long labels that may become unreadable at page scale.  
   **Smallest repair direction:** Preserve the four distinct packages and source attribution, but give each its own uncluttered display area.  
   **Role:** Layout Agent

4. **Location:** Page 24, full-page splash; verify after parser repair.  
   **Problem:** The number of required lettering elements risks competing with the closing image.  
   **Smallest repair direction:** Keep each required item anchored to its physical source and preserve the upper-half breathing room specified in the layout.  
   **Role:** Layout Agent

## Plausibility ledger

- **[FIXED] Page count:** The book requires exactly Pages 1–24. The current renderable thumbnail output does not verify all twenty-four pages.
- **[FIXED] TJ distinction:** Roman’s bonded TJ and Sitara’s TJ are separate physical units; Roman’s is the only neural-bonded unit.
- **[FIXED] TJ scale:** Both units must remain approximately 249 grams and small-dog scale, never large stereotypical robot dogs.
- **[FIXED] Credential scope:** Falcon’s challenge-response credential opens only the hatch and a local maintenance interface.
- **[FIXED] Fabrication limit:** TJ fabrication is limited to small tools or replacement parts and costs time, power, and heat.
- **[FIXED] Colorado limits:** Project 863 uses selected PET/polyolefin feedstock, leaves rejected material and residual solids, consumes water and grid power, monitors emissions, and has finite throughput.
- **[UNLABELLED / PROPOSAL in `story.md`] Colorado figures:** `41 → 68` clarity units and `3 → 11` invertebrate taxa appear in the script and layouts but remain proposed fictional metrics pending Director approval. If changed, replace every occurrence consistently on Pages 15 and 21.
- **[FIXED] Consent sequence:** Roman’s TJ refuses deletion, then gives witnessed screen-and-speaker consent to limited disclosure. Sitara’s TJ separately authorizes its own selected records.
- **[FIXED] Disclosure scope:** No full mission partition, private neural telemetry, unrestricted sensory archive, or unrelated TJ data is released.
- **[FIXED] Geography:** Falcon and Nexus remain separate sites. Falcon appears from Nexus only through an authenticated remote record.
- **[FIXED] Falcon outcome:** Drilling enters safe hold and the local record is flagged for inspection; this is not destruction, arrest, or climate reversal.
- **[FIXED] Nexus outcome:** The corridor floods and refreezes; Nayah orders evacuation and the team leaves nonessential material.
- **[FIXED] Roman’s consequence:** Public exposure and loss of employment/access appear on-page; no arrest, charge, sentencing, or formal prosecution is shown.
- **[FIXED] Ending state:** The Colorado pilot continues under an unincorporated interim partnership while ownership, financing, governance, and TJ personhood remain unresolved.
- **[EXECUTION DEFECT] Layout parsing:** Eleven layout blocks fail JSON parsing, so their page geometry and lettering instructions cannot be trusted until repaired.

## Continuity ledger

| Element | Current state | Required carry-forward |
|---|---|---|
| Layout registry/render output | The supplied thumbnail output verifies only Pages 1, 2, 4–10, 13, and 15–17 | Repair the eleven malformed blocks and render exactly Pages 1–24 |
| Page 2 lettering | `KRAK—` overlaps Nayah’s `Sitara!` balloon in Panel 3 | Letterer must separate the SFX and balloon |
| Page 3 | No renderable thumbnail | Preserve local-only credential access, five-minute limit, and Sitara’s non-neural TJ |
| Page 11 | No renderable thumbnail | Preserve qualified krill evidence, conductive bridge, and visible power cost |
| Page 12 | No renderable thumbnail | Preserve paired-record alignment and selected synchronization only |
| Page 14 | No renderable thumbnail | Preserve accepted/rejected streams, feedstock, residuals, emissions, water, grid demand, and limited throughput |
| Page 18 | No renderable thumbnail | Preserve witnessed Roman-TJ consent and separate Sitara-TJ authorization |
| Page 19 | No renderable thumbnail | Preserve Nayah’s evacuation order, authenticated Falcon feed, safe hold, and inspection flag |
| Page 20 | No renderable thumbnail | Preserve separately attributable TJ and human disclosure packages |
| Page 21 | No renderable thumbnail | Preserve inspection before continuation and readable benefit/limit metrics |
| Page 22 | No renderable thumbnail | Preserve aloud contract reading and open ownership, financing, and governance |
| Page 23 | No renderable thumbnail | Preserve Croft’s active refusal to block the pilot without implying redemption |
| Page 24 | No renderable thumbnail | Preserve co-lead balance, separate TJs, shared provenance, local memory retention, and unresolved public debate |
| Sitara | 26, uninjured, Antarctic red jacket, concealed Merritt copies | Her evidence and credit become shared rather than exclusive |
| Roman | 22, chemically trained, complicit in unauthorized T-ALL research | His exposure costs employment and access, not on-page prosecution |
| Nayah | Field commander with a real safety veto | Her evacuation order controls Page 19 |
| Roman’s TJ | Only neural-bonded unit; local archive and consent authority | Its refusal and limited authorization remain distinct |
| Sitara’s TJ | Separate heat/sensor unit with no neural bond | Its own selected records remain separately authorized |
| Falcon | Illegal exploratory drilling site | Appears on Page 19 only through authenticated remote data |
| Nexus | Coastal cave laboratory | Fracture, flooding, archive movement, and evacuation remain legible |
| Colorado pilot | Real but bounded benefit | No universal restoration, unlimited throughput, or fossil-fuel replacement |

## Questions for the Director

1. Are the fictional Colorado metrics `41 → 68` and `3 → 11` approved as canon, or should they be replaced consistently on Pages 15 and 21?
2. After the eleven JSON blocks are repaired, should the renderer be rerun before page packets are generated?
3. Should `DRILL CONTROL: SAFE HOLD` remain an automated/local control-record state with no named operator?
4. Does the Director approve the distinct disclosure packages and source attribution on Page 20?
5. Does the Director approve retaining all lettering groups on the Page 24 splash, provided each is anchored to its correct physical object?

BLOCKERS: 2
FIX: layout, letterer